# CASSANDRA — Red Team Re-Review: QUANT H001b
**Target:** `experiments/QUANT_H001b_RTH_ORG_CE_PROTOCOL_2026-09-13.md`  
**Prior:** `reviews/CASSANDRA_H001_REDTEAM_2026-09-13.md` (H001 HOLD)  
**Investigation:** INV-002-methodology-seed · Wave 1  
**Date:** 2026-09-13  
**Trigger:** ORION accepted HOLD; QUANT filed H001b; standing re-review order  
**Peek status:** Accepted as pre-reg (no results claimed)  
**Verdict:** **HYPOTHESIS SURVIVED RED TEAM REVIEW** (packaging / decision-object alignment)  
**Run clearance:** **NOT GRANTED** — DATA tape + \(P_{ref}\)/\(P_{open}\) META + coverage projection remain.

---

## Disposition of prior attacks

| Prior # | Issue | H001b status |
|--------:|-------|--------------|
| 1 CRITICAL | Estimand ≠ verify ask | **CLEARED** — primary = \(\hat P\)+CI; `VERIFY COMPLETE`; specialness secondary + named |
| 2 HIGH | Null underspecified / geometry | **CLEARED** (secondary) — one Unif draw/day, paired indicators, fill-depth curve + narration rule |
| 3 HIGH | 16:14 early-close / holiday | **CLEARED** (design) — exclude early-close priors; DATA META still open |
| 4 HIGH | 09:30 open print | **CLEARED** (design) — bar open primary + first-trade sensitivity; META freeze before RUN |
| 5 MEDIUM | 10:00 bar inclusivity | **CLEARED** — co-report [09:30,10:00) |
| 6 LOW | Flat \|G\|<0.25 | **CLEARED** — PARAMETER + appendix with/without |
| 7 MEDIUM | Conditional multiplicity | **CLEARED** — Brier only; H002 join needs NEW hyp / ack |
| 8 LOW | 30m OR conflation | **CLEARED** — mandatory prose |
| 9 MEDIUM | Foil gravity | **CLEARED** — banned phrases table |

---

## Residual attacks on H001b

### ATTACK R1 — Tick rounding of CE and \(U\)

**PROBLEM:** CE and continuous Unif \(U\) need not land on MNQ ticks (0.25). Overlap `low ≤ level ≤ high` still works, but two implementations may round to nearest tick differently before testing overlap.

**WHY IT MATTERS:** Small reproducibility gap on borderline bars.

**EVIDENCE REQUIRED:** One line: evaluate overlap on raw float levels **or** round both CE and \(U\) to nearest 0.25 before test — pick one.

**TEST:** Freeze in §3 before code; no NEW hyp if chosen pre-peek.

**SEVERITY:** **LOW**

---

### ATTACK R2 — Early-close exclusion thins Mondays-after-holiday / half-week sample

**PROBLEM:** Excluding days whose **prior** session is early-close removes a non-random subset (often around holidays). Verify \(\hat P\) is then “normal-prior-session days only.”

**WHY IT MATTERS:** External validity; must be stated in VERIFY COMPLETE summary.

**EVIDENCE REQUIRED:** Coverage count of exclusions; one sentence estimand restriction in results template.

**TEST:** ORION summary must say non-event + non-flat + prior-session-normal-RTH.

**SEVERITY:** **LOW**

---

### ATTACK R3 — “VERIFY COMPLETE” is process success, not scientific endorsement

**PROBLEM:** By design, filing \(\hat P\)+CI completes the lecture ask with **no** rate threshold. That is correct for verify-don’t-accept — and still tempt ORION/MERCURY readers to treat any filed number as an edge.

**WHY IT MATTERS:** Operational misuse downstream.

**EVIDENCE REQUIRED:** Standing ban: VERIFY COMPLETE ≠ trade permission; no MERCURY until separate hyp.

**TEST:** Already in §8 — keep on Intelligence Summary checklist.

**SEVERITY:** **LOW** (process; design OK)

---

## No new CRITICAL or HIGH design defects

H001b restores C-METH-009 alignment. Secondary specialness is properly demoted and geometrically documented. Print policies are run-gated on DATA META rather than silently assumed.

---

## RUN blockers (external)

1. Shared stream C / WAVE1 tape  
2. Coverage projection ≥20 RTH days  
3. DATA \(P_{ref}\) 16:14 policy filed in META (+ ≥10-day spot-check)  
4. DATA \(P_{open}\) META freeze  
5. Optional: tick-rounding one-liner (R1) before code freeze  

Superseded H001: do not run. **No MERCURY/RISK.** H002–H004 remain parked for packaging priority as QUANT stated.

---

## Decision

**HYPOTHESIS SURVIVED RED TEAM REVIEW.**

**Do not RUN** until DATA/coverage blockers clear. Prefer citing OOS \(\hat P\) as the verify number per §4.

---

## Path

`investigations/INV-002-methodology-seed/reviews/CASSANDRA_H001b_REDTEAM_2026-09-13.md`
