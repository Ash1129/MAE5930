"""Modeled view of what the load does inside a transformer: oil and winding hot-spot temperatures.

This is the IEEE C57.91 (loading guide) clause-7 exponential model, driven by the hourly loads the
tool already records. It is an ESTIMATE for the 3D view on the review page: the tool has no oil or
winding sensors, and these numbers feed no decision. Parameters live in playbook["thermal_model"].

  K            load / rated maximum
  top-oil rise ΔΘ_TO,U = ΔΘ_TO,R · ((K²·R + 1) / (R + 1))^n, approached with time constant τ_TO
  hot-spot rise over top oil ΔΘ_H = ΔΘ_H,R · K^(2m)   (winding time constant is minutes, so hourly steps use the ultimate value)
  hot spot Θ_H = ambient + ΔΘ_TO + ΔΘ_H
  aging factor F_AA = exp(15000/383 − 15000/(Θ_H + 273))   (1.0 at the 110 °C reference hot spot)
"""

from __future__ import annotations

import math

DEFAULTS = {
    "ambient_c": 20.0,
    "top_oil_rise_rated_c": 55.0,
    "hot_spot_rise_over_top_oil_rated_c": 25.0,
    "loss_ratio_R": 3.2,
    "oil_exponent_n": 0.8,
    "winding_exponent_m": 0.8,
    "oil_time_constant_h": 3.0,
    "hot_spot_limit_c": 110.0,
    "hot_spot_emergency_c": 120.0,
    "note": "IEEE C57.91 exponential model with typical ONAN distribution-transformer parameters and a fixed ambient; an estimate for the 3D view only, not used by any rule.",
}


def params(playbook: dict | None) -> dict:
    out = dict(DEFAULTS)
    out.update((playbook or {}).get("thermal_model") or {})
    return out


def aging_factor(hot_spot_c: float) -> float:
    return math.exp(15000.0 / 383.0 - 15000.0 / (hot_spot_c + 273.0))


def simulate(readings: list[dict], rating: float, playbook: dict | None = None, step_h: float = 1.0) -> dict:
    """Hourly top-oil and hot-spot estimates for a list of readings (dicts with timestamp and load).

    The oil starts at the steady state of the first hour's load, so the series needs no warm-up.
    """
    p = params(playbook)
    pts = [r for r in readings if r.get("load") is not None and rating]
    series = []
    to_rise = None
    peak = None
    for r in pts:
        k = max(float(r["load"]), 0.0) / float(rating)
        ult = p["top_oil_rise_rated_c"] * (((k * k) * p["loss_ratio_R"] + 1.0) / (p["loss_ratio_R"] + 1.0)) ** p["oil_exponent_n"]
        if to_rise is None:
            to_rise = ult
        else:
            to_rise = ult + (to_rise - ult) * math.exp(-step_h / p["oil_time_constant_h"])
        hs_rise = p["hot_spot_rise_over_top_oil_rated_c"] * (k ** (2.0 * p["winding_exponent_m"]))
        top_oil = p["ambient_c"] + to_rise
        hot_spot = top_oil + hs_rise
        row = {
            "timestamp": r["timestamp"],
            "load": round(float(r["load"]), 2),
            "k": round(k, 4),
            "top_oil_c": round(top_oil, 1),
            "hot_spot_c": round(hot_spot, 1),
            "aging": round(aging_factor(hot_spot), 3),
        }
        series.append(row)
        if peak is None or row["hot_spot_c"] > peak["hot_spot_c"]:
            peak = row
    hours_over = sum(1 for s in series if s["hot_spot_c"] >= p["hot_spot_limit_c"])
    return {
        "series": series,
        "peak": peak,
        "hours_at_or_over_limit": hours_over,
        "params": {k: v for k, v in p.items() if k != "note"},
        "note": p["note"],
        "modeled": True,
    }
