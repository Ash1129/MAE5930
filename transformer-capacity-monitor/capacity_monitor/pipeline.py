"""Steps 6-12: align, validate, control-chart, decide stability, project demand, measure capability, decide review.

Pure functions over plain dicts. Deterministic; no AI.
"""

from __future__ import annotations

import csv
import math
import re
import statistics
from datetime import date

from . import config
from .guards import RunFailed, check_text
from .sources import Period

Z_95 = 1.959964  # two-sided 95% normal quantile


# ---- Step 6: align the run inputs -------------------------------------------------------

def _point_in_ring(lon: float, lat: float, ring: list) -> bool:
    inside = False
    n = len(ring)
    j = n - 1
    for i in range(n):
        xi, yi = ring[i][0], ring[i][1]
        xj, yj = ring[j][0], ring[j][1]
        if (yi > lat) != (yj > lat):
            x_cross = (xj - xi) * (lat - yi) / ((yj - yi) or 1e-12) + xi
            if lon < x_cross:
                inside = not inside
        j = i
    return inside


def point_in_area(lon: float, lat: float, area: dict) -> bool:
    for poly in area["polygons"]:
        if not poly:
            continue
        if _point_in_ring(lon, lat, poly[0]) and not any(_point_in_ring(lon, lat, hole) for hole in poly[1:]):
            return True
    return False


def align_inputs(period: Period, readings: dict, assets: dict, boundaries: dict, forecasts: dict, playbook: dict) -> dict:
    """Step 6: match readings, ratings, boundary areas and forecasts to the same period and identifiers."""
    areas = {a["area_id"]: a for a in boundaries["rows"]}
    wanted_version = playbook.get("forecast", {}).get("version")
    forecast_by_area = {}
    for f in forecasts["rows"]:
        if wanted_version and f["forecast_version"] != wanted_version:
            continue
        forecast_by_area.setdefault(f["area_id"], f)

    transformers: dict[str, dict] = {}
    for a in assets["rows"]:
        if not a["in_effect"]:
            continue
        located = []
        if a["lat"] is not None and a["lon"] is not None:
            located = [aid for aid, ar in areas.items() if point_in_area(a["lon"], a["lat"], ar)]
        declared = a["area_id"]
        if declared and declared in areas:
            chosen = declared
            allocation = "declared_primary_area"
        elif len(located) == 1:
            chosen = located[0]
            allocation = "located_by_boundary"
        else:
            chosen = declared or (located[0] if located else "")
            allocation = "declared_primary_area" if declared else ("first_located_area" if located else "none")
        transformers[a["transformer_id"]] = {
            **a,
            "located_areas": located,
            "declared_area": declared,
            "area_id": chosen,
            "area_name": areas.get(chosen, {}).get("name", ""),
            "allocation": allocation,
            "allocation_flag": (len(located) != 1) or (declared and located and declared not in located),
            "forecast": forecast_by_area.get(chosen),
            "daily_peaks": {},
            "period_readings": [],
            "reading_units": [],
        }

    unknown = set()
    for r in readings["rows"]:
        t = transformers.get(r["transformer_id"])
        if t is None:
            unknown.add(r["transformer_id"])
            continue
        d = r["date"]
        if d not in t["daily_peaks"] or r["load"] > t["daily_peaks"][d]:
            t["daily_peaks"][d] = r["load"]
        if r["unit"] and r["unit"] not in t["reading_units"]:
            t["reading_units"].append(r["unit"])
        if period.start.isoformat() <= d <= period.end.isoformat():
            t["period_readings"].append(r)

    return {
        "period": period.to_dict(),
        "transformers": transformers,
        "unknown_reading_ids": sorted(unknown),
        "feed_validity": {
            "boundaries": boundaries["meta"],
            "forecast_versions": forecasts["meta"].get("versions", []),
            "forecast_version_wanted": wanted_version,
            "forecast_rows_used": len(forecast_by_area),
        },
        "sources": {
            "readings": readings["source"],
            "assets": assets["source"],
            "boundaries": boundaries["source"],
            "forecast": forecasts["source"],
        },
        "loader_problems": readings["problems"] + assets["problems"] + boundaries["problems"] + forecasts["problems"],
        "counts": {
            "transformers_monitored": len(transformers),
            "readings_in_window": len(readings["rows"]),
            "areas": len(areas),
            "forecast_areas": len(forecast_by_area),
        },
    }


# ---- Step 7: check input completeness ---------------------------------------------------

def _covers(valid_from, valid_to, day: date) -> bool:
    if valid_from and date.fromisoformat(valid_from) > day:
        return False
    if valid_to and date.fromisoformat(valid_to) < day:
        return False
    return True


def check_completeness(joined: dict, playbook: dict) -> dict:
    """Step 7: blocking problems stop the run (RunFailed); warnings are carried to the report."""
    period = Period.from_dict(joined["period"])
    blocking: list[str] = []
    warnings: list[str] = []

    for p in joined["loader_problems"]:
        (warnings if "instruction-like" in p or "blocked term" in p else blocking).append(p)

    fv = joined["feed_validity"]
    b = fv["boundaries"]
    if not _covers(b.get("valid_from"), b.get("valid_to"), period.end):
        blocking.append(
            f"Boundary feed is for a different reporting period (valid {b.get('valid_from')} to {b.get('valid_to')}, "
            f"run period ends {period.end})"
        )
    if fv["forecast_version_wanted"] and fv["forecast_version_wanted"] not in fv["forecast_versions"]:
        blocking.append(
            f"Heat-pump forecast version {fv['forecast_version_wanted']!r} (playbook) not found in feed; "
            f"feed has {fv['forecast_versions']}"
        )
    if fv["forecast_rows_used"] == 0:
        blocking.append("Heat-pump forecast feed has no usable rows for the approved version")

    if joined["counts"]["transformers_monitored"] == 0:
        blocking.append("No transformer asset records are in effect for this period")

    period_dates = [d.isoformat() for d in period.dates()]
    for tid, t in sorted(joined["transformers"].items()):
        if t["rated_max"] is None or t["rated_max"] <= 0:
            blocking.append(f"{tid}: no rated maximum load on the asset record")
        if not t["unit"]:
            blocking.append(f"{tid}: asset record has no unit")
        if t["lat"] is None or t["lon"] is None:
            blocking.append(f"{tid}: asset record has no location")
        units = t["reading_units"]
        if units and t["unit"] and any(u.lower() != t["unit"].lower() for u in units):
            blocking.append(f"{tid}: reading unit {units} does not match rating unit {t['unit']!r}")
        missing_days = [d for d in period_dates if d not in t["daily_peaks"]]
        if missing_days:
            blocking.append(f"{tid}: no readings for {len(missing_days)} of {len(period_dates)} period days (first missing {missing_days[0]})")
        if not t["area_id"]:
            warnings.append(f"{tid}: could not be placed in any boundary area; forecast cannot be applied")
        elif t["declared_area"] and t["located_areas"] and t["declared_area"] not in t["located_areas"]:
            warnings.append(
                f"{tid}: declared area {t['declared_area']} but its location falls in {t['located_areas']}; "
                f"using {t['allocation']} = {t['area_id']}"
            )
        elif not t["declared_area"] and len(t["located_areas"]) != 1:
            warnings.append(f"{tid}: no declared area and location falls in {len(t['located_areas'])} area(s); using {t['allocation']} = {t['area_id']}")
        if t["forecast"] is None:
            warnings.append(f"{tid}: no heat-pump forecast row for area {t['area_id'] or '(none)'}")
        for prob in check_text(t.get("notes"), f"{tid} notes", max_len=500):
            warnings.append(prob)
            t["notes"] = "[quarantined: instruction-like or blocked text removed]"
    if joined["unknown_reading_ids"]:
        warnings.append(f"Readings present for {len(joined['unknown_reading_ids'])} unknown transformer id(s): {joined['unknown_reading_ids'][:5]}")

    if blocking:
        raise RunFailed(7, f"Input completeness check failed with {len(blocking)} blocking problem(s)", blocking + [f"warning: {w}" for w in warnings])
    return {"blocking": [], "warnings": warnings}


# ---- Step 8: check load stability (I-MR chart) ------------------------------------------

def imr_chart(daily_peaks: dict, period: Period, playbook: dict) -> dict:
    """Individuals and moving-range chart on one value per day (the daily peak).

    Limits come from the baseline (days before the period) and describe historical variation.
    They are not the rated maximum.
    """
    cp = playbook["chart"]
    pts = sorted((d, float(v)) for d, v in daily_peaks.items() if v is not None and math.isfinite(float(v)))
    dates = [d for d, _ in pts]
    vals = [v for _, v in pts]
    baseline_idx = [i for i, d in enumerate(dates) if d < period.start.isoformat()]
    n_base = len(baseline_idx)
    out = {
        "dates": dates,
        "values": vals,
        "n_points": len(vals),
        "n_baseline": n_base,
        "min_history_points": int(cp["min_history_points"]),
        "signals": [],
        "moving_ranges": [None] + [abs(vals[i] - vals[i - 1]) for i in range(1, len(vals))],
    }
    if n_base < int(cp["min_history_points"]):
        out.update({"status": "insufficient_history", "center": None, "ucl": None, "lcl": None, "sigma": None, "mr_bar": None, "mr_ucl": None})
        return out
    base = [vals[i] for i in baseline_idx]
    mrs = [abs(base[i] - base[i - 1]) for i in range(1, len(base))]
    mr_bar = sum(mrs) / len(mrs)
    center = sum(base) / len(base)
    if mr_bar <= 0:
        out.update({"status": "zero_variation", "center": center, "ucl": center, "lcl": center, "sigma": 0.0, "mr_bar": 0.0, "mr_ucl": 0.0})
        return out
    sigma = mr_bar / float(cp["d2"])
    ucl = center + float(cp["E2"]) * mr_bar
    lcl = center - float(cp["E2"]) * mr_bar
    mr_ucl = float(cp["D4"]) * mr_bar
    out.update({"center": center, "ucl": ucl, "lcl": lcl, "sigma": sigma, "mr_bar": mr_bar, "mr_ucl": mr_ucl})

    signals = []
    for i, v in enumerate(vals):
        if v > ucl or v < lcl:
            signals.append({"rule": "beyond_3_sigma", "date": dates[i], "value": v, "in_period": dates[i] >= period.start.isoformat()})
    # 2 of 3 consecutive beyond 2 sigma on the same side
    for i in range(2, len(vals)):
        window = vals[i - 2 : i + 1]
        hi = sum(1 for v in window if v > center + 2 * sigma)
        lo = sum(1 for v in window if v < center - 2 * sigma)
        if hi >= 2 or lo >= 2:
            signals.append({"rule": "two_of_three_beyond_2_sigma", "date": dates[i], "value": vals[i], "in_period": dates[i] >= period.start.isoformat()})
    # 8 in a row on one side of the center line
    run_side, run_len = 0, 0
    for i, v in enumerate(vals):
        side = 1 if v > center else (-1 if v < center else 0)
        if side != 0 and side == run_side:
            run_len += 1
        else:
            run_side, run_len = side, (1 if side else 0)
        if run_len == 8:
            signals.append({"rule": "eight_in_a_row_one_side", "date": dates[i], "value": v, "in_period": dates[i] >= period.start.isoformat()})
    for i, mr in enumerate(out["moving_ranges"]):
        if mr is not None and mr > mr_ucl:
            signals.append({"rule": "moving_range_beyond_ucl", "date": dates[i], "value": mr, "in_period": dates[i] >= period.start.isoformat()})
    # keep only rules enabled in the playbook, one entry per (rule, date)
    enabled = set(cp.get("run_rules", ["beyond_3_sigma", "two_of_three_beyond_2_sigma", "eight_in_a_row_one_side", "moving_range_beyond_ucl"]))
    seen = set()
    for s in signals:
        key = (s["rule"], s["date"])
        if s["rule"] in enabled and key not in seen:
            seen.add(key)
            out["signals"].append(s)
    out["status"] = "signal" if out["signals"] else "stable"
    return out


def check_stability(joined: dict, playbook: dict) -> dict:
    """Step 8 for every transformer."""
    period = Period.from_dict(joined["period"])
    charts = {}
    for tid, t in joined["transformers"].items():
        charts[tid] = imr_chart(t["daily_peaks"], period, playbook)
    return charts


# ---- Step 9: is the load pattern stable? ------------------------------------------------

def decide_stability(chart: dict) -> str:
    """Returns 'stable', 'signal', 'insufficient_history' or 'zero_variation'."""
    return chart["status"]


# ---- Step 10: project demand growth -----------------------------------------------------

def project_demand(t: dict, period: Period, playbook: dict) -> dict:
    """Apply the heat-pump adoption forecast with the recorded allocation rule to estimate a future peak."""
    period_vals = [v for d, v in t["daily_peaks"].items() if period.start.isoformat() <= d <= period.end.isoformat()]
    period_peak = max(period_vals) if period_vals else None
    f = t.get("forecast")
    if f is None or period_peak is None or t.get("customers") is None:
        reason = "no forecast for area" if f is None else ("no period readings" if period_peak is None else "customer count missing on asset record")
        return {"period_peak": period_peak, "projected_peak": None, "added_load": None, "assumptions": {"reason_not_projected": reason}}
    added_share = max(0.0, f["hp_share_forecast"] - f["hp_share_base"])
    added_kw = t["customers"] * added_share * f["kw_per_heat_pump"]
    # Unit model: forecast demand is real power (kW); readings and ratings are apparent power (kVA)
    # unless the asset unit says kW. Convert with the playbook power factor and record it.
    unit = (t.get("unit") or "").strip().lower()
    pf = float(playbook.get("forecast", {}).get("power_factor", 1.0))
    if unit in ("kva", "mva"):
        added_load = added_kw / pf
        unit_note = f"kW converted to {t['unit']} using power factor {pf}"
    elif unit in ("kw", "mw"):
        added_load = added_kw
        unit_note = "forecast kW added directly to kW readings"
    else:
        added_load = added_kw / pf
        unit_note = f"unit {t.get('unit')!r} not recognized; treated as apparent power with power factor {pf}"
    if unit in ("mva", "mw"):
        added_load = added_load / 1000.0
        unit_note += "; kW scaled to MW/MVA"
    return {
        "period_peak": period_peak,
        "projected_peak": period_peak + added_load,
        "added_load": added_load,
        "assumptions": {
            "added_kw": added_kw,
            "power_factor": pf,
            "unit_note": unit_note,
            "forecast_version": f["forecast_version"],
            "horizon": f["horizon_label"],
            "area_id": t["area_id"],
            "area_name": t.get("area_name", ""),
            "allocation_method": t["allocation"],
            "allocation_flagged": bool(t["allocation_flag"]),
            "located_areas": t["located_areas"],
            "customers_served": t["customers"],
            "hp_share_base": f["hp_share_base"],
            "hp_share_forecast": f["hp_share_forecast"],
            "kw_per_heat_pump": f["kw_per_heat_pump"],
            "formula": "projected_peak = period_peak + customers x (hp_share_forecast - hp_share_base) x kw_per_heat_pump / power_factor",
        },
    }


# ---- Step 11: measure capacity headroom -------------------------------------------------

def _normality_jarque_bera(vals: list) -> dict:
    """Jarque-Bera test for normality (stdlib). p-value is exact for the chi-square(2) reference."""
    n = len(vals)
    mean = sum(vals) / n
    m2 = sum((v - mean) ** 2 for v in vals) / n
    if m2 <= 0:
        return {"statistic": None, "p_value": None, "skewness": 0.0, "excess_kurtosis": 0.0}
    m3 = sum((v - mean) ** 3 for v in vals) / n
    m4 = sum((v - mean) ** 4 for v in vals) / n
    skew = m3 / m2 ** 1.5
    kurt = m4 / m2 ** 2 - 3.0
    jb = n / 6.0 * (skew ** 2 + kurt ** 2 / 4.0)
    return {"statistic": jb, "p_value": math.exp(-jb / 2.0), "skewness": skew, "excess_kurtosis": kurt}


def _lag1_autocorrelation(vals: list) -> float | None:
    n = len(vals)
    if n < 3:
        return None
    mean = sum(vals) / n
    denom = sum((v - mean) ** 2 for v in vals)
    if denom <= 0:
        return None
    return sum((vals[i] - mean) * (vals[i - 1] - mean) for i in range(1, n)) / denom


def check_capability_assumptions(vals: list, playbook: dict) -> dict:
    """Independence (lag-1 autocorrelation) and normality (Jarque-Bera) checks required for a
    conventional Cpk interpretation (NIST/SEMATECH e-Handbook 6.1.6). Returns flags, never raises."""
    cap = playbook["capability"]
    n = len(vals)
    flags = []
    r1 = _lag1_autocorrelation(vals)
    band = 2.0 / math.sqrt(n) if n > 0 else None
    if r1 is not None and band is not None and abs(r1) > band:
        flags.append(f"serial correlation: lag-1 autocorrelation {r1:.2f} exceeds +/-{band:.2f}")
    jb = _normality_jarque_bera(vals)
    alpha = float(cap.get("normality_alpha", 0.05))
    if jb["p_value"] is not None and jb["p_value"] < alpha:
        flags.append(f"non-normal daily peaks: Jarque-Bera p={jb['p_value']:.3f} (skew {jb['skewness']:.2f}, excess kurtosis {jb['excess_kurtosis']:.2f})")
    return {"lag1_autocorrelation": r1, "autocorrelation_band": band, "jarque_bera": jb, "flags": flags, "note": "Daily peaks can carry seasonality and weather effects; a 60-day window limits but does not remove them."}


def capacity_headroom(chart: dict, rating: float, projection: dict, playbook: dict) -> dict:
    """One-sided Cpk (Cpu) against the rated maximum with a 95% interval; forecast margin against rating.

    sigma comes from the average moving range (MRbar/d2). The interval uses Bissell's approximation
    with the effective degrees of freedom of that estimator, 0.62 x (n-1) (Wheeler), which a simulation
    in tests/test_pipeline.py shows gives about 95% coverage; n-1 would give about 88%.
    """
    cap = playbook["capability"]
    vals = [v for v in chart["values"] if v is not None and math.isfinite(v)]
    n = len(vals)
    out = {
        "n": n,
        "rating": rating,
        "cpk": None,
        "cpk_ci_low": None,
        "cpk_ci_high": None,
        "mean": None,
        "sigma_within": None,
        "insufficient_data": False,
        "assumption_flags": [],
        "assumptions": None,
        "period_peak": projection.get("period_peak"),
        "period_peak_ratio": (projection["period_peak"] / rating) if projection.get("period_peak") is not None else None,
        "projected_peak": projection.get("projected_peak"),
        "forecast_ratio": (projection["projected_peak"] / rating) if projection.get("projected_peak") is not None else None,
        "forecast_margin": (rating - projection["projected_peak"]) if projection.get("projected_peak") is not None else None,
    }
    if chart["status"] != "stable":
        out["insufficient_data"] = True
        out["note"] = f"Capability not calculated: load pattern is {chart['status'].replace('_', ' ')}, not confirmed stable"
        return out
    if n < int(cap["min_points"]) or n < 3:
        out["insufficient_data"] = True
        out["note"] = f"Capability not calculated: {n} points, playbook minimum is {cap['min_points']}"
        return out
    mean = sum(vals) / n
    mrs = [abs(vals[i] - vals[i - 1]) for i in range(1, n)]
    sigma = (sum(mrs) / len(mrs)) / float(playbook["chart"]["d2"])
    if sigma <= 0:
        out["insufficient_data"] = True
        out["note"] = "Capability not calculated: zero variation in readings"
        return out
    cpk = (rating - mean) / (3.0 * sigma)
    df_factor = float(cap.get("mr_effective_df_factor", 0.62))
    df_eff = max(1.0, df_factor * (n - 1))
    half = Z_95 * math.sqrt(1.0 / (9.0 * n) + (cpk * cpk) / (2.0 * df_eff))
    checks = check_capability_assumptions(vals, playbook)
    out.update(
        {
            "cpk": cpk,
            "cpk_ci_low": cpk - half,
            "cpk_ci_high": cpk + half,
            "mean": mean,
            "sigma_within": sigma,
            "effective_df": df_eff,
            "confidence_level": cap["confidence_level"],
            "assumption_flags": checks["flags"],
            "assumptions": checks,
        }
    )
    return out


# ---- Step 12: does a transformer need review? (decision table) --------------------------

_COND = re.compile(r"^\s*(\w+)\s*(>=|<=|==|!=|>|<|is missing|is present)\s*(.*?)\s*$")


_PLACEHOLDER = re.compile(r"\$\{([a-zA-Z0-9_.]+)\}")


def _resolve_placeholders(text: str, playbook: dict) -> str:
    """Replace ${section.key} with the playbook value so thresholds live in one place."""

    def sub(m):
        node = playbook
        for part in m.group(1).split("."):
            if not isinstance(node, dict) or part not in node:
                raise ValueError(f"decision table refers to unknown playbook value {m.group(1)!r}")
            node = node[part]
        return str(node)

    return _PLACEHOLDER.sub(sub, text)


def load_decision_table(path=None, playbook: dict | None = None) -> list[dict]:
    path = path or config.DECISION_TABLE_PATH
    playbook = playbook or config.load_playbook()
    with open(path, "r", encoding="utf-8", newline="") as fh:
        rows = list(csv.DictReader(fh))
    for r in rows:
        if r["when"].startswith("REPLACE") or r["then"].startswith("REPLACE"):
            raise ValueError("rules/decision-table.csv still contains REPLACE placeholders")
        r["when_template"] = r["when"]
        r["when"] = _resolve_placeholders(r["when"], playbook)
        r["notes"] = _resolve_placeholders(r["notes"], playbook)
    return rows


def _literal(text: str):
    text = text.strip()
    if text.startswith(("'", '"')) and text.endswith(("'", '"')):
        return text[1:-1]
    return float(text)


def _eval_condition(cond: str, facts: dict) -> bool:
    cond = cond.strip()
    if cond.lower() == "otherwise":
        return True
    parts = re.split(r"\s+and\s+", cond)
    for part in parts:
        m = _COND.match(part)
        if not m:
            raise ValueError(f"Cannot parse decision-table condition: {part!r}")
        field, op, rhs = m.group(1), m.group(2), m.group(3)
        if field not in facts:
            raise ValueError(f"Decision-table condition uses unknown field {field!r}")
        val = facts[field]
        if op == "is missing":
            if val is not None:
                return False
            continue
        if op == "is present":
            if val is None:
                return False
            continue
        lit = _literal(rhs)
        if val is None:
            return False
        if op == ">=" and not val >= lit:
            return False
        if op == "<=" and not val <= lit:
            return False
        if op == ">" and not val > lit:
            return False
        if op == "<" and not val < lit:
            return False
        if op == "==" and not val == lit:
            return False
        if op == "!=" and not val != lit:
            return False
    return True


def needs_review(facts: dict, table: list[dict]) -> dict:
    """First matching row wins. facts: stability, cpk, cpk_ci_low, cpk_ci_high, forecast_ratio, period_peak_ratio."""
    for row in table:
        if _eval_condition(row["when"], facts):
            return {"outcome": row["then"], "rule": row["rule"], "reason": row["notes"], "condition": row["when"]}
    raise ValueError("Decision table has no matching row (add an 'otherwise' row)")


# ---- Whole-pipeline helper used by run.py and the DAG -------------------------------------

def evaluate_transformers(joined: dict, charts: dict, playbook: dict, table: list[dict]) -> dict:
    """Steps 9-12 for each transformer. Returns {transformer_id: result dict}."""
    period = Period.from_dict(joined["period"])
    results = {}
    for tid, t in sorted(joined["transformers"].items()):
        chart = charts[tid]
        stability = decide_stability(chart)
        # Step 10 runs only for stable transformers (step 9 routes signals/insufficient history to review).
        if stability == "stable":
            projection = project_demand(t, period, playbook)
        else:
            vals = [v for d, v in t["daily_peaks"].items() if period.start.isoformat() <= d <= period.end.isoformat()]
            projection = {"period_peak": max(vals) if vals else None, "projected_peak": None, "added_load": None, "assumptions": {"reason_not_projected": f"load pattern {stability}"}}
        capacity = capacity_headroom(chart, t["rated_max"], projection, playbook)
        facts = {
            "stability": stability,
            "cpk": capacity["cpk"],
            "cpk_ci_low": capacity["cpk_ci_low"],
            "cpk_ci_high": capacity["cpk_ci_high"],
            "forecast_ratio": capacity["forecast_ratio"],
            "period_peak_ratio": capacity["period_peak_ratio"],
            "assumption_flags": float(len(capacity["assumption_flags"])),
        }
        decision = needs_review(facts, table)
        results[tid] = {
            "transformer_id": tid,
            "name": t["name"],
            "area_id": t["area_id"],
            "area_name": t.get("area_name", ""),
            "rated_max": t["rated_max"],
            "unit": t["unit"],
            "customers": t["customers"],
            "customer_class": t.get("customer_class", "unknown"),
            "lat": t["lat"],
            "lon": t["lon"],
            "stability": stability,
            "chart": chart,
            "projection": projection,
            "capacity": capacity,
            "decision": decision,
            "status": decision["outcome"],
            "period_readings": t["period_readings"],
            "notes": t.get("notes", ""),
        }
    return results


def summarize(results: dict) -> dict:
    counts = {"within_limits": 0, "review_needed": 0, "stable": 0, "signal": 0, "insufficient_history": 0, "zero_variation": 0}
    for r in results.values():
        counts[r["status"]] = counts.get(r["status"], 0) + 1
        counts[r["stability"]] = counts.get(r["stability"], 0) + 1
    counts["transformers"] = len(results)
    return counts
