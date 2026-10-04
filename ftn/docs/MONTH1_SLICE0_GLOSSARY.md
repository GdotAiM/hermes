# Month 1 Slice 0 — glossary (proposed)

No production code.

---

## 1. Identification

```
identified_setup_elements: present | none
```

Explicit. Not inferred from other notes.

---

## 2. Flag

```
setup_elements.flag: true | false
setup_elements.reason: string
```

**Frozen semantic rule:**

```
identified_setup_elements == present
    → setup_elements.flag = true
otherwise false
```

Not required: dealing_range_side, fair valuation, liquidity run, impulse, protraction, conditioning, focus.

Slice 1 only **parses** a provided flag. Derivation is a later slice.

---

## 3. Dealing-range side

```
dealing_range_side: premium | equilibrium | discount | none
```

Labeled location. Not a scanner.
≠ M5 `nearest_premium_id` / `nearest_discount_id`.

---

## 4. Supporting notes

```
conditioning_note: present | none
focus_note: present | none
fair_valuation_note: present | none
liquidity_run_note: present | none
impulse_note: present | none
protraction_note: present | none
```

```
liquidity_run_note  ≠  DayContext liquidity probe
protraction_note    ≠  M9 protraction_stage
```

---

## 5. M1 ↔ M9 / M5 / M4

M1 does not write `profile`, `liquidity_probe`, or M5 HTF PD ids.
M1 does not mint from M4 catalog presence.

---

Sign or correct 1–5. Then Slice 1 contracts + known-state fixture.
