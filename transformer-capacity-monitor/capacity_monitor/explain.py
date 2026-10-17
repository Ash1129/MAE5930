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
