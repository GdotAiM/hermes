# Month 3 Slice 0 — glossary (proposed)

No production code. BOS/CHoCH not imported.

---

## 1. Timeframe

```
selected_timeframe: monthly | weekly | daily | h4 | none
```

Annotation of the TF used to define the setup. Not a scanner.

---

## 2. Institutional order flow (M3-owned label)

```
institutional_order_flow: bullish | bearish | unclear | none
```

Where liquidity is being sought, as labeled evidence.
Does **not** write M9 `pair_institutional.daytrade_iof`.

---

## 3. Institutional sponsorship (M3-owned label)

```
institutional_sponsorship: bullish | bearish | unclear | none
```

Does **not** write M9 `pair_institutional.sponsorship`.

---

## 4. Institutional market structure

```
institutional_structure: bullish | bearish | unclear | none
```

Lecture-level directional structure read. Not BOS/CHoCH kinds.

Optional note field later. Not required for Slice 1.

---

## 5. Macro → micro

```
macro_to_micro: present | none
```

Confirming that a top-down path was labeled. Not a pair ranker.

---

## 6. Trap pattern notes

```
trap_pattern: trendline_phantom | head_shoulders | none
```

```
trap_pattern  ≠  institutional_structure
```

---

## 7. next_setup flag

```
anticipated_setup: present | none
next_setup.flag: true | false
next_setup.reason: string
```

`anticipated_setup` is the explicit identification that a next setup was named.
It is not IOF, sponsorship, or structure.

**Frozen semantic rule:**

```
selected_timeframe != none
AND anticipated_setup == present
    → next_setup = true
otherwise false
```

IOF / sponsorship / structure / macro / traps do **not** mint the flag.

Valid:

```
TF monthly + IOF bullish + sponsorship bullish + structure bullish
+ anticipated_setup none
    → next_setup false
```

No named setup catalogue yet. Identity deferred.

Slice 1 only **parses** provided fields. Derivation is a later slice.

---

## 8. M3 ↔ M9

```
Month3State.iof / sponsorship   = context labels
DayContext.pair_institutional   = M9 session state
```

No overwrite. No arbiter between the two.

---

Sign or correct 1–8. Then Slice 1 contracts + known-state fixture.
