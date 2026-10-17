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
Four feeds a utility planning team already holds. The engineer types nothing per run. Full column
definitions and real collection methods are in `data/README.md`.

| Input | Type and units | Where the user gets it |
|---|---|---|
| `readings.csv`, one row per transformer per hour | load, kVA | AMI smart-meter interval data summed per transformer, or a transformer load monitor |
| `assets.csv`, one row per transformer | nameplate rating in kVA, lat/lon, customers served, optional customer class | the utility's asset register and GIS connectivity model (customers = meters connected downstream; class = their main rate class) |
| `boundaries.geojson`, one polygon per town or village | lon/lat polygons | Tompkins County GIS open data portal |
| `heat_pump_forecast.csv`, one row per area | adoption share 0-1, kW per heat pump | the utility's load forecast or the state electrification forecast used in planning |

Every column the statistics use is something the utility measures or already records. The engineer does
not need to know any process parameter. One loaded column, `households`, is not used by any calculation;
it is a candidate for removal.

## 4. The statistics, and why (rubric: valid QC analysis 25)
- **Method:** an Individuals and Moving Range (I-MR) chart on one value per transformer per day, the
  daily peak load. The limits come from the 60-day baseline before the 7-day review period:
  centre = mean, UCL/LCL = mean ± 2.66 × MR-bar, MR UCL = 3.267 × MR-bar. Four run rules apply: a point
  beyond 3 sigma, 2 of 3 beyond 2 sigma on one side, 8 in a row on one side, and a moving range above its UCL.
  Only transformers whose chart is stable get a one-sided capability index against the nameplate rating:
  Cpk = Cpu = (rating − mean) / (3σ), with σ = MR-bar / 1.128 over all 61 days. A 95% interval uses
  Bissell's approximation with effective degrees of freedom 0.62 × (n − 1) for the moving-range estimator.
  A heat-pump projection adds customers × (forecast share − base share) × kW per heat pump ÷ power factor
  0.95 to the period peak. A first-match-wins decision table (`rules/decision-table.csv`) turns these
  results into "within limits" or "review needed".
- **Why it fits the use case:** each transformer gives one natural value per day and no rational subgroups,
  so I-MR is the right chart. The rating is a one-sided upper limit, so Cpu is the right capability index.
  Capability is only meaningful once the chart shows the pattern is stable.
- **Assumptions and how the tool checks them:**
  - *Stability:* checked by the I-MR chart. An unstable chart withholds Cpk and sends the case to review.
  - *Independence:* lag-1 autocorrelation must fall inside ±2/√n. Otherwise the case is flagged and Cpk is shown for information only.
  - *Normality:* a Jarque-Bera test at α = 0.05 checks the daily peaks. Otherwise the case is flagged the same way.
  - *Enough data:* the chart needs at least 20 baseline days and Cpk needs at least 20 points. Otherwise the result is "insufficient history".
  - *Zero variation:* if MR-bar is 0, the result is "zero variation" and goes to review as a likely meter or feed fault.
  - *Units:* readings and ratings must share a unit. Forecast kW becomes kVA with the playbook power factor.
  - *Seasonality:* a 60-day window limits weather drift but does not remove it. The report says so.
- **Known-answer check:** take 61 daily peaks alternating 59.5 and 60.5 kVA, starting at 59.5. Then
  MR-bar = 1.000, σ = 1/1.128 = 0.8865, centre = 60.00, UCL = 62.66, LCL = 57.34 and MR UCL = 3.267.
  Against a 100 kVA rating, mean = 59.992 and Cpk = (100 − 59.992)/(3 × 0.8865) = 15.04. This series
  alternates perfectly, so both assumption checks must also fire on it. Setting the period day
  2026-10-13 to 70 kVA must trigger "beyond 3 sigma" on that date. The real demo also gives a hand check:
  T-DAN-010 has rating 50, mean 40.176 and σ 2.850, so Cpk = 9.824/8.551 = 1.15.
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
The web app and the scheduler only call these functions and display the results.

## 5. Delivery (rubric: working tool 25)
- **Stack:** a Python library (`capacity_monitor/`) with a Flask review dashboard (`webapp/`) and an Apache
  Airflow 3 scheduler (`airflow/dags/`). **Gap:** this is not one of the listed starter stacks (FastAPI,
  plumber, React, Shiny). The closest listed shape is "Python library plus dashboard".
- **Starting demo:** none. The app was built from the `BUILD.md` kit rather than copied from `demos/`.
  **Gap:** there is no `app/` folder with the four-script contract (`testme`, `manifestme`, `deployme`,
  `README.md`). The existing one-command equivalents are `scripts/setup_env.sh`, `scripts/start_app.sh` and
  `Start Capacity Monitor.command`.
- **Deployment:** runs locally at http://127.0.0.1:5055. **Gap:** it is not deployed to the course Posit
  Connect server and has no `manifest.json`. Airflow cannot run on Posit Connect, so a deploy would publish
  the Flask review app alone, with "Run now" doing the scheduling. See CONTRACT task H-06.

## 6. Outputs
- **What the user sees:**
  - **Map:** every transformer as a dot, green for within limits and red for review needed.
  - **Review page per transformer:** the I-MR chart of daily peaks in kVA, with limits and signals in red.
    It also shows Cpk with its 95% interval, the period peak as a percentage of rating, the projected peak
    as a percentage of rating, the matching decision-table rule, and the source readings.
  - **Period report:** HTML, Markdown and JSON, finalized only after every flagged case has a disposition.
  - **Heatmap:** hourly load per transformer for any recorded date. A seasonal view labeled MODELED
    scales the recorded shapes by the playbook's assumed monthly factors. It is context only and feeds no decision.
- *How to read this:* red means a person must look before the report goes out. The rule number names the
  reason, for example "rule 2: chart signal", "rule 8: lower 95% bound below 1.33" or
  "rule 9: forecast peak at 90% of rating or more".

## 7. Test datasets and codebook (rubric: demo 10, datasets 5, codebook 5)
`data/README.md` is the codebook. `demo/README.md` walks through each dataset with the exact command and
the numbers it prints. All three datasets are SYNTHETIC and produced by `scripts/make_synthetic_data.py`:
- **Datasets:**
  - `normal`: 12 transformers in which every review rule fires at least once. It includes a stable
    transformer with a planted spike 2 days before period end, a low Cpk, an uncertain Cpk, a forecast
    exception, a new transformer with only 12 days of history, and a transformer in overlapping boundary areas.
  - `boundary-mismatch`: the boundary file is valid only for 2025, so the run must stop at step 7.
  - `missing-rating`: T-GRO-009 has no rating, so the run must stop at step 7.
- **Gap:** each dataset is four files and is regenerated by a command rather than shipped as one CSV per
  case. `data/feeds/readings.csv` is git-ignored. `./scripts/setup_env.sh` generates it automatically,
  for 500 transformers, when it is missing. The committed assets, boundaries and forecast files match
  that seeded run. `scripts/run_demo.py` and the tests build their own 12-transformer data.

## 8. Documentation and reproducibility (rubric: docs 10, public repo 5)
- `START-HERE.md` covers everyday use. `README-DEVELOPER.md` covers internals. `data/README.md` is the
  codebook and `demo/README.md` is the walkthrough.
- `requirements.txt` pins the versions that were tested. **Gap:** a fresh clone still needs `uv` and one
  setup command (`./scripts/setup_env.sh`) before the tests run.

## 9. Out of scope
- Defaults: logins, real customer data, a second statistic before the first one is tested.
- The tool never changes equipment, switching or operating settings. It only prepares a report for a person.
- No AI or model calls anywhere. Every step is a fixed rule.
- No load-flow, voltage or thermal-ageing modelling. Capacity means the nameplate kVA rating only.
- No per-customer forecasting. Heat-pump growth is applied by area share.
- No fitted seasonal model. The heatmap's monthly factors are labeled assumptions, not estimates.
- Real utility feeds and the approved playbook thresholds are owner setup, not part of the hackathon build.
