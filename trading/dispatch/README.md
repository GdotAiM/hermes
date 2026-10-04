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

Automation: Action `mint-notify-on-board.yml` (staged in `ci/github-workflows/`, to be moved to root `.github/workflows/`) runs this scanner in-repo on research board/LEDGER changes and publishes `latest.json` as a job summary + artifact.

Scheduled routines must either run from `trading/` with `PYTHONPATH=src` (or after `pip install -e trading`) — otherwise `python3 -m mint...` fails with `ModuleNotFoundError: No module named 'mint'`.

## FTN DayContext (read-only context, never orders)

`mint.dispatch.ftn_context` reads the FTN handoff.v1 contract
(`../ftn/dispatch/out/handoff_latest.json`; override `--handoff PATH` or
`$FTN_HANDOFF_PATH`) and writes `dispatch/out/ftn_context_latest.json`:

```bash
PYTHONPATH=src python3 -m mint.dispatch.ftn_context
PYTHONPATH=src python3 -m mint.dispatch.ftn_context --handoff ../ftn/dispatch/samples/handoff_v1_m9_reconstruction_eurusd_2017-05-30_london.json
```

- Rejects (exit 1, writes nothing) anything that is not `schemaVersion "1"` /
  `kind "day_context_handoff"` / `mode "paper"`, or that carries a banned field at
  any depth (BUY/SELL calls, confidence, best_pam/pam_rank, broker_*, order fields).
  FTN's `mint_draft_*.json` files are **not** the contract and are rejected.
- Records context (symbol/date/session, profile, candidates, PAM1 completeness,
  FTN objectives, FTN session-ticket id) plus the research board gate.
- `execution.order_intents_emitted` is always `0`; FTN candidates, the FTN
  session_ticket and PAM1 are never turned into orders. With zero SURVIVES the gate
  is `blocked_no_survives`; with a SURVIVES lock the record only says human review —
  entries still go through allowlist + RISK + human paper ack (W4).
- Refuses to run if `config.yaml` drifts from the hard paper limits ($100k,
  0.5 %/trade, 2 % daily, 5 % DD, `live_enabled: false`).
- Tests: `tests/test_ftn_context.py` (no-order proof with broker/network paths
  monkeypatched to explode, ban rejection, no broker imports, limits, ban-list parity
  with FTN).
