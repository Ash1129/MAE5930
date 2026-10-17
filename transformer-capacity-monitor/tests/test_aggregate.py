"""Numerical checks independent of Flask and SVG output."""
import json

import pytest

from capacity_monitor.aggregate import box_stats, county_control_statistics

DATES = ["2026-10-01", "2026-10-02", "2026-10-09"]
START = DATES[-1]


def result(values, signals=(), rating=100, calibration=False, dates=DATES):
    return {"rated_max": rating, "is_calibration": calibration, "chart": {
        "dates": dates, "values": values,
        "signals": [{"date": d, "rule": "test"} for d in signals],
    }}


def test_xs_and_u_known_answers_and_period_counts():
    # Each reference subgroup is [40,60]: mean 50%, sample s=sqrt(200).
    # n=2 constants: c4=sqrt(2/pi), A3=2.6586807764, B4=3.2665319193.
    # Reference u=1 event / 2 transformers. Period u=8/2=4 events per asset.
    rows = [result([40, 40, 0], DATES[:2] + [START] * 8), result([60, 60, 200])]
    before = json.dumps(rows)
    out = county_control_statistics(rows, START)
    assert out["status"] == "computed" and out["baseline_source"] == "pre_period"
    assert out["baseline_dates"] == DATES[:2]
    assert out["x"]["center"] == pytest.approx(50)
    assert out["s"]["center"] == pytest.approx(14.1421356237)
    x = out["x"]["points"][-1]
    assert x["value"] == pytest.approx(100)
    assert x["ucl"] == pytest.approx(87.5994241195)
    assert x["lcl"] == pytest.approx(12.4005758805)
    s = out["s"]["points"][-1]
    assert s["value"] == pytest.approx(141.4213562373)
    assert s["ucl"] == pytest.approx(46.1957374218)
    assert s["lcl"] == 0
    u = out["u"]["points"][-1]
    assert out["u"]["center"] == 50
    assert (u["value"], u["ucl"], u["lcl"]) == (400, 200, 0)
    assert all(out[k + "_out"] == 1 for k in ("p", "u", "x", "s"))
    assert json.dumps(rows) == before  # numerical API leaves caller inputs untouched
    assert "svg" not in json.dumps(out).lower()


def test_p_known_answer_and_variable_denominator():
    # 2 high observations / 8 reference observations = .25.
    # With n=4: .25 +/- 3*sqrt(.25*.75/4), truncated to [0,1].
    rows = [result([100, 100, 100])] + [result([40, 40, 100]) for _ in range(3)]
    out = county_control_statistics(rows, START)
    p = out["p"]["points"][-1]
    assert out["p"]["center"] == 25
    assert p["value"] == 100
    assert p["ucl"] == pytest.approx(89.9519052838)
    assert p["lcl"] == 0 and p["out"] is True
    # A missing period observation reduces n to 3, widening the upper limit to 100%.
    rows[-1]["chart"]["values"][-1] = None
    p = county_control_statistics(rows, START)["p"]["points"][-1]
    assert p["ucl"] == 100 and p["out"] is False


@pytest.mark.parametrize("rows", [[], [result([40], dates=[START])], [result([None, None, None])]])
def test_empty_one_date_or_missing_returns_explicit_insufficient_data(rows):
    out = county_control_statistics(rows, START)
    assert out["status"] == "insufficient_data"
    assert all(out[k]["points"] == [] for k in ("p", "u", "x", "s"))
    assert all(out[k + "_out"] == 0 for k in ("p", "u", "x", "s"))


def test_constant_and_single_member_subgroups():
    for rows in ([result([40, 40, 40])], [result([40, 40, 40])] * 2):
        out = county_control_statistics(rows, START)
        assert len(out["p"]["points"]) == 3
        assert all(p["ucl"] == p["lcl"] == p["value"] == 0 for p in out["p"]["points"])
        assert out["x"]["points"] == out["s"]["points"] == []


def test_missing_baseline_is_explicit_legacy_fallback():
    out = county_control_statistics([result([40, 50, 60])], "2026-09-01")
    assert out["baseline_source"] == "all_dates_fallback"
    assert out["baseline_dates"] == DATES


def test_ineligible_records_and_nonfinite_peaks_do_not_change_results():
    rows = [result([40, 50, 60]), result([60, 40, 70])]
    expected = county_control_statistics(rows, START)
    ignored = [result([1, 1, 1], calibration=True), result([1, 1, 1], rating=0),
               result([1, 1, 1], rating="bad"), result([float("nan"), float("inf"), None])]
    assert county_control_statistics(rows + ignored, START) == expected


def test_box_statistics_known_answer_empty_and_single():
    assert box_stats([]) is None
    assert box_stats([None]) is None
    assert box_stats([7]) == {"n": 1, "min": 7, "q1": 7, "median": 7, "q3": 7, "max": 7}
    assert box_stats([4, 1, None, 3, 2]) == {
        "n": 4, "min": 1, "q1": 1.75, "median": 2.5, "q3": 3.25, "max": 4,
    }
