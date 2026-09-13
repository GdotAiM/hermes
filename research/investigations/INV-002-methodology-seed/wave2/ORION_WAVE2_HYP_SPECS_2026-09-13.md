# ORION — Wave 2 hyp specs (H008–H010)
**Date:** 2026-09-13  
**Tape:** FREE_YF_NQ (keyless)

## Rank
H009 → H010 → H008  
(weekly DOL is the cleanest falsifiable object on weekly/daily bars; state classifier is useful but definition-heavy)

### H009 — Weekly DOL delivery
**Statement:** For each week W, set candidate DOL_high = prior week high, DOL_low = prior week low. After W opens, measure which extreme is touched first on daily (primary) and whether either is touched by week end. Compare first-touch accuracy / touch rates vs random choice of which prior-week extreme is “the” DOL.  
**Falsify:** no lift vs random-side foil after OOS weeks.  
**Resolution:** weekly + daily NQ=F.

### H010 — HTF stack improves DOL pick
**Statement:** Predict which of {PWH, PWL, PDH, PDL} is delivered first in the next RTH day (daily bar path) using a ruleset that prefers weekly level when daily is nested / aligned. Compare accuracy vs daily-only rule and vs random among the four.  
**Falsify:** HTF-aware rule ≤ daily-only and ≤ random after OOS.  
**Resolution:** daily (+ weekly); hourly optional secondary on 60d window.

### H008 — State → next path
**Statement:** Classify each daily bar’s regime with a frozen mechanical rule (e.g. range vs ATR expansion, break of prior day, inside day). Test whether class predicts next-day range expansion / trend continuation better than unconditional baseline (Brier or hit-rate on pre-registered labels).  
**Falsify:** no OOS lift.  
**Note:** Until Week Lifecycle gives Observed state vocabulary, classifier = PARAMETER.

## Non-goals
- Do not claim MNQ 1m ICT session results from this tape
- Do not run Wave 1 hyps on FREE_YF

## ATLAS update (2026-09-13)
H008 has **thin** Observed parent (C-METH-030 weekly profile naming only). Do not pretend expansion/reversal/consolidation/compression was spoken. Prefer H009/H010; H008 = PARAMETER weekly-profile study or defer.
