"""Hourly load data for the heatmap: recorded readings by date and hour, plus a labeled seasonal model.

Recorded mode uses the readings feed as it is. Seasonal mode scales each transformer's recorded hourly
shape by the playbook's monthly factors; it is a MODEL for months with no recorded data and is labeled
as such wherever it is shown.
"""

from __future__ import annotations

import csv
import math
import threading
from datetime import datetime

from . import config
from .sources import feed_path

_lock = threading.Lock()
_cache: dict = {"key": None, "by_date": {}, "shape": {}, "level": {}, "dates": []}


def _feed_key():
    p = feed_path("readings")
    if not p.exists():
        return None
    st = p.stat()
    return (st.st_mtime_ns, st.st_size)


def _build() -> None:
    """Parse the readings feed once into {date: {tid: [24 hourly loads]}} plus per-transformer shapes."""
    by_date: dict[str, dict[str, list]] = {}
    with open(feed_path("readings"), "r", encoding="utf-8", newline="") as fh:
        for r in csv.DictReader(fh):
            try:
                ts = datetime.fromisoformat(r["timestamp"].strip())
                load = float(r["load"])
            except (KeyError, ValueError):
                continue
            if load != load:  # NaN
                continue
            day = by_date.setdefault(ts.date().isoformat(), {})
            arr = day.get(r["transformer_id"])
            if arr is None:
                arr = day[r["transformer_id"]] = [None] * 24
            h = ts.hour
            arr[h] = load if arr[h] is None else max(arr[h], load)
    # per-transformer average hourly shape (share of daily peak) and average daily peak level
    sums: dict[str, list] = {}
    counts: dict[str, int] = {}
    peaks: dict[str, list] = {}
    for day in by_date.values():
        for tid, arr in day.items():
            vals = [v for v in arr if v is not None]
            if len(vals) < 12:
                continue
            peak = max(vals)
            if peak <= 0:
                continue
            acc = sums.setdefault(tid, [0.0] * 24)
            for h, v in enumerate(arr):
                if v is not None:
                    acc[h] += v / peak
            counts[tid] = counts.get(tid, 0) + 1
            peaks.setdefault(tid, []).append(peak)
    shape = {tid: [x / counts[tid] for x in acc] for tid, acc in sums.items()}
    level = {tid: sum(p) / len(p) for tid, p in peaks.items()}
    _cache.update({"key": _feed_key(), "by_date": by_date, "shape": shape, "level": level, "dates": sorted(by_date)})


def _ensure() -> None:
    with _lock:
        if _cache["key"] != _feed_key():
            if _feed_key() is None:
                _cache.update({"key": None, "by_date": {}, "shape": {}, "level": {}, "dates": []})
            else:
                _build()


def dates() -> list[str]:
    _ensure()
    return list(_cache["dates"])


def recorded_day(date_iso: str) -> dict[str, list]:
    """{tid: [24 loads or null]} for one recorded date."""
    _ensure()
    return _cache["by_date"].get(date_iso, {})


def previous_recorded_day(date_iso: str) -> dict[str, list]:
    """The recorded day just before date_iso (empty if none), used to warm the thermal model up."""
    _ensure()
    earlier = [d for d in _cache["dates"] if d < date_iso]
    return _cache["by_date"].get(earlier[-1], {}) if earlier else {}


def typical_ambient(month: int, playbook: dict) -> float:
    monthly = (playbook.get("thermal_model") or {}).get("monthly_ambient_c") or {}
    return float(monthly.get(str(month), (playbook.get("thermal_model") or {}).get("ambient_c", 20.0)))


def typical_ambient_hours(month: int, playbook: dict) -> list[float]:
    """MODELED outside air for each hour of a typical day: the month's mean plus a daily swing (coldest
    before dawn, warmest at thermal_model.warmest_hour)."""
    tm = playbook.get("thermal_model") or {}
    mean = typical_ambient(month, playbook)
    swing = float(tm.get("diurnal_swing_c", 0.0))
    peak = int(tm.get("warmest_hour", 15))
    return [round(mean + swing * math.cos((h - peak) / 24.0 * 2.0 * math.pi), 1) for h in range(24)]


def temperature_multipliers(ambient_hours: list[float], playbook: dict) -> list[float]:
    """MODELED load response to outside air, hour by hour: heating load below the heating base, cooling
    load above the cooling base (seasonal_model.temperature_response). Scaled to average 1.0 over the
    day, so the month's calibration holds and the temperature only moves load between hours."""
    tr = (playbook.get("seasonal_model") or {}).get("temperature_response") or {}
    hb, hp = float(tr.get("heating_base_c", 15.0)), float(tr.get("heating_pct_per_degree", 0.0)) / 100.0
    cb, cp = float(tr.get("cooling_base_c", 22.0)), float(tr.get("cooling_pct_per_degree", 0.0)) / 100.0
    demand = [1.0 + hp * max(0.0, hb - t) + cp * max(0.0, t - cb) for t in ambient_hours]
    mean = sum(demand) / len(demand) if demand else 1.0
    return [d / mean for d in demand]


def seasonal_day(month: int, playbook: dict | None = None) -> dict:
    """MODELED {tid: [24 loads]} for a typical day of the given month, with the load following that
    month's typical outside air through the day."""
    _ensure()
    pb = playbook or config.load_playbook()
    sm = pb.get("seasonal_model", {})
    factor = float(sm.get("monthly_factors", {}).get(str(month), 1.0))
    boost = float(sm.get("winter_evening_boost", 0.0)) if month in (12, 1, 2) else 0.0
    ambient = typical_ambient_hours(month, pb)
    mult = temperature_multipliers(ambient, pb)
    out = {}
    for tid, shp in _cache["shape"].items():
        lvl = _cache["level"].get(tid, 0.0) * factor
        out[tid] = [lvl * shp[h] * mult[h] * (1.0 + (boost if 17 <= h <= 21 else 0.0)) for h in range(24)]
    return {"month": month, "factor": factor, "modeled": True, "loads": out,
            "ambient": ambient, "typical_ambient_c": typical_ambient(month, pb), "temperature_multipliers": [round(m, 4) for m in mult]}
