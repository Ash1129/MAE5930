# Demo: the Transformer Capacity Monitor on each test dataset

Three demonstration datasets, each run with one command. Every number below was printed by the tool on
2026-10-16 for the period 2026-10-09 to 2026-10-15. All data is SYNTHETIC; the codebook is
[`data/README.md`](../data/README.md).

Setup, once, from the app folder:

```bash
./scripts/setup_env.sh
```

`scripts/run_demo.py` builds the dataset in a temporary folder and runs the full pipeline there, so it
never touches `data/feeds/` or the review app's database. Re-running it gives the same numbers, because
the generator uses a fixed seed.

---

## Dataset 1: `normal`, 12 transformers covering every review rule

```bash
.venv/bin/python scripts/run_demo.py normal
```

What it prints:

```text
Run status: success, stopped at step 15

transformer stability               Cpk        95% CI peak/rating forecast/rating  rule  outcome
T-CAR-006   stable                 2.75   [2.12,3.38]         73%            142%     9  review_needed
T-CAY-003   stable                 2.87   [2.21,3.53]         65%             75%    11  within_limits
T-DAN-010   stable                 1.15   [0.87,1.42]         93%            101%     7  review_needed
T-DRY-004   signal                    -             -         82%               -     2  review_needed
T-ENF-011   stable                 3.31   [2.55,4.07]         64%             71%    11  within_limits
T-GRO-009   stable                 3.94   [3.04,4.84]         64%             74%    11  within_limits
T-ITH-001   stable                 3.35   [2.58,4.11]         65%             74%    11  within_limits
T-ITH-002   stable                 3.05   [2.35,3.75]         63%             71%    11  within_limits
T-LAN-005   stable                 1.54   [1.18,1.90]         78%             87%     8  review_needed
T-NEW-008   stable                 2.84   [2.19,3.49]         66%             74%    11  within_limits
T-TRU-012   stable                 3.41   [2.63,4.19]         68%             78%    11  within_limits
T-ULY-007   insufficient_history      -             -         61%               -     1  review_needed

12 transformers: 7 within limits, 5 need review.
```

**How to read this.** "Rule" is the first matching row of `rules/decision-table.csv`. Rule 11 means
nothing matched, so the transformer is within limits. Each "review_needed" row shows a different reason:

| Transformer | Rule | Why it is flagged | Check it by hand |
|---|---|---|---|
| T-DRY-004 | 2, chart signal | The daily peak of 61.5 kVA on 2026-10-13 is above the UCL of 55.47 kVA. The centre is 44.81 and MR-bar is 4.01. The peak is still only 82% of the 75 kVA rating. Cpk is withheld because the pattern is not stable. | UCL = 44.81 + 2.66 × 4.008 = 55.47 |
| T-DAN-010 | 7, low Cpk | Cpk is 1.15, below 1.33, although every reading is under the 50 kVA rating. Its forecast peak of 101% would also trip rule 9, but rule 7 matches first. | (50 − 40.176) / (3 × 2.850) = 1.15 |
| T-LAN-005 | 8, uncertain Cpk | Cpk is 1.54, above 1.33, but its 95% lower bound of 1.18 is below 1.33. Sixty-one days of data cannot rule out thin headroom. | Bissell interval with 0.62 × 60 = 37.2 degrees of freedom |
| T-CAR-006 | 9, forecast | Healthy today at 73% of rating with Cpk 2.75. Heat-pump growth adds 68.2 kVA, so the projected peak is 142% of the 100 kVA rating. | 73.30 + 60 × (0.57 − 0.12) × 2.4 / 0.95 = 141.5 kVA |
| T-ULY-007 | 1, insufficient history | A new transformer with 12 days of readings. Only 5 fall before the period, short of the 20 baseline days a chart needs. | 5 < 20 |

T-NEW-008 sits where four synthetic boundary rectangles overlap: ITH-T, DAN, ENF and NEW. It is within
limits. Its forecast assumptions record `allocation_flagged: true`, the four located areas, and that its
declared primary area NEW was used. No warning is raised, because the declared area contains the location.

**See it in the app.** Run `./scripts/start_app.sh`, open http://127.0.0.1:5055/dashboard, pick period end
2026-10-15 and press **Run now**. This runs on whatever is in `data/feeds/`. To get exactly the 12
transformers above, first run `.venv/bin/python scripts/make_synthetic_data.py --end 2026-10-15`.
1. On the **Map**, the five transformers above show as red dots.
2. Open T-DRY-004 with **Review**. The I-MR chart marks 2026-10-13 in red, and the checklist sits beside it.
3. Choose **Approve conclusion**, **Request changes** or **Reject** with a note. Repeat for each red transformer.
4. Press **Approve and finalize report**. It is refused with HTTP 409 until every flagged case has a disposition.
5. Optionally open the period's **Heatmap** to see hourly load by transformer. Its seasonal view is
   labeled MODELED: it scales the recorded hourly shapes by assumed monthly factors and is never used
   in a review decision.

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

That prints `26 passed`. The tests include these cases:
- **Constant readings** give "zero variation". No Cpk is reported, and decision-table rule 3 sends the case to review as a likely meter fault.
- **One point or no points** give "insufficient history".
- **Non-finite values** are dropped before the chart.
- **A planted run-rule pattern** is caught for each rule: 2 of 3 beyond 2 sigma, 8 in a row, and moving range above its UCL.

The six evaluation cases in `evals/examples.csv` run with `.venv/bin/python scripts/run_evals.py`.
The results are in `evals/results.md`.
