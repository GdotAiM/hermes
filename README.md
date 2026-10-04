# HERMES — research → execution → desk (monorepo)

One repo for PROJECT HERMES-X: the **research evidence spine**, the **MINT** paper-first
execution layer, the **HERMES Desk** ICT charting terminal, and **FTN** (Filling The
Numbers), the paper-first ICT daily-range engine that produces the shared DayContext.

| Path | What it is | Formerly |
|------|------------|----------|
| [`research/`](research/) | Research evidence spine — `investigations/`, `evidence/`, `beliefs/LEDGER.md`, `summaries/` (board locks, utilization memos), `protocols/`, `risk/`, `scripts/`, and the **LOOM** workflow-agent package in `agent/`. ORION curates. | [`GdotAiM/hermes-x`](https://github.com/GdotAiM/hermes-x) |
| [`trading/`](trading/) | **MINT** — paper-first execution & P&L layer. Python package `mint` (`trading/src/mint`): Alpaca paper stub, dispatch scanner, W4 execution workflow, allowlist, journals. | [`GdotAiM/mint-agent`](https://github.com/GdotAiM/mint-agent) |
| [`desk/`](desk/) | **HERMES Desk** — vanilla HTML/CSS/JS Canvas ICT trading terminal (slices A–K: overlays, replay, data adapter, paper ticket → MINT, research-contract adapter, board-status chip) + FTN DayContext adapter (`js/adapters/dayContext.js`). | [`GdotAiM/hermes-desk`](https://github.com/GdotAiM/hermes-desk) |
| [`ftn/`](ftn/) | **FTN** — Filling The Numbers: paper-first ICT daily-range engine (`src/ftn`: `os/` Month-1–12 + PAM1 modules, `engine`, `models` REV/CONSO/PIP20/BB/FTN, `workflow/orchestrator`, `adapters`, `journal`), 58 fixtures (EURUSD-first, 2 XAUUSD), 171 docs. **DayContext producer**: exports `ftn/dispatch/out/handoff_latest.json` (handoff.v1). | `ftn-agent` zip (no git history; no GitHub repo) |

`research/`, `trading/` and `desk/` were imported **with full git history** (`git filter-repo --to-subdirectory-filter`
per repo, then `git merge --allow-unrelated-histories`; no squash). Use
`git log --full-history -- <dir>` / `git log --follow` to browse per-part history. Commit SHAs
of imported history differ from the original repos (paths were rewritten). `ftn/` came from a
zip with no history and was added as a single import commit (2026-10-04).

## How the parts connect

### The one shared contract: handoff.v1 (FTN DayContext)

```
ftn/ (FTN brief) ──▶ ftn/dispatch/out/handoff_latest.json   schemaVersion "1", kind "day_context_handoff", mode "paper"
                        │   schema: ftn/dispatch/schema/handoff.v1.schema.json
                        │   validator + recursive bans: ftn.os.handoff_contract   (samples: ftn/dispatch/samples/)
          ┌─────────────┼──────────────────────────────┬───────────────────────────────────┐
          ▼             ▼                              ▼                                   ▼
 desk: dayContext.js   trading: mint.dispatch.ftn_context   research: scripts/file_ftn_handoff.py   (human)
 read-only projection  context record only — never orders  → research/evidence/ftn/ (evidence intake)
```

- **Bans** (absent at any depth, enforced by FTN tests, the Desk guard and the MINT reader):
  BUY/SELL calls, `confidence`, `best_pam` / `pam_rank`, `broker_*`, order fields.
  FTN's internal IOF label `confidence` is exported as `qualification`.
- **Desk** displays Market State, Charter, PAM1, candidates and FTN levels verbatim (no
  desk-side derivation — FTN's I1 acceptance test, `desk/tests/dayContext.test.mjs`).
- **MINT** logs DayContext as context; FTN candidates, the FTN session ticket and PAM1 never
  become orders (`trading/tests/test_ftn_context.py`). Only a research board SURVIVES can
  clear a strategy, and even then entries go through allowlist + RISK + human ack.
- **Research** files handoffs as evidence, not claims; open questions live in
  `research/investigations/INV-003-ftn-intake/` (no verdicts).

### Research board → MINT → Desk

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
- **CI** (path-filtered; **staged in [`ci/github-workflows/`](ci/github-workflows/) until moved to `.github/workflows/`** — see that README; the creating token lacked the `workflow` scope):
  - `mint-e2e-dry.yml` — `trading/**` or research board/LEDGER changes → pytest + E2E dry-run
    (working-directory `trading`, scanning `../research`).
  - `mint-notify-on-board.yml` — research board/LEDGER change on `main` → runs `scan_clears`
    in-repo, posts `latest.json` to the job summary + artifact.
  - `desk-check.yml` — `desk/**` → JS module syntax check + `index.html` asset refs + DayContext adapter acceptance test.
  - `ftn-check.yml` — `ftn/**` (+ MINT dispatch, desk adapter) → FTN pytest, handoff sample validation, `scripts/e2e_fixtures.sh`.

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

# FTN tests + one-shot fixture E2E (FTN brief → contract → MINT scan → ftn_context → desk test)
cd ftn && rm -f dispatch/out/*.json && python3 -m pytest -q && cd ..
scripts/e2e_fixtures.sh            # or: make e2e   (E2E_TESTS=1 / make e2e-full adds pytest)

# Desk
python3 -m http.server 8765   # open http://localhost:8765/desk/  → EURUSD → FTN DayContext → Load
```

## Honest limits

- **Desk data is synthetic** for every symbol (NQ/ES/YM and the new EURUSD/XAUUSD). FTN levels
  are drawn verbatim from the handoff onto *synthetic* bars — they line up in scale only; the
  bars are not the fixture day's tape.
- **FTN is forex-first** (EURUSD pips, some XAUUSD); the Desk and Wave-1 research are
  **index-first** (NQ points). There is no EURUSD/XAUUSD tape in `research/` yet.
- FTN fixtures are hand-labelled single days, not a sample; FTN's tests prove reconstruction,
  not edge. Nothing FTN emits is a tradeable claim until the research board says SURVIVES.
- No single FTN fixture carries both PAM1/Charter and FTN four levels, so there are two
  committed samples.

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
