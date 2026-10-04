# Month 8 Slice 4 — delayed vs none

Classifier **not changed**. Three research fixtures run through Slice 3 as-is.

## Classifier output (current Hermes rule)

| Fixture | Path | Slice 2 profile | Slice 3 profile | Opportunity |
|---------|------|-----------------|-----------------|-------------|
| `m8_path_eurusd.json` | up + HH + by 02:00 | none | `normal_protraction_sell` | true |
| `m8_evidence_eurusd.json` | no path | none | `none` | false |
| `m8_s4_late_rally.json` | up + HH + **after** 02:00 | none | `delayed_protraction_sell` | true |
| `m8_s4_no_hh.json` | up + by 02:00 + **no HH** | none | `delayed_protraction_sell` | true |
| `m8_s4_first_move_only.json` | `first_move=up` only | none | `delayed_protraction_sell` | true |

All three S4 fixtures still have **no** `ict_london_profile` key. Slice 2 still returns `none`.

## What the Month 8 lectures actually distinguish

**Normal protraction sell (lecture 5):**  
CBDR classic + Asian compressed + **after 00:00 NY price rallies** and takes above Asian/CBDR, typically into 02:00–04:00, then delivers lower with IOF.

**Delayed protraction (lecture 5):**  
The **protractionary stage is late in the day**. Price may **not** rally after midnight. The Judas/high can form later in London. CBDR may even be imperfect. Delay is a **timing** claim.

Lecture 6 (avoid London) is about wide/erratic CBDR-Asian, not about labeling every non-classic uptick as delayed.

So “delayed” in ICT is closer to: **the expansion/Judas is postponed**, not: **any bullish tick after the anchor**.

## Determination

| Case | Current label | Determination | Tag if we later edit |
|------|---------------|---------------|----------------------|
| Late rally + HH taken | `delayed_protraction_sell` | **Keep.** Matches lecture delayed: range is taken, clock is late. | `ict_source` |
| Early up, **no** HH/LL | `delayed_protraction_sell` | **Too strong.** First move without range-take is not a named London profile. Prefer `none`. | would be `hermes_interpretation` if we kept delayed; proposed change → `none` |
| `first_move` only | `delayed_protraction_sell` | **Insufficient evidence.** Prefer `none`. | same |

**Written call:**

1. Delayed is ICT-supported when there is a **late** protraction that **does take** the relevant high/low.  
2. Delayed is **not** ICT-supported for “directionally consistent tick, no range, no timing.”  
3. Do **not** silently treat (2) and (3) as delayed in a future detector rewrite without tagging the leftover as Hermes.

## Proposed classifier change (not applied)

```
if bearish and first_move == up:
    if HH and early:     normal_protraction_sell   # ict_source
    if HH and not early: delayed_protraction_sell  # ict_source
    else:                none                      # insufficient path
```

Same mirror for buy.

Apply only after you sign this call. Until then Slice 3 classifier stays frozen.

## Stop line

No Slice 5 projection. No HTF. No DTR. No desk.


## Classifier applied (signed)

Regression:

- normal path → normal_protraction_sell
- late HH (flag and window-only) → delayed_protraction_sell
- no HH → none
- first move only → none
- no path → none

Slice 4 complete. Next permitted: Slice 5.
