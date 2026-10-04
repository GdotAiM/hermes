# Month 12 Slice 0 — glossary (proposed)

No production code.

---

## 1. Horizon notes (independent)

```
long_term_note: present | none
intermediate_term_note: present | none
short_term_note: present | none
intraday_note: present | none
```

Independent. Not a cascade gate. Missing intermediate ≠ blocked flag.

---

## 2. Identification

```
identified_top_down: present | none
```

Explicit. Not inferred from “all four notes present” or from M5–M11 attachment.

---

## 3. Flag

```
top_down.flag: true | false
top_down.reason: string
```

**Frozen semantic rule:**

```
identified_top_down == present
    → top_down.flag = true
otherwise false
```

Slice 1 only **parses** a provided flag. Derivation is a later slice.

---

## 4. M12 ↔ M5–M11 / M9

```
Month12State.top_down     ≠  M9 session_ticket
Month12State              ≠  pair_institutional
Month12State horizon notes ≠  M5/M6/M8/M11 owned fields
```

No score. No winner. No router.

---

Sign or correct 1–4. Then Slice 1 contracts + known-state fixture.
