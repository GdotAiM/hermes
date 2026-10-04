# Month 11 essence — FROZEN

2017 ICT Core Content Month 11. **4 lectures.** One process.

Playlist: https://www.youtube.com/playlist?list=PLVgHx4Z63paa4FfJ8zI_QpdJICSLkXTQO

`mega_trade` is an **annotation**, not a ticket.

`identified_mega_trade == present` is the only input that mints the flag.
Quarterly / seasonal / SMT / M5 position / M6 swing do not.

M11 owns the teaching of multi-month mega-trades.
It must not overwrite M5 quarterly_shift or become a second position ticket.

---

## Canon (4)

1. Commodity Mega-Trades — `u5S6Zt1ZIpA`
2. Forex & Currency Mega-Trades — `CxwFON8MLB0`
3. Stock Mega-Trades — `kny8Kpisvoc`
4. Bond Mega-Trades — `At43V93rnDQ`

---

## Process

```
Mega-trade family
   (commodity | fx | stock | bond | none)
        ↓
Quarterly-shift overlap note
        ↓
Seasonal overlap note
        ↓
SMT / relative-strength note
        ↓
identified_mega_trade
        ↓
mega_trade annotation
```

---

## Layer map

```
M5  position / quarterly          sibling
M6  swing                         sibling
M11 DayContext.month11            annotation
M9  session_ticket
```

M11 must not inspect raw month1–10 to mint evidence.
M11 must not write M5 quarterly_shift.

---

## Frozen out

- No paper_mega
- No M5 / M6 field mutation
- No candidate / ticket / broker
- No mega_trade_horizon field unless a later slice proves the lecture requires it

---

## Next permitted

Slice 0 glossary. No m11_contracts.py until Slice 0 is signed.
