#!/usr/bin/env python3
"""Run the tool on one demonstration dataset and print what a reviewer would see.

Each demo dataset is one scenario of scripts/make_synthetic_data.py (all SYNTHETIC data):

  normal             12 transformers, every review rule exercised (stable, signal, low Cpk,
                     uncertain Cpk, forecast exception, insufficient history, area overlap)
  boundary-mismatch  the boundary file is valid for 2025 only, so the run must stop at step 7
  missing-rating     one transformer has no rated maximum, so the run must stop at step 7

Usage:
  python scripts/run_demo.py normal
  python scripts/run_demo.py boundary-mismatch
  python scripts/run_demo.py missing-rating

Runs in a temporary folder, so it never touches data/feeds/ or the review app's database.
"""

from __future__ import annotations

import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
END = "2026-10-15"
SCENARIOS = ("normal", "boundary-mismatch", "missing-rating")


def main(argv: list[str]) -> int:
    scenario = argv[1] if len(argv) > 1 else "normal"
    if scenario not in SCENARIOS:
        print(f"unknown scenario {scenario!r}; choose one of {', '.join(SCENARIOS)}")
        return 2
    home = Path(tempfile.mkdtemp(prefix=f"capmon-demo-{scenario}-"))
    (home / "rules").mkdir()
    for f in ("playbook.json", "decision-table.csv"):
        (home / "rules" / f).write_bytes((ROOT / "rules" / f).read_bytes())
    os.environ["CAPMON_HOME"] = str(home)
    os.environ.pop("CAPMON_DB", None)
    sys.path.insert(0, str(ROOT))
    subprocess.run([sys.executable, str(ROOT / "scripts" / "make_synthetic_data.py"), "--scenario", scenario, "--end", END],
                   check=True, capture_output=True, env=dict(os.environ, PYTHONPATH=str(ROOT)))

    from capacity_monitor import config
    from capacity_monitor.run import execute_run
    from capacity_monitor.store import Store

    config.ensure_dirs()
    run = execute_run(END, "demo", Store())
    print(f"Demo dataset: {scenario} (SYNTHETIC), period ending {END}")
    print(f"Run status: {run['status']}, stopped at step {run['current_step']}")
    if run["status"] == "failed":
        print("Blocking problems:")
        for p in run["problems"]:
            if not p.startswith("warning:"):
                print(f"  - {p}")
        print("How to read this: the run refused to analyse incomplete or mismatched inputs; no report was written.")
        return 0

    rows = Store().get_transformer_results(END)
    print()
    print(f"{'transformer':<11} {'stability':<21} {'Cpk':>5} {'95% CI':>13} {'peak/rating':>11} {'forecast/rating':>15}  rule  outcome")
    for r in sorted(rows, key=lambda x: x["transformer_id"]):
        c = r["capacity"]
        cpk = f"{c['cpk']:.2f}" if c["cpk"] is not None else "-"
        ci = f"[{c['cpk_ci_low']:.2f},{c['cpk_ci_high']:.2f}]" if c["cpk"] is not None else "-"
        pk = f"{c['period_peak_ratio']:.0%}" if c["period_peak_ratio"] is not None else "-"
        fc = f"{c['forecast_ratio']:.0%}" if c["forecast_ratio"] is not None else "-"
        print(f"{r['transformer_id']:<11} {r['stability']:<21} {cpk:>5} {ci:>13} {pk:>11} {fc:>15}  {r['decision']['rule']:>4}  {r['status']}")
    n_rev = sum(1 for r in rows if r["status"] == "review_needed")
    n_insp = sum(1 for r in rows if r["status"] == "inspect_now")
    print()
    print(f"{len(rows)} transformers: {len(rows) - n_rev - n_insp} within limits, {n_rev} need review (amber), {n_insp} need an inspection now (red).")
    print("How to read this: 'rule' is the first matching row of rules/decision-table.csv; every flagged (amber or red)")
    print("transformer waits for a named reviewer's disposition before the period report can be finalized.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
