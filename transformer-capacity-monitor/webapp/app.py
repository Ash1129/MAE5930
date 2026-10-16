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

from capacity_monitor import airflow_client, config  # noqa: E402
from capacity_monitor.charts import imr_svg  # noqa: E402
from capacity_monitor.guards import check_text  # noqa: E402
from capacity_monitor.report import write_report  # noqa: E402
from capacity_monitor.run import execute_run, new_run_id  # noqa: E402
from capacity_monitor.sources import feed_status, period_for  # noqa: E402
from capacity_monitor.store import Store, now_iso  # noqa: E402

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


@app.template_filter("pct")
def _pct(v):
    return "-" if v is None else f"{float(v) * 100:,.0f}%"


# ---- dashboard / intake ------------------------------------------------------------------

@app.route("/")
def dashboard():
    sched = airflow_client.status()
    runs = store.list_runs(limit=15)
    periods = store.list_periods(limit=10)
    pb = config.load_playbook()
    default_end = (date.today() - timedelta(days=1)).isoformat()
    return render_template("dashboard.html", sched=sched, runs=runs, periods=periods, playbook=pb, default_end=default_end, feeds=feed_status(), alerts=store.list_alerts(limit=8, unacknowledged_only=True))


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
        ("Numbers shown agree with the chart and source readings", False),
    ]
    return render_template("transformer.html", period=period, r=r, svg=svg, checklist=checklist, decisions=DECISIONS, review_started_at=now_iso(), playbook=pb, period_readings=r["period_readings"][-48:])


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

@app.route("/map")
def map_latest():
    periods = store.list_periods(limit=1)
    if not periods:
        flash("Run a period first; the map shows the latest period's results.", "error")
        return redirect(url_for("dashboard"))
    return redirect(url_for("period_map", period_id=periods[0]["period_id"]))


@app.route("/periods/<period_id>/map")
def period_map(period_id):
    import json

    period = store.get_period(period_id)
    if not period:
        abort(404)
    points = []
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
                "area": r.get("area_name", ""),
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
                "disposition": (f"{DECISIONS[d['decision']]} by {d['reviewer']}") if d else None,
                "url": url_for("transformer_detail", period_id=period_id, tid=r["transformer_id"]),
                "is_calibration": r["is_calibration"],
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
    return render_template("map.html", period=period, points=points, boundaries=boundaries, periods=periods)


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
    return render_template("setup.html", feeds=feed_status(), feeds_dir=str(config.FEEDS_DIR), playbook=config.load_playbook(), sched=airflow_client.status(), env=env, db=str(config.DB_PATH), reports=str(config.REPORTS_DIR))


@app.post("/alerts/<int:alert_id>/ack")
def ack_alert(alert_id):
    store.acknowledge_alert(alert_id, reviewer_name() or "reviewer")
    return redirect(request.referrer or url_for("dashboard"))


@app.route("/alerts")
def alerts():
    return render_template("alerts.html", alerts=store.list_alerts(limit=200))


@app.route("/metrics")
def metrics():
    return render_template("metrics.html", m=store.review_metrics())


@app.route("/api/status")
def api_status():
    last = store.last_run()
    return {"last_run": last and {k: last[k] for k in ("run_id", "period_id", "status", "started_at", "finished_at", "error")}, "scheduler": airflow_client.status(), "feeds": feed_status()}


if __name__ == "__main__":
    port = int(os.environ.get("CAPMON_APP_PORT", "5055"))
    config.ensure_dirs()
    app.run(host="127.0.0.1", port=port, debug=False, threaded=True)
