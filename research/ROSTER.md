# HERMES-X Roster

ORION (Director of Financial Intelligence) — synthesis layer. Determines what matters.

**LOOM** (Workflow Conductor) — process compliance / stage machine. See `agent/AGENT.md`. ORION = science priority/board; LOOM = packaging gates, vocabulary, handoffs.

## Live agents

| Agent | Role | Status |
|-------|------|--------|
| ORION | Synthesis / Financial Intelligence Director | Live (this chat) |
| LOOM | Workflow Conductor (stage machine / process compliance) | Live |
| ATLAS | Market Intelligence | Live |
| QUANT | Quantitative Research | Live |
| CASSANDRA | Research Red Team | Live |
| MACRO | Macroeconomic Intelligence | Live |
| HISTORIAN | Market Behavior Historian | Live |
| DATA | Data Quality | Live |
| RISK | Portfolio Risk Officer | Live |
| FORGE | CTO / Systems Architect | Live |
| MERCURY | Experimental AI Portfolio Manager | Live |
| MINT | Execution & P&L (paper default; live locked) | Live package |

## Pipeline

ATLAS / MACRO / HISTORIAN / DATA → QUANT → CASSANDRA → RISK → MERCURY → **MINT** (paper exec / P&L) → ORION
FORGE beside the loop (systems) · LOOM beside the loop (process) · MINT paper-only until human live unlock

## Paper hard caps

- Starting equity: $100,000
- Max trade risk: 0.5%
- Max daily loss: 2%
- Max portfolio drawdown: 5%
- No live execution without human dual unlock (`MINT_LIVE=1` + config `live_enabled`); limits cannot rise without human approval
- MINT package: `trading/` — Wave 1 allowlist has **no entry strategies**

## Human

Ntloso — human researcher. MERCURY must not imitate Ntloso's decisions.
