"""Plain-language explanations are rule-based and cover the known failure patterns."""


def test_explain_known_problems(sandbox):
    from capacity_monitor.explain import explain_alert, explain_note, explain_problem

    e = explain_problem("Boundary feed is for a different reporting period (valid 2026-01-01 to 2025-12-31, run period ends 2026-10-13)")
    assert e["title"].startswith("The boundary map file") and "2026-10-13" in e["action"] and "boundaries.geojson" in e["action"]
    e = explain_problem("T-GRO-009: no rated maximum load on the asset record")
    assert "T-GRO-009" in e["meaning"] and "rated_max" in e["action"]
    e = explain_problem("Transformer readings feed is missing: readings.csv not found in /x/data/feeds")
    assert e["title"] == "An input file is missing" and "readings.csv" in e["action"]
    e = explain_problem("T-CAR-101: no readings for 7 of 7 period days (first missing 2026-10-09)")
    assert "7 of the 7 days" in e["meaning"]
    e = explain_problem("something new and unexpected")
    assert e["title"] == "The run hit a problem" and e["raw"] == "something new and unexpected"
    n = explain_note("T-CAY-003: location falls in 2 area(s) ['ITH-T', 'CAY-V']; using declared_primary_area = CAY-V")
    assert "Nothing to fix" in n and "T-CAY-003" in n
    assert explain_note("totally unknown warning") is None

    msg = ("Run 2026-10-13_airflow_manual failed at step 7: Input completeness check failed with 1 blocking problem(s)\n"
           "Boundary feed is for a different reporting period (valid 2026-01-01 to 2025-12-31, run period ends 2026-10-13)\n"
           "warning: T-CAY-003: location falls in 2 area(s) ['ITH-T', 'CAY-V']; using declared_primary_area = CAY-V")
    a = explain_alert(msg, None)
    assert a["step"] == 7 and a["step_name"] == "Check input completeness"
    assert a["title"].startswith("The boundary map file") and len(a["notes"]) == 1 and "Nothing to fix" in a["notes"][0]
    a = explain_alert("Airflow DAG run manual__x failed in task step_7_check_input_completeness", None)
    assert a["title"] == "A scheduled run stopped"


def test_alerts_page_shows_plain_language(sandbox):
    from webapp import app as webapp

    webapp.app.config["TESTING"] = True
    client = webapp.app.test_client()
    webapp.store.add_alert("error", "Run r1 failed at step 7: Input completeness check failed with 1 blocking problem(s)\nT-GRO-009: no rated maximum load on the asset record", run_id="r1", period_id="2026-10-15", step=7)
    page = client.get("/alerts").data.decode()
    assert "A transformer has no rated maximum" in page and "What to do" in page and "Technical details" in page
