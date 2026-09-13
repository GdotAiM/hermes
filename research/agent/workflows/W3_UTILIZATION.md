# W3 — Utilization

**Purpose:** Convert board locks into actionable **use / demote / do-not-trade** rules without laundering frequency into edge.  
**Stages:** UTILIZE → DEMOTE → LEDGER  
**Exit:** Utilization memo + updated beliefs; MERCURY still blocked unless SURVIVES path exists.

---

## Preconditions

- [ ] At least one ORION board lock on disk
- [ ] CASSANDRA results RT agreement on file for decision-class claims
- [ ] Pull before write

---

## Hard rule

A measured **frequency** is not an **edge**. An edge needs: entry, invalidation, expectancy vs cost, OOS survival, and usually a control that shows the object is **special** — not just that something often happens.

**VERIFY COMPLETE ≠ trade permission.**  
**FAILS / INCONCLUSIVE → no MERCURY.**

---

## Stage — UTILIZE

### Checklist

- [ ] For each board row, fill: Board label · Utilizable? · How (prior / logging / negative playbook / research watchlist)
- [ ] Separate **can utilize** vs **cannot utilize as edge**
- [ ] Preserve tape honesty labels on every claim reused downstream
- [ ] Prefer calibrated priors and demotions over new narrative
- [ ] Use `summaries/_UTILIZATION_TEMPLATE.md`

### Outputs

| Artifact | Path pattern |
|----------|--------------|
| Utilization memo | `summaries/<DATE>_UTILIZATION_*.md` |

---

## Stage — DEMOTE

### Checklist

- [ ] Encode explicit NO-TRADE / demote rules from FAILS
- [ ] Retire folklore numbers killed by VERIFY (e.g. Wave 1: ~70% → ~56% prior)
- [ ] Park INCONCLUSIVE with frozen reopen conditions (N gate, new weeks) — no silent reopen on burned OOS
- [ ] Brand language (e.g. Silver Bullet) stays untested unless mechanism hyp exists

---

## Stage — LEDGER / NEXT

### Checklist

- [ ] `beliefs/LEDGER.md` rows for utilizable changes
- [ ] Ranked “what to do with this” table (decision impact)
- [ ] One-line board answer: what is cleared for MERCURY (usually: nothing)
- [ ] Handoff to ORION for next experiment **or** RISK only if SURVIVES cleared

### Handoff examples

```
Next: ORION
Path: investigations/<INV>/STATUS.md
Ask: Pick next hyp or close chapter; do not reopen burned OOS without new id.
```

```
Next: RISK
Path: risk/GATES.md
Ask: Survival review for SURVIVES-only candidate <H###> (human must still approve MERCURY).
```

---

## Exit criteria

W3 complete when utilization memo states clearly what is prior/logging/negative knowledge vs what is forbidden as edge, and LEDGER reflects belief changes.

**Success reminder:** Negative knowledge and clean FAILS are utilizable discoveries.
