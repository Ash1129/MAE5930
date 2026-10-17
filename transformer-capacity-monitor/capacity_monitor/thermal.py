"""Modeled view of what the load does inside a transformer: oil and winding hot-spot temperatures.

This is the IEEE C57.91 (loading guide) clause-7 exponential model, driven by the hourly loads the
tool already records. It is an ESTIMATE for the 3D view on the review page: the tool has no oil or
winding sensors, and these numbers feed no decision.

  K            load / rated maximum
  top-oil rise ΔΘ_TO,U = ΔΘ_TO,R · ((K²·R + 1) / (R + 1))^n, approached with time constant τ_TO
  hot-spot rise over top oil ΔΘ_H = ΔΘ_H,R · K^(2m)   (winding time constant is minutes, so hourly steps use the ultimate value)
  hot spot Θ_H = ambient + ΔΘ_TO + ΔΘ_H
  aging factor F_AA = exp(15000/383 − 15000/(Θ_H + 273))   (1.0 at the 110 °C reference hot spot)

Inputs, in order of weight:
  1. nameplate values on the asset record (assets.csv columns top_oil_rise_c, hot_spot_rise_c,
     loss_ratio, oil_time_constant_h) when present;
  2. otherwise playbook["thermal_model"]["types"][kind] for the unit kind (pole or pad);
  3. otherwise playbook["thermal_model"] / the defaults below.
Ambient comes from the optional feed data/feeds/ambient.csv (hourly or daily) when present, else the
playbook's fixed ambient_c. The result records which sources were used so the page can say so.
"""

from __future__ import annotations

import csv
import math
from datetime import datetime
from pathlib import Path

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
}
NUMERIC = tuple(DEFAULTS)
# asset-record column -> model parameter (nameplate values, the strongest source)
ASSET_COLUMNS = {
    "top_oil_rise_c": "top_oil_rise_rated_c",
    "hot_spot_rise_c": "hot_spot_rise_over_top_oil_rated_c",
    "loss_ratio": "loss_ratio_R",
    "oil_time_constant_h": "oil_time_constant_h",
}


def kind_of(name: str | None) -> str:
    return "pole" if "pole" in (name or "").lower() else "pad"


def params(playbook: dict | None, kind: str | None = None, asset: dict | None = None) -> tuple[dict, str]:
    """Layer the parameter sources. Returns (params, description of the strongest source used)."""
    tm = (playbook or {}).get("thermal_model") or {}
    out = dict(DEFAULTS)
    out.update({k: float(v) for k, v in tm.items() if k in NUMERIC})
    source = "playbook defaults"
    typed = (tm.get("types") or {}).get(kind or "")
    if typed:
        out.update({k: float(v) for k, v in typed.items() if k in NUMERIC})
        source = f"typical {kind} unit (playbook)"
    used = []
    for col, key in ASSET_COLUMNS.items():
        raw = (asset or {}).get(col)
        if raw is None or str(raw).strip() == "":
            continue
        try:
            v = float(raw)
        except (TypeError, ValueError):
            continue
        if math.isfinite(v) and v > 0:
            out[key] = v
            used.append(col)
    if used:
        source = "nameplate (asset record)" if len(used) == len(ASSET_COLUMNS) else f"nameplate for {len(used)} of {len(ASSET_COLUMNS)} values, typical {kind or 'unit'} for the rest"
    return out, source


def asset_record(path: Path, transformer_id: str) -> dict | None:
    """The asset row for one transformer, read fresh so nameplate columns need no rerun."""
    if not path.exists():
        return None
    with open(path, "r", encoding="utf-8", newline="") as fh:
        for row in csv.DictReader(fh):
            if (row.get("transformer_id") or "").strip() == transformer_id:
                return row
    return None


def load_ambient(path: Path) -> dict:
    """Optional ambient feed: rows of timestamp,temp_c (hourly) or date,temp_c (daily). Bad rows are skipped."""
    hourly, daily = {}, {}
    if not path.exists():
        return {"hourly": hourly, "daily": daily, "present": False}
    with open(path, "r", encoding="utf-8", newline="") as fh:
        for row in csv.DictReader(fh):
            try:
                t = float(row.get("temp_c", ""))
            except (TypeError, ValueError):
                continue
            if not math.isfinite(t):
                continue
            ts = (row.get("timestamp") or "").strip()
            d = (row.get("date") or "").strip()
            if ts:
                hourly[ts[:13]] = t  # YYYY-MM-DDTHH
                daily.setdefault(ts[:10], []).append(t)
            elif d:
                daily.setdefault(d[:10], []).append(t)
    return {"hourly": hourly, "daily": {k: sum(v) / len(v) for k, v in daily.items()}, "present": True}


def ambient_at(ambient: dict | None, timestamp: str, fallback: float) -> tuple[float, bool]:
    """Ambient for one reading hour: the recorded hour, else that day's mean, else the fixed assumption."""
    if not ambient or not ambient.get("present"):
        return fallback, False
    key = (timestamp or "")[:13]
    if key in ambient["hourly"]:
        return ambient["hourly"][key], True
    day = (timestamp or "")[:10]
    if day in ambient["daily"]:
        return ambient["daily"][day], True
    return fallback, False


def aging_factor(hot_spot_c: float) -> float:
    return math.exp(15000.0 / 383.0 - 15000.0 / (hot_spot_c + 273.0))


def simulate(readings: list[dict], rating: float, playbook: dict | None = None, step_h: float = 1.0,
             kind: str | None = None, asset: dict | None = None, ambient: dict | None = None) -> dict:
    """Hourly top-oil and hot-spot estimates for a list of readings (dicts with timestamp and load).

    The oil starts at the steady state of the first hour's load, so the series needs no warm-up.
    """
    p, param_source = params(playbook, kind, asset)
    pts = [r for r in readings if r.get("load") is not None and rating]
    series = []
    to_rise = None
    peak = None
    recorded_hours = 0
    for r in pts:
        amb, recorded = ambient_at(ambient, r.get("timestamp", ""), p["ambient_c"])
        recorded_hours += 1 if recorded else 0
        k = max(float(r["load"]), 0.0) / float(rating)
        ult = p["top_oil_rise_rated_c"] * (((k * k) * p["loss_ratio_R"] + 1.0) / (p["loss_ratio_R"] + 1.0)) ** p["oil_exponent_n"]
        if to_rise is None:
            to_rise = ult
        else:
            to_rise = ult + (to_rise - ult) * math.exp(-step_h / p["oil_time_constant_h"])
        hs_rise = p["hot_spot_rise_over_top_oil_rated_c"] * (k ** (2.0 * p["winding_exponent_m"]))
        top_oil = amb + to_rise
        hot_spot = top_oil + hs_rise
        row = {
            "timestamp": r["timestamp"],
            "load": round(float(r["load"]), 2),
            "k": round(k, 4),
            "ambient_c": round(amb, 1),
            "top_oil_c": round(top_oil, 1),
            "hot_spot_c": round(hot_spot, 1),
            "aging": round(aging_factor(hot_spot), 3),
        }
        series.append(row)
        if peak is None or row["hot_spot_c"] > peak["hot_spot_c"]:
            peak = row
    hours_over = sum(1 for s in series if s["hot_spot_c"] >= p["hot_spot_limit_c"])
    if series and recorded_hours == len(series):
        ambient_source = "recorded ambient feed (every hour)"
    elif recorded_hours:
        ambient_source = f"recorded ambient feed for {recorded_hours} of {len(series)} hours, fixed {p['ambient_c']:g} °C for the rest"
    else:
        ambient_source = f"fixed {p['ambient_c']:g} °C assumption (no ambient feed)"
    return {
        "series": series,
        "peak": peak,
        "hours_at_or_over_limit": hours_over,
        "params": p,
        "sources": {"parameters": param_source, "ambient": ambient_source, "kind": kind or "unit"},
        "note": "IEEE C57.91 exponential model; an estimate for the 3D view only, not used by any rule.",
        "modeled": True,
    }
