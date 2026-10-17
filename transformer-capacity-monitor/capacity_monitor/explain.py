"""Plain-language explanations for alerts and run problems. Fixed rules, no AI.

Each known failure pattern maps to: what happened, what it means, and what to do next.
Anything unrecognized gets a generic explanation plus the technical text under details.
"""

from __future__ import annotations

import re

from . import config

STEP_NAMES = dict(config.STEPS)

# (regex, title, meaning, action). {groups} from the regex can be used in the text.
_RULES = [
    (
        re.compile(r"Boundary feed is for a different reporting period \(valid (?P<from>[\d-]+) to (?P<to>[\d-]+), run period ends (?P<end>[\d-]+)\)"),
        "The boundary map file is for the wrong period",
        "The town and village boundary file in data/feeds is marked valid from {from} to {to}, but this run covers the period ending {end}. The tool will not use boundaries from another period, so it stopped before any analysis.",
        "Get the current boundary file from the county GIS team, save it as data/feeds/boundaries.geojson, then press Run now for the period ending {end}.",
    ),
    (
        re.compile(r"(?P<tid>T-[A-Z0-9-]+): no rated maximum load on the asset record"),
        "A transformer has no rated maximum",
        "Transformer {tid} is in the asset file without a rated maximum load, so the tool cannot tell how much capacity it has. The run stopped so a partial report is not published.",
        "Add the nameplate rating for {tid} to data/feeds/assets.csv (column rated_max), then press Run now again.",
    ),
    (
        re.compile(r"(?P<what>[A-Za-z -]+) feed is missing: (?P<file>\S+) not found"),
        "An input file is missing",
        "The {what} file ({file}) was not in data/feeds when the run started, so the run stopped before any analysis.",
        "Copy the latest {file} export into data/feeds, then press Run now again.",
    ),
    (
        re.compile(r"(?P<tid>T-[A-Z0-9-]+): no readings for (?P<n>\d+) of (?P<total>\d+) period days \(first missing (?P<day>[\d-]+)\)"),
        "Readings are incomplete for the period",
        "Transformer {tid} has no load readings for {n} of the {total} days in the period (first missing day {day}). The tool needs every day to judge the week, so it stopped.",
        "Check that the meter export covers the whole period and re-export readings.csv, then press Run now again.",
    ),
    (
        re.compile(r"(?P<tid>T-[A-Z0-9-]+): reading unit .* does not match rating unit"),
        "Readings and ratings use different units",
        "Transformer {tid} has readings in one unit and a rating in another, so they cannot be compared safely.",
        "Fix the unit column in readings.csv or assets.csv for {tid} so both match (usually kVA), then press Run now again.",
    ),
    (
        re.compile(r"Heat-pump forecast version '(?P<v>[^']+)' \(playbook\) not found in feed"),
        "The approved forecast version is not in the forecast file",
        "The playbook says to use heat-pump forecast version {v}, but the forecast file does not contain that version.",
        "Either add version {v} to data/feeds/heat_pump_forecast.csv or update forecast.version in rules/playbook.json to the version the planning team approved, then press Run now again.",
    ),
    (
        re.compile(r"No transformer asset records are in effect"),
        "The asset file has no transformers in effect for this period",
        "Every row in assets.csv is either missing or dated outside this period, so there is nothing to monitor.",
        "Check the effective_from and effective_to dates in data/feeds/assets.csv, then press Run now again.",
    ),
    (
        re.compile(r"Airflow DAG run (?P<run>\S+) failed in task (?P<task>\S+)"),
        "A scheduled run stopped",
        "The scheduler's run {run} stopped at task {task}. The reason is in the matching alert for the same run.",
        "Open the run from the link to see which step failed and what to fix; after fixing the input, press Run now for that period.",
    ),
]

_WARNING_LOCATION = re.compile(r"(?P<tid>T-[A-Z0-9-]+): location falls in (?P<n>\d+) area\(s\) \[(?P<areas>[^\]]*)\]; using (?P<method>\w+) = (?P<area>\S+)")
_WARNING_DECLARED = re.compile(r"(?P<tid>T-[A-Z0-9-]+): declared area (?P<declared>\S+) but its location falls in \[(?P<areas>[^\]]*)\]; using (?P<method>\w+) = (?P<area>\S+)")
_STEP_IN_MESSAGE = re.compile(r"failed at step (?P<step>\d+)")


def explain_problem(text: str) -> dict:
    """One problem line -> {title, meaning, action, raw}."""
    for pattern, title, meaning, action in _RULES:
        m = pattern.search(text)
        if m:
            g = {k: (v or "") for k, v in m.groupdict().items()}
            return {"title": title, "meaning": meaning.format(**g), "action": action.format(**g), "raw": text}
    return {"title": "The run hit a problem", "meaning": text, "action": "Open the run to see the step it stopped at; fix the input it names, then press Run now again.", "raw": text}


def explain_note(text: str) -> str | None:
    """Non-blocking warnings -> a one-line plain note, or None if unrecognized."""
    m = _WARNING_LOCATION.search(text)
    if m:
        return f"{m['tid']} sits where {m['n']} boundary areas overlap (for example a village inside its town); its forecast uses the area on its asset record, {m['area']}. Nothing to fix."
    m = _WARNING_DECLARED.search(text)
    if m:
        return f"{m['tid']} is recorded in area {m['declared']} but its map location is in {m['areas']}; the tool used {m['area']}. Check the asset record's area or coordinates."
    if "instruction-like" in text or "blocked term" in text:
        return "A text field in a feed contained instruction-like or blocked wording; it was ignored and replaced with a placeholder. Nothing was acted on."
    if "unknown transformer id" in text:
        return "Some readings belong to transformer ids that are not in the asset file; they were ignored. Add those transformers to assets.csv if they should be monitored."
    return None


def explain_alert(message: str, step: int | None = None) -> dict:
    """An alert message (possibly several lines) -> headline, meaning, action, notes and details."""
    lines = [ln.strip() for ln in (message or "").splitlines() if ln.strip()]
    problems, notes = [], []
    for ln in lines:
        if ln.startswith("warning:"):
            note = explain_note(ln[len("warning:"):].strip())
            notes.append(note or ln[len("warning:"):].strip())
        else:
            problems.append(ln)
    # the first line of a run-failure alert is the summary ("Run X failed at step 7: ..."); explain the specific problems
    specific = [p for p in problems[1:]] if len(problems) > 1 and problems[0].startswith("Run ") else problems
    explained = [explain_problem(p) for p in specific] or [explain_problem(problems[0] if problems else message)]
    if step is None and problems:
        m = _STEP_IN_MESSAGE.search(problems[0])
        if m:
            step = int(m["step"])
    first = explained[0]
    return {
        "title": first["title"] if len(explained) == 1 else f"{first['title']} (and {len(explained) - 1} more)",
        "meaning": first["meaning"],
        "action": first["action"],
        "others": explained[1:],
        "notes": notes,
        "step": step,
        "step_name": STEP_NAMES.get(step, "") if step else "",
        "details": message,
    }



def summarize_transformer(r: dict) -> str:
    """One or two plain sentences about a transformer result, from fixed templates (fallback when AI is off)."""
    c = r.get("capacity", {})
    unit = r.get("unit") or ""
    rating = r.get("rated_max")
    pk = c.get("period_peak_ratio")
    fc = c.get("forecast_ratio")
    rule = str((r.get("decision") or {}).get("rule", ""))
    stab = r.get("stability")
    peak_txt = f"this week's peak reached {pk:.0%} of its {rating:,.0f} {unit} rating" if pk is not None and rating else "no peak was recorded this week"
    if r.get("status") != "review_needed":
        return f"Within limits: {peak_txt}, the load pattern is stable and the margin to the rating is comfortable."
    if stab == "signal":
        sig = (r.get("chart") or {}).get("signals") or []
        when = f" on {sig[0]['date']}" if sig else ""
        return f"The load pattern changed{when}, so headroom is not calculated until someone checks why; {peak_txt}."
    if stab == "insufficient_history":
        return f"Not enough history yet to judge this transformer; {peak_txt}."
    if stab == "zero_variation":
        return "Readings show no variation at all, which usually means a meter or feed problem."
    if rule == "9" and fc is not None:
        return f"Fine today ({peak_txt}), but projected heat-pump growth would push the peak to {fc:.0%} of rating."
    if rule in ("7", "8") and c.get("cpk") is not None:
        lo = c.get("cpk_ci_low")
        return f"Headroom is thin or uncertain: Cpk {c['cpk']:.2f}" + (f" (could be as low as {lo:.2f})" if lo is not None else "") + f"; {peak_txt}."
    if rule == "4":
        return f"A reading this week reached or exceeded the rated maximum; {peak_txt}."
    return f"Flagged for review ({(r.get('decision') or {}).get('reason', 'see rule')}); {peak_txt}."


def _horizon_phrase(assumptions: dict) -> str:
    m = re.search(r"(\d{4})", str(assumptions.get("horizon") or ""))
    return f"winter {m.group(1)}" if m else "the forecast winter"


def why_flagged(r: dict, playbook: dict | None = None) -> dict:
    """Headline, what happened and what to do for the review page, from fixed templates keyed on the decision rule."""
    pb = playbook or config.load_playbook()
    cpk_line = pb["capability"]["cpk_review_below"]
    c = r.get("capacity") or {}
    ch = r.get("chart") or {}
    unit = r.get("unit") or "kVA"
    rating = r.get("rated_max")
    pk, pkr, fc, fcr = c.get("period_peak"), c.get("period_peak_ratio"), c.get("projected_peak"), c.get("forecast_ratio")
    rule = str((r.get("decision") or {}).get("rule", ""))
    area = r.get("area_name") or "its area"
    if area.split(" ")[0] in ("Town", "City", "Village"):
        area = "the " + area
    peak = (f"This week's highest load was {pk:,.1f} {unit}, {pkr:.0%} of the {rating:,.0f} {unit} rating." if pk is not None and pkr is not None and rating
            else "No peak was recorded this week.")
    if r.get("status") != "review_needed":
        return {"headline": "Within limits this week", "meaning": peak + " The load pattern is steady and the margin to the rating is comfortable.",
                "action": "Nothing to decide. It is listed for reference."}
    if rule == "1":
        return {"headline": "Not enough steady history to judge it yet",
                "meaning": f"Only {ch.get('n_baseline', 0)} days of steady history are available; the tool needs {ch.get('min_history_points', 20)} before it sets a normal range. " + peak,
                "action": "Check whether the readings started recently or have gaps. If the load looks reasonable, agree and keep it on watch."}
    if rule == "2":
        sig = [s for s in ch.get("signals") or [] if s.get("in_period")] or list(ch.get("signals") or [])
        when = f" on {sig[0]['date']}" if sig else ""
        rng = f" ({ch['lcl']:,.1f} to {ch['ucl']:,.1f} {unit})" if ch.get("lcl") is not None and ch.get("ucl") is not None else ""
        return {"headline": f"The load pattern changed{when}",
                "meaning": f"The daily peak moved outside its normal range from history{rng}, so the room left today is not worked out until the change is explained. " + peak,
                "action": "Look at the chart and the hourly readings around that date for a new connection, a switching event or a meter problem, and note what you find."}
    if rule == "3":
        return {"headline": "The readings don't change at all",
                "meaning": "Every daily peak is the same value, which usually means a stuck meter or a feed problem rather than real load.",
                "action": "Check the meter and the readings export before trusting these numbers. \"Something needs fixing first\" fits if the feed is wrong."}
    if rule == "4":
        return {"headline": "A reading this week reached the rating",
                "meaning": peak + " At least one reading was at or above the rated maximum.",
                "action": "Check whether it was a one-off, such as a switching event, or sustained load. Plan relief if it is sustained."}
    if rule == "5":
        return {"headline": "The room left today could not be worked out",
                "meaning": (c.get("note") or "There was not enough data to calculate headroom.") + " " + peak,
                "action": "Check the readings for gaps, then judge from the chart and the peak."}
    if rule == "6":
        return {"headline": "The headroom figure can't be trusted for this one",
                "meaning": "The room-left figure assumes daily peaks that are independent and roughly bell-shaped; here " + "; ".join(c.get("assumption_flags") or ["they are not"]) + ". " + peak,
                "action": "Judge from the chart and this week's peak rather than the Cpk number."}
    if rule == "7" and c.get("cpk") is not None:
        return {"headline": "Not much room left today",
                "meaning": f"Daily peaks run close to the {rating:,.0f} {unit} rating for how much they vary (Cpk {c['cpk']:.2f}, review line {cpk_line}). " + peak,
                "action": "Decide whether to plan an upgrade, move load to a neighbour, or watch it."}
    if rule == "8" and c.get("cpk") is not None:
        lo = c.get("cpk_ci_low")
        return {"headline": "The room left today is uncertain",
                "meaning": f"Cpk is {c['cpk']:.2f}, but with {c.get('n', 0)} days of data it could be as low as {lo:.2f}, under the {cpk_line} review line. " + peak,
                "action": "Watch it for a few more weeks, or agree and plan a check."}
    if rule == "9" and fc is not None and fcr is not None:
        when = _horizon_phrase((r.get("projection") or {}).get("assumptions") or {})
        verb = "reach its rating" if fcr >= 1 else "come close to its rating"
        under = "well under" if (pkr or 0) < 0.75 else "under"
        return {"headline": f"Fine today, but expected to {verb} by {when}",
                "meaning": f"This week's highest load was {pk:,.1f} {unit}, {under} the {rating:,.0f} {unit} rating. Adding the expected heat-pump growth for {area} brings the winter peak to about {fc:,.1f} {unit} ({fcr:.0%} of rating).",
                "action": "Decide whether to plan an upgrade or watch it." + (" Today's load pattern is steady, so this is a planning call, not an urgent one." if r.get("stability") == "stable" else "")}
    if rule == "10":
        reason = ((r.get("projection") or {}).get("assumptions") or {}).get("reason_not_projected") or "no forecast row for its area"
        return {"headline": "No winter estimate for this transformer",
                "meaning": f"The heat-pump forecast could not be applied ({reason}), so the tool cannot tell whether winter load will fit. " + peak,
                "action": "Add the forecast row for its area to data/feeds/heat_pump_forecast.csv, then rerun the period."}
    return {"headline": "Flagged for review", "meaning": ((r.get("decision") or {}).get("reason") or "A rule flagged it.") + ". " + peak,
            "action": "Check the chart and the numbers below, then record a decision."}
