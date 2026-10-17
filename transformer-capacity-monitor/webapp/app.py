"""Review app: intake (Run now), run progress, exception review with Approve / Request changes / Reject,
report finalization (enforced in the backend), scheduler status with pause control, setup and metrics.

Run:  python -m webapp.app   (http://127.0.0.1:5055)
"""

from __future__ import annotations

import os
import sys
import threading
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from flask import Flask, abort, flash, redirect, render_template, request, send_from_directory, url_for  # noqa: E402

from capacity_monitor import ai_explain, airflow_client, config, explain, heat  # noqa: E402
from capacity_monitor.charts import imr_svg, mini_imr_svg  # noqa: E402
from capacity_monitor.guards import check_text  # noqa: E402
from capacity_monitor.report import write_report  # noqa: E402
from capacity_monitor.run import execute_run, new_run_id  # noqa: E402
from capacity_monitor.sources import feed_status, period_for  # noqa: E402
from capacity_monitor.store import Store, now_iso  # noqa: E402
from webapp.viz import (  # noqa: E402
    STATUS_LABEL,
    STATUS_ORDER,
    STABILITY_LABEL,
    STABILITY_ORDER,
    area_chart_svg,
    filter_summary,
    forecast_row,
    pie_svg,
    summarize_results,
    usage_strip_svg,
)

app = Flask(__name__, template_folder=str(Path(__file__).parent / "templates"))
app.secret_key = os.environ.get("CAPMON_SECRET", "local-review-app-not-for-internet")
store = Store()
_running: dict[str, threading.Thread] = {}

DECISIONS = {"approve": "Approve", "request_changes": "Request changes", "reject": "Reject"}


def reviewer_name() -> str:
    return store.get_setting("reviewer_name", "") or config.load_playbook().get("review", {}).get("reviewer_name", "") or ""


@app.context_processor
def _ctx():
    return {"reviewer_name": reviewer_name(), "unacked_alerts": len(store.list_alerts(unacknowledged_only=True)), "now": now_iso()}


@app.template_filter("num")
def _num(v, nd=2):
    if v is None:
        return "-"
    try:
        return f"{float(v):,.{nd}f}"
    except (TypeError, ValueError):
        return str(v)


@app.template_filter("explain")
def _explain(alert):
    out = explain.explain_alert(alert.get("message", ""), alert.get("step"))
    out["ai"] = store.get_ai_explanation(ai_explain._key(alert.get("message", ""), alert.get("step"))) if ai_explain.enabled(store) else None
    out["ai_error"] = store.get_ai_error(ai_explain._key(alert.get("message", ""), alert.get("step"))) if ai_explain.enabled(store) and not out["ai"] else None
    out["ai_on"] = ai_explain.enabled(store) and ai_explain.cli_path() is not None
    return out


@app.template_filter("explain_problem")
def _explain_problem(text):
    if text.startswith("warning:"):
        return {"note": explain.explain_note(text[len("warning:"):].strip()) or text[len("warning:"):].strip()}
    return explain.explain_problem(text)


@app.template_filter("pct")
def _pct(v):
    return "-" if v is None else f"{float(v) * 100:,.0f}%"


# ---- dashboard / intake ------------------------------------------------------------------

@app.route("/dashboard")
def dashboard():
    sched = airflow_client.status()
    runs = store.list_runs(limit=15)
    periods = store.list_periods(limit=10)
    pb = config.load_playbook()
    default_end = (date.today() - timedelta(days=1)).isoformat()
    chart_card = None
    if periods:
        summary = summarize_results(store.get_transformer_results(periods[0]["period_id"]))
        chart_card = {"period_id": periods[0]["period_id"], "status": summary["status_slices"], "stability": summary["stability_slices"], "areas": len(summary["areas"]), "usage": summary["usage"]}
    return render_template("dashboard.html", sched=sched, runs=runs, periods=periods, playbook=pb, default_end=default_end, feeds=feed_status(), alerts=store.list_alerts(limit=8, unacknowledged_only=True), chart_card=chart_card)


@app.post("/runs")
def start_run():
    period_end = request.form.get("period_end", "").strip()
    try:
        d = date.fromisoformat(period_end)
    except ValueError:
        flash("Enter a valid period end date (YYYY-MM-DD).", "error")
        return redirect(url_for("dashboard"))
    if d > date.today():
        flash("The period end cannot be in the future.", "error")
        return redirect(url_for("dashboard"))
    period = period_for(d)
    run_id = new_run_id(period, "manual")
    t = threading.Thread(target=execute_run, args=(d, "manual", Store()), kwargs={"run_id": run_id}, daemon=True)
    _running[run_id] = t
    t.start()
    return redirect(url_for("run_detail", run_id=run_id))


@app.route("/runs/<run_id>")
def run_detail(run_id):
    run = store.get_run(run_id)
    if not run:
        if run_id in _running and _running[run_id].is_alive():
            return render_template("run.html", run=None, run_id=run_id, refresh=True)
        abort(404)
    refresh = run["status"] == "running"
    period = store.get_period(run["period_id"]) if run["status"] == "success" else None
    return render_template("run.html", run=run, run_id=run_id, refresh=refresh, period=period)


# ---- periods / review ---------------------------------------------------------------------

def _finalize_blockers(period_id: str) -> list[str]:
    """Backend approval gate: every exception needs a current disposition; request_changes blocks."""
    results = store.get_transformer_results(period_id)
    blockers = []
    for r in results:
        if r["status"] != "review_needed":
            continue
        d = r.get("disposition")
        if not d:
            blockers.append(f"{r['transformer_id']}: no disposition recorded for the current inputs")
        elif d["decision"] == "request_changes" and not r["is_calibration"]:
            blockers.append(f"{r['transformer_id']}: changes were requested; rerun or re-review before finalizing")
    return blockers


@app.route("/periods/<period_id>")
def period_detail(period_id):
    period = store.get_period(period_id)
    if not period:
        abort(404)
    results = store.get_transformer_results(period_id)
    exceptions = [r for r in results if r["status"] == "review_needed"]
    within = [r for r in results if r["status"] != "review_needed"]
    blockers = _finalize_blockers(period_id)
    runs = [r for r in store.list_runs(limit=100) if r["period_id"] == period_id]
    return render_template("period.html", period=period, exceptions=exceptions, within=within, blockers=blockers, runs=runs, decisions=DECISIONS)


@app.route("/periods/<period_id>/transformers/<tid>")
def transformer_detail(period_id, tid):
    period = store.get_period(period_id)
    r = store.get_transformer_result(period_id, tid)
    if not period or not r:
        abort(404)
    svg = imr_svg(r["chart"], period["period"]["start"], r["unit"], r["rated_max"])
    pb = config.load_playbook()
    checklist = [
        ("Chart signals investigated (dates, rule, source readings)", r["stability"] == "signal"),
        ("Enough stable history for limits and capability", r["stability"] == "insufficient_history"),
        (f"Cpk at or above {pb['capability']['cpk_review_below']} and lower bound above {pb['capability']['cpk_ci_low_review_below']}", r["capacity"]["cpk"] is not None and (r["capacity"]["cpk"] < pb["capability"]["cpk_review_below"] or r["capacity"]["cpk_ci_low"] < pb["capability"]["cpk_ci_low_review_below"])),
        (f"Forecast peak below {int(pb['forecast']['near_rating_ratio'] * 100)}% of rating; allocation assumption acceptable", r["capacity"]["forecast_ratio"] is not None and r["capacity"]["forecast_ratio"] >= pb["forecast"]["near_rating_ratio"]),
        ("Period readings below the rated maximum", r["capacity"]["period_peak_ratio"] is not None and r["capacity"]["period_peak_ratio"] >= 1.0),
        ("Capability assumptions met (independent, roughly normal daily peaks)", bool(r["capacity"].get("assumption_flags"))),
        ("Numbers shown agree with the chart and source readings", False),
    ]
    ai_on = ai_explain.enabled(store) and ai_explain.cli_path() is not None
    summary = {"rule": explain.summarize_transformer(r), "ai": ai_explain.cached_summary(store, period_id, r) if ai_on else None, "ai_on": ai_on,
               "url": url_for("api_transformer_summary", period_id=period_id, tid=tid)}
    return render_template("transformer.html", period=period, r=r, svg=svg, checklist=checklist, decisions=DECISIONS, review_started_at=now_iso(), playbook=pb, period_readings=r["period_readings"][-48:], summary=summary)


@app.post("/periods/<period_id>/transformers/<tid>/disposition")
def record_disposition(period_id, tid):
    r = store.get_transformer_result(period_id, tid)
    period = store.get_period(period_id)
    if not r or not period:
        abort(404)
    if period["status"] == "final":
        flash("This period's report is already final. Rerun the period to review it again.", "error")
        return redirect(url_for("transformer_detail", period_id=period_id, tid=tid))
    decision = request.form.get("decision", "")
    reviewer = request.form.get("reviewer", "").strip()
    notes = request.form.get("notes", "").strip()
    if decision not in DECISIONS:
        abort(400, "Unknown decision")
    if not reviewer:
        flash("Enter the reviewer's name before recording a disposition.", "error")
        return redirect(url_for("transformer_detail", period_id=period_id, tid=tid))
    pb = config.load_playbook()
    problems = check_text(notes, "notes", max_len=int(pb["review"].get("max_text_length", 2000))) + check_text(reviewer, "reviewer", max_len=120)
    if problems:
        flash("Disposition not recorded: " + "; ".join(problems), "error")
        return redirect(url_for("transformer_detail", period_id=period_id, tid=tid))
    if decision != "approve" and not notes:
        flash("Request changes and Reject need a note explaining what is wrong.", "error")
        return redirect(url_for("transformer_detail", period_id=period_id, tid=tid))
    caught = None
    if r["is_calibration"]:
        caught = 1 if decision in ("request_changes", "reject") else 0
    store.record_disposition(period_id, tid, r["input_hash"], decision, notes, reviewer, request.form.get("review_started_at"), r["is_calibration"], caught)
    store.set_setting("reviewer_name", reviewer)
    write_report(store, period_id)
    if r["is_calibration"]:
        flash(("Well caught: " if caught else "Missed: ") + "this was a seeded known-wrong calibration case. It is excluded from the report and counted in Metrics.", "info")
    else:
        flash(f"{DECISIONS[decision]} recorded for {tid} by {reviewer}.", "info")
    return redirect(url_for("period_detail", period_id=period_id))


@app.post("/periods/<period_id>/finalize")
def finalize(period_id):
    period = store.get_period(period_id)
    if not period:
        abort(404)
    reviewer = request.form.get("reviewer", "").strip()
    if not reviewer or check_text(reviewer, "reviewer", max_len=120):
        flash("Enter the finalizing reviewer's name.", "error")
        return redirect(url_for("period_detail", period_id=period_id))
    blockers = _finalize_blockers(period_id)  # enforced here, not in the page
    if blockers:
        flash("Cannot finalize: " + "; ".join(blockers), "error")
        return redirect(url_for("period_detail", period_id=period_id)), 409
    store.finalize_period(period_id, reviewer)
    store.set_setting("reviewer_name", reviewer)
    write_report(store, period_id)
    flash(f"Report for period {period_id} finalized by {reviewer}.", "info")
    return redirect(url_for("period_detail", period_id=period_id))


@app.route("/reports/<period_id>/<path:filename>")
def report_file(period_id, filename):
    d = config.REPORTS_DIR / period_id
    if not d.exists() or filename not in ("report.html", "report.json", "report.md"):
        abort(404)
    return send_from_directory(d, filename, as_attachment=filename != "report.html")


# ---- map ---------------------------------------------------------------------------------

@app.route("/")
@app.route("/map")
def map_latest():
    """Home page: the map of the latest period, or the first-launch map (boundaries only) before any run."""
    periods = store.list_periods(limit=1)
    if not periods:
        return _render_map(None)
    return redirect(url_for("period_map", period_id=periods[0]["period_id"]))


@app.route("/periods/<period_id>/map")
def period_map(period_id):
    if not store.get_period(period_id):
        abort(404)
    return _render_map(period_id)


def _latest_alert() -> dict | None:
    alerts = store.list_alerts(limit=1, unacknowledged_only=True)
    if not alerts:
        return None
    a = alerts[0]
    e = explain.explain_alert(a.get("message", ""), a.get("step"))
    ai = store.get_ai_explanation(ai_explain._key(a.get("message", ""), a.get("step"))) if ai_explain.enabled(store) else None
    return {
        "id": a["id"],
        "when": a["created_at"],
        "headline": (ai or e)["title"],
        "happened": (ai or e)["meaning"],
        "todo": (ai or e)["action"],
        "run_id": a.get("run_id"),
        "period_id": a.get("period_id"),
    }


def _render_map(period_id: str | None):
    import json

    period = store.get_period(period_id) if period_id else None
    points = []
    if period:
        for r in store.get_transformer_results(period_id):
            if r.get("lat") is None or r.get("lon") is None:
                continue
            c = r["capacity"]
            d = r.get("disposition")
            points.append(
                {
                    "id": r["transformer_id"],
                    "name": r["name"],
                    "lat": r["lat"],
                    "lon": r["lon"],
                    "status": r["status"],
                    "stability": r["stability"],
                    "area": r.get("area_id", ""),
                    "area_name": r.get("area_name", ""),
                    "rating": r["rated_max"],
                    "unit": r["unit"],
                    "period_peak": c["period_peak"],
                    "period_peak_ratio": c["period_peak_ratio"],
                    "cpk": c["cpk"],
                    "cpk_ci_low": c["cpk_ci_low"],
                    "cpk_ci_high": c["cpk_ci_high"],
                    "projected_peak": c["projected_peak"],
                    "forecast_ratio": c["forecast_ratio"],
                    "reason": r["decision"]["reason"],
                    "rule": r["decision"]["rule"],
                    "signals": [f"{s['rule']} on {s['date']}" for s in r["chart"]["signals"]][:4],
                    "assumption_flags": c.get("assumption_flags", []),
                    "disposition": (f"{DECISIONS[d['decision']]} by {d['reviewer']}") if d else None,
                    "url": url_for("transformer_detail", period_id=period_id, tid=r["transformer_id"]),
                    "is_calibration": r["is_calibration"],
                    "cls": r.get("customer_class", "unknown"),
                }
            )
    boundaries = None
    bpath = config.FEEDS_DIR / config.FEED_FILES["boundaries"]
    if bpath.exists():
        try:
            boundaries = json.loads(bpath.read_text(encoding="utf-8"))
        except ValueError:
            boundaries = None
    periods = [p["period_id"] for p in store.list_periods(limit=20)]
    pb = config.load_playbook()
    return render_template(
        "map.html",
        period=period,
        points=points,
        boundaries=boundaries,
        periods=periods,
        districts=_districts(boundaries),
        feeds=feed_status(),
        default_end=(date.today() - timedelta(days=1)).isoformat(),
        playbook=pb,
        dates=heat.dates() if period else [],
        seasonal=pb.get("seasonal_model", {}),
        heat_default_date=period["period"]["end"] if period else None,
        latest_alert=_latest_alert(),
        sched=airflow_client.status(),
        last_run=store.last_run(),
    )


def _chart_href(period_id: str, status: str | None, stability: str | None) -> str:
    kw = {}
    if status:
        kw["status"] = status
    if stability:
        kw["stability"] = stability
    return url_for("period_charts", period_id=period_id, **kw)


def _chart_models(period_id: str, status: str | None, stability: str | None):
    if status not in STATUS_ORDER:
        status = None
    if stability not in STABILITY_ORDER:
        stability = None
    full = summarize_results(store.get_transformer_results(period_id))
    for row in full["transformers"]:
        row["url"] = url_for("transformer_detail", period_id=period_id, tid=row["id"])
        row["area_url"] = url_for("area_detail", period_id=period_id, area_id=row["area_id"])
    for area in full["areas"]:
        area["url"] = url_for("area_detail", period_id=period_id, area_id=area["area_id"])
    for sl in full["status_slices"]:
        sl["href"] = _chart_href(period_id, None if status == sl["key"] else sl["key"], stability)
    for sl in full["stability_slices"]:
        sl["href"] = _chart_href(period_id, status, None if stability == sl["key"] else sl["key"])
    view = filter_summary(full, status, stability)
    return full, view, status, stability


@app.route("/charts")
def charts_latest():
    periods = store.list_periods(limit=1)
    if not periods:
        flash("Run a period first. The charts use that period's results.", "info")
        return redirect(url_for("dashboard"))
    return redirect(url_for("period_charts", period_id=periods[0]["period_id"]))


@app.route("/periods/<period_id>/charts")
def period_charts(period_id):
    period = store.get_period(period_id)
    if not period:
        abort(404)
    model, view, status, stability = _chart_models(period_id, request.args.get("status"), request.args.get("stability"))
    near = float(config.load_playbook().get("forecast", {}).get("near_rating_ratio", 0.9))
    periods = [p["period_id"] for p in store.list_periods(limit=20)]
    return render_template(
        "charts.html",
        period=period,
        periods=periods,
        model=model,
        view=view,
        active_status=status,
        active_stability=stability,
        status_label=STATUS_LABEL.get(status, ""),
        stability_label=STABILITY_LABEL.get(stability, ""),
        status_svg=pie_svg(model["status_slices"], status),
        stability_svg=pie_svg(model["stability_slices"], stability),
        area_svg=area_chart_svg(view["areas"], near),
        strip_svg=usage_strip_svg(view["transformers"], near),
        near_pct=round(near * 100),
        readings_present=feed_status().get("readings", {}).get("present", False),
    )


@app.route("/periods/<period_id>/areas/<area_id>")
def area_detail(period_id, area_id):
    period = store.get_period(period_id)
    if not period:
        abort(404)
    model = summarize_results(store.get_transformer_results(period_id))
    area = next((a for a in model["areas"] if a["area_id"] == area_id), None)
    if not area:
        abort(404)
    for row in area["transformers"]:
        row["url"] = url_for("transformer_detail", period_id=period_id, tid=row["id"])
    version = config.load_playbook().get("forecast", {}).get("version", "")
    forecast = forecast_row(config.FEEDS_DIR / config.FEED_FILES["forecast"], version, area_id)
    return render_template("area.html", period=period, area=area, forecast=forecast)


def _districts(boundaries) -> list[dict]:
    out = []
    for f in (boundaries or {}).get("features", []):
        props = f.get("properties", {})
        geom = f.get("geometry", {})
        coords = geom.get("coordinates", [])
        polys = [coords] if geom.get("type") == "Polygon" else coords
        lons = [pt[0] for poly in polys for ring in poly[:1] for pt in ring]
        lats = [pt[1] for poly in polys for ring in poly[:1] for pt in ring]
        if lons and lats:
            out.append({"id": props.get("area_id"), "name": props.get("name"), "kind": props.get("kind"), "bbox": [[min(lats), min(lons)], [max(lats), max(lons)]]})
    return out


@app.route("/heatmap")
def heatmap_latest():
    return redirect(url_for("map_latest"))


@app.route("/periods/<period_id>/heatmap")
def period_heatmap(period_id):
    """The heat view now lives on the Map page (pick a district)."""
    return redirect(url_for("period_map", period_id=period_id))


@app.route("/api/heat/recorded")
def api_heat_recorded():
    date_iso = request.args.get("date", "")
    data = heat.recorded_day(date_iso)
    return {"date": date_iso, "modeled": False, "loads": data, "transformers": len(data)}


@app.route("/api/heat/seasonal")
def api_heat_seasonal():
    try:
        month = int(request.args.get("month", "1"))
    except ValueError:
        abort(400)
    if not 1 <= month <= 12:
        abort(400)
    return heat.seasonal_day(month)


# ---- scheduler controls -------------------------------------------------------------------

@app.post("/scheduler/<action>")
def scheduler_action(action):
    try:
        if action == "pause":
            airflow_client.set_paused(True)
            flash("Scheduled runs paused.", "info")
        elif action == "resume":
            airflow_client.set_paused(False)
            flash("Scheduled runs resumed.", "info")
        elif action == "trigger":
            pe = request.form.get("period_end", "").strip() or None
            airflow_client.trigger(pe)
            flash("Run queued in Airflow; it appears below once the scheduler picks it up.", "info")
        else:
            abort(404)
    except Exception as exc:  # noqa: BLE001
        flash(f"Scheduler action failed: {exc}", "error")
    return redirect(url_for("dashboard"))


# ---- setup / alerts / metrics -------------------------------------------------------------

@app.route("/setup", methods=["GET", "POST"])
def setup():
    if request.method == "POST":
        name = request.form.get("reviewer_name", "").strip()
        if check_text(name, "reviewer", max_len=120):
            flash("Reviewer name rejected by the input check.", "error")
        else:
            store.set_setting("reviewer_name", name)
            flash("Saved.", "info")
        return redirect(url_for("setup"))
    env = {k: ("set" if os.environ.get(k) else "not set") for k in ("CAPMON_ALERT_TO", "CAPMON_SMTP_HOST", "CAPMON_SMTP_USER", "CAPMON_SMTP_PASSWORD")}
    return render_template("setup.html", feeds=feed_status(), feeds_dir=str(config.FEEDS_DIR), playbook=config.load_playbook(), sched=airflow_client.status(), env=env, db=str(config.DB_PATH), reports=str(config.REPORTS_DIR), ai=ai_explain.status(store))


@app.post("/alerts/<int:alert_id>/ack")
def ack_alert(alert_id):
    store.acknowledge_alert(alert_id, reviewer_name() or "reviewer")
    return redirect(request.referrer or url_for("dashboard"))


@app.post("/alerts/<int:alert_id>/explain")
def ai_explain_alert(alert_id):
    alert = next((a for a in store.list_alerts(limit=500) if a["id"] == alert_id), None)
    if not alert:
        abort(404)
    if not ai_explain.enabled(store):
        flash("AI explanations are off. Turn them on in Setup.", "error")
    elif not ai_explain.cli_path():
        flash("The claude command-line tool was not found on this computer.", "error")
    else:
        rec = ai_explain.explain_alert_record(store, alert, force=True)
        flash("Claude's explanation is ready." if rec else "Claude could not produce a usable explanation; the rule-based text stays. See Setup for details.", "info" if rec else "error")
    return redirect(request.referrer or url_for("alerts"))


@app.post("/setup/ai")
def setup_ai():
    on = request.form.get("ai_explanations") == "on"
    store.set_setting(ai_explain.SETTING_KEY, "on" if on else "off")
    flash("AI explanations turned " + ("on." if on else "off."), "info")
    return redirect(url_for("setup"))


@app.route("/alerts")
def alerts():
    return render_template("alerts.html", alerts=store.list_alerts(limit=200))


@app.route("/metrics")
def metrics():
    return render_template("metrics.html", m=store.review_metrics())


@app.route("/api/status")
def api_status():
    last = store.last_run()
    return {
        "last_run": last and {k: last[k] for k in ("run_id", "period_id", "status", "started_at", "finished_at", "error", "current_step")},
        "scheduler": airflow_client.status(),
        "feeds": feed_status(),
        "latest_alert": _latest_alert(),
        "unacknowledged_alerts": len(store.list_alerts(unacknowledged_only=True)),
    }


@app.route("/api/periods/<period_id>/transformers/<tid>/mini")
def api_transformer_mini(period_id, tid):
    """Popup content: compact control charts, a rule-based line, and the cached Haiku summary if one exists."""
    period = store.get_period(period_id)
    r = store.get_transformer_result(period_id, tid)
    if not period or not r:
        abort(404)
    ai_on = ai_explain.enabled(store) and ai_explain.cli_path() is not None
    return {
        "svg": mini_imr_svg(r["chart"], period["period"]["start"], r["unit"], r["rated_max"]),
        "rule_summary": explain.summarize_transformer(r),
        "ai": ai_explain.cached_summary(store, period_id, r) if ai_on else None,
        "ai_on": ai_on,
        "model": ai_explain.SUMMARY_MODEL,
    }


@app.route("/api/periods/<period_id>/transformers/<tid>/summary")
def api_transformer_summary(period_id, tid):
    """Haiku summary through the Claude CLI; blocks for the call (a few seconds) unless cached."""
    r = store.get_transformer_result(period_id, tid)
    if not r:
        abort(404)
    if not (ai_explain.enabled(store) and ai_explain.cli_path()):
        return {"error": "AI summaries are off or the claude CLI is not installed"}, 409
    rec = ai_explain.summarize(store, period_id, r)
    if not rec:
        return {"error": store.get_ai_error(ai_explain.summary_key(period_id, r)) or "no summary"}, 502
    return rec


@app.post("/api/runs")
def api_start_run():
    """Start a run from the map page's run box; returns the run id to poll."""
    period_end = (request.get_json(silent=True) or {}).get("period_end") or request.form.get("period_end", "")
    try:
        d = date.fromisoformat(str(period_end).strip())
    except ValueError:
        return {"error": "Enter a valid period end date (YYYY-MM-DD)."}, 400
    if d > date.today():
        return {"error": "The period end cannot be in the future."}, 400
    run_id = new_run_id(period_for(d), "manual")
    t = threading.Thread(target=execute_run, args=(d, "manual", Store()), kwargs={"run_id": run_id}, daemon=True)
    _running[run_id] = t
    t.start()
    return {"run_id": run_id, "period_id": d.isoformat()}


@app.route("/api/runs/<run_id>")
def api_run(run_id):
    run = store.get_run(run_id)
    if not run:
        if run_id in _running and _running[run_id].is_alive():
            return {"run_id": run_id, "status": "running", "current_step": 1}
        abort(404)
    out = {k: run[k] for k in ("run_id", "period_id", "status", "current_step", "error")}
    if run["status"] == "failed":
        problems = [p for p in run.get("problems", []) if not p.startswith("warning:")]
        out["headline"] = explain.explain_problem(problems[0] if problems else (run.get("error") or ""))["title"]
    return out


if __name__ == "__main__":
    port = int(os.environ.get("CAPMON_APP_PORT", "5055"))
    config.ensure_dirs()
    app.run(host="127.0.0.1", port=port, debug=False, threaded=True)
