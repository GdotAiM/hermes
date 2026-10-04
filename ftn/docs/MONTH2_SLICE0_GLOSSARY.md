# Month 2 Slice 0 — glossary (proposed)

No production code.

---

## 1. Small-account posture

```
small_account_posture: present | none
```

Context only. Does **not** gate `low_risk_frame`.

---

## 2. Identified framing (explicit)

```
identified_low_risk_frame: present | none
identified_high_reward_context: present | none
```

These are the explicit identification fields.
Stop / target / R-multiple / M6 RiskFrame presence ≠ these fields.

---

## 3. low_risk_frame flag

```
low_risk_frame.flag: true | false
low_risk_frame.reason: string
```

**Frozen semantic rule:**

```
identified_low_risk_frame == present
AND identified_high_reward_context == present
    → low_risk_frame = true
otherwise false
```

Not required: small_account_posture, psychology, loss notes, traps.

Slice 1 only **parses** a provided flag. Derivation is a later slice.

---

## 4. Guidance

```
monthly_return_guidance: "10_percent" | none
```

Text/enum for briefing. Never a numeric KPI or gate.

---

## 5. Psychology / loss notes

```
psychology_note: no_fear_of_losing | none
loss_mitigation_note: present | none
```

Notes only. No auto-resize. No block-trade router.

---

## 6. Trap pattern notes

```
trap_pattern: false_flag | false_breakout | none
```

```
trap_pattern  ≠  low_risk_frame
```

---

## 7. M2 ↔ M6

```
Month2State.low_risk_frame   = M2 teaching annotation
Month6State.risk_frame       = M6 swing stop/target refs
```

Sibling. M2 does not write M6 RiskFrame.

---

Sign or correct 1–7. Then Slice 1 contracts + known-state fixture.
