# H017 (holdout): DRAFT prereg, fixed REV on DATA's certified-untouched history

**Status:** DRAFT. It is NOT registered and NOT tagged, and no R exists. It is tagged `prereg-H017` only after review by CASSANDRA, DATA and ORION.
**Binding text:** `H017_HOLDOUT_PREREG_DRAFT_2026-10-04.json` (this note is a summary).
**Drafted:** 2026-10-04 SAST, on branch `research/h017-holdout-draft` off main 0df97e3. Paper only.

## What it tests
This is a one-shot test of the **unchanged H016b rule**.
- All 111 prereg-H016b pins are identical between harness-H016b-v1 (f062ed2) and main 0df97e3.
- The scoring path is harness-H016b-v1 unchanged: correct-side BID/ASK fills with DATA's slippage floors, binding per-ticket R, entry-minute / exit-bar / 171-of-180 rules, the conservative one-sided exit v2 and the 21 fill-fragility perturbations, and the session-cluster bootstrap (seed 20261004, B 10,000, v[500]).

**Data:** DATA's certified-untouched ranges (DATA_RULINGS_MARKETDATA_2026-10-04.md §4):
- US100: 2019-01-01 → 2022-12-23 17:00 NY.
- US500: 2019-01-01 → 2025-06-01 18:00 NY.

**Feed:** Dukascopy BID+ASK raw bi5 only. No HistData and no fallback.
- The first 22 sessions are context only, so counting starts 2019-02-04.
- NYSE full closures and early closes are excluded.

## File inventory (names and sizes only; nothing opened)
| | BID day files | ASK day files |
|---|---|---|
| US100 2019-01-01 → 2022-12-23 | 772 (from 2020-07-07) | 1,246 (complete) |
| US500 2019-01-01 → 2025-06-01 | 1,535 (from 2020-07-07) | 2,009 (complete) |

DATA's backfill is still downloading **474 BID files per instrument** (2019-01-01 → 2020-07-06). H017 cannot be registered for running until DATA freezes and attests the full manifest.

## Expected N (estimate: burned trade rate × eligible sessions)
| | naive | min-stop/level-adjusted (central) | vol ×1.5 |
|---|---|---|---|
| US100 | 516 | **433** | 478 |
| US500 | 638 | **414** | 582 |
| pooled | 1,154 | **847** | 1,060 |

The min-stop gate (10.2 / 4.88 pt) is pinned in points. Index levels then were about ⅓–½ of today's, so more tickets fall under it. If only sub-window A of US500 counts (Q2), the pooled N is about 653.

## Power (joint P(pass) of P1–P5; normal-approx cluster bound)
| true mean R | N≈847 | N≈1,154 | sub-window A only, N≈653 |
|---|---|---|---|
| 0 (size) | 0.05 | 0.05 | 0.05 |
| +0.10 | 0.60 | 0.70 | 0.47 |
| +0.15 | 0.89 | 0.94 | 0.78 |
| +0.20 | 0.99 | 1.00 | 0.94 |

Fill-fragility (P6) cannot be simulated from burned data, so it can only lower these numbers.

## Pass rule (all required)
- **P1:** pooled cluster-bootstrap one-sided 95% LB v[500] > 0.
- **P2:** mean > 0 on US100 and on US500.
- **P3:** ex-top-1% > 0.
- **P4:** ex-small-stop > 0.
- **P5:** foil ≥ p95.
- **P6:** no flip of P1–P5 under any of the 21 fill-fragility perturbations, including the conservative exit.

Verdicts:
- Fail on any of P1–P5 → `FAILS (holdout)`.
- P6 flip → `FAILS (holdout, fill-fragile)`.
- Pooled N < 400 → `INCONCLUSIVE`.

## One-shot run (ORION ruling #9, quoted in the JSON `orion_rulings.9`)
- **One run.** ORION runs it **once**, from a frozen worktree at the H017 harness tag.
- **Preconditions.** It runs only after `DATA_CERTIFIED` and `CASSANDRA_CLEARED` exist for that tag, and DATA has attested the per-file sha256 of the frozen manifest immediately beforehand.
- **Logging and sealing.** Start and end times, the commit and the tape digest are logged, and outputs are written sealed.
- **Unseal.** There is a single unseal, with CASSANDRA notified, and results are recorded as they are.
- **No reruns.** A crash before outputs counts as no-run. Any rerun needs CASSANDRA's written approval. This replaces the earlier crash-rerun exception.
- **No waiting on H016b.** Its kill and futility rules are mechanical; an early stop enters Holm at p = 1.
- **Changes.** Any change needs a new ID and fresh data.

## Family and replication (ORION ruling #6, quoted in the JSON `orion_rulings.6`)
- H017 opens **family F2**, because F1 is closed under ORION's rule.
- Alpha is one-sided 0.05 with Holm across F2. H017 is the only member, so p < 0.05.
- The member list closes at registration.
- H017 is never pooled with H016b.

H017 may be the new-ID replication for H016b, in either direction, **only if all of the following hold**:
- **R1:** identical frozen REV, entry/exit logic and cost model.
- **R2:** no bar or session overlap with H016b's counted window, and DATA certifies the H017 tape as untouched.
- **R3:** `prereg-H017` is tagged before H016b's first counted row.
- **R4:** both pass on their own terms (H016b via Holm in F1, H017 in F2), under correct-side costs and a non-flipping fill-fragility co-report.
- **R5:** CASSANDRA gives written sign-off on independence (same feed, regime overlap).

If both pass, that is **one** finding: "REV, forward and historical holdout". If any condition fails, an H016b pass needs a separate new-ID replication.

**R3 deadline.** In harness-H016b-v1 a "row" is the log row written by `h016b.py final`; it carries its compute time, and `counted` is True only for counted trades. So the moment meant is that row's **compute time**, not the start of the session.
- H016b's first eligible session is London 2026-10-05 02:00 NY (08:00 SAST). A row for it can exist only once that day's files are final, at ≥ 2026-10-06 01:00 UTC.
- The scheduled run is at about 01:07 UTC, i.e. **~03:07 SAST Tue 2026-10-06**. If 2026-10-05 produces no counted trade, the first counted row comes later.
- **Binding:** `prereg-H017` must be tagged and visible on origin before **2026-10-06 01:00 UTC (03:00 SAST)**. Failing that, it must be tagged before the first counted row's `computed_at_utc`, checked afterwards from timestamp and status columns only.
- **Conservative target:** 2026-10-05 08:00 SAST.
- **If missed:** H017 is still a valid stand-alone F2 test, but it cannot be H016b's replication.

**FX arm:** listed as a future arm. DATA has not certified EURUSD/GBPUSD/XAUUSD, and the pinned REV instrument config has no FX frictions or min-stop.

## Regime caveats
- The window spans COVID 2020, the 2021 melt-up and the 2022 bear market.
- The pinned point constants make costs per R higher at lower index levels.
- Spreads differ by era. DATA's era p90/p99 schedule is required, frozen at registration.
- US500 2022-12-27 → 2025-05-30 overlaps INV-002's NQ path (correlated-path disclosure). It is reported as sub-window B.

## Open questions for reviewers
- **Q1 (DATA):** wait for the BID backfill, or start counting later?
- **Q2:** is US500 sub-window B confirmatory?
- **Q3:** does the US100 HTF end (2021-09-12) apply to REV's daily context?
- **Q4:** should "mean ≥ +0.10" be binding?
- **Q5:** keep the N < 400 INCONCLUSIVE floor?
- **Q6:** RESOLVED by ORION #6 (see above).
- **Q7 (DATA):** certify the 2019–2021 ASK for fills and freeze the era spread schedule; confirm QC and rebuild did no outcome-bearing computation.
- **Q8:** do the fixed-point constants count as the "same rule"?
- **Q9:** RESOLVED by ORION #9 (see above).
- **Q10:** can Q1–Q5, Q7 and Q8 be settled before the R3 deadline? Or should they be fixed as pre-declared conditional rules (window from DATA's frozen manifest; spread schedule frozen at harness registration), so that `prereg-H017` can be tagged first?

## Drafter attestation
No bar data inside the certified ranges was opened, loaded, decoded, content-hashed or computed on for this draft. The only inputs were:
- DATA's rulings and certified table;
- manifest and calendar metadata;
- raw-file names and sizes;
- burned trades;
- pinned code;
- approximate public index levels.
