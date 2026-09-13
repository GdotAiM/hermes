# CASSANDRA — Result Red Team: H003c Exploratory (Kaggle NQ 1m)
**Target:** `experiments/results/H003c_EXPLORATORY_RESULTS_2026-09-13.md`  
**Protocol:** `QUANT_H003c_REL_TO_RANGE_PROTOCOL_2026-09-13.md`  
**Date:** 2026-09-13  
**Requestor:** ORION (PARAMETER detector, Foil A, SELECTION-DEPENDENT)

---

## Verdict

**AGREE: FAILS (primary REL/REH→range + Foil A).**

| Check | Result |
|-------|--------|
| OOS Δ | **≈ −0.150** CI **[−0.247, −0.052]** entirely **< 0** |
| WF median Δ | **−0.143** (< 0) |
| Calendar OOS 2025 | also FAILS (Δ CI < 0; N_treat=114≥80) |
| SELECTION-DEPENDENT | still FAILS (Δ < 0, CI < 0) |
| Mid R79 tertile | Δ < 0, CI < 0 — not a WIDTH-only artifact |
| PARAMETER / no red-line / no MERCURY | **Labeled correctly** |

**Do not** narrate as lecture bread-and-butter confirmation. **Do not** MERCURY. CONTINUOUS-KAGGLE only.

---

## ORION focus attacks

### 1) PARAMETER detector

**PROBLEM:** Memo correctly tags fractal+τ_eq=2.0 as PARAMETER. Day rows show `has_rel=True` on **all 641** eligible-range days (same for REH). Detector is effectively **always-on** in 07:00–09:00 once a range exists — not a sparse “REL pool” filter. Spot-checks: \(L_{rel}\) hugs mid-range (median |L_rel−mid|≈2 pts on sample).

**WHY IT MATTERS:** Test is closer to “sweep mid-box PARAMETER level → opposite extreme” than ATLAS red-line REL. FAILS still informative for **this** PARAMETER map; must not be sold as red-line identity (already banned — keep it).

**EVIDENCE REQUIRED:** Already: detector PARAMETER + H003c_REL_DETECTOR_LOCK. Optional: report distribution of |L_rel−mid|/R79.

**TEST:** Intelligence prose: **FAILS (PARAMETER detector)** — never “REL lecture failed” without PARAMETER tag.

**SEVERITY:** **HIGH** (interpretation) — does **not** overturn FAILS for the locked map

### 2) Foil A

**PROBLEM:** Foil A @09:30 on all eligible range days; P̂_ctrl OOS≈0.75 vs P̂_treat≈0.60. Treatment after REL/REH sweep underperforms random-side opposite hit. Seeds documented.

**WHY IT MATTERS:** FAILS is against the pre-registered control family CASSANDRA required — not a stacked no-sweep baseline.

**EVIDENCE REQUIRED:** Implementation matches protocol (S at 09:30; I_ctrl=opposite touch by 12:00). Appears OK from memo + spot-check columns.

**TEST:** Spot-check I_ctrl vs S on Appendix rows — consistent.

**SEVERITY:** **LOW** (control OK; result adverse)

### 3) SELECTION-DEPENDENT

**PROBLEM:** Gate re-run with ctrl = days touching ≥1 of {H79,L79}; Δ still negative with CI<0 (full and calendar OOS). Tertile reweight also negative.

**WHY IT MATTERS:** FAILS is **not** rescued by the selection fix. Good — closes the “active morning confound” escape hatch for a false SURVIVES; here it confirms adverse Δ.

**SEVERITY:** **NONE** for overturning FAILS — **PASS** as executed

---

## Additional attacks

### ATTACK D1 — Dual-sweep exclusions (n=298)
Large treat filter (HH/LL before REL/REH). Estimand = “REL/REH-first days only.” State in TLDR. Does not flip FAILS.

**SEVERITY:** **MEDIUM** (estimand clarity)

### ATTACK D2 — Tape truncation (2025-12-11)
Same as H001b. Calendar OOS still FAILS — robustness helps.

**SEVERITY:** **MEDIUM** (label OOS end date)

### ATTACK D3 — Rival B also FAILS (worse)
HH/LL-sweep map also Δ≪0 — consistent “opposite-after-first-extreme” under Foil A is not an edge on this tape/detector.

**SEVERITY:** **LOW** (supports not cherry-picking Rival B)

### ATTACK D4 — Narrative inversion
FAILS can be spun as “fade the setup.” Ban trade advice; FAILS ≠ short-the-bread-and-butter without NEW hyp.

**SEVERITY:** **HIGH** (prose)

---

## Decision

| Claim | Allowed? |
|-------|----------|
| **FAILS** PARAMETER REL/REH→range vs Foil A on CONTINUOUS-KAGGLE | **YES** |
| Lecture red-line / Observed detector confirmation | **NO** |
| SURVIVES | **NO** |
| MERCURY / fade-the-setup trade | **NO** without NEW hyp |

**HYPOTHESIS FAILED decision review** under pre-registered gates (correct). Packaging SURVIVED earlier; exploratory result is a clean adverse.

---

## Path

`investigations/INV-002-methodology-seed/reviews/CASSANDRA_H003c_RESULTS_REDTEAM_2026-09-13.md`
