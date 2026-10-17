"""Charts for a period's results: review outcome, load stability, and usage by area.

The numbers come from the period the pipeline already computed out of the feed CSVs
(readings, assets, boundaries, heat-pump forecast). This module only aggregates them.
"""

from __future__ import annotations

import csv
import math
from html import escape

from capacity_monitor.aggregate import box_stats, county_control_statistics

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


# ---- county control charts ---------------------------------------------------------------
# One daily peak per transformer. A day is a large subgroup whose size changes, so:
# p (share at or above 90% of rating) and u (stability signals per transformer) match
# attribute data with a varying sample. X-S matches a large subgroup. X-R, np and c
# need a small or a fixed sample, so they are not drawn.

_EMPTY_CHART = '<p class="muted">Not enough daily peaks for this chart.</p>'


def _shewhart_panel(points: list[dict], center: float | None, period_start: str, title: str, x: float, y: float, width: float, height: float) -> list[str]:
    """One dark-theme Shewhart panel. points carry date, value, ucl, lcl, out."""
    values = [p["value"] for p in points if p["value"] is not None]
    limits = [p[k] for p in points for k in ("ucl", "lcl") if p.get(k) is not None]
    if center is not None:
        limits.append(center)
    if not values:
        return [f'<text x="{x + 8}" y="{y + 28}" fill="#5d6675" font-size="12">{escape(title)}: no points</text>']
    lo = min(values + limits)
    hi = max(values + limits)
    if lo == hi:
        lo, hi = lo - 1, hi + 1
    span = hi - lo
    lo -= span * 0.12
    hi += span * 0.18
    left, right, top, bottom = 44, 8, 16, 18
    plot_w = width - left - right
    plot_h = height - top - bottom
    n = max(len(points) - 1, 1)

    def px(i: int) -> float:
        return x + left + plot_w * i / n

    def py(v: float) -> float:
        return y + top + plot_h * (1 - (v - lo) / (hi - lo))

    parts = [f'<text x="{x + left}" y="{y + 11}" fill="#1D2430" font-size="11">{escape(title)}</text>']
    first_period = next((i for i, p in enumerate(points) if p["date"] >= period_start), None)
    if first_period is not None and plot_h > 0:
        parts.append(
            f'<rect x="{px(first_period):.1f}" y="{y + top:.1f}" width="{max(px(len(points) - 1) - px(first_period), 0):.1f}" height="{plot_h:.1f}" fill="rgba(182,130,53,.16)"/>'
        )
    def tick(v: float) -> str:
        return f"{v:.1f}" if abs(v) >= 10 else f"{v:.2f}"

    if center is not None:
        parts.append(f'<line x1="{x + left}" x2="{x + width - right}" y1="{py(center):.1f}" y2="{py(center):.1f}" stroke="#1B7F4B" stroke-dasharray="4 3" stroke-width="1"/>')
        parts.append(f'<text x="{x + left - 4}" y="{py(center) + 3:.1f}" fill="#1B7F4B" font-size="10" text-anchor="end">{tick(center)}</text>')
    labeled_ucl = next((p["ucl"] for p in reversed(points) if p.get("ucl") is not None), None)
    if labeled_ucl is not None:
        parts.append(f'<text x="{x + left - 4}" y="{py(labeled_ucl) + 3:.1f}" fill="#D7263D" font-size="10" text-anchor="end">{tick(labeled_ucl)}</text>')
    for key in ("ucl", "lcl"):
        pts = [(px(i), py(p[key])) for i, p in enumerate(points) if p.get(key) is not None]
        if len(pts) > 1:
            parts.append('<polyline fill="none" stroke="#D7263D" stroke-width="1" stroke-dasharray="3 3" points="' + " ".join(f"{a:.1f},{b:.1f}" for a, b in pts) + '"/>')
    series = [(px(i), py(p["value"])) for i, p in enumerate(points) if p["value"] is not None]
    if len(series) > 1:
        parts.append('<polyline fill="none" stroke="#1F5FA8" stroke-width="1.4" points="' + " ".join(f"{a:.1f},{b:.1f}" for a, b in series) + '"/>')
    for i, p in enumerate(points):
        if p["value"] is None:
            continue
        color = "#D7263D" if p.get("out") else "#1F5FA8"
        radius = 3.2 if p.get("out") else 2.1
        parts.append(f'<circle cx="{px(i):.1f}" cy="{py(p["value"]):.1f}" r="{radius}" fill="{color}"><title>{escape(p["date"])}: {p["value"]:.2f}</title></circle>')
    parts.append(f'<line x1="{x + left}" x2="{x + left}" y1="{y + top}" y2="{y + top + plot_h}" stroke="rgba(29,36,48,.3)"/>')
    parts.append(f'<line x1="{x + left}" x2="{x + width - right}" y1="{y + top + plot_h}" y2="{y + top + plot_h}" stroke="rgba(29,36,48,.3)"/>')
    for i in {0, len(points) // 2, len(points) - 1}:
        if 0 <= i < len(points):
            parts.append(f'<text x="{px(i):.1f}" y="{y + height - 4}" fill="#5d6675" font-size="10" text-anchor="middle">{escape(points[i]["date"][5:])}</text>')
    return parts


def _shewhart_svg(panels: list[tuple], period_start: str) -> str:
    """panels: (points, center, title). One panel fills the card; a pair is stacked."""
    if not panels or not any(item[0] for item in panels):
        return _EMPTY_CHART
    width = 460
    row_h = 108 if len(panels) > 1 else 150
    height = row_h * len(panels)
    parts = [f'<svg viewBox="0 0 {width} {height}" width="100%" height="100%" preserveAspectRatio="xMidYMid meet" role="img">']
    for i, (points, center, title) in enumerate(panels):
        parts.extend(_shewhart_panel(points, center, period_start, title, 0, i * row_h, width, row_h))
    parts.append("</svg>")
    return "".join(parts)


def county_control_charts(results: list[dict], period_start: str) -> dict:
    """Render the numerical aggregate series without calculating control limits."""
    stats = county_control_statistics(results, period_start)
    def panel(key, title):
        series = stats[key]
        return series["points"], series["center"], title

    return {
        "p_svg": _shewhart_svg([panel("p", "% at or above 90% of rating")], period_start),
        "u_svg": _shewhart_svg([panel("u", "Signals per 100 transformers")], period_start),
        "xs_svg": _shewhart_svg([
            panel("x", "X-bar, mean peak % of rating"), panel("s", "S, spread")
        ], period_start),
        **{key: stats[key] for key in ("p_out", "u_out", "x_out", "s_out")},
    }
