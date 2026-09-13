# H003c REL detector lock — L81eMQhmXmc

**For:** CASSANDRA Attack 1 / QUANT §3.2 (τ_eq vs fractal)  
**By:** ATLAS · 2026-09-13  
**Question:** Does QUANT’s mechanical REL detector match the red line he drew?

## Verdict

**Not matched to 1 tick. Do not treat §3.2 as lecture-locked.**

The red line is a **visual pair of swing lows**, not a stated 1-bar fractal + 2.0-pt rule. We cannot compute `L_rel` on this session: the lecture day is **not on-screen**, and there is no 1m OHLC in stream C yet.

## What he drew

| Object | Picture (00:09:25 / 00:11:00) |
|--------|-------------------------------|
| Beige box | 7–9 HH → 7–9 LL |
| Red line | One horizontal through **two** swing lows inside the box (~07:30–08:00 and ~08:50 ET) |
| Axis (read, not tape) | Line sits just above the **21,020** tick on NQ Sep 2026 1m |
| 7:00 LL | ~20,930 — unpaired; **not** on the red line |
| Post-HH pullback | A higher swing low **above** the red line — not part of the pair |

Frame: `frames/rel_detector_7-9_x3.jpg`

## vs QUANT §3.2

| Rule | Demo |
|------|------|
| 1-bar fractal (`low[i]<low[i±1]`) | The two red-line lows **look** like completed 3-bar swings. Extra 1-bar swings also exist in the box (open-leg pauses + the post-HH higher low). He never says “fractal.” |
| `τ_eq = 2.0` MNQ pts | **Not spoken.** Pixel scale on this 768×480 frame is ~0.8 pt/px; both lows sit on the same 1–2 px line, so they *might* be inside 2 pts — or 3–5. That is **not** a 1-tick proof. ICT “relative equal” is a visual class, usually wider than 2 NQ pts. |
| `L_rel` = mean of pair, tick-round 0.25 | He draws **one** line through both lows (typical: line at the **higher** of the two, i.e. the resting liquidity). Mean vs higher-low is an extra PARAMETER. |
| Multiple pairs → **lowest** mean | On **this** day the 7:00 LL has no twin, so lowest-mean would *probably* pick the red pair **if** the pair is detected. That does **not** lock the rule. A lower 1-bar pair on another morning would steal the treatment object (CASSANDRA Attack 3). |
| No REL → skip day | Consistent with “include any relative equal lows **if** you see them.” |

## Lock for QUANT

1. **Primary detector stays PARAMETER**, not Observed. Freeze `τ_eq=2.0` + 1-bar fractal only if ORION accepts a researcher map. Do not write “matches the red line.”
2. **1-tick spot-check = FAIL / blocked** until a 1m print of this exact session exists. Then: compute `L_rel` and `|L_rel − red|`. Pass only if ≤ 0.25.
3. **Rival selection (descriptive, pre-peek):** most obvious pair a student would annotate — two swing lows a human marks as “this low is relatively equal to that one” (00:09:20). Mid-box pair, not lowest-mean. Co-report; cannot flip SURVIVES alone.
4. **Rival τ:** 4.0 and 8.0 pts (visual REL band). Keep 1.0/2.0 as tight maps. If 2.0 misses the lecture pair once tape exists, retune **pre-peek** or NEW id.
5. Do **not** promote 1-bar fractal to Observed. If a swing definition is needed, say “ATLAS-unspecified; QUANT choice.”

## Still

- Instrument: NQ Sep 2026, 1m (on-screen header).  
- No calendar date on the clip.  
- REH not drawn; detector-for-REH is unchecked.  
- H003 box lock unchanged: sweep object = this red REL; target = opposite beige HH/LL.
