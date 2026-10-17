# Template and rubric audit — 2026-10-17, revision 963bcdf

This replaces the earlier audit and its superseded follow-ups. Sources are the local course
[template SPEC](../Timmy's%20stuff/SPEC.md), [ledger](../Timmy's%20stuff/CONTRACT.yaml),
[agent rules](../Timmy's%20stuff/AGENTS.md), and [rubric](../Timmy's%20stuff/docs/criteria.md).
This is an implementation/documentation audit, not a predicted judging score or real-utility validation.

## Conclusion

The app now substantially follows the rubric's statistical separation and documentation principles.
The unsupported aggregate control charts are gone; numerical descriptive functions live outside the
web layer. Individual-chart findings 2–6 are implemented and tested. Full template compliance remains
conditional on the explicitly deferred layout/dataset questions and delivery/reproducibility checks.
Normality-method improvement remains deferred by owner choice, not considered statistically resolved.

## Rubric mapping

| Criterion | Current evidence | Remaining qualification |
|---|---|---|
| Working tool, 25 | Flask review app, preserved sample database, backend finalization gate; recent local dashboard and review-page HTTP 200 checks; web-path tests | Team confirms deployed; current public access is not reverified in this audit. |
| Valid QC analysis, 25 | Plain I-MR/capability/forecast functions in `capacity_monitor/pipeline.py`; descriptive functions in `aggregate.py`; regression, known-answer, edge-case and simulation tests | Synthetic-case evidence is not validation on real load/weather data. Statistical limitations remain documented. |
| Prompt fit, 5 | SPEC names Smart Grid Transformer Surges and links load monitoring, headroom and heat-pump growth to planning decisions | Forecast explicitly covers heat pumps, not separate EV/data-center scenarios; observed readings can include any load. This is a disclosed scope choice. |
| Clear user/use case, 5 | Named grid-planning engineer; exception review and period sign-off | No independent utility-user evaluation claimed. “Inspect now” is a prioritization rule, not automatic dispatch. |
| Minimal reasonable inputs, 5 | Four required utility feeds; optional ambient and asset thermal fields have defaults | File replacement is still a developer/IT workflow; no browser upload. The rubric does not require five inputs. |
| Demonstration, 10 | All three isolated demo commands executed in this audit; walkthrough numbers and hand checks refreshed | Teammate walkthrough not verified. Preserved 500-transformer demo uses the earlier analysis version. |
| Documentation, 10 | README, SPEC, METHODS, codebook, demo, start guide and developer notes explain inputs, formulas, assumptions and usage | Add the tested public URL later. Historical delivery sections remain explicitly historical. |
| 2–3 working datasets, 5 | Normal, boundary-mismatch and missing-rating scenarios ran as documented | Generated multi-file scenarios differ from the template's small committed CSV fixtures; instructor question deferred. |
| Codebook, 5 | Input schemas/units/collection methods and planted cases in data/README; optional model sources in METHODS | Scenario rows were corrected for the three inspection cases during this audit. |
| Public/reproducible code, 5 | Public repository location documented; requirements, manifest, launch and publish scripts exist | Fresh-clone verification is deferred; setup currently installs version ranges. Public accessibility and Devpost are not independently checked here. |

## Resolved since the first audit

- Aggregate calculations moved out of `webapp/viz.py`; numerical summaries have independent tests.
- County p/u/X-S limits, alarm points and baseline fallback removed. Replacement daily trends show
  near-rating percentage, unique affected transformer counts and median with the middle-50% band.
- Individual baseline dependence checks at lags 1–7 run before capability availability is assessed;
  flags carry into review routing. Checks are pointwise exploratory screens, not proof of independence.
- Eight-point runs that continue into the review period remain signaled on subsequent days.
- `history_days` now means baseline days: 60 before the seven-day review period, 67 total.
- Confidence intervals explicitly support only 95%; other configured levels are rejected.
- Chart wording distinguishes run-pattern signals from limit exceedances; “no issue detected” avoids
  asserting independence or stability. Legacy saved results identify missing baseline diagnostics.
- METHODS documents current formulas, units, numerical outputs, model defaults and limitations.

## Current evidence

| Check | Observed result |
|---|---|
| Latest full suite, preceding statistics-fix verification | `58 passed in 6.07s`; not repeated for these documentation-only edits |
| `scripts/run_demo.py normal`, run in this audit | Success, step 15; 12 transformers: 4 within, 5 review, 3 inspect |
| `scripts/run_demo.py boundary-mismatch`, run in this audit | Expected failed analysis at step 7, wrong-period boundary identified |
| `scripts/run_demo.py missing-rating`, run in this audit | Expected failed analysis at step 7, T-GRO-009 missing rating identified |
| Scenario isolation | Each command creates its own temporary CAPMON_HOME; working feeds/database/reports untouched |
| Numerical walkthrough | Updated from the isolated run, including T-DAN-010 Cpk 1.13 and T-LAN-005 Cpk 1.59, interval 1.24–1.95 |
| Current saved app | Prior check after latest fixes: transformer review HTTP 200, qualified caption and legacy diagnostics label |
| Static audit checks | Ledger parses, task IDs unique, required contract files exist, local documentation links resolve, manifest checksums match, git diff --check passes |
| Saved outputs | Working feeds, database and reports have no Git diff; preserved counts remain 22/97/381 |

The normal demo is freshly generated and analyzed only in a temporary directory. The preserved app
analysis is not the same dataset or analysis version; its counts must not be presented as expected
output from rerunning current rules. No evaluation script, scheduler trigger or working-data rerun was
performed. Older test/evaluation counts remain dated historical evidence.

## Remaining items and agreed timing

| Item | Disposition |
|---|---|
| Posit Connect URL/public access | Deployed per team; verify later and add the tested URL to README/delivery evidence. |
| Reproducibility | Deferred. Install from pinned requirements rather than ranges, then verify a clean checkout. |
| Starter, stack and `app/` layout | Ask instructor later. Four-file contract exists in `transformer-capacity-monitor/`, but no starter was copied and Flask differs from the named dashboard stacks. |
| Multi-file datasets | Ask instructor later whether the three generated feed-set scenarios satisfy the fixture requirement. |
| Devpost submission | Planned for the end. No submission action taken. |
| Teammate demonstration/method explanation | Have a teammate reproduce the walkthrough and explain the method before closing the corresponding ledger checks. |
| Normality | Owner deferred changes. Current Jarque–Bera asymptotic screen is retained; it is not an exact finite-sample test. |
| Real utility feeds, approved thresholds, field-calibrated thermal values | Outside the hackathon demo; do not claim operational readiness. |

Additional statistical limitations remain: dependence screens have multiple-comparison false positives,
capability intervals were simulated under independent normal observations rather than weather-dependent
loads, and the synthetic generator selects cases matching intended labels. Missing daily/hourly coverage
can affect peaks; the current completeness check requires a reading each period day, not all expected
hourly intervals. Thermal and seasonal outputs remain explicitly MODELED. The public assumption-check
helper is not hardened for empty direct input, though the capability caller guards sample size.

## Documentation refreshed in this audit

- Replaced this audit's contradictory historical findings with the current rubric mapping.
- Updated demo output and hand checks for the corrected baseline; retained the separate saved-data demo.
- Corrected planted-case codebook rows and the start guide's dashboard description.
- Updated SPEC's worked example and inspection interpretation, and DELIVERY-REPORT's current snapshot.
- Updated the task ledger and deployment-manifest checksums without publishing or changing analysis data.
  The full checksum check also found and corrected a pre-existing stale checksum for map.html.
