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
    # the synthetic set carries nameplate values for the labeled cases and an hourly ambient feed
    assert j["sources"]["parameters"] == "nameplate (asset record)" and j["sources"]["ambient"].startswith("recorded ambient feed (every hour)")
    assert len({s["ambient_c"] for s in j["series"]}) > 1
    assert client.get("/api/periods/2026-10-15/transformers/NOPE/thermal").status_code == 404


def test_parameter_layering_and_ambient_lookup(tmp_path):
    from capacity_monitor.thermal import ambient_at, load_ambient, params, simulate

    pb = {"thermal_model": {"ambient_c": 15.0, "types": {"pole": {"loss_ratio_R": 4.5, "oil_time_constant_h": 1.8}}}}
    p, src = params(pb, "pole", None)
    assert p["loss_ratio_R"] == 4.5 and p["ambient_c"] == 15.0 and src.startswith("typical pole")
    p, src = params(pb, "pole", {"loss_ratio": "3.9", "top_oil_rise_c": "", "hot_spot_rise_c": "x", "oil_time_constant_h": "2.2"})
    assert p["loss_ratio_R"] == 3.9 and p["oil_time_constant_h"] == 2.2 and "nameplate for 2 of 4" in src
    f = tmp_path / "ambient.csv"
    f.write_text("timestamp,temp_c\n2026-10-10T05:00:00-04:00,4.0\n2026-10-10T15:00:00-04:00,14.0\nbad,row\n", encoding="utf-8")
    amb = load_ambient(f)
    assert ambient_at(amb, "2026-10-10T15:00:00-04:00", 20.0) == (14.0, True)
    assert ambient_at(amb, "2026-10-10T20:00:00-04:00", 20.0) == (9.0, True)  # that day's mean
    assert ambient_at(amb, "2026-10-11T20:00:00-04:00", 20.0) == (20.0, False)
    assert ambient_at(load_ambient(tmp_path / "none.csv"), "2026-10-10T15:00:00-04:00", 20.0) == (20.0, False)
    out = simulate([{"timestamp": "2026-10-10T15:00:00-04:00", "load": 50.0}, {"timestamp": "2026-10-11T15:00:00-04:00", "load": 50.0}], 100.0, pb, kind="pole", ambient=amb)
    assert out["series"][0]["ambient_c"] == 14.0 and out["series"][1]["ambient_c"] == 15.0 and "1 of 2 hours" in out["sources"]["ambient"]
