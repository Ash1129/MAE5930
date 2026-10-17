"""SVG rendering for the I-MR control chart. Standard library only."""

from __future__ import annotations

from html import escape


def _scale(vmin, vmax, pad=0.1):
    if vmin == vmax:
        vmin, vmax = vmin - 1, vmax + 1
    span = vmax - vmin
    return vmin - span * pad, vmax + span * pad


def _panel(dates, values, lines, signal_dates, period_start, title, unit, width, height, top):
    left, right, bottom = 60, 20, 28
    ys = [v for v in values if v is not None] + [v for _, v, _ in lines if v is not None]
    lo, hi = _scale(min(ys), max(ys))
    n = max(len(values) - 1, 1)

    def x(i):
        return left + (width - left - right) * i / n

    def y(v):
        return top + (height - bottom) - (height - bottom) * (v - lo) / (hi - lo)

    parts = [f'<text x="{left}" y="{top - 6}" class="title">{escape(title)}</text>']
    # period shading
    first_period = next((i for i, d in enumerate(dates) if d >= period_start), None)
    if first_period is not None:
        parts.append(f'<rect x="{x(first_period):.1f}" y="{top}" width="{x(len(dates) - 1) - x(first_period):.1f}" height="{height - bottom}" class="period"/>')
    for label, val, cls in lines:
        if val is None:
            continue
        parts.append(f'<line x1="{left}" x2="{width - right}" y1="{y(val):.1f}" y2="{y(val):.1f}" class="{cls}"/>')
        parts.append(f'<text x="{width - right}" y="{y(val) - 3:.1f}" class="limit-label" text-anchor="end">{escape(label)} {val:,.1f}</text>')
    pts = [(x(i), y(v)) for i, v in enumerate(values) if v is not None]
    if len(pts) > 1:
        parts.append('<polyline class="series" points="' + " ".join(f"{px:.1f},{py:.1f}" for px, py in pts) + '"/>')
    for i, v in enumerate(values):
        if v is None:
            continue
        cls = "signal" if dates[i] in signal_dates else "pt"
        parts.append(f'<circle cx="{x(i):.1f}" cy="{y(v):.1f}" r="{4 if cls == "signal" else 2.5}" class="{cls}"><title>{dates[i]}: {v:,.1f} {escape(unit)}</title></circle>')
    # axes
    parts.append(f'<line x1="{left}" x2="{left}" y1="{top}" y2="{top + height - bottom}" class="axis"/>')
    parts.append(f'<line x1="{left}" x2="{width - right}" y1="{top + height - bottom}" y2="{top + height - bottom}" class="axis"/>')
    for frac in (0, 0.5, 1):
        v = lo + (hi - lo) * frac
        parts.append(f'<text x="{left - 6}" y="{y(v) + 4:.1f}" class="tick" text-anchor="end">{v:,.0f}</text>')
    step = max(1, len(dates) // 6)
    for i in range(0, len(dates), step):
        parts.append(f'<text x="{x(i):.1f}" y="{top + height - bottom + 16}" class="tick" text-anchor="middle">{dates[i][5:]}</text>')
    return "\n".join(parts)


def imr_svg(chart: dict, period_start: str, unit: str = "", rating: float | None = None, width: int = 860) -> str:
    """Two panels: individuals (with limits and, separately styled, the rated maximum) and moving range."""
    dates = chart["dates"]
    if not dates:
        return '<svg xmlns="http://www.w3.org/2000/svg" width="400" height="60"><text x="10" y="35">No readings to chart</text></svg>'
    signal_dates = {s["date"] for s in chart["signals"] if s["rule"] != "moving_range_beyond_ucl"}
    mr_signal_dates = {s["date"] for s in chart["signals"] if s["rule"] == "moving_range_beyond_ucl"}
    h1, h2 = 230, 150
    i_lines = [("UCL", chart.get("ucl"), "limit"), ("CL", chart.get("center"), "center"), ("LCL", chart.get("lcl"), "limit")]
    if rating:
        i_lines.append(("Rated max", rating, "rating"))
    mr_lines = [("UCL", chart.get("mr_ucl"), "limit"), ("MRbar", chart.get("mr_bar"), "center")]
    body = _panel(dates, chart["values"], i_lines, signal_dates, period_start, f"Individuals: daily peak load ({unit})", unit, width, h1, 24)
    body += _panel(dates, chart["moving_ranges"], mr_lines, mr_signal_dates, period_start, "Moving range", unit, width, h2, h1 + 40)
    style = """
    <style>
      .title{font:600 13px system-ui,sans-serif;fill:#333}
      .tick{font:11px system-ui,sans-serif;fill:#666}
      .limit-label{font:10px system-ui,sans-serif;fill:#555}
      .axis{stroke:#999;stroke-width:1}
      .series{fill:none;stroke:#1f5fa8;stroke-width:1.5}
      .pt{fill:#1f5fa8}
      .signal{fill:#d7263d;stroke:#7a0010;stroke-width:1}
      .limit{stroke:#d7263d;stroke-width:1;stroke-dasharray:5 4}
      .center{stroke:#2a9d8f;stroke-width:1}
      .rating{stroke:#111;stroke-width:2}
      .period{fill:#ffe9a8;opacity:.45}
    </style>"""
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{h1 + h2 + 50}" viewBox="0 0 {width} {h1 + h2 + 50}">{style}\n{body}\n</svg>'


def rating_svg(chart: dict, period_start: str, rating: float | None, width: int = 860) -> str:
    """Daily peak as a percent of the nameplate. The 70, 90 and 100 lines are reference marks, not control limits."""
    dates = chart.get("dates") or []
    values = chart.get("values") or []
    if not dates or not rating or rating <= 0:
        return ""
    pcts = [None if v is None else 100.0 * float(v) / float(rating) for v in values]
    if not any(v is not None for v in pcts):
        return ""
    near = {d for d, v in zip(dates, pcts) if v is not None and v >= 90}
    height = 210
    lines = [("Rated max", 100.0, "rating"), ("90%", 90.0, "limit"), ("70%", 70.0, "guide")]
    body = _panel(dates, pcts, lines, near, period_start, "Daily peak as percent of rated maximum", "%", width, height, 24)
    style = """
    <style>
      .title{font:600 13px system-ui,sans-serif;fill:#333}
      .tick{font:11px system-ui,sans-serif;fill:#666}
      .limit-label{font:10px system-ui,sans-serif;fill:#555}
      .axis{stroke:#999;stroke-width:1}
      .series{fill:none;stroke:#1f5fa8;stroke-width:1.5}
      .pt{fill:#1f5fa8}
      .signal{fill:#d7263d;stroke:#7a0010;stroke-width:1}
      .limit{stroke:#d7263d;stroke-width:1;stroke-dasharray:5 4}
      .guide{stroke:#b68235;stroke-width:1;stroke-dasharray:2 3}
      .rating{stroke:#111;stroke-width:2}
      .period{fill:#ffe9a8;opacity:.45}
    </style>"""
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height + 36}" viewBox="0 0 {width} {height + 36}">{style}\n{body}\n</svg>'


def mini_imr_svg(chart: dict, period_start: str, unit: str = "", rating: float | None = None, width: int = 308) -> str:
    """Compact I-MR chart for the map popup. Inline attributes only (no <style>), so it cannot leak CSS into the page.

    Individuals panel with the history-based limits and centre line, the review period shaded, signal points in red,
    and the rated maximum drawn only when it falls inside the plotted range (otherwise noted as text).
    """
    dates = chart.get("dates") or []
    vals = chart.get("values") or []
    if not dates:
        return f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="40" role="img" aria-label="No readings"><text x="4" y="24" font-size="11" fill="#5d6675">No readings to chart</text></svg>'
    left, right, h1, h2, gap = 34, 6, 92, 44, 16
    height = 14 + h1 + gap + h2 + 16
    n = max(len(vals) - 1, 1)
    x = lambda i: left + (width - left - right) * i / n  # noqa: E731
    sig_i = {s["date"] for s in chart.get("signals", []) if s["rule"] != "moving_range_beyond_ucl"}
    sig_mr = {s["date"] for s in chart.get("signals", []) if s["rule"] == "moving_range_beyond_ucl"}
    first_period = next((i for i, d in enumerate(dates) if d >= period_start), None)

    def panel(series, lines, sig, top, ph, label):
        ys = [v for v in series if v is not None] + [v for _, v, _ in lines if v is not None]
        lo, hi = min(ys), max(ys)
        if lo == hi:
            lo, hi = lo - 1, hi + 1
        pad = (hi - lo) * 0.12
        lo, hi = lo - pad, hi + pad
        y = lambda v: top + ph - ph * (v - lo) / (hi - lo)  # noqa: E731
        out = [f'<text x="{left}" y="{top - 3}" font-size="9.5" fill="#5d6675" letter-spacing=".06em">{escape(label)}</text>']
        if first_period is not None:
            out.append(f'<rect x="{x(first_period):.1f}" y="{top}" width="{max(x(len(dates) - 1) - x(first_period), 2):.1f}" height="{ph}" fill="#f4b400" opacity=".16"/>')
        for name, val, kind in lines:
            if val is None:
                continue
            stroke, dash, sw = {"limit": ("#d7263d", "4 3", 1), "center": ("#2a9d8f", "", 1), "rating": ("#1d2430", "", 1.6)}[kind]
            out.append(f'<line x1="{left}" x2="{width - right}" y1="{y(val):.1f}" y2="{y(val):.1f}" stroke="{stroke}" stroke-width="{sw}"' + (f' stroke-dasharray="{dash}"' if dash else "") + "/>")
            out.append(f'<text x="{width - right}" y="{y(val) - 2:.1f}" font-size="8.5" text-anchor="end" fill="{stroke}">{escape(name)}</text>')
        pts = [(x(i), y(v)) for i, v in enumerate(series) if v is not None]
        if len(pts) > 1:
            out.append('<polyline fill="none" stroke="#1f5fa8" stroke-width="1.2" points="' + " ".join(f"{a:.1f},{b:.1f}" for a, b in pts) + '"/>')
        for i, v in enumerate(series):
            if v is not None and dates[i] in sig:
                out.append(f'<circle cx="{x(i):.1f}" cy="{y(v):.1f}" r="3.2" fill="#d7263d" stroke="#fff" stroke-width="1"><title>{dates[i]}: {v:,.1f} {escape(unit)}</title></circle>')
        out.append(f'<line x1="{left}" x2="{left}" y1="{top}" y2="{top + ph}" stroke="#9aa1ab" stroke-width=".8"/>')
        for frac in (0, 1):
            v = lo + (hi - lo) * frac
            out.append(f'<text x="{left - 4}" y="{y(v) + 3:.1f}" font-size="8.5" text-anchor="end" fill="#5d6675">{v:,.0f}</text>')
        return "".join(out)

    i_lines = [("UCL", chart.get("ucl"), "limit"), ("CL", chart.get("center"), "center"), ("LCL", chart.get("lcl"), "limit")]
    note = ""
    if rating:
        ymax = max([v for v in vals if v is not None] + [chart.get("ucl") or 0])
        if rating <= ymax * 1.18:
            i_lines.append(("Rated max", rating, "rating"))
        else:
            note = f"Rated max {rating:,.0f} {unit} is above this range"
    mr_lines = [("UCL", chart.get("mr_ucl"), "limit"), ("MR̄", chart.get("mr_bar"), "center")]
    body = panel(vals, i_lines, sig_i, 14, h1, f"DAILY PEAK ({unit})")
    body += panel(chart.get("moving_ranges") or [], mr_lines, sig_mr, 14 + h1 + gap, h2, "MOVING RANGE")
    foot = f"{dates[0][5:]} to {dates[-1][5:]}" + (f" · {note}" if note else "") + ("" if chart.get("center") is not None else " · not enough history for limits")
    body += f'<text x="{left}" y="{height - 3}" font-size="8.5" fill="#5d6675">{escape(foot)}</text>'
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="100%" viewBox="0 0 {width} {height}" role="img" aria-label="Control chart of daily peak load">{body}</svg>'


def _nice_step(span: float, target: int = 5) -> float:
    raw = span / max(target, 1)
    mag = 10 ** len(str(int(raw))) / 10 if raw >= 1 else 1
    for m in (1, 2, 2.5, 5, 10):
        if raw <= m * mag:
            return m * mag
    return 10 * mag


def review_chart_svg(chart: dict, period_start: str, unit: str = "kVA", rating: float | None = None) -> str:
    """Daily peak chart for the review page (light ground). Inline attributes only, literal text in every <text>.

    Rating as a 2px ink line labeled just inside the left edge of the plot; UCL/LCL dashed blue; centre line blue at 50%;
    this period shaded accent with its points in accent-700; history points small grey; signal points red.
    """
    dates, vals = chart.get("dates") or [], chart.get("values") or []
    W, H, L, R, TOP, BOT = 900, 260, 52, 886, 10, 230
    if not dates:
        return f'<svg viewBox="0 0 {W} 60" role="img" aria-label="No readings" style="width:100%;height:auto;display:block"><text x="{L}" y="34" font-size="12" fill="rgba(29,36,48,.6)">No readings to chart</text></svg>'
    lines = [v for v in (chart.get("ucl"), chart.get("lcl"), chart.get("center"), rating) if v is not None]
    ys = [v for v in vals if v is not None] + lines
    lo, hi = min(ys), max(ys)
    if lo == hi:
        lo, hi = lo - 1, hi + 1
    pad = (hi - lo) * 0.06
    lo, hi = lo - pad, hi + pad
    step = _nice_step(hi - lo)
    n = max(len(dates) - 1, 1)
    x = lambda i: L + (R - L) * i / n  # noqa: E731
    y = lambda v: TOP + (hi - v) / (hi - lo) * (BOT - TOP)  # noqa: E731
    ink, blue = "rgba(29,36,48,", "#1F5FA8"
    out = [f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="Daily peak load chart" style="width:100%;height:auto;display:block;font-family:Lora,Georgia,serif">']
    annotations = []
    first = next((i for i, d in enumerate(dates) if d >= period_start), None)
    if first is not None:
        x0 = x(first) - (6 if first else 0)
        out.append(f'<rect x="{x0:.1f}" y="{TOP}" width="{max(x(len(dates) - 1) - x0 + 6, 4):.1f}" height="{BOT - TOP}" fill="rgba(182,130,53,.16)"/>')
    t = (lo // step + 1) * step
    while t < hi:
        out.append(f'<line x1="{L - 4}" x2="{L}" y1="{y(t):.1f}" y2="{y(t):.1f}" stroke="{ink}.25)"/>')
        out.append(f'<text x="{L - 8}" y="{y(t) + 4:.1f}" text-anchor="end" font-size="11" fill="{ink}.55)">{t:g}</text>')
        t += step
    for key, dash, w, op in (("ucl", "5 4", 1.2, 1), ("lcl", "5 4", 1.2, 1), ("center", "", 1, .5)):
        v = chart.get(key)
        if v is not None:
            da = f' stroke-dasharray="{dash}"' if dash else ""
            out.append(f'<line x1="{L - 4}" x2="{R + 4}" y1="{y(v):.1f}" y2="{y(v):.1f}" stroke="{blue}" stroke-width="{w}" opacity="{op}"{da}/>')
    if rating is not None:
        out.append(f'<line x1="{L - 4}" x2="{R + 4}" y1="{y(rating):.1f}" y2="{y(rating):.1f}" stroke="{ink}.85)" stroke-width="2"/>')
        ly = y(rating) - 6 if y(rating) - 6 > TOP + 8 else y(rating) + 14
        annotations.append(f'<text x="{L + 8}" y="{ly:.1f}" text-anchor="start" font-size="11" stroke="#f8f7f6" stroke-width="4" stroke-linejoin="round" paint-order="stroke" data-annotation="rating" fill="{ink}.75)">rating {rating:,.0f} {escape(unit)}</text>')
    pts = [(i, v) for i, v in enumerate(vals) if v is not None]
    if pts:
        out.append('<path d="' + " ".join(("M" if k == 0 else "L") + f"{x(i):.1f} {y(v):.1f}" for k, (i, v) in enumerate(pts)) + f'" fill="none" stroke="{ink}.7)" stroke-width="1.4"/>')
    sig = {s["date"] for s in chart.get("signals") or [] if s.get("rule") != "moving_range_beyond_ucl"}
    for i, v in pts:
        d = dates[i]
        if d in sig:
            out.append(f'<circle cx="{x(i):.1f}" cy="{y(v):.1f}" r="3.8" fill="#D7263D"><title>{escape(d)}: {v:,.1f} {escape(unit)}, I-MR signal</title></circle>')
        elif first is not None and i >= first:
            out.append(f'<circle cx="{x(i):.1f}" cy="{y(v):.1f}" r="3.5" fill="#7d5411"><title>{escape(d)}: {v:,.1f} {escape(unit)}</title></circle>')
        else:
            out.append(f'<circle cx="{x(i):.1f}" cy="{y(v):.1f}" r="2.4" fill="{ink}.6)"><title>{escape(d)}: {v:,.1f} {escape(unit)}</title></circle>')
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    k = min(5, len(dates))
    idx = sorted({round(j * n / (k - 1)) for j in range(k)}) if k > 1 else [0]
    for j, i in enumerate(idx):
        d = dates[i]
        label = f"{months[int(d[5:7]) - 1]} {int(d[8:10])}"
        anchor = "start" if j == 0 else "end" if j == len(idx) - 1 else "middle"
        out.append(f'<text x="{x(i):.1f}" y="250" text-anchor="{anchor}" font-size="11" fill="{ink}.55)">{label}</text>')
    out.extend(annotations)
    out.append("</svg>")
    return "".join(out)


def review_chart_caption(chart: dict, unit: str = "kVA") -> str:
    """One plain sentence under the review chart."""
    status = chart.get("status")
    lcl, ucl = chart.get("lcl"), chart.get("ucl")
    rng = f" ({lcl:,.1f} to {ucl:,.1f} {unit})" if lcl is not None and ucl is not None else ""
    if status == "signal":
        return (f"Configured I-MR signals were detected: a limit exceedance or a run-pattern rule. "
                f"The historical control range is{rng}; a pattern signal can occur inside these limits. "
                "Investigate the cause before interpreting capability. The black line is the nameplate rating.")
    if status == "insufficient_history":
        return "There is insufficient baseline history for control limits. The black line is the nameplate rating."
    if status == "zero_variation":
        return "The baseline has no variation; check the meter or feed before interpreting the chart."
    flags = (chart.get("baseline_dependence") or {}).get("flags", [])
    caution = " Baseline dependence issues were detected; interpret limits cautiously." if flags else " This does not establish that the load pattern is unchanged."
    return f"No configured I-MR signal was detected. Historical control range{rng}." + caution


def review_headroom_svg(chart: dict, period_start: str, rating: float | None, review_ratio: float = 0.9) -> str:
    """Daily peak as a percent of the rated maximum, in the review page's style (light ground, inline attributes).

    Rating at 100% as a 2px ink line, the review line (review_ratio) dashed red, 70% dashed accent as a guide,
    this period shaded; days at or above the review line are red.
    """
    dates, vals = chart.get("dates") or [], chart.get("values") or []
    W, H, L, R, TOP, BOT = 900, 260, 52, 886, 10, 230
    if not dates or not rating or rating <= 0:
        return f'<svg viewBox="0 0 {W} 60" role="img" aria-label="No readings" style="width:100%;height:auto;display:block"><text x="{L}" y="34" font-size="12" fill="rgba(29,36,48,.6)">No readings to chart</text></svg>'
    pcts = [None if v is None else 100.0 * float(v) / float(rating) for v in vals]
    have = [p for p in pcts if p is not None]
    if not have:
        return review_headroom_svg({"dates": [], "values": []}, period_start, rating)
    review_pct = review_ratio * 100.0
    lo = min(min(have), 70.0) - 6.0
    hi = max(max(have), 100.0) + 6.0
    step = _nice_step(hi - lo)
    n = max(len(dates) - 1, 1)
    x = lambda i: L + (R - L) * i / n  # noqa: E731
    y = lambda v: TOP + (hi - v) / (hi - lo) * (BOT - TOP)  # noqa: E731
    ink = "rgba(29,36,48,"
    out = [f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="Daily peak as a percent of the rating" style="width:100%;height:auto;display:block;font-family:Lora,Georgia,serif">']
    annotations = []
    first = next((i for i, d in enumerate(dates) if d >= period_start), None)
    if first is not None:
        x0 = x(first) - (6 if first else 0)
        out.append(f'<rect x="{x0:.1f}" y="{TOP}" width="{max(x(len(dates) - 1) - x0 + 6, 4):.1f}" height="{BOT - TOP}" fill="rgba(182,130,53,.16)"/>')
    t = (lo // step + 1) * step
    while t < hi:
        out.append(f'<line x1="{L - 4}" x2="{L}" y1="{y(t):.1f}" y2="{y(t):.1f}" stroke="{ink}.25)"/>')
        out.append(f'<text x="{L - 8}" y="{y(t) + 4:.1f}" text-anchor="end" font-size="11" fill="{ink}.55)">{t:g}%</text>')
        t += step
    out.append(f'<line x1="{L - 4}" x2="{R + 4}" y1="{y(70):.1f}" y2="{y(70):.1f}" stroke="#b68235" stroke-width="1" stroke-dasharray="2 3" opacity=".9"/>')
    out.append(f'<line x1="{L - 4}" x2="{R + 4}" y1="{y(review_pct):.1f}" y2="{y(review_pct):.1f}" stroke="#D7263D" stroke-width="1.2" stroke-dasharray="5 4"/>')
    annotations.append(f'<text x="{L + 8}" y="{y(review_pct) + 14:.1f}" text-anchor="start" font-size="11" stroke="#f8f7f6" stroke-width="4" stroke-linejoin="round" paint-order="stroke" data-annotation="review" fill="#9e1428">review line {review_pct:g}%</text>')
    out.append(f'<line x1="{L - 4}" x2="{R + 4}" y1="{y(100):.1f}" y2="{y(100):.1f}" stroke="{ink}.85)" stroke-width="2"/>')
    annotations.append(f'<text x="{L + 8}" y="{y(100) - 6:.1f}" text-anchor="start" font-size="11" stroke="#f8f7f6" stroke-width="4" stroke-linejoin="round" paint-order="stroke" data-annotation="rating" fill="{ink}.75)">rating {rating:,.0f} = 100%</text>')
    pts = [(i, p) for i, p in enumerate(pcts) if p is not None]
    out.append('<path d="' + " ".join(("M" if k == 0 else "L") + f"{x(i):.1f} {y(p):.1f}" for k, (i, p) in enumerate(pts)) + f'" fill="none" stroke="{ink}.7)" stroke-width="1.4"/>')
    for i, p in pts:
        d = dates[i]
        if p >= review_pct:
            out.append(f'<circle cx="{x(i):.1f}" cy="{y(p):.1f}" r="3.8" fill="#D7263D"><title>{escape(d)}: {p:.0f}% of rating</title></circle>')
        elif first is not None and i >= first:
            out.append(f'<circle cx="{x(i):.1f}" cy="{y(p):.1f}" r="3.5" fill="#7d5411"><title>{escape(d)}: {p:.0f}% of rating</title></circle>')
        else:
            out.append(f'<circle cx="{x(i):.1f}" cy="{y(p):.1f}" r="2.4" fill="{ink}.6)"><title>{escape(d)}: {p:.0f}% of rating</title></circle>')
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    k = min(5, len(dates))
    idx = sorted({round(j * n / (k - 1)) for j in range(k)}) if k > 1 else [0]
    for j, i in enumerate(idx):
        d = dates[i]
        anchor = "start" if j == 0 else "end" if j == len(idx) - 1 else "middle"
        out.append(f'<text x="{x(i):.1f}" y="250" text-anchor="{anchor}" font-size="11" fill="{ink}.55)">{months[int(d[5:7]) - 1]} {int(d[8:10])}</text>')
    out.extend(annotations)
    out.append("</svg>")
    return "".join(out)


def review_headroom_caption(chart: dict, period_start: str, rating: float | None, review_ratio: float = 0.9) -> str:
    """One plain sentence under the headroom chart."""
    dates, vals = chart.get("dates") or [], chart.get("values") or []
    if not dates or not rating:
        return ""
    week = [(d, v) for d, v in zip(dates, vals) if d >= period_start and v is not None]
    over = sum(1 for _, v in week if v >= rating)
    near = sum(1 for _, v in week if v >= review_ratio * rating) - over
    peak = max((v for _, v in week), default=None)
    if peak is None:
        return "No readings this week."
    head = f"This week's highest day reached {100 * peak / rating:.0f}% of the rating."
    if over:
        return head + f" {over} day{'s' if over != 1 else ''} reached or passed the rating itself" + (f" and {near} more sat above the {review_ratio:.0%} review line." if near else ".")
    if near:
        return head + f" {near} day{'s' if near != 1 else ''} sat above the {review_ratio:.0%} review line, none reached the rating."
    return head + f" Every day stayed under the {review_ratio:.0%} review line."
