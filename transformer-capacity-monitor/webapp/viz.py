"""Charts for a period's results: review outcome, load stability, and usage by area.

The numbers come from the period the pipeline already computed out of the feed CSVs
(readings, assets, boundaries, heat-pump forecast). This module only aggregates them.
"""

from __future__ import annotations

import csv
import math
from html import escape

STATUS_ORDER = ("within_limits", "review_needed")
STABILITY_ORDER = ("stable", "signal", "insufficient_history", "zero_variation")

STATUS_LABEL = {"within_limits": "Within limits", "review_needed": "Review needed"}
STABILITY_LABEL = {
    "stable": "Stable",
    "signal": "Unstable",
    "insufficient_history": "Short history",
    "zero_variation": "No variation",
}
STATUS_COLOR = {"within_limits": "#1b7f4b", "review_needed": "#d7263d"}
STABILITY_COLOR = {
    "stable": "#1b7f4b",
    "signal": "#d7263d",
    "insufficient_history": "#9a5b00",
    "zero_variation": "#5d6675",
}


def _quantile(sorted_vals: list[float], p: float) -> float:
    if len(sorted_vals) == 1:
        return sorted_vals[0]
    idx = p * (len(sorted_vals) - 1)
    lo = int(idx)
    hi = min(lo + 1, len(sorted_vals) - 1)
    frac = idx - lo
    return sorted_vals[lo] * (1 - frac) + sorted_vals[hi] * frac


def box_stats(values: list[float]) -> dict | None:
    """Min, quartiles and max. Whiskers are the full range so every reading stays visible."""
    clean = sorted(v for v in values if v is not None)
    if not clean:
        return None
    return {
        "n": len(clean),
        "min": clean[0],
        "q1": _quantile(clean, 0.25),
        "median": _quantile(clean, 0.5),
        "q3": _quantile(clean, 0.75),
        "max": clean[-1],
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
        stroke = ' stroke="#1d2430" stroke-width="3"' if s["key"] == active_key else ""
        parts.append(f'<a href="{escape(s["href"], quote=True)}"><circle cx="{cx}" cy="{cy}" r="{radius}" fill="{s["color"]}"{stroke}><title>{escape(s["label"])}: {s["count"]}</title></circle></a>')
    else:
        angle = 0.0
        for s in slices:
            sweep = 2 * math.pi * s["count"] / total
            stroke = ' stroke="#1d2430" stroke-width="3"' if s["key"] == active_key else ' stroke="#fff" stroke-width="1"'
            path = _arc(cx, cy, radius, angle, angle + sweep)
            parts.append(f'<a href="{escape(s["href"], quote=True)}"><path d="{path}" fill="{s["color"]}"{stroke}><title>{escape(s["label"])}: {s["count"]}</title></path></a>')
            angle += sweep
    parts.append("</svg>")
    return "".join(parts)


def _nice_max(pcts: list[float]) -> float:
    peak = max([100.0] + pcts)
    return max(100.0, math.ceil(peak / 10.0) * 10)


def _y_mapper(y_max: float, top: float, plot_h: float):
    def y(pct: float) -> float:
        return top + plot_h * (1 - pct / y_max)

    return y


def _ticks(y_max: float) -> list[float]:
    step = 25 if y_max <= 150 else 50
    ticks = []
    value = 0
    while value <= y_max + 0.01:
        ticks.append(float(value))
        value += step
    return ticks


def usage_strip_svg(rows: list[dict], near_ratio: float) -> str:
    """One box for every transformer, with a point per transformer that opens its review."""
    stats = box_stats([r["usage"] for r in rows])
    if not stats:
        return '<p class="muted">No usage figures in this view.</p>'
    pcts = [r["usage_pct"] for r in rows if r["usage_pct"] is not None]
    y_max = _nice_max(pcts)
    width, height = 640, 280
    left, right, top, bottom = 48, 16, 16, 28
    plot_h = height - top - bottom
    y = _y_mapper(y_max, top, plot_h)
    box_x = left + 70
    parts = [
        f'<svg viewBox="0 0 {width} {height}" width="100%" height="{height}" role="img">',
        "<style>.ref{stroke:#9a5b00;stroke-dasharray:4 3;stroke-width:1} .tick{fill:#5d6675;font-size:11px} .whisk{stroke:#1d2430;stroke-width:1.5} .box{fill:#e3eefb;stroke:#1d2430;stroke-width:1.5}</style>",
    ]
    for tick in _ticks(y_max):
        yy = y(tick)
        parts.append(f'<line x1="{left}" x2="{width - right}" y1="{yy:.1f}" y2="{yy:.1f}" stroke="#e6eaee"/>')
        parts.append(f'<text class="tick" x="{left - 6}" y="{yy + 4:.1f}" text-anchor="end">{tick:.0f}</text>')
    near = near_ratio * 100
    if 0 <= near <= y_max:
        parts.append(f'<line class="ref" x1="{left}" x2="{width - right}" y1="{y(near):.1f}" y2="{y(near):.1f}"/>')
        parts.append(f'<text class="tick" x="{width - right}" y="{y(near) - 4:.1f}" text-anchor="end">{near:.0f}% of rating</text>')
    smin, sq1, smed, sq3, smax = (stats[k] * 100 for k in ("min", "q1", "median", "q3", "max"))
    parts.append(f'<line class="whisk" x1="{box_x}" x2="{box_x}" y1="{y(smin):.1f}" y2="{y(smax):.1f}"/>')
    parts.append(f'<line class="whisk" x1="{box_x - 14}" x2="{box_x + 14}" y1="{y(smin):.1f}" y2="{y(smin):.1f}"/>')
    parts.append(f'<line class="whisk" x1="{box_x - 14}" x2="{box_x + 14}" y1="{y(smax):.1f}" y2="{y(smax):.1f}"/>')
    box_top, box_bot = y(sq3), y(sq1)
    parts.append(f'<rect class="box" x="{box_x - 22}" y="{box_top:.1f}" width="44" height="{max(box_bot - box_top, 1):.1f}"/>')
    parts.append(f'<line class="whisk" x1="{box_x - 22}" x2="{box_x + 22}" y1="{y(smed):.1f}" y2="{y(smed):.1f}"/>')
    for i, row in enumerate(r for r in rows if r["usage_pct"] is not None):
        jitter = ((i % 7) - 3) * 8
        color = STABILITY_COLOR.get(row["stability"], "#5d6675")
        cx = box_x + 90 + jitter
        cy = y(row["usage_pct"])
        label = f"{row['id']} {row['usage_pct']:.0f}% of rating, {STABILITY_LABEL.get(row['stability'], row['stability'])}"
        parts.append(
            f'<a href="{escape(row["url"], quote=True)}"><circle cx="{cx}" cy="{cy:.1f}" r="6" fill="{color}" stroke="#fff" stroke-width="1.5"><title>{escape(label)}</title></circle></a>'
        )
    parts.append(f'<text class="tick" x="{box_x}" y="{height - 8}" text-anchor="middle">middle half</text>')
    parts.append(f'<text class="tick" x="{box_x + 90}" y="{height - 8}" text-anchor="middle">each transformer</text>')
    parts.append("</svg>")
    return "".join(parts)


def area_chart_svg(areas: list[dict], near_ratio: float) -> str:
    """Usage by area. The whole column opens that area. A box appears once an area has two or more transformers."""
    if not areas:
        return '<p class="muted">No areas in this view.</p>'
    pcts = []
    for area in areas:
        for row in area["transformers"]:
            if row["usage_pct"] is not None:
                pcts.append(row["usage_pct"])
            if row["forecast_pct"] is not None:
                pcts.append(row["forecast_pct"])
    y_max = _nice_max(pcts)
    col_w = 72
    left, right, top, bottom = 48, 16, 16, 108
    width = left + right + col_w * len(areas)
    height = top + 220 + bottom
    plot_h = height - top - bottom
    y = _y_mapper(y_max, top, plot_h)
    parts = [
        f'<svg viewBox="0 0 {width} {height}" width="{width}" height="{height}" role="img">',
        "<style>.ref{stroke:#9a5b00;stroke-dasharray:4 3;stroke-width:1} .tick{fill:#5d6675;font-size:11px} .whisk{stroke:#1d2430;stroke-width:1.5} .box{fill:#e3eefb;stroke:#1d2430;stroke-width:1.5} .alabel{fill:#1d2430;font-size:11px} a:hover .hit{fill:#f3f6fb}</style>",
    ]
    for tick in _ticks(y_max):
        yy = y(tick)
        parts.append(f'<line x1="{left}" x2="{width - right}" y1="{yy:.1f}" y2="{yy:.1f}" stroke="#e6eaee"/>')
        parts.append(f'<text class="tick" x="{left - 6}" y="{yy + 4:.1f}" text-anchor="end">{tick:.0f}</text>')
    near = near_ratio * 100
    if 0 <= near <= y_max:
        parts.append(f'<line class="ref" x1="{left}" x2="{width - right}" y1="{y(near):.1f}" y2="{y(near):.1f}"/>')
        parts.append(f'<text class="tick" x="{width - right}" y="{max(y(near) - 4, 12):.1f}" text-anchor="end">{near:.0f}%</text>')

    for i, area in enumerate(areas):
        x0 = left + i * col_w
        cx = x0 + col_w / 2
        tip = f"{area['area_name']}: {area['n']} transformers, {area['review_needed']} need review"
        if area["usage"]:
            tip += f", median usage {area['usage']['median'] * 100:.0f}%"
        parts.append(f'<a href="{escape(area["url"], quote=True)}">')
        parts.append(f'<rect class="hit" x="{x0 + 2}" y="{top}" width="{col_w - 4}" height="{plot_h}" fill="transparent"/>')
        stats = area["usage"]
        if stats and stats["n"] >= 2:
            smin, sq1, smed, sq3, smax = (stats[k] * 100 for k in ("min", "q1", "median", "q3", "max"))
            parts.append(f'<line class="whisk" x1="{cx}" x2="{cx}" y1="{y(smin):.1f}" y2="{y(smax):.1f}"/>')
            parts.append(f'<line class="whisk" x1="{cx - 10}" x2="{cx + 10}" y1="{y(smin):.1f}" y2="{y(smin):.1f}"/>')
            parts.append(f'<line class="whisk" x1="{cx - 10}" x2="{cx + 10}" y1="{y(smax):.1f}" y2="{y(smax):.1f}"/>')
            box_top, box_bot = y(sq3), y(sq1)
            parts.append(f'<rect class="box" x="{cx - 16}" y="{box_top:.1f}" width="32" height="{max(box_bot - box_top, 1):.1f}"/>')
            parts.append(f'<line class="whisk" x1="{cx - 16}" x2="{cx + 16}" y1="{y(smed):.1f}" y2="{y(smed):.1f}"/>')
        for j, row in enumerate(r for r in area["transformers"] if r["usage_pct"] is not None):
            spread = 14 if stats and stats["n"] > 1 else 0
            jitter = ((j % 5) - 2) * (spread / 2)
            color = STABILITY_COLOR.get(row["stability"], "#5d6675")
            parts.append(f'<circle cx="{cx + jitter:.1f}" cy="{y(row["usage_pct"]):.1f}" r="5.5" fill="{color}" stroke="#fff" stroke-width="1"/>')
        forecast_pcts = [r["forecast_pct"] for r in area["transformers"] if r["forecast_pct"] is not None]
        if forecast_pcts and area["forecast"]:
            fy = y(area["forecast"]["median"] * 100)
            parts.append(f'<rect x="{cx - 5}" y="{fy - 5:.1f}" width="10" height="10" fill="#fff" stroke="#1f5fa8" stroke-width="1.5" transform="rotate(45 {cx} {fy:.1f})"/>')
        label_y = height - bottom + 12
        parts.append(f'<text class="alabel" x="{cx}" y="{label_y}" text-anchor="end" transform="rotate(-55 {cx} {label_y})">{escape(area["area_name"])}</text>')
        parts.append(f"<title>{escape(tip)}</title></a>")
    parts.append("</svg>")
    return "".join(parts)
