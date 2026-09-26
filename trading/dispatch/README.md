# Dispatch — research spine → MINT

Watches lab **board locks** (`../research/summaries/*BOARD_LOCK*.md`) + **LEDGER** (`../research/beliefs/LEDGER.md`) and emits **tickets** (no broker calls).

```bash
# from trading/ — research root auto-detected at ../research
PYTHONPATH=src python3 -m mint.dispatch.scan_clears
PYTHONPATH=src python3 -m mint.dispatch.scan_clears --apply-filters
cat dispatch/out/latest.json
```

| Ticket kind | MINT action |
|-------------|-------------|
| `entry_candidate` (SURVIVES) | Propose allowlist PR + RISK review — **still no auto order** |
| `demote_filter` (FAILS) | Update no-trade filters |
| `prior_log` (VERIFY) | Research logging only |
| `ignore` (INCONCLUSIVE) | Park |

Automation: root Action `.github/workflows/mint-notify-on-board.yml` runs this scanner in-repo on research board/LEDGER changes and publishes `latest.json` as a job summary + artifact.

Scheduled routines must either run from `trading/` with `PYTHONPATH=src` (or after `pip install -e trading`) — otherwise `python3 -m mint...` fails with `ModuleNotFoundError: No module named 'mint'`.
