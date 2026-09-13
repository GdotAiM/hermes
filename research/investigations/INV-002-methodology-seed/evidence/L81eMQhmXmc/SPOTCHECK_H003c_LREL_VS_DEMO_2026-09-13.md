# Spot-check — H003c \(L_{rel}\) vs demo red REL
**Date:** 2026-09-13  
**Owner:** QUANT  
**Lock:** `H003_BOX_LOCK.md`  
**Protocol:** `experiments/QUANT_H003c_REL_TO_RANGE_PROTOCOL_2026-09-13.md`  
**CASSANDRA:** Attack 1 / RUN blocker — detector vs demo  

## Visual (frames — no OHLC tape yet)

| Frame | Red REL (approx y-axis read) | Notes |
|-------|------------------------------|-------|
| `frames/lock_00-06-40.jpg` | **~29,020–29,025** | Mid-box; origin ~07:35–07:45 swing low; **not** beige LL (~28,940) |
| `frames/lock_00-10-55.jpg` | **~29,020** | Cursor on same red shelf |
| ATLAS lock | REL pair ~07:30 & ~08:50 | Distinct from box LL |

**Instrument on chart:** NQ-family 1m (Sep contract on screen). Shared Wave-1 tape should be MNQ/NQ with META — scale 1:1 on index points for level compare.

## Algorithmic compute

**Status:** **BLOCKED** — INV-001/002 stream C OHLC for this demo session **not filed**. Cannot emit numeric \(L_{rel}\) from fractal+\(	au_{eq}\) until tape covers the lecture chart date.

**When tape arrives:** run detector on that session’s [07:00,09:00) bars; record \(L_{rel}\) at \(	au_{eq}=2.0\); pass if \(|L_{rel} - L_{red}| ≤ 1\) tick (0.25). If fail → ORION-acked retune **pre-peek** (or NEW id if after outcome peek).

## Selection-rule change (pre-peek, Attack 3)

Demo REL is **mid-box**, not the lowest equal-low cluster.  

**Was:** multiple pairs → lowest mean (biased to LL).  
**Now (H003c §3.2):** multiple pairs → pair whose mean is **closest to mid-range** \((H_{79}+L_{79})/2\); lowest-mean retained as **rival selection** (descriptive).

## SELECTION-DEPENDENT

Already in H003c §5 (imported from H003b residual). Confirmed 2026-09-13.

## Verdict this pass

| Item | Status |
|------|--------|
| Visual red REL level | ~29,020–29,025 (frame read) |
| Computed \(L_{rel}\) | **PENDING tape** |
| Selection rule vs demo | **Amended** to mid-range preference |
| SELECTION-DEPENDENT §5 | **Present** |
| RUN | Still **HOLD** |

## CASSANDRA follow-up (2026-09-13)

- Attack 3 (mid-range multi-REL): **CLEARED** pre-peek.
- SELECTION-DEPENDENT: confirmed in protocol.
- Attack 1: still **OPEN** for RUN — computed \(L_{rel}\) PENDING stream C; pass only if \(|L_{rel}-L_{red}|≤0.25\) on demo session. Packaging SURVIVED stands; RUN HOLD unchanged.

## ATLAS REL detector lock (2026-09-13)

`H003c_REL_DETECTOR_LOCK.md` — **1-tick match = FAIL / blocked** until session tape.  
§3.2 fractal+τ_eq=2.0 = **PARAMETER, not lecture-locked**.  
Axis read on lock frame ~**21,020** (NQ Sep 2026) — prior ~29,020 frame reads were approximate/wrong scale; neither is a pass.  
Rival: human mid-box pair + τ∈{4,8}. Ban SURVIVES-as-red-line-confirmation.

## CASSANDRA DETECTOR_PARAMETER (2026-09-13)

Visual ~29,020 / ATLAS ~21,020 = **calibration diagnostics only**.  
Passing |L_rel − L_red|≤0.25 later = “visually consistent on demo day,” **still PARAMETER** — not Observed red-line identity.  
SURVIVES prose must say **PARAMETER detector**.
