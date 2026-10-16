# Evaluation results

Run at 2026-10-16T18:18:20 on synthetic feeds (period ending 2026-10-15), isolated home /var/folders/qy/kyrsp2bn37x8k7bfgdz_y_p00000gn/T/capmon-evals-0fw0qppi.

| # | Case | Expected | Observed | Pass |
|---|---|---|---|---|
| 1 | Synthetic case: one transformer has complete readings and a rating, but the boundary feed  | Stop before analysis or publication, identify the period mismatch, alert the responsible p | run failed at step 7; problem: Boundary feed is for a different reporting period (valid 2026-01-01 to 2025-12-31, run period ends 2026-10-15); no period results saved; alert recorded | PASS |
| 2 | Synthetic case: a transformer has enough historical readings, with one point beyond the co | Flag the load pattern as unstable, show the chart signal, and do not report a capability i | T-DRY-004 stability=signal, signals=['beyond_3_sigma', 'moving_range_beyond_ucl'], cpk=None, period peak 82% of rating, status=review_needed | PASS |
| 3 | Synthetic case: a stable transformer has complete inputs, but its one-sided Cpk confidence | Flag the uncertain result for human review and show the estimate, interval, threshold, and | T-LAN-005 cpk=1.43 CI [1.10, 1.77] threshold 1.33 -> rule 8 (Uncertain Cpk: the lower 95% confidence bound is b); review_needed | PASS |
| 4 | Synthetic case: a stable transformer’s forecast peak is above its rated maximum, although  | Flag the forecast exception, display the forecast period, allocation assumption, and ratin | T-CAR-006 period peak 70% of rating, projected peak 139% of rating (TC-HP-2026-v1, 2030 winter peak, allocation declared_primary_area) -> rule 9; disposition required before finalize | PASS |
| 5 | Synthetic case: the same reporting period is rerun after a successful report was saved. | Replace or update that period’s result without creating a duplicate, and retain an auditab | 1 period record after rerun (run_id now 1820607_eval), rerun_count=1, status back to draft for re-approval; 2 run records kept | PASS |
| 6 | Synthetic case: a required sensor feed is unavailable after the configured wait limit. | Mark the run failed or incomplete, alert a person with the run and period identifiers, and | run failed at step 2 (Transformer readings feed is missing: readings.csv not found); alert error with run and period ids; no report available | PASS |

**6 of 6 cases passed.**

Cases are the illustrative synthetic cases from evals/examples.csv; replace them with real past examples and rerun `python scripts/run_evals.py`.