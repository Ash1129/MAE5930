# Additional chart and model methods

This documents the aggregate-statistics extraction from `5fdfdbc`; it is not a completed validation
of the statistical assumptions.
Per-transformer I-MR, capability, forecast and decision methods are in [SPEC.md](SPEC.md),
[README.md](README.md), and `capacity_monitor/pipeline.py`. The additional views below do not
change the per-transformer decision-table outcome.

## Aggregate dashboard charts

`capacity_monitor/aggregate.py:county_control_statistics(results, period_start)` accepts plain
transformer result dictionaries and the first review-period date. It performs no I/O and returns:

- `p`, `u`, `x`, `s`: numerical `center` and `points` (date, value, ucl, lcl, out).
- `p_out`, `u_out`, `x_out`, `s_out`: counts of out-of-limit days inside the review period;
  a count is days, not transformers or signal events.
- `status`: `computed` or `insufficient_data` (availability, not process stability).
- `baseline_source`: `pre_period` or `all_dates_fallback`, with `baseline_dates`.

`webapp/viz.py:county_control_charts` calls that function and renders SVG only. `box_stats(values)`
also lives in the numerical module; it returns n/min/q1/median/q3/max, linearly interpolates quartiles
at index p*(n-1), ignores None, and returns None for empty input. Its whiskers use the full range.

For each day, the input contains each eligible transformer's daily peak divided by its rating.
Calibration cases, invalid/nonpositive ratings and missing/nonfinite load ratios are excluded.
A transformer can therefore be absent from a day; `n_d` is the number of eligible ratios on day d.
The reference days are dates before `period_start`. Currently, if none exist, all dates are used
instead. That fallback is an open statistical issue: it can fit limits to the same review observations
being evaluated. Fewer than two total dates or no reference observations returns empty charts.
A point is flagged only when strictly beyond a limit, with a numerical tolerance of 1e-9.

### p chart: fraction near rating

Let `h_d` count ratios at or above 0.90, and `p_d = h_d / n_d`.
The pooled reference fraction is `p_bar = sum(h_d) / sum(n_d)` over reference days.
Each day's limits are:

- `UCL_d = min(1, p_bar + 3 * sqrt(p_bar * (1 - p_bar) / n_d))`
- `LCL_d = max(0, p_bar - 3 * sqrt(p_bar * (1 - p_bar) / n_d))`

Values, centre and limits are displayed as percentages. Here 90% is the chart's fixed
`NEAR_RATIO` cutoff, separate from the forecast threshold in the decision playbook.
This describes the daily fraction near rating, not the probability of equipment failure.
Conventional binomial limits assume independent trials with a common underlying probability;
shared weather, repeat observations and unlike transformers can violate those assumptions.

### u chart: signal events per transformer

Let `c_d` count I-MR signal records dated on day d for eligible observations. Multiple rules firing
on one transformer can contribute multiple records. The rate is `u_d = c_d / n_d` and the pooled
reference rate is `u_bar = sum(c_d) / sum(n_d)`.

- `UCL_d = u_bar + 3 * sqrt(u_bar / n_d)`
- `LCL_d = max(0, u_bar - 3 * sqrt(u_bar / n_d))`

The chart multiplies rates and limits by 100 and labels them **signals per 100 transformers**.
This is an event rate, not the percentage of unique transformers needing review. Standard u-chart
limits assume Poisson events and comparable opportunities; correlated run rules and weather
can violate that model. These assumptions need assessment before operational interpretation.

### X-S chart: mean and spread of daily loading ratios

Each day is a subgroup of transformers. `x_bar_d` is the mean ratio and `s_d` is the sample
standard deviation with denominator `n_d - 1`. The reference centre `x_bar_bar` is the pooled mean
of all reference ratios (weighted by each day's size); `s_bar` is the unweighted mean of the
reference days' defined sample standard deviations.

For subgroup size n:

- `c4(n) = sqrt(2/(n-1)) * Gamma(n/2) / Gamma((n-1)/2)`
- `A3 = 3 / (c4(n) * sqrt(n))`
- `B3 = max(0, 1 - 3 * sqrt(1 - c4(n)^2) / c4(n))`
- `B4 = 1 + 3 * sqrt(1 - c4(n)^2) / c4(n)`
- Mean limits: `x_bar_bar ± A3 * s_bar`
- Spread limits: `B3 * s_bar`, `B4 * s_bar`

Both panels multiply values by 100, expressing means and spread on the percent-of-rating scale.
A day with fewer than two observations, or a reference spread of zero, is omitted from these panels.
Conventional X-S limits rely on independent, approximately normal observations and rational subgroups.
Different transformers observed together may not form such a subgroup; normalization by rating does
not establish comparability. Variable subgroup sizes also require review of the pooled estimators.

### Existing verification and remaining work

`tests/test_aggregate.py` checks hand-computed p/u/X/S limits and centers, variable subgroup size,
period signal counts, missing/nonfinite observations, empty/single-date inputs, constant/single-member
subgroups, explicit missing-baseline fallback, caller-input preservation, and box quartiles. It imports
only the numerical module. `tests/test_viz.py` retains the rendering/aggregation integration checks.

The saved 500-transformer report produced byte-for-byte identical SVGs and equal signal counts
before and after extraction. The next statistical review should address baseline policy and subgroup/
distribution assumptions. This refactor preserves existing formulas and does not establish suitability.

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
