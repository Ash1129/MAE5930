# Transformer Capacity Monitor (Tompkins County)

A statistical process control (SPC) tool for the **grid-planning engineer** who reviews distribution
transformer loading. Three times a week it checks every transformer's daily peak load on an I-MR control
chart. For stable transformers it measures headroom below the nameplate rating with a one-sided Cpk and a
95% interval, then projects heat-pump demand growth. A fixed decision table flags transformers for review.
A named reviewer records a disposition on each flagged transformer before the period report can be finalized.

Every statistic and review decision is a fixed rule. An optional setting, off by default, asks the
local `claude` CLI to reword alerts and transformer summaries in plain language. That text is display
only and never changes a result. The tool never changes equipment or operating settings. All data in
this repository is SYNTHETIC.

| Read this | For |
|---|---|
| [`START-HERE.md`](START-HERE.md) | everyday use in three steps |
| [`demo/README.md`](demo/README.md) | the tool run on each of the three test datasets, with the numbers it prints |
| [`data/README.md`](data/README.md) | codebook: every file, column, unit and how to collect it for real |
| [`SPEC.md`](SPEC.md) | user, inputs, statistics, assumptions, known-answer checks, scope |
| [`CONTRACT.yaml`](CONTRACT.yaml) | the hackathon task ledger and what is still open |
| [`README-DEVELOPER.md`](README-DEVELOPER.md) | code layout, scheduler, idempotency and guardrails |

## Run it

The first command needs [`uv`](https://docs.astral.sh/uv/), which on macOS installs with `brew install uv`.

```bash
./scripts/setup_env.sh
```

```bash
.venv/bin/python scripts/run_demo.py normal
```

```bash
./testme.sh
```

The review app opens at http://127.0.0.1:5055. The optional scheduler starts with
`./scripts/start_airflow.sh`. To run the tests:

```bash
.venv/bin/python -m pytest tests -q
```

The app is deployed on Posit Connect (confirmed by the team). Public access will be reverified
later; see [DEPLOY.md](DEPLOY.md). See [TEMPLATE-AUDIT.md](TEMPLATE-AUDIT.md) for the
remaining template and rubric checks.

The committed 2026-10-15 analysis opens without **Run now**: **22 Inspect now, 97 Review needed,
381 Within limits** (500 total). Do not regenerate feeds to view it. The demo command above
uses a temporary folder and leaves this saved analysis unchanged.

## Inputs

Four required feeds and one optional feed in `data/feeds/`. Their columns are defined in [`data/README.md`](data/README.md).

| File | Holds |
|---|---|
| `readings.csv` | hourly transformer load in kVA |
| `assets.csv` | nameplate rating in kVA, location, customers served, declared area |
| `boundaries.geojson` | town and village polygons with their approval dates |
| `heat_pump_forecast.csv` | base and forecast heat-pump share by area, kW per heat pump |
| `ambient.csv` (optional) | outside air temperature, hourly or daily; read only by the modeled views (the review page's 3D cutaway and the map's Temperature heat view) |

## Parameters

All thresholds live in [`rules/playbook.json`](rules/playbook.json), and
[`rules/decision-table.csv`](rules/decision-table.csv) refers to them. The values are reversible defaults
until the utility approves its own.

| Parameter | Default | Meaning |
|---|---|---|
| `period_days` | 7 | days in each review period, ending the day before the run |
| `history_days` | 60 | baseline days before the period used for control limits |
| `chart.min_history_points` | 20 | fewest baseline days for a chart |
| `chart.run_rules` | 4 rules | beyond 3σ; 2 of 3 beyond 2σ; 8 in a row on one side; moving range above its UCL |
| `chart.inspect_rules` | 8 in a row; 2 of 3 beyond 2σ | a pattern rule firing in the period means **inspect now** (red), not just review |
| `chart.inspect_outliers_at` | 3 | this many days with an isolated outlier in the period also means inspect now; fewer is **review needed** (amber) |
| `seasonal_model.temperature_response` | 2.5 %/°C below 15 °C; 1.5 %/°C above 22 °C | how the map's MODELED seasonal load follows the typical outside air through the day; scaled so a day averages 1.0 |
| `thermal_model.monthly_ambient_c`, `diurnal_swing_c` | typical Ithaca means; 5 °C swing | the seasonal view's outside air for each month and hour (the recorded view uses `ambient.csv`) |
| `capability.cpk_review_below` | 1.33 | Cpk below this needs review |
| `capability.cpk_ci_low_review_below` | 1.33 | a lower 95% bound below this needs review |
| `capability.mr_effective_df_factor` | 0.62 | effective degrees of freedom of the MR-bar sigma, as a share of n − 1 |
| `capability.normality_alpha` | 0.05 | Jarque-Bera significance level |
| `forecast.version` | TC-HP-2026-v1 | the only forecast release used |
| `forecast.near_rating_ratio` | 0.9 | a projected peak at this share of rating or more needs review |
| `forecast.power_factor` | 0.95 | converts forecast kW to kVA |
| `schedule.cron` | `0 6 * * 1,3,5` | Mon, Wed, Fri at 06:00 America/New_York |
| `seasonal_model.monthly_factors` | 0.85 to 1.35 | MODELED monthly multipliers for the heatmap's seasonal view only |

## How each function works

The statistics are plain functions in `capacity_monitor/pipeline.py` that use the standard library only.

| Function | Input | Output |
|---|---|---|
| `imr_chart(daily_peaks, period, playbook)` | daily peak in kVA by date | centre, UCL and LCL as mean ± 2.66 × MR-bar from baseline days only; MR UCL as 3.267 × MR-bar; signals; status `stable`, `signal`, `insufficient_history` or `zero_variation` |
| `check_capability_assumptions(values, playbook)` | daily peaks | lag-1 autocorrelation against ±2/√n, Jarque-Bera p-value, list of flags |
| `capacity_headroom(chart, rating, projection, playbook)` | chart, nameplate rating, projection | Cpk = (rating − mean)/(3 × MR-bar/1.128) with a Bissell 95% interval, plus period and projected peaks as shares of rating; withheld unless the chart is stable |
| `project_demand(transformer, period, playbook)` | period peak, customers, area forecast | period peak + customers × (forecast share − base share) × kW per heat pump ÷ power factor |
| `needs_review(facts, table)` | the results above | the first matching decision-table row: outcome, rule number, reason |

These functions drive the per-transformer decisions. Descriptive daily dashboard trends
use plain percentage, unique-count and quartile functions in `capacity_monitor/aggregate.py`; the modeled thermal view uses
`capacity_monitor/thermal.py`. Their formulas, inputs, assumptions, units and existing test evidence are documented in
[METHODS.md](METHODS.md). Review of the individual I-MR/capability assumptions remains tracked in
[TEMPLATE-AUDIT.md](TEMPLATE-AUDIT.md).

## Outputs

- A map of transformers: green for within limits, amber for review needed (a few outliers, or a capacity or
  forecast concern), red for inspect now (a reading at the rating, a sustained shift, or repeated outliers this period).
- A review page per transformer with the I-MR chart, Cpk and its interval, assumption flags, the
  projection and its assumptions, the matching rule, and the source readings.
- On that page, a 3D cutaway labeled MODELED: the oil and winding hot-spot temperatures the week's
  hourly loads would produce under the IEEE C57.91 loading guide (`playbook.thermal_model`). It uses
  nameplate thermal values from `assets.csv` when they are there, typical values for the unit kind
  otherwise, and the optional `ambient.csv` feed for outside air; the page says which it used. The tool
  has no sensors inside the unit; this view is for understanding and feeds no rule.
- A heatmap of hourly load per transformer for a recorded date, plus a seasonal view labeled MODELED.
- A period report in `data/reports/<period end>/` as HTML, Markdown and JSON. It can be finalized only
  after every flagged transformer has a disposition, and the backend enforces this with HTTP 409.
