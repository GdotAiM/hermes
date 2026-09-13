# ORION — Wave 1 hyp specs (from Passed Observed only)
**Date:** 2026-09-13  
**Parents Passed:** C-METH-003–011, 015  
**Amended lock:** C-METH-008 — RTH open = **9:30 ET** (ASR 9:00 rejected)  
**Tape:** shared INV-001 stream C / WAVE1 stub — **RUN HOLD**

## Ranking
H001 → H003 → H004 → H002  
(info gain on a verify-don’t-accept number; then clean liquidity geometry; then timed FVG event; then classifier)

---

### H001 — RTH opening-gap half / CE by 10:00 ET
**Parents:** C-METH-008, 009, 015  
**Statement:** On NASDAQ index futures (1m), define RTH ORG as prior-day **16:14 ET** (4:14 p.m.) final print → **09:30 ET** RTH open. Let CE = midpoint. Measure whether price reaches CE by **10:00 ET**. Estimate baseline P(hit) and conditional P(hit | gap size, gap direction, prior-day trend, pre-market 7–9 state, event day).  
**Not a claim:** that P≈0.70 — lecture says verify; 0.70 is a foil only.  
**Falsify (example):** if unconditional P(hit by 10:00) is not distinguishable from a pre-registered null after costs/filters, or if claimed conditionals do not improve vs baseline under OOS.  
**QUANT:** draft protocol only; no run until tape.

### H002 — 7:00–9:00 state → post-9:30 behaviour
**Parents:** C-METH-003, 004, 005  
**Statement:** Classify each trading day (excl. Sundays) 07:00–09:00 ET as expansion↑ / expansion↓ / consolidation / compression (mechanical defs TBD by QUANT+DATA). Test whether class predicts post-09:30 path features (first side swept, range expansion, chop) at 10:00 / 11:00 / 12:00 horizons better than unconditional baseline.  
**Falsify:** no lift in predictive accuracy vs baseline after OOS.  
**Note:** precursor, not panacea (Passed 005).

### H003 — One-side sweep of 7–9 → opposite boundary
**Parents:** C-METH-003, 004, 006  
**Statement:** Given a 07:00–09:00 ET range, if after 09:30 one boundary is swept first, P(reach opposite boundary) exceeds a pre-registered baseline (e.g. random-side or no-sweep days). Report time-to-target, MAE, MFE.  
**Falsify:** Δ≤0 vs control under OOS (CASSANDRA to attack control choice before run).

### H004 — First 10:00-hour FVG
**Parents:** C-METH-010, 011  
**Statement:** On 1m, take the first FVG that forms in the 10:00 ET hour (10:00 candle may qualify); include volume imbalance. Event-study returns / MFE/MAE / revisit vs later FVGs same day (selection-bias control).  
**Falsify:** first-10:00 FVG metrics not better than later same-day FVGs (or random RTH FVG control — CASSANDRA to set).

## Explicit non-parents
11:30 lunch, CISD, ASR 9:00 open — not Passed. Do not import INV-001 lunch into Wave 1.

## Next
1. QUANT drafts H001–H004 protocols (no run)  
2. CASSANDRA red-teams H001 first  
3. Shared tape remains the hard blocker
