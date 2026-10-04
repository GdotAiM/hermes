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

API · DB · live primary feed · Mint wiring · ORION/LOOM changes · new ICT detectors.

~~merging the three repos~~ — **superseded 2026-10-04 by the user's decision** ("Yes, integrate FTN
fully as planned"): FTN now lives in the `GdotAiM/hermes` monorepo as `ftn/`, alongside
`research/` (HERMES-X), `trading/` (MINT) and `desk/` (HERMES Desk). The invariants above are
unchanged: DayContext is still the only shared object and handoff.v1 is still transport only.
"Mint wiring" remains read-only (see below) — MINT never acts on FTN output.

## Monorepo status (2026-10-04)

| Slice | State | Where |
|-------|-------|-------|
| I1b handoff.v1 + PAM1 on export | DONE | `src/ftn/os/handoff.py` (IOF `confidence` exported as `qualification` to satisfy the bans) |
| I1c acceptance fixture tests | DONE | `tests/test_handoff_contract.py`, `dispatch/schema/handoff.v1.schema.json`, `src/ftn/os/handoff_contract.py`, `dispatch/samples/` |
| I1d–e Desk `dayContext.js` | DONE | `../desk/js/adapters/dayContext.js` + `../desk/tests/dayContext.test.mjs` |
| I1f Manual E2E projection | DONE (headless screenshots; fixture E2E `../scripts/e2e_fixtures.sh`) | |
| I2 Mint read-only | DONE (context only) | `../trading/src/mint/dispatch/ftn_context.py` + `../trading/tests/test_ftn_context.py` |
| HERMES-X evidence intake | DONE | `../research/scripts/file_ftn_handoff.py` → `../research/evidence/ftn/`; questions `../research/investigations/INV-003-ftn-intake/` |

**I1 acceptance answer: yes.** Every PAM1 / Charter / Market State value and every chart level
the Desk shows is read verbatim from a handoff JSON path (the row's tooltip shows the path);
the node test asserts value == handoff[path] for both committed samples and that the adapter
contains none of the old desk's level math. Limits: Desk bars are synthetic; FTN is
forex-first while Desk/Wave-1 research are index-first.
