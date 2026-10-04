# Month 6 Slice 0 — glossary (proposed, awaiting sign-off)

Sources: Lessons 2, 4, 5, 8 (2017 core). Community “12 weekly profiles” do **not** belong here.

No production code in this slice.

---

## 1. Bullish sequential patterns (Lesson 4)

ICT names the **Monthly–Weekly–Daily alignment stack**, not three chart patterns like H&S.

| Software id | Lecture sense |
|-------------|---------------|
| `mwd_all_bullish` | Monthly, weekly, and daily all indicate higher. Buy daily (and 4H) bullish discount arrays. |
| `mw_bullish_daily_correcting` | Monthly + weekly bullish; daily correcting lower. Buy daily discounts **at or inside nested weekly** discount arrays. |
| `m_bullish_wd_correcting` | Monthly bullish; weekly and daily correcting. “Bullish MWD sequential”: monthly discount (OB / FVG) is the parent; buy daily discounts nested in that monthly array. |

`swing_family = bull` when any of these is watching.  
`swing_family = none` when monthly is not bullish (or unclear).

Do not invent a fourth bullish sequential name.

---

## 2. Bearish mirrors (Lesson 5)

Lecture: everything said about bullish setups generally applies inverted.

| Software id | Lecture sense |
|-------------|---------------|
| `mwd_all_bearish` | M + W + D all indicate lower. Sell daily / 4H bearish premium arrays. |
| `mw_bearish_daily_correcting` | M + W bearish; daily correcting higher. Sell daily premiums nested in weekly premium. |
| `m_bearish_wd_correcting` | Monthly bearish; weekly + daily correcting. Bearish MWD sequential into monthly premium. |

`swing_family = bear` when any of these is watching.

---

## 3. Lesson 2 — required vs confirming

Lesson 2 lists several inputs. Essence: not all universally required.

**Required to even research a swing (must be labeled or derived later):**

| Field | Meaning |
|-------|---------|
| `htf_trend` | Monthly (and preferably weekly) directional sponsorship |
| `institutional_order_flow` | HTF IOF / sponsorship already on Market State |
| `pd_arrays` | A named HTF discount (bull) or premium (bear) array |

**Confirming / enhancing (absence does not kill research; absence blocks Million-Dollar composite):**

| Field | Meaning |
|-------|---------|
| `seasonal_tendency` | Calendar seasonal in the intended direction |
| `interest_rates` | Rates triad / bond market agreement |
| `cot` | Commercials supporting the swing direction |
| `intermarket` | Correlated market / commodity / DXY agreement |

Rationale: Lesson 8 says *do not look for a swing trade without a seasonal tendency* **for the Million-Dollar setup**. Lesson 2 treats seasonal/COT/intermarket as elements of *successful* swing trading, not as the only way to name a family. So:

- Family can be named from M/W/D alignment + PD array.  
- `million_dollar_swing = assembled` requires the confirming set below.  
- `swing_opportunity` for generic M6 can be true on family + suitability + risk frame **without** MD assembled.  
- MD assembled is a stricter flag.

If you want seasonal required for **all** `swing_opportunity`, say so before Slice 1. Default in this glossary: seasonal required **only** for MD assembled.

---

## 4. Lesson 8 — Million-Dollar gates (order)

ICT’s own sequence:

1. `seasonal_tendency` — required for MD. No seasonal → do not call it MD. Consider ST/day-trade instead.  
2. `major_market_analysis` — need **one from each group** trending (rates, stocks, commodities, currencies).  
3. `intermarket_analysis` — COT commercials in agreement, then correlation / commodity / open-interest filters.  
4. `top_down_analysis` — ~9–18 months of history; M/W/D/4H PD arrays; IPDA 20/40/60. After intermarket, before setup.  
5. `setup` — buy or sell setup in the PD spectrum (maps to sequential family + classic approach).  
6. `management` — buy/sell management plan exists (annotation). Not an order.

Composite:

```
million_dollar_swing:
  state: assembled | incomplete | none
  missing: tuple of gate ids
```

`assembled` only if all **six** gates are present.  
`incomplete` if family exists but ≥1 gate is missing.  
`none` if no swing family.

Management is **annotation that a plan is stated**, not live trade management.

---

## 5. Market selection (Lessons 1 + 7)

```
market_selection: suitable | unsuitable | unclear
```

Suitable ≈ trending / institutionally sponsored market that can expand.  
Unsuitable ≈ range-bound / no sponsorship / Lesson-7 “will not move explosively.”  
No numeric score. No pair ranking.

---

## 6. Risk frame (Lesson 6)

```
stop_reference    # array or swing that invalidates
target_reference  # opposing premium/discount or liquidity
reward_frame      # descriptive, e.g. discount_to_premium
```

No lots. No `$` risk.

---

## 7. Explicitly out of glossary

- Weekly profiles (those are M7)  
- London gate (M8)  
- REV / BB / PIP20 / CONSO (M9)  
- paper_swing persist (M7 only)  
- broker  

---

Sign this glossary (or correct names/gates) before Slice 1 contracts.
