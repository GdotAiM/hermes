# Decision Record — MINT / MERCURY-compatible

**Date:** YYYY-MM-DD  
**Decision id:** MINT-DEC-YYYYMMDD-##  
**Author role:** MINT | MERCURY  
**Mode:** paper  
**Live unlocked:** no

---

## Board / utilization refs (required)

| Ref type | Path |
|----------|------|
| Board lock | `summaries/…` |
| Utilization | `summaries/…` |
| STATUS (if any) | `investigations/…/STATUS.md` |

**Board labels cited:** SURVIVES | VERIFY | FAILS | INCONCLUSIVE | none (idle)

---

## Strategy

| Field | Value |
|-------|-------|
| Strategy id (allowlist) | |
| Hypothesis id | |
| Strategy card | `trading/strategies/…` |
| ICT objects used | |

---

## Thesis (one paragraph)

What cleared research justifies this ticket? If idle / NO-TRADE, say why (e.g. Wave 1 zero SURVIVES).

---

## Ticket

| Field | Value |
|-------|-------|
| Instrument | |
| Side | buy / sell / flat |
| Size / qty | |
| Entry rule | |
| Stop / invalidation | |
| Target(s) | |
| $ risk | |
| % equity risk | |
| Correlation cluster | |

---

## RISK gate

| Field | Value |
|-------|-------|
| RISK memo path | |
| Outcome | PASS / SIZE DOWN / NO-TRADE / HOLD / N/A (idle) |
| Caps respected | 0.5% / 2% / 5% |

---

## Execution

| Field | Value |
|-------|-------|
| Adapter | alpaca_paper_stub / alpaca |
| Dry-run | yes / no |
| Broker order id | |
| Client order id | |
| Submit refused reason (if any) | |

---

## P&L impact (expected)

| Field | Value |
|-------|-------|
| Expected R | |
| Book path | `risk/BOOK.md` |
| Daily P&L after | |

---

## Outcome (fill post-trade or same-day)

| Field | Value |
|-------|-------|
| Fill | |
| Exit | |
| Realized P&L $ | |
| Lessons / hygiene | |

---

## Handoff

```
Next: RISK | ORION
Path: …
Ask: …
```

---

## Hard bans checklist

- [ ] Not trading from VERIFY / FAILS / INCONCLUSIVE
- [ ] Board ref present
- [ ] Allowlist id valid
- [ ] No live without dual unlock
- [ ] No secrets in this file
