"""Review app: intake (Run now), run progress, exception review with Approve / Request changes / Reject,
report finalization (enforced in the backend), scheduler status with pause control, setup and metrics.

Run:  python -m webapp.app   (http://127.0.0.1:5055)
"""

from __future__ import annotations

import os
import sys
import threading
from datetime import date, datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from flask import Flask, abort, flash, redirect, render_template, request, send_from_directory, url_for  # noqa: E402

from capacity_monitor import ai_explain, airflow_client, config, explain, heat, thermal  # noqa: E402
from capacity_monitor.charts import mini_imr_svg, review_chart_caption, review_chart_svg, review_moving_range_caption, review_moving_range_svg  # noqa: E402
from capacity_monitor.guards import check_text  # noqa: E402
from capacity_monitor.report import write_report  # noqa: E402
from capacity_monitor.run import execute_run, new_run_id  # noqa: E402
from capacity_monitor.sources import feed_status, optional_feed_status, period_for  # noqa: E402
from capacity_monitor.store import Store, now_iso  # noqa: E402
from webapp.viz import (  # noqa: E402
    STATUS_LABEL,
    STATUS_ORDER,
    STATUS_COLOR,
    STABILITY_LABEL,
    STABILITY_ORDER,
    county_trend_charts,
    forecast_row,
    pie_svg,
    summarize_results,
)

app = Flask(
    __name__,
    template_folder=str(Path(__file__).parent / "templates"),
    static_folder=str(Path(__file__).parent / "static"),
)
app.secret_key = os.environ.get("CAPMON_SECRET", "local-review-app-not-for-internet")
store = Store()
_running: dict[str, threading.Thread] = {}

DECISIONS = {"approve": "Approve", "request_changes": "Request changes", "reject": "Reject"}
DECISION_CHIPS = {"approve": "Approved", "request_changes": "Changes requested", "reject": "Rejected"}


def reviewer_name() -> str:
    return store.get_setting("reviewer_name", "") or config.load_playbook().get("review", {}).get("reviewer_name", "") or ""


@app.context_processor
def _ctx():
    return {"reviewer_name": reviewer_name(), "unacked_alerts": len(store.list_alerts(unacknowledged_only=True)), "now": now_iso(), "latest_alert": _latest_alert()}


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


@app.template_filter("day")
def _day(iso):
    """'2026-10-16T06:02:11-04:00' -> 'Fri 16 Oct'."""
    try:
        return datetime.fromisoformat(iso).strftime("%a %-d %b")
    except (TypeError, ValueError):
        return iso or ""


@app.template_filter("clock")
def _clock(iso):
    return (iso or "")[11:16]


@app.template_filter("delivery")
def _delivery(text):
    t = (text or "").lower()
    if t.startswith("email to"):
        return "Sent by email"
    if t.startswith("email failed"):
        return "Email failed; shown here"
    return "Shown here only"


@app.template_filter("pct")
def _pct(v):
    return "-" if v is None else f"{float(v) * 100:,.0f}%"


@app.template_filter("tid")
def _tid(v):
    """Drop the synthetic T- prefix. Stored ids and URLs keep it."""
    s = "" if v is None else str(v)
    return s[2:] if s.startswith("T-") else s


# ---- dashboard / intake ------------------------------------------------------------------

BAND_ORDER = ("high", "mid", "ok")
BAND_LABEL = {"high": "90% or more", "mid": "70 to 90%", "ok": "Under 70%"}
BAND_COLOR = {"high": "#d7263d", "mid": STATUS_COLOR["review_needed"], "ok": "#1b7f4b"}


def _area_parts(name: str) -> tuple[str, str]:
    for prefix, kind in (("City of ", "city"), ("Town of ", "town"), ("Village of ", "village")):
        if name.startswith(prefix):
            return name[len(prefix):], kind
    return name, ""


def _board_url(period_id: str, **params) -> str:
    q = {"period": period_id}
    q.update({k: v for k, v in params.items() if v})
    return url_for("dashboard", **q)


def _with_hrefs(slices: list[dict], current: str, key: str, period_id: str, status: str, stability: str, area: str, band: str) -> list[dict]:
    params = {"status": status, "stability": stability, "area": area, "band": band}
    params.update({k: request.args.get(k, "") for k in ("reason", "q", "followup", "sort")})
    out = []
    for s in slices:
        nxt = dict(params)
        nxt[key] = "" if current == s["key"] else s["key"]
        item = dict(s)
        item["href"] = _board_url(period_id, **nxt)
        out.append(item)
    return out


REVIEW_REASONS = {
    "4": "Load pattern change", "5": "Short history", "6": "Meter / feed check",
    "7": "Capability unavailable", "8": "Capability assumptions",
    "9": "Low capability", "10": "Uncertain capability", "11": "Future capacity", "12": "Forecast unavailable",
}
FOLLOWUP_STATUSES = {"planned": "Planned", "in_progress": "In progress", "watch": "Watching", "complete": "Complete"}


@app.route("/dashboard")
def dashboard():
    """One screen for a reviewer: outcome and load pies, control charts, then the queue."""
    alerts = store.list_alerts(limit=8, unacknowledged_only=True)
    periods = store.list_periods(limit=12)
    period_id = request.args.get("period", "").strip()
    if not period_id and periods:
        period_id = periods[0]["period_id"]
    period = store.get_period(period_id) if period_id else None
    if period_id and not period:
        abort(404)
    status = request.args.get("status", "").strip()
    stability = request.args.get("stability", "").strip()
    area = request.args.get("area", "").strip()
    band = request.args.get("band", "").strip()
    if status not in ("", "all", *STATUS_ORDER):
        status = ""
    if stability not in ("", *STABILITY_ORDER):
        stability = ""
    if band not in ("", *BAND_ORDER):
        band = ""

    reason = request.args.get("reason", "")
    reason = reason if reason in REVIEW_REASONS else ""
    if reason:
        status = "review_needed"
    search = request.args.get("q", "").strip()[:120]
    followup_filter = request.args.get("followup", "")
    sort = request.args.get("sort", "priority")
    board = None
    if period:
        raw = store.get_transformer_results(period_id)
        full = summarize_results(raw)
        period_start = (period.get("period") or {}).get("start") or period_id
        for row in full["transformers"]:
            row["url"] = url_for("transformer_detail", period_id=period_id, tid=row["id"])
        scope = [r for r in raw if not r.get("is_calibration") and (not area or r.get("area_id") == area)]
        focused = summarize_results(scope) if area else full
        for row in focused["transformers"]:
            row["url"] = url_for("transformer_detail", period_id=period_id, tid=row["id"])
        status_slices = _with_hrefs(focused["status_slices"], status, "status", period_id, status, stability, area, band)
        stability_slices = _with_hrefs(focused["stability_slices"], stability, "stability", period_id, status, stability, area, band)
        band_counts = []
        for key in BAND_ORDER:
            count = sum(1 for r in focused["transformers"] if r["usage_band"] == key)
            if count:
                band_counts.append({"key": key, "label": BAND_LABEL[key], "count": count, "color": BAND_COLOR[key]})
        band_slices = _with_hrefs(band_counts, band, "band", period_id, status, stability, area, band)
        for item in full["areas"]:
            item["short"], item["kind"] = _area_parts(item["area_name"])
        base_counts = {}
        for item in full["areas"]:
            base_counts[item["short"]] = base_counts.get(item["short"], 0) + 1
        for item in full["areas"]:
            if base_counts[item["short"]] > 1 and item["kind"]:
                item["short"] = f"{item['short']} ({item['kind']})"
        areas = sorted(full["areas"], key=lambda a: (-a["inspect_now"], -a["flagged"], a["area_name"]))
        rows = focused["transformers"]
        if status == "all":
            pass
        elif status:
            rows = [r for r in rows if r["status"] == status]
        else:
            rows = [r for r in rows if r["status"] != "within_limits"]
        rows = sorted(rows, key=lambda r: 0 if r["status"] == "inspect_now" else 1)  # stable sort: red first, then by usage
        if stability:
            rows = [r for r in rows if r["stability"] == stability]
        if area:
            rows = [r for r in rows if r["area_id"] == area]
        if band:
            rows = [r for r in rows if r["usage_band"] == band]
        reason_options = [{"key": key, "label": label, "count": sum(r["status"] == "review_needed" and str(r["rule"]) == key for r in focused["transformers"])} for key, label in REVIEW_REASONS.items()]
        if reason:
            rows = [r for r in rows if r["status"] == "review_needed" and str(r["rule"]) == reason]
        if search:
            rows = [r for r in rows if search.casefold() in " ".join([r["id"], r["name"], r["area_name"]]).casefold()]
        today = date.today().isoformat()
        for row in rows:
            f = row.get("followup")
            row["overdue"] = bool(f and f["status"] != "complete" and f["due_date"] < today)
        if followup_filter:
            rows = [r for r in rows if (not r["followup"] if followup_filter == "unassigned" else r["overdue"] if followup_filter == "overdue" else bool(r["followup"] and r["followup"]["status"] == followup_filter))]
        if sort in ("peak", "forecast"):
            field = "usage" if sort == "peak" else "forecast"
            rows.sort(key=lambda r: (r[field] is None, -(r[field] or 0)))
        elif sort == "due":
            rows.sort(key=lambda r: (not bool(r["followup"]), (r["followup"] or {}).get("due_date", "")))
        review_n = sum(1 for r in focused["transformers"] if r["status"] != "within_limits")
        trends = county_trend_charts(scope, period_start)
        board = {
            "status_slices": status_slices,
            "stability_slices": stability_slices,
            "band_slices": band_slices,
            "status_svg": pie_svg(status_slices, status if status and status != "all" else None),
            "stability_svg": pie_svg(stability_slices, stability or None),
            "band_svg": pie_svg(band_slices, band or None),
            "areas": areas,
            "rows": rows,
            "review_n": review_n,
            "total": len(focused["transformers"]),
            "area_name": next((a["area_name"] for a in full["areas"] if a["area_id"] == area), area),
            "queue": not status,
            "trends": trends,
        }
    return render_template(
        "dashboard.html",
        period=period,
        periods=[p["period_id"] for p in periods],
        alerts=alerts,
        board=board,
        status=status,
        stability=stability,
        area=area,
        band=band,
        reason=reason, search=search, followup_filter=followup_filter, sort=sort,
        reason_options=reason_options if period else [], followup_statuses=FOLLOWUP_STATUSES,
        review_reasons=REVIEW_REASONS, inspect_reasons={"1": "At or above rating", "2": "Sustained load shift", "3": "Repeated outliers"},
        status_label=STATUS_LABEL.get(status, ""),
        stability_label=STABILITY_LABEL.get(stability, ""),
        band_label=BAND_LABEL.get(band, ""),
        stability_labels=STABILITY_LABEL,
    )


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
        if r["status"] == "within_limits":
            continue
        d = r.get("disposition")
        if not d:
            blockers.append(f"{_tid(r['transformer_id'])}: no disposition recorded for the current inputs")
        elif d["decision"] == "request_changes" and not r["is_calibration"]:
            blockers.append(f"{_tid(r['transformer_id'])}: changes were requested; rerun or re-review before finalizing")
    return blockers


@app.route("/periods/<period_id>")
def period_detail(period_id):
    period = store.get_period(period_id)
    if not period:
        abort(404)
    results = store.get_transformer_results(period_id)
    exceptions = sorted([r for r in results if r["status"] != "within_limits"], key=lambda r: 0 if r["status"] == "inspect_now" else 1)
    within = [r for r in results if r["status"] == "within_limits"]
    blockers = _finalize_blockers(period_id)
    runs = [r for r in store.list_runs(limit=100) if r["period_id"] == period_id]
    return render_template("period.html", period=period, exceptions=exceptions, within=within, blockers=blockers, runs=runs, decisions=DECISIONS)


@app.route("/periods/<period_id>/transformers/<tid>")
def transformer_detail(period_id, tid):
    period = store.get_period(period_id)
    r = store.get_transformer_result(period_id, tid)
    if not period or not r:
        abort(404)
    pb = config.load_playbook()
    cap, fc = r["capacity"], pb["forecast"]["near_rating_ratio"]
    # same order and flags as before, worded for a non-statistician; the index of the item that matches the decision rule
    checklist = [
        ("Load pattern looked at for changes", r["stability"] == "signal"),
        ("Enough steady history to judge it", r["stability"] == "insufficient_history"),
        (f"Room left today is healthy (Cpk {pb['capability']['cpk_review_below']} or more)", cap["cpk"] is not None and (cap["cpk"] < pb["capability"]["cpk_review_below"] or cap["cpk_ci_low"] < pb["capability"]["cpk_ci_low_review_below"])),
        (f"Winter estimate stays under {int(fc * 100)}% of the rating", cap["forecast_ratio"] is not None and cap["forecast_ratio"] >= fc),
        ("No reading this week reached the rating", cap["period_peak_ratio"] is not None and cap["period_peak_ratio"] >= 1.0),
        ("Daily peaks meet the capability assumptions", bool(cap.get("assumption_flags"))),
        ("Numbers match the chart and the raw readings", False),
    ]
    cause = {"2": 0, "3": 0, "4": 0, "5": 1, "9": 2, "10": 2, "11": 3, "1": 4, "8": 5}.get(str(r["decision"]["rule"])) if r["status"] != "within_limits" else None
    ai_on = ai_explain.enabled(store) and ai_explain.cli_path() is not None
    summary = {"rule": explain.summarize_transformer(r), "ai": ai_explain.cached_summary(store, period_id, r) if ai_on else None, "ai_on": ai_on,
               "url": url_for("api_transformer_summary", period_id=period_id, tid=tid)}
    flagged = [x for x in store.get_transformer_results(period_id) if x["status"] != "within_limits"]
    review_ids = [x["transformer_id"] for x in sorted(flagged, key=lambda x: 0 if x["status"] == "inspect_now" else 1)]
    case = None
    if tid in review_ids:
        i = review_ids.index(tid)
        case = {"n": i + 1, "of": len(review_ids), "prev": review_ids[i - 1] if i > 0 else None, "next": review_ids[i + 1] if i + 1 < len(review_ids) else None}
    readings = r.get("period_readings") or []
    peak_reading = max(readings, key=lambda x: x["load"], default=None)
    reporting_days = len({x["date"] for x in readings})
    expected_days = (date.fromisoformat(period["period"]["end"]) - date.fromisoformat(period["period"]["start"])).days + 1
    peak_evidence = {"peak": peak_reading, "days": reporting_days, "expected_days": expected_days,
                     "samples": len(readings), "above": sum(x["load"] >= r["rated_max"] for x in readings),
                     "latest": max((x["timestamp"] for x in readings), default=None)}
    return render_template("transformer.html", period=period, r=r, peak_evidence=peak_evidence, followup_statuses=FOLLOWUP_STATUSES, chart_svg=review_chart_svg(r["chart"], period["period"]["start"], r["unit"], r["rated_max"]),
                           moving_range_svg=review_moving_range_svg(r["chart"], period["period"]["start"], r["unit"]), moving_range_caption=review_moving_range_caption(r["chart"], r["unit"]),
                           chart_caption=review_chart_caption(r["chart"], r["unit"]), checklist=checklist, cause=cause, why=explain.why_flagged(r, pb),
                           decisions=DECISIONS, decision_chips=DECISION_CHIPS, review_started_at=now_iso(), playbook=pb, summary=summary, case=case,
                           back=url_for("period_map", period_id=period_id) if request.args.get("from") == "map" else None)


@app.post("/periods/<period_id>/transformers/<tid>/followup")
def save_followup(period_id, tid):
    r = store.get_transformer_result(period_id, tid)
    if not r:
        abort(404)
    fields = {k: request.form.get(k, "").strip() for k in ("action", "owner", "due_date", "status", "notes")}
    if fields["status"] not in FOLLOWUP_STATUSES:
        abort(400, "Unknown follow-up status")
    try:
        date.fromisoformat(fields["due_date"])
    except ValueError:
        abort(400, "Enter a valid follow-up date")
    if not fields["action"] or not fields["owner"]:
        abort(400, "Action and owner are required")
    for key, limit in (("action", 300), ("owner", 120), ("notes", 2000)):
        if check_text(fields[key], key, max_len=limit):
            abort(400, "Follow-up contains invalid text")
    store.record_followup(period_id, tid, r["input_hash"], **fields)
    flash("Follow-up saved. The analysis and review decision are unchanged.", "info")
    return redirect(url_for("transformer_detail", period_id=period_id, tid=tid) + "#followup")


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
    nxt = request.form.get("next", "")
    if nxt.startswith("/") and not nxt.startswith("//"):  # same-site only: back to the map when the review came from it
        return redirect(nxt)
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
def home():
    """The content root. With a finished period, the address stays /map."""
    if not store.list_periods(limit=1):
        return _render_map(None)
    return redirect(url_for("map_latest"))


@app.route("/map")
def map_latest():
    """The map of the latest period. The address does not include the period id."""
    periods = store.list_periods(limit=1)
    if not periods:
        return _render_map(None)
    return _render_map(periods[0]["period_id"])


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


@app.route("/charts")
def charts_latest():
    return redirect(url_for("dashboard"))


@app.route("/periods/<period_id>/charts")
def period_charts(period_id):
    if not store.get_period(period_id):
        abort(404)
    q = {k: v for k, v in request.args.items() if k in ("status", "stability", "area", "band") and v}
    q["period"] = period_id
    return redirect(url_for("dashboard", **q))


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
    pb = config.load_playbook()
    amb = thermal.load_ambient(config.FEEDS_DIR / config.OPTIONAL_FEED_FILES["ambient"])
    hours = [thermal.ambient_at(amb, f"{date_iso}T{h:02d}:00:00", thermal.params(pb)[0]["ambient_c"]) for h in range(24)]
    recorded = sum(1 for _, ok in hours if ok)
    hot = thermal.day_hot_spots(data, [a for a, _ in hours], thermal.asset_table(config.FEEDS_DIR / config.FEED_FILES["assets"]), pb, heat.previous_recorded_day(date_iso), date_iso)
    return {"date": date_iso, "modeled": False, "loads": data, "transformers": len(data),
            "hot_spot": hot, "hot_spot_modeled": True, "ambient": [round(a, 1) for a, _ in hours],
            "ambient_source": "recorded ambient feed" if recorded == 24 else (f"ambient feed for {recorded} of 24 hours" if recorded else "fixed playbook ambient (no feed)")}


@app.route("/api/heat/seasonal")
def api_heat_seasonal():
    try:
        month = int(request.args.get("month", "1"))
    except ValueError:
        abort(400)
    if not 1 <= month <= 12:
        abort(400)
    pb = config.load_playbook()
    out = heat.seasonal_day(month, pb)
    # a typical day: the same loads as yesterday, so the oil starts warm
    out["hot_spot"] = thermal.day_hot_spots(out["loads"], out["ambient"], thermal.asset_table(config.FEEDS_DIR / config.FEED_FILES["assets"]), pb, out["loads"], f"2000-{month:02d}-15")
    out.update({"hot_spot_modeled": True, "ambient_source": "typical for the month and hour (playbook)"})
    return out


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
    """Setup now lives on the Docs page; the address is kept for old links and the reviewer-name form."""
    if request.method == "POST":
        name = request.form.get("reviewer_name", "").strip()
        if check_text(name, "reviewer", max_len=120):
            flash("Reviewer name rejected by the input check.", "error")
        else:
            store.set_setting("reviewer_name", name)
            flash("Saved.", "info")
    return redirect(url_for("docs") + "#setup")


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
        flash("AI explanations are off. Turn them on under Docs › Setup.", "error")
    elif not ai_explain.cli_path():
        flash("The claude command-line tool was not found on this computer.", "error")
    else:
        rec = ai_explain.explain_alert_record(store, alert, force=True)
        flash("A plainer explanation is ready." if rec else "No usable plainer version came back; the fixed-rule text stays. See Docs › Setup for details.", "info" if rec else "error")
    return redirect(request.referrer or url_for("alerts"))


@app.post("/setup/ai")
def setup_ai():
    on = request.form.get("ai_explanations") == "on"
    store.set_setting(ai_explain.SETTING_KEY, "on" if on else "off")
    flash("AI explanations turned " + ("on." if on else "off."), "info")
    return redirect(url_for("docs") + "#setup")


@app.route("/alerts")
def alerts():
    show = request.args.get("show", "open")
    show = show if show in ("open", "acked", "all") else "open"
    every = store.list_alerts(limit=200)
    opened = [a for a in every if not a["acknowledged_at"]]
    acked = [a for a in every if a["acknowledged_at"]]
    shown = {"open": opened, "acked": acked, "all": every}[show]
    return render_template("alerts.html", alerts=shown, show=show, n_open=len(opened), n_acked=len(acked))


@app.route("/metrics")
def metrics():
    return render_template("metrics.html", m=store.review_metrics())


@app.route("/docs")
def docs():
    """Rules, data, API and citation, read from the live playbook and decision table so the page cannot drift."""
    from capacity_monitor.pipeline import load_decision_table

    pb = config.load_playbook()
    example = None
    periods = store.list_periods(limit=1)
    if periods:
        flagged = [r for r in store.get_transformer_results(periods[0]["period_id"]) if r["status"] != "within_limits"]
        if flagged:
            example = {"period": periods[0]["period_id"], "tid": flagged[0]["transformer_id"]}
    days = heat.dates()
    env = {k: ("set" if os.environ.get(k) else "not set") for k in ("CAPMON_ALERT_TO", "CAPMON_SMTP_HOST", "CAPMON_SMTP_USER", "CAPMON_SMTP_PASSWORD")}
    return render_template(
        "docs.html",
        playbook=pb,
        table=load_decision_table(playbook=pb),
        feeds=feed_status(),
        optional_feeds=optional_feed_status(),
        feeds_dir=str(config.FEEDS_DIR),
        example=example,
        heat_date=days[-1] if days else date.today().isoformat(),
        sched=airflow_client.status(),
        env=env,
        db=str(config.DB_PATH),
        reports=str(config.REPORTS_DIR),
        ai=ai_explain.status(store),
    )


TEAM = [
    {"slug": "spencer", "name": "Spencer Witt", "initials": "SW", "role": "Developer · data and workflow",
     "did": "Replaced the synthetic map rectangles with NYS municipal boundaries, added the transformer follow-up workflow, reworked the review layout, improved accessibility, and documented the chart methods."},
    {"slug": "ashwin", "name": "Ashwin Prajeeth", "initials": "AP", "role": "Developer · review app and rules",
     "did": "Built the fixed-rules pipeline, the decision table and its three tiers, the map and its heat views, the review pages with the modeled transformer cutaway, and the synthetic datasets."},
    {"slug": "daoming", "name": "Daoming Zhang", "initials": "DZ", "role": "Developer · deployment and map experience",
     "did": "Published the review app to Posit Connect from GitHub Actions, added the first-visit tour and the county seal, refined the dashboard and the map's review screens, and committed the finished analysis so a checkout opens ready to read."},
    {"slug": "abdullah", "name": "Abdullah Saleh Alnamlah", "initials": "AA", "role": "Team member",
     "did": "Member of the MAE 5930 project team."},
]


def _headshot(slug: str) -> str | None:
    """Static path of the first headshot found for a team member, or None (the page then shows initials)."""
    for ext in ("jpg", "jpeg", "png", "webp"):
        if (Path(app.static_folder) / "team" / f"{slug}.{ext}").exists():
            return f"team/{slug}.{ext}"
    return None


@app.route("/about")
def about():
    team = [dict(m, photo=_headshot(m["slug"])) for m in TEAM]
    return render_template("about.html", playbook=config.load_playbook(), team=team)


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


@app.route("/api/periods/<period_id>/transformers/<tid>/thermal")
def api_transformer_thermal(period_id, tid):
    """Modeled oil and hot-spot temperatures for the week, for the review page's 3D view. Not a decision input."""
    r = store.get_transformer_result(period_id, tid)
    if not r:
        abort(404)
    kind = thermal.kind_of(r.get("name"))
    asset = thermal.asset_record(config.FEEDS_DIR / config.FEED_FILES["assets"], tid)
    ambient = thermal.load_ambient(config.FEEDS_DIR / config.OPTIONAL_FEED_FILES["ambient"])
    out = thermal.simulate(r["period_readings"], r["rated_max"], config.load_playbook(), kind=kind, asset=asset, ambient=ambient)
    out.update({"transformer_id": tid, "rating": r["rated_max"], "unit": r["unit"], "kind": kind})
    return out


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


@app.get("/health")
def health():
    """Posit Connect deploy check. No data, no login."""
    return {"ok": True}


if __name__ == "__main__":
    port = int(os.environ.get("CAPMON_APP_PORT", "5055"))
    config.ensure_dirs()
    app.run(host="127.0.0.1", port=port, debug=False, threaded=True)
