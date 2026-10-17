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
        stroke = ' stroke="#f3f1e8" stroke-width="3"' if s["key"] == active_key else ""
        parts.append(f'<a href="{escape(s["href"], quote=True)}"><circle cx="{cx}" cy="{cy}" r="{radius}" fill="{s["color"]}"{stroke}><title>{escape(s["label"])}: {s["count"]}</title></circle></a>')
    else:
        angle = 0.0
        for s in slices:
            sweep = 2 * math.pi * s["count"] / total
            stroke = ' stroke="#f3f1e8" stroke-width="3"' if s["key"] == active_key else ' stroke="#1a1919" stroke-width="1"'
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


# ---- county control charts ---------------------------------------------------------------
# One daily peak per transformer. A day is a large subgroup whose size changes, so:
# p (share at or above 90% of rating) and u (stability signals per transformer) match
# attribute data with a varying sample. X-S matches a large subgroup. X-R, np and c
# need a small or a fixed sample, so they are not drawn.

NEAR_RATIO = 0.9
_EMPTY_CHART = '<p class="muted">Not enough daily peaks for this chart.</p>'


def _c4(n: int) -> float:
    """Unbiasing constant for a subgroup standard deviation."""
    if n < 2:
        return 1.0
    return math.sqrt(2 / (n - 1)) * math.exp(math.lgamma(n / 2) - math.lgamma((n - 1) / 2))


def _sample_sd(values: list[float]) -> float | None:
    if len(values) < 2:
        return None
    mean = sum(values) / len(values)
    return math.sqrt(sum((v - mean) ** 2 for v in values) / (len(values) - 1))


def _day_buckets(results: list[dict]) -> dict[str, dict]:
    days: dict[str, dict] = {}
    for result in results:
        if result.get("is_calibration"):
            continue
        chart = result.get("chart") or {}
        try:
            rating = float(result.get("rated_max"))
        except (TypeError, ValueError):
            continue
        if rating <= 0:
            continue
        signals_on: dict[str, int] = {}
        for signal in chart.get("signals") or []:
            day = signal.get("date") or ""
            signals_on[day] = signals_on.get(day, 0) + 1
        for day, value in zip(chart.get("dates") or [], chart.get("values") or []):
            if value is None:
                continue
            try:
                ratio = float(value) / rating
            except (TypeError, ValueError):
                continue
            if not math.isfinite(ratio):
                continue
            bucket = days.setdefault(day, {"ratios": [], "signals": 0})
            bucket["ratios"].append(ratio)
            bucket["signals"] += signals_on.get(day, 0)
    return days


def _shewhart_panel(points: list[dict], center: float | None, period_start: str, title: str, x: float, y: float, width: float, height: float) -> list[str]:
    """One dark-theme Shewhart panel. points carry date, value, ucl, lcl, out."""
    values = [p["value"] for p in points if p["value"] is not None]
    limits = [p[k] for p in points for k in ("ucl", "lcl") if p.get(k) is not None]
    if center is not None:
        limits.append(center)
    if not values:
        return [f'<text x="{x + 8}" y="{y + 28}" fill="#aeaba3" font-size="12">{escape(title)}: no points</text>']
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

    parts = [f'<text x="{x + left}" y="{y + 11}" fill="#f3f1e8" font-size="11">{escape(title)}</text>']
    first_period = next((i for i, p in enumerate(points) if p["date"] >= period_start), None)
    if first_period is not None and plot_h > 0:
        parts.append(
            f'<rect x="{px(first_period):.1f}" y="{y + top:.1f}" width="{max(px(len(points) - 1) - px(first_period), 0):.1f}" height="{plot_h:.1f}" fill="rgba(201,150,74,.14)"/>'
        )
    def tick(v: float) -> str:
        return f"{v:.1f}" if abs(v) >= 10 else f"{v:.2f}"

    if center is not None:
        parts.append(f'<line x1="{x + left}" x2="{x + width - right}" y1="{py(center):.1f}" y2="{py(center):.1f}" stroke="#57b57f" stroke-dasharray="4 3" stroke-width="1"/>')
        parts.append(f'<text x="{x + left - 4}" y="{py(center) + 3:.1f}" fill="#57b57f" font-size="10" text-anchor="end">{tick(center)}</text>')
    labeled_ucl = next((p["ucl"] for p in reversed(points) if p.get("ucl") is not None), None)
    if labeled_ucl is not None:
        parts.append(f'<text x="{x + left - 4}" y="{py(labeled_ucl) + 3:.1f}" fill="#ff6b7a" font-size="10" text-anchor="end">{tick(labeled_ucl)}</text>')
    for key in ("ucl", "lcl"):
        pts = [(px(i), py(p[key])) for i, p in enumerate(points) if p.get(key) is not None]
        if len(pts) > 1:
            parts.append('<polyline fill="none" stroke="#ff6b7a" stroke-width="1" stroke-dasharray="3 3" points="' + " ".join(f"{a:.1f},{b:.1f}" for a, b in pts) + '"/>')
    series = [(px(i), py(p["value"])) for i, p in enumerate(points) if p["value"] is not None]
    if len(series) > 1:
        parts.append('<polyline fill="none" stroke="#8ab4f8" stroke-width="1.4" points="' + " ".join(f"{a:.1f},{b:.1f}" for a, b in series) + '"/>')
    for i, p in enumerate(points):
        if p["value"] is None:
            continue
        color = "#ff6b7a" if p.get("out") else "#8ab4f8"
        radius = 3.2 if p.get("out") else 2.1
        parts.append(f'<circle cx="{px(i):.1f}" cy="{py(p["value"]):.1f}" r="{radius}" fill="{color}"><title>{escape(p["date"])}: {p["value"]:.2f}</title></circle>')
    parts.append(f'<line x1="{x + left}" x2="{x + left}" y1="{y + top}" y2="{y + top + plot_h}" stroke="rgba(243,241,232,.35)"/>')
    parts.append(f'<line x1="{x + left}" x2="{x + width - right}" y1="{y + top + plot_h}" y2="{y + top + plot_h}" stroke="rgba(243,241,232,.35)"/>')
    for i in {0, len(points) // 2, len(points) - 1}:
        if 0 <= i < len(points):
            parts.append(f'<text x="{px(i):.1f}" y="{y + height - 4}" fill="#aeaba3" font-size="10" text-anchor="middle">{escape(points[i]["date"][5:])}</text>')
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


def _beyond(value: float, ucl: float, lcl: float) -> bool:
    return value > ucl + 1e-9 or value < lcl - 1e-9


def county_control_charts(results: list[dict], period_start: str) -> dict:
    """p, u and X-S charts. Limits come from days before the period."""
    days = _day_buckets(results)
    dates = sorted(days)
    base = [d for d in dates if d < period_start] or dates
    empty = {"p_svg": _EMPTY_CHART, "u_svg": _EMPTY_CHART, "xs_svg": _EMPTY_CHART, "p_out": 0, "u_out": 0, "x_out": 0, "s_out": 0}
    if len(dates) < 2:
        return empty

    def counted(day: str) -> tuple[int, int, int, float | None, float | None]:
        ratios = days[day]["ratios"]
        n = len(ratios)
        high = sum(1 for r in ratios if r >= NEAR_RATIO)
        mean = sum(ratios) / n if n else None
        return n, high, days[day]["signals"], mean, _sample_sd(ratios)

    base_n = sum(counted(d)[0] for d in base)
    if not base_n:
        return empty
    pbar = sum(counted(d)[1] for d in base) / base_n
    ubar = sum(counted(d)[2] for d in base) / base_n
    base_ratios = [r for d in base for r in days[d]["ratios"]]
    xbar_bar = sum(base_ratios) / len(base_ratios)
    base_s = [counted(d)[4] for d in base if counted(d)[4] is not None]
    sbar = sum(base_s) / len(base_s) if base_s else 0.0

    p_points, u_points, x_points, s_points = [], [], [], []
    p_out = u_out = x_out = s_out = 0
    for day in dates:
        n, high, signals, mean, sd = counted(day)
        if not n:
            continue
        in_period = day >= period_start
        se_p = math.sqrt(max(pbar * (1 - pbar), 0) / n)
        p_ucl, p_lcl = min(1.0, pbar + 3 * se_p), max(0.0, pbar - 3 * se_p)
        p_value = high / n
        p_hit = _beyond(p_value, p_ucl, p_lcl)
        p_out += int(p_hit and in_period)
        p_points.append({"date": day, "value": p_value * 100, "ucl": p_ucl * 100, "lcl": p_lcl * 100, "out": p_hit})

        se_u = math.sqrt(max(ubar, 0) / n)
        u_ucl, u_lcl = ubar + 3 * se_u, max(0.0, ubar - 3 * se_u)
        u_value = signals / n
        u_hit = _beyond(u_value, u_ucl, u_lcl)
        u_out += int(u_hit and in_period)
        u_points.append({"date": day, "value": u_value * 100, "ucl": u_ucl * 100, "lcl": u_lcl * 100, "out": u_hit})

        if mean is None or sd is None or sbar <= 0 or n < 2:
            continue
        c4 = _c4(n)
        sigma_factor = math.sqrt(max(1 - c4 * c4, 0)) / c4
        a3 = 3 / (c4 * math.sqrt(n))
        b4 = 1 + 3 * sigma_factor
        b3 = max(0.0, 1 - 3 * sigma_factor)
        x_ucl, x_lcl = (xbar_bar + a3 * sbar) * 100, (xbar_bar - a3 * sbar) * 100
        x_value = mean * 100
        x_hit = _beyond(x_value, x_ucl, x_lcl)
        x_out += int(x_hit and in_period)
        x_points.append({"date": day, "value": x_value, "ucl": x_ucl, "lcl": x_lcl, "out": x_hit})
        s_ucl, s_lcl = b4 * sbar * 100, b3 * sbar * 100
        s_value = sd * 100
        s_hit = _beyond(s_value, s_ucl, s_lcl)
        s_out += int(s_hit and in_period)
        s_points.append({"date": day, "value": s_value, "ucl": s_ucl, "lcl": s_lcl, "out": s_hit})

    return {
        "p_svg": _shewhart_svg([(p_points, pbar * 100, "% at or above 90% of rating")], period_start),
        "u_svg": _shewhart_svg([(u_points, ubar * 100, "Signals per 100 transformers")], period_start),
        "xs_svg": _shewhart_svg(
            [(x_points, xbar_bar * 100, "X-bar, mean peak % of rating"), (s_points, sbar * 100, "S, spread")],
            period_start,
        ),
        "p_out": p_out,
        "u_out": u_out,
        "x_out": x_out,
        "s_out": s_out,
    }
