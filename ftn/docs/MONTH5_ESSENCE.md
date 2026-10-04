# Month 5 essence — FROZEN

2017 ICT Core Content, Month 05. **18 lectures.** Position / quarterly / HTF horizon.

Official playlist:
https://www.youtube.com/playlist?list=PLVgHx4Z63paYBN404Q2QZ7D4mOJz1IHAk

Not 18 bots. One evidence-accumulation process.

`position_opportunity` is an **opportunity / annotation**, not a ticket.

---

## Canon (18)

1. Quarterly Shifts & IPDA Data Ranges — `n7SPAK_tpN8`
2. Open Float — `BkmZgjuYREU`
3. Using IPDA Data Ranges — `LRKtiysz4nA`
4. Defining Open Float Liquidity Pools — `vqtA1S9JH34`
5. Defining Institutional Swing Points — `xRjKtUEKkSE`
6. Using 10 Year Notes In HTF Analysis — `z-7ypchAMDE`
7. Qualifying Trade Conditions With 10 Year Yields — `N8_8tEw2_44`
8. Interest Rate Differentials — `w6VlX-rsTUs`
9. How To Use Intermarket Analysis — `4i_hnoEk6lw`
10. How To Use Bullish Seasonal Tendencies In HTF Analysis
11. How To Use Bearish Seasonal Tendencies In HTF Analysis
12. Ideal Seasonal Tendencies
13. Money Management
14. Defining HTF PD Arrays — `pwO-E-OOH5k`
15. Trade Conditions & Setup Progressions — `Y1oxwc354oo`
16. Stop Entry Techniques For Long Term Traders
17. Limit Order Entry Techniques For Long Term Traders
18. Position Trade Management

#10-13, 16-18 IDs remain playlist-indexed until needed.

---

## Process (frozen)

```
Quarterly shift + IPDA window (20 / 40 / 60)
        ↓
Open float (standing interest above / below)
        ↓
Open-float liquidity pools (distinct field)
        ↓
Institutional swing point
        ↓
Rates / 10Y / yields / differentials   (confirming)
        ↓
Intermarket                             (confirming)
        ↓
Seasonal tendency                       (confirming)
        ↓
HTF PD-array hierarchy
        ↓
Trade-condition / setup progression
        ↓
entry_technique  stop | limit | none    (annotation)
        ↓
position management                     (annotation)
        ↓
position_opportunity  true | false
```

---

## Layer map

```
M5  position / quarterly   DayContext.month5     annotation only
M6  swing / monthly        DayContext.month6     swing_opportunity
M7  weekly / OSOK          DayContext.month7     paper_swing
M8  ICT day                DayContext.month8
M9  session                candidates            session_ticket
```

```
M5 position_opportunity
        ≠
M6 swing_opportunity
        ≠
M7 OSOK
        ≠
M9 candidate
        ≠
M9 session_ticket
        ≠
order
```

M5 publishes labeled `quarterly_shift` + `ipda_window`.
M6/M7 may consume later.
M5 must **not** inspect raw `month7` to satisfy its own gates.

---

## Frozen governance

| Decision | Choice |
|----------|--------|
| Opportunity | `position_opportunity` annotation. Not a ticket. |
| Persist | No `paper_position_m5`. |
| IPDA | Labeled 20 / 40 / 60. No optimizer. |
| Quarterly shift | M5-owned context. |
| Seasonal | Confirming for generic opportunity. |
| Rates / intermarket | Confirming labels. Not a router. |
| HTF PD | Hierarchical representation. |
| Stop / limit | `entry_technique` annotation. |
| Money / position mgmt | Guidance only. Not a gate for generic opportunity. |
| Broker | Out. |

---

## Next permitted

Slice 0 glossary. No `m5_contracts.py` until Slice 0 is signed.
