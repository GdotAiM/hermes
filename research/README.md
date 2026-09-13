# PROJECT HERMES-X

Financial-intelligence research ledger for a multi-agent paper-trading research org.

**ORION** is the synthesis layer (this repo’s curator). Specialists (ATLAS, QUANT, CASSANDRA, MACRO, HISTORIAN, DATA, RISK, FORGE, MERCURY) feed evidence here. **MINT** is the paper execution / P&L layer (`trading/`).

## Layout

| Path | Purpose |
|------|---------|
| `agent/` | **LOOM** workflow agent package — stage machine, workflows, config |
| `beliefs/` | Belief ledger — what we thought and what changed |
| `evidence/` | Source map, taxonomy intake, macro baselines |
| `investigations/` | Live investigations (INV-001, …) + `_TEMPLATE/` |
| `summaries/` | Intelligence summaries + board/utilization templates |
| `ROSTER.md` | Agent roster and pipeline |
| `docs/WORKFLOW_BLUEPRINT.md` | Portable multi-agent + GitHub collaboration blueprint |
| `docs/CLAUDE_CODE_STARTER.md` | One-page starter prompt for Claude Code / external agents |
| `docs/prompts/` | Per-role mission prompts (ORION, ATLAS, QUANT, …) |
| `trading/` | **MINT** execution / P&L layer — paper default, live locked |
| `risk/` | RISK gates + paper book |
| `docs/ANTI_PATTERNS.md` | Wave 1 process anti-patterns |


## Agent package (LOOM)

Portable stage machine for multi-agent research via GitHub. **ORION** owns science priority/board; **LOOM** owns process compliance.

| Doc | Path |
|-----|------|
| Package README | [`agent/README.md`](agent/README.md) |
| LOOM charter | [`agent/AGENT.md`](agent/AGENT.md) |
| Config | [`agent/config.yaml`](agent/config.yaml) |
| Solo mode | [`agent/SOLO_MODE.md`](agent/SOLO_MODE.md) |
| W1 Claim→Gate | [`agent/workflows/W1_CLAIM_TO_GATE.md`](agent/workflows/W1_CLAIM_TO_GATE.md) |
| W2 Hyp→Board | [`agent/workflows/W2_HYP_TO_BOARD.md`](agent/workflows/W2_HYP_TO_BOARD.md) |
| W3 Utilization | [`agent/workflows/W3_UTILIZATION.md`](agent/workflows/W3_UTILIZATION.md) |
| Role prompts | [`docs/prompts/`](docs/prompts/) |
| INV templates | [`investigations/_TEMPLATE/`](investigations/_TEMPLATE/) |
| Blueprint | [`docs/WORKFLOW_BLUEPRINT.md`](docs/WORKFLOW_BLUEPRINT.md) |

## Active investigations

### INV-002 — Methodology seed (program definition)
Six-video golden corpus → ICT Research Protocol v0.1. Wave 1: H001–H004 (gap 50%, 7–9→RTH, one-side sweep, first 10:00 FVG). See `investigations/INV-002-methodology-seed/` and `protocols/ICT_RESEARCH_PROTOCOL_v0.1.md`.

### INV-001 (active)

2026 ICT SMC lectures — session algorithms. Pilot: NY Lunch Algorithmic Theory (`C90xGr3kW8Y`).

- Passed Observed claims + H1b protocol (packaging cleared by CASSANDRA)
- **QUANT run HOLD** until tape stream C (MNQ Mar 2026, 1m, ET) is filed
- Large lecture media and auto-captions are **not** in git (see `.gitignore`)


## Trading layer (MINT)

**MINT** turns cleared research into **paper** orders, journals, and P&L. Default `mode: paper`; live requires human dual unlock. Wave 1 has **no tradeable edge**.

| Doc | Path |
|-----|------|
| Package README | [`trading/README.md`](trading/README.md) |
| MINT charter | [`trading/AGENT.md`](trading/AGENT.md) |
| Config | [`trading/config.yaml`](trading/config.yaml) |
| Allowlist | [`trading/ALLOWLIST.md`](trading/ALLOWLIST.md) |
| W4 Execution | [`trading/workflows/W4_EXECUTION.md`](trading/workflows/W4_EXECUTION.md) |
| Alpaca adapter | [`trading/adapters/alpaca.md`](trading/adapters/alpaca.md) |
| Paper stub | [`trading/adapters/alpaca_paper_stub.py`](trading/adapters/alpaca_paper_stub.py) |
| Role prompt | [`docs/prompts/MINT.md`](docs/prompts/MINT.md) |

## Hard paper limits

- Starting equity: $100,000
- Max trade risk: 0.5% · Max daily loss: 2% · Max portfolio DD: 5%
- No live execution (MINT live locked unless human dual unlock)

## Secrets

Never commit tokens, `.env`, or credentials. Rotate any PAT that appears in chat.
