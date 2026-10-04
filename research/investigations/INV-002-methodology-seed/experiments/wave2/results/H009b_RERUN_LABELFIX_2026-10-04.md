# H009b (Kaggle daily-agg) RE-RUN (LABELFIX) — 2026-10-04
`CONTINUOUS-KAGGLE-NQ1M · labels=bar-close (corrected 2026-10-04) · roll undocumented · truncation CONFIRMED (ends 2025-12-11) · not MNQ Mar 2026 · not stream C · No MERCURY` · daily-agg from 1m · not Sunday Globex-open identity · not Yahoo 1wk.csv

**Replaces (re-check of):** `H009b_KAGGLE_DAILY_AGG_RESULTS_2026-09-13.md` · **Protocol:** `wave2/QUANT_H009b_NEAREST_PWPM_PROTOCOL_2026-09-13.md` (§0e freeze) · **Script:** `/workspace/h009b_kaggle_labelfix.py`. The original run was inline and no script is on file, so this one was rebuilt. `H009B_MODE=old` reproduces the 2026-09-13 result; `H009B_MODE=new` is the bar-open re-run.
**Artifacts:** `H009b_KAGGLE_daily_agg_FULL_ET_RERUN_LABELFIX_2026-10-04.csv`, `H009b_KAGGLE_unique_weeks_RERUN_LABELFIX_2026-10-04.csv`, `H009b_KAGGLE_all_weeks_RERUN_LABELFIX_2026-10-04.csv`

## One-line confirmation for DATA
**The result does not change.** The decision stays **INCONCLUSIVE (N_OOS = 38 < 80)**. OOS N is unchanged, and OOS Δ moves 0.5263 → 0.5000. This comes from one OOS week whose nearest-side pick flipped because P0 moved by 3.5 pts. The impact is negligible, as DATA expected.

## Decision
| | OLD | NEW |
|---|---|---|
| L4 nearest-side vs 4-way random foil, unique-first weeks | INCONCLUSIVE (N_OOS < 80) | **INCONCLUSIVE (N_OOS < 80)** |

The allowed label, if powered, would be "Observed nearest-side (022) · PARAMETER Mon-open proxy". Neither run is powered, so SURVIVES is not claimed. No MERCURY.

## Window / horizon convention (bar-open; raw label = bar open + 1 min)
| Object | Bar-open definition | Raw-label range |
|---|---|---|
| Daily OHLC (primary, full ET calendar day) | all bars **opening** on ET date D, i.e. bars [D 00:00, D+1 00:00) | labels **D 00:01 … D+1 00:00** (the old run used labels D 00:00 … D 23:59) |
| P0 (Mon-open proxy) | open of the bar opening **09:30** on the first ISO-week day that has one; else that day's first open | open of label **09:31** |
| Fri-close P0 (sensitivity) | close of the last bar of the prior calendar day on tape | — |
| RTH-agg sensitivity | bars opening [09:30, 16:00) | labels 09:31 … 16:00 |
| Prior-week HH/LL | max high / min low of daily bars in the prior ISO week (Mon–Sun; the Sunday-evening session sits in the week it ends) | — |
| Prior-month HH/LL | prior calendar month of the ISO-week Monday, from the same daily series | — |

## Reconstruction fidelity (OLD mode vs the 2026-09-13 artifacts)
- Daily aggregate: **923/923 days identical** to `H009b_KAGGLE_daily_agg_FULL_ET.csv` on all 9 columns.
- Weeks processed: 154. Unique-first weeks: 82, the **identical set**. P0, L*, first_tag, U, success, foil_success, success_fri and dual all match on **82/82** weeks.
- Every primary number in the old memo is reproduced exactly: ALL/IS/OOS accuracy, CIs, foil rate, Δ and Δ CIs, Fri-close OOS 0.7632, and RTH-agg OOS N=41 with accuracy 0.7073.
- Frozen rules recovered from the old artifacts:
  - A high-type level (PWH/PMH) counts as touched when the day's high ≥ the level; a low-type level when the day's low ≤ the level.
  - The first day with any touch decides the week; it is unique only if exactly one level is touched that day.
  - A nearest-side tie inside one family (e.g. PWH = PWL distance) excludes the week.
  - Foil: `random.seed(20260913)`, then one `random.choice(L4)` per processed week, in order.
- **Two items not reproduced exactly:**
  1. **WF median.** The old memo gives 0.5667. The only simple scheme I found that reproduces it is non-overlapping full blocks of 15 OOS unique-first weeks (2 folds). I used that scheme, and also report blocks of 10 (≥5 weeks).
  2. **RTH-agg foil.** The old memo has foil 0.2927 / Δ 0.4146. The reconstruction gives 0.2683 / 0.4390, a one-week difference on a co-report-only sensitivity. Cause unknown; no decision depends on it.

## OLD vs NEW — every decision number
| Quantity | OLD | NEW |
|---|---|---|
| Daily bars / weeks processed | 923 / 154 | 923 / 154 |
| Unique-first L4 weeks | 82 | 83 |
| **N IS / OOS** | 44 / 38 | **45 / 38** |
| Acc ALL [CI] | 0.6829 [0.5854, 0.7805] | 0.6747 [0.5663, 0.7711] |
| Acc IS [CI] | 0.6364 [0.5000, 0.7727] | 0.6444 [0.4889, 0.7778] |
| **Acc OOS [CI]** | 0.7368 [0.5789, 0.8684] | **0.7105 [0.5526, 0.8421]** |
| Foil acc IS / OOS (vs E=0.25) | 0.3409 / 0.2105 | 0.3333 / 0.2105 |
| Δ ALL [CI] | 0.4024 [0.2683, 0.5366] | 0.3976 [0.2530, 0.5301] |
| Δ IS [CI] | 0.2955 [0.0909, 0.5000] | 0.3111 [0.1111, 0.5111] |
| **Δ OOS [CI]** | 0.5263 [0.3684, 0.6842] | **0.5000 [0.3158, 0.6842]** |
| WF median Δ (OOS, 15-week full blocks) | 0.5667 | 0.5333 |
| WF median Δ (OOS, 10-week blocks, alt) | 0.5000 | 0.4875 |
| Fri-close P0 OOS acc | 0.7632 | 0.7632 |
| RTH-agg OOS N / acc / foil / Δ [CI] (reconstructed both sides) | 41 / 0.7073 / 0.2683 / 0.4390 [0.2683, 0.6098] | 41 / 0.7073 / 0.2683 / 0.4390 [0.2683, 0.6098] |
| Gates: OOS N≥80 / Δ>0 / CI>0 / WF>0 | FAIL / PASS / PASS / PASS | FAIL / PASS / PASS / PASS |
| Decision | INCONCLUSIVE (N_OOS < 80) | **INCONCLUSIVE (N_OOS < 80)** |

## What moved
- Daily bars, out of 923:
  - open changed on 703 and close on 698, because the first and last minute of each day moved.
  - high changed on 9 and low on 2.
  - The 09:30 open changed on 745.
- Weeks, out of 154:
  - P0 changed on 148.
  - L* changed on 4.
  - Unique status changed on 1: 2024-W14 (IS) was a PWH/PWL tie and is now resolved to PWH.
  - Success changed on 2: 2023-W44 (IS) 0→1; **2024-W44 (OOS) 1→0**, where L* went PMH→PWH after P0 moved 21819.75→21823.25.
  - first_tag and the foil draws are unchanged.

---
*Exploratory CONTINUOUS-KAGGLE only. Daily-agg from 1m. Not Sunday-open identity; not Yahoo weekly; not MNQ Mar 2026. No MERCURY.*
