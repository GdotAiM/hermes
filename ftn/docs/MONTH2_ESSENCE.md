# Month 2 essence — FROZEN

2016 ICT Core Content Month 02. **8 lectures.** One process.

Playlist: https://www.youtube.com/playlist?list=PLVgHx4Z63paZvjqerfbn320myZ06L1MOB

`low_risk_frame` is an **annotation**, not a ticket and not a lot-size.

M2 accumulates risk-framing and small-account context; it does not
calculate position size or create a trading ticket.

`low_risk_frame` is true only when M2 explicitly identifies a
low-risk/high-reward framing; the mere presence of stop, target,
R multiple, or M6 risk references does not mint the flag.

10%/month is ICT **guidance**, not an OS KPI.

---

## Canon (8)

1. Growing Small Accounts — `mjVHmE1gVMg`
2. Framing Low Risk Trade Setups — `Zsg8IeBtfu0`
3. How Traders Make 10% Per Month — `pctqB3UD6dk`
4. No Fear Of Losing — `pFdW8wdR9sQ`
5. How To Mitigate Losing Trades Effectively — `vWDElb65YHg`
6. The Secrets To Selecting High Reward Setups — `bftKgceXqYo`
7. Market Maker Trap False Flag — `cRbPS3uxkj4`
8. Market Maker Trap False Breakouts — `pv2-R-STviA`

---

## Process (shape frozen; exact fields = Slice 0)

```
Small-account posture
        ↓
Low-risk / high-reward framing
        ↓
Reward-selection context
        ↓
Loss-mitigation / psychology notes
        ↓
MM-trap pattern notes
        ↓
low_risk_frame annotation
```

Not: small_account_posture AND ... → flag.

---

## Layer map

```
M2  DayContext.month2     annotation
M3–M8
M6  RiskFrame             sibling annotation (M2 does not populate it)
M9  session_ticket
```

M2 must not inspect raw month3–9.
M2 must not write session_ticket or compute lots.

---

## Frozen out

- No paper_risk_m2
- No lot / dollar / broker
- No 10% KPI detector
- No fear → block trade
- No loss → auto-resize
- No M9 arbitration

---

## Next permitted

Slice 0 glossary. No m2_contracts.py until Slice 0 is signed.
