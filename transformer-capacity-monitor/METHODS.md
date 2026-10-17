# Additional chart and model methods

This documents the aggregate-statistics extraction from `5fdfdbc`; it is not a completed validation
of the statistical assumptions.
Per-transformer I-MR, capability, forecast and decision methods are in [SPEC.md](SPEC.md),
[README.md](README.md), and `capacity_monitor/pipeline.py`. The additional views below do not
change the per-transformer decision-table outcome.

## Individual-chart corrections (new analyses)

`history_days` now means the number of calendar days before the review period. A seven-day period
ending 2026-10-15 has baseline 2026-08-10 through 2026-10-08 (60 days), then review 2026-10-09
through 2026-10-15. Previously the lookback began at period_end minus 60 days, yielding 54 baseline
days and 61 total. Saved reports are historical snapshots and are not automatically recomputed.

`imr_chart` records `baseline_dependence` before checking chart stability, so the baseline screen is
available even when capability is withheld. With at least 20 baseline points and nonzero variance,
it calculates autocorrelation at lags 1 through 7 using the common denominator sum((x-mean)^2).
Each lag is compared with the approximate pointwise band +/-2/sqrt(n). These are exploratory,
unadjusted multiple screens, not a joint test or proof of independence. Weekly weather/day-type
structure still needs engineering interpretation. Missing baseline calendar dates are flagged because
adjacent observations no longer represent consistent daily lags. Short and constant baselines have
explicit diagnostic statuses. Flags are carried into capability output and route stable-chart cases
to decision rule 8; any displayed Cpk is interpreted cautiously.

The existing full-window lag-1 and Jarque-Bera capability checks are unchanged. In particular, the
normality method has not been revised. UI text says “no issue detected” rather than asserting that
assumptions are established. Older saved results without baseline diagnostics are identified as legacy
results rather than presented as screened by the new method.

The eight-in-a-row rule now records every subsequent day on the same side once the run reaches eight.
A run starting before the review week therefore remains a current-period signal if it continues.
Chart captions distinguish control-limit exceedances from run-pattern signals, which may lie inside
individual limits. Absence of a configured signal does not establish an unchanged process.

Only confidence_level=0.95 is supported: both playbook loading and direct capability calls reject
other values. The existing approximate interval formula and normal quantile are unchanged. Numerical
Cpk values with flagged assumptions are explicitly marked for cautious interpretation, rather than
being labeled comfortable. No newly calculated results overwrite the saved demo during this work.

Regression tests in `tests/test_pipeline.py` cover exact baseline dates, weekly dependence, missing
baseline dates, dependence diagnostics with withheld capability, continuing cross-period runs,
non-95% configuration rejection, review routing and qualified chart captions.

## Descriptive dashboard trends

`capacity_monitor/aggregate.py:county_trend_statistics(results)` accepts plain transformer result
records and returns `status` (`computed` or `insufficient_data`) plus one numerical point per date.
There is no baseline fitting, control limit, out-of-control test or aggregate alarm count.
`webapp/viz.py:county_trend_charts(results, period_start)` renders the points; period_start is used
only to shade the review week. The existing pie charts and individual transformer I-MR charts remain.

| Numerical field | Meaning and units |
|---|---|
| `n` | unique eligible transformers reporting that day |
| `near_rating_count` | reporting transformers whose daily peak/rating is >= 0.90 |
| `near_rating_pct` | 100 * near_rating_count / n |
| `signal_transformers` | unique reporting transformers with at least one I-MR rule dated that day; multiple rules count once |
| `median_pct` | median daily peak/rating, multiplied by 100 |
| `q1_pct`, `q3_pct` | 25th and 75th percentiles of daily peak/rating, multiplied by 100 |

Calibration cases, invalid/nonpositive/nonfinite ratings, and missing/nonfinite peaks are excluded.
Missing dates are omitted rather than filled with zeros. The denominator can vary by day; tooltips
show reporting counts, and comparisons should consider coverage changes. Duplicate transformer IDs
are counted once per date; if duplicate values conflict, the last eligible value is used.

`box_stats(values)` returns n/min/q1/median/q3/max; quartiles interpolate linearly at index p*(n-1).
It ignores None, returns None for empty input, and uses the full range for box whiskers. The loading
trend instead shades q1 to q3 (the middle 50% of observed transformers); this is a distribution band,
not a confidence interval. A single observation has equal q1, median and q3.

These summaries do not assume binomial/Poisson distributions or comparable normal subgroups. They
also do not establish causation, predict failures, or resolve the individual I-MR assumptions.
The 90% cutoff remains a descriptive threshold, not a failure probability.

The former p/u/X-S limits were removed after review: mixed equipment and shared weather complicate
the p/X-S assumptions, while overlapping I-MR rule detections make a Poisson event-rate model
unjustified. References: [NIST p charts](https://www.itl.nist.gov/div898/handbook/pmc/section3/pmc332.htm),
[NIST count charts](https://www.itl.nist.gov/div898/handbook/pmc/section3/pmc331.htm),
[NIST X-bar/S charts](https://www.itl.nist.gov/div898/handbook/pmc/section3/pmc321.htm).

`tests/test_aggregate.py` checks hand-computed percentages, unique signal counts and quartiles,
varying coverage, empty/constant/single observations, duplicate IDs and invalid data. Rendering and
Flask tests verify the descriptive panels, quartile ribbon, retained pies and absence of aggregate
alarm labels. The individual decision table and saved 2026-10-15 analysis are unchanged.

## Modeled thermal cutaway and map temperatures

`capacity_monitor/thermal.py:simulate(readings, rating, playbook, step_h=1, kind, asset, ambient)`
returns hourly modeled temperatures, aging factors, the peak row, parameter/source metadata and a
count at/above the configured hot-spot limit. The UI labels this **MODELED**. There are no internal
sensor readings, and neither temperature nor aging enters `needs_review`.

Let K be nonnegative load divided by rating, R the load-loss/no-load-loss ratio, n the oil exponent,
m the winding exponent, tau the oil time constant in hours, and dt the step length:

- Ultimate oil rise: `oil_ultimate = oil_rated * ((K^2 * R + 1)/(R + 1))^n`
- Oil dynamics: `oil_rise = oil_ultimate + (previous_oil_rise - oil_ultimate) * exp(-dt/tau)`
- Top oil: `ambient + oil_rise`
- Hot spot: `top_oil + winding_rated * K^(2*m)`
- Relative aging factor: `exp(15000/383 - 15000/(hot_spot + 273))`

The implementation identifies this as an IEEE C57.91 exponential-model approximation. This note
records that attribution without asserting independent verification against the complete standard.
The first oil state is initialized at the first load's steady state; winding rise responds within
the hourly step. Input ordering and hourly spacing are assumed, rather than inferred from timestamps.
`hours_at_or_over_limit` counts returned rows at/above the threshold; it represents hours for the
normal hourly input and default step. It is not a measured remaining-life estimate.

Parameter precedence is positive valid asset-record thermal fields, then unit-kind playbook values,
then general playbook/default values. General defaults are ambient 20 °C, oil rise 55 °C, winding rise
25 °C, R=3.2, n=m=0.8 and tau=3 h. Kind-specific and nameplate overrides can change these values.
The playbook's 110 °C limit and 120 °C emergency value are illustrative view settings, not approved
utility dispatch thresholds. Consult `rules/playbook.json` for current values.

Ambient precedence is matching recorded hour, recorded daily mean, then fixed assumed ambient.
`ambient.csv` accepts `timestamp,temp_c` or `date,temp_c`; invalid/nonfinite temperatures are skipped.
In this repository the ambient feed itself is synthetic. “Recorded” distinguishes the feed-based
view from a seasonal model, not real field measurements. Source metadata identifies fallback use.

Known-answer evidence in `tests/test_thermal.py`: under general defaults at rated steady load,
top oil is `20 + 55 = 75 °C` and hot spot is `75 + 25 = 100 °C`; aging factor is 1 at 110 °C.
Other tests cover a load step/oil lag, parameter precedence, ambient lookup/fallback, the thermal API,
and a one-for-one temperature shift with ambient for identical loads. This establishes implementation
checks, not field calibration or full coverage of malformed thermal inputs.

## Seasonal heat view

`capacity_monitor/heat.py` uses recorded average hourly shapes and daily-peak levels, multiplied by
the playbook's monthly factors and winter evening adjustment. Its temperature response applies
2.5% per degree below 15 °C and 1.5% per degree above 22 °C, then normalizes the daily temperature
multipliers to average 1. Monthly assumed ambient plus a diurnal swing supplies seasonal temperatures.
These configurable factors are assumptions, not fitted weather relationships. Thermal map estimates
use the same thermal module. Neither seasonal output nor modeled temperature drives a review rule.
