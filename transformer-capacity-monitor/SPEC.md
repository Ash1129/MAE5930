# SPEC: Transformer Capacity Monitor (Tompkins County)

What this tool IS. Where the code and this file disagree, the code is the bug: change this file first,
then the code. Filled in from the app as built, following the hackathon template in
`Timmy's stuff/SPEC.md`. Team, track and challenge prompt confirmed by the team.

## 1. Team and prompt
- **Team name:** SplitSync.
- **Track:** On-campus (24-hour sprint).
- **Challenge category:** Energy Systems.
- **Prompt we chose:** Smart Grid Transformer Surges.

  > Due to sudden local adoption of heat pumps, EVs, data centers, etc., local step-down transformers are blowing out. The utility has no predictive tracking. Design a system to log load and monitor/model the ability of the system to meet transformer requirements/limits to support local neighorhoods.

- **Our public repo:** github.com/Ash1129/MAE5930 (the app lives in `transformer-capacity-monitor/`).

## 2. User and use case (rubric: scope 5, user and use case 5)
- **User:** the grid-planning engineer at the local distribution utility who reviews distribution
  transformer loading for Tompkins County three times a week.
- **Decision the tool helps them make, and when:** after each scheduled run (Mon, Wed, Fri 06:00), which
  transformers need an engineering review now. A transformer needs review because its load pattern has
  changed, its headroom below the nameplate rating is thin or uncertain, or projected heat-pump growth
  would push its peak to 90% of rating or more. The engineer records a disposition on each flagged
  transformer, then signs off the period report.
- **Why this matches the prompt:** it logs neighborhood transformer loads, uses SPC to flag changes in
  daily peaks, measures headroom against transformer ratings, and projects additional heat-pump demand
  so utility planners can identify transformers that may struggle to meet future neighborhood needs.

## 3. Inputs (rubric: minimal inputs 5)
Four required feeds a utility planning team already holds, plus an optional ambient-temperature feed for modeled views. The engineer types nothing per run. Full column
definitions and real collection methods are in `data/README.md`.

| Input | Type and units | Where the user gets it |
|---|---|---|
| `readings.csv`, one row per transformer per hour | load, kVA | AMI smart-meter interval data summed per transformer, or a transformer load monitor |
| `assets.csv`, one row per transformer | nameplate rating in kVA, lat/lon, customers served, optional customer class | the utility's asset register and GIS connectivity model (customers = meters connected downstream; class = their main rate class) |
| `boundaries.geojson`, one polygon per town or village | lon/lat polygons | Tompkins County GIS open data portal |
| `heat_pump_forecast.csv`, one row per area | adoption share 0-1, kW per heat pump | the utility's load forecast or the state electrification forecast used in planning |
| `ambient.csv` (optional), hourly or daily | outside air, °C | weather station or utility export; modeled views only |

Optional asset thermal columns support the modeled cutaway; defaults are used when absent. They are not required for the QC decision.

Every column the statistics use is something the utility measures or already records. The engineer does
not need to know any process parameter. One loaded column, `households`, is not used by any calculation;
it is a candidate for removal.

## 4. The statistics, and why (rubric: valid QC analysis 25)
- **Method:** an Individuals and Moving Range (I-MR) chart on one value per transformer per day, the
  daily peak load. The limits come from the 60-day baseline before the 7-day review period:
  centre = mean, UCL/LCL = mean ± 2.66 × MR-bar, MR UCL = 3.267 × MR-bar. Four run rules apply: a point
  beyond 3 sigma, 2 of 3 beyond 2 sigma on one side, 8 in a row on one side, and a moving range above its UCL.
  Only transformers whose chart is stable get a one-sided capability index against the nameplate rating:
  Cpk = Cpu = (rating − mean) / (3σ), with σ = MR-bar / 1.128 over all finite daily peaks in the loaded chart window. A 95% interval uses
  Bissell's approximation with effective degrees of freedom 0.62 × (n − 1) for the moving-range estimator.
  A heat-pump projection adds customers × (forecast share − base share) × kW per heat pump ÷ power factor
  0.95 to the period peak. A first-match-wins decision table (`rules/decision-table.csv`) turns these
  results into three outcomes: "within limits" (green), "review needed" (amber: a few isolated outliers, or a
  capacity or forecast concern) and "inspect now" (red: a reading at or above the rating, a run rule such as
  8 in a row or 2 of 3 beyond 2 sigma firing in the period, or 3 or more outlier days in the period).
- **Why it fits the use case:** each transformer gives one natural value per day and no rational subgroups,
  so I-MR is the right chart. The rating is a one-sided upper limit, so Cpu is the right capability index.
  Capability is only meaningful once the chart shows the pattern is stable.
- **Assumptions and how the tool checks them:**
  - *Stability:* checked by the I-MR chart. An unstable chart withholds Cpk and sends the case to review.
  - *Dependence screen:* baseline autocorrelations at lags 1–7 are compared with pointwise ±2/√n
    bands; missing calendar dates are flagged. This exploratory screen also runs when capability is
    withheld. Flags route the case to review. The existing full-window lag-1 check remains; passing
    these screens does not prove independence. See METHODS.md.
  - *Normality:* a Jarque-Bera test at α = 0.05 checks the daily peaks. Otherwise the case is flagged the same way.
  - *Enough data:* the chart needs at least 20 baseline days and Cpk needs at least 20 points. Otherwise the result is "insufficient history".
  - *Zero variation:* if MR-bar is 0, the result is "zero variation" and goes to review as a likely meter or feed fault.
  - *Units:* readings and ratings must share a unit. Forecast kW becomes kVA with the playbook power factor.
  - *Seasonality:* a 60-day baseline does not remove weather or weekday effects. The report says so.
- **Known-answer check:** take 61 daily peaks alternating 59.5 and 60.5 kVA, starting at 59.5. Then
  MR-bar = 1.000, σ = 1/1.128 = 0.8865, centre = 60.00, UCL = 62.66, LCL = 57.34 and MR UCL = 3.267.
  Against a 100 kVA rating, mean = 59.992 and Cpk = (100 − 59.992)/(3 × 0.8865) = 15.04. This series
  alternates perfectly, so both assumption checks must also fire on it. Setting the period day
  2026-10-13 to 70 kVA must trigger "beyond 3 sigma" on that date. The real demo also gives a hand check:
  T-DAN-010 has rating 50, mean 39.91015 and σ 2.98383, so Cpk = 10.08985/8.95149 = 1.12717.
  These tests in `tests/test_pipeline.py` assert the known answers and degenerate cases:
  - `test_imr_chart_limits_come_from_history_not_rating` and `test_capability_cpk_and_interval` cover the series above.
  - `test_cpk_interval_hand_computed_known_answer` checks a 25-point interval computed by hand.
  - `test_cpk_interval_coverage_by_simulation` shows the interval covers about 95% of the time.
  - `test_forecast_projection_known_answer_with_unit_conversion` checks 40 × 0.45 × 2.4 / 0.95 = 45.47 kVA.
  - `test_chart_edge_cases_constant_one_point_nonfinite` covers constant data, n = 1, empty and non-finite values.
  - `test_chart_run_rules_two_of_three_and_eight_in_a_row_and_mr` plants each run rule.

Where the statistics live: `capacity_monitor/pipeline.py`, in the plain functions `imr_chart`,
`capacity_headroom`, `check_capability_assumptions`, `project_demand` and `needs_review`. They use the
Python standard library only and no web framework. This differs from the template's `app/qc.py` path.
These functions drive per-transformer decisions. Descriptive dashboard calculations live in the
framework-independent `capacity_monitor/aggregate.py`, with numerical tests in `tests/test_aggregate.py`.
[METHODS.md](METHODS.md) documents the daily threshold percentage, unique signal count and median/
quartile trends, plus thermal and seasonal models. Aggregate trends have no statistical alarm limits.

## 5. Delivery (rubric: working tool 25)
- **Stack:** Python library (`capacity_monitor/`), Flask dashboard (`webapp/`), optional local Airflow scheduler.
- **Local contract:** `testme.sh`, `manifestme.sh`, `deployme.sh` and this folder's `README.md` now exist.
  After environment setup, `./testme.sh` serves the app in the foreground without running an analysis.
- **Template deviation:** this folder is the application root rather than `app/`; no starter demo was
  copied. Flask is outside the template's named dashboard stacks. These are explicit deviations,
  not evidence of instructor approval. See `TEMPLATE-AUDIT.md` for remaining alignment work.
- **Deployment:** `manifest.json`, `.python-version`, root `app.py`, and the repository's
  `.github/workflows/deploy-flask.yml` implement Posit Connect publishing with
  `APP_DIR: transformer-capacity-monitor`. The team confirms Posit Connect is deployed; public
  access and workflow re-verification are deferred until later. Airflow is local only; hosted analysis is manual. See `DEPLOY.md`.
- **Saved demonstration:** the committed 2026-10-15 analysis opens without running the pipeline:
  500 transformers, 22 inspect now, 97 review needed, 381 within limits.

## 6. Outputs
- **What the user sees:**
  - **Map:** every transformer as a dot: green within limits, amber review needed, red inspect now.
  - **Review page per transformer:** the I-MR chart of daily peaks in kVA, with limits and signals in red.
    It also shows Cpk with its 95% interval, the period peak as a percentage of rating, the projected peak
    as a percentage of rating, the matching decision-table rule, and the source readings.
  - **Dashboard and area views:** county/district pie summaries, review queues, and descriptive daily
    trends: percentage near rating, unique transformers with signals, median loading and middle 50%.
    These have no aggregate control limits or alarm points; individual transformer I-MR charts remain.
  - **Modeled thermal view:** estimated oil/hot-spot temperatures from loads, optional ambient data,
    asset thermal values or defaults; explanatory only, not measured temperatures or a dispatch order.
  - **Period report:** HTML, Markdown and JSON, finalized only after every flagged case has a disposition.
  - **Heatmap:** hourly load per transformer for any recorded date. A seasonal view labeled MODELED
    scales the recorded shapes by the playbook's assumed monthly factors. It is context only and feeds no decision.
- *How to read this:* amber and red both need a person before the report goes out; red prioritizes prompt engineering inspection; it is not an automatic dispatch or proof of failure. The rule number names the reason, for example "rule 2: a run rule fired this period",
  "rule 4: a few outliers", "rule 10: lower 95% bound below 1.33" or "rule 11: forecast peak at 90% of
  rating or more".

## 7. Test datasets and codebook (rubric: demo 10, datasets 5, codebook 5)
`data/README.md` is the codebook. `demo/README.md` walks through each dataset with the exact command and
the numbers it prints. All three datasets are SYNTHETIC and produced by `scripts/make_synthetic_data.py`:
- **Datasets:**
  - `normal`: 12 transformers covering all three outcomes and several representative review rules. It includes a stable
    transformer with a planted spike 2 days before period end, a low Cpk, an uncertain Cpk, a forecast
    exception, a new transformer with only 12 days of history, and a transformer in overlapping boundary areas.
  - `boundary-mismatch`: the boundary file is valid only for 2025, so the run must stop at step 7.
  - `missing-rating`: T-GRO-009 has no rating, so the run must stop at step 7.
- **Template deviation:** scenarios are generated multi-file datasets rather than 2–3 small committed
  CSV fixtures. The 500-transformer feeds, review database, and 2026-10-15 reports are committed.
  `scripts/run_demo.py` generates its 12-transformer scenarios in a temporary folder; it does not
  replace the saved app data. Do not regenerate the working feeds to demonstrate the saved analysis.

## 8. Documentation and reproducibility (rubric: docs 10, public repo 5)
- `START-HERE.md` covers everyday use. `README-DEVELOPER.md` covers internals. `data/README.md` is the
  codebook and `demo/README.md` is the walkthrough.
- `requirements.txt` pins the versions that were tested. **Gap:** a fresh clone still needs `uv` and one
  setup command (`./scripts/setup_env.sh`) before the tests run.

## 9. Out of scope
- Defaults: logins, real customer data, a second statistic before the first one is tested.
- The tool never changes equipment, switching or operating settings. It only prepares a report for a person.
- No AI in the statistics or the review decision. Every pipeline step is a fixed rule. The only model
  call is an optional, off-by-default plain-language rewrite of alert and summary text in the review
  app (`capacity_monitor/ai_explain.py`). Its output is display only, and the rule-based text is always shown.
- No load-flow or voltage modelling. A thermal/ageing estimate exists for the labeled MODELED
  visualization only (`capacity_monitor/thermal.py`); it never changes a review decision. Capacity
  decisions use the nameplate rating, SPC results and heat-pump projection.
- No per-customer forecasting. Heat-pump growth is applied by area share.
- No fitted seasonal model. The heatmap's monthly factors are labeled assumptions, not estimates.
- Real utility feeds and the approved playbook thresholds are owner setup, not part of the hackathon build.
