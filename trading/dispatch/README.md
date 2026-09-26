# Dispatch — HERMES-X → MINT

Watches lab **board locks** + **LEDGER** and emits **tickets** (no broker calls).

```bash
PYTHONPATH=src python3 -m mint.dispatch.scan_clears --hermes-x ../hermes-x
PYTHONPATH=src python3 -m mint.dispatch.scan_clears --hermes-x ../hermes-x --apply-filters
cat dispatch/out/latest.json
```

| Ticket kind | MINT action |
|-------------|-------------|
| `entry_candidate` (SURVIVES) | Propose allowlist PR + RISK review — **still no auto order** |
| `demote_filter` (FAILS) | Update no-trade filters |
| `prior_log` (VERIFY) | Research logging only |
| `ignore` (INCONCLUSIVE) | Park |

Automation: hermes-x Action `mint-notify-on-board.yml` notifies on board/LEDGER changes. Scanner is the local/CI worker.
