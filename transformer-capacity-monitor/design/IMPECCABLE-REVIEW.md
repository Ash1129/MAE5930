# Impeccable interface review and refinement

Review of the existing Flask app, starting at 6053642. This is a refinement of the existing
serif/brass interface, not a redesign. Statistics, thresholds, saved analysis and review actions
are outside this pass. Used [Impeccable 4.6.0](https://github.com/pbakaus/impeccable), its official
SKILL.md and audit/polish/craft-floor references, downloaded to a temporary toolkit checkout.
The toolkit is not installed globally and no automatic design hooks were enabled.

## Implementation integrity verdict

The interface has a coherent, product-specific identity and working review workflow. The main
issues are accessibility, responsive compression and inconsistency between separate page shells,
not lack of a new visual concept. Preserve the county identity, map, pie summaries and data semantics.

## Audit health (provisional code-review score)

| Dimension | Score / 4 | Evidence and limit |
|---|---|---|
| Accessibility | 2 | Labels, focus, skip links, larger controls and tutorial focus containment improved; no complete screen-reader/contrast certification. |
| Performance | 3 | Fonts now served locally with swap; hidden-tab thermal playback pauses; external map/3D dependencies remain. |
| Theming | 2 | Shared secondary-text tokens and legible light chart paper in dark mode; remaining hard-coded chart/status colors need a separate rendered contrast check. |
| Responsive | 3 | Desktop dashboard and narrow effective viewport inspected; mobile stacking and scrolling improved; physical touch and all routes/devices not tested. |
| Implementation integrity | 3 | Shared refinement stylesheet reduces drift; existing template-local styling still extensive. |
| Total | 13 / 20 | Provisional: significant improvement opportunities remain; not a WCAG conformity claim. |

## Findings and disposition

| Severity | Finding/location | Impact | Action |
|---|---|---|---|
| P1 | Shared low-opacity secondary text (`light_base`, `map`) | Low contrast makes labels harder to read | Stronger shared foreground tokens. Source scanner cannot resolve the Jinja stylesheet link, so its old token warnings require contextual review. |
| P1 | Fixed-height desktop dashboard applied to cramped screens | Chart/queue content can be compressed or clipped | Preserve desktop dashboard layout; enable page flow on narrow or short viewports, stack mobile trends and pies. |
| P1 | Small header, filter and slider controls | Harder to select and focus, especially on touch | Larger header targets, inputs, legends and slider hit areas; explicit focus rings. Full physical touch audit remains open. |
| P1 | Tutorial declares modal behavior without focus isolation | Keyboard navigation can escape behind it | Root content inert while tour is open; Tab loops within tour; dismiss returns focus to header. |
| P2 | Custom area chooser uses incomplete listbox semantics | Arrow navigation and dismissal are inconsistent | Use ordinary navigation links with current state; focus current link on opening, support arrows/Home/End/Escape and close on focus departure. |
| P2 | Shared header/queue text gets squeezed | Secondary labels and reasons become ellipsized | Better wrapping, table reason wrapping, compact mobile header with page scrolling instead of sticky obstruction. |
| P2 | Remote fonts are a runtime dependency | Delayed or unavailable stylesheet can delay presentation | Preserve both fonts but serve their licensed font files locally with font-display:swap; licenses included. |
| P2 | CSS reduced-motion alone does not stop 3D rotation/map zoom | Unexpected motion despite system preference | Disable automatic rotation and map zoom animation under reduced motion; pause thermal playback when document is hidden. |
| P2 | Remaining fixed colors in server SVGs | Contrast/theming cannot be certified from source scan | Retain existing light chart surfaces; evaluate chart tokens and physical-device contrast in a later focused pass. |
| P3 | Repeated template-local micro typography | Same-role text has inconsistent sizes | Raise 10px functional labels to 11px; preserve the existing visual hierarchy. |

Positive findings: no new calculation code belongs in this change; status labels supplement color;
backend finalization protection and disposition forms remain; the map and review are connected.

## Mechanical detector evidence

Ran the official `impeccable detect --json` once across light_base, base, dashboard, map,
transformer and ui-polish.css. Result: exit 2, 57 findings: 10 low-contrast, 40 undersized-ui-text,
5 tiny-text, 1 tight-leading, 1 all-caps-body.

The scanner emitted these limitations:

```
could not read linked stylesheet {{ url_for('static', filename='ui-polish.css') }}
color and custom-property rules will be incomplete
```

Consequently these counts are raw source findings, not the final rendered defect count. Confirmed
small functional text was increased; shared low-contrast tokens are overridden by ui-polish.css.
The dark map canvas warnings do not account reliably for the translucent foreground panels; they
are not evidence that every map label is invisible. The uppercase finding combines short model/data
labels rather than a paragraph of uppercase body copy; those labels were retained. No broad ignore
rules were added and no clean scanner result is claimed.

## Verification

- Full suite: 60 passed in 6.27s, including local font assets, content landmarks, tutorial/reduced-motion
  markup, and the preserved review form. These tests use temporary sample data, not the working feeds.
- Native Chrome desktop screenshot: dashboard pies, descriptive trend panels and review queue render.
- Native Chrome at 300% browser zoom: narrow effective viewport, vertically stacked summary content
  and page scrolling inspected. This is a desktop zoom test, not physical-mobile or touch evidence.
- Theme/area controls were exercised; a complete dark-mode, keyboard and screen-reader traversal is
  still required before claiming full accessibility. CSS/JS implements the documented behaviors.
- Shared styles are used on map, dashboard, alerts, setup, metrics and review pages. Do not infer
  exhaustive visual/device coverage from the automated route checks.
- Saved feeds, database and reports remain unchanged. No Run now, disposition or setup save was used.

Next focused commands: `/impeccable adapt` for physical-touch/map controls, `/impeccable audit` for
rendered contrast across themes, then `/impeccable polish` for remaining chart-token consistency.
