# H017 (holdout): DRAFT BASELINE prereg, fixed REV on DATA's certified-untouched history

**Status:** this is the DRAFT BASELINE. It is **NOT registered, NOT tagged, and NOT to be locked as reviewed.** No R exists.
- **USER DECISION (2026-10-04 ~13:57 SAST):** redesign before locking, so that US100 era costs are not the deciding factor. See `H017_REDESIGN_OPTIONS_2026-10-04.md`.
- **Reviews:**
  - **ORION ACCEPTS** (a531580). Ruling file `summaries/2026-10-04_H017_RULINGS.md`, sha256 `5a0b2a6063d6a30ebfa1c70d4db231a4bcdcd4ac16950ca81354c9f1c8d10649`.
  - **DATA:** PASS WITH CONDITIONS, then ACCEPT once E1–E12 are in. They are applied here. Source: `DATA_REVIEW_H017_HOLDOUT_PREREG_2026-10-04.md`.
  - **CASSANDRA:** ACCEPT, conditional on A1–A6. They are applied verbatim. Source: `CASSANDRA_H017_HOLDOUT_PREREG_REDTEAM_2026-10-04.md`.
- **Binding text:** the `.json`, with all rulings quoted verbatim and their sha256 values.

## Rule and data
- **Rule:** the unchanged H016b rule. The 111 pins are byte-identical, including min-stop 10.2/4.88 pt. The scoring path is harness-H016b-v1, unchanged.
- **Feed:** Dukascopy BID+ASK raw bi5 only. Never HistData, never a fallback.
- **Manifest bounds (E7):**
  - US100: `20190101..20221223`.
  - US500: `20190101..20250530` (the 20250601 files are dropped).
  - Files outside these bounds are refused, including the 2018 days.
- **Saturdays (E8):** treated as closed, empty days. A burned-data equivalence test is required.
- **Confirmatory pool (Q2; ORION, DATA and CASSANDRA agree):** US100 and US500 sub-window A, both [S\*, 2022-12-23].
- **Exploratory (report-only, never pooled):** US500 sub-window B, 2022-12-27 → 2025-05-30, labelled "correlated-path overlap (INV-002 NQ)".
- **Q3:** the US100 HTF end of 2021-09-12 does not apply. A non-binding US100 split is reported at 2021-09-13.

**Window rule (E4, DATA §2 rules 1–5):**
- **Start.** S\* is the earliest NYSE session ≥ 2019-02-04 whose 22 prior sessions are complete on BID and ASK for both instruments.
- **Freeze.** The manifest freezes at the earlier of (backfill complete + procedure S passed) or **2026-10-18 23:59 SAST**.
- **Gaps** after S\* follow H016b's per-session rules.
- **No HistData** substitution and **no extension**.
- **Disclosed range:** S\* falls between 2019-02-04 and about 2020-08-06.

**Procedure S (E6).** DATA runs a sealed integrity seal once, after the freeze and before harness registration:
- read-only snapshot;
- pre-committed code and whitelist;
- per-file raw and decompressed sha256 and `complete()`;
- per instrument × year × session: one-sided, crossed and zero-spread minutes, and spread p50/p90/p95/p99/max;
- pass criteria: ≥ 99% complete, crossed ≤ 0.1%, one-sided ≤ 1%, p50 > 0.

What follows from S:
- A year-side that fails S is not counted.
- The era p90/p99 schedule comes from S and feeds the co-report only. Binding fills use the measured ASK.
- qc.py's 2019–20 spreads (HistData BID paired with Dukascopy ASK) are **not** used.

**Permitted decodes (E11).** Procedure S and DATA's pre-run snapshot attestation are the **only** decodes allowed before the run. That attestation checks raw and decompressed sha256 against the frozen manifest (E9).

## Expected N and power (confirmatory pool, primary)
| | N | equal +0.15 | equal +0.10 | burned per-instrument means (US100 +0.006, US500 +0.183) | era-cost adjusted (US100 −0.10, US500 +0.23) |
|---|---|---|---|---|---|
| central (level-adjusted) | ~653 (US100 433, US500 220) | **0.78** | **0.47** | **0.27** | **0.05** |

Notes on the table:
- CASSANDRA's table (A2, 400 reps) gives 0.77 / 0.47 / 0.27 / 0.05. The drafter reproduced it with 2,000 reps (`H017_HOLDOUT_POWER_PERINSTRUMENT_2026-10-04.out`).
- Equal-edge power at +0.20 is 0.94.

**Fallback (E3).** If S\* slips to about 2020-08-06, the central N is about 433. INCONCLUSIVE then becomes realistic, and CASSANDRA's < 450 pre-run check would postpone the run.

**Q8 pre-data expectation (CASSANDRA, verbatim in the JSON).**
- US100's era off-RTH spread is about 3.46 pt, against 1.18 burned. That puts the expected US100 mean at about −0.10R.
- P2 is therefore the expected binding failure.
- A FAIL driven by US100 costs is a valid FAIL and may **never** be reworded as "era costs, not edge".

## Pass rule and verdicts
- **P1–P6 as before.** The mean and its CI are a mandatory co-report.
- **Small-effect flag:** if the mean is < +0.10R, the verdict carries a `small-effect` flag and MINT may not size above its minimum.
- **INCONCLUSIVE:** pooled N < 400 on the confirmatory pool. This still consumes the holdout.
- **Pre-run check (Q5):** before the run, DATA counts eligible sessions from file presence and ORION multiplies by the burned rates. If the expected N is < 450, the run is postponed and the holdout stays sealed.

## Run and replication
- **ORION #9:** one run from a frozen worktree at the harness tag, after `DATA_CERTIFIED` and `CASSANDRA_CLEARED`. Sealed outputs, a single unseal with CASSANDRA notified, and no reruns without her written approval.
- **A3:** DATA_CERTIFIED must cover the Dukascopy BID+ASK feed.
- **A5:** an independent scorer with its own sha256 must reproduce the 258 burned R values and every sealed H017 R to within 1e-9 before unseal.
- **A6:** accepting the prereg does not clear the harness.
- **Replication (ORION #6, as amended by CASSANDRA A1/Q4):** conditions R1–R5 apply, and the confirmatory **mean must also be ≥ +0.10R**.
  - **R3:** `prereg-H017` must be on origin before 2026-10-06 01:00 UTC.
  - **R5:** CONDITIONAL. It needs five conditions, of which (1), (3) and (4) are missing today.
- **A4:** CASSANDRA's F4 list of outcome-free holdout reads (g4, f3/f3b, g5b, f1c/f1d, the parquet rebuild, the 2025 US500 loads overlapping B) is disclosed. DATA attests it.

## Regime caveats (E10)
- COVID 2020; the March 2020 circuit-breaker halts on 03-09, 03-12, 03-16 and 03-18 are not closures.
- The 2021 melt-up and the 2022 bear market.
- Point constants are relatively heavier at low index levels.
- BID and ASK 2019–2022 are either certified by S or not counted.

## Resolved questions (E1)
Q1–Q10 are all resolved; the rulings are in the JSON `resolved_questions`.

## Reviewer conflicts (flagged, not chosen)
- **K1:** DATA wants one common S\*; CASSANDRA wants a start per instrument.
- **K2:** DATA's freeze date and fallback against CASSANDRA's < 450 postpone rule. Under the fallback, the run would be postponed indefinitely.
- **K3:** the fallback N is about 450 per CASSANDRA, but about 433 per DATA and the model.
- **K4:** ORION has not yet confirmed CASSANDRA's amendment of his Q4 premise.

## Drafter attestation
No bar inside the certified ranges was opened, loaded, decoded, content-hashed or computed on.
