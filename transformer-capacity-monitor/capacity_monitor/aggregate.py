"""Framework-independent numerical statistics for aggregate dashboard views.

These descriptive charts do not alter per-transformer decisions. Formulas and
assumption limitations are documented in METHODS.md. No rendering or I/O here.
"""
from __future__ import annotations

import math

NEAR_RATIO = 0.9


def _quantile(sorted_vals: list[float], p: float) -> float:
    if len(sorted_vals) == 1:
        return sorted_vals[0]
    idx = p * (len(sorted_vals) - 1)
    lo = int(idx)
    hi = min(lo + 1, len(sorted_vals) - 1)
    frac = idx - lo
    return sorted_vals[lo] * (1 - frac) + sorted_vals[hi] * frac


def box_stats(values: list[float]) -> dict | None:
    """Min, quartiles and max. Whiskers are the full range so every reading stays visible."""
    clean = sorted(v for v in values if v is not None)
    if not clean:
        return None
    return {
        "n": len(clean),
        "min": clean[0],
        "q1": _quantile(clean, 0.25),
        "median": _quantile(clean, 0.5),
        "q3": _quantile(clean, 0.75),
        "max": clean[-1],
    }


def _c4(n: int) -> float:
    """Unbiasing constant for a subgroup standard deviation."""
    if n < 2:
        return 1.0
    return math.sqrt(2 / (n - 1)) * math.exp(math.lgamma(n / 2) - math.lgamma((n - 1) / 2))


def _sample_sd(values: list[float]) -> float | None:
    if len(values) < 2:
        return None
    mean = sum(values) / len(values)
    return math.sqrt(sum((v - mean) ** 2 for v in values) / (len(values) - 1))


def _day_buckets(results: list[dict]) -> dict[str, dict]:
    days: dict[str, dict] = {}
    for result in results:
        if result.get("is_calibration"):
            continue
        chart = result.get("chart") or {}
        try:
            rating = float(result.get("rated_max"))
        except (TypeError, ValueError):
            continue
        if rating <= 0:
            continue
        signals_on: dict[str, int] = {}
        for signal in chart.get("signals") or []:
            day = signal.get("date") or ""
            signals_on[day] = signals_on.get(day, 0) + 1
        for day, value in zip(chart.get("dates") or [], chart.get("values") or []):
            if value is None:
                continue
            try:
                ratio = float(value) / rating
            except (TypeError, ValueError):
                continue
            if not math.isfinite(ratio):
                continue
            bucket = days.setdefault(day, {"ratios": [], "signals": 0})
            bucket["ratios"].append(ratio)
            bucket["signals"] += signals_on.get(day, 0)
    return days


def _beyond(value: float, ucl: float, lcl: float) -> bool:
    return value > ucl + 1e-9 or value < lcl - 1e-9


def county_control_statistics(results: list[dict], period_start: str) -> dict:
    """Return numerical p/u/X-S series, centers and period signal counts; no markup.

    Values use the existing display scale: percentages for p/X/S, events per 100
    transformers for u. `status` describes data availability, not process stability.
    The legacy all-date baseline fallback is retained explicitly in `baseline_source`.
    """
    days = _day_buckets(results)
    dates = sorted(days)
    historical = [d for d in dates if d < period_start]
    base = historical or dates
    source = "pre_period" if historical else "all_dates_fallback"
    empty = {
        "status": "insufficient_data", "baseline_source": source, "baseline_dates": base,
        **{key: {"points": [], "center": None} for key in ("p", "u", "x", "s")},
        "p_out": 0, "u_out": 0, "x_out": 0, "s_out": 0,
    }
    if len(dates) < 2:
        return empty

    def counted(day: str) -> tuple[int, int, int, float | None, float | None]:
        ratios = days[day]["ratios"]
        n = len(ratios)
        high = sum(1 for r in ratios if r >= NEAR_RATIO)
        mean = sum(ratios) / n if n else None
        return n, high, days[day]["signals"], mean, _sample_sd(ratios)

    base_n = sum(counted(d)[0] for d in base)
    if not base_n:
        return empty
    pbar = sum(counted(d)[1] for d in base) / base_n
    ubar = sum(counted(d)[2] for d in base) / base_n
    base_ratios = [r for d in base for r in days[d]["ratios"]]
    xbar_bar = sum(base_ratios) / len(base_ratios)
    base_s = [counted(d)[4] for d in base if counted(d)[4] is not None]
    sbar = sum(base_s) / len(base_s) if base_s else 0.0

    p_points, u_points, x_points, s_points = [], [], [], []
    p_out = u_out = x_out = s_out = 0
    for day in dates:
        n, high, signals, mean, sd = counted(day)
        if not n:
            continue
        in_period = day >= period_start
        se_p = math.sqrt(max(pbar * (1 - pbar), 0) / n)
        p_ucl, p_lcl = min(1.0, pbar + 3 * se_p), max(0.0, pbar - 3 * se_p)
        p_value = high / n
        p_hit = _beyond(p_value, p_ucl, p_lcl)
        p_out += int(p_hit and in_period)
        p_points.append({"date": day, "value": p_value * 100, "ucl": p_ucl * 100, "lcl": p_lcl * 100, "out": p_hit})

        se_u = math.sqrt(max(ubar, 0) / n)
        u_ucl, u_lcl = ubar + 3 * se_u, max(0.0, ubar - 3 * se_u)
        u_value = signals / n
        u_hit = _beyond(u_value, u_ucl, u_lcl)
        u_out += int(u_hit and in_period)
        u_points.append({"date": day, "value": u_value * 100, "ucl": u_ucl * 100, "lcl": u_lcl * 100, "out": u_hit})

        if mean is None or sd is None or sbar <= 0 or n < 2:
            continue
        c4 = _c4(n)
        sigma_factor = math.sqrt(max(1 - c4 * c4, 0)) / c4
        a3 = 3 / (c4 * math.sqrt(n))
        b4 = 1 + 3 * sigma_factor
        b3 = max(0.0, 1 - 3 * sigma_factor)
        x_ucl, x_lcl = (xbar_bar + a3 * sbar) * 100, (xbar_bar - a3 * sbar) * 100
        x_value = mean * 100
        x_hit = _beyond(x_value, x_ucl, x_lcl)
        x_out += int(x_hit and in_period)
        x_points.append({"date": day, "value": x_value, "ucl": x_ucl, "lcl": x_lcl, "out": x_hit})
        s_ucl, s_lcl = b4 * sbar * 100, b3 * sbar * 100
        s_value = sd * 100
        s_hit = _beyond(s_value, s_ucl, s_lcl)
        s_out += int(s_hit and in_period)
        s_points.append({"date": day, "value": s_value, "ucl": s_ucl, "lcl": s_lcl, "out": s_hit})

    return {
        "status": "computed", "baseline_source": source, "baseline_dates": base,
        "p": {"points": p_points, "center": pbar * 100},
        "u": {"points": u_points, "center": ubar * 100},
        "x": {"points": x_points, "center": xbar_bar * 100},
        "s": {"points": s_points, "center": sbar * 100},
        "p_out": p_out, "u_out": u_out, "x_out": x_out, "s_out": s_out,
    }
