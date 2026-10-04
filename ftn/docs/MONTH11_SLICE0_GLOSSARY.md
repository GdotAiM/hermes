# Month 11 Slice 0 — glossary (proposed)

No production code.

---

## 1. Family

```
mega_trade_family: commodity | fx | stock | bond | none
```

Context classification. Not a ticket kind.

---

## 2. Identification

```
identified_mega_trade: present | none
```

Explicit. Not inferred from quarterly / seasonal / SMT / M5 / M6.

---

## 3. Flag

```
mega_trade.flag: true | false
mega_trade.reason: string
```

**Frozen semantic rule:**

```
identified_mega_trade == present
    → mega_trade.flag = true
otherwise false
```

Slice 1 only **parses** a provided flag. Derivation is a later slice.

---

## 4. Overlap / strength notes

```
quarterly_shift_overlap: present | none
seasonal_overlap: present | none
relative_strength_note: present | none
```

Notes only. Do not mint the flag.
`quarterly_shift_overlap` ≠ M5 `quarterly_shift`.

---

## 5. M11 ↔ M5 / M6 / M9

```
Month11State.mega_trade               ≠  M5 position_opportunity
Month11State.quarterly_shift_overlap  ≠  M5 quarterly_shift
Month11State.mega_trade               ≠  M6 swing_opportunity
Month11State                          ≠  session_ticket
```

Do not add `mega_trade_horizon` in Slice 1.

---

Sign or correct 1–5. Then Slice 1 contracts + known-state fixture.
