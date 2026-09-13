# CASSANDRA — Red Team Review: QUANT H004 (First 10:00-hour FVG)
**Target:** `experiments/QUANT_H004_FIRST_1000_FVG_PROTOCOL_2026-09-13.md`  
**Parents:** C-METH-010, C-METH-011 — **Passed Observed**  
**Date:** 2026-09-13  
**Requestor:** ORION (packaging priority; H009b board-locked INCONCLUSIVE; work with Kaggle tape)  
**Peek/run:** none — packaging only  
**Verdict:** **DID NOT SURVIVE packaging** → **HOLD — file H004b before any exploratory RUN**

---

## Board context

H009b = INCONCLUSIVE (locked). No N-gate amend. No MERCURY. Next = H004 on `CONTINUOUS-KAGGLE-NQ1M` (same 1m tape as H001b/H003c). Protocol still says MNQ/shared stream C — must retarget labels in H004b.

---

## Severity table (ORION must-locks)

| # | Topic | Finding | Severity |
|---|-------|---------|----------|
| 1 | Primary control | Later-same-day vs random RTH both listed; “CASSANDRA to set” — **not locked** | **CRITICAL** |
| 2 | FVG + volume-imbalance body rule | Classic 3-candle OK; body-gap **merge** text is vague / researcher-discretion | **CRITICAL** |
| 3 | Birth-time / first-in-[10:00,11:00) | Earliest birth in hour mostly OK; several selection/look-ahead holes | **HIGH** |
| 4 | Horizons + falsification | Primary metric **not locked** (revisit vs MFE−\|MAE\|); multi-horizon multiplicity | **CRITICAL** |
| 5 | Forces H004b? | **YES** — items 1, 2, 4 alone | — |

---

## ATTACK 1 — Primary control unlocked

**PROBLEM:** §4 lists ORION primary (later FVG birth ∈ [11:00,15:00)) and CASSANDRA alternate (random RTH). Protocol defers final choice. No polarity match rule. No rule when zero later FVGs exist. No paired bootstrap detail.

**WHY IT MATTERS:** Same failure mode as early H003 — researcher can pick the quieter null after peek.

**EVIDENCE REQUIRED / H004b lock:**

```
PRIMARY control: one FVG drawn uniformly from same-day births in [11:00, 15:00) ET,
  same polarity as treatment, excluding treatment; seed H004b_later_{date}.
  If empty → day contributes no pair (coverage: "first10 but no later same-polarity FVG").
SENSITIVITY: random RTH FVG birth ∈ [09:30, 15:30) ex treatment, same polarity
  (broader null; cannot sole-SURVIVES).
SECONDARY: second FVG in [10:00,11:00) if exists — descriptive only.
Δ primary = m_treat − m_later on paired days only.
```

**SEVERITY:** **CRITICAL**

---

## ATTACK 2 — Volume imbalance = Observed intent, mechanics = PARAMETER

**PROBLEM:** C-METH-011 Observed: include volume imbalance when bodies don’t meet. §3.1 “exact body rule” then allows classic FVG **or** contiguous body gap involving t−1/neighbors with merge left to “DATA/ATLAS may refine.” That is not exact.

**WHY IT MATTERS:** Zone width and even birth identity can change; post-hoc refine after demo peek = leakage.

**EVIDENCE REQUIRED / H004b lock (label PARAMETER where not forced by 011):**

```
Body[i] = [min(O,C), max(O,C)].
Classic FVG as §3.1 bull/bear on highs/lows.
Volume imbalance (PARAMETER implementation of 011):
  Bullish: if Body[t].low > Body[t-2].high, expand zone top/bottom to
    [min(high[t-2], Body[t-2].high), max(low[t], Body[t].low)] 
    — OR simpler locked rule: zone = [high[t-2], low[t]] UNION [Body[t-2].high, Body[t].low]
       clipped to a single interval (min of lowers, max of uppers of the two gaps).
Pick ONE merge rule ≤10 lines; freeze before RUN.
Do NOT “refine on demo stills” after code exists without NEW id.
ATLAS optional: confirm demo still matches frozen rule (calibration), not redesign.
```

**SEVERITY:** **CRITICAL**

---

## ATTACK 3 — Birth-time / first-in-hour / look-ahead / selection

**PROBLEM:**
1. **Treatment ID:** earliest birth in [10:00,11:00) with birth=close(t) — OK, no future bars for ID. 10:00 bar as t uses 09:58–10:00 — OK.  
2. **Lecture “or immediately after”:** covered by earliest-in-hour. OK.  
3. **Selection:** days with no FVG in hour dropped — report coverage.  
4. **Look-ahead in outcomes:** MFE/MAE/revisit use path after birth — OK if ex-post event study, but **MFE from “birth mid or CE”** is unlocked (which price?).  
5. **Leave-then-revisit:** “after leaving” undefined (midpoint through? full zone exit?).  
6. **Same-bar / multi-FVG:** if two FVGs share birth minute — tie rule missing.  
7. **Control draw after seeing day path** — must be seed-only, no outcome conditioning.

**WHY IT MATTERS:** Unlocked revisit/MFE origin = metric hacking; leave rule changes revisit rate a lot.

**EVIDENCE REQUIRED / H004b:**
- Anchor price for MFE/MAE = **birth bar close** (PARAMETER) or zone midpoint — pick one.  
- Leave = first bar with no overlap with zone; revisit = later overlap.  
- Tie: lowest bar index / bullish before bearish — freeze.  
- Coverage table mandatory before Δ.

**SEVERITY:** **HIGH**

---

## ATTACK 4 — Horizons + falsification not decision-ready

**PROBLEM:** Horizons +15/+30/+60/rest-of-RTH. Primary metric still “CASSANDRA may pick”; default 60m revisit **or** MFE−|MAE|. FAILS/SURVIVES on Δ of undefined m. Multiplicity across horizons/polarities with only soft HOUR-DEPENDENT label.

**WHY IT MATTERS:** Not run-ready; SURVIVES would be meaningless.

**EVIDENCE REQUIRED / H004b:**

```
PRIMARY metric m = I(revisit zone within 60m after leave; if never leaves, I=1)
  — level utility; matches “look for” pedagogy better than raw MFE.
Report MFE/MAE at +15/+30/+60/RTH as DESCRIPTIVE only (cannot flip SURVIVES).
FAILS if OOS N_pairs≥80: Δ≤0 or CI(Δ) includes ≤0 on primary m (later control).
SURVIVES only if Δ>0, CI>0, WF median Δ>0 on primary m AND sensitivity random-RTH
  does not flip (or label CONTROL-DEPENDENT).
Polarity strata descriptive; HOUR/EVENT-DEPENDENT labels as now.
IS/OOS: prefer calendar 2023–2024 / 2025 on CONTINUOUS-KAGGLE (match H001b) OR 60/40 — freeze one.
N≥80 pairs; coverage projection ≥20 days.
```

**SEVERITY:** **CRITICAL**

---

## ATTACK 5 — Tape / identity / MERCURY

**PROBLEM:** Protocol cites MNQ + shared stream C. Board uses CONTINUOUS-KAGGLE-NQ1M (truncated). MFE invites trade wrap.

**H004b:** Mandatory stream label CONTINUOUS-KAGGLE; roll undocumented; truncation FLAG; no MNQ Mar 2026 identity; **No MERCURY**; MAE/MFE descriptive ≠ expectancy after costs.

**SEVERITY:** **HIGH**

---

## Look-ahead summary

| Step | Look-ahead? |
|------|-------------|
| Detect FVG at close of t | No |
| Choose first birth in [10:00,11:00) | No |
| Score revisit/MFE after birth | Ex-post by design — OK if labeled event study |
| Expand zone using only bars ≤ t | Must hold — body rule must not use future bars |

---

## Decision

**HYPOTHESIS DID NOT SURVIVE RED TEAM REVIEW** (packaging).

**H004b required before exploratory RUN.** No run authorization from CASSANDRA.

---

## Exact H004b change list

1. **Retarget tape:** CONTINUOUS-KAGGLE-NQ1M; drop stream-C/MNQ-as-primary identity.  
2. **Lock primary control** = later same-day same-polarity FVG in [11:00,15:00); random RTH = sensitivity.  
3. **Lock volume-imbalance merge** ≤10 lines; label PARAMETER implementation of 011; no post-code demo redesign.  
4. **Lock primary metric** = 60m revisit indicator (or explicitly MFE−|MAE| from birth **close** — pick one; recommend revisit).  
5. **Lock leave/revisit and MFE anchor; birth-minute tie rule.**  
6. **Freeze IS/OOS + N≥80 pairs + coverage projection + event strata.**  
7. **SURVIVES vocabulary:** first-10:00-hour FVG vs later control — not Silver Bullet brand proof; no MERCURY.  
8. **New file id H004b**; retain H004 as audit draft.

---

## Path

`investigations/INV-002-methodology-seed/reviews/CASSANDRA_H004_REDTEAM_2026-09-13.md`
