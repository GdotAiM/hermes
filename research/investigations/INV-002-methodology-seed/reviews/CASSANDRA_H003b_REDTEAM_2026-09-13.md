# CASSANDRA — Red Team Re-Review: QUANT H003b
**Target:** `experiments/QUANT_H003b_79_SWEEP_OPPOSITE_PROTOCOL_2026-09-13.md`  
**Priors:** `CASSANDRA_H003_REDTEAM_2026-09-13.md`, `CASSANDRA_H003_RECONTROL_2026-09-13.md`  
**Date:** 2026-09-13  
**Requestor:** ORION (packaging re-review; ATLAS equal-lows still RUN gate)  
**Peek status:** Pre-reg claimed; no results  
**Verdict:** **HYPOTHESIS SURVIVED RED TEAM REVIEW** (packaging)  
**Run clearance:** **NOT GRANTED** — ATLAS equal-lows + tape/coverage + residual HIGH lock below.

---

## Disposition of prior attacks

| Prior | Issue | H003b status |
|-------|-------|--------------|
| CRITICAL control fork | Two primaries in one cell | **CLEARED** — single §4.1 |
| CRITICAL no-sweep both-extremes | Structurally ≈0 baseline | **CLEARED** — KILLED as Δ baseline |
| CRITICAL/HIGH paired random on sweep days | E[Δ]≤0 / ill-posed | **CLEARED** — KILLED; not primary |
| HIGH range confounding | Width selection | **CLEARED** (gate) — tertiles + RANGE-DEPENDENT mid tertile |
| HIGH horizon multiplicity | 10/11/12 | **CLEARED** — \(T^*=12:00\) only for SURVIVES |
| HIGH equal-lows vs HH/LL | Lecture map | **GATED** — ATLAS before RUN (correct) |
| MEDIUM pierce | Touch vs takeout | **CLEARED** — mandatory co-report |
| MEDIUM MAE/MFE trade creep | | **CLEARED** — descriptive; no MERCURY |
| LOW window half-open | | **CLEARED** — PARAMETER + co-report |

---

## Residual attacks

### ATTACK R1 — Treatment vs control pool mismatch (selection into sweep)

**PROBLEM:** Primary Δ compares \(P_{treat}\) on **first-sweep days only** to \(P_{ctrl}\) on **all** eligible 7–9 days (random side at 09:30). Treatment days have already expanded to a 7–9 extreme; many control days never touch either extreme, so \(I_{ctrl}=0\) often. Positive Δ can mean “sweep days are active mornings,” not “opposite-after-first-sweep is special.”

§4.1 width tertiles + RANGE-DEPENDENT reduce but do not eliminate this. Reweight/match is **optional**. §4.3 (days touching ≥1 extreme) is closer to a fair foil but is co-report only.

**WHY IT MATTERS:** Same family of selection bias that motivated range strata; leftover confirmation path for a false bread-and-butter edge.

**EVIDENCE REQUIRED:** Pre-RUN lock one of:
1. **Mandatory sensitivity:** recompute primary-style Δ with control universe = days that touch **≥1** of \(\{H_{79},L_{79}\}\) by \(T^*\) (same random-side rule); or  
2. Elevate §4.3 to co-primary gate: lecture SURVIVES requires §4.1 **and** \(\Delta_{pair}>0\) CI>0; or  
3. Mandatory tertile-matched/reweighted control (not optional).

If full-universe Δ “survives” but ≥1-extreme-matched Δ fails → label **SELECTION-DEPENDENT** — not lecture confirmation.

**TEST:** Amend §5 with SELECTION-DEPENDENT rule before RUN (ORION ack, no peek → same H003b file OK).

**SEVERITY:** **HIGH** (does not reopen CRITICAL control invalidity; blocks naive SURVIVES prose)

---

### ATTACK R2 — Bootstrap wording soft

**PROBLEM:** “stratified or on day pools as follows” allows two resampling stories.

**WHY IT MATTERS:** Minor degrees of freedom.

**EVIDENCE REQUIRED:** One line: resample treatment days and control days independently with replacement; Δ = mean difference.

**TEST:** Freeze pre-code.

**SEVERITY:** **LOW**

---

## Credit

- Implemented recommended control family (random-side @ 09:30, all range days) with killed invalid baselines.
- Horizon / range / pierce / MERCURY / coverage hygiene now Wave-1-grade.
- ATLAS equal-lows correctly left as RUN gate, not silently assumed.

---

## RUN blockers

1. ATLAS equal-lows vs HH/LL note (ORION: required even if packaging survives)  
2. Shared stream C + coverage projection  
3. SELECTION-DEPENDENT lock (Attack R1) — pre-RUN hygiene  
4. No MERCURY  

Superseded H003: do not run.

---

## Decision

**HYPOTHESIS SURVIVED RED TEAM REVIEW** (packaging / control validity).

**Do not RUN** until ATLAS + tape/coverage + R1 SELECTION-DEPENDENT rule are locked.

---

## Path

`investigations/INV-002-methodology-seed/reviews/CASSANDRA_H003b_REDTEAM_2026-09-13.md`
