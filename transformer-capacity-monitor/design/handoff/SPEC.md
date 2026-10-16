# Transformer Capacity Monitor — landing page handoff

Framework-agnostic. Routes, data shapes and the approval rule are unchanged from the brief; this is a skin over them.
Tokens: `tokens.css`. Live reference: `Capacity Monitor Landing.dc.html` (switch state with the Tweaks panel). Artboards: `States Canvas.dc.html`. Parts: `Component Sheet.dc.html`.

## Page shell

- The map fills the viewport (`position:absolute; inset:0`). Every panel is absolutely positioned over it; nothing pushes the map.
- Page ground under tiles: `#0b0f14`. Dot layer above boundaries above heat layer above tiles.
- Boundaries: white 1.5px dashed `5 4`, opacity .85, fill .03. Selected district 2.5px; others drop to opacity .3.
- Fit padding when framing the county or a district: desktop `top-left 260×80, bottom-right 340×60` so the panels never cover dots; narrow `20×130 / 20×110`.

## Desktop geometry (≥1000px, reference 1440×900)

| Element | Box |
|---|---|
| Top bar | top 12, left/right 16, h 52, radius 16, padding 0 8 0 18 |
| Districts panel | top 80, left 16, w 220, max-h calc(100% − 160), radius 20 |
| Heat strip | top 80, left 252, right 332, radius 20 (district selected only) |
| Review sidebar | top 80, right 16, bottom 16, w 300, radius 20 |
| Legend + status | bottom 16, left 16, radius 14 |
| Map controls | bottom 16, right 16, zoom stack 36×36 ×2, base toggle 32 h |
| Run card | 340 w, 40px below the pill, left-aligned to it |
| Alerts card | 320 w, 44px below the bell, right-aligned |
| Popup | 300 w, centered on the dot, bottom edge 18px above it |

## Narrow (<1000px) and phone (<600px)

- Districts → horizontal chip row, top 76, 36px pills, scrolls, no scrollbar.
- Review sidebar → bottom sheet, full width, radius 20 20 0 0, 140px collapsed (220 on first launch), 62% open; drag handle 40×4 at 25% ink; tapping the heading toggles.
- Heat strip → full width at top 124.
- Legend and map controls sit 12px above the collapsed sheet.
- Run pill → "Run"; period selector and reviewer hide; Setup is icon only (<600 also hides the status line).

## Type

- Titles: Cormorant Garamond 600, 21px (panel titles, brand, popup id), 20px (run card, alert card), 22px clock.
- Everything else: Lora 400, 14 body, 13 rows and sliders, 12 captions, 11 chips, 10 micro-labels (uppercase, .12em). Weight 600 only for transformer ids and counts.
- `font-variant-numeric: tabular-nums` on the whole page.
- Ink on glass: #1D2430 at 90% primary, 75% reasons, 60% muted. Decision chips #1F5FA8; red count text #b01d30 (#ffb3bd on the selected dark row).

## Components

**Glass panel** — `.glass` in tokens.css. Hover brightens to 68%; no motion other than that 200ms fade. Cards that sit over other content (popup, run card, alerts) use `.glass-card` (72%, blur 28).

**District row** — button, 44 h, radius 12, padding 0 10. Name 14 / kind·count 11 muted. Red count right-aligned: 7px red dot + number; omitted when zero. Selected: ink 90% fill, white text. Hover: ink 7%. Focus: 2px accent ring inset.

**Review row** — 9px red dot with 2px white ring, id 600 14, "name · town" 12 muted (ellipsis), reason 12 at 75% ink, optional decision chip (blue outline). A 36px arrow cell on the right links to the full review. Row hover ink 5%; the row whose popup is open tints accent 12%.

**Status chips** — outline only, 11px, pill: green "Within limits", red "Review needed", blue "Approve by …" / "Request changes by …". Feed chips: 6px dot + "readings.csv · present/missing".

**MODELED badge** — amber #F4B400 fill, ink text, 10px uppercase 600. Shown on the heat strip and the Hotspots heading whenever the seasonal model is on. RECORDED is the green outline twin. Projected peak always carries the `estimate` micro-label.

**Dots** — circle markers: red r 5.5 (11px), green r 4 (8px), 2px white stroke, fill .95. Outside the selected district: fill .25, stroke .3. Tooltip: `T-CAR-006 · review needed`.

**Popup** — id, "name · town", status chip, close. Grid of label/value rows: Rated maximum, Period peak "84.2 kVA (84% of rating)", Cpk "1.12 (0.92 to 1.32)" or "not calculated: signal", Projected peak + estimate, Rule "Rule 7 · reason", Decision "none recorded". Full-width outlined "Open full review".

**Run box** — pill: 32 h, accent outline, play icon, "Run a monitoring period". Expands on hover / focus-within; collapses on pointer leave / focus leaving. States: running (spinner, "Running, step n of 15", 80px progress track; map overlay `--map-dim`), failed (red outline pill, headline, "See alert" opens the bell dropdown, dismiss).

**Heat strip** — district name (Cormorant 20), two segmented controls (active option: accent text + 1px inset accent ring), badge, clock right-aligned. Slider rows: 48px micro-label, range input (accent-color), live label ("18:00, evening peak hours" / "January, ×1.35 of recorded level" / "2026-10-15 (7 of 7 recorded days)"), Play/Pause outlined. Play advances one hour every 700ms and rolls the date (recorded) or month (seasonal).

**Hotspots now** — appears at the top of the review sidebar when a district is selected: eight rows, id + name, value ("82% of rating" or "61.3 kVA"), 4px bar colored green <70%, amber <90%, red ≥90%.

**Finalize** — outlined primary, disabled (45% opacity) while any red case lacks a decision; the reason line beneath reads "n red cases still need a decision before the report can be finalized". Never hidden.

## Copy rules

- "review needed" / "within limits"; never pass/fail.
- Every figure carries kVA or "% of rating".
- Alert dropdown shows headline, WHAT HAPPENED, WHAT TO DO as three lines.
- Anything modeled or projected is labeled where it appears.

## Interactions

- District select: fit bbox, fade others, filter list, show heat strip + Hotspots, fetch `/api/heat/recorded?date=` or `/api/heat/seasonal?month=`.
- Dot click / review row click: pan to dot (zoom ≥13), open popup, highlight row. Map click closes popup and dropdowns.
- Period selector: navigate to `/periods/<id>/map`.
- Reduced motion: all transitions and the spinner stop.
