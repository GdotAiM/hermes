# INV-003 Status
**Updated:** 2026-10-04 (ORION — intake note filed with the FTN monorepo merge; nothing authorized)

## Stage checklist

### W1 — Claim to gate
- [x] FTN source registered (`evidence/SOURCE_MAP.md`), handoff evidence path (`evidence/ftn/`)
- [x] 2 contract-sample handoffs filed, `origin: fixture`
- [ ] DATA gate on any EURUSD / XAUUSD tape (none filed)
- [ ] ATLAS: confirm which FTN rules are genuinely `ict_source` (lecture + timestamp)

### W2 — Hyp to board
- [ ] ORION picks ≤3 candidates from `claims/FTN_CANDIDATE_HYPOTHESES.md` and assigns H-IDs
- [ ] QUANT protocol (**NO RUN**)
- [ ] CASSANDRA packaging review
- [ ] RUN AUTHORIZATION

## RUN AUTHORIZATION log
| Date | Hyp | Scope | Tape | Authored by | Notes |
|------|-----|-------|------|-------------|-------|
| — | — | — | — | — | none |

## NEXT
- [ ] DATA: source and gate an EURUSD 1m/15m tape covering London + NY AM (owner: DATA)

## Hard reminders
- FTN `selected` / `session_ticket` / PAM1 complete ≠ edge ≠ clearance
- No verdicts in this folder until a board lock exists
- MINT ignores PAM1 and FTN candidates unless a strategy is board-cleared
