"""Charts aggregate a period's results by area, stability and usage."""

from webapp.viz import box_stats, county_trend_charts, filter_summary, pie_svg, summarize_results


def _result(tid, area_id, area_name, stability, status, usage, forecast=None):
    return {
        "transformer_id": tid,
        "name": tid,
        "area_id": area_id,
        "area_name": area_name,
        "stability": stability,
        "status": status,
        "is_calibration": False,
        "rated_max": 100,
        "unit": "kVA",
        "customers": 40,
        "capacity": {"period_peak_ratio": usage, "period_peak": usage * 100 if usage is not None else None, "forecast_ratio": forecast},
    }


def test_box_and_area_rollup():
    results = [
        _result("T-A", "DRY", "Town of Dryden", "stable", "within_limits", 0.4, 0.5),
        _result("T-B", "DRY", "Town of Dryden", "signal", "review_needed", 0.9, 1.1),
        _result("T-C", "CAR", "Town of Caroline", "stable", "within_limits", 0.55, 0.6),
        _result("T-D", "CAR", "Town of Caroline", "signal", "inspect_now", 0.7, 0.8),
    ]
    model = summarize_results(results)
    assert box_stats([0.4, 0.9])["median"] == 0.65
    dry = next(a for a in model["areas"] if a["area_id"] == "DRY")
    assert dry["n"] == 2 and dry["review_needed"] == 1 and dry["inspect_now"] == 0 and dry["flagged"] == 1 and dry["unstable"] == 1
    car = next(a for a in model["areas"] if a["area_id"] == "CAR")
    assert car["inspect_now"] == 1 and car["flagged"] == 1
    assert dry["usage"]["median"] == 0.65
    assert model["areas"][0]["area_id"] == "DRY"  # highest median usage first
    assert [s["key"] for s in model["status_slices"]] == ["within_limits", "review_needed", "inspect_now"]
    assert model["status_slices"][1]["count"] == 1 and model["status_slices"][2]["count"] == 1

    view = filter_summary(model, "review_needed", None)
    assert [t["id"] for t in view["transformers"]] == ["T-B"]
    assert model["status_slices"][0]["count"] == 2  # pies stay on the full set

    pie = pie_svg([{"key": "review_needed", "label": "Review needed", "count": 1, "color": "#d7263d", "href": "/dashboard?status=review_needed"}], "review_needed")
    assert "circle" in pie and "review_needed" in pie


def test_descriptive_trends_have_ribbon_and_no_alarm_limits():
    def one(tid, peaks, signals=()):
        return {
            "transformer_id": tid,
            "rated_max": 100,
            "is_calibration": False,
            "chart": {
                "dates": ["2026-09-01", "2026-09-02", "2026-10-08"],
                "values": peaks,
                "signals": [{"date": d, "rule": "beyond_3_sigma"} for d in signals],
            },
        }

    charts = county_trend_charts(
        [one("T1", [40, 60, 95], ["2026-10-08"]), one("T2", [50, 50, 96])],
        "2026-10-08",
    )
    assert "2026-10-08" in charts["near_svg"]
    assert "polygon" in charts["loading_svg"]
    assert "middle 50%" in charts["loading_svg"]
    assert "Transformers with signals" in charts["signals_svg"]
    for svg in charts.values():
        assert "stroke-dasharray" not in svg and "#D7263D" not in svg


def test_empty_and_single_day_trends_render():
    assert "No eligible" in county_trend_charts([], "2026-10-09")["near_svg"]
    rows = [{"transformer_id": "A", "rated_max": 100,
             "chart": {"dates": ["2026-10-09"], "values": [40]}}]
    assert "<svg" in county_trend_charts(rows, "2026-10-09")["loading_svg"]
