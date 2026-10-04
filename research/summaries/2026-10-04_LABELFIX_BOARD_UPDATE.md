# INTELLIGENCE SUMMARY — Wave 1 board update after the Kaggle label fix
**Date:** 2026-10-04 (SAST)  
**Owner:** ORION  
**Tape:** CONTINUOUS-KAGGLE-NQ1M · labels=bar-close (corrected 2026-10-04) · roll undocumented · truncation CONFIRMED (ends 2025-12-11) · not MNQ Mar 2026 · not stream C · **touched: no confirmatory use**  
**Basis:** DATA `evidence/tape/KAGGLE_NQ_1M_2022_2025/ADDENDUM_2026-10-04_LABEL_CONVENTION.md` (and DATA_RULINGS_MARKETDATA_2026-10-04 §2/§4, filed locally under `POST-WAVE1-LEADS/`, not in this repo) · QUANT `experiments/results/LABELFIX_RERUN_SUMMARY_2026-10-04.md` plus one re-run memo per hypothesis (paths relative to `research/investigations/INV-002-methodology-seed/`)  
**Supersedes (numbers only):** the Wave 1 figures in `2026-09-13_WAVE1_EXPLORATORY_BOARD.md`; for H003c also the verdict. Earlier memos and locks are kept as filed.

## WHAT DID WE THINK?
The Wave 1 board (2026-09-13) was computed with the Kaggle `timestamp ET` read as the bar **open**. DATA has ruled that it is the bar **close**: raw label T = the bar [T−1:00, T:00). Lag correlation to the US100 CFD peaks at k = −1 (0.984 / 0.990). The cash-open volume spike is on label 09:31, and no 18:00 label exists. So every Wave 1 window was one minute early. The old Popen was the 09:29 pre-open price. The old "first path bar" was the 09:29 pre-open bar, not the 09:30 cash-open bar.

## WHAT DID WE OBSERVE?
QUANT re-ran every Wave 1 script in bar-open time (ts = raw label − 1 min). Logic, seeds, splits, event calendar and holiday sets were frozen. End-of-window edges follow DATA §2. Before the re-run, the original scripts were replayed and reproduced the 2026-09-13 day rows byte-for-byte; H009b was reconstructed exactly. The raw CSV matches the marketdata parquet on 1,048,575/1,048,575 rows.

| Hyp | Old board | **Board after label fix** | Key number OLD → NEW (OOS) |
|-----|-----------|---------------------------|----------------------------|
| H001b frequency (CE by 10:00 incl.) | VERIFY COMPLETE (frequency filed) | **VERIFY COMPLETE (frequency filed)**: holds | P̂ 0.556 [0.488, 0.624] N=205 → **0.588 [0.520, 0.657] N=204** |
| H001b CE-specialness | FAILS | **FAILS**: holds | Δ −0.068 [−0.127, −0.015] → **−0.049 [−0.103, 0.005]** (CI now touches 0; still not > 0) |
| H002b 7–9 state → first side (board = soft empirical prior) | FAILS | **FAILS**: holds | lift 0.0165 [−0.025, 0.057] → **0.016 [−0.025, 0.056]**; class changed on 13/633 primary days (4 OOS) |
| H003c REL/REH → opposite 7–9 extreme vs Foil A | FAILS | **INCONCLUSIVE (power: OOS N_treat 52 < 80)**: changed | Δ −0.150 [−0.247, −0.052] N_treat 139 → **−0.269 [−0.412, −0.124] N_treat 52**; WF median −0.143 → **−0.263** (6 folds) |
| H004b first-10:00-hour FVG vs later control | FAILS | **FAILS**: holds | Δ 0.005 [−0.068, 0.078] → **0.029 [−0.044, 0.102]** N=205; 111/640 old treatment FVGs were 09:59 births |
| H009b weekly nearest-side (Kaggle daily-agg) | INCONCLUSIVE (N) | **INCONCLUSIVE (N_OOS 38 < 80)**: holds | Δ 0.526 [0.368, 0.684] → **0.500 [0.316, 0.684]**; one OOS week's L* flipped |
| H013 Model U v1 · US100 CFD | OPEN · NEEDS MORE DATA · frozen forward-only | unchanged (different tape) | n/a |
| H014 MMXM v5 A · US100+US500 CFD | FAILS (historical) · frozen forward-only | unchanged (different tape) | n/a |

## WHAT CHANGED?
**H003c moves FAILS → INCONCLUSIVE, and the cause is power only.**
1. Treatment days collapse from 343 to 123: IS 204 → 71, OOS 139 → **52**, below the frozen N ≥ 80 gate. Calendar co-report OOS: 114 → 41.
2. **Mechanism.** On almost every treatment day the first REL/REH touch is on the first path bar: 338/343 old, **122/123 new** (the 09:30 bar; one day at 09:40; sides 59 REL / 64 REH). The corrected first bar is the 09:30 cash-open bar, with a median range of about 25 pts against about 8 for the old 09:29 bar. The wider bar trips the protocol's **frozen dual-same-bar exclusion** far more often.
   - Of the 343 old treatment days, **224** move into that exclusion: 112 dual REL+REH and 112 dual REL/REH + range.
   - 1 more day becomes no_path (2025-01-09 closure). 118 stay as treatment, and 5 new days enter, giving 123.
   - Total dual exclusions go from 298 to 517.
3. **The direction is more adverse, not less.** OOS Δ −0.269 [−0.412, −0.124] with the CI entirely below 0; WF median −0.263; IS −0.270. All co-reports are negative (Pierce, SELECTION gate, tertile-reweighted, mid-tertile, calendar split). The label is INCONCLUSIVE only because the frozen protocol requires N ≥ 80 before any verdict.
4. The REL/REH detector stays **PARAMETER** (1-bar fractal + τ_eq = 2.0), not a red-line identity.

QUANT's flag (adopted): the H003c treatment is effectively defined by the state of the opening bar, so the estimand is fragile to the first-bar definition. That is an **estimand design problem**, not a data defect to tune around.

## WHAT SURVIVED?
- All four other verdicts: H001b VERIFY COMPLETE + CE-specialness FAILS, H002b FAILS, H004b FAILS, H009b INCONCLUSIVE. The numbers moved; the labels did not.
- The discipline: frozen protocols re-run without retuning, old numbers verified by replay before comparison, and both end-edge variants reported (identical decision numbers for H003c, H004b and H002b).

## WHAT FAILED?
- The 2026-09-13 label-as-open assumption in the Kaggle gate. DATA's condition 8 now applies: no inference from this tape may use the 2026-09-13 Pref/Popen locks.
- H003c's old FAILS verdict as a *powered* verdict. Its adverse point estimate stands; its power does not.

## WHAT REMAINS UNKNOWN?
- Whether a sweep-then-opposite premise has any lift once the cash-open bar is handled by design rather than by exclusion. This tape cannot answer it: it is touched.
- H009b WF scheme and RTH-agg foil had to be reverse-engineered (inline code not on file). This is co-report only; no decision depends on it.
- MNQ Mar 2026 / lecture-aligned tape (unchanged).

## Decision (ORION ruling)
**H003c = INCONCLUSIVE (power only).**
- The direction is adverse: OOS Δ −0.269 with the CI below 0.
- There will be **no rescue run on this tape**: no relaxed exclusion, no re-pooled split, no lowered N gate, no alternative first-bar rule on the Kaggle tape.
- Any successor is a **new id (H003d)**. It needs a redesigned estimand that explicitly handles the 09:30 cash-open bar (for example by defining the touch and exclusion relative to that bar, set before any data is seen). It must run on **untouched** data, with a fresh CASSANDRA packaging review.

H001b, H002b, H004b and H009b: verdicts hold, numbers updated as above. All results on this tape are tagged `labels=bar-close (corrected 2026-10-04)`. The tape is touched, so there is no confirmatory use. No MERCURY.

**Wave 1 headline is unchanged: no validated edge.** Wave 1 now reads as four falsifications or verify-only results (H001b verify + specialness FAILS, H002b FAILS, H004b FAILS) plus two underpowered results (H003c INCONCLUSIVE with an adverse point estimate; H009b INCONCLUSIVE). Nothing is cleared for MERCURY.

## Frozen locks that still say "H003c FAILS" (not edited)
These locks are frozen and are **not** amended. Read them as superseded by this update on H003c's label and on the Wave 1 numbers.

| File | Line | Text |
|------|-----:|------|
| `2026-10-04_H013_BOARD_LOCK.md` | 61 | Wave 1 scoreboard: `H003c REL→opposite` = **FAILS** |
| `2026-10-04_H013_BOARD_LOCK.md` | 227 | §8 Conflicts: "**H003c FAILS** (REL→opposite 7–9 extreme vs Foil A, OOS Δ≈−0.15)", severity **HIGH** |
| `2026-10-04_H013_BOARD_LOCK.md` | 260 | §9 CASSANDRA answers: "H003c conflict: **Not ruled → OPEN item**" |
| `2026-10-04_H014_BOARD_LOCK.md` | 64 | Wave 1 scoreboard: `H003c REL→opposite` = **FAILS** |
| `2026-10-04_H014_BOARD_LOCK.md` | 230 | Conflicts: "**H003c FAILS** / H003b family (sweep → reversal to the opposite extreme)", severity MEDIUM |
| `2026-09-13_H002b_BOARD_LOCK.md` | 44 | Wave 1 scoreboard: `H003c REL→opposite` = **FAILS** |
| `2026-09-13_H004b_BOARD_LOCK.md` | 39 | Wave 1 scoreboard: `H003c REL→opposite` = **FAILS** |
| `2026-09-13_H009b_BOARD_LOCK.md` | 36 | Key findings: "H003c REL→opposite **FAILS** vs Foil A." |

The same frozen locks also cite the old H001b figure "VERIFY ~56%": H013 l.58 and l.229, H014 l.61, H002b l.41, H004b l.37, H009b l.35. That figure is now 0.588 OOS. Not frozen locks but carrying the old wording: `2026-09-13_WAVE1_EXPLORATORY_BOARD.md` l.6/l.8 (addendum added at its foot) and `2026-09-13_UTILIZATION_FROM_WAVE1.md` l.10–24, 42–44, 57, 72, 97–98 (left as filed; its "~56% prior" should be read as ~59% OOS on corrected labels).

**H013 H003c-conflict assessment still holds.** The premise is still adverse (now more so: OOS Δ −0.269) and is now underpowered on this tape rather than powered-FAILS. The "Direct / HIGH" overlap with H013's reversal setups (201/244 trades target the opposite 7–9 extreme) is unchanged. H014's MEDIUM sweep-then-reverse overlap is likewise unchanged. **This stays a CASSANDRA OPEN item** (H013 §9: "Not ruled"). CASSANDRA should note that the old powered FAILS is now "adverse but underpowered" when ruling.

## HIGHEST-VALUE NEXT EXPERIMENT
None on this tape. If the board wants the sweep-then-opposite question answered, the next step is H003d packaging: an estimand that handles the cash-open bar, a power projection, and untouched data. That goes through CASSANDRA before any data is touched. The forward tests H013/H014 are unaffected.

## Provenance (copied into this repo, bodies unchanged)
- QUANT: `experiments/results/LABELFIX_RERUN_SUMMARY_2026-10-04.md`, `H001b/H002b/H003c/H004b_RERUN_LABELFIX_2026-10-04.md`, `*_day_rows_RERUN_LABELFIX_2026-10-04.csv`; `experiments/wave2/results/H009b_RERUN_LABELFIX_2026-10-04.md` + three `H009b_KAGGLE_*_RERUN_LABELFIX_2026-10-04.csv`.
- DATA: `evidence/tape/KAGGLE_NQ_1M_2022_2025/ADDENDUM_2026-10-04_LABEL_CONVENTION.md` (the original gate file is not rewritten).
- Old memos kept, each with QUANT's one-line header only: H001b and H003c **SUSPENDED**; H002b, H004b and H009b (Kaggle daily-agg) **UNDER RE-CHECK**.
- ORION spot-checked the decision numbers from the day-row CSVs: H001b OOS N 204 / P̂ 0.5882 / Δ −0.0490; H003c N_treat 123, OOS 52, Δ −0.2692, old-treatment breakdown 118/112/112/1, tau on the 09:30 bar 122/123; H004b 111/640 old treatments at raw label 10:00.
