# Strategy Card — MINT

**Strategy id:** `snake_case_id`  
**Allowlist status:** proposed | listed | demoted | paper_pilot  
**Kind:** entry | filter | logging | paper_pilot  
**Owner:** MINT  
**Created:** YYYY-MM-DD

---

## Hypothesis mapping

| Field | Value |
|-------|-------|
| Hypothesis id | H0xx / H0xxb |
| Investigation | INV-00x |
| Required board status | SURVIVES (entry) · or n/a (filter/logging) |
| Board lock path | `summaries/…` |
| Utilization path | `summaries/…` |
| CASSANDRA results RT | path or n/a |

**If required board status is not met → MINT must not size.**

---

## ICT vocabulary (domain only)

| Object | Layer | Notes |
|--------|-------|-------|
| e.g. FVG / CE / OR | Observed / PARAMETER / Interpretation | Never relabel PARAMETER as Observed |

---

## Rules

### Entry

1. …

### Stop / invalidation

1. …

### Target

1. …

### Filters (no-trade)

1. … (encode FAILS demotions here when kind=filter)

---

## Sizing policy

| Field | Value |
|-------|-------|
| Max risk % | ≤ 0.5 (RISK may cut further) |
| Max daily loss interaction | respect 2% |
| Correlation notes | |

---

## Logging only (if kind=logging)

What to log (priors, watchlist frames). **No orders.**

---

## Kill / demote criteria

- Board flips to FAILS / INCONCLUSIVE reopen burned
- RISK NO-TRADE streak
- Human revoke paper pilot
- …

---

## Wave 1 note

Do not list entry strategies until a hyp **SURVIVES**. CE ~56% prior ≠ entry. H002b/H003c/H004b FAILS → demote filters. H009b INCONCLUSIVE → no size.
