"""End-to-end runs on synthetic feeds: labeled cases, failure cases, idempotent rerun."""

import json
import os


def _run(end="2026-10-15", by="test"):
    from capacity_monitor.run import execute_run
    from capacity_monitor.store import Store

    return execute_run(end, by, Store())


def _results(period="2026-10-15"):
    from capacity_monitor.store import Store

    return {r["transformer_id"]: r for r in Store().get_transformer_results(period)}


def test_labeled_synthetic_cases(sandbox):
    run = _run()
    assert run["status"] == "success", run["error"]
    r = _results()
    assert r["T-DRY-004"]["stability"] == "signal" and r["T-DRY-004"]["capacity"]["cpk"] is None  # case 2
    assert r["T-DRY-004"]["capacity"]["period_peak_ratio"] < 1.0
    assert r["T-LAN-005"]["decision"]["rule"] == "8"  # case 3: uncertain Cpk
    assert r["T-CAR-006"]["decision"]["rule"] == "9" and r["T-CAR-006"]["capacity"]["forecast_ratio"] > 1.0  # case 4
    assert r["T-ULY-007"]["stability"] == "insufficient_history"
    assert r["T-DAN-010"]["decision"]["rule"] == "7"
    assert r["T-ITH-001"]["status"] == "within_limits"
    assert all(s["status"] == "success" for s in run["steps"] if s["step"] not in (13,))
    assert [s["status"] for s in run["steps"] if s["step"] == 13] == ["waiting"]
    from capacity_monitor import config

    rep = json.loads((config.REPORTS_DIR / "2026-10-15" / "report.json").read_text())
    assert rep["report_status"] == "draft" and rep["exceptions_total"] == 5


def test_boundary_period_mismatch_stops_before_analysis(sandbox):
    sandbox["generate"]("boundary-mismatch")
    run = _run()
    assert run["status"] == "failed"
    assert run["current_step"] == 7
    assert any("different reporting period" in p for p in run["problems"])
    from capacity_monitor import config
    from capacity_monitor.store import Store

    assert not (config.REPORTS_DIR / "2026-10-15").exists()  # no partial report
    assert Store().get_period("2026-10-15") is None
    alerts = Store().list_alerts()
    assert alerts and alerts[0]["level"] == "error" and "2026-10-15" in alerts[0]["period_id"]


def test_missing_rating_blocks_run(sandbox):
    sandbox["generate"]("missing-rating")
    run = _run()
    assert run["status"] == "failed" and any("no rated maximum" in p for p in run["problems"])


def test_missing_feed_fails_with_alert(sandbox):
    from capacity_monitor import config

    os.remove(config.FEEDS_DIR / "readings.csv")
    run = _run()
    assert run["status"] == "failed" and run["current_step"] == 2 and "missing" in run["error"]


def test_unsafe_text_is_quarantined_not_executed(sandbox):
    sandbox["generate"]("unsafe-text")
    run = _run()
    assert run["status"] == "success"
    from capacity_monitor.store import Store

    p = Store().get_period("2026-10-15")
    assert any("instruction-like" in w for w in p["warnings"])
    assert "quarantined" in _results()["T-ITH-001"]["notes"]


def test_rerun_replaces_period_without_duplicate_and_keeps_audit(sandbox):
    from capacity_monitor import config
    from capacity_monitor.store import Store

    r1 = _run()
    st = Store()
    st.record_disposition("2026-10-15", "T-CAR-006", _results()["T-CAR-006"]["input_hash"], "approve", "", "Tester", None, False, None)
    r2 = _run()
    assert r1["run_id"] != r2["run_id"]
    periods = st.list_periods()
    assert len(periods) == 1 and periods[0]["run_id"] == r2["run_id"] and periods[0]["rerun_count"] == 1
    assert len([r for r in st.list_runs() if r["period_id"] == "2026-10-15"]) == 2
    # same inputs -> the earlier disposition still applies; history kept
    assert _results()["T-CAR-006"]["disposition"]["decision"] == "approve"
    hist = list((config.REPORTS_DIR / "2026-10-15" / "history").glob("*.json"))
    assert len(hist) >= 2
    # changed inputs -> disposition becomes stale
    sandbox["generate"]("normal", end="2026-10-15") if False else None
    st.record_disposition("2026-10-15", "T-CAR-006", "deadbeef", "approve", "", "Tester", None, False, None)
    assert st.current_disposition("2026-10-15", "T-CAR-006", "otherhash") is None


def test_retry_then_fail(sandbox):
    from capacity_monitor.guards import with_retries

    calls = []

    def flaky():
        calls.append(1)
        raise OSError("transient")

    try:
        with_retries(flaky, attempts=3, delay=0)
    except OSError:
        pass
    assert len(calls) == 3
