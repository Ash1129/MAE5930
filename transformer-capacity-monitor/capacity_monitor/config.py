"""Paths and playbook loading. All locations can be overridden with CAPMON_HOME."""

from __future__ import annotations

import json
import os
from pathlib import Path

ROOT = Path(os.environ.get("CAPMON_HOME", Path(__file__).resolve().parent.parent))
DATA_DIR = ROOT / "data"
FEEDS_DIR = DATA_DIR / "feeds"
REPORTS_DIR = DATA_DIR / "reports"
WORK_DIR = DATA_DIR / "work"
DB_PATH = Path(os.environ.get("CAPMON_DB", DATA_DIR / "capacity_monitor.sqlite3"))
RULES_DIR = ROOT / "rules"
PLAYBOOK_PATH = RULES_DIR / "playbook.json"
DECISION_TABLE_PATH = RULES_DIR / "decision-table.csv"

FEED_FILES = {
    "readings": "readings.csv",
    "assets": "assets.csv",
    "boundaries": "boundaries.geojson",
    "forecast": "heat_pump_forecast.csv",
}
# Optional feeds: read when present, never required by the run or the readiness sensor.
OPTIONAL_FEED_FILES = {
    "ambient": "ambient.csv",  # outside air temperature, hourly (timestamp,temp_c) or daily (date,temp_c); modeled 3D view only
}

# Step numbers and names exactly as in the architecture table.
STEPS = [
    (1, "Scheduled monitoring run"),
    (2, "Load transformer readings"),
    (3, "Load transformer asset records"),
    (4, "Load local boundaries"),
    (5, "Load heat-pump growth forecasts"),
    (6, "Align the run inputs"),
    (7, "Check input completeness"),
    (8, "Check load stability"),
    (9, "Is the load pattern stable?"),
    (10, "Project demand growth"),
    (11, "Measure capacity headroom"),
    (12, "Does a transformer need review?"),
    (13, "Review capacity exceptions"),
    (14, "Save the monitoring report"),
    (15, "Monitoring run complete"),
]

_DEFAULT_PLAYBOOK = {
    "version": "default-2026-10-16",
    "timezone": "America/New_York",
    "schedule": {"cron": "0 6 * * 1,3,5", "description": "Monday, Wednesday and Friday at 06:00"},
    "period_days": 7,
    "history_days": 60,
    "chart": {"min_history_points": 20, "E2": 2.66, "D4": 3.267, "d2": 1.128},
    "capability": {"confidence_level": 0.95, "min_points": 20, "cpk_review_below": 1.33, "cpk_ci_low_review_below": 1.33, "mr_effective_df_factor": 0.62, "normality_alpha": 0.05},
    "forecast": {"version": "TC-HP-2026-v1", "allocation_method": "declared_primary_area", "near_rating_ratio": 0.9, "power_factor": 0.95},
    "review": {"reviewer_name": "", "max_text_length": 2000},
    "retries": {"max_attempts": 3, "delay_seconds": 2},
}


def load_playbook() -> dict:
    """Read rules/playbook.json; missing keys fall back to documented defaults."""
    data = dict(_DEFAULT_PLAYBOOK)
    if PLAYBOOK_PATH.exists():
        with open(PLAYBOOK_PATH, "r", encoding="utf-8") as fh:
            loaded = json.load(fh)
        for key, value in loaded.items():
            if isinstance(value, dict) and isinstance(data.get(key), dict):
                merged = dict(data[key])
                merged.update(value)
                data[key] = merged
            else:
                data[key] = value
    if data["capability"]["confidence_level"] != 0.95:
        raise ValueError("Only 95% capability confidence intervals are supported (confidence_level must be 0.95)")
    return data


def ensure_dirs() -> None:
    for d in (DATA_DIR, FEEDS_DIR, REPORTS_DIR, WORK_DIR):
        d.mkdir(parents=True, exist_ok=True)
