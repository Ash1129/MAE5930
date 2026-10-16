# Developer notes

## Layout

| Path | Purpose |
|---|---|
| `capacity_monitor/` | Fixed-rules pipeline (standard library only). `sources.py` steps 2-5, `pipeline.py` steps 6-12, `run.py` orchestration and step 13-15 bookkeeping, `report.py` step 14, `store.py` SQLite, `guards.py` guardrails, `charts.py` SVG, `airflow_client.py` scheduler status/pause/trigger via the Airflow REST API, `notify.py` alerts. |
| `airflow/dags/log_transformer_loads_and_monitor_capacity_again.py` | Airflow 3 DAG: feed-readiness sensor, then one task per step calling `RunContext`. Small JSON references via XCom; bulk data in `data/work/<run_id>/`. |
| `webapp/` | Flask review app (port 5055): intake, run progress, exception review, backend-enforced finalization, scheduler status and pause, setup, alerts, metrics. |
| `rules/playbook.json`, `rules/decision-table.csv` | Approved thresholds and the first-match-wins review decision table. |
| `data/feeds/` | Input feeds (synthetic until replaced). `data/reports/<period>/` outputs. `data/capacity_monitor.sqlite3` run log, results, dispositions, alerts. |
| `scripts/` | `setup_env.sh` (venv + Airflow + Flask), `env.sh`, `start_app.sh`, `start_airflow.sh`, `stop.sh`, `status.sh`, `make_synthetic_data.py`, `run_evals.py`. |
| `tests/` | pytest: pipeline units, end-to-end runs and failure cases, web user path including the approval bypass attempt. |

## Run locally

```bash
./scripts/setup_env.sh        # once
./scripts/start_airflow.sh    # scheduler + Airflow UI on :8080 (admin password in airflow_home/simple_auth_manager_passwords.json.generated)
./scripts/start_app.sh        # review app on :5055
.venv/bin/python -m pytest tests -q
.venv/bin/python scripts/run_evals.py
```

Airflow runs in `standalone` mode with `AIRFLOW_HOME=airflow_home/` (SQLite metadata, local executor). For
production use a managed Airflow or a proper deployment (Postgres metadata DB, separate scheduler, api-server,
dag-processor and triggerer, credentials in a secrets backend); re-test with that executor.

## Period mapping

A run covers `period_days` (7) days ending on `period_end`. Scheduled runs use the day before the run's
`data_interval_end` in America/New_York. Manual runs take `period_end` from the app form or the DAG run conf.
Control-chart history is `history_days` (60) before the period end. `period_id == period_end`.

## Idempotency and audit

`period_results` and `transformer_results` are keyed by period and replaced on rerun (status returns to draft,
`rerun_count` increments). Every attempt stays in `runs`/`run_steps`. Dispositions carry the `input_hash` of the
inputs reviewed; if a rerun changes a transformer's inputs the old disposition is kept in history but no longer
counts. Report files are overwritten in `data/reports/<period>/` with per-run copies in `history/`.

## Guardrails

Text fields in feeds and in review forms pass `guards.check_text` (length limit, blocked terms, instruction-like
text). Matching feed text is quarantined and reported as a warning; matching form input is refused. Report output
passes `redact_pii`. Loaders retry transient I/O errors `retries.max_attempts` times, then the run fails and an
alert is recorded (and e-mailed when `CAPMON_ALERT_TO`/`CAPMON_SMTP_*` are set).

## Connecting real feeds

Replace the file reads in `capacity_monitor/sources.py` (`_read_csv`, `_read_geojson`) with the connector calls
and keep the returned row shape. Keep the validity metadata (boundary `valid_from/valid_to`, forecast
`forecast_version`) so step 7 can refuse mismatched partitions. When upstream imports are Airflow DAGs, swap the
readiness sensor for `ExternalTaskSensor` (template at the bottom of the DAG file).
