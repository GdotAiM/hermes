# Month 10 Slice 0 — glossary (proposed)

No production code.

---

## 1. Identification

```
identified_multi_asset: present | none
```

Explicit. Not inferred from COT / seasonal / RS / OI / M5 / M6.

---

## 2. Flag

```
multi_asset_context.flag: true | false
multi_asset_context.reason: string
```

**Frozen semantic rule:**

```
identified_multi_asset == present
    → multi_asset_context.flag = true
otherwise false
```

Slice 1 only **parses** a provided flag. Derivation is a later slice.

---

## 3. COT / RS / OI readings (M10-owned labels)

```
cot_reading: bullish | bearish | unclear | none
relative_strength: accumulation | distribution | unclear | none
open_interest: rising | falling | unclear | none
```

Sibling of M5 `confirming.cot`. M10 does not write that field.

---

## 4. Seasonal / carrying-charge notes

```
commodity_seasonal_note: present | none
carrying_charge_note: premium | carrying_charge | none
```

Sibling of M5 seasonal. Not a gate.

---

## 5. Asset-class session model

```
asset_class: bond | index | stock | commodity | none
asset_session_note: present | none
```

Notes only. Not an M8 London profile and not a session ticket.

Bond AM/PM, index AM/PM, stock watchlists stay as notes until a later
research slice names a lecture-backed enum.

---

## 6. Confluence / options / watchlist notes

```
multi_asset_confluence_note: present | none
options_note: present | none
watchlist_note: buy | sell | none
```

No options routing. No M9 watchlist overwrite.

---

## 7. M10 ↔ M5 / M6 / M9

```
Month10State.cot_reading          ≠  M5 confirming.cot
Month10State.commodity_seasonal   ≠  M5 seasonal_tendency
Month10State.multi_asset_context  ≠  M6 intermarket_analysis
Month10State                      ≠  session_ticket
```

---

Sign or correct 1–7. Then Slice 1 contracts + known-state fixture.
