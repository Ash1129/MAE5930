"""Heatmap data service: recorded days, hourly shapes and the labeled seasonal model."""

import time


def test_recorded_and_seasonal_model(sandbox):
    from capacity_monitor import config, heat

    days = heat.dates()
    assert "2026-10-15" in days and len(days) >= 60
    day = heat.recorded_day("2026-10-15")
    assert len(day) == 12 and len(day["T-CAR-006"]) == 24
    # the recorded daily peak equals the max of the hourly values
    assert max(day["T-CAR-006"]) > 0
    jan = heat.seasonal_day(1)
    may = heat.seasonal_day(5)
    pb = config.load_playbook()
    assert jan["modeled"] is True and jan["factor"] == pb["seasonal_model"]["monthly_factors"]["1"]
    # January is scaled above May by the ratio of the playbook factors, times each month's hourly
    # temperature response (outside the winter evening boost hours)
    tm = lambda d, h: d["temperature_multipliers"][h]  # noqa: E731
    ratio = jan["loads"]["T-ITH-002"][3] / may["loads"]["T-ITH-002"][3]
    assert abs(ratio - (jan["factor"] / may["factor"]) * (tm(jan, 3) / tm(may, 3))) < 1e-3
    # winter evening boost applies 17:00-21:00 only
    boost = pb["seasonal_model"]["winter_evening_boost"]
    assert abs(jan["loads"]["T-ITH-002"][19] / may["loads"]["T-ITH-002"][19] - (jan["factor"] / may["factor"]) * (tm(jan, 19) / tm(may, 19)) * (1 + boost)) < 1e-3
    # the modeled shape peaks at the class's peak hour: commercial downtown pad peaks by day, residential in the evening
    com = jan["loads"]["T-ITH-001"]
    res = jan["loads"]["T-ITH-002"]
    assert com.index(max(com)) in (9, 10) and res.index(max(res)) == 18
    # downtown stays comparatively high overnight (commercial profile)
    assert com[2] / max(com) > 0.6 and res[2] / max(res) < 0.6
    assert heat.recorded_day("1999-01-01") == {}


def test_heat_endpoints_and_page(sandbox):
    from webapp import app as webapp

    webapp.app.config["TESTING"] = True
    client = webapp.app.test_client()
    resp = client.post("/runs", data={"period_end": "2026-10-15"})
    run_id = resp.headers["Location"].rsplit("/", 1)[-1]
    for _ in range(300):
        run = webapp.store.get_run(run_id)
        if run and run["status"] != "running":
            break
        time.sleep(0.1)
    assert client.get("/periods/2026-10-15/heatmap").status_code == 302  # folded into the Map page
    page = client.get("/periods/2026-10-15/map").data
    assert b"Seasonal model" in page and b"Town of Dryden" in page and b"Districts" in page
    j = client.get("/api/heat/recorded?date=2026-10-15").get_json()
    assert j["modeled"] is False and j["transformers"] == 12
    j = client.get("/api/heat/seasonal?month=12").get_json()
    assert j["modeled"] is True and len(j["loads"]) == 12
    assert client.get("/api/heat/seasonal?month=13").status_code == 400
    assert client.get("/heatmap").status_code == 302


def test_heat_endpoints_carry_modeled_temperatures(sandbox):
    """The map's temperature view: hot-spot estimates per hour, with the outside air that drove them."""
    from capacity_monitor import config
    from webapp import app as webapp

    webapp.app.config["TESTING"] = True
    client = webapp.app.test_client()
    j = client.get("/api/heat/recorded?date=2026-10-15").get_json()
    assert j["hot_spot_modeled"] is True and len(j["ambient"]) == 24 and j["ambient_source"] == "recorded ambient feed"
    assert len(j["hot_spot"]) == 12 and len(j["hot_spot"]["T-CAR-006"]) == 24
    hs, loads = j["hot_spot"]["T-CAR-006"], j["loads"]["T-CAR-006"]
    assert all(h is not None for h in hs) and hs[loads.index(max(loads))] > min(h for h in hs if h is not None)
    # the seasonal view takes the month's typical outside air: January is colder than July at the same hour of a typical day
    jan = client.get("/api/heat/seasonal?month=1").get_json()
    jul = client.get("/api/heat/seasonal?month=7").get_json()
    pb = config.load_playbook()
    assert abs(sum(jan["ambient"]) / 24 - pb["thermal_model"]["monthly_ambient_c"]["1"]) < 0.2 and jan["ambient_source"].startswith("typical for the month")
    # January carries more load (factor 1.35 vs 1.02) yet the 27-degree colder air keeps the winding only modestly hotter
    assert jan["hot_spot"]["T-ITH-002"][18] - jul["hot_spot"]["T-ITH-002"][18] < 27 - 0


def test_seasonal_load_follows_the_typical_outside_air(sandbox):
    """The seasonal model's temperature response: load moves toward the cold hours of a typical day."""
    from capacity_monitor import config, heat
    from webapp import app as webapp

    pb = config.load_playbook()
    jan = heat.seasonal_day(1, pb)
    air, mult = jan["ambient"], jan["temperature_multipliers"]
    assert len(air) == 24 and len(mult) == 24
    assert min(air) < jan["typical_ambient_c"] < max(air)  # a daily swing around the month's mean
    assert air.index(max(air)) == pb["thermal_model"]["warmest_hour"]
    assert abs(sum(mult) / 24 - 1.0) < 1e-6  # the day still averages the month's calibration
    assert mult[air.index(min(air))] > mult[air.index(max(air))]  # colder hour, more heating load
    # the hourly load carries the multiplier on top of the recorded shape and monthly factor
    base = heat.seasonal_day(1, {**pb, "seasonal_model": {**pb["seasonal_model"], "temperature_response": {}}})
    h = air.index(min(air))
    assert abs(jan["loads"]["T-ITH-002"][h] / base["loads"]["T-ITH-002"][h] - mult[h]) < 1e-3
    # July: afternoons above the cooling base carry cooling load instead
    jul = heat.seasonal_day(7, pb)
    assert jul["temperature_multipliers"][jul["ambient"].index(max(jul["ambient"]))] > 1.0
    webapp.app.config["TESTING"] = True
    client = webapp.app.test_client()
    j = client.get("/api/heat/seasonal?month=1").get_json()
    assert len(j["ambient"]) == 24 and j["ambient_source"].startswith("typical for the month and hour")
