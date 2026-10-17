"""Known-answer checks for descriptive summaries, independent of the web layer."""
import json
import pytest
from capacity_monitor.aggregate import box_stats, county_trend_statistics

DATES = ["2026-10-01", "2026-10-09"]


def result(tid, values, signals=(), rating=100, calibration=False):
    return {"transformer_id": tid, "rated_max": rating, "is_calibration": calibration,
            "chart": {"dates": DATES, "values": values,
                      "signals": [{"date": d, "rule": "test"} for d in signals]}}


def test_known_percentages_unique_signal_counts_and_quartiles():
    rows = [result("A", [40, 90], [DATES[1]] * 3), result("B", [60, 100], [DATES[1]]),
            result("C", [80, 50]), result("D", [100, None])]
    before = json.dumps(rows)
    points = county_trend_statistics(rows)["points"]
    assert points[0] == {"date": DATES[0], "n": 4, "near_rating_count": 1,
                         "near_rating_pct": 25, "signal_transformers": 0,
                         "median_pct": pytest.approx(70), "q1_pct": pytest.approx(55), "q3_pct": pytest.approx(85)}
    assert points[1]["n"] == 3
    assert points[1]["near_rating_pct"] == pytest.approx(200 / 3)
    assert points[1]["signal_transformers"] == 2  # not four rule events
    assert points[1]["median_pct"] == 90
    assert points[1]["q1_pct"] == 70 and points[1]["q3_pct"] == 95
    assert before == json.dumps(rows)
    assert not {"ucl", "lcl", "out", "baseline"}.intersection(points[0])


def test_invalid_calibration_and_missing_observations_are_excluded():
    good = result("A", [90, 50])
    ignored = [result("B", [100, 100], calibration=True), result("C", [50, 50], rating=0),
               result("D", [50, 50], rating="bad"), result("E", [50, 50], rating=float("inf")),
               result("F", [float("nan"), float("inf")]), result("G", [None, None])]
    assert county_trend_statistics([good] + ignored) == county_trend_statistics([good])
    assert county_trend_statistics(ignored) == {"status": "insufficient_data", "points": []}


def test_single_constant_and_missing_dates_need_no_baseline():
    out = county_trend_statistics([result("A", [None, 50], [DATES[1]])])
    assert len(out["points"]) == 1
    p = out["points"][0]
    assert p["date"] == DATES[1] and p["n"] == p["signal_transformers"] == 1
    assert p["median_pct"] == p["q1_pct"] == p["q3_pct"] == 50
    assert p["near_rating_pct"] == 0
    assert county_trend_statistics([])["points"] == []


def test_duplicate_transformer_not_counted_twice():
    row = result("A", [90, 90], [DATES[1]])
    assert county_trend_statistics([row, row]) == county_trend_statistics([row])


def test_box_statistics_known_answer_empty_and_single():
    assert box_stats([]) is None and box_stats([None]) is None
    assert box_stats([7]) == {"n": 1, "min": 7, "q1": 7, "median": 7, "q3": 7, "max": 7}
    assert box_stats([4, 1, None, 3, 2]) == {
        "n": 4, "min": 1, "q1": 1.75, "median": 2.5, "q3": 3.25, "max": 4}
