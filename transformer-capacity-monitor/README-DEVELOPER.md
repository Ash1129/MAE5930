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

## Statistics (what the numbers mean and their limits)

- **Chart**: individuals and moving-range chart on one value per day (the daily peak). Limits from the baseline days before the period (E2 = 2.66, D4 = 3.267, d2 = 1.128). Run rules: beyond 3 sigma, 2 of 3 beyond 2 sigma, 8 in a row one side, moving range beyond its limit. Constant data gives `zero_variation`; fewer than `min_history_points` baseline days gives `insufficient_history`.
- **Cpk**: one-sided Cpu = (rating - mean) / (3 sigma), sigma = MRbar / d2 over the window. Reported only for stable charts with at least `min_points` values.
- **Interval**: Bissell's approximation, half-width z x sqrt(1/(9n) + Cpk^2 / (2 df)), with df = `mr_effective_df_factor` x (n-1) = 0.62(n-1), the effective degrees of freedom of the average-moving-range estimator (Wheeler). `tests/test_pipeline.py` checks coverage by simulation (about 95%; n-1 would give about 88%).
- **Assumptions**: a conventional Cpk reading needs independent, roughly normal observations (NIST/SEMATECH e-Handbook 6.1.6). The tool checks lag-1 autocorrelation (band +/- 2/sqrt(n)) and Jarque-Bera normality (alpha `normality_alpha`). A failed check routes the case to review (decision-table rule 6). Seasonality and weather effects over the 60-day window are not modeled; that is a known limitation for the reviewer to weigh.
- **Forecast units**: heat-pump demand is real power (kW). For assets rated in kVA the added kW is divided by `forecast.power_factor` before it is added to the period peak; kW-rated assets add directly. The factor and note are in every result's forecast assumptions.
- **Tiers**: the decision table gives three outcomes. `inspect_now` (red) when a reading reaches the rating, when one of `chart.inspect_rules` (8 in a row on one side, 2 of 3 beyond 2 sigma) fires in the period, or when `chart.inspect_outliers_at` or more days in the period carry an isolated outlier (beyond 3 sigma or a moving-range spike); `review_needed` (amber) for fewer outliers or any capacity, assumption, history or forecast concern; otherwise `within_limits`. `pipeline.signal_counts` supplies the `inspect_signals` and `outlier_signals` facts.
- **Inside the transformer (modeled)**: `capacity_monitor/thermal.py` runs the IEEE C57.91 clause-7 exponential model hour by hour on the period readings (top-oil rise with a time constant, hot-spot rise as K^2m, ageing factor). `GET /api/periods/<id>/transformers/<tid>/thermal` serves it; the review page draws a three.js cutaway (ESM from jsdelivr, OrbitControls) with the windings and oil coloured by those estimates and a scrubber over the 168 hours. Parameters sit in `playbook.thermal_model`; nothing in the decision table reads them.
- **Thresholds**: `rules/decision-table.csv` references playbook values as `${section.key}`; `load_decision_table` resolves them, so editing `rules/playbook.json` changes behavior. The DAG reads its cron and time zone from the playbook too.

## Map page (landing)

`webapp/templates/map.html` is a standalone page (it does not extend `base.html`) built to the design handoff in `design/`: full-bleed Leaflet map, glass districts panel (left), heat strip (district selected), review sidebar or bottom sheet (right / narrow), top bar with the run pill, alerts bell and reviewer. `_render_map(period_id)` builds the context; `/` renders the first-launch state when no period exists. The run pill posts to `POST /api/runs` and polls `GET /api/runs/<id>` (status, current_step, failure headline); `/api/status` adds `latest_alert` and `unacknowledged_alerts`. Finalize posts to the period's finalize route with the reviewer name; the button is disabled client-side while any red case lacks a decision and the backend still returns 409.

## Heatmap

`capacity_monitor/heat.py` parses the readings feed once into `{date: {transformer: [24 hourly loads]}}` (cached until the file changes) plus each transformer's average hourly shape and daily-peak level. `/api/heat/recorded?date=` returns one recorded day; `/api/heat/seasonal?month=` returns a MODELED typical day: level x `seasonal_model.monthly_factors[month]` x shape, with `winter_evening_boost` on 17:00-21:00 in Dec-Feb. The heat view lives on the Map page (`webapp/templates/map.html`, Leaflet.heat): district buttons from the boundary feed; choosing a district zooms in and reveals recorded or seasonal mode, date/month/hour sliders with playback, utilization or absolute load, and a hotspot list. `/heatmap` routes redirect to the map. Seasonal factors are placeholders in `rules/playbook.json` until the utility supplies monthly peak ratios from a full year of readings.

## Synthetic data

`scripts/make_synthetic_data.py --count N` writes the 12 labeled cases plus N-12 generated transformers, each with a `customer_class` (residential, commercial, institutional, mixed) that sets its hourly load shape; downtown Ithaca is mostly commercial so it stays loaded at night. The generator verifies each intended-pass series with the real chart, capability and assumption functions and redraws until it matches its label. `data/feeds/readings.csv` is gitignored (42 MB at 500 transformers); regenerate with the script.

## Alert explanations

`explain.py` maps known failure patterns to plain-language title/meaning/action (templates, no AI) and groups non-blocking warnings as notes. `ai_explain.py` optionally asks the Claude CLI (`claude -p`, the owner's subscription) to rewrite an alert; it runs in an empty temp folder so no project context loads, passes the alert as data between markers, requires a JSON answer, length-limits, PII-redacts and guard-checks the answer, caches it in `ai_explanations`, and is triggered in the background by `send_alert` when the Setup toggle (`settings.ai_explanations`) is on. `CAPMON_CLAUDE_CLI` overrides the binary path (tests use a fake); `CAPMON_CLAUDE_TIMEOUT` sets the call timeout.

## Map popup

Clicking a transformer opens a glass card with a short summary, compact I-MR control charts and the key numbers. `GET /api/periods/<id>/transformers/<tid>/mini` returns the chart (`charts.mini_imr_svg`, inline attributes only so it cannot leak CSS), the rule-based line (`explain.summarize_transformer`) and any cached AI summary. When AI explanations are on in Setup, the page then calls `GET .../summary`, which runs one slim Claude CLI call on `claude-haiku-5-5` (`CAPMON_CLAUDE_SUMMARY_MODEL`; no tools, no MCP servers, no skills, no saved session, about 700 tokens, 3 to 9 seconds), passes the transformer's facts as data between markers, guard-checks and PII-redacts the answer, and caches it per period, transformer, inputs and model. Concurrent requests for the same transformer share one call. The rule-based line shows until the summary arrives and stays if the call fails.

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
