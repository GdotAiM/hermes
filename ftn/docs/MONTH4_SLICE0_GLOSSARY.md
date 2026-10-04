# Month 4 Slice 0 — glossary (proposed)

Sources: Month 4 lectures 1–14 + official playlist order.
No production code.

---

## A. Array taxonomy — 10 sibling kinds

Lecture titles that name a structure become catalog identities.
Do **not** collapse them into “OB + five sisters” unless a lecture
explicitly says one *is* a subtype of another.

```
pd_array_kind:
    orderblock
    mitigation_block
    breaker_block
    rejection_block
    reclaimed_orderblock
    propulsion_block
    vacuum_block
    liquidity_void
    liquidity_pool
    fvg
    none
```

Each instance also carries:

```
id                  labeled string
kind                one of the above
polarity            bullish | bearish | none
timeframe           monthly | weekly | daily | h4 | none
```

Relatedness may be annotated later (`related_to`) without making
kinds exclusive. Coexistence is allowed.

---

## B. FVG vs liquidity void

Keep both kinds.

Lecture / notes: an FVG is the gap on the timeframe you are looking at;
breaking the same move down on a lower TF can look like a **void**, not
“one gap.” FVG, void, OB, and pool **overlap a lot**.

Frozen relationship:

```
fvg              ≠  liquidity_void
same price span  →  both may be labeled
                  →  not two mutually exclusive winners
```

Do not write a detector that forces “if FVG then not void.”

---

## C. Pattern notes — not catalog kinds

```
pattern_note:
    divergence_phantom
    double_bottom
    double_top
    none
```

```
pattern_note  ≠  pd_array_kind
```

A day can have `fvg` + `double_bottom` without promoting DB into the catalog.

---

## D. Opportunity gate — proposed freeze

Essence: do **not** set true merely because any array object exists.

Proposed rule (generic catalog presence, not a ranking):

```
kind != none
AND polarity in {bullish, bearish}
    → array_opportunity = true
otherwise
    → false
```

Not required for the generic flag:

- interest-rate confirming
- a second overlapping array
- M5 nearest-id match
- dealing-range classification
- pattern notes

Those stay annotations. A later research slice can study a stricter
“liquidity-context” variant without changing this generic gate.

Slice 1 still only **parses** a provided flag. Derivation belongs to a
later detector slice.

---

## Confirming

`interest_rate_effects` = confirming boolean. Not a router.

---

## What Slice 0 does not do

- No subtype tree (reclaimed/propulsion/vacuum stay siblings)
- No scan-order list (that belongs to M5 HTF PD identity, not M4 kinds)
- No CHoCH / BOS kinds
- No additional opportunity rule or detector logic

Sign or correct A–D. Then Slice 1 contracts + known-state fixture.
