# CASSANDRA — Red Team Review: QUANT H003c (REL/REH → opposite range)
**Target:** `experiments/QUANT_H003c_REL_TO_RANGE_PROTOCOL_2026-09-13.md`  
**ATLAS lock:** `evidence/L81eMQhmXmc/H003_BOX_LOCK.md`  
**Date:** 2026-09-13  
**Requestor:** ORION (H003c primary after box lock; H003b = rival only)  
**Verdict:** **HYPOTHESIS SURVIVED RED TEAM REVIEW** (packaging / correct demo map)  
**Run clearance:** **NOT GRANTED**

---

## Scope

Packaging only. Score **H003c**, not superseded H003. H003b = Rival B only.

---

## Credit

- NEW hyp id when treatment object changed (correct vs silent H003b amend).
- ATLAS primary map implemented: REL/REH sweep → opposite beige HH/LL; Rival A/B labeled.
- Foil A imported cleanly (random-side @09:30, all range days); invalid baselines stay banned.
- Horizon 12:00-only; RANGE-DEPENDENT mid tertile; tick-round; no MERCURY; coincide-days dual log.

---

## ATTACK 1 — REL/REH detector is researcher-invented (not ATLAS-locked)

**PROBLEM:** ATLAS locks *which chart objects* matter (red REL vs beige box). QUANT §3.2 invents detection: fractal swing + \(\tau_{eq}=2.0\) pts + “lowest/highest mean pair” tie-breaks. Demo red-line level is not yet shown to equal computed \(L_{rel}\) on the lecture day. \(\tau_{eq}\) and pair selection are free PARAMETERS.

**WHY IT MATTERS:** Wrong detector → testing a different claim than bread-and-butter. Overfitting surface before any tape expansion.

**EVIDENCE REQUIRED:** Spot-check on L81eMQhmXmc session: computed \(L_{rel}\) vs on-screen red REL (points). File path under evidence. If \|diff\| > 1 tick, retune under ORION ack **pre-peek** or NEW id if after peek.

**TEST:** RUN blocked until detector-vs-demo note filed. Sensitivity \(\tau_{eq}\in\{1,2,4\}\) may stay descriptive **after** primary OOS only if detector passes demo spot-check at frozen \(\tau_{eq}=2\).

**SEVERITY:** **HIGH**

---

## ATTACK 2 — SELECTION-DEPENDENT (Foil A pool mismatch) carried from H003b

**PROBLEM:** \(P_{treat}\) on REL/REH-sweep days vs \(P_{ctrl}\) on all range days. Active mornings selected; quiet days drag \(P_{ctrl}\) down. H003c §5 lacks explicit **SELECTION-DEPENDENT** label.

**WHY IT MATTERS:** False lecture confirmation from selection, not from REL→range package.

**EVIDENCE REQUIRED:** Mandatory sensitivity: Foil A control universe restricted to days that touch ≥1 of \(\{H_{79},L_{79}\}\) by \(T^*\) (and/or days with any REL/REH present). If only full-universe Δ works → **SELECTION-DEPENDENT**.

**TEST:** Add to §5 before RUN (same file, ORION ack, no peek).

**SEVERITY:** **HIGH**

---

## ATTACK 3 — “Lowest mean REL pair” selection rule

**PROBLEM:** Multiple equal-low pairs → always take lowest mean. Demo may use a mid-box REL that is not the lowest cluster.

**WHY IT MATTERS:** Systematic mis-pick on multi-REL days.

**EVIDENCE REQUIRED:** Demo spot-check (Attack 1) + rival rule “closest pair to mid-range” as descriptive.

**TEST:** If demo REL ≠ lowest-mean pair, change selection rule pre-peek (ORION ack) without claiming SURVIVES yet.

**SEVERITY:** **MEDIUM**

---

## ATTACK 4 — Pierce / touch on REL

**PROBLEM:** Touch primary; pierce co-report. Spoken “swept below” suggests pierce. Same as prior sweep-def issue.

**WHY IT MATTERS:** PARAMETER.

**EVIDENCE REQUIRED:** Already co-reported — keep SWEEP-DEF-DEPENDENT in SURVIVES prose rules (present). OK.

**SEVERITY:** **LOW** (handled)

---

## ATTACK 5 — Coverage: many days lack REL/REH under fractal+τ_eq

**PROBLEM:** Strict fractal equals may yield sparse \(N_{treat}\). Pressure to loosen \(\tau_{eq}\) after seeing coverage.

**WHY IT MATTERS:** Optional stopping / post-hoc tolerance.

**EVIDENCE REQUIRED:** Coverage projection reports % days with ≥1 REL or REH **before** any Δ. Freeze \(\tau_{eq}\) before projection peek of outcomes (coverage-only OK).

**TEST:** Operational checklist.

**SEVERITY:** **MEDIUM**

---

## H003b scoring (per ORION)

**Rival-map only.** Prior packaging SURVIVE on Foil A hygiene stands for import into H003c. **No lecture SURVIVES** from H003b / Rival B alone.

---

## RUN blockers

1. REL detector vs demo red-line spot-check (Attack 1)  
2. SELECTION-DEPENDENT §5 lock (Attack 2)  
3. Shared stream C + coverage projection  
4. No MERCURY  

---

## Decision

**HYPOTHESIS SURVIVED RED TEAM REVIEW** (correct primary map + control family).

**Do not RUN** until blockers above clear. Do not score H003/H003b as demo confirmation.

---

## Path

`investigations/INV-002-methodology-seed/reviews/CASSANDRA_H003c_REDTEAM_2026-09-13.md`
