"""Step 14: save the period-specific monitoring report (JSON, Markdown, HTML).

Writes go to data/reports/<period_id>/ and are replaced on rerun; every run's copy is
also kept under history/ for audit. Output passes the PII filter before it is written.
"""

from __future__ import annotations

import json
from html import escape
from pathlib import Path

from . import config
from .charts import imr_svg
from .guards import redact_structure
from .store import Store, now_iso


def _fmt(v, nd=2):
    if v is None:
        return "-"
    if isinstance(v, float):
        return f"{v:,.{nd}f}"
    return str(v)


def build_report(store: Store, period_id: str) -> dict:
    period = store.get_period(period_id)
    if not period:
        raise ValueError(f"No results for period {period_id}")
    results = store.get_transformer_results(period_id)
    real = [r for r in results if not r["is_calibration"]]
    exceptions = [r for r in real if r["status"] != "within_limits"]
    report = {
        "title": f"Transformer capacity monitoring report, period ending {period_id}",
        "generated_at": now_iso(),
        "report_status": period["status"],
        "finalized_by": period.get("finalized_by"),
        "finalized_at": period.get("finalized_at"),
        "run_id": period["run_id"],
        "rerun_count": period["rerun_count"],
        "period": period["period"],
        "summary": period["summary"],
        "sources": period["sources"],
        "warnings": period["warnings"],
        "playbook_version": config.load_playbook().get("version"),
        "calibration_cases_in_queue": sum(1 for r in results if r["is_calibration"]),
        "transformers": [],
    }
    for r in real:
        disp = r.get("disposition")
        report["transformers"].append(
            {
                "transformer_id": r["transformer_id"],
                "name": r["name"],
                "area": f"{r['area_name']} ({r['area_id']})" if r["area_id"] else "",
                "rated_max": r["rated_max"],
                "unit": r["unit"],
                "stability": r["stability"],
                "chart_signals": r["chart"]["signals"],
                "chart_limits": {k: r["chart"].get(k) for k in ("center", "ucl", "lcl", "mr_bar", "mr_ucl", "n_baseline", "n_points")},
                "period_peak": r["capacity"]["period_peak"],
                "period_peak_ratio": r["capacity"]["period_peak_ratio"],
                "cpk": r["capacity"]["cpk"],
                "cpk_ci": [r["capacity"]["cpk_ci_low"], r["capacity"]["cpk_ci_high"]],
                "projected_peak": r["capacity"]["projected_peak"],
                "forecast_ratio": r["capacity"]["forecast_ratio"],
                "forecast_assumptions": r["projection"]["assumptions"],
                "status": r["status"],
                "decision_rule": r["decision"],
                "disposition": {k: disp[k] for k in ("decision", "notes", "reviewer", "recorded_at")} if disp else None,
                "daily_peaks": dict(zip(r["chart"]["dates"], r["chart"]["values"])),
            }
        )
    report["exceptions_total"] = len(exceptions)
    report["exceptions_with_disposition"] = sum(1 for r in exceptions if r.get("disposition"))
    return redact_structure(report)


def _markdown(rep: dict) -> str:
    L = [f"# {rep['title']}", "", f"Status: **{rep['report_status'].upper()}**" + (f" (finalized by {rep['finalized_by']} at {rep['finalized_at']})" if rep["finalized_by"] else " (not yet finalized by a reviewer)"), ""]
    L += [f"- Period: {rep['period']['start']} to {rep['period']['end']} ({rep['period']['days']} days); chart history from {rep['period']['history_start']}", f"- Run: {rep['run_id']} (reruns of this period: {rep['rerun_count']})", f"- Playbook version: {rep['playbook_version']}", f"- Generated: {rep['generated_at']}", ""]
    s = rep["summary"]
    L += ["## Summary", "", f"| Transformers | Within limits | Review needed | Inspect now | Stable | Chart signal | Insufficient history |", "|---|---|---|---|---|---|---|", f"| {s.get('transformers',0)} | {s.get('within_limits',0)} | {s.get('review_needed',0)} | {s.get('inspect_now',0)} | {s.get('stable',0)} | {s.get('signal',0)} | {s.get('insufficient_history',0)} |", ""]
    L += [f"Exceptions with a recorded disposition: {rep['exceptions_with_disposition']} of {rep['exceptions_total']}", ""]
    L += ["## Sources", ""] + [f"- {k}: `{v['path']}` ({v['rows']} rows, sha256 {v['sha256']}, modified {v['modified']})" for k, v in rep["sources"].items()] + [""]
    if rep["warnings"]:
        L += ["## Warnings", ""] + [f"- {w}" for w in rep["warnings"]] + [""]
    L += ["## Transformers", "", "| Transformer | Area | Rated max | Period peak | Stability | Cpk (95% CI) | Projected peak | Status | Disposition |", "|---|---|---|---|---|---|---|---|---|"]
    for t in rep["transformers"]:
        ci = f"{_fmt(t['cpk'])} ({_fmt(t['cpk_ci'][0])} to {_fmt(t['cpk_ci'][1])})" if t["cpk"] is not None else "not calculated"
        d = t["disposition"]
        L.append(f"| {t['transformer_id']} {t['name']} | {t['area']} | {_fmt(t['rated_max'],1)} {t['unit']} | {_fmt(t['period_peak'],1)} | {t['stability']} | {ci} | {_fmt(t['projected_peak'],1)} | {t['status']} | {(d['decision'] + ' by ' + d['reviewer']) if d else '-'} |")
    L.append("")
    for t in rep["transformers"]:
        if t["status"] == "within_limits":
            continue
        L += [f"### {t['transformer_id']} {t['name']}", "", f"- Why flagged: rule {t['decision_rule']['rule']}: {t['decision_rule']['reason']}"]
        for sgn in t["chart_signals"]:
            L.append(f"- Chart signal: {sgn['rule']} on {sgn['date']} (value {_fmt(sgn['value'],1)})")
        L.append(f"- Forecast assumptions: {json.dumps(t['forecast_assumptions'])}")
        if t["disposition"]:
            L.append(f"- Disposition: {t['disposition']['decision']} by {t['disposition']['reviewer']} at {t['disposition']['recorded_at']}: {t['disposition']['notes'] or ''}")
        else:
            L.append("- Disposition: none recorded yet")
        L.append("")
    L += ["---", "This report was produced by fixed rules (no AI). It does not change any equipment or operating setting."]
    return "\n".join(L)


def _html(rep: dict, results_by_id: dict) -> str:
    rows = []
    for t in rep["transformers"]:
        r = results_by_id.get(t["transformer_id"])
        svg = imr_svg(r["chart"], rep["period"]["start"], r["unit"], r["rated_max"]) if r else ""
        ci = f"{_fmt(t['cpk'])} ({_fmt(t['cpk_ci'][0])} to {_fmt(t['cpk_ci'][1])})" if t["cpk"] is not None else "not calculated"
        d = t["disposition"]
        rows.append(
            f"<section class='t'><h3>{escape(t['transformer_id'])} {escape(t['name'])} <span class='tag {t['status']}'>{t['status'].replace('_',' ')}</span></h3>"
            f"<p>Area {escape(t['area'])} | Rated max {_fmt(t['rated_max'],1)} {escape(t['unit'])} | Period peak {_fmt(t['period_peak'],1)} | Stability {t['stability']} | Cpk {ci} | Projected peak {_fmt(t['projected_peak'],1)}</p>"
            f"<p>Rule {escape(str(t['decision_rule']['rule']))}: {escape(t['decision_rule']['reason'])}</p>"
            + (f"<p><b>Disposition:</b> {escape(d['decision'])} by {escape(d['reviewer'])} at {escape(d['recorded_at'])}<br>{escape(d['notes'] or '')}</p>" if d else "<p><i>No disposition recorded</i></p>")
            + f"<details><summary>Control chart and forecast assumptions</summary>{svg}<pre>{escape(json.dumps(t['forecast_assumptions'], indent=1))}</pre></details></section>"
        )
    s = rep["summary"]
    return f"""<!doctype html><html><head><meta charset='utf-8'><title>{escape(rep['title'])}</title>
<link rel='stylesheet' href='https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@600&family=Lora:wght@400;600&display=swap'><style>body{{font:14px/1.55 Lora,Georgia,serif;margin:0;padding:32px clamp(20px,5vw,72px);max-width:1100px;background:#1a1919;color:#f3f1e8}} h1,h2,h3{{font-family:'Cormorant Garamond',Georgia,serif;font-weight:600;line-height:1.15}} h1{{font-size:34px}} a{{color:#e1ad66}} .tag{{display:inline-block;padding:2px 9px;border-radius:999px;font-size:11px;letter-spacing:.03em;border:1px solid currentColor;vertical-align:middle}} .within_limits{{color:#57b57f}} .review_needed{{color:#e1ad66}} .inspect_now{{color:#ff6b7a}} section.t{{border-top:1px solid rgba(243,241,232,.12);padding:12px 0}} .status{{font-weight:600;color:#e1ad66}} ul{{padding-left:20px}} pre{{background:#262525;border:1px solid rgba(243,241,232,.12);padding:12px;border-radius:4px;overflow:auto;font-size:12px}} details summary{{cursor:pointer;color:#e1ad66}} svg{{background:#f6f4ee;border-radius:8px;padding:8px;max-width:100%}} small{{color:#aeaba3}}</style></head><body>
<h1>{escape(rep['title'])}</h1>
<p class='status'>Status: {escape(rep['report_status'].upper())}{(' - finalized by ' + escape(rep['finalized_by']) + ' at ' + escape(rep['finalized_at'])) if rep['finalized_by'] else ' - not yet finalized by a reviewer'}</p>
<p>Period {rep['period']['start']} to {rep['period']['end']} | Run {escape(rep['run_id'])} | Reruns {rep['rerun_count']} | Playbook {escape(str(rep['playbook_version']))} | Generated {rep['generated_at']}</p>
<p>Transformers {s.get('transformers',0)} | Within limits {s.get('within_limits',0)} | Review needed {s.get('review_needed',0)} | Inspect now {s.get('inspect_now',0)} | Dispositions {rep['exceptions_with_disposition']} of {rep['exceptions_total']}</p>
<h2>Sources</h2><ul>{''.join(f"<li>{escape(k)}: {escape(v['path'])} ({v['rows']} rows, sha256 {v['sha256']}, modified {v['modified']})</li>" for k, v in rep['sources'].items())}</ul>
{('<h2>Warnings</h2><ul>' + ''.join(f'<li>{escape(w)}</li>' for w in rep['warnings']) + '</ul>') if rep['warnings'] else ''}
<h2>Transformers</h2>{''.join(rows)}
<p><small>Produced by fixed rules (no AI). This report does not change any equipment or operating setting.</small></p></body></html>"""


def write_report(store: Store, period_id: str, run_id: str | None = None) -> dict:
    """Write/replace data/reports/<period_id>/report.{json,md,html} and keep a history copy."""
    rep = build_report(store, period_id)
    results_by_id = {r["transformer_id"]: r for r in store.get_transformer_results(period_id)}
    out_dir = config.REPORTS_DIR / period_id
    hist = out_dir / "history"
    out_dir.mkdir(parents=True, exist_ok=True)
    hist.mkdir(exist_ok=True)
    (out_dir / "report.json").write_text(json.dumps(rep, indent=1, default=str), encoding="utf-8")
    (out_dir / "report.md").write_text(_markdown(rep), encoding="utf-8")
    (out_dir / "report.html").write_text(_html(rep, results_by_id), encoding="utf-8")
    tag = f"{run_id or rep['run_id']}-{rep['report_status']}"
    (hist / f"{tag}.json").write_text(json.dumps(rep, indent=1, default=str), encoding="utf-8")
    return {"dir": str(out_dir), "files": ["report.json", "report.md", "report.html"], "status": rep["report_status"]}
