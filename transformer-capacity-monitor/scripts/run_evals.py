#!/usr/bin/env python3
"""Run the evaluation cases in evals/examples.csv against the pipeline and write evals/results.md.

Each case maps to a scenario of the synthetic generator or to an action in the store. Results are
observed outcomes, not a checklist. Runs in an isolated temporary CAPMON_HOME so it never touches
the owner's live database or reports.
"""

from __future__ import annotations

import csv
import os
import subprocess
import sys
import tempfile
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
END = "2026-10-15"


def main():
    tmp = Path(tempfile.mkdtemp(prefix="capmon-evals-"))
    (tmp / "rules").mkdir()
    for f in ("playbook.json", "decision-table.csv"):
        (tmp / "rules" / f).write_bytes((ROOT / "rules" / f).read_bytes())
    os.environ["CAPMON_HOME"] = str(tmp)
    os.environ.pop("CAPMON_DB", None)
    sys.path.insert(0, str(ROOT))
    from capacity_monitor import config
    from capacity_monitor.run import execute_run
    from capacity_monitor.store import Store

    config.ensure_dirs()

    def gen(scenario):
        subprocess.run([sys.executable, str(ROOT / "scripts/make_synthetic_data.py"), "--scenario", scenario, "--end", END], check=True, capture_output=True, env=dict(os.environ, PYTHONPATH=str(ROOT)))

    def fresh_store():
        if config.DB_PATH.exists():
            for p in config.DB_PATH.parent.glob(config.DB_PATH.name + "*"):
                p.unlink()
        return Store()

    rows = list(csv.DictReader(open(ROOT / "evals/examples.csv", encoding="utf-8")))
    out = []
    for row in rows:
        cid = row["id"]
        if cid == "1":
            gen("boundary-mismatch"); st = fresh_store(); run = execute_run(END, "eval", st)
            ok = run["status"] == "failed" and run["current_step"] == 7 and any("different reporting period" in p for p in run["problems"]) and st.get_period(END) is None and st.list_alerts()
            obs = f"run {run['status']} at step {run['current_step']}; problem: {next((p for p in run['problems'] if 'period' in p), '')[:110]}; no period results saved; alert recorded"
        elif cid == "2":
            gen("normal"); st = fresh_store(); run = execute_run(END, "eval", st)
            r = {x["transformer_id"]: x for x in st.get_transformer_results(END)}["T-DRY-004"]
            ok = r["stability"] == "signal" and r["capacity"]["cpk"] is None and r["capacity"]["period_peak_ratio"] < 1 and r["status"] == "review_needed"
            obs = f"T-DRY-004 stability={r['stability']}, signals={[s['rule'] for s in r['chart']['signals']][:2]}, cpk={r['capacity']['cpk']}, period peak {r['capacity']['period_peak_ratio']:.0%} of rating, status={r['status']}"
        elif cid == "3":
            gen("normal"); st = fresh_store(); run = execute_run(END, "eval", st)
            r = {x["transformer_id"]: x for x in st.get_transformer_results(END)}["T-LAN-005"]
            c = r["capacity"]
            ok = r["decision"]["rule"] == "8" and r["status"] == "review_needed"
            obs = f"T-LAN-005 cpk={c['cpk']:.2f} CI [{c['cpk_ci_low']:.2f}, {c['cpk_ci_high']:.2f}] threshold 1.33 -> rule {r['decision']['rule']} ({r['decision']['reason'][:50]}); review_needed"
        elif cid == "4":
            gen("normal"); st = fresh_store(); run = execute_run(END, "eval", st)
            r = {x["transformer_id"]: x for x in st.get_transformer_results(END)}["T-CAR-006"]
            c = r["capacity"]; a = r["projection"]["assumptions"]
            ok = r["decision"]["rule"] == "9" and c["forecast_ratio"] > 1 and c["period_peak_ratio"] < 1
            obs = f"T-CAR-006 period peak {c['period_peak_ratio']:.0%} of rating, projected peak {c['forecast_ratio']:.0%} of rating ({a['forecast_version']}, {a['horizon']}, allocation {a['allocation_method']}) -> rule 9; disposition required before finalize"
        elif cid == "5":
            gen("normal"); st = fresh_store(); r1 = execute_run(END, "eval", st); st.finalize_period(END, "Eval reviewer"); r2 = execute_run(END, "eval", st)
            periods = st.list_periods(); p = periods[0]
            ok = len(periods) == 1 and p["run_id"] == r2["run_id"] and p["rerun_count"] == 1 and p["status"] == "draft" and len([x for x in st.list_runs() if x["period_id"] == END]) == 2
            obs = f"{len(periods)} period record after rerun (run_id now {r2['run_id'][-12:]}), rerun_count={p['rerun_count']}, status back to {p['status']} for re-approval; {len([x for x in st.list_runs()])} run records kept"
        elif cid == "6":
            gen("normal"); st = fresh_store(); os.remove(config.FEEDS_DIR / "readings.csv"); run = execute_run(END, "eval", st)
            al = st.list_alerts()
            ok = run["status"] == "failed" and run["current_step"] == 2 and al and al[0]["period_id"] == END and st.get_period(END) is None
            obs = f"run {run['status']} at step {run['current_step']} ({run['error'][:60]}); alert {al[0]['level']} with run and period ids; no report available"
        else:
            ok, obs = False, "no mapping for this case id"
        out.append((cid, row["input"], row["good_result"], obs, ok))

    lines = [f"# Evaluation results", "", f"Run at {datetime.now().isoformat(timespec='seconds')} on synthetic feeds (period ending {END}), isolated home {tmp}.", "", "| # | Case | Expected | Observed | Pass |", "|---|---|---|---|---|"]
    for cid, inp, good, obs, ok in out:
        lines.append(f"| {cid} | {inp[:90]} | {good[:90]} | {obs} | {'PASS' if ok else 'FAIL'} |")
    passed = sum(1 for *_, ok in out if ok)
    lines += ["", f"**{passed} of {len(out)} cases passed.**", "", "Cases are the illustrative synthetic cases from evals/examples.csv; replace them with real past examples and rerun `python scripts/run_evals.py`."]
    (ROOT / "evals/results.md").write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines))
    return 0 if passed == len(out) else 1


if __name__ == "__main__":
    sys.exit(main())
