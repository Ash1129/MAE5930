# Handoff: Transformer Capacity Monitor — landing page (map home)

## Overview
A new skin for the home route `/` → `/periods/<id>/map` of the Transformer Capacity Monitor (Flask + Leaflet, `webapp/templates/map.html`). The map becomes full-bleed; a glass district panel floats left, a glass "Review needed" sidebar floats right, a collapsible run box lives in the top bar. Backend routes, data shapes, the approval rule and status colors are unchanged. The engineer must answer "is anything red, where, how many" in ten seconds, then zoom into a town, open a red case, decide.

## About the design files
Everything under `design/` is a **design reference built in HTML** (a streaming prototype format with `support.js`; it opens directly in a browser). It is not production code to paste in. The task is to **recreate the design inside the existing app** — a Jinja template rendered by Flask with vanilla JS and Leaflet 1.9.4 + leaflet.heat, which is the stack `webapp/templates/map.html` already uses. Keep that stack; no framework is needed. Open `design/Capacity Monitor Landing.dc.html` in a browser (serve the folder over HTTP so `data/` fetches work) and use its Tweaks panel (`scenario`, `frame`) to see every state.

## Fidelity
**High-fidelity.** Colors, type, sizes, radii, blur and copy are final. Recreate pixel-perfectly. The prototype's statuses and numbers are synthetic (hashed from transformer ids); real values come from the existing `points` context the route already builds.

## Where it goes in the codebase
- Replace the body of `webapp/templates/map.html`. It currently `extends base.html`; this page should **not** use `base.html`'s header/main shell (the map is the page). Either render it standalone or add a `{% block body %}` override in `base.html`.
- Context already provided by `period_map()` in `webapp/app.py`: `period`, `points`, `boundaries`, `periods`, `districts` (id, name, kind, bbox), `feeds` (present/modified per file), `default_end`, `playbook`, `dates`, `seasonal.monthly_factors`, `heat_default_date`, plus `reviewer_name` and `unacked_alerts` from the context processor.
- Heat data stays on `/api/heat/recorded?date=` and `/api/heat/seasonal?month=` (response `{loads: {id: [24 values]}, modeled, factor}`).
- "Run now" posts to `start_run` as today. Run progress: poll the existing status endpoint (`/api/status` returns `last_run` with status/step) every ~2s while running.
- Alerts dropdown reads the latest unacknowledged alert (headline / what happened / what to do fields already produced by `explain.py`).
- Finalize: disabled until every `review_needed` point has a `disposition`; backend still enforces with 409.
- Scheduler line: `/api/status` → `scheduler` (active, next run) and `last_run`.

## Screens / states
All are one page. Detailed geometry and component specs are in **SPEC.md** (sections: page shell, desktop geometry table, narrow/phone, type, components, copy rules, interactions). Summary:

1. **Normal** — full map, ~500 dots, districts panel, review sidebar, legend + status bottom-left, zoom + Satellite/Streets bottom-right.
2. **District selected** — map fits the district bbox (with panel padding), outside dots fade to 25%, row highlighted, sidebar filtered ("in City of Ithaca"), heat strip appears between the panels, "Hotspots now" section at the top of the sidebar, heat layer under dots.
3. **Dot popup** — 300px glass card 18px above the dot: id, name · town, status chip, Rated maximum, Period peak, Cpk (with interval), Projected peak + ESTIMATE, Rule, Decision, "Open full review" → `/periods/<id>/transformers/<tid>`.
4. **Run in progress** — pill shows spinner + "Running, step n of 15" + progress track; map dimmed `rgba(5,8,12,.32)`; panels remain usable.
5. **Run failed** — red pill with headline ("Run failed: readings.csv is missing"), "See alert" opens the bell dropdown, dismiss ×.
6. **First launch** — boundaries only; sidebar: "No period has been run yet" + "Run the first period"; legend counts 0.
7. **Run box expanded** — hover/focus on the pill: 340px card with date (default yesterday), "Run now", four feed chips.
8. **Alerts dropdown** — 320px card: "Latest alert", time, headline, WHAT HAPPENED / WHAT TO DO rows, "All alerts (n)" → `/alerts`.
9. **Tablet <1000px** — districts become a chip row at top 76; sidebar becomes a bottom sheet (140 collapsed / 62% open); heat strip full width; run pill becomes "Run".
10. **Phone <600px** — plus: period selector and reviewer hidden (live in Setup), Setup icon-only, status line hidden.

`design/States Canvas.dc.html` shows all ten side by side with callouts.

## Design tokens
`tokens.css` is copy-ready. Key values:
- Status (fixed): within limits `#1B7F4B`, review needed `#D7263D`, modeled/warning `#F4B400`, info `#1F5FA8`.
- Ink on glass `#1D2430` at 90% / 75% / 60%; hairline `rgba(29,36,48,.12)`.
- Control accent `#b68235`, accent text `#7d5411`, hover tint 12%, pressed 22%. Buttons are **outlined**, never filled.
- Glass: `rgba(255,255,255,.62)` (`.72` for popups/dropdowns), `backdrop-filter: blur(24px) saturate(1.5)` (28 for cards), border `1px solid rgba(255,255,255,.35)`, `inset 0 1px 0 rgba(255,255,255,.65)` highlight, shadow `0 10px 30px rgba(0,0,0,.25)`. Hover → 68%.
- Radii: panels 20, top bar 16, controls/rows 12, pills 999.
- Type: Cormorant Garamond 600 for titles (21 / 20 / 22 clock); Lora 400 for everything else (14 / 13 / 12 / 11 / 10 micro uppercase .12em); `font-variant-numeric: tabular-nums` globally. Google Fonts: `Cormorant+Garamond:wght@400;600`, `Lora:wght@400;600`.
- Dots: red 11px / green 8px, 2px white ring, .95 opacity; outside district .25.
- Layout: gutter 16, bar 52 h at top 12, panels at top 80, districts 220 w, sidebar 300 w, rows 44 h.
- Motion: only 150–250ms background/height fades; honor `prefers-reduced-motion`.

## Interactions & behavior
See SPEC.md "Interactions". Essentials: district select → fitBounds(bbox, padding) + fade + filter + fetch heat; dot/row click → setView(≥13) + popup; map click closes popup/dropdowns; run pill expands on hover and focus-within, collapses on leave; Play steps the hour every 700ms and rolls date/month; segmented controls carry an inset accent ring on the active option; keyboard focus = 2px accent ring; all rows are `<button>`s ≥44px.

## State
`district`, `popup` (point id), `mode` recorded|seasonal, `metric` util|load, `dateIdx`, `month`, `hour`, `playing`, `base` sat|streets, `runOpen`, `running`+`runStep`, `runFailed`, `alertsOpen`, `sheetOpen` (narrow), `firstLaunch` (derived: no period).

## Copy rules
"review needed" / "within limits" only; every figure carries `kVA` or `% of rating`; alerts shown as three lines (headline / what happened / what to do); modeled and projected values labeled where they appear (MODELED badge, `estimate` micro-label).

## Assets
- Icons: Lucide (bell, settings, play, pause, plus, minus, arrow-right, x) as inline SVG, 1.8–2px stroke, currentColor.
- Tiles: Esri World Imagery + Reference labels (satellite), OpenStreetMap (streets) — same URLs as the current template.
- `design/data/boundaries.geojson` and `design/data/assets.csv` are copies of the repo feeds used by the prototype; the app already has them.
- Design system stylesheet (`design/_ds/.../styles.css`) supplies the font import, accent ramp and `.btn`/`.seg`/`.input` classes referenced by the prototype; `tokens.css` restates what the page needs.

## Files
- `README.md` — this file.
- `SPEC.md` — geometry tables, component specs, copy rules, interactions.
- `tokens.css` — CSS variables and glass/chip/button helper classes.
- `design/Capacity Monitor Landing.dc.html` — the interactive prototype (all states via Tweaks; logic in the inline script shows the exact behavior).
- `design/States Canvas.dc.html` — ten artboards with callouts.
- `design/Component Sheet.dc.html` — glass panel, rows, chips, badges, dots, popup, sliders, tokens.
- `design/support.js`, `design/_ds/`, `design/data/` — runtime, stylesheet and data the prototypes load.

## Suggested prompt for Claude Code
"Read design_handoff_landing_page/README.md and SPEC.md. Rebuild webapp/templates/map.html to match design/Capacity Monitor Landing.dc.html exactly, using the existing Flask context, Leaflet and the /api/heat endpoints. Keep routes, data and the finalize rule unchanged. Then run the tests."
