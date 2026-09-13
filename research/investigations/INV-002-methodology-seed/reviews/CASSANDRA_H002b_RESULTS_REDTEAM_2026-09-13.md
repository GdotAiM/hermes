# CASSANDRA — Result Red Team: H002b Exploratory
**Target:** `experiments/results/H002b_EXPLORATORY_RESULTS_2026-09-13.md`  
**Protocol:** `QUANT_H002b_79_STATE_CLASSIFIER_PROTOCOL_2026-09-13.md`  
**Date:** 2026-09-13  

---

## Verdict

**DISAGREE with SURVIVES as a scientific / board decision.**

| Call | CASSANDRA |
|------|-----------|
| Protocol-mechanical SURVIVES vs hard one-hot IS-majority log-loss | Numerically real — **scientifically INVALID baseline** |
| **Board decision** | **FAILS** (or at best **INCONCLUSIVE / HOLD**) under any serious constant baseline |
| Empirical-prior descriptive lift ≈0.017 CI includes ≤0 | Would **FAILS** if that were primary |
| Balanced accuracy ≈0.37 (3-class) | ≈ chance — **no useful discrimination** |
| MERCURY / Observed class identity / panacea | **Banned** — memo OK on vocab |

**Do not board-lock SURVIVES.** Prefer **FAILS (predictive lift vs proper constant prior)** or reopen as **H002c** with baseline redefined **before** any new look at OOS.

---

## ATTACK 1 — Hard one-hot majority baseline inflates log-loss (CRITICAL)

**PROBLEM:** Primary baseline puts probability **1** on IS modal y (`high`) and **0** on others. With clipped multiclass log-loss, every OOS day with y≠high contributes ~−log(ε) ≈ large loss → L_base≈**18.8**. Soft model L≈**0.75** yields lift≈**18** that is almost entirely **baseline pathology**, not precursor skill.

**WHY IT MATTERS:** SURVIVES gates (lift>0, CI>0, WF>0) all pass **automatically** against this strawman. Persistence sensitivity shows the **same artifact** (lift≈18). Empirical-prior constant (IS frequencies) — the standard constant baseline for log-loss — gives lift≈0.017 with CI through 0 → **FAILS**.

**EVIDENCE REQUIRED:** Already in memo § “Baseline construction note.” Day-row / y mix: OOS high≈99/207≈48% so ~52% of days pay the clipped-zero penalty under hard majority.

**TEST:**  
1. **Reject** board SURVIVES on hard-one-hot baseline.  
2. Treat empirical-prior lift as the **scientifically primary** constant-baseline comparison for this tape pass → **FAILS**.  
3. If org wants log-loss vs majority formally: **H002c** lock baseline = **IS empirical class distribution** (soft constant), freeze **before** re-looking at OOS (this OOS already peeked — for a clean H002c SURVIVES need new unseen weeks OR accept this run as FAILS under corrected baseline only).

**SEVERITY:** **CRITICAL**

---

## ATTACK 2 — Discrimination is weak (HIGH)

**PROBLEM:** Descriptive bal-acc **0.373** (3-class chance ≈0.33); accuracy ~0.54 vs majority rate ~0.48. Matches “not a panacea” and contradicts any strong SURVIVES narrative.

**WHY IT MATTERS:** Confirms Attack 1 — mechanical lift ≠ useful prediction of first-side-swept.

**SEVERITY:** **HIGH**

---

## ATTACK 3 — Rare compression OOS n=8 (MEDIUM)

**PROBLEM:** Sparse cell; multinomial coefficients for compression→y unstable. Neither y also rare (IS=3, OOS=3).

**WHY IT MATTERS:** Model fit fragility; does not rescue or create SURVIVES under proper baseline.

**SEVERITY:** **MEDIUM**

---

## ATTACK 4 — Protocol ambiguity enabled the artifact (HIGH)

**PROBLEM:** Packaging said “IS-majority class constant predictor.” For **classification error**, hard majority is fine. For **log-loss**, a constant predictor must emit the **IS empirical distribution** (or at least soft probabilities), not one-hot zeros.

**WHY IT MATTERS:** Packaging SURVIVED, but score definition was underspecified for probabilistic loss → false decision SURVIVES.

**TEST:** Amend interpretation now; H002c for formal baseline text if re-run.

**SEVERITY:** **HIGH**

---

## What still looks fine

| Item | Status |
|------|--------|
| §3 hash OK | PASS |
| CONTINUOUS-KAGGLE / truncation / non-event / T*=12:00 | PASS |
| ATR prior-day / ex Sundays | PASS (as labeled) |
| Vocab: PARAMETER / not panacea / no MERCURY / not Observed identity | PASS |
| N_OOS≥80 / coverage | PASS |

---

## Decision table

| Claim | Allowed? |
|-------|----------|
| SURVIVES (board / intelligence) | **NO** |
| SURVIVES only vs hard-one-hot strawman | Acknowledge numeric, **do not promote** |
| **FAILS** vs empirical-prior constant (descriptive primary science) | **YES — preferred board call** |
| MERCURY / Observed 004 classes confirmed | **NO** |

---

## Path

`investigations/INV-002-methodology-seed/reviews/CASSANDRA_H002b_RESULTS_REDTEAM_2026-09-13.md`
