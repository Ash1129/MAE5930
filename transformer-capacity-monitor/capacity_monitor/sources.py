"""Steps 2-5: load the four source feeds for a measurement period.

Feeds are files in data/feeds/ (see FEED_FILES). Each loader returns a dict with
`rows`, a `source` reference (path, size, modified time, checksum, row count) and
metadata. Nothing here changes equipment or settings.

To connect a real upstream system, replace the file read inside `_read_csv` /
`_read_geojson` with the connector call and keep the returned shape identical.
"""

from __future__ import annotations

import csv
import hashlib
import json
import math
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from pathlib import Path

from . import config
from .guards import RunFailed, scan_rows, with_retries


@dataclass
class Period:
    """A measurement period: `period_days` days ending on `end` (inclusive)."""

    end: date
    days: int = 7
    history_days: int = 60

    @property
    def start(self) -> date:
        return self.end - timedelta(days=self.days - 1)

    @property
    def history_start(self) -> date:
        return self.end - timedelta(days=self.history_days)

    @property
    def period_id(self) -> str:
        return self.end.isoformat()

    def dates(self) -> list[date]:
        return [self.start + timedelta(days=i) for i in range(self.days)]

    def to_dict(self) -> dict:
        return {
            "period_id": self.period_id,
            "start": self.start.isoformat(),
            "end": self.end.isoformat(),
            "days": self.days,
            "history_start": self.history_start.isoformat(),
            "history_days": self.history_days,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "Period":
        return cls(end=date.fromisoformat(d["end"]), days=int(d["days"]), history_days=int(d["history_days"]))


def period_for(end: date | str, playbook: dict | None = None) -> Period:
    pb = playbook or config.load_playbook()
    if isinstance(end, str):
        end = date.fromisoformat(end)
    return Period(end=end, days=int(pb["period_days"]), history_days=int(pb["history_days"]))


def feed_path(name: str) -> Path:
    return config.FEEDS_DIR / config.FEED_FILES[name]


def _source_ref(path: Path, rows: int) -> dict:
    digest = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 16), b""):
            digest.update(chunk)
    st = path.stat()
    return {
        "path": str(path),
        "bytes": st.st_size,
        "modified": datetime.fromtimestamp(st.st_mtime).isoformat(timespec="seconds"),
        "sha256": digest.hexdigest()[:16],
        "rows": rows,
    }


def _retry_opts(playbook: dict) -> dict:
    r = playbook.get("retries", {})
    return {"attempts": int(r.get("max_attempts", 3)), "delay": float(r.get("delay_seconds", 2))}


def _read_csv(path: Path, playbook: dict) -> list[dict]:
    def read():
        with open(path, "r", encoding="utf-8", newline="") as fh:
            return list(csv.DictReader(fh))

    return with_retries(read, **_retry_opts(playbook))


def _read_geojson(path: Path, playbook: dict) -> dict:
    def read():
        with open(path, "r", encoding="utf-8") as fh:
            return json.load(fh)

    return with_retries(read, **_retry_opts(playbook))


def _require(path: Path, step: int, what: str) -> None:
    if not path.exists():
        raise RunFailed(step, f"{what} feed is missing: {path.name} not found in {path.parent}")


def feed_status() -> dict:
    """Quick readiness snapshot for the setup screen and the Airflow readiness sensor."""
    out = {}
    for name, fname in config.FEED_FILES.items():
        p = config.FEEDS_DIR / fname
        if p.exists():
            st = p.stat()
            out[name] = {
                "file": fname,
                "present": True,
                "bytes": st.st_size,
                "modified": datetime.fromtimestamp(st.st_mtime).isoformat(timespec="seconds"),
            }
        else:
            out[name] = {"file": fname, "present": False}
    return out


def feeds_ready() -> bool:
    return all(v["present"] for v in feed_status().values())


# ---- Step 2 -------------------------------------------------------------------------

def load_readings(period: Period, playbook: dict) -> dict:
    """Step 2: readings for the history window through the period end, with timestamps, units, ids."""
    path = feed_path("readings")
    _require(path, 2, "Transformer readings")
    raw = _read_csv(path, playbook)
    rows, bad = [], []
    lo, hi = period.history_start, period.end
    for i, r in enumerate(raw):
        try:
            ts = datetime.fromisoformat(r["timestamp"].strip())
            d = ts.date()
            if d < lo or d > hi:
                continue
            load = float(r["load"])
            if not math.isfinite(load):
                raise ValueError(f"load is not a finite number: {r['load']!r}")
            rows.append(
                {
                    "transformer_id": r["transformer_id"].strip(),
                    "timestamp": ts.isoformat(),
                    "date": d.isoformat(),
                    "load": load,
                    "unit": (r.get("unit") or "").strip(),
                }
            )
        except (KeyError, ValueError) as exc:
            bad.append(f"readings row {i + 2}: {exc!r}")
    latest = max((r["timestamp"] for r in rows), default=None)
    return {
        "rows": rows,
        "problems": bad,
        "source": _source_ref(path, len(raw)),
        "meta": {"rows_in_window": len(rows), "latest_timestamp": latest, "window": [lo.isoformat(), hi.isoformat()]},
    }


# ---- Step 3 -------------------------------------------------------------------------

def load_assets(period: Period, playbook: dict) -> dict:
    """Step 3: transformer identifiers, locations and rated maximum loads effective for the period."""
    path = feed_path("assets")
    _require(path, 3, "Transformer asset records")
    raw = _read_csv(path, playbook)
    rows, bad = [], []
    for i, r in enumerate(raw):
        try:
            eff_from = date.fromisoformat(r["effective_from"]) if r.get("effective_from") else None
            eff_to = date.fromisoformat(r["effective_to"]) if r.get("effective_to") else None
            rating = r.get("rated_max", "").strip()
            rows.append(
                {
                    "transformer_id": r["transformer_id"].strip(),
                    "name": (r.get("name") or "").strip(),
                    "lat": float(r["lat"]) if r.get("lat") else None,
                    "lon": float(r["lon"]) if r.get("lon") else None,
                    "rated_max": (float(rating) if rating and math.isfinite(float(rating)) else None),
                    "unit": (r.get("unit") or "").strip(),
                    "customers": int(float(r["customers"])) if r.get("customers") else None,
                    "area_id": (r.get("area_id") or "").strip(),
                    "effective_from": eff_from.isoformat() if eff_from else None,
                    "effective_to": eff_to.isoformat() if eff_to else None,
                    "notes": (r.get("notes") or "").strip(),
                    "in_effect": (eff_from is None or eff_from <= period.end) and (eff_to is None or eff_to >= period.end),
                }
            )
        except (KeyError, ValueError) as exc:
            bad.append(f"assets row {i + 2}: {exc!r}")
    bad.extend(scan_rows(rows, ["name", "notes"], "assets"))
    return {"rows": rows, "problems": bad, "source": _source_ref(path, len(raw)), "meta": {"in_effect": sum(r["in_effect"] for r in rows)}}


# ---- Step 4 -------------------------------------------------------------------------

def load_boundaries(period: Period, playbook: dict) -> dict:
    """Step 4: approved town/village/neighborhood boundary polygons (GeoJSON, lon/lat)."""
    path = feed_path("boundaries")
    _require(path, 4, "Boundary")
    gj = _read_geojson(path, playbook)
    feats, bad = [], []
    meta = gj.get("metadata", {})
    for i, f in enumerate(gj.get("features", [])):
        props = f.get("properties", {})
        geom = f.get("geometry", {})
        if geom.get("type") not in ("Polygon", "MultiPolygon"):
            bad.append(f"boundaries feature {i}: unsupported geometry {geom.get('type')}")
            continue
        polys = [geom["coordinates"]] if geom["type"] == "Polygon" else geom["coordinates"]
        feats.append(
            {
                "area_id": str(props.get("area_id", "")).strip(),
                "name": str(props.get("name", "")).strip(),
                "kind": str(props.get("kind", "")).strip(),
                "polygons": polys,  # list of polygons, each a list of rings, each ring a list of [lon, lat]
            }
        )
    bad.extend(scan_rows(feats, ["name"], "boundaries"))
    return {
        "rows": feats,
        "problems": bad,
        "source": _source_ref(path, len(feats)),
        "meta": {
            "approved_version": meta.get("approved_version"),
            "valid_from": meta.get("valid_from"),
            "valid_to": meta.get("valid_to"),
            "source_name": meta.get("source"),
        },
    }


# ---- Step 5 -------------------------------------------------------------------------

def load_forecasts(period: Period, playbook: dict) -> dict:
    """Step 5: heat-pump adoption forecast by area with its version, base period and horizon."""
    path = feed_path("forecast")
    _require(path, 5, "Heat-pump forecast")
    raw = _read_csv(path, playbook)
    rows, bad = [], []
    for i, r in enumerate(raw):
        try:
            rows.append(
                {
                    "forecast_version": r["forecast_version"].strip(),
                    "area_id": r["area_id"].strip(),
                    "horizon_label": (r.get("horizon_label") or "").strip(),
                    "households": int(float(r["households"])),
                    "hp_share_base": float(r["hp_share_base"]),
                    "hp_share_forecast": float(r["hp_share_forecast"]),
                    "kw_per_heat_pump": float(r["kw_per_heat_pump"]),
                    "valid_from": (r.get("valid_from") or "").strip() or None,
                    "valid_to": (r.get("valid_to") or "").strip() or None,
                    "notes": (r.get("notes") or "").strip(),
                }
            )
        except (KeyError, ValueError) as exc:
            bad.append(f"forecast row {i + 2}: {exc!r}")
    bad.extend(scan_rows(rows, ["notes", "horizon_label"], "forecast"))
    versions = sorted({r["forecast_version"] for r in rows})
    return {"rows": rows, "problems": bad, "source": _source_ref(path, len(raw)), "meta": {"versions": versions}}
