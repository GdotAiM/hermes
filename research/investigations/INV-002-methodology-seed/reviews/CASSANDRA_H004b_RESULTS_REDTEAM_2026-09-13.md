# CASSANDRA — Result Red Team: H004b Exploratory
**Target:** `experiments/results/H004b_EXPLORATORY_RESULTS_2026-09-13.md`  
**Protocol:** `QUANT_H004b_FIRST_1000_FVG_PROTOCOL_2026-09-13.md`  
**Date:** 2026-09-13  

---

## Verdict

**AGREE: FAILS**

| Gate (OOS) | Memo | CASSANDRA |
|------------|------|-----------|
| N_pairs≥80 | 205 | **PASS** |
| Δ>0 | 0.0049 | Numeric yes — **economically null** |
| CI entirely >0 | [−0.068, 0.078] | **FAIL** |
| WF median Δ>0 | 0.000 | **FAIL** |
| RTH sensitivity | Δ=−0.029 CI includes 0 / negative point | Not a rescue |

**Decision class:** first-10:00-hour FVG is **not distinguishable** from later same-polarity FVG on primary m (60m revisit) under CONTINUOUS-KAGGLE.  
**Not** Silver Bullet proof. **No MERCURY.**

---

## Requested hygiene checks

| Check | Status |
|-------|--------|
| m = 60m revisit-after-leave | **PASS** |
| Later same-polarity [11:00,15:00) primary | **PASS** |
| Classic-wick birth; VI expands only | **PASS** (stated) |
| CONTINUOUS-KAGGLE / truncation / not stream C / not MNQ Mar 2026 | **PASS** |
| OOS N_pairs≥80 | **PASS** (205) |
| Never-leave treat vs ctrl | **0 / 0** — not WIDTH-DEPENDENT by rule |

---

## Residual attacks

### ATTACK 1 — “Almost SURVIVES” gravity
**PROBLEM:** Tiny positive OOS Δ with CI through zero + WF median 0 invites soft language (“directionally positive”).  
**WHY IT MATTERS:** Same optional-narrative failure as H009b strong-Δ INCONCLUSIVE.  
**TEST:** Lead with **FAILS**; ban “near miss / promising.”  
**SEVERITY:** **HIGH** (prose)

### ATTACK 2 — no_first10_fvg = 0
**PROBLEM:** Every paired-eligible day has a first FVG in [10:00,11:00). Population is not sparse.  
**WHY IT MATTERS:** “First in 10:00 hour” may be nearly “any early AM FVG clock slot” on 1m NQ — weak selection of a special object. Does not overturn FAILS (still no lift vs later).  
**SEVERITY:** **MEDIUM** (interpretation)

### ATTACK 3 — Body-expanded share = 1.000
**PROBLEM:** Every treatment zone reports body-expand.  
**WHY IT MATTERS:** Either VI almost always present after classic FVG, or expand logic over-triggers — worth a one-line code QA. Treat mean width 14.2 vs later 8.1 — systematic width gap; revisit m still null vs later.  
**SEVERITY:** **MEDIUM**

### ATTACK 4 — Truncation
OOS 2025 ends ~2025-12-11 — label in board TLDR (same as H001b/H003c).  
**SEVERITY:** **LOW**

### ATTACK 5 — RTH control beats treatment (full sample CI<0)
Consistent with no 10:00-hour specialty vs generic RTH FVG. Reinforces FAILS; do not cherry-pick.  
**SEVERITY:** **LOW** (supports decision)

---

## Decision table

| Claim | Allowed? |
|-------|----------|
| **FAILS** (first-10:00-hour vs later on m) | **YES** |
| SURVIVES / Silver Bullet confirmed | **NO** |
| MERCURY | **NO** |
| “Δ>0 so interesting” without FAILS | **NO** |

---

## Path

`investigations/INV-002-methodology-seed/reviews/CASSANDRA_H004b_RESULTS_REDTEAM_2026-09-13.md`
