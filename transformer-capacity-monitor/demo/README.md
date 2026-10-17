# Demo: the Transformer Capacity Monitor on each test dataset

Three demonstration datasets, each run with one command. Every number below was printed by the tool on
2026-10-17 at revision `963bcdf` for the period 2026-10-09 to 2026-10-15. All data is SYNTHETIC; the codebook is
[`data/README.md`](../data/README.md).

Setup, once, from the app folder:

```bash
./scripts/setup_env.sh
```

`scripts/run_demo.py` builds the dataset in a temporary folder and runs the full pipeline there, so it
never touches `data/feeds/` or the review app's database. Re-running it gives the same numbers, because
the generator uses a fixed seed.

---

## Dataset 1: `normal`, 12 transformers covering all three outcomes

```bash
.venv/bin/python scripts/run_demo.py normal
```

What it prints:

```text
Run status: success, stopped at step 15

transformer stability               Cpk        95% CI peak/rating forecast/rating  rule  outcome
T-CAR-006   stable                 2.65   [2.07,3.23]         73%            142%    11  review_needed
T-CAY-003   stable                 3.87   [3.03,4.72]         66%             75%    13  within_limits
T-DAN-010   stable                 1.13   [0.87,1.38]         86%             95%     9  review_needed
T-DRY-004   signal                    -             -         82%               -     4  review_needed
T-ENF-011   signal                    -             -        102%               -     1  inspect_now
T-GRO-009   signal                    -             -         71%               -     2  inspect_now
T-ITH-001   stable                 3.95   [3.09,4.81]         67%             75%    13  within_limits
T-ITH-002   stable                 3.55   [2.77,4.32]         66%             74%    13  within_limits
T-LAN-005   stable                 1.59   [1.24,1.95]         78%             87%    10  review_needed
T-NEW-008   stable                 2.90   [2.27,3.54]         66%             74%    13  within_limits
T-TRU-012   signal                    -             -         82%               -     3  inspect_now
T-ULY-007   insufficient_history      -             -         61%               -     5  review_needed

12 transformers: 4 within limits, 5 need review (amber), 3 need an inspection now (red).
```

**How to read this.** "Rule" is the first matching row of `rules/decision-table.csv`. Rule 13 means
nothing matched, so the transformer is within limits (green). Rules 1 to 3 mean **inspect now** (red):
a reading at the rating, a run rule firing this period, or repeated outliers this period. Rules 4 to 12
mean **review needed** (amber). Each flagged row shows a different reason:

| Transformer | Rule | Why it is flagged | Check it by hand |
|---|---|---|---|
| T-ENF-011 | 1, reading at the rating | One daily peak of 76.53 kVA is 102% of the 75 kVA rating, so the transformer ran past its nameplate. It goes straight to inspect now, before any chart rule is considered. | 76.53 / 75 = 1.0204 ≥ 1.0 |
| T-GRO-009 | 2, run rule this period | Eight days in a row sat above the centre line and 2 of 3 consecutive days were beyond 2 sigma, ending inside the period. A pattern like this is a real change on the circuit, not noise, so it is inspect now even though the peak is only 71% of rating. | 8 consecutive peaks > centre; `inspect_signals` ≥ 1 |
| T-TRU-012 | 3, repeated outliers | Three separate days in the period fell beyond 3 sigma (two high, one low), with no run rule. Three or more outlier days in one week is `chart.inspect_outliers_at`, so it is inspect now. | `outlier_signals` = 3 ≥ 3 |
| T-DRY-004 | 4, a few outliers | The daily peak of 61.5 kVA on 2026-10-13 is above the UCL of 55.13 kVA. The centre is 44.963 and MR-bar is 3.823. The peak is still only 82% of the 75 kVA rating. Cpk is withheld because the pattern is not stable. | UCL = 44.9628 + 2.66 × 3.82254 = 55.1308 |
| T-DAN-010 | 9, low Cpk | Cpk is 1.13, below 1.33, although every reading is under the 50 kVA rating. The period peak is 86% and forecast peak is 95%; rule 9 matches before the forecast rule. | (50 − 39.91015) / (3 × 2.98383) = 1.12717 |
| T-LAN-005 | 10, uncertain Cpk | Cpk is 1.59, above 1.33, but its 95% lower bound of 1.24 is below 1.33. Sixty-seven days of data cannot rule out thin headroom. | Bissell interval with 0.62 × 66 = 40.92 degrees of freedom |
| T-CAR-006 | 11, forecast | Healthy today at 73% of rating with Cpk 2.65. Heat-pump growth adds 68.2 kVA, so the projected peak is 142% of the 100 kVA rating. | 73.30 + 60 × (0.57 − 0.12) × 2.4 / 0.95 = 141.5 kVA |
| T-ULY-007 | 5, insufficient history | A new transformer with 12 days of readings. Only 5 fall before the period, short of the 20 baseline days a chart needs. | 5 < 20 |

The saved report's allocation example for T-NEW-008 refers to the former synthetic rectangle boundary
set. The map now uses public NYS municipal geometries, and this synthetic transformer's coordinates are
not a verified Newfield location. Treat that saved spatial example as historical; the analysis has not
been rerun against the new boundary feed.

**See the committed demonstration in the app.** Run `./testme.sh` and open
http://127.0.0.1:5055. The saved 2026-10-15 analysis has **500 transformers: 22 inspect now,
97 review needed, 381 within limits**. It is a larger dataset than the isolated 12-transformer
scenario above. Do not press **Run now** or regenerate the feeds just to view it.

1. On the Map, open an amber or red transformer and select **Open full review**.
2. Inspect its rule, chart, headroom and source readings. The 3D temperatures are MODELED.
3. Dispositions modify the working review database. Demonstrate decisions on a separate copy if
   the committed demonstration must remain unchanged. Finalization is blocked until the review
   requirements are met; request-changes cases also block finalization.
4. Select a district on the Map to reveal the integrated heat controls. Seasonal load and
   temperature views are models and do not drive the decision table.

---

## Dataset 2: `boundary-mismatch`, the boundary file is for the wrong year

```bash
.venv/bin/python scripts/run_demo.py boundary-mismatch
```

What it prints:

```text
Run status: failed, stopped at step 7
Blocking problems:
  - Boundary feed is for a different reporting period (valid 2026-01-01 to 2025-12-31, run period ends 2026-10-15)
```

**How to read this.** The boundary metadata says the shapes are valid until 2025-12-31, but the period
ends in 2026. The tool stops before any statistic is computed. It writes no partial report and records an
alert with the run and period ids. A wrong-period join would silently assign transformers to the wrong
forecast area, so refusing is the correct result.

---

## Dataset 3: `missing-rating`, one transformer has no nameplate rating

```bash
.venv/bin/python scripts/run_demo.py missing-rating
```

What it prints:

```text
Run status: failed, stopped at step 7
Blocking problems:
  - T-GRO-009: no rated maximum load on the asset record
```

**How to read this.** Without a rating there is no upper limit for Cpk and no "% of rating", so the run
stops and names the transformer to fix in the asset register. Fix the record and press **Run now** for
the same period. The rerun replaces that period's draft instead of creating a duplicate.

---

## Degenerate cases

The test suite covers the inputs that are too small to show in a demo table:

```bash
.venv/bin/python -m pytest tests -q
```

The current observed result is recorded in [TEMPLATE-AUDIT.md](../TEMPLATE-AUDIT.md). The tests include these cases:
- **Constant readings** give "zero variation". No Cpk is reported, and decision-table rule 6 sends the case to review as a likely meter fault.
- **One point or no points** give "insufficient history".
- **Non-finite values** are dropped before the chart.
- **A planted run-rule pattern** is caught for each rule: 2 of 3 beyond 2 sigma, 8 in a row, and moving range above its UCL.

The six evaluation cases in `evals/examples.csv` run with `.venv/bin/python scripts/run_evals.py`.
The results are in `evals/results.md`.
