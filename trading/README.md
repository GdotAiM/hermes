# MINT Agent

**Paper-first execution & P&L AI agent** for PROJECT HERMES-X — the `trading/` part of the [GdotAiM/hermes](../README.md) monorepo.

MINT is the company layer that turns **board-locked** research into risk-capped paper orders (Alpaca API/CLI-ready). It does **not** invent ICT setups from chat.

| Default | Live |
|---------|------|
| `mode: paper` · `live_enabled: false` | Requires human unlock in `config.yaml` **and** `MINT_LIVE=1` |

**Wave 1 reality:** no cleared tradeable edge yet. Allowlist = no-trade filters + research logging only.

## Quick start (inside the GdotAiM/hermes monorepo)

```bash
git clone https://github.com/GdotAiM/hermes.git
cd hermes/trading
python3 -m venv .venv && source .venv/bin/activate
pip install -e .            # or prefix commands with PYTHONPATH=src
cp .env.example .env        # add PAPER Alpaca keys if you want account smoke tests
python3 -m mint account                                   # dry / paper account
python3 -m mint place_order --symbol QQQ --qty 1 --side buy   # dry-run by default
python3 -m pytest -q        # tests (pytest config sets pythonpath=src)
```

## Layout

```
AGENT.md                 # Full agent charter (paste into Claude Code / Cursor)
AGENTS.md                # Operating rules for coding agents
config.yaml              # Paper/live locks, caps, allowlist
ALLOWLIST.md             # How strategies get clearance
docs/MINT_PROMPT.md      # Role prompt
dispatch/                # research board -> MINT tickets (no orders)
src/mint/
  adapters/              # Alpaca docs + paper stub
  dispatch/scan_clears.py
  workflows/W4_EXECUTION.md
  journal/               # Decision templates
  strategies/            # Strategy templates
tests/                   # pytest
```

## Relationship to the rest of the monorepo

| Layer | Path | Role |
|-------|------|------|
| Research spine | [`../research/`](../research/) | ORION, LOOM, QUANT, CASSANDRA, … board locks + LEDGER |
| Execution | **`trading/` (this folder)** | MINT |
| Desk | [`../desk/`](../desk/) | HERMES Desk charting terminal; paper ticket stub points here |

This folder was imported with full history from the former standalone repo
`GdotAiM/mint-agent`. The old `hermes-x/trading/` lab mirror and its sync
scripts/Action are **retired** — see [`SYNC.md`](SYNC.md).

## Auto-dispatch (not auto-trade)

From `trading/` — the research spine is auto-detected at `../research`:

```bash
PYTHONPATH=src python3 -m mint.dispatch.scan_clears            # writes dispatch/out/latest.json
PYTHONPATH=src python3 -m mint.dispatch.scan_clears --apply-filters
cat dispatch/out/latest.json
```

Override with `--hermes-x PATH` (alias `--research`) or `HERMES_RESEARCH_PATH` / `HERMES_X_PATH`.
The scanner exits **2** with a clear error if `summaries/` or `beliefs/LEDGER.md` is missing.
Tickets ≠ orders. See [`dispatch/README.md`](dispatch/README.md).

## E2E dry-run (fixture)

```bash
REQUIRE_HERMES_SCAN=1 bash fixtures/paper_pilot_e2e/run_e2e_dry.sh
```

CI (root `.github/workflows/mint-e2e-dry.yml`) runs pytest + this script against `../research`
with `REQUIRE_HERMES_SCAN=1` so the dispatch scan cannot silently skip.
Path B paper-pilot fixture — not a science SURVIVES.

## Safety

- No secrets in git
- No MERCURY/live promotion from VERIFY/FAILS/INCONCLUSIVE
- RISK caps cannot rise without human approval

## License

MIT
