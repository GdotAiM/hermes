# PROJECT HERMES-X

Financial-intelligence research ledger for a multi-agent paper-trading research org.

**ORION** is the synthesis layer (this repo’s curator). Specialists (ATLAS, QUANT, CASSANDRA, MACRO, HISTORIAN, DATA, RISK, FORGE, MERCURY) feed evidence here.

## Layout

| Path | Purpose |
|------|---------|
| `beliefs/` | Belief ledger — what we thought and what changed |
| `evidence/` | Source map, taxonomy intake, macro baselines |
| `investigations/` | Live investigations (INV-001, …) |
| `summaries/` | Intelligence summaries |
| `ROSTER.md` | Agent roster and pipeline |
| `docs/WORKFLOW_BLUEPRINT.md` | Portable multi-agent + GitHub collaboration blueprint |

## Active investigations

### INV-002 — Methodology seed (program definition)
Six-video golden corpus → ICT Research Protocol v0.1. Wave 1: H001–H004 (gap 50%, 7–9→RTH, one-side sweep, first 10:00 FVG). See `investigations/INV-002-methodology-seed/` and `protocols/ICT_RESEARCH_PROTOCOL_v0.1.md`.

### INV-001 (active)

2026 ICT SMC lectures — session algorithms. Pilot: NY Lunch Algorithmic Theory (`C90xGr3kW8Y`).

- Passed Observed claims + H1b protocol (packaging cleared by CASSANDRA)
- **QUANT run HOLD** until tape stream C (MNQ Mar 2026, 1m, ET) is filed
- Large lecture media and auto-captions are **not** in git (see `.gitignore`)

## Hard paper limits

- Starting equity: $100,000
- Max trade risk: 0.5% · Max daily loss: 2% · Max portfolio DD: 5%
- No live execution

## Secrets

Never commit tokens, `.env`, or credentials. Rotate any PAT that appears in chat.
