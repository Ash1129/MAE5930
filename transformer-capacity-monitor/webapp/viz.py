"""Charts for a period's results: review outcome, load stability, and usage by area.

The numbers come from the period the pipeline already computed out of the feed CSVs
(readings, assets, boundaries, heat-pump forecast). This module only aggregates them.
"""

from __future__ import annotations

import csv
import math
from html import escape

from capacity_monitor.aggregate import box_stats, county_trend_statistics

STATUS_ORDER = ("within_limits", "review_needed", "inspect_now")
STABILITY_ORDER = ("stable", "signal", "insufficient_history", "zero_variation")

STATUS_LABEL = {"within_limits": "Within limits", "review_needed": "Review needed", "inspect_now": "Inspect now"}
STABILITY_LABEL = {
    "stable": "Stable",
    "signal": "Unstable",
    "insufficient_history": "Short history",
    "zero_variation": "No variation",
}
STATUS_COLOR = {"within_limits": "#1b7f4b", "review_needed": "#e8960c", "inspect_now": "#d7263d"}
STABILITY_COLOR = {
    "stable": "#1b7f4b",
    "signal": "#d7263d",
    "insufficient_history": "#9a5b00",
    "zero_variation": "#5d6675",
}


def usage_band(ratio: float | None) -> str:
    if ratio is None:
        return "none"
    if ratio >= 0.9:
        return "high"
    if ratio >= 0.7:
        return "mid"
    return "ok"


def _row(result: dict) -> dict:
    cap = result.get("capacity") or {}
    usage = cap.get("period_peak_ratio")
    forecast = cap.get("forecast_ratio")
    return {
        "id": result.get("transformer_id", ""),
        "name": result.get("name") or "",
        "area_id": result.get("area_id") or "unknown",
        "area_name": result.get("area_name") or result.get("area_id") or "Unknown area",
        "status": result.get("status") or "",
        "stability": result.get("stability") or "",
        "usage": usage,
        "forecast": forecast,
        "usage_pct": None if usage is None else usage * 100,
        "forecast_pct": None if forecast is None else forecast * 100,
        "usage_band": usage_band(usage),
        "peak": cap.get("period_peak"),
        "rating": result.get("rated_max"),
        "unit": result.get("unit") or "",
        "customers": result.get("customers"),
        "reason": (result.get("decision") or {}).get("reason") or "",
        "rule": (result.get("decision") or {}).get("rule"),
    }


def _counts(rows: list[dict], key: str, order: tuple[str, ...], labels: dict, colors: dict) -> list[dict]:
    found = {k: 0 for k in order}
    extra = []
    for row in rows:
        value = row.get(key) or ""
        if value in found:
            found[value] += 1
        elif value and value not in extra:
            extra.append(value)
    slices = [{"key": k, "label": labels.get(k, k), "count": found[k], "color": colors.get(k, "#5d6675")} for k in order if found[k]]
    for value in extra:
        slices.append({"key": value, "label": value.replace("_", " "), "count": sum(1 for r in rows if r.get(key) == value), "color": "#5d6675"})
    return slices


def summarize_results(results: list[dict]) -> dict:
    """Aggregate one period. Seeded calibration cases are left out of the charts."""
    skipped = 0
    rows = []
    for result in results:
        if result.get("is_calibration"):
            skipped += 1
            continue
        rows.append(_row(result))

    by_area: dict[str, list[dict]] = {}
    for row in rows:
        by_area.setdefault(row["area_id"], []).append(row)

    areas = []
    for area_id, members in by_area.items():
        members.sort(key=lambda r: (r["usage"] is None, -(r["usage"] or 0), r["id"]))
        usage = box_stats([r["usage"] for r in members])
        forecast = box_stats([r["forecast"] for r in members if r["forecast"] is not None])
        areas.append(
            {
                "area_id": area_id,
                "area_name": members[0]["area_name"],
                "n": len(members),
                "review_needed": sum(1 for r in members if r["status"] == "review_needed"),
                "inspect_now": sum(1 for r in members if r["status"] == "inspect_now"),
                "flagged": sum(1 for r in members if r["status"] != "within_limits"),
                "stable": sum(1 for r in members if r["stability"] == "stable"),
                "unstable": sum(1 for r in members if r["stability"] == "signal"),
                "usage": usage,
                "forecast": forecast,
                "transformers": members,
            }
        )
    areas.sort(key=lambda a: (-(a["usage"]["median"] if a["usage"] else -1), a["area_name"]))

    return {
        "transformers": sorted(rows, key=lambda r: (r["usage"] is None, -(r["usage"] or 0), r["id"])),
        "calibration_excluded": skipped,
        "status_slices": _counts(rows, "status", STATUS_ORDER, STATUS_LABEL, STATUS_COLOR),
        "stability_slices": _counts(rows, "stability", STABILITY_ORDER, STABILITY_LABEL, STABILITY_COLOR),
        "usage": box_stats([r["usage"] for r in rows]),
        "forecast": box_stats([r["forecast"] for r in rows if r["forecast"] is not None]),
        "areas": areas,
    }


def filter_summary(model: dict, status: str | None, stability: str | None) -> dict:
    """Same summary, limited to one review outcome and/or one stability class. Pies stay complete."""
    if not status and not stability:
        return model
    rows = [
        r
        for r in model["transformers"]
        if (not status or r["status"] == status) and (not stability or r["stability"] == stability)
    ]
    by_area: dict[str, list[dict]] = {}
    for row in rows:
        by_area.setdefault(row["area_id"], []).append(row)
    areas = []
    for area in model["areas"]:
        members = by_area.get(area["area_id"])
        if not members:
            continue
        areas.append(
            {
                **area,
                "n": len(members),
                "review_needed": sum(1 for r in members if r["status"] == "review_needed"),
                "inspect_now": sum(1 for r in members if r["status"] == "inspect_now"),
                "flagged": sum(1 for r in members if r["status"] != "within_limits"),
                "stable": sum(1 for r in members if r["stability"] == "stable"),
                "unstable": sum(1 for r in members if r["stability"] == "signal"),
                "usage": box_stats([r["usage"] for r in members]),
                "forecast": box_stats([r["forecast"] for r in members if r["forecast"] is not None]),
                "transformers": members,
            }
        )
    return {
        **model,
        "transformers": rows,
        "usage": box_stats([r["usage"] for r in rows]),
        "forecast": box_stats([r["forecast"] for r in rows if r["forecast"] is not None]),
        "areas": areas,
    }


def forecast_row(path, version: str, area_id: str) -> dict | None:
    """The playbook forecast version for one area, read straight from the forecast CSV."""
    try:
        fh = open(path, encoding="utf-8", newline="")
    except OSError:
        return None
    with fh:
        for row in csv.DictReader(fh):
            if row.get("area_id") == area_id and row.get("forecast_version") == version:
                return row
    return None


def _arc(cx: float, cy: float, r: float, a0: float, a1: float) -> str:
    large = 1 if (a1 - a0) > math.pi else 0

    def pt(angle: float) -> tuple[float, float]:
        return cx + r * math.sin(angle), cy - r * math.cos(angle)

    x0, y0 = pt(a0)
    x1, y1 = pt(a1)
    return f"M {cx:.2f} {cy:.2f} L {x0:.2f} {y0:.2f} A {r:.2f} {r:.2f} 0 {large} 1 {x1:.2f} {y1:.2f} Z"


def pie_svg(slices: list[dict], active_key: str | None = None) -> str:
    """Donut-free pie. Each slice is a link. A single slice is drawn as a circle."""
    total = sum(s["count"] for s in slices)
    if total <= 0:
        return '<svg viewBox="0 0 220 220" width="220" height="220" role="img"><text x="110" y="114" text-anchor="middle" fill="#5d6675" font-size="13">No data</text></svg>'
    cx = cy = 110
    radius = 88
    parts = ['<svg viewBox="0 0 220 220" width="220" height="220" role="img">']
    if len(slices) == 1:
        s = slices[0]
        stroke = ' stroke="#1D2430" stroke-width="3"' if s["key"] == active_key else ""
        parts.append(f'<a href="{escape(s["href"], quote=True)}"><circle cx="{cx}" cy="{cy}" r="{radius}" fill="{s["color"]}"{stroke}><title>{escape(s["label"])}: {s["count"]}</title></circle></a>')
    else:
        angle = 0.0
        for s in slices:
            sweep = 2 * math.pi * s["count"] / total
            stroke = ' stroke="#1D2430" stroke-width="3"' if s["key"] == active_key else ' stroke="#f3f2f2" stroke-width="1"'
            path = _arc(cx, cy, radius, angle, angle + sweep)
            parts.append(f'<a href="{escape(s["href"], quote=True)}"><path d="{path}" fill="{s["color"]}"{stroke}><title>{escape(s["label"])}: {s["count"]}</title></path></a>')
            angle += sweep
    parts.append("</svg>")
    return "".join(parts)


# ---- descriptive daily trends -----------------------------------------------------------

_EMPTY_CHART = '<p class="muted">No eligible daily peaks for this trend.</p>'


def _trend_svg(points: list[dict], key: str, title: str, period_start: str,
               band: bool = False) -> str:
    """Render descriptive points, with an optional interquartile ribbon."""
    if not points:
        return _EMPTY_CHART
    width, height = 460, 190
    left, right, top, bottom = 48, 16, 25, 30
    lo = min(p["q1_pct"] if band else p[key] for p in points)
    hi = max(p["q3_pct"] if band else p[key] for p in points)
    span = hi - lo or max(abs(hi) * .1, 1)
    lo = max(0, lo - span * .1)
    hi += span * .15
    def px(i):
        return left + (width - left - right) * i / max(len(points) - 1, 1)
    def py(value):
        return top + (height - top - bottom) * (hi - value) / (hi - lo)
    parts = [f'<svg viewBox="0 0 {width} {height}" width="100%" height="100%" role="img" aria-label="{escape(title, quote=True)}"><title>{escape(title)}</title>']
    first = next((i for i, p in enumerate(points) if p["date"] >= period_start), None)
    if first is not None:
        x = max(left, px(first) - (px(1) - px(0))/2) if len(points) > 1 else left
        parts.append(f'<rect x="{x:.1f}" y="{top}" width="{width-right-x:.1f}" height="{height-top-bottom}" fill="rgba(182,130,53,.12)"/>')
    for value in (lo, (lo + hi)/2, hi):
        parts.append(f'<text x="{left-6}" y="{py(value)+3:.1f}" fill="#5d6675" font-size="10" text-anchor="end">{value:.1f}</text>')
    if band:
        coords = [(px(i), py(p["q3_pct"])) for i,p in enumerate(points)]
        coords += [(px(i), py(p["q1_pct"])) for i,p in reversed(list(enumerate(points)))]
        parts.append('<polygon fill="rgba(31,95,168,.18)" points="'+ ' '.join(f'{x:.1f},{y:.1f}' for x,y in coords)+'"/>')
    coords = ' '.join(f'{px(i):.1f},{py(p[key]):.1f}' for i,p in enumerate(points))
    parts.append(f'<polyline fill="none" stroke="#1F5FA8" stroke-width="1.5" points="{coords}"/>')
    for i,p in enumerate(points):
        detail = f'{p["date"]}: {p[key]:.2f}; {p["n"]} reporting'
        if band:
            detail += f'; middle 50% {p["q1_pct"]:.2f}–{p["q3_pct"]:.2f}%'
        parts.append(f'<circle cx="{px(i):.1f}" cy="{py(p[key]):.1f}" r="2.3" fill="#1F5FA8"><title>{escape(detail)}</title></circle>')
    parts.append(f'<path d="M {left} {top} V {height-bottom} H {width-right}" fill="none" stroke="#87909a"/>')
    for i in sorted({0, len(points)//2, len(points)-1}):
        anchor = "start" if i == 0 else ("end" if i == len(points)-1 else "middle")
        parts.append(f'<text x="{px(i):.1f}" y="{height-8}" fill="#5d6675" font-size="10" text-anchor="{anchor}">{escape(points[i]["date"][5:])}</text>')
    parts.append('</svg>')
    return ''.join(parts)


def county_trend_charts(results: list[dict], period_start: str) -> dict:
    """Render the numerical daily summaries; no aggregate alarm interpretation."""
    points = county_trend_statistics(results)["points"]
    return {
        "near_svg": _trend_svg(points, "near_rating_pct", "At or above 90% of rating (%)", period_start),
        "signals_svg": _trend_svg(points, "signal_transformers", "Transformers with signals (count)", period_start),
        "loading_svg": _trend_svg(points, "median_pct", "Median loading and middle 50% (% of rating)", period_start, band=True),
    }
