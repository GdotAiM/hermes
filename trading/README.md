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
python3 -m mint account                 # dry / paper account (needs keys for live HTTP)
python3 -m mint order --symbol QQQ --qty 1 --side buy   # dry-run by default
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


## Sync with hermes-x

**SoT = this repo.** Lab mirror = `hermes-x/trading/`. See [`SYNC.md`](SYNC.md).

CI Action `sync-lab-mirror` opens a hermes-x PR when SoT changes (**needs** secret `HERMES_X_SYNC_TOKEN`; fails closed if missing).

```bash
./scripts/sync_to_hermes_x.sh /path/to/hermes-x
./scripts/check_drift.sh /path/to/hermes-x
```

## Auto-dispatch (not auto-trade)

```bash
HERMES_X_PATH=/path/to/hermes-x PYTHONPATH=src python3 -m mint.dispatch.scan_clears --hermes-x "$HERMES_X_PATH"
cat dispatch/out/latest.json
```

Tickets ≠ orders. See [`dispatch/README.md`](dispatch/README.md).

## E2E dry-run (fixture)

```bash
HERMES_X_PATH=/path/to/hermes-x REQUIRE_HERMES_SCAN=1 bash fixtures/paper_pilot_e2e/run_e2e_dry.sh
```

CI clones hermes-x and sets `REQUIRE_HERMES_SCAN=1` so the dispatch scan cannot silently skip.
Path B paper-pilot fixture — not a science SURVIVES.

## Safety

- No secrets in git
- No MERCURY/live promotion from VERIFY/FAILS/INCONCLUSIVE
- RISK caps cannot rise without human approval

## License

MIT
