# Transformer Capacity Monitor (Tompkins County)

A statistical process control (SPC) tool for the **grid-planning engineer** who reviews distribution
transformer loading. Three times a week it checks every transformer's daily peak load on an I-MR control
chart. For stable transformers it measures headroom below the nameplate rating with a one-sided Cpk and a
95% interval, then projects heat-pump demand growth. A fixed decision table flags transformers for review.
A named reviewer records a disposition on each flagged transformer before the period report can be finalized.

No AI is used. The tool never changes equipment or operating settings. All data in this repository is
SYNTHETIC.

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
./scripts/start_app.sh
```

The review app opens at http://127.0.0.1:5055. The optional scheduler starts with
`./scripts/start_airflow.sh`. To run the tests:

```bash
.venv/bin/python -m pytest tests -q
```

There is no public deployment yet. See CONTRACT task H-06.

## Inputs

Four feeds in `data/feeds/`. Their columns are defined in [`data/README.md`](data/README.md).

| File | Holds |
|---|---|
| `readings.csv` | hourly transformer load in kVA |
| `assets.csv` | nameplate rating in kVA, location, customers served, declared area |
| `boundaries.geojson` | town and village polygons with their approval dates |
| `heat_pump_forecast.csv` | base and forecast heat-pump share by area, kW per heat pump |

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

The Airflow DAG and the Flask app only call these functions, store the results and display them.

## Outputs

- A map of transformers, green for within limits and red for review needed.
- A review page per transformer with the I-MR chart, Cpk and its interval, assumption flags, the
  projection and its assumptions, the matching rule, and the source readings.
- A heatmap of hourly load per transformer for a recorded date, plus a seasonal view labeled MODELED.
- A period report in `data/reports/<period end>/` as HTML, Markdown and JSON. It can be finalized only
  after every flagged transformer has a disposition, and the backend enforces this with HTTP 409.
