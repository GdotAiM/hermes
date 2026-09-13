# CASSANDRA — Red Team Review: QUANT H002 (7–9 state classifier)
**Target:** `experiments/QUANT_H002_79_STATE_CLASSIFIER_PROTOCOL_2026-09-13.md`  
**Parents:** C-METH-003, 004, 005 — **Passed Observed**  
**Date:** 2026-09-13  
**Requestor:** ORION (packaging; H004b FAILS locked; Kaggle tape next)  
**Peek/run:** none  
**Verdict:** **DID NOT SURVIVE packaging** → **HOLD — file H002b before any RUN**  
**No run auth. No MERCURY.**

---

## Severity table

| Topic | Finding | Severity |
|-------|---------|----------|
| PARAMETER class thresholds | Labeled PARAMETER (good) but taxonomy + cutoffs unlocked as decision objects; sensitivity after OOS only is right | **HIGH** |
| Primary outcome / score lock | Multiclass first-side-swept OK as target; **balanced accuracy vs log-loss unlocked**; horizons 10/11/12 unlocked | **CRITICAL** |
| Controls / baseline | Majority **or** intercept **or** persistence — unlocked | **CRITICAL** |
| Look-ahead | 7–9 features pre-09:30 OK; ATR prior-20 OK if strict; chop@T must use bars ≤T | **MEDIUM** (fixable) |
| IS/OOS | Not frozen | **HIGH** |
| SURVIVES vocab / tape | “Not panacea” present; still MNQ/stream C; no CONTINUOUS-KAGGLE | **HIGH** |
| Cross-hyp leakage | Note says freeze before H001/H003 runs — those already ran on same tape | **HIGH** |

---

## ATTACK 1 — Primary score & horizon unlocked

**PROBLEM:** §5 allows balanced accuracy **/** log-loss; §4 three horizons. FAILS/SURVIVES on undefined “lift.”

**WHY IT MATTERS:** Same CRITICAL as H004 pre-b.

**H002b lock:**
```
PRIMARY horizon T* = 12:00 ET (10:00/11:00 descriptive only).
PRIMARY target y = first side swept of 7–9 HH/LL after 09:30 by T*
  ∈ {high, low, neither} (neither if neither extreme touched by T*).
PRIMARY score = OOS multiclass log-loss of multinomial/logistic(class → y)
  vs MAJORITY-class baseline log-loss on same OOS (frozen baseline = OOS empirical mode from IS frequencies — pick one:
  RECOMMEND: baseline predicts IS majority class for all OOS days).
Lift = L_base − L_model (higher better). Optionally report balanced accuracy descriptive only.
FAILS if OOS N≥80: lift≤0 or bootstrap CI(lift) includes ≤0.
SURVIVES if lift>0, CI>0, WF median lift>0, AND prose includes “not a panacea” (005).
```

**SEVERITY:** **CRITICAL**

---

## ATTACK 2 — Baseline unlocked

**PROBLEM:** Unconditional frequencies / majority / previous-day persistence listed as alternatives.

**H002b:** One primary baseline = **IS majority class** constant predictor. Persistence = sensitivity only (cannot sole-SURVIVES).

**SEVERITY:** **CRITICAL**

---

## ATTACK 3 — PARAMETER thresholds / class taxonomy

**PROBLEM:** Observed 004 = trending / consolidating / reversing (qualitative). Protocol uses expansion↑/↓ / consolidation / compression with ATR multiples and body fraction — all PARAMETER. 005 outcomes = expansion/trend/chop — partially aligned to post-9:30 labels, not to four-class input taxonomy.

**WHY IT MATTERS:** Testing a QUANT state machine, not a lecture-numeric rule. OK if labeled; SURVIVES must say **PARAMETER classifier implementing 003–005 precursor claim**, not “Observed 7–9 classes confirmed.”

**H002b:**
- Keep four-class table; freeze numbers: ATR lookback=20; expand mult=1.0; body frac=0.5; compression=0.5.  
- Sensitivity grid only **after** primary OOS (already).  
- SURVIVES vocabulary ban: Observed trending/consolidating/reversing identity.

**SEVERITY:** **HIGH**

---

## ATTACK 4 — Look-ahead / leakage

**PROBLEM:** ATR_ref = median prior 20 days’ 7–9 R — OK if days < D. Chop uses 5m closes in [09:30,T) — lock “bars with timestamp < T”. Classifier must not use post-09:30 info.  
**Cross-hyp:** Do not retune thresholds using H001b/H003c/H004b outcomes already seen on CONTINUOUS-KAGGLE.

**H002b:** Explicit “ATR days strictly before D”; “no threshold retune from other hyp results on this tape”; freeze hash of §3 table before RUN.

**SEVERITY:** **HIGH** (process) / look-ahead mechanics **MEDIUM**

---

## ATTACK 5 — IS/OOS + tape retarget

**PROBLEM:** No calendar split; MNQ/shared tape.

**H002b:** CONTINUOUS-KAGGLE-NQ1M; truncation FLAG; IS=2023–2024 / OOS=2025; N≥80; coverage ≥20; event strata descriptive; ex Sundays (003).

**SEVERITY:** **HIGH**

---

## ATTACK 6 — SURVIVES / MERCURY

Must include **“not a panacea” (005)**. Ban deterministic post-9:30 claims. No MERCURY. MAE/MFE if added = descriptive only.

**SEVERITY:** **MEDIUM** (partially present)

---

## Decision

**HYPOTHESIS DID NOT SURVIVE RED TEAM REVIEW** (packaging).

---

## Exact H002b change list

1. Retarget **CONTINUOUS-KAGGLE-NQ1M** (+ truncation / not stream C / not MNQ Mar 2026).  
2. Freeze **T\*=12:00**; 10:00/11:00 descriptive.  
3. Freeze primary target = first-side-swept ∈ {high,low,neither}.  
4. Freeze primary score = **log-loss lift vs IS-majority baseline**; balanced accuracy descriptive.  
5. Persistence baseline = sensitivity only.  
6. Freeze PARAMETER thresholds (20 / 1.0 / 0.5 / 0.5); sensitivity grid post-primary-OOS only.  
7. Lock ATR prior-day strictness + chop bars < T; ban retune from other hyp peeks.  
8. Calendar IS/OOS 2023–24/2025; N≥80; coverage ≥20; event strata.  
9. SURVIVES vocab: PARAMETER classifier / precursor **not panacea**; not Observed class identity; no MERCURY.  
10. NEW id **H002b**; retain H002 as audit draft.

---

## Path

`investigations/INV-002-methodology-seed/reviews/CASSANDRA_H002_REDTEAM_2026-09-13.md`
