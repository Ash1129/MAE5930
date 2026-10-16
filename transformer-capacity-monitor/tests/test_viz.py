"""Charts aggregate a period's results by area, stability and usage."""

from webapp.viz import area_chart_svg, box_stats, filter_summary, pie_svg, summarize_results


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
    ]
    model = summarize_results(results)
    assert box_stats([0.4, 0.9])["median"] == 0.65
    dry = next(a for a in model["areas"] if a["area_id"] == "DRY")
    assert dry["n"] == 2 and dry["review_needed"] == 1 and dry["unstable"] == 1
    assert dry["usage"]["median"] == 0.65
    assert model["areas"][0]["area_id"] == "DRY"  # highest median usage first
    assert [s["key"] for s in model["status_slices"]] == ["within_limits", "review_needed"]
    assert model["status_slices"][1]["count"] == 1

    view = filter_summary(model, "review_needed", None)
    assert [t["id"] for t in view["transformers"]] == ["T-B"]
    assert model["status_slices"][0]["count"] == 2  # pies stay on the full set

    dry["url"] = "/periods/2026-10-15/areas/DRY"
    model["areas"][1]["url"] = "/periods/2026-10-15/areas/CAR"
    model["areas"][1]["area_name"] = "Town <img>"
    svg = area_chart_svg(model["areas"], 0.9)
    assert 'href="/periods/2026-10-15/areas/DRY"' in svg
    assert "<img>" not in svg and "&lt;img&gt;" in svg

    pie = pie_svg([{"key": "review_needed", "label": "Review needed", "count": 1, "color": "#d7263d", "href": "/charts?status=review_needed"}], "review_needed")
    assert "circle" in pie and "review_needed" in pie
