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
    # January is scaled above May by the ratio of the playbook factors (outside the winter evening boost hours)
    ratio = jan["loads"]["T-ITH-002"][3] / may["loads"]["T-ITH-002"][3]
    assert abs(ratio - jan["factor"] / may["factor"]) < 1e-9
    # winter evening boost applies 17:00-21:00 only
    boost = pb["seasonal_model"]["winter_evening_boost"]
    assert abs(jan["loads"]["T-ITH-002"][19] / may["loads"]["T-ITH-002"][19] - (jan["factor"] / may["factor"]) * (1 + boost)) < 1e-9
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
