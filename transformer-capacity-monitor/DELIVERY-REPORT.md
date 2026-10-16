# Delivery report: Transformer capacity monitoring (Tompkins County)

Built 2026-10-16 to the contract in DELIVERY.md. Fixed-rules pipeline, Apache Airflow scheduler,
small browser review app. **No AI model is used anywhere.**

## Status: DEMO ONLY (real processing and scheduler verified; real feeds and approved thresholds pending)

What is real and tested:
- The processing is real local processing, not canned output: I-MR control charts, one-sided Cpk with a
  95% interval, heat-pump demand projection, a first-match-wins decision table, period-keyed idempotent
  storage and report writing. All of it ran on the synthetic feeds and produced the reports in `data/reports/`.
- The scheduler is real: Apache Airflow 3.3.2 runs locally (standalone mode), parsed the DAG, executed
  it end to end on an API trigger, **fired a run on its own schedule** (run type `scheduled`, see below),
  and can be paused/resumed from the app. Next/last run and failures are shown on the dashboard.
- The approval gate is enforced in the backend (HTTP 409 on a direct finalize request without dispositions).

Why not READY:
- The four feeds in `data/feeds/` are **synthetic, clearly labeled sample data**. The real meter, asset, GIS
  and forecast exports have not been connected or seen. Every report produced so far is sample output.
- Thresholds in `rules/playbook.json` (Cpk 1.33, 90% forecast margin, 20 days minimum history, Mon/Wed/Fri
  06:00 schedule, 7-day period, 60-day history, declared-primary-area allocation) are the builder's
  reversible defaults, not the owner's approved playbook. The named reviewer and alert recipient are not set.

## Launch location

- Double-click `Start Capacity Monitor.command` (or `./scripts/start_airflow.sh` and `./scripts/start_app.sh`).
- Review app: http://127.0.0.1:5055 (tested entry point). Airflow UI: http://127.0.0.1:8080
  (admin password is generated into `airflow_home/simple_auth_manager_passwords.json.generated`).
- Stop: `Stop Capacity Monitor.command` or `./scripts/stop.sh`. Status: `./scripts/status.sh`.
- Everyday steps: START-HERE.md. Developer details: README-DEVELOPER.md.

## Files built

| Area | Files |
|---|---|
| Pipeline (steps 1-15) | `capacity_monitor/` (`config.py`, `sources.py`, `pipeline.py`, `run.py`, `report.py`, `store.py`, `guards.py`, `charts.py`, `notify.py`, `airflow_client.py`) |
| Scheduler | `airflow/dags/log_transformer_loads_and_monitor_capacity_again.py` (feed-readiness sensor + one task per step, failure callback) |
| Review app | `webapp/app.py`, `webapp/templates/*.html` |
| Rules | `rules/playbook.json`, `rules/decision-table.csv` (placeholders replaced with real rules) |
| Data | `scripts/make_synthetic_data.py` -> `data/feeds/` (synthetic), outputs in `data/reports/<period>/`, database `data/capacity_monitor.sqlite3` |
| Setup and launch | `scripts/setup_env.sh`, `scripts/env.sh`, `scripts/start_*.sh`, `scripts/stop.sh`, `scripts/status.sh`, `Start/Stop Capacity Monitor.command` |
| Tests and evals | `tests/` (pytest), `scripts/run_evals.py` -> `evals/results.md` |
| Docs | `START-HERE.md`, `README-DEVELOPER.md`, this report |

Every step in the architecture table exists and hands on to the next: steps 1-8 are individual functions and
Airflow tasks; steps 9-12 run in `pipeline.evaluate_transformers` (recorded individually in the run log);
step 13 is the app's review queue (the run shows `waiting` until dispositions exist); step 14 writes the
period report; step 15 marks the draft report available, pending reviewer finalization.

## Tests actually run and their outcomes

Environment: macOS, Python 3.12 venv, apache-airflow 3.3.2 (standalone, LocalExecutor, SQLite metadata), Flask 3.1.3.

| Test | Observed result |
|---|---|
| `pytest tests -q` (pipeline units, end-to-end runs, failure cases, web user path, approval bypass, injection) | **17 passed** |
| `scripts/run_evals.py` (the 6 cases in evals/examples.csv, isolated home) | **6 of 6 passed**; details in `evals/results.md` |
| Labeled synthetic cases, period ending 2026-10-15 | 12 transformers: 7 within limits, 5 review needed. T-DRY-004 chart signal (beyond 3 sigma on 2026-10-13, Cpk withheld, peak 82% of rating); T-LAN-005 uncertain Cpk 1.43 (CI 1.16 to 1.70); T-CAR-006 forecast peak 135% of rating with current peak 70%; T-DAN-010 low Cpk 1.22; T-ULY-007 insufficient history (11 days) |
| Airflow DAG import | Parsed with no import errors; appears in the Airflow API with schedule "At 06:00, only on Monday, Wednesday, and Friday" |
| Airflow manual trigger (API, conf period_end 2026-10-15) | DAG run `success` in about 60 s; app run log shows steps 1-15 with step 13 `waiting` |
| Airflow scheduled firing | Cron temporarily set to every 2 minutes; run `scheduled__2026-10-16T21:14:00+00:00` (type `scheduled`) started 21:14:29Z and finished `success` 21:15:16Z; cron restored to `0 6 * * 1,3,5`; next run reported as 2026-10-19T10:00Z (Monday 06:00 EDT) |
| Pause control | Dashboard Pause -> Airflow reports `is_paused: true`; Resume -> active. Verified in the browser |
| Controlled failure in Airflow (boundary feed valid to 2025-12-31, run period 2026-10-13) | DAG run `failed` after 130 s at `step_7_check_input_completeness`; app shows run failed at step 7, steps 8-15 skipped; two alerts recorded with run and period ids; no period results or report written |
| Missing feed with Airflow | Readiness sensor kept waiting (reschedule mode) instead of running on incomplete inputs; the 6-hour wait limit was not run to exhaustion (would take 6 h). The same missing-feed case in-process fails at step 2 with an alert (eval case 6, pytest) |
| Rerun of the same period | One `period_results` row per period, `rerun_count` increments, status returns to draft, all run attempts kept, report history copies kept (`data/reports/2026-10-15/history/` has 5) |
| Disposition survives a rerun with unchanged inputs | Reject recorded for T-DRY-004 at 17:14:26 still current after the scheduler reran the period (input hash unchanged); a changed input hash makes a disposition stale (pytest) |
| Approval bypass | Direct `POST /periods/2026-10-15/finalize` with no dispositions -> HTTP 409, period stays draft. Request-changes on any case also blocks finalization. Dispositions are refused after a period is final |
| Browser user path (Claude's browser) | Dashboard, period page, transformer review page (checklist beside chart, signals, source readings), Reject with note recorded (10.8 s review time captured), Alerts page |
| Second fresh task after restart | Stopped both services, restarted with the scripts, ran period 2026-10-14 from the form -> `success`, step 15 |
| Guardrails | Instruction-like text in an asset note is quarantined and reported as a warning (never acted on); instruction-like text in a review note is refused; e-mail/phone/SSN patterns are redacted from report output; loaders retry 3 times then fail with an alert (pytest) |
| Known-wrong calibration seeding | Implemented (`review.known_wrong_seed_every_n_periods` = 3); it did not fall on the periods run today; next due period ends 2026-10-25 to 2026-10-28. Catch rate is shown on the Review metrics page. Not yet exercised with a real reviewer |

Not tested: e-mail delivery of alerts (no SMTP configured; alerts are recorded in the app), the 6-hour sensor
timeout at full length, production Airflow deployment (standalone mode is for development), real feed formats.

## Sample input and saved output

- Input: `data/feeds/readings.csv` (hourly kVA, 12 synthetic transformers, 2026-08-02 to 2026-10-15),
  `assets.csv`, `boundaries.geojson` (synthetic rectangles, metadata valid 2026), `heat_pump_forecast.csv`
  (version TC-HP-2026-v1 plus a superseded version that is correctly ignored).
- Output: `data/reports/2026-10-15/report.html`, `report.md`, `report.json` (status DRAFT; one Reject disposition
  recorded; finalization pending the remaining four dispositions). Also `data/reports/2026-10-14/`.

## Setup remaining (owner actions)

1. Replace the synthetic feeds in `data/feeds/` with real exports (columns listed on the Setup page), or have
   IT point `capacity_monitor/sources.py` at the meter, asset, GIS and forecast systems. Then run one period and
   compare with the current manual process (run alongside for two weeks, as the plan says).
2. Approve the playbook values in `rules/playbook.json` and `rules/decision-table.csv`: measurement period,
   schedule and time zone, late-data cutoff, Cpk thresholds, forecast margin, run rules, minimum history,
   forecast version and allocation method. Record who approved them.
3. Enter the named reviewer on the Setup page; set `CAPMON_ALERT_TO` and `CAPMON_SMTP_*` in the environment
   (before starting the app) if failure alerts should also go by e-mail; agree the escalation path.
4. Decide where it runs for real. Today it runs on this Mac (free; nothing leaves the machine). For unattended
   operation use a machine that stays on, or a managed Airflow service (priced by its provider, which would be a new
   cost beyond the $0/month estimate). Airflow standalone is development mode; a production deployment needs a proper
   metadata database and credentials in a secrets backend, and should be re-tested with that executor.
5. Collect 10 to 20 real past cases into `evals/examples.csv` and rerun `scripts/run_evals.py` as the baseline.

## Costs

No new accounts, subscriptions or AI usage. Airflow and Flask are free open-source software running locally.
