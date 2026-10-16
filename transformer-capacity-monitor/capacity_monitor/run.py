"""Run orchestration: steps 1-15 in order, each recorded in the store.

`execute_run` is used by the review app's Run now button and by tests. The Airflow DAG
calls the same `RunContext` step methods one task at a time, handing on small JSON
references through the work directory (data/work/<run_id>/).
"""

from __future__ import annotations

import hashlib
import json
import traceback
from datetime import date, datetime

from . import config, pipeline, sources
from .guards import RunFailed
from .notify import send_alert
from .report import write_report
from .sources import Period
from .store import Store


def new_run_id(period: Period, triggered_by: str) -> str:
    return f"{period.period_id}_{datetime.now().strftime('%Y%m%dT%H%M%S%f')[:-3]}_{triggered_by}"


def _input_hash(t: dict) -> str:
    payload = json.dumps(
        {"peaks": t["daily_peaks"], "rating": t["rated_max"], "unit": t["unit"], "customers": t["customers"], "forecast": t.get("forecast"), "area": t["area_id"]},
        sort_keys=True,
        default=str,
    )
    return hashlib.sha256(payload.encode()).hexdigest()[:16]


def calibration_due(period: Period, playbook: dict) -> bool:
    n = int(playbook.get("review", {}).get("known_wrong_seed_every_n_periods", 0) or 0)
    if n <= 0:
        return False
    return (period.end.toordinal() // max(period.days, 1)) % n == 0


def make_calibration_case(results: dict, period: Period) -> dict | None:
    """A deliberately wrong case for the review queue: the chart shows a reading above the rated
    maximum, but the numbers claim a comfortable margin. The reviewer should reject it."""
    stable = [r for r in results.values() if r["stability"] == "stable" and r["status"] == "within_limits"]
    if not stable:
        return None
    src = json.loads(json.dumps(stable[0]))
    cid = f"CAL-{period.period_id}"
    src["transformer_id"] = cid
    src["name"] = "Calibration check (routine)"
    last = src["chart"]["dates"][-1]
    bumped = src["rated_max"] * 1.06
    src["chart"]["values"][-1] = bumped
    if src["period_readings"]:
        src["period_readings"][-1] = dict(src["period_readings"][-1], load=bumped)
    src["status"] = "review_needed"
    src["decision"] = {"outcome": "review_needed", "rule": "9", "reason": "Forecast peak near or above the rated maximum (0.9 of rating or more)", "condition": "forecast_ratio >= 0.9"}
    src["capacity"]["cpk"] = 1.85
    src["capacity"]["cpk_ci_low"] = 1.52
    src["capacity"]["cpk_ci_high"] = 2.18
    src["capacity"]["period_peak_ratio"] = 0.78
    src["capacity"]["period_peak"] = src["rated_max"] * 0.78
    src["capacity"]["forecast_ratio"] = 0.91
    src["capacity"]["projected_peak"] = src["rated_max"] * 0.91
    src["input_hash"] = hashlib.sha256(f"{cid}{last}".encode()).hexdigest()[:16]
    return src


class RunContext:
    """Holds a run's identifiers and performs each step. State between steps lives in files."""

    def __init__(self, period: Period, run_id: str, triggered_by: str, store: Store | None = None, playbook: dict | None = None):
        self.period = period
        self.run_id = run_id
        self.triggered_by = triggered_by
        self.store = store or Store()
        self.playbook = playbook or config.load_playbook()
        self.work = config.WORK_DIR / run_id
        self.work.mkdir(parents=True, exist_ok=True)

    # -- file handoff helpers (small references go through XCom; bulk data stays on disk) --
    def _save(self, name: str, data) -> str:
        p = self.work / f"{name}.json"
        p.write_text(json.dumps(data, default=str), encoding="utf-8")
        return str(p)

    def _load(self, name: str):
        return json.loads((self.work / f"{name}.json").read_text(encoding="utf-8"))

    def start(self) -> dict:
        """Step 1: record the scheduled period and run identifier."""
        self.store.create_run(self.run_id, self.period.period_id, self.triggered_by)
        self.store.step_start(self.run_id, 1)
        self.store.step_done(self.run_id, 1, "success", {"period": self.period.to_dict(), "triggered_by": self.triggered_by})
        return {"run_id": self.run_id, "period": self.period.to_dict()}

    def _loader(self, step: int, name: str, fn) -> dict:
        self.store.step_start(self.run_id, step)
        try:
            data = fn(self.period, self.playbook)
        except RunFailed:
            raise
        except Exception as exc:
            raise RunFailed(step, f"{name}: {exc!r}") from exc
        ref = self._save(name, data)
        detail = {"source": data["source"], "meta": data["meta"], "problems": len(data["problems"])}
        self.store.step_done(self.run_id, step, "success", detail)
        return {"ref": ref, **detail}

    def load_readings(self):
        return self._loader(2, "readings", sources.load_readings)

    def load_assets(self):
        return self._loader(3, "assets", sources.load_assets)

    def load_boundaries(self):
        return self._loader(4, "boundaries", sources.load_boundaries)

    def load_forecasts(self):
        return self._loader(5, "forecast", sources.load_forecasts)

    def align(self) -> dict:
        self.store.step_start(self.run_id, 6)
        joined = pipeline.align_inputs(self.period, self._load("readings"), self._load("assets"), self._load("boundaries"), self._load("forecast"), self.playbook)
        ref = self._save("joined", joined)
        self.store.step_done(self.run_id, 6, "success", {"counts": joined["counts"], "unknown_reading_ids": joined["unknown_reading_ids"][:10]})
        return {"ref": ref, **joined["counts"]}

    def check_completeness(self) -> dict:
        self.store.step_start(self.run_id, 7)
        joined = self._load("joined")
        result = pipeline.check_completeness(joined, self.playbook)  # raises RunFailed on blocking problems
        self._save("joined", joined)  # quarantined text may have been replaced
        self._save("completeness", result)
        self.store.step_done(self.run_id, 7, "success", {"warnings": result["warnings"]})
        return {"warnings": len(result["warnings"])}

    def check_stability(self) -> dict:
        self.store.step_start(self.run_id, 8)
        charts = pipeline.check_stability(self._load("joined"), self.playbook)
        self._save("charts", charts)
        counts = {}
        for c in charts.values():
            counts[c["status"]] = counts.get(c["status"], 0) + 1
        self.store.step_done(self.run_id, 8, "success", counts)
        return counts

    def evaluate(self) -> dict:
        """Steps 9-12 (decision, projection, capability, decision table) recorded individually."""
        joined, charts = self._load("joined"), self._load("charts")
        table = pipeline.load_decision_table()
        for step in (9, 10, 11, 12):
            self.store.step_start(self.run_id, step)
        results = pipeline.evaluate_transformers(joined, charts, self.playbook, table)
        for tid, r in results.items():
            r["input_hash"] = _input_hash(joined["transformers"][tid])
        summary = pipeline.summarize(results)
        self.store.step_done(self.run_id, 9, "success", {"stable": summary.get("stable", 0), "signal": summary.get("signal", 0), "insufficient_history": summary.get("insufficient_history", 0)})
        self.store.step_done(self.run_id, 10, "success", {"projected": sum(1 for r in results.values() if r["capacity"]["projected_peak"] is not None)})
        self.store.step_done(self.run_id, 11, "success", {"cpk_calculated": sum(1 for r in results.values() if r["capacity"]["cpk"] is not None)})
        self.store.step_done(self.run_id, 12, "success", {"review_needed": summary.get("review_needed", 0), "within_limits": summary.get("within_limits", 0)})
        calibration_ids = set()
        if calibration_due(self.period, self.playbook):
            cal = make_calibration_case(results, self.period)
            if cal:
                results[cal["transformer_id"]] = cal
                calibration_ids.add(cal["transformer_id"])
        self.store.save_period_results(self.period.to_dict(), self.run_id, summary, joined["sources"], self._load("completeness")["warnings"], results, calibration_ids)
        self._save("summary", summary)
        return summary

    def review_gate(self) -> dict:
        """Step 13: a person reviews exceptions in the app. The run records whether it is waiting."""
        summary = self._load("summary")
        self.store.step_start(self.run_id, 13)
        if summary.get("review_needed", 0) > 0:
            self.store.step_done(self.run_id, 13, "waiting", {"exceptions": summary["review_needed"], "note": "Awaiting reviewer dispositions in the app"})
        else:
            self.store.step_done(self.run_id, 13, "success", {"exceptions": 0, "note": "No exceptions; report still needs reviewer finalization"})
        return {"exceptions": summary.get("review_needed", 0)}

    def save_report(self) -> dict:
        self.store.step_start(self.run_id, 14)
        info = write_report(self.store, self.period.period_id, self.run_id)
        self.store.step_done(self.run_id, 14, "success", info)
        return info

    def complete(self) -> dict:
        self.store.step_start(self.run_id, 15)
        summary = self._load("summary")
        self.store.step_done(self.run_id, 15, "success", {"report": f"data/reports/{self.period.period_id}/", "status": "draft report available; awaiting reviewer finalization"})
        self.store.finish_run(self.run_id, "success", summary=summary)
        return summary

    def fail(self, step: int, message: str, problems: list | None = None) -> None:
        self.store.step_done(self.run_id, step, "failed", {"error": message, "problems": problems or []})
        self.store.finish_run(self.run_id, "failed", error=message, problems=problems)
        send_alert(self.store, "error", f"Run {self.run_id} failed at step {step}: {message}" + (("\n" + "\n".join(problems[:20])) if problems else ""), run_id=self.run_id, period_id=self.period.period_id, step=step)


def execute_run(period_end: date | str, triggered_by: str = "manual", store: Store | None = None, playbook: dict | None = None, run_id: str | None = None) -> dict:
    """Run steps 1-15 for one period. Returns the run record (status success or failed)."""
    playbook = playbook or config.load_playbook()
    period = sources.period_for(period_end, playbook)
    run_id = run_id or new_run_id(period, triggered_by)
    ctx = RunContext(period, run_id, triggered_by, store, playbook)
    ctx.start()
    steps = [
        (2, ctx.load_readings), (3, ctx.load_assets), (4, ctx.load_boundaries), (5, ctx.load_forecasts),
        (6, ctx.align), (7, ctx.check_completeness), (8, ctx.check_stability), (9, ctx.evaluate),
        (13, ctx.review_gate), (14, ctx.save_report), (15, ctx.complete),
    ]
    for step, fn in steps:
        try:
            fn()
        except RunFailed as exc:
            ctx.fail(exc.step, exc.message, exc.problems)
            break
        except Exception as exc:  # noqa: BLE001
            ctx.fail(step, f"{exc!r}", [traceback.format_exc()[-1500:]])
            break
    return ctx.store.get_run(run_id)
