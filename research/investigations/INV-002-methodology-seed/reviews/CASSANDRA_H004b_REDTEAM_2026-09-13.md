# CASSANDRA — Packaging Re-Review: QUANT H004b
**Target:** `experiments/QUANT_H004b_FIRST_1000_FVG_PROTOCOL_2026-09-13.md`  
**Prior:** `CASSANDRA_H004_REDTEAM_2026-09-13.md` (DID NOT SURVIVE)  
**Date:** 2026-09-13  
**Peek/run:** none claimed  
**Verdict:** **HYPOTHESIS SURVIVED RED TEAM REVIEW** (packaging)  
**Run clearance:** **NOT GRANTED** — ORION auth still required; one **HIGH** pre-RUN hygiene amend below

---

## 8-item lock checklist

| # | Required lock | H004b status |
|---|---------------|--------------|
| 1 | CONTINUOUS-KAGGLE retarget + truncation / not stream C / not MNQ Mar 2026 | **PASS** |
| 2 | Later same-polarity [11:00,15:00) primary; random RTH sensitivity | **PASS** |
| 3 | VI merge ≤10 lines PARAMETER; no post-code demo redesign | **PASS** (text frozen) |
| 4 | Primary \(m\) = 60m revisit-after-leave; MFE/MAE descriptive | **PASS** |
| 5 | Leave / revisit / birth-close / birth-minute tie | **PASS** |
| 6 | Calendar 2023–24/2025; N≥80 pairs; coverage ≥20 | **PASS** |
| 7 | SURVIVES vocab = first-10:00-hour vs later (not Silver Bullet) | **PASS** |
| 8 | NEW id H004b; H004 audit only | **PASS** |

Prior CRITICAL control / metric / VI-vagueness / identity issues are **cleared**.

---

## Residual attack (pre-RUN hygiene)

### ATTACK R1 — Body gap alone as birth (011 fidelity)

**PROBLEM:** §3.1 line “Birth if classic FVG **OR** body gap.” C-METH-011 is: when marking an FVG, **include** volume imbalance where bodies don’t meet — it does not say a body gap alone is a fair value gap. Allowing body-only births expands the “first FVG in 10:00 hour” population beyond 010/011.

**WHY IT MATTERS:** Wrong object / PARAMETER inflation of treatment count; can change who is “first.”

**EVIDENCE REQUIRED / one-line amend (no peek, same H004b file + ORION ack):**

```
Birth requires classic wick FVG at t.
If body gap exists (same polarity), expand zone = UNION(wick_gap, body_gap) as single interval.
Do not birth on body gap alone.
```

**TEST:** Amend before exploratory RUN. Until then: packaging SURVIVED, but **RUN blocked** on R1.

**SEVERITY:** **HIGH**

---

### ATTACK R2 — Never-leaves → m=1

**PROBLEM:** Wide zones / sticky prices get automatic success without a leave-revisit cycle.

**WHY IT MATTERS:** Inflates \(m\) for large VI-expanded zones; control shares the rule so Δ may be partially protected, but width dependence remains.

**EVIDENCE REQUIRED:** Report never-leave rate treat vs control; if treat never-leave ≫ control, label **WIDTH-DEPENDENT** descriptive. Optional future hyp: never-leave = 0 or NA.

**SEVERITY:** **MEDIUM** (does not block packaging SURVIVE)

---

### ATTACK R3 — Truncation / OOS 2025

Same CONTINUOUS-KAGGLE end ~2025-12-11 — label in every results memo.

**SEVERITY:** **LOW** (known)

---

## Decision

**HYPOTHESIS SURVIVED RED TEAM REVIEW** (packaging / decision-object locks).

**Do not RUN** until:
1. R1 birth-rule amend (classic FVG required),  
2. ORION exploratory authorization,  
3. Coverage projection ≥20 days.

**No MERCURY.** Do not run superseded H004.

---

## Path

`investigations/INV-002-methodology-seed/reviews/CASSANDRA_H004b_REDTEAM_2026-09-13.md`
