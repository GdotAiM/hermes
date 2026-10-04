# H015b: WITHDRAWN-PRE-DATA (ORION, 2026-10-04 11:4x SAST)

Status: **WITHDRAWN-PRE-DATA**. This is not FAILS, and it carries no verdict on FTN REV.

Basis: CASSANDRA's ruling, /home/box/hermes-x/reviews/post-wave1/CASSANDRA_H015B_WITHDRAWAL_RULING_2026-10-04.md.
1. The binding flat 0.8/0.5 cost is biased in the pass direction. With correct-side fills, US100 goes from -0.018R to -0.132R, because the 1-point buffer is smaller than the ~1.2-point spread.
2. H016's trades are a subset of H015b's (256 of 258 R values match). H015b would only add alpha cost to the family.
3. H015b has zero counted rows. Withdrawal happens before its first counted run (01:07 UTC Tue 2026-10-06), so no outcome has been seen.

Actions:
- ORION's nightly H015b runner routine is deleted, so no H015b rows are computed. If anyone runs the harness later, it is a non-binding diagnostic only, and its R stays sealed until H016b reaches a verdict.
- The tags prereg-H015b and harness-H015b-v2 are kept for provenance. DATA_CERTIFIED and CASSANDRA_CLEARED for H015b lapse; CASSANDRA is revoking hers.
- The forward family is now **H013, H014 and H016b**. Holm at one-sided 0.05 is 0.0167, 0.025 and 0.05. To be quoted pre-data in the H016b prereg.
- Family rules (a) and (b) stand, including CASSANDRA's stricter additions:
  - a flat-cost SURVIVES also needs the correct-side co-report to pass;
  - the (b)4 check needs a non-flipping fill-fragility co-report.
