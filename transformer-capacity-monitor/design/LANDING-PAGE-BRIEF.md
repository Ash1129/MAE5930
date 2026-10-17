# Design brief: Transformer Capacity Monitor, landing page

For Claude Design. This document says what the app does, what the landing page must do, and the visual
direction. Everything the page needs from the backend already exists; the design is a new skin over working
routes and data, not a new product.

## 1. What the app is, in one paragraph

A monitoring tool for the grid-planning engineer at a small electric utility in Tompkins County, New York.
Three mornings a week it reads hourly load on about 500 neighborhood transformers, checks each one's daily
peak on a control chart to see whether its load pattern has changed, measures how much headroom is left below
the transformer's rated maximum, adds the expected heat-pump growth for its town, and sorts every transformer
into **within limits** (green) or **review needed** (red). The engineer reviews each red case, records a
decision, and signs off a weekly report. No AI makes decisions; the tool never changes any equipment.

## 2. Who uses it and what they want to do in the first ten seconds

- **The grid-planning engineer** (primary). Opens the app on a Monday morning. Wants to see, at a glance:
  Is anything red? Where? How many? Then: zoom into a town, open a red case, decide, move on.
- **Their manager** (occasional). Wants the same picture without touching anything.
- Both are comfortable with maps and numbers but are not software people. No jargon on the landing page.

## 3. The landing page: the vision

> The user opens the app and sees the full map of Tompkins County, full screen. On the left, a liquid-glass
> panel lists the district names. On the right, a narrow sidebar lists the issues and the transformers that
> need review. Across the top, a small box for running a monitoring period that collapses out of the way and
> expands on hover. Aesthetic, calm, and immediate.

### 3.1 Layout (desktop first, 1440 x 900 reference)

```
+--------------------------------------------------------------------------------+
|  [top bar: app name . period selector . collapsed "Run a period" pill . Alerts . Setup . reviewer]  |
|                                                                                |
|  +-----------+                                              +----------------+ |
|  | DISTRICTS |            FULL-BLEED SATELLITE MAP          | REVIEW NEEDED  | |
|  | glass     |            green / red transformer dots      | narrow sidebar | |
|  | panel     |            white dashed town boundaries      | glass, scroll  | |
|  |           |                                              |                | |
|  | Whole     |                                              | T-CAR-006  red | |
|  |  county   |                                              | T-DAN-010  red | |
|  | Ithaca 20 |                                              | ...            | |
|  | Caroline  |                                              |                | |
|  | ...       |                                              | [Finalize]     | |
|  +-----------+                                              +----------------+ |
|                                                                                |
|  [bottom-left: legend . last run time . scheduler state]   [bottom-right: map controls, layer toggle] |
+--------------------------------------------------------------------------------+
```

- **The map is the page.** It fills the viewport edge to edge. Panels float over it; nothing pushes it around.
- **Left panel, districts.** A liquid-glass card (translucent, frosted, soft inner highlight, 1px hairline
  border, large radius) listing: "Whole county" then the 12 towns and villages, alphabetically. Each row:
  name, a small count of red cases (or nothing if none), and the kind (city / town / village) in muted text.
  Selecting a row zooms the map to that district, dims the other districts, and (see 3.3) reveals the
  heat controls. Width about 220 px. Rows are generous (44 px) and keyboard-focusable.
- **Right sidebar, review needed.** A narrow glass sidebar (about 300 px) with a count header
  ("Review needed 97") and a scrollable list of red transformers: id in bold, name and town in muted text,
  one line of plain-English reason, a status chip if a decision was already recorded. Clicking a row pans
  the map to the dot and opens its popup; a small arrow opens the full review page. At the bottom, a
  "Finalize report" control that is disabled with a reason until every red case has a decision. When a
  district is selected the list filters to that district and the header says so.
- **Top bar, collapsible run box.** A slim bar: app name on the left, then a pill that reads
  "Run a monitoring period" and, on hover or focus, expands into a small glass card with a date field
  (default yesterday), a "Run now" button, and four tiny status chips for the input files (present /
  missing). Collapses when the pointer leaves. Also in the bar: period selector (which week is shown),
  an Alerts bell with a count, Setup, and the reviewer's name.
- **Map furniture.** Zoom buttons and the Satellite / Streets toggle bottom-right, small and glass.
  Legend bottom-left: green dot "within limits", red dot "review needed". A one-line status next to it:
  "Last run Mon 06:02 . next Wed 06:00 . scheduler active".

### 3.2 States the design must cover

1. **Normal.** Map with 500 dots (about 400 green, 100 red). Panels in resting state.
2. **District selected.** Map zoomed to the district; dots outside it faded; left row highlighted; right
   list filtered; heat controls visible (3.3).
3. **Dot popup.** A small card anchored to the dot: id, name, town, status chip, rated maximum, period peak
   as a percent of rating, Cpk with its interval, projected peak as a percent, the rule that flagged it, the
   recorded decision if any, and an "Open full review" button.
4. **Run in progress.** After "Run now", the top pill shows a progress state ("Running, step 8 of 15") and
   the map dims slightly until the new results load. A failure turns the pill red with a short headline and
   a link to the alert.
5. **Alerts present.** The bell shows a count; the alerts page itself is a separate, simpler screen
   (not part of this brief) but the bell's dropdown shows the latest alert's headline and "What to do".
6. **No period yet** (first launch). The map shows boundaries only, the right sidebar says "No period has
   been run yet" with a single primary action "Run the first period".
7. **Narrow screens** (tablet 768 and phone 390). Panels become bottom sheets: the district list becomes a
   horizontal chip row above the map; the review list becomes a swipe-up sheet; the run box becomes a
   button in the bar that opens a sheet.

### 3.3 District heat view (already built; needs its visual home)

When a district is selected, a compact control strip appears over the top of the map (inside a glass
card): Recorded vs Seasonal model; Utilization vs Load; a Date slider (recorded days), a Month slider
(seasonal model) and an Hour slider, each with a live label ("18:00, evening peak hours",
"January, x1.35 of recorded level"); a Play button. The map shows a heat layer under the dots. The right
sidebar gains a "Hotspots now" section listing the top eight transformers at that hour with a small bar.
The Seasonal model view carries a visible "MODELED" badge because it is an estimate, not measured data.

## 4. Visual direction

- **Mood.** Calm control room. Dark satellite imagery as the ground; light glass panels floating on it;
  one accent used sparingly. Nothing decorative that competes with the dots.
- **Liquid glass.** Panels: background white at 55-65% with backdrop blur 20-30 px and saturation boost,
  1 px border white at 35%, inner top highlight, radius 20-24 px, soft shadow (0 10 30 rgba(0,0,0,.25)).
  On hover a panel brightens slightly; nothing bounces. Respect reduced-motion.
- **Color.** Status colors are fixed and must stay: within limits green #1B7F4B, review needed red #D7263D,
  modeled/warning amber #F4B400, info blue #1F5FA8. The accent for controls can be the info blue or a
  restrained slate. Text on glass: near-black #1D2430 at 90% for primary, 60% for muted.
- **Type.** One humanist sans for everything (Inter, SF, or similar); tabular numerals for all figures;
  sizes 13/14 body, 12 captions, 20-22 panel titles. Uppercase micro-labels with letter-spacing for
  "What happened / What to do" style rows.
- **Dots.** Red dots slightly larger than green (11 vs 8 px), white 2 px ring, 95% opacity; 25% opacity
  when outside the selected district. Dense areas must stay readable at county zoom: consider a light
  cluster treatment only when more than 30 dots overlap.
- **Icons.** Minimal line icons; no emoji.

## 5. Content rules (copy)

- Say "review needed" and "within limits", never "fail/pass".
- Every number carries its unit or "% of rating". Example: "70.5 kVA (70% of rating)".
- Explanations are already written in plain English by the backend (headline, what happened, what to do);
  the design shows them as three short lines, not a paragraph.
- Anything estimated (seasonal model, projected peak) is labeled as such where it appears.

## 6. What the design must not change

- Routes and data stay as they are: `/` (map, home), `/periods/<id>/map`, `/periods/<id>` (period page),
  `/periods/<id>/transformers/<tid>` (full review page), `/dashboard`, `/alerts`, `/setup`,
  `/api/heat/recorded?date=`, `/api/heat/seasonal?month=`.
- The approval rule: the report cannot be finalized until every red case has a decision; the backend
  enforces it. The design shows this state honestly (disabled control with a reason), never hides it.
- The distinction between recorded data and the seasonal model.
- Status colors and their meaning.

## 7. Data available to the page (shapes the design can rely on)

Per transformer (one dot): `id`, `name`, `area` (district id), `area_name`, `lat`, `lon`, `status`
(within_limits | review_needed), `stability` (stable | signal | insufficient_history | zero_variation),
`rating` + `unit`, `period_peak`, `period_peak_ratio`, `cpk`, `cpk_ci_low`, `cpk_ci_high`,
`projected_peak`, `forecast_ratio`, `rule`, `reason` (plain English), `signals[]`, `assumption_flags[]`,
`disposition` (text or null), `cls` (residential | commercial | institutional | mixed), `url`.

Per district: `id`, `name`, `kind`, `bbox`, counts of transformers and red cases.

Period: `period_id` (end date), `status` (draft | final), summary counts, generated time, run id.

Scheduler: active/paused, next run, last run and its state, failed runs in the last few.

Feeds: four files with present/missing and modified time.

## 8. Deliverables wanted from the design

1. Landing page, desktop, in states 1, 2, 3 and 4 above.
2. The collapsed and expanded top run box.
3. Tablet and phone adaptations (state 7).
4. A small component sheet: glass panel, district row, review row, status chips, dot styles, popup card,
   slider row with live label, MODELED badge.
5. Design tokens (colors, radii, blur, shadows, type scale) in a form a developer can copy into CSS.

## 9. Reference

The current working version (plain Flask + Leaflet, satellite base map, district panel on the left, review
list on the right, run form above the map) is in the repository at
`github.com/Ash1129/MAE5930/tree/main/transformer-capacity-monitor`, file `webapp/templates/map.html`.
Screens: the Map page, the full review page with the control chart, the alerts page with plain-language
explanations. All data in the repo is synthetic.
