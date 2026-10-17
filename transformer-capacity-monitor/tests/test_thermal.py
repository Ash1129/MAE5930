"""Modeled oil and hot-spot temperatures (IEEE C57.91 exponential model) for the 3D view."""

import pytest


def test_steady_state_at_rated_load_and_monotonic_in_load():
    from capacity_monitor.thermal import DEFAULTS, aging_factor, simulate

    rated = [{"timestamp": f"2026-10-10T{h:02d}:00:00-04:00", "load": 100.0} for h in range(24)]
    out = simulate(rated, 100.0, {})
    last = out["series"][-1]
    assert last["k"] == 1.0
    assert last["top_oil_c"] == pytest.approx(DEFAULTS["ambient_c"] + DEFAULTS["top_oil_rise_rated_c"], abs=0.1)
    assert last["hot_spot_c"] == pytest.approx(DEFAULTS["ambient_c"] + 55 + 25, abs=0.1)
    assert out["hours_at_or_over_limit"] == 0 and out["modeled"] is True
    half = simulate([{**r, "load": 50.0} for r in rated], 100.0, {})["series"][-1]
    assert half["hot_spot_c"] < last["hot_spot_c"] and half["top_oil_c"] < last["top_oil_c"]
    assert aging_factor(110.0) == pytest.approx(1.0) and aging_factor(120.0) > 1.0


def test_oil_lags_a_step_in_load():
    from capacity_monitor.thermal import simulate

    rows = [{"timestamp": f"2026-10-10T{h:02d}:00:00-04:00", "load": 40.0 if h < 12 else 100.0} for h in range(24)]
    s = simulate(rows, 100.0, {})["series"]
    # the winding responds at once; the oil climbs over the next hours
    assert s[12]["hot_spot_c"] > s[11]["hot_spot_c"] + 10
    assert s[12]["top_oil_c"] < s[23]["top_oil_c"]
    assert s[23]["top_oil_c"] == pytest.approx(75.0, abs=1.0)


def test_thermal_api_returns_the_week(sandbox):
    from webapp import app as webapp

    webapp.app.config["TESTING"] = True
    client = webapp.app.test_client()
    from capacity_monitor.run import execute_run

    execute_run("2026-10-15", "test", webapp.store)
    j = client.get("/api/periods/2026-10-15/transformers/T-ENF-011/thermal").get_json()
    assert len(j["series"]) == 168 and j["kind"] == "pole" and j["peak"]["hot_spot_c"] > j["series"][0]["top_oil_c"]
    assert j["modeled"] is True and "hot_spot_limit_c" in j["params"]
    assert client.get("/api/periods/2026-10-15/transformers/NOPE/thermal").status_code == 404
