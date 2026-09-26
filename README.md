# HERMES — research → execution → desk (monorepo)

One repo for PROJECT HERMES-X: the **research evidence spine**, the **MINT** paper-first
execution layer, and the **HERMES Desk** ICT charting terminal.

| Path | What it is | Formerly |
|------|------------|----------|
| [`research/`](research/) | Research evidence spine — `investigations/`, `evidence/`, `beliefs/LEDGER.md`, `summaries/` (board locks, utilization memos), `protocols/`, `risk/`, `scripts/`, and the **LOOM** workflow-agent package in `agent/`. ORION curates. | [`GdotAiM/hermes-x`](https://github.com/GdotAiM/hermes-x) |
| [`trading/`](trading/) | **MINT** — paper-first execution & P&L layer. Python package `mint` (`trading/src/mint`): Alpaca paper stub, dispatch scanner, W4 execution workflow, allowlist, journals. | [`GdotAiM/mint-agent`](https://github.com/GdotAiM/mint-agent) |
| [`desk/`](desk/) | **HERMES Desk** — vanilla HTML/CSS/JS Canvas ICT trading terminal (slices A–K: overlays, replay, data adapter, paper ticket → MINT, research-contract adapter, board-status chip). | [`GdotAiM/hermes-desk`](https://github.com/GdotAiM/hermes-desk) |

All three were imported **with full git history** (`git filter-repo --to-subdirectory-filter`
per repo, then `git merge --allow-unrelated-histories`; no squash). Use
`git log --full-history -- <dir>` / `git log --follow` to browse per-part history. Commit SHAs
of imported history differ from the original repos (paths were rewritten).

## How the parts connect

```
research/summaries/*_BOARD_LOCK.md ─┐
research/beliefs/LEDGER.md ─────────┼─▶ trading: mint.dispatch.scan_clears ─▶ trading/dispatch/out/latest.json
                                    │        (tickets only — never orders)            │
                                    │                                                 ▼
                                    └─▶ desk: research-contract adapter / board chip   desk: paper ticket stub → MINT Path B
```

- **research → trading.** `scan_clears` reads board locks and the LEDGER from `../research`
  (auto-detected; override with `--hermes-x PATH` or `HERMES_RESEARCH_PATH`). FAILS → demotion
  filters, VERIFY → prior log, INCONCLUSIVE → park, SURVIVES → `entry_candidate` that *still*
  needs allowlist + RISK + human ack. The old `trading/` mirror and mint-agent ↔ hermes-x sync
  are retired (see [`trading/SYNC.md`](trading/SYNC.md)).
- **research/trading → desk.** Serve the repo root (`python3 -m http.server 8765`, open
  `/desk/`); the desk loads research JSON and MINT tickets by same-origin relative paths
  (`../research/…`, `../trading/dispatch/out/latest.json`). No GitHub raw URLs.
- **CI** (root `.github/workflows/`, path-filtered):
  - `mint-e2e-dry.yml` — `trading/**` or research board/LEDGER changes → pytest + E2E dry-run
    (working-directory `trading`, scanning `../research`).
  - `mint-notify-on-board.yml` — research board/LEDGER change on `main` → runs `scan_clears`
    in-repo, posts `latest.json` to the job summary + artifact.
  - `desk-check.yml` — `desk/**` → JS module syntax check + `index.html` asset refs.

Paths written inside `research/` docs are relative to `research/` (e.g. `summaries/…` means
`research/summaries/…`) unless prefixed with `trading/` or `desk/`.

## Quick start

```bash
git clone https://github.com/GdotAiM/hermes.git && cd hermes

# MINT tests + dispatch scan (from trading/)
cd trading
python3 -m pip install pytest && python3 -m pytest -q
PYTHONPATH=src python3 -m mint.dispatch.scan_clears      # → dispatch/out/latest.json
PYTHONPATH=src python3 -m mint place_order --symbol QQQ --qty 1 --side buy   # dry-run
cd ..

# Desk
python3 -m http.server 8765   # open http://localhost:8765/desk/
```

## Paper-only limits (hard)

| Limit | Value |
|-------|-------|
| Starting paper equity | **$100,000** |
| Max risk per trade | **0.5%** |
| Max daily loss | **2%** |
| Max portfolio drawdown | **5%** |
| Live execution | **None.** MINT defaults to `mode: paper`, `live_enabled: false`; live would need human dual unlock (`live_enabled: true` **and** `MINT_LIVE=1`) and is out of scope. Caps cannot rise without human approval. |

Wave 1 has **no cleared tradeable edge** (zero SURVIVES): the allowlist is no-trade filters
and research logging only. The desk shows *Paper research* and never routes orders.

## Secrets

Never commit tokens, `.env`, or credentials. The old `HERMES_X_SYNC_TOKEN` PAT is no longer
needed — revoke it if it exists.
