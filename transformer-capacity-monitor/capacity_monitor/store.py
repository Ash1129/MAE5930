"""SQLite store: runs, step progress, period results, dispositions, alerts, settings.

Writes are period-specific and safe to repeat: a rerun of the same period replaces that
period's results (UPSERT) while every run attempt stays in `runs` for audit.
"""

from __future__ import annotations

import json
import sqlite3
import threading
from datetime import datetime, timezone
from pathlib import Path

from . import config

_SCHEMA = """
CREATE TABLE IF NOT EXISTS runs (
  run_id TEXT PRIMARY KEY,
  period_id TEXT NOT NULL,
  triggered_by TEXT NOT NULL,
  started_at TEXT NOT NULL,
  finished_at TEXT,
  status TEXT NOT NULL,          -- running | success | failed
  current_step INTEGER,
  error TEXT,
  problems_json TEXT,
  summary_json TEXT
);
CREATE INDEX IF NOT EXISTS runs_period ON runs(period_id, started_at);
CREATE TABLE IF NOT EXISTS run_steps (
  run_id TEXT NOT NULL,
  step INTEGER NOT NULL,
  name TEXT NOT NULL,
  status TEXT NOT NULL,          -- pending | running | success | failed | skipped | waiting
  started_at TEXT,
  finished_at TEXT,
  detail TEXT,
  PRIMARY KEY (run_id, step)
);
CREATE TABLE IF NOT EXISTS period_results (
  period_id TEXT PRIMARY KEY,
  run_id TEXT NOT NULL,
  generated_at TEXT NOT NULL,
  status TEXT NOT NULL,          -- draft | final
  summary_json TEXT NOT NULL,
  period_json TEXT NOT NULL,
  sources_json TEXT NOT NULL,
  warnings_json TEXT NOT NULL,
  finalized_by TEXT,
  finalized_at TEXT,
  rerun_count INTEGER NOT NULL DEFAULT 0
);
CREATE TABLE IF NOT EXISTS transformer_results (
  period_id TEXT NOT NULL,
  transformer_id TEXT NOT NULL,
  run_id TEXT NOT NULL,
  input_hash TEXT NOT NULL,
  status TEXT NOT NULL,          -- within_limits | review_needed
  stability TEXT NOT NULL,
  result_json TEXT NOT NULL,
  is_calibration INTEGER NOT NULL DEFAULT 0,
  PRIMARY KEY (period_id, transformer_id)
);
CREATE TABLE IF NOT EXISTS dispositions (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  period_id TEXT NOT NULL,
  transformer_id TEXT NOT NULL,
  input_hash TEXT NOT NULL,
  decision TEXT NOT NULL,        -- approve | request_changes | reject
  notes TEXT,
  reviewer TEXT NOT NULL,
  review_started_at TEXT,
  recorded_at TEXT NOT NULL,
  seconds_spent REAL,
  is_calibration INTEGER NOT NULL DEFAULT 0,
  calibration_caught INTEGER
);
CREATE INDEX IF NOT EXISTS disp_period ON dispositions(period_id, transformer_id, recorded_at);
CREATE TABLE IF NOT EXISTS alerts (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  created_at TEXT NOT NULL,
  run_id TEXT,
  period_id TEXT,
  step INTEGER,
  level TEXT NOT NULL,           -- error | warning | info
  message TEXT NOT NULL,
  delivered TEXT,                -- how it was delivered (log, email) or why not
  acknowledged_at TEXT,
  acknowledged_by TEXT
);
CREATE TABLE IF NOT EXISTS settings (
  key TEXT PRIMARY KEY,
  value TEXT
);
"""


def now_iso() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


class Store:
    def __init__(self, path: Path | str | None = None):
        self.path = Path(path or config.DB_PATH)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()
        with self._conn() as c:
            c.executescript(_SCHEMA)

    def _conn(self) -> sqlite3.Connection:
        c = sqlite3.connect(self.path, timeout=30, isolation_level=None)
        c.row_factory = sqlite3.Row
        c.execute("PRAGMA journal_mode=WAL")
        c.execute("PRAGMA busy_timeout=30000")
        return c

    # ---- runs -------------------------------------------------------------------------
    def create_run(self, run_id: str, period_id: str, triggered_by: str) -> None:
        with self._conn() as c:
            c.execute(
                "INSERT INTO runs(run_id, period_id, triggered_by, started_at, status, current_step) VALUES (?,?,?,?,?,?)",
                (run_id, period_id, triggered_by, now_iso(), "running", 1),
            )
            for step, name in config.STEPS:
                c.execute("INSERT OR IGNORE INTO run_steps(run_id, step, name, status) VALUES (?,?,?,?)", (run_id, step, name, "pending"))

    def step_start(self, run_id: str, step: int) -> None:
        with self._conn() as c:
            c.execute("UPDATE run_steps SET status='running', started_at=? WHERE run_id=? AND step=?", (now_iso(), run_id, step))
            c.execute("UPDATE runs SET current_step=? WHERE run_id=?", (step, run_id))

    def step_done(self, run_id: str, step: int, status: str = "success", detail: str | dict | None = None) -> None:
        if isinstance(detail, dict):
            detail = json.dumps(detail, default=str)
        with self._conn() as c:
            c.execute("UPDATE run_steps SET status=?, finished_at=?, detail=? WHERE run_id=? AND step=?", (status, now_iso(), detail, run_id, step))

    def finish_run(self, run_id: str, status: str, error: str | None = None, problems: list | None = None, summary: dict | None = None) -> None:
        with self._conn() as c:
            c.execute(
                "UPDATE runs SET status=?, finished_at=?, error=?, problems_json=?, summary_json=? WHERE run_id=?",
                (status, now_iso(), error, json.dumps(problems or []), json.dumps(summary or {}, default=str), run_id),
            )
            if status == "failed":
                c.execute("UPDATE run_steps SET status='skipped' WHERE run_id=? AND status='pending'", (run_id,))

    def get_run(self, run_id: str) -> dict | None:
        with self._conn() as c:
            r = c.execute("SELECT * FROM runs WHERE run_id=?", (run_id,)).fetchone()
            if not r:
                return None
            steps = c.execute("SELECT * FROM run_steps WHERE run_id=? ORDER BY step", (run_id,)).fetchall()
        d = dict(r)
        d["problems"] = json.loads(d.pop("problems_json") or "[]")
        d["summary"] = json.loads(d.pop("summary_json") or "{}")
        d["steps"] = [dict(s) for s in steps]
        return d

    def list_runs(self, limit: int = 50) -> list[dict]:
        with self._conn() as c:
            rows = c.execute("SELECT * FROM runs ORDER BY started_at DESC LIMIT ?", (limit,)).fetchall()
        out = []
        for r in rows:
            d = dict(r)
            d["summary"] = json.loads(d.pop("summary_json") or "{}")
            d["problems"] = json.loads(d.pop("problems_json") or "[]")
            out.append(d)
        return out

    def last_run(self) -> dict | None:
        runs = self.list_runs(limit=1)
        return runs[0] if runs else None

    # ---- period results ---------------------------------------------------------------
    def save_period_results(self, period: dict, run_id: str, summary: dict, sources: dict, warnings: list, results: dict, calibration_ids: set) -> None:
        """Replace the period's results. Dispositions whose input_hash still matches stay valid."""
        period_id = period["period_id"]
        with self._lock, self._conn() as c:
            c.execute("BEGIN IMMEDIATE")
            try:
                prev = c.execute("SELECT rerun_count FROM period_results WHERE period_id=?", (period_id,)).fetchone()
                rerun_count = (prev["rerun_count"] + 1) if prev else 0
                c.execute(
                    """INSERT INTO period_results(period_id, run_id, generated_at, status, summary_json, period_json, sources_json, warnings_json, rerun_count)
                       VALUES (?,?,?,?,?,?,?,?,?)
                       ON CONFLICT(period_id) DO UPDATE SET run_id=excluded.run_id, generated_at=excluded.generated_at, status='draft',
                         summary_json=excluded.summary_json, period_json=excluded.period_json, sources_json=excluded.sources_json,
                         warnings_json=excluded.warnings_json, finalized_by=NULL, finalized_at=NULL, rerun_count=excluded.rerun_count""",
                    (period_id, run_id, now_iso(), "draft", json.dumps(summary), json.dumps(period), json.dumps(sources), json.dumps(warnings), rerun_count),
                )
                c.execute("DELETE FROM transformer_results WHERE period_id=?", (period_id,))
                for tid, r in results.items():
                    c.execute(
                        "INSERT INTO transformer_results(period_id, transformer_id, run_id, input_hash, status, stability, result_json, is_calibration) VALUES (?,?,?,?,?,?,?,?)",
                        (period_id, tid, run_id, r["input_hash"], r["status"], r["stability"], json.dumps(r, default=str), 1 if tid in calibration_ids else 0),
                    )
                c.execute("COMMIT")
            except Exception:
                c.execute("ROLLBACK")
                raise

    def get_period(self, period_id: str) -> dict | None:
        with self._conn() as c:
            r = c.execute("SELECT * FROM period_results WHERE period_id=?", (period_id,)).fetchone()
        if not r:
            return None
        d = dict(r)
        for k in ("summary", "period", "sources", "warnings"):
            d[k] = json.loads(d.pop(f"{k}_json") or "null")
        return d

    def list_periods(self, limit: int = 50) -> list[dict]:
        with self._conn() as c:
            rows = c.execute("SELECT period_id FROM period_results ORDER BY period_id DESC LIMIT ?", (limit,)).fetchall()
        return [self.get_period(r["period_id"]) for r in rows]

    def get_transformer_results(self, period_id: str) -> list[dict]:
        with self._conn() as c:
            rows = c.execute("SELECT * FROM transformer_results WHERE period_id=? ORDER BY transformer_id", (period_id,)).fetchall()
        out = []
        for r in rows:
            d = json.loads(r["result_json"])
            d["is_calibration"] = bool(r["is_calibration"])
            d["disposition"] = self.current_disposition(period_id, r["transformer_id"], r["input_hash"])
            out.append(d)
        return out

    def get_transformer_result(self, period_id: str, transformer_id: str) -> dict | None:
        with self._conn() as c:
            r = c.execute("SELECT * FROM transformer_results WHERE period_id=? AND transformer_id=?", (period_id, transformer_id)).fetchone()
        if not r:
            return None
        d = json.loads(r["result_json"])
        d["is_calibration"] = bool(r["is_calibration"])
        d["disposition"] = self.current_disposition(period_id, transformer_id, r["input_hash"])
        d["disposition_history"] = self.disposition_history(period_id, transformer_id)
        return d

    # ---- dispositions -----------------------------------------------------------------
    def current_disposition(self, period_id: str, transformer_id: str, input_hash: str) -> dict | None:
        """The latest disposition recorded against the *current* inputs; stale ones do not count."""
        with self._conn() as c:
            r = c.execute(
                "SELECT * FROM dispositions WHERE period_id=? AND transformer_id=? AND input_hash=? ORDER BY recorded_at DESC, id DESC LIMIT 1",
                (period_id, transformer_id, input_hash),
            ).fetchone()
        return dict(r) if r else None

    def disposition_history(self, period_id: str, transformer_id: str) -> list[dict]:
        with self._conn() as c:
            rows = c.execute("SELECT * FROM dispositions WHERE period_id=? AND transformer_id=? ORDER BY recorded_at DESC, id DESC", (period_id, transformer_id)).fetchall()
        return [dict(r) for r in rows]

    def record_disposition(self, period_id, transformer_id, input_hash, decision, notes, reviewer, review_started_at, is_calibration, calibration_caught) -> int:
        started = None
        seconds = None
        if review_started_at:
            try:
                started = datetime.fromisoformat(review_started_at)
                seconds = (datetime.now(timezone.utc).astimezone() - started).total_seconds()
            except ValueError:
                started = None
        with self._conn() as c:
            cur = c.execute(
                """INSERT INTO dispositions(period_id, transformer_id, input_hash, decision, notes, reviewer, review_started_at, recorded_at, seconds_spent, is_calibration, calibration_caught)
                   VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
                (period_id, transformer_id, input_hash, decision, notes, reviewer, review_started_at if started else None, now_iso(), seconds, 1 if is_calibration else 0, calibration_caught),
            )
            return cur.lastrowid

    def finalize_period(self, period_id: str, reviewer: str) -> None:
        with self._conn() as c:
            c.execute("UPDATE period_results SET status='final', finalized_by=?, finalized_at=? WHERE period_id=?", (reviewer, now_iso(), period_id))

    def review_metrics(self) -> dict:
        with self._conn() as c:
            rows = c.execute("SELECT decision, seconds_spent, is_calibration, calibration_caught FROM dispositions").fetchall()
        total = len(rows)
        real = [r for r in rows if not r["is_calibration"]]
        overrides = sum(1 for r in real if r["decision"] != "approve")
        times = [r["seconds_spent"] for r in rows if r["seconds_spent"] is not None]
        cal = [r for r in rows if r["is_calibration"]]
        return {
            "dispositions": total,
            "real_dispositions": len(real),
            "override_rate": (overrides / len(real)) if real else None,
            "median_seconds": (sorted(times)[len(times) // 2] if times else None),
            "mean_seconds": (sum(times) / len(times)) if times else None,
            "fast_reviews_under_20s": sum(1 for t in times if t < 20),
            "calibration_cases": len(cal),
            "calibration_caught": sum(1 for r in cal if r["calibration_caught"]),
        }

    # ---- alerts / settings ------------------------------------------------------------
    def add_alert(self, level: str, message: str, run_id=None, period_id=None, step=None, delivered=None) -> int:
        with self._conn() as c:
            cur = c.execute(
                "INSERT INTO alerts(created_at, run_id, period_id, step, level, message, delivered) VALUES (?,?,?,?,?,?,?)",
                (now_iso(), run_id, period_id, step, level, message, delivered),
            )
            return cur.lastrowid

    def list_alerts(self, limit: int = 50, unacknowledged_only: bool = False) -> list[dict]:
        q = "SELECT * FROM alerts" + (" WHERE acknowledged_at IS NULL" if unacknowledged_only else "") + " ORDER BY id DESC LIMIT ?"
        with self._conn() as c:
            return [dict(r) for r in c.execute(q, (limit,)).fetchall()]

    def acknowledge_alert(self, alert_id: int, who: str) -> None:
        with self._conn() as c:
            c.execute("UPDATE alerts SET acknowledged_at=?, acknowledged_by=? WHERE id=?", (now_iso(), who, alert_id))

    def get_setting(self, key: str, default=None):
        with self._conn() as c:
            r = c.execute("SELECT value FROM settings WHERE key=?", (key,)).fetchone()
        return r["value"] if r else default

    def set_setting(self, key: str, value) -> None:
        with self._conn() as c:
            c.execute("INSERT INTO settings(key, value) VALUES (?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value", (key, value))
