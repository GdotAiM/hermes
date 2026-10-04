# Month 1 essence — FROZEN

2016 ICT Core Content Month 01. **8 lectures.** One process.

Playlist: https://www.youtube.com/playlist?list=PLVgHx4Z63paYzh3KwUFX0UHQUf31CAEXk

`setup_elements` is an **annotation**, not a ticket.

`identified_setup_elements == present` is the only input that mints the flag.
Premium/discount, fair valuation, liquidity-run, or M4 array presence do not.

M1 owns foundation teaching of premium/discount and setup elements.
It must not overwrite Hermes `profile` or M9 liquidity-probe fields.

---

## Canon (8) — official ICT titles

1. Elements Of A Trade Setup — `0LhteuLVuDU`
2. How Market Makers Condition The Market — `XwYYWBttWro`
3. What To Focus On Right Now — `B7_cjybYQ0g`
4. Equilibrium Vs. Discount — `qC0LogyIk2I`
5. Equilibrium Vs. Premium — `YuefjnUKQdM`
6. Fair Valuation — `SiVmoeyOWZE`
7. Liquidity Runs — `22XkhpJR5eA`
8. Impulse Price Swings & Market Protraction — `K4LtfujVpJs`

Lesson 2 official title is “How Market Makers Condition The Market.”
“Understanding Liquidity Providers” is a re-upload alias only.

---

## Process

```
Setup elements
        ↓
Market-maker conditioning notes
        ↓
Focus / current-study note
        ↓
Equilibrium / discount / premium
        ↓
Fair valuation
        ↓
Liquidity-run note
        ↓
Impulse / protraction note
        ↓
identified_setup_elements
        ↓
setup_elements annotation
```

---

## Layer map

```
M1  DayContext.month1     foundation annotation
M2–M8
M9  Hermes profile + liquidity_probe + session_ticket
```

M1 must not inspect raw month2–9.
M1 must not write `profile` or `liquidity_probe`.

---

## Frozen out

- No paper_setup_m1
- No PD-array presence gate
- No M5 nearest-id overwrite
- No broker / ticket / candidate

---

## Next permitted

Slice 0 glossary. No m1_contracts.py until Slice 0 is signed.
