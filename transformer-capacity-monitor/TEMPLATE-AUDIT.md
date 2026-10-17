# Template and rubric audit — 2026-10-17

Compared current checkout `5fdfdbc` with the local course materials:
[template SPEC](../Timmy's%20stuff/SPEC.md),
[task ledger](../Timmy's%20stuff/CONTRACT.yaml),
[agent rules](../Timmy's%20stuff/AGENTS.md), and
[100-point rubric](../Timmy's%20stuff/docs/criteria.md).
This is a local-snapshot audit. The team confirms Posit Connect is deployed; re-verification is
deferred. Clean-clone checks are also deferred, starter/layout and multi-file-case questions await
the instructor, and Devpost submission is planned for the end. The next implementation task is
statistical validation. These deferred items are tracked, not blockers to pushing this documentation.

## Highest-priority remaining work

| Priority | Requirement and observed state | Next action |
|---|---|---|
| 1 | Valid QC analyses earn 25 points. Per-transformer analysis is in plain pipeline functions. The p/u/X-S calculations and quartiles are now in `capacity_monitor/aggregate.py`, with numerical known-answer and edge-case tests. | Extraction and numerical checks are complete. Next assess the baseline fallback and the binomial/Poisson/rational-subgroup assumptions documented in METHODS.md. |
| 2 | The template requires explaining every printed number. SPEC previously omitted the new charts and contradicted the thermal visualization. These are now documented in METHODS.md. | Keep METHODS.md synchronized with the upcoming statistical changes; validate the methods separately. Do not equate modeled temperatures with measurements. |
| 3 | Working public Posit Connect deployment is required. Publishing files exist and the team confirms deployment. Re-verification is deferred. | Verify the latest workflow, follow the public app redirect to a successful map, confirm saved counts, and put the tested public URL in README and delivery evidence. No need to run analysis for this check. |
| 4 | Reproducibility requires a fresh clone. `requirements.txt` is pinned but `setup_env.sh` installs broad version ranges; `testme.sh` assumes Python/dependencies are ready. | Install from the pinned requirements, then check setup and launch in an isolated clean checkout. Preserve the saved feeds and database; verify 22/97/381 without Run now. |
| 5 | The template names a starter copied into `app/`, `app/qc.py`, and the four-file launch/deploy contract. Scripts now exist, but in this project's app root; Flask was built independently. | Resolve the explicit layout/stack deviation with the instructor, or adapt to the required structure. Renaming a folder does not establish that a starter was used. Keep the workflow and manifest consistent with any move. |
| 6 | The template asks for 2–3 small CSV datasets in `data/`. Current cases are generated multi-file scenarios; one large saved demonstration is committed. | Commit small self-contained scenario fixtures with required companion files and exact expected outcomes, or confirm the multi-feed equivalent is acceptable. Current isolated scenario commands are useful but not literal fixture compliance. |
| 7 | Public repo and Devpost submission are required; teammate reproduction is part of the ledger's completion checks. | At the end, verify public access, submit the repo plus demo and live URL, and record the teammate walkthrough. Record evidence rather than assuming these are complete. |

## Statistical review questions before adding more features

- The p chart treats the daily count at/above 90% of rating as a binomial fraction. Document why
  transformers can be treated as independent trials; shared weather and unequal equipment may violate this.
- The u chart counts I-MR signal events per transformer. Multiple rules can fire for one asset/day;
  explain the counting convention and assess the Poisson/equal-opportunity assumptions.
- The X-S chart groups different transformers on a day. Explain whether these form rational subgroups;
  heterogeneous ratings, customer classes and shared weather can make conventional limits misleading.
- `county_control_statistics` currently falls back to all dates when no pre-period baseline exists.
  An explicit insufficient-baseline result is preferable to silently fitting on review-period observations.
- The modeled thermal functions live outside the web layer and have dedicated tests. The report should
  distinguish these illustrative estimates from validated asset-specific thermal forecasts.
- “Inspect now” is a configured prioritization label. It does not establish a validated safety threshold
  or an automatic field dispatch; the engineer still makes and records the decision.

## What is already in place

- Named user, prompt and engineering decision in SPEC; four required feeds plus optional ambient data.
  The rubric asks for minimal feasible inputs, not a minimum of five inputs.
- I-MR, capability/interval, forecast and three-tier decision functions; automated tests.
- Local `testme.sh`, `manifestme.sh`, `deployme.sh`, README, Connect manifest and publish workflow.
- Committed 2026-10-15 sample report: 500 total, 22 inspect now, 97 review needed, 381 within limits.
- Integrated map/heat controls, review checklist, backend finalization gate and optional display-only AI.
- No requirement in the reviewed rubric to replace this working app with a new Version 2 or add graphs.
  New-data upload would improve usability but is not explicitly mandated by that rubric.

## Documentation changes made in this audit

- METHODS: numerical formulas, denominators, baselines, units, assumptions, parameter precedence,
  thermal known answers, existing coverage and remaining statistical work.
- README-DEVELOPER: correct current rule number and tracked-feed status; link the method reference.
- SPEC: current scripts/deployment implementation, three outcomes, optional inputs, added charts,
  thermal scope, committed demo data and remaining deviations.
- README: use `testme.sh`, explain saved counts, distinguish publish files from verified deployment,
  and identify aggregate computations outside the core pipeline.
- CONTRACT: remove obsolete missing-script/untracked-data claims; preserve open external checks.
- Data codebook: correct committed output status and ambient feed usage.
- Demo guide: separate isolated 12-transformer cases from the saved 500-transformer app; remove the
  instruction to regenerate working feeds just to view the demonstration.
- START-HERE: update the dashboard description.
- DELIVERY-REPORT: current snapshot supersedes historical feature counts and delivery gaps.

## Evidence and limits

- `.venv/bin/python -m pytest tests -q`: **44 passed in 5.19s**. Tests use isolated temporary data;
  no production analysis or feed regeneration was invoked. Passing tests alone does not establish
  that the new aggregate charts have adequate statistical validation.
- During the preceding local recovery, the Git database passed SQLite integrity_check (`ok`);
  the restarted app's root redirect led to a map returning HTTP 200.
- Documentation audit checks: ledger parses, required contract files exist, `git diff --check` passes.
- Not performed: fresh clone/dependency installation, demo commands, live publication, public browser
  check, Devpost verification, real-data validation, or approval of utility thresholds.
- Older sections of DELIVERY-REPORT retain dated historical results; this audit's snapshot takes
  precedence for the current implementation. AI CLI access is optional and environment-specific.

## Aggregate extraction follow-up

Calculations and box quartiles now live in `capacity_monitor/aggregate.py`, without web imports,
markup or I/O. The web wrapper preserves its existing output contract. Numerical tests cover p/u/X/S
known answers and degenerate cases; saved-data SVGs and counts match the prior implementation exactly.
The all-date fallback is retained and identified in the numerical metadata. This is architectural and
numerical verification, not resolution of the modeling assumptions listed above.

## Descriptive trends supersede aggregate control charts

The p/u/X-S charts and their aggregate alarm limits have now been replaced with daily near-rating
percentage, unique transformers with signals, and median loading with a quartile band. This resolves
the aggregate baseline-fallback and distribution/subgroup concerns above by removing the inference;
it does not validate those discarded limits. Pie summaries, individual I-MR charts, per-transformer
outcomes and the saved analysis remain unchanged. Current formulas and tests are in METHODS.md.
The next assumptions review concerns the individual I-MR/capability analysis.
