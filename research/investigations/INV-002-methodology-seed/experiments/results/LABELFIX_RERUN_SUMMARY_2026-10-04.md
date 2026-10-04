# LABELFIX RE-RUN SUMMARY — 2026-10-04 (QUANT)
`CONTINUOUS-KAGGLE-NQ1M · labels=bar-close (corrected 2026-10-04) · roll undocumented · truncation CONFIRMED (ends 2025-12-11) · not MNQ Mar 2026 · not stream C · No MERCURY`

**Basis:** DATA `ADDENDUM_2026-10-04_LABEL_CONVENTION.md` and `DATA_RULINGS_MARKETDATA_2026-10-04.md` §2.
- Every Wave 1 script was re-run in bar-open time (ts = raw label − 1 min), with frozen logic, seeds, splits, event calendar and holiday rules.
- End-of-window comparisons follow DATA §2: "ends at X" = last bar opening X−1. The pure-shift variant gives identical decision numbers for H003c, H004b and H002b.
- Old numbers were verified by replaying the original scripts. The replayed day rows are byte-identical to the 2026-09-13 files, and H009b was reconstructed exactly.
- Raw CSV vs marketdata parquet: 1,048,575/1,048,575 rows match (ts_ny = label − 1 min; O/H/L/C mismatches 0).

| Hyp | Old decision | New decision | Key number OLD → NEW | Verdict |
|---|---|---|---|---|
| **H001b** RTH ORG CE (`results/H001b_RERUN_LABELFIX_2026-10-04.md`) | PRIMARY VERIFY COMPLETE (frequency filed) · SECONDARY FAILS (CE-specialness) | PRIMARY **VERIFY COMPLETE (frequency filed)** · SECONDARY **FAILS (CE-specialness)** | OOS P̂(hit CE by 10:00 incl.) 0.5561 [0.4878, 0.6244] N=205 → **0.5882 [0.5196, 0.6569] N=204**. CE-specialness OOS Δ −0.0683 [−0.1268, −0.0146] → **−0.0490 [−0.1029, 0.0049]** | **UNCHANGED (labels).** The filed frequency rises by +0.032. Specialness Δ is still ≤0 (FAILS), but its CI now touches 0. 0.70 stays a withdrawn FOIL only. |
| **H003c** REL/REH → 7–9 range (`results/H003c_RERUN_LABELFIX_2026-10-04.md`) | FAILS (OOS N_treat 139) | **INCONCLUSIVE (OOS N_treat 52 < 80)** | OOS Δ −0.1500 [−0.2474, −0.0520] → **−0.2692 [−0.4123, −0.1235]**; WF median −0.1429 → **−0.2630**; N_treat 343 → 123 | **CHANGED: FAILS → INCONCLUSIVE, on power.** The 09:30 cash-open bar now triggers the frozen dual-same-bar exclusion on 224 former treatment days. The direction is more negative, so this is not a rescue. PARAMETER REL detector; no red-line identity. |
| **H004b** first-10:00-hour FVG vs later control (`results/H004b_RERUN_LABELFIX_2026-10-04.md`) | FAILS | **FAILS** | OOS Δ 0.0049 [−0.0683, 0.0780] → **0.0293 [−0.0439, 0.1024]** (N=205); WF median OOS 0.0000 → **0.0500** | **UNCHANGED.** The CI includes 0. On 111/640 days the old "10:00-hour" treatment was born on the 09:59 bar; those days now get a different treatment. Not Silver Bullet proof. |
| **H002b** 7–9 state classifier (`results/H002b_RERUN_LABELFIX_2026-10-04.md`) | Board FAILS (soft empirical prior); locked hard-majority rejected | **Board FAILS** (soft empirical prior); locked hard-majority still rejected | Soft-prior lift 0.0165 [−0.0253, 0.0566] → **0.0157 [−0.0250, 0.0558]**; hard lift 18.0559 → 17.9913 [15.5459, 20.4583]; §3 hash OK | **UNCHANGED.** 7–9 values changed on many rows. Class changed on 13 of 633 primary days (4 OOS) and y on 3 (0 OOS). No strong edge; not a panacea. |
| **H009b** Kaggle daily-agg (`wave2/results/H009b_RERUN_LABELFIX_2026-10-04.md`) | INCONCLUSIVE (N_OOS 38 < 80) | **INCONCLUSIVE (N_OOS 38 < 80)** | OOS Δ 0.5263 [0.3684, 0.6842] → **0.5000 [0.3158, 0.6842]**; OOS acc 0.7368 → 0.7105 | **UNCHANGED (negligible).** One OOS week's L* flipped after a 3.5-pt P0 move. |

**DATA cross-check (H001b):** recomputed on all raw weekdays, I get exactly DATA's figures:
- Popen moves on 97.4% of days (median 3.25, p90 9.25, max 44.75).
- Pref moves on 96.7% (median 2.0).
- CE moves ≥2 ticks on 84.8%.
- 17/758 days flip gap sign.

**Flags for the board:**
1. H003c's treatment is almost always set on the first path bar: 338/343 days old, 122/123 new. That makes it very sensitive to how the opening bar is defined.
2. The H009b WF scheme and the RTH-agg foil had to be reverse-engineered, because the inline code is not on file (see that memo).
3. `/workspace/hxvenv` pip is broken (`pip._internal.operations.build` missing) and there is no pyarrow, so the parquet check used `/workspace/marketdata/.venv`.
