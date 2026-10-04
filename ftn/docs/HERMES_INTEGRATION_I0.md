# HERMES OS Integration — I0 invariants (FROZEN)

**Cross-repo contract.** Distinct from FTN internal `INTEGRATION_SUITE.md` (multi-month OS isolation).

## Architecture

```
                    HERMES OS
              ┌─────────────────┐
              │  DayContext     │
              │  producer today │
              │  = ftn-agent    │
              └────────┬────────┘
                       │ handoff.v1 (transport only)
              ┌────────┴────────┐
              │                 │
              ▼                 ▼
        HERMES DESK          MINT
        projection          execution
              │                 │
              └──── HUMAN ──────┘
```

Target ownership: HERMES-X is research SoT. **Implementation reality (I0):** DayContext is **constructed in ftn-agent**. Hermes-X consumes exports; it does not currently reconstruct FTN state.

Desk is never the middleman between FTN/Hermes-X and MINT.

## Ownership

| Component | Owns | Does not own |
|-----------|------|----------------|
| ftn-agent | DayContext construction + export | Desk presentation, Mint orders |
| HERMES-X | Research ledger, investigations, board | Reconstructing FTN detectors |
| HERMES Desk | Read-only projection | PAM/M9 reasoning, orders |
| MINT | Execution / P&L | ICT interpretation |
| handoff.v1 | Transport of DayContext | A second domain model |

## Canonical object

- **DayContext** = only shared domain object.
- **handoff.v1.json** = serialized transport (`schemaVersion: "1"`, `kind: "day_context_handoff"`).
- “HERMES Day Package” = conceptual name only — not a third schema.

## Data classes

1. **Evidence** (HERMES-X / FTN labels) — observed / labeled / measured.
2. **Intelligence** (HERMES-X / FTN derivation) — Market State, Charter/PAM recognition, candidates.
3. **Execution state** (MINT only) — paper ticket, order, fill, P&L, journal.

## Vocabulary (must not collapse)

`setup_elements` · `low_risk_frame` · `next_setup` · `array_opportunity` · `position_opportunity` · `swing_opportunity` · `paper_swing` · candidate · `session_ticket` · order · Charter recognition · PAM1 completeness

Annotation ≠ opportunity ≠ candidate ≠ ticket ≠ order.  
Recognition ≠ clearance ≠ execution.

## Handoff bans (Phase I)

Must be **absent** (not merely null):

- BUY / SELL recommendation  
- confidence / best_pam / pam_rank  
- broker_instruction / automatic clearance as an instruction  

Allowed: evidence, context, recognition, candidates, research refs, clearance **projection**, execution **projection**.

## PAM1 pilot

PAM1 is research intelligence on DayContext. Desk may display it. MINT ignores PAM1 unless a future **cleared strategy_id** exists.

## Provenance

Block/artifact-level first (`_provenance` optional). Not every primitive field.

## Operating modes (docs only)

Historical · Live observation · Paper · Live (dual unlock). Not separate product builds in Phase I.

## Phase I sequence

| Slice | Scope |
|-------|--------|
| I0 | This document |
| I1a | Cross-repo docs (this file) |
| I1b | handoff.v1 + PAM1 evidence/completeness on export |
| I1c | Acceptance fixture tests (after I1b review) |
| I1d–e | Desk `dayContext.js` sibling adapter |
| I1f | Manual E2E projection |
| I2+ | Provenance UX, Mint read-only clearance, paper loop |

## I1 acceptance question

> Can Desk display the same PAM1/Charter/Market State facts as the FTN handoff **without any code that independently derives those facts?**

## Non-goals (Phase I)

API · DB · live primary feed · Mint wiring · ORION/LOOM changes · new ICT detectors · merging the three repos.
