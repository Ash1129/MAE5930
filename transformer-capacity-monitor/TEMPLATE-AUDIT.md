# Template and rubric audit — 2026-10-17, revision 8a24321

Compared the committed application at `8a2432176367660dafc29bd6cb6d6306d27362ef` with the local
course [template SPEC](../Timmy's%20stuff/SPEC.md), [rubric](../Timmy's%20stuff/docs/criteria.md),
[agent rules](../Timmy's%20stuff/AGENTS.md), and the project [SPEC](SPEC.md) and [ledger](CONTRACT.yaml).
This is a repository and interface review, not a predicted judging score, live deployment check, or
validation with a utility's operational data.

## Conclusion

The current interface supports a coherent review-to-follow-up workflow: summarize the county,
filter the queue by review reason and follow-up state, inspect the evidence for an individual
transformer, and record an owner and next action. The core QC methods and their assumptions are
documented separately from web rendering. The project still has explicit template deviations and
external checks to resolve. The instructor questions about the starter/layout and generated,
multi-file datasets remain open as requested.

## Rubric mapping

| Criterion | Evidence at 8a24321 | Remaining qualification |
|---|---|---|
| Working tool, 25 | Flask review app; saved October 15 results; period approval gate; targeted user-path tests | Posit Connect is deployed per the team, but public access and the deployment bundle need later verification. |
| Valid QC analysis, 25 | Plain I-MR, capability, forecast, and decision functions; framework-independent descriptive summaries; known-answer and edge-case tests documented in SPEC/METHODS | Synthetic data is not field validation. Normality improvement is deferred by the owner; dependence and capability limitations remain documented. |
| Prompt fit, 5 | Smart Grid Transformer Surges prompt; loading, nameplate headroom, and heat-pump growth inform planning review | The projection models heat pumps by area, not separate EV or data-center adoption scenarios. |
| Clear user and use case, 5 | SPEC names a grid-planning engineer reviewing three times weekly; findings are explicitly review priorities, not dispatch orders | No independent utility engineer evaluation is claimed. |
| Minimal inputs, 5 | Four required utility feeds; optional ambient and thermal inputs have defaults; no per-run manual data entry | Feed replacement remains an IT/developer workflow, not a stakeholder upload flow. |
| Demonstration, 10 | `demo/README.md` documents normal, boundary-mismatch, and missing-rating scenarios; the saved 500-transformer analysis opens without rerunning | Scenarios are generated multi-file sets. Teammate reproduction is pending; saved analysis predates current rules. |
| Documentation, 10 | README, SPEC, METHODS, codebook, demo guide, start guide, and developer notes describe the tool and methods | Live URL and teammate fresh-clone walkthrough remain pending. The audit and ledger are being reconciled to this commit in H-18. |
| Test datasets and codebook, 10 | Synthetic cases and `data/README.md` document inputs, units, and scenario behavior | Instructor to confirm whether generated multi-file scenarios meet the small-CSV-fixture expectation. |
| Public and reproducible code, 5 | Public GitHub repository; pinned `requirements.txt`; setup, test, manifest, and deploy scripts | Clean-clone verification and Devpost submission remain deferred. The committed `manifest.json` has stale checksums for ten files changed by 8a24321; refresh before the next bundle/deployment verification. |

These are rubric categories and evidence, not a score prediction.

## Changes present at 8a24321

- The map's review panel uses **Review status**, matching the dashboard.
- The dashboard keeps the summary and daily-trend captions beside their titles, removes the daily reporting-count caveat from that caption, and allocates more vertical space to the queue.
- The queue exposes search, Review needed reason categories, follow-up state and overdue filters, and sorting by peak, forecast, or due date. Its reason labels correspond to the category filter. The **Show all 500** control was removed.
- Individual pages show peak time, margin to rating, sample counts at or above rating, reporting-day coverage, latest saved reading, and analysis time. The page explicitly warns that sample counts do not establish overload duration and reporting-day coverage does not verify every interval.
- Optional follow-ups record action, owner, due/recheck date, status, and notes in append-only SQLite history. They are separate from report dispositions, remain editable after report sign-off, and are marked for rechecking when their input hash is old. They are period-specific, do not notify owners, and are not included in report exports.
- The requested Cpk graph was removed. Cpk and its interval remain available as numeric case evidence when calculated; cases with unstable or insufficient history withhold Cpk.
- The existing peak evidence and follow-up features were added to README and SPEC. The ledger has not previously recorded these changes; H-17 records the implementation commit and H-18 tracks this reconciliation.

## Verification evidence and limits

| Check | Evidence |
|---|---|
| Latest full test run available | `64 passed in 6.82s`, before the last dashboard refinements and Cpk-graph removal; not repeated for this read-only audit. |
| Latest targeted run after removing the Cpk graph and “Show all 500” | `13 passed in 2.23s` for `tests/test_viz.py` and `tests/test_webapp.py`. |
| Saved October 15 result counts | Read-only SQLite query: 22 inspect now, 97 review needed, 381 within limits. Follow-up table contains 0 plans. |
| Working database state | The local `data/capacity_monitor.sqlite3` is modified in the worktree and has the follow-up table; it is not part of commit 8a24321. Its current counts match the saved results above. |
| Manifest | Comparing the committed manifest hashes with normalized blobs at 8a24321 found ten stale application/documentation file checksums: README, SPEC, store, webapp tests/app/templates/viz, and UI polish CSS. No manifest paths were missing. Manifest regeneration and deployment verification are pending. |
| Demo scenarios | Normal, boundary-mismatch, and missing-rating scenarios were run in the prior 963bcdf audit, not rerun against 8a24321. |

No feeds were regenerated during this audit. The saved analysis is an earlier result set and should not
be represented as a rerun of current rules. The workflow test evidence covers local synthetic cases;
it does not establish production safety or field accuracy.

## Open items and agreed timing

| Item | Status |
|---|---|
| Starter, stack, and `app/` layout | **Ask the instructor later.** The project uses a Flask layout, not a copied starter in `app/`; no instructor exception is recorded. |
| Small CSV fixtures vs generated multi-file scenarios | **Ask the instructor later.** Preserve this as an open requirement question. |
| Posit Connect public access | Team says it is deployed. Verify the public URL and logged-out behavior later, as planned. |
| Reproducibility | Fresh-clone and pinned-environment checks deferred. Refresh stale manifest checksums before the next deployment verification. |
| Devpost | Submit at the end, as planned. |
| Teammate demonstration and method explanation | Pending; do not mark demonstrated by the author alone. |
| Task checkout discipline | The ledger currently has several open tasks; H-05 and H-07 share the owner "Claude" despite the one-active-task-per-person rule. Resolve the ownership/statuses before starting more ledger work. |
| Normality | Owner deferred method changes. Current Jarque–Bera screen remains; do not describe the assumption as resolved. |
| Follow-up continuity | Current plans are period-specific, have no reminders, and are not exported. Carry-forward/notifications are future product work, not a template requirement. |
| Real utility operation | Real feeds, utility-approved thresholds, feeder topology, interval completeness, and field-calibrated thermal inputs are not validated here. |

## Statistical and operational limitations

The I-MR and Cpk methods are per transformer; county-level descriptive trends carry no control limits.
Baseline lag screens are exploratory pointwise checks and can have multiple-comparison false
positives. Cpk interval coverage was simulated under independent normal observations, not weather-
dependent load. Missing interval data can change a peak: the completeness check requires at least one
reading per review day, while the page explicitly avoids inferring full hourly coverage or overload
duration. The heat-pump forecast uses area-level assumptions. Thermal and seasonal views are labeled
MODELED and do not affect the review decision.
