# MINT Agent

**Paper-first execution & P&L AI agent** for [PROJECT HERMES-X](https://github.com/GdotAiM/hermes-x).

MINT is the company layer that turns **board-locked** research into risk-capped paper orders (Alpaca API/CLI-ready). It does **not** invent ICT setups from chat.

| Default | Live |
|---------|------|
| `mode: paper` · `live_enabled: false` | Requires human unlock in `config.yaml` **and** `MINT_LIVE=1` |

**Wave 1 reality:** no cleared tradeable edge yet. Allowlist = no-trade filters + research logging only.

## Quick start

```bash
git clone https://github.com/GdotAiM/mint-agent.git
cd mint-agent
python3 -m venv .venv && source .venv/bin/activate
pip install -e .
cp .env.example .env   # add PAPER Alpaca keys if you want account smoke tests
python -m mint account                 # dry / paper account (needs keys for live HTTP)
python -m mint order --symbol QQQ --qty 1 --side buy   # dry-run by default
```

## Layout

```
AGENT.md                 # Full agent charter (paste into Claude Code / Cursor)
AGENTS.md                # Operating rules for coding agents
config.yaml              # Paper/live locks, caps, allowlist
ALLOWLIST.md             # How strategies get clearance
docs/MINT_PROMPT.md      # Role prompt
src/mint/
  adapters/              # Alpaca docs + paper stub
  workflows/W4_EXECUTION.md
  journal/               # Decision templates
  strategies/            # Strategy templates
```

## Relationship to HERMES-X

| Layer | Repo / role |
|-------|-------------|
| Research lab | [hermes-x](https://github.com/GdotAiM/hermes-x) — ORION, LOOM, QUANT, CASSANDRA, … |
| Execution | **this repo** — MINT |
| Mirror in lab | `hermes-x/trading/` stays in sync as the lab-side package |

## Safety

- No secrets in git
- No MERCURY/live promotion from VERIFY/FAILS/INCONCLUSIVE
- RISK caps cannot rise without human approval

## License

MIT
