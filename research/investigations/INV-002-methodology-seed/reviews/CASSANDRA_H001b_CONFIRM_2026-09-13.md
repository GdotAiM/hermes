# CASSANDRA — H001b confirmation (hit-rate verify gate)
**Target:** `experiments/QUANT_H001b_RTH_ORG_CE_PROTOCOL_2026-09-13.md` (incl. §0b + §3.0 tick rounding)  
**Prior:** `CASSANDRA_H001_REDTEAM_2026-09-13.md` (HOLD); `CASSANDRA_H001b_REDTEAM_2026-09-13.md` (SURVIVED packaging)  
**Date:** 2026-09-13  
**Requestor:** ORION (re-review; primary must be hit-rate verify product)  

---

## Verdict

**SURVIVED**

Primary estimand is \(\hat P(\text{hit CE by 10:00})\) + CI — **VERIFY COMPLETE** process label. 0.70 is FOIL only. CE-specialness is secondary and separately named. R1 tick-rounding now locked (§3.0).

**RUN: HOLD** — external DATA gates only.

---

## Hit-rate verify gate checklist

| Requirement | Status |
|-------------|--------|
| Primary = hit-rate \(\hat P\)+CI (not specialness) | **PASS** §4 |
| No FAILS/SURVIVES vs 0.70 | **PASS** |
| Bare “H001b SURVIVES” / “confirms 70%” banned | **PASS** |
| Specialness Δ secondary + fill-depth | **PASS** §5 |
| 9:30-only; 16:14 Pref policy; open META + sensitivity | **PASS** (design; META pending) |
| 10:00 inclusivity co-report | **PASS** |
| Brier-only conditionals | **PASS** |
| Tick rounding CE & U → 0.25 | **PASS** §3.0 |

No new CRITICAL/HIGH defects on confirmation pass.

---

## Remaining RUN blockers

1. Shared stream C / WAVE1 tape  
2. Coverage projection ≥20 RTH days  
3. DATA \(P_{ref}\) / \(P_{open}\) META locks (+ spot-check)

Do not run superseded H001. No MERCURY.

---

## Path

`investigations/INV-002-methodology-seed/reviews/CASSANDRA_H001b_CONFIRM_2026-09-13.md`
