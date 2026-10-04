# Month 5 Slice 0 — glossary (proposed)

Sources: Lessons 1–5, 14 (2017). No production code.

Do not invent extra quarterly-profile enums. Do not collapse Open Float into OF pools.

---

## 1. Quarterly shift (Lesson 1)

Look-back 3–4 months on the weekly / daily. Directional reset.

```
quarterly_shift:
  state: in_progress | none | unclear
  lookback_months: 3 | 4 | none
  direction: bullish | bearish | unclear
```

Lecture names **3-month shifts** and **4-month shifts**, plus **look back** and **cast forward**.

Do not freeze Q1/Q2/Q3/Q4 calendar labels as ICT-required enums unless a later lecture names them as the operating taxonomy. Calendar quarters may be confirming notes, not the state machine.

Underlying vs benchmark (lecture): e.g. EURUSD vs DXY. Store as optional labels:

```
underlying_symbol
benchmark_symbol
```

---

## 2. IPDA window (Lessons 1 + 3)

Labeled only: `20 | 40 | 60`.

```
ipda_window:
  days: 20 | 40 | 60 | none
  high: labeled or none
  low: labeled or none
```

Look-back **and** cast-forward are the same window, used both ways.  
No volatility heuristic that picks 20 vs 40 vs 60.

First IPDA line in the lecture = first trading day of the **previous** calendar month (context note, not a detector in Slice 0).

M5 publishes this. M7 may consume the labeled days later. M5 does not read raw `month7`.

---

## 3. Open Float vs OF liquidity pools (Lessons 2 + 4)

**Keep two fields.**

### Open Float (Lesson 2)

Standing interest **above and below** current price.

```
open_float:
  buy_side: present | absent | unclear
  sell_side: present | absent | unclear
```

Advanced structure vocabulary used in that lecture (store as optional annotations, not extra opportunity gates):

`STH / STL` · `ITH / ITL` · `LTH / LTL`

### Open Float Liquidity Pools (Lesson 4)

The **pools** the float is organized into — typically the IPDA 20/40/60 highs and lows and the three-month high/low.

```
open_float_pools:
  pool_ids: tuple of labeled ids
```

OF concept ≠ OF pool list. A day can have float direction without a named pool id.

---

## 4. Institutional swing points (Lesson 5)

ICT: two forms only.

| Software id | Lecture |
|-------------|---------|
| `breaker_swing_point` | Stop-run swing (preferred) |
| `failure_swing` | Approach without clearing the prior extreme |
| `none` | Not named |

Breaker entry annotations (not orders):

`turtle_soup` · `breaker_block`

```
institutional_swing:
  kind: breaker_swing_point | failure_swing | none
  entry_annotation: turtle_soup | breaker_block | none
```

Do not add CHoCH / BOS as M5 swing-point kinds.

---

## 5. Confirming evidence (Lessons 6–12)

Same split as M6:

**Not required for generic `position_opportunity`:**

- `ten_year_notes`
- `ten_year_yields`
- `interest_rate_differentials`
- `intermarket`
- `seasonal_tendency` (`bullish` | `bearish` | `ideal` | `none`)

`ideal` seasonal is a **named note**, not yet a separate composite. Do not create `ideal_seasonal_position` until a later research slice proves Lesson 12 defines a gated template.

---

## 6. HTF PD hierarchy (Lesson 14)

Do not invent new array types. Reuse the existing PD matrix.

Do not freeze scan order as a detector.

Hierarchy is directional: from current price / equilibrium toward the Premium or Discount extreme.
Store nearest-to-extreme array identity, not a traversal enum.

ICT scan-from-EQ (context only): mitigation → breaker → void/FVG → order block → rejection → old high/low.

M5 stores:

```
htf_pd:
  dealing_range_tf: monthly | weekly | daily | none
  equilibrium: labeled or none
  nearest_premium_id
  nearest_discount_id
```

---

## 7. Setup progression + entry + management (Lessons 15–18)

```
setup_progression: watching | none
entry_technique: stop | limit | none
position_management: annotated | none
```

Money-management lecture does **not** gate `position_opportunity`.

---

## 8. Opportunity (generic)

Proposed later-slice rule (not a detector yet):

```
position_opportunity = true
  when quarterly or IPDA context exists
  AND (open float or named pool or named swing)
  AND HTF PD dealing range labeled
```

Confirming rates / seasonal / intermarket are **not** required for that generic flag.

---

Sign or correct this glossary before Slice 1 contracts.
