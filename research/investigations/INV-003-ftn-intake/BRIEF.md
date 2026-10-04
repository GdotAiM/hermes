# INV-003 — FTN intake (Filling The Numbers → candidate hypotheses)
**Opened:** 2026-10-04  
**Owner:** ORION (intake note only)  
**Status:** OPEN — intake; **no hypotheses authorized, no runs, no verdicts**

## Primary question
Which of FTN's encoded design choices are testable claims about markets (rather than
governance), and which deserve a QUANT protocol + CASSANDRA packaging review before anyone
treats FTN output as more than a reconstruction of ICT vocabulary?

## Context
FTN (`ftn/`, merged into the monorepo 2026-10-04) is a paper-first, deterministic ICT
daily-range engine: DTR → Market State → REV / CONSO / PIP20 / BB candidates → FTN four-number
objectives → candidate arbiter → one paper session ticket. It exports DayContext as
handoff.v1 (`ftn/dispatch/out/handoff_latest.json`), filed here via
`research/scripts/file_ftn_handoff.py` → `research/evidence/ftn/`.

FTN labels every rule's provenance (`ict_source` / `hermes_interpretation` /
`hermes_governance` / `hermes_empirical`). **Nothing in FTN is `hermes_empirical` yet** —
none of its choices has been tested on tape. Its ~130 tests check that the code reproduces
hand-labelled fixtures ("gold" reconstructions), not that any rule has an edge.

## Working belief (label: belief, not fact)
FTN is a faithful *recognizer*. Whether any selected candidate, arbiter order or filter
improves outcomes is unknown.

## Out of scope
- Live trading; any MINT allowlist change (MINT reads DayContext as context only)
- Editing `beliefs/LEDGER.md` or board locks from this note
- Re-deriving FTN detectors inside research/

## Candidate list
See `claims/FTN_CANDIDATE_HYPOTHESES.md` — candidates for QUANT and CASSANDRA, **unnumbered
(no H-IDs) and verdict-free**. ORION assigns H-IDs only if a candidate is promoted.

## Data reality (DATA should gate first)
- FTN fixtures (58 JSON, EURUSD-first, 2 XAUUSD) are hand-labelled single days, mostly
  2017–2018. They are **not a sample**; they cannot support any frequency or edge claim.
- No EURUSD / XAUUSD intraday tape is filed in `research/evidence/tape/` yet. Wave 1 tape is
  NQ (CONTINUOUS-KAGGLE). FTN is forex-first; the Desk and Wave 1 are index-first.
- FTN `fingerprint` is now deterministic (`sha256:` over canonical DayContext JSON); the two
  first filed rows predate that and carry the old salted `hash()` value. File sha256 stays the identity.

## Links
- STATUS: `STATUS.md`
- Candidates: `claims/FTN_CANDIDATE_HYPOTHESES.md`
- Evidence: `../../evidence/ftn/`
- FTN integration contract: `../../../ftn/docs/HERMES_INTEGRATION_I0.md`
