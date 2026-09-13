# CASSANDRA — Result Red Team: H009b Kaggle daily-agg powered re-run
**Target:** `experiments/wave2/results/H009b_KAGGLE_DAILY_AGG_RESULTS_2026-09-13.md`  
**Date:** 2026-09-13  
**Requestor:** ORION  

---

## Verdict

**AGREE: INCONCLUSIVE (N_OOS = 38 < 80).**  

Strong Δ/CI/WF are **not** a SURVIVES path under the frozen gate. Lead every summary with INCONCLUSIVE.

**No MERCURY. CONTINUOUS-KAGGLE only. Not Sunday-open identity.**

---

## Gate / hygiene checklist

| Item | Status |
|------|--------|
| OOS N≥80 | **FAIL (38)** — decisive |
| OOS Δ>0 / CI>0 / WF median>0 | Numeric PASS — **underpowered** |
| L4 primary vs 4-way foil | **PASS** |
| Week HH/LL = daily ISO-week agg | **PASS** (§0e freeze; Yahoo 1wk.csv not used) |
| CONTINUOUS-KAGGLE / truncation / Mon-open proxy labels | **PASS** |
| Unique-first 53.2% | Formal OK (≥50%); restricted estimand |
| Foil vs E=0.25 | OOS 0.21 — closer than FREE_YF pilot; OK |
| Fri-close / RTH-agg sensitivity | Directionally similar — no ANCHOR flip claimed |

---

## Residual attacks

### ATTACK 1 — SURVIVES gravity (worse than FREE_YF pilot)
**PROBLEM:** Δ≈0.53 with tight-looking CI invites upgrade talk.  
**WHY IT MATTERS:** Optional stopping / narrative confirmation.  
**TEST:** Ban SURVIVES / “022 confirmed” without N≥80.  
**SEVERITY:** **HIGH**

### ATTACK 2 — Truncation + short OOS calendar
**PROBLEM:** Tape ends 2025-12-11; OOS only 38 unique-first weeks after mid-2024.  
**WHY IT MATTERS:** Power and regime coverage thin (esp. 2025).  
**SEVERITY:** **MEDIUM**

### ATTACK 3 — Full-ET daily agg PARAMETER
**PROBLEM:** Primary uses full ET calendar day, not RTH-only. ICT weekly DOL often framed on RTH. Sensitivity RTH N=41 Δ still large.  
**WHY IT MATTERS:** Proxy layer on top of Mon-open.  
**TEST:** Keep labeled; RTH cannot sole-SURVIVES without protocol primary switch + NEW id if after peek.  
**SEVERITY:** **LOW**

---

## Advice: amend OOS N gate (e.g. ≥40 + stricter WF)?

### Short answer

**Not acceptable to amend the N gate to graduate *this* peeked run to SURVIVES.**  
**Prefer wait for longer / denser tape (or more unique-first weeks) under the frozen N≥80 rule.**

### Why

| Option | Scientifically OK? |
|--------|-------------------|
| Lower N≥80 → ≥40 **after** seeing Δ≈0.53 on N=38 | **NO** — post-hoc gate shift / optional stopping. Calling it “pre-reg amend” does not erase the peek. |
| Add “stricter WF” to compensate for lower N on **this sample** | **NO** — WF already passed; tightening WF after peek still selects a story that fits observed strength. |
| Wait until N_OOS≥80 under **frozen** protocol (more history, less truncation, or different split that was locked **before** outcomes) | **YES** — clean path. |
| File **H009c** with N≥40 + stricter WF **only for future unseen weeks**, and permanently leave this run **INCONCLUSIVE** | **Conditionally YES** as a *new* hyp — but **this memo’s weeks are burned** for that gate; H009c SURVIVES must not use the already-seen OOS block as its decision sample. |

### Recommendation to ORION

1. Keep decision **INCONCLUSIVE**.  
2. Do **not** amend H009b N≥80 for SURVIVES on current results.  
3. Next powered attempt: extend tape / wait for post-2025-12-11 data (or accept slower accrual of unique-first weeks) until **N_OOS≥80** under current locks.  
4. If organization insists on a lower-N design: **NEW hyp id**, gates frozen **before** any look at new OOS, and exclude weeks already used in this decision table from the new OOS (or use a later calendar cut never scored before).

---

## Decision

| Claim | Allowed? |
|-------|----------|
| **INCONCLUSIVE (N_OOS<80)** | **YES — required** |
| SURVIVES Observed nearest-side (022) | **NO** |
| Amend N gate → SURVIVES on this run | **NO** |
| MERCURY | **NO** |

---

## Path

`investigations/INV-002-methodology-seed/reviews/wave2/CASSANDRA_H009b_KAGGLE_RESULTS_REDTEAM_2026-09-13.md`
