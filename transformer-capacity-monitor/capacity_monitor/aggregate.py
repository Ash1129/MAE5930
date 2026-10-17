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


def county_trend_statistics(results: list[dict]) -> dict:
    """Daily descriptive summaries; no control limits, baseline fit or alarm decisions.

    Percentages and quartiles use only finite peaks with finite positive ratings.
    Signals count distinct transformer IDs with >=1 rule on an eligible day.
    Calibration cases are excluded. Missing days are not imputed as zero.
    """
    days = {}
    for index, result in enumerate(results):
        if result.get("is_calibration"):
            continue
        try:
            rating = float(result.get("rated_max"))
        except (TypeError, ValueError):
            continue
        if not math.isfinite(rating) or rating <= 0:
            continue
        tid = result.get("transformer_id") or ("row", index)
        chart = result.get("chart") or {}
        signal_dates = {sig.get("date") for sig in chart.get("signals") or []}
        for day, value in zip(chart.get("dates") or [], chart.get("values") or []):
            try:
                ratio = float(value) / rating
            except (TypeError, ValueError):
                continue
            if not math.isfinite(ratio):
                continue
            bucket = days.setdefault(day, {})
            # Result records are normally unique by transformer; avoid counting duplicates twice.
            bucket[tid] = (ratio, day in signal_dates or bucket.get(tid, (0, False))[1])
    points = []
    for day, observations in sorted(days.items()):
        ratios = [ratio for ratio, _ in observations.values()]
        n = len(ratios)
        high = sum(ratio >= NEAR_RATIO for ratio in ratios)
        quartiles = box_stats(ratios)
        points.append({
            "date": day, "n": n, "near_rating_count": high,
            "near_rating_pct": high / n * 100,
            "signal_transformers": sum(flag for _, flag in observations.values()),
            "median_pct": quartiles["median"] * 100,
            "q1_pct": quartiles["q1"] * 100, "q3_pct": quartiles["q3"] * 100,
        })
    return {"status": "computed" if points else "insufficient_data", "points": points}
