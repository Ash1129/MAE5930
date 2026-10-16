"""Read-only status and pause/resume/trigger for the Airflow scheduler through its public REST API.

Settings (environment variables):
  CAPMON_AIRFLOW_URL   default http://localhost:8080
  AIRFLOW_HOME         used to find the standalone-generated admin password file
  CAPMON_AIRFLOW_USER / CAPMON_AIRFLOW_PASSWORD  override credentials (never stored in code)
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from pathlib import Path

from . import config

DAG_ID = "log_transformer_loads_and_monitor_capacity_again"
BASE = os.environ.get("CAPMON_AIRFLOW_URL", "http://localhost:8080").rstrip("/")
TIMEOUT = 6


def _credentials() -> tuple[str, str] | None:
    user, pw = os.environ.get("CAPMON_AIRFLOW_USER"), os.environ.get("CAPMON_AIRFLOW_PASSWORD")
    if user and pw:
        return user, pw
    home = Path(os.environ.get("AIRFLOW_HOME", config.ROOT / "airflow_home"))
    f = home / "simple_auth_manager_passwords.json.generated"
    if f.exists():
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
            if data:
                user = "admin" if "admin" in data else next(iter(data))
                return user, data[user]
        except (OSError, ValueError):
            return None
    return None


def _request(method: str, path: str, body: dict | None = None, token: str | None = None):
    req = urllib.request.Request(f"{BASE}{path}", method=method)
    req.add_header("Accept", "application/json")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    data = None
    if body is not None:
        data = json.dumps(body).encode()
        req.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(req, data=data, timeout=TIMEOUT) as resp:
        raw = resp.read()
        return json.loads(raw) if raw else {}


def _token() -> str | None:
    creds = _credentials()
    if not creds:
        return None
    out = _request("POST", "/auth/token", {"username": creds[0], "password": creds[1]})
    return out.get("access_token")


def status() -> dict:
    """Scheduler status for the dashboard. Never raises; `available` says whether Airflow answered."""
    out = {"available": False, "url": BASE, "dag_id": DAG_ID}
    try:
        token = _token()
        if not token:
            out["error"] = "No Airflow credentials found (start Airflow with scripts/start_airflow.sh first)"
            return out
        dag = _request("GET", f"/api/v2/dags/{DAG_ID}", token=token)
        runs = _request("GET", f"/api/v2/dags/{DAG_ID}/dagRuns?limit=8&order_by=-run_after", token=token)
        out.update(
            {
                "available": True,
                "is_paused": dag.get("is_paused"),
                "schedule": dag.get("timetable_description") or dag.get("timetable_summary"),
                "next_run": dag.get("next_dagrun_run_after"),
                "next_period_end": dag.get("next_dagrun_data_interval_end"),
                "has_import_errors": dag.get("has_import_errors"),
                "runs": [
                    {
                        "dag_run_id": r.get("dag_run_id"),
                        "state": r.get("state"),
                        "run_after": r.get("run_after"),
                        "start": r.get("start_date"),
                        "end": r.get("end_date"),
                        "type": r.get("run_type"),
                        "conf": r.get("conf"),
                    }
                    for r in runs.get("dag_runs", [])
                ],
            }
        )
        last = out["runs"][0] if out["runs"] else None
        out["last_run"] = last
        out["failed_runs"] = [r for r in out["runs"] if r["state"] == "failed"]
        out["ui_url"] = f"{BASE}/dags/{DAG_ID}"
    except urllib.error.HTTPError as exc:
        out["error"] = f"Airflow answered {exc.code} for {exc.url}"
        if exc.code == 404:
            out["error"] += " (DAG not registered yet; wait for the scheduler to parse airflow/dags)"
    except (urllib.error.URLError, OSError, ValueError) as exc:
        out["error"] = f"Airflow not reachable at {BASE}: {getattr(exc, 'reason', exc)}"
    return out


def set_paused(paused: bool) -> dict:
    token = _token()
    if not token:
        raise RuntimeError("No Airflow credentials available")
    return _request("PATCH", f"/api/v2/dags/{DAG_ID}", {"is_paused": paused}, token=token)


def trigger(period_end: str | None = None) -> dict:
    token = _token()
    if not token:
        raise RuntimeError("No Airflow credentials available")
    body = {"conf": {"period_end": period_end} if period_end else {}, "logical_date": None}
    return _request("POST", f"/api/v2/dags/{DAG_ID}/dagRuns", body, token=token)
