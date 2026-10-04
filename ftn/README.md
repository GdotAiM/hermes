# FTN Agent — Filling The Numbers

> Part of the [GdotAiM/hermes](../README.md) monorepo since 2026-10-04 (imported from the
> `ftn-agent` zip as one commit — there was no git history and no GitHub repo). Siblings:
> [`../research/`](../research/), [`../trading/`](../trading/) (MINT), [`../desk/`](../desk/).
> FTN is the **DayContext producer**; its handoff.v1 export is the monorepo's one shared
> contract. See "In the monorepo" below and [`docs/HERMES_INTEGRATION_I0.md`](docs/HERMES_INTEGRATION_I0.md).

Paper-first ICT orchestration agent in the same company style as MINT
([`../trading/`](../trading/), formerly GdotAiM/mint-agent).

FTN runs the Month-09 *Filling The Numbers* workflow:

1. Daily prep (HTF context + four measurement families)
2. Pre-session filter (bias + four-level count)
3. Kill-zone watch (London / NY AM)
4. Setup gate (raid → displacement → MSS → PD-array retrace)
5. Management (scale after four numbers; leave a runner)
6. Close-of-day journal

**It does not invent live edges and does not place live orders.**
Default mode is `paper`. Live requires dual unlock (`live_enabled: true` **and**
`FTN_LIVE=1`) and is still refused by the stub.

## In the monorepo

| What | Where |
|------|-------|
| **The contract** | `dispatch/out/handoff_latest.json` (written by `ftn brief`; git-ignored scratch) — `schemaVersion "1"`, `kind "day_context_handoff"`, `mode "paper"` |
| Schema / validator | `dispatch/schema/handoff.v1.schema.json` · `python -m ftn.os.handoff_contract FILE…` (structure + recursive bans) |
| Committed samples | `dispatch/samples/` (real `ftn brief` output from 2 fixtures; see its README) |
| Contract tests | `tests/test_handoff_contract.py` (samples, every fixture's handoff, 18 injected ban violations, regeneration equality) |
| Desk projection | `../desk/js/adapters/dayContext.js` (read-only; acceptance test `../desk/tests/dayContext.test.mjs`) |
| MINT reader | `../trading/src/mint/dispatch/ftn_context.py` (context only; never orders) |
| Research intake | `../research/scripts/file_ftn_handoff.py` → `../research/evidence/ftn/`; open questions `../research/investigations/INV-003-ftn-intake/` |
| One-shot E2E | `../scripts/e2e_fixtures.sh` (`make e2e`) |

Changes made on import (beyond moving files): the handoff export renames the internal
`InstitutionalContext.confidence` IOF label to `qualification` (the I0 bans forbid a
`confidence` key anywhere; FTN's own test only checked top-level keys), and the handoff
contract module/schema/samples/tests above were added. No engine logic changed.

Fixes on branch `ftn-fixes` (after import): lazily resolved, env-overridable output dirs and
isolated tests; deterministic `sha256:` fingerprint; `ftn brief` / `ftn run` refuse the wrong
fixture type with a clear message; the old MINT paper draft became an opt-in research draft
without a buy/sell side; `ftn run` tickets are never `actionable_for_mint`. Model/candidate
logic is unchanged (all reconstruction tests still pass).

**Not the contract:** `dispatch/out/latest.json` (from `ftn run`, the older six-stage
FTN ticket; since ftn-fixes its kind is `ftn_setup_ticket`/`no_trade` — never MINT's own
`entry_candidate` — and `actionable_for_mint` is always `false`) and the legacy research draft from `src/ftn/os/mint_draft.py`. That draft is
no longer written by default; with `FTN_WRITE_MINT_DRAFT=1`, `ftn brief` writes
`dispatch/drafts/ftn_draft_*.json` (outside `dispatch/out/`). It carries
`direction_hypothesis` (the IOF label: bullish/bearish/unclear), never a buy/sell `side`
(I0 bans BUY/SELL), and `actionable_for_mint: false`. MINT's reader rejects both; only
handoff.v1 crosses part boundaries.

### Known limitations (honest)
- Forex-first: fixtures are EURUSD (56) and XAUUSD (2), hand-labelled single days
  (mostly 2017–2018). The Desk / Wave-1 research are index-first (NQ). Fixtures are not a
  sample — tests prove the engine reproduces the labelled reconstructions, not an edge.
- `fingerprint` is `sha256:` + 16 hex of SHA-256 over the canonical JSON of the DayContext
  (`ftn.os.contracts.context_fingerprint`) — deterministic across processes and
  `PYTHONHASHSEED` values. (Before ftn-fixes it was a salted `abs(hash(json))`.)
- Output dirs are resolved at call time (`src/ftn/paths.py`): `FTN_OUT_DIR` (default
  `dispatch/out`), `FTN_JOURNAL_DIR` (`dispatch/journal`), `FTN_DRAFT_DIR` (`dispatch/drafts`).
  The test suite redirects all three to `tmp_path` (`tests/conftest.py`), so it is
  idempotent and order-independent and never touches the real `dispatch/` folders.
- `fixtures/sample_eurusd.json` is for `ftn run/prep`. `ftn brief` refuses it, the `*.expected.json`
  gold oracles and handoff.v1 outputs with a one-line reason and exit code 2 (no traceback).

## Old desk (reference only)

FTN's standalone desk now lives in [`desk-reference/`](desk-reference/) and is **superseded**
by the monorepo Desk + `dayContext.js`. Its `levels.js` computed pivots/ranges in the
browser; that was deliberately not ported (no desk-side derivation).

## Quick start

```bash
cd ftn
python3 -m venv .venv && source .venv/bin/activate
pip install -e . pytest
python3 -m ftn brief --fixture fixtures/m9_reconstruction_eurusd.json   # → dispatch/out/handoff_latest.json
python3 -m ftn.os.handoff_contract dispatch/out/handoff_latest.json     # contract check
python3 -m ftn brief --fixture fixtures/m9_raw_eurusd.json              # REV session ticket; research-draft gate chain blocked_by allowlist
python3 -m ftn run --symbol EURUSD --fixture fixtures/sample_eurusd.json
rm -f dispatch/out/*.json && pytest                                     # clean first (see limitations)
```

### One ticket authority, one research-draft gate chain

`ftn brief` is the only path that reaches the Month-9 kernel
(`src/ftn/os/briefing.py::brief_from_fixture`); `ftn run` refuses DTR fixtures and points to
`ftn brief`. The brief evaluates one research-draft gate chain (`src/ftn/os/mint_draft.py`):

1. `kernel_ticket` — the kernel selected an entry model (REV/CONSO/BB/PIP20) and persisted its session ticket.
2. `direction` — `direction_hypothesis` (bullish/bearish) from evidence, never defaulted
   (REV/BB/PIP20: daytrade IOF; CONSO: raided box edge).
3. `risk` — `config.yaml` caps: 0.5% per trade, 2% daily loss, 5% drawdown, valid protective stop.
4. `allowlist` — the model is on `config.yaml mint_allowlist` (see `docs/MINT_ALLOWLIST.md`); stamps must be signed.
5. `mode` — paper only. Live stays dual-locked and refused; no broker routing.
6. `contract` — **always FAIL** (`hermes_integration_i0_ftn_never_actionable`): under the frozen
   HERMES_INTEGRATION_I0 contract FTN output is never MINT-actionable.

So the draft (`kind: ftn_research_draft`, written to `dispatch/drafts/` only with
`FTN_WRITE_MINT_DRAFT=1`) always has `actionable_for_mint: false`, never a `side`, and records
`gates_before_contract_pass` plus `blocked_by`. **Today the allowlist is empty**, so every kernel
ticket is `blocked_by: allowlist:not_on_mint_allowlist`. Months 1–8, 10–12, the Charter and
Model 13 are context on the DayContext; they never issue tickets. `FTN_CONFIG` selects another config file.

## Layout

```
AGENT.md                 # Charter (paste into Claude Code / Cursor)
AGENTS.md                # Coding-agent operating rules
config.yaml              # Paper/live locks, sessions, risk caps
src/ftn/
  os/                    # Month-1–12 + PAM1/Charter modules, DTR, candidates, handoff(+_contract)
  engine/                # Pivots, CBDR, Asian, Flout, PD-array overlap
  models/                # REV, CONSO, PIP20, BB, FTN
  workflow/              # Six-stage orchestrator
  adapters/              # Paper stub (no live broker)
  journal/               # Decision template
dispatch/schema/         # handoff.v1 JSON Schema
dispatch/samples/        # committed handoff.v1 samples
fixtures/                # 58 hand-labelled day fixtures (+ *.expected.json gold)
docs/                    # month/slice sources, briefings, PAM1, HERMES_INTEGRATION_I0
desk-reference/          # old standalone desk (superseded, reference only)
```

## Safety (inherited from MINT)

- Paper default
- Dual unlock for live — stub still refuses live
- No secrets in git
- Tickets ≠ orders
- Caps cannot rise without a human

## License

MIT
