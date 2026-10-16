"""Log transformer loads and monitor capacity against limits across Tompkins County.

Airflow 3 DAG. Each task calls one step of capacity_monitor.run.RunContext; bulk data stays in
data/work/<run_id>/ and only a small reference dict travels through XCom. Period mapping:
  - scheduled run: the 7-day period ends the day before the run's data_interval_end (local date)
  - manual run: pass {"period_end": "YYYY-MM-DD"} in the trigger conf; otherwise the same rule applies
A rerun of the same period replaces that period's results (period-keyed upsert) and keeps every
run attempt in the run log. Failures mark the run failed in the app and raise an alert.

Dependency wait: the scaffold's ExternalTaskSensors pointed at placeholder import DAGs
(REPLACE_first_import_dag). Until upstream import DAGs exist, a feed-readiness sensor waits for
the four feed files and for readings that cover the period end. When the upstream jobs become
Airflow DAGs, replace `wait_for_feeds` with ExternalTaskSensor as shown at the bottom.
"""

from __future__ import annotations

import os
import re
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

ROOT = Path(os.environ.get("CAPMON_HOME", Path(__file__).resolve().parents[2]))
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pendulum  # noqa: E402
from airflow.sdk.exceptions import AirflowFailException  # noqa: E402
from airflow.sdk import Param, dag, task  # noqa: E402
from airflow.sdk.bases.sensor import PokeReturnValue  # noqa: E402

DAG_ID = "log_transformer_loads_and_monitor_capacity_again"
LOCAL_TZ = "America/New_York"


def _period_end_from_context(context) -> date:
    conf = (context.get("dag_run").conf or {}) if context.get("dag_run") else {}
    params = context.get("params") or {}
    explicit = conf.get("period_end") or params.get("period_end")
    if explicit:
        return date.fromisoformat(str(explicit))
    interval_end = context.get("data_interval_end") or context.get("logical_date") or pendulum.now(LOCAL_TZ)
    return (pendulum.instance(interval_end).in_tz(LOCAL_TZ) - timedelta(days=1)).date()


def _run_ref(context) -> dict:
    """Deterministic run id from the DAG run, so a failure callback can find the same run."""
    from capacity_monitor import config, sources

    period = sources.period_for(_period_end_from_context(context), config.load_playbook())
    dag_run_id = re.sub(r"[^A-Za-z0-9_.-]+", "-", context["dag_run"].run_id)
    return {"run_id": f"{period.period_id}_airflow_{dag_run_id}", "period": period.to_dict()}


def _ctx(ref: dict):
    from capacity_monitor.run import RunContext
    from capacity_monitor.sources import Period

    return RunContext(Period.from_dict(ref["period"]), ref["run_id"], "airflow")


def _step(fn_name: str, step_no: int):
    """Run one RunContext method; RunFailed fails the task without retries and marks the run failed."""

    def inner(ref: dict) -> dict:
        from capacity_monitor.guards import RunFailed

        ctx = _ctx(ref)
        try:
            getattr(ctx, fn_name)()
        except RunFailed as exc:
            ctx.fail(exc.step, exc.message, exc.problems)
            raise AirflowFailException(f"step {exc.step}: {exc.message}") from exc
        except Exception as exc:  # unexpected: let Airflow retry, but keep the run status honest
            ctx.store.step_done(ref["run_id"], step_no, "failed", {"error": repr(exc)})
            raise
        return ref

    inner.__name__ = fn_name
    return inner


def _on_dag_failure(context):
    """Preserve the failed status in the app and send the alert (worker-driven failures only)."""
    try:
        from capacity_monitor.notify import send_alert
        from capacity_monitor.store import Store

        ref = _run_ref(context)
        store = Store()
        run = store.get_run(ref["run_id"])
        if run and run["status"] == "running":
            store.finish_run(ref["run_id"], "failed", error=f"Airflow task failed: {context.get('task_instance').task_id}")
        send_alert(store, "error", f"Airflow DAG run {context['dag_run'].run_id} failed in task {context.get('task_instance').task_id}", run_id=ref["run_id"], period_id=ref["period"]["period_id"])
    except Exception as exc:  # noqa: BLE001
        print(f"failure callback error: {exc!r}")


@dag(
    dag_id=DAG_ID,
    schedule="0 6 * * 1,3,5",  # Monday, Wednesday, Friday 06:00 local (rules/playbook.json)
    start_date=pendulum.datetime(2026, 10, 1, tz=LOCAL_TZ),
    catchup=False,
    max_active_runs=1,
    default_args={"retries": 1, "retry_delay": timedelta(minutes=2), "execution_timeout": timedelta(minutes=20)},
    params={"period_end": Param(None, type=["null", "string"], description="Optional YYYY-MM-DD period end for a manual run")},
    on_failure_callback=_on_dag_failure,
    tags=["agent-architecture-guide", "fixed-rules", "tompkins-county"],
    doc_md=__doc__,
)
def log_transformer_loads_and_monitor_capacity_again():
    @task.sensor(poke_interval=300, timeout=int(timedelta(hours=6).total_seconds()), mode="reschedule", retries=0)
    def wait_for_feeds(**context) -> PokeReturnValue:
        """Readiness, not just a timer: all four feeds exist and readings reach the period end."""
        import csv

        from capacity_monitor import sources

        period_end = _period_end_from_context(context)
        if not sources.feeds_ready():
            return PokeReturnValue(is_done=False)
        latest = None
        with open(sources.feed_path("readings"), encoding="utf-8", newline="") as fh:
            for row in csv.DictReader(fh):
                try:
                    d = datetime.fromisoformat(row["timestamp"].strip()).date()
                except (KeyError, ValueError):
                    continue
                latest = d if latest is None or d > latest else latest
        ready = latest is not None and latest >= period_end
        return PokeReturnValue(is_done=ready, xcom_value={"latest_reading_date": str(latest), "period_end": str(period_end)})

    @task
    def step_1_scheduled_monitoring_run(**context) -> dict:
        ref = _run_ref(context)
        _ctx(ref).start()
        return ref

    step_2 = task(_step("load_readings", 2), task_id="step_2_load_transformer_readings")
    step_3 = task(_step("load_assets", 3), task_id="step_3_load_transformer_asset_records")
    step_4 = task(_step("load_boundaries", 4), task_id="step_4_load_local_boundaries")
    step_5 = task(_step("load_forecasts", 5), task_id="step_5_load_heat_pump_growth_forecasts")
    step_6 = task(_step("align", 6), task_id="step_6_align_the_run_inputs")
    step_7 = task(_step("check_completeness", 7), task_id="step_7_check_input_completeness")
    step_8 = task(_step("check_stability", 8), task_id="step_8_check_load_stability")
    steps_9_12 = task(_step("evaluate", 12), task_id="steps_9_to_12_stability_forecast_capability_decision")
    step_13 = task(_step("review_gate", 13), task_id="step_13_review_capacity_exceptions_in_app")
    step_14 = task(_step("save_report", 14), task_id="step_14_save_the_monitoring_report")
    step_15 = task(_step("complete", 15), task_id="step_15_monitoring_run_complete")

    ready = wait_for_feeds()
    ref = step_1_scheduled_monitoring_run()
    ready >> ref
    ref = step_2(ref)
    ref = step_3(ref)
    ref = step_4(ref)
    ref = step_5(ref)
    ref = step_6(ref)
    ref = step_7(ref)
    ref = step_8(ref)
    ref = steps_9_12(ref)
    ref = step_13(ref)
    ref = step_14(ref)
    step_15(ref)

    # When upstream feed imports are Airflow DAGs, wait for their specific runs instead:
    # from airflow.providers.standard.sensors.external_task import ExternalTaskSensor
    # wait_readings = ExternalTaskSensor(task_id="wait_for_readings_import", external_dag_id="readings_import",
    #                                    execution_delta=timedelta(hours=1), mode="reschedule",
    #                                    timeout=int(timedelta(hours=6).total_seconds()))
    # wait_readings >> ref   (document the upstream cadence and date alignment before enabling)


log_transformer_loads_and_monitor_capacity_again()
