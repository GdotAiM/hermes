# ftn-agent review — 2026-10-04

Review of the FTN (Filling The Numbers) agent, imported into the HERMES monorepo as `ftn/`.
The review was done on a working copy on the agent box. Absolute `/workspace/...` paths below
are box paths kept for provenance; in this repo, the Model 13 source notes are at
`ftn/docs/review/MODEL13_SOURCE_FROM_USER.md`. Nothing was merged, and live trading stays
dual-locked.

---

## Rebase onto main (2026-10-04) — read this first

Main already merged FTN (bf26d59 / c13534c, plus scanner fix 78031e1). This branch was
rebased onto current main; only deltas main lacked were ported, and **main wins wherever it
already had an equivalent**. Rows below that describe the superseded design are kept for
history and marked here.

**Already on main (kept main's version, mine dropped):**
- F1 test isolation → main's `ftn.paths` (`FTN_OUT_DIR` / `FTN_JOURNAL_DIR` / `FTN_DRAFT_DIR`) + autouse conftest. `FTN_DISPATCH_DIR` is gone.
- F2 deterministic sha256 `context_fingerprint`.
- F3 prep never actionable, F10 run-authority (main's `ftn run` refuses DTR fixtures → `ftn brief`), F13 same-second journal names.
- F16 `ftn desk-snapshot` / FTN desk → superseded by the monorepo `desk/` + handoff.v1 `dayContext.js` adapter.
- D19 MINT scanner clears → fixed on main by 78031e1.
- My handoff additions (`last`, `execution_context`, `four_reason`) dropped: handoff.v1 is frozen (HERMES_INTEGRATION_I0) and stays byte-identical to main for every committed sample.

**Ported (deltas main lacked):**
- Research-draft gate chain in `os/mint_draft.py`, rebuilt on main's I0 draft (`kind: ftn_research_draft`, no `side`, `direction_hypothesis`):
  kernel_ticket → direction → risk → allowlist (signed-stamp check) → mode → **contract**.
  `execution_context` / `gate_input()` live in memory only; never written into the handoff.
- **D20 (new): the contract gate always FAILs** (`hermes_integration_i0_ftn_never_actionable`). This replaces F11's "actionable when all five pass". The draft records `gates_before_contract_pass` instead. Making FTN actionable needs a new integration contract and a human decision.
- `briefing.py` "Research draft (gate chain)" section (`draft_status`, direction only).
- `bias_undetermined` no_trade reason in main's orchestrator; Model 13 annotation payload (off by default); Model 13 card on the Charter layer (omitted when absent, so main's sample fingerprints don't change).
- `journal/write.py` "Ticket authority" block; `config_load.dispatch_out()` delegates to `ftn.paths.out_dir`.
- Unsigned REV paper-pilot stamp (D10, still unsigned; REV not allowlisted), staged CI workflow, tests: `test_gate_chain.py` (rewritten for I0), `test_model13.py`, `test_review_fixes{,2}.py` (main-duplicate tests removed).

## Summary

**Test results**

| | Result |
|---|---|
| Before, first run (clean `dispatch/`) | 132 passed |
| Before, second run (same tree) | **131 passed, 1 failed** (`test_month7_slice7_swing`). Tests write session/swing tickets into the repo's `dispatch/out/`, and the next run reads them back. |
| After first pass | 146 passed, same result on repeated runs. Nothing is written into the repo. |
| After `run` re-route | 198 passed, run 3× in a row, all green. The 52 new tests are in `tests/test_run_authority.py`: 6 scenarios + `run` == `brief` parametrised over all 46 dated fixtures. The direct `python tests/test_reconstruction.py` runner also exits 0. |
| **After gate chain + six fixes (current, 07:42 follow-up)** | **286 passed**, run 3× in a row, all green. 88 new tests: `tests/test_gate_chain.py` (every gate passing and blocked; run == brief == desk on all 46 dated fixtures, with the default config and with a test-only human pilot) and `tests/test_review_fixes2.py` (config parser, journal collisions, undetermined bias, desk snapshot). |

**CLI / desk smoke (Python 3.13 venv, `pip install -e .`)**

- `python3 -m ftn run --symbol EURUSD --fixture fixtures/sample_eurusd.json` → exit 0. Before the review: `entry_candidate`, `actionable_for_mint: true` from fixture booleans. Now: `no_trade` / `fixture_not_m9_daycontext` (see F10).
- `prep` → exit 0. Before the fix it also wrote an actionable `entry_candidate` to `latest.json`. Now it writes `prep_only`, not actionable.
- `brief --fixture fixtures/m9_raw_eurusd.json` → OK. `live-probe` → data off, orders refused (correct).
- Current: `run --fixture fixtures/m9_raw_eurusd.json` → `m9_session_ticket` (REV, buy), `actionable_for_mint: false`, `blocked_by: allowlist:not_on_mint_allowlist`. `brief` and the desk show the same.
- Desk served with `python3 -m http.server` and checked with curl: `/`, every `js/*.js`, `styles.css` and `os_state.json` return 200. All JS passes `node --check`. Not checked in a browser.

**Overall verdict.** The Month-9 kernel holds together: DTR → frozen MarketState → REV/CONSO/BB/PIP20 → arbiter → `session_ticket`, plus a gold oracle that the engine never reads. The separation rules (annotation ≠ candidate ≠ ticket ≠ order) are well tested. The weaknesses are elsewhere:
- (a) a legacy `ftn run` path bypassed the M9 kernel (**fixed in F10, per the user's decision**);
- (b) fixture state was persisted into the repo;
- (c) the M1–M7 and M10–M12 layers mostly echo hand labels;
- (d) the FTN handoff has no consumer in the HERMES monorepo.

Month 9 is **not** missing. It is the `os/` kernel plus `models/`; only its blueprint status line was stale.

---

## Fixes made (all in the working copy; each has a regression test)

| # | Priority | Fix | Files |
|---|---|---|---|
| F1 | P0 | **Test isolation / no repo pollution.** `session_ticket`, `m7_swing`, `handoff`, `mint_draft`, the orchestrator and the journal all wrote to `<repo>/dispatch` through paths computed at import time, which made tests order- and run-dependent. Added `config_load.dispatch_dir()/dispatch_out()` (resolved at call time, `FTN_DISPATCH_DIR` override) and an autouse session fixture in `tests/conftest.py`. The default location is unchanged for real use. | `src/ftn/config_load.py`, `os/{session_ticket,m7_swing,handoff,mint_draft}.py`, `workflow/orchestrator.py`, `journal/write.py`, `__main__.py`, `tests/conftest.py` |
| F2 | P0 | **MarketState fingerprint was not reproducible.** It used `str(abs(hash(blob)))`, and the builtin `hash()` is salted per process, so the "fingerprint" Hermes X is supposed to cite changed on every run (verified: seed 1 → 8427…, seed 2 → 2617…). Now `sha256(blob)[:16]`. | `os/contracts.py` |
| F3 | P1 | **`ftn prep` emitted an actionable entry candidate** and overwrote `latest.json`. PREP now produces `kind: prep_only`, `actionable_for_mint: false`, reason `prep_stage_only`. | `workflow/orchestrator.py` |
| F4 | P1 | **MINT draft invented a direction.** BB/PIP20/CONSO set `side = "sell"` whenever IOF was not bullish, including `unclear`. Unclear IOF now gives `side: None`. The CONSO side rule itself is open (D4). | `os/mint_draft.py` |
| F5 | P2 | **Config was declared but not loaded.** `killzones` was hardcoded in the orchestrator, and `risk_caps.*` were never parsed. Both are now loaded; the orchestrator gate uses `cfg["killzones"]` and the ticket shows `max_trade_risk_pct`. | `config_load.py`, `orchestrator.py` |
| F6 | P2 | **Desk showed synthetic data unlabelled.** The chart candles come from `synthBars()` (sin/cos), and the header had a hardcoded "−12.0 pips · PD". Added a "Synthetic bars · not market data" pill, and the header now shows the snapshot date + "synthetic chart". | `desk/index.html`, `desk/js/app.js` |
| F7 | P3 | **Stale M9 blueprint.** The status line said "no modules implemented yet", and §9 names `pd_matrix.py` / `arbiter.py`, which do not exist. Added a dated review note pointing at the real files; signed text left as is. | `docs/MONTH9_BLUEPRINT.md` |
| F8 | P3 | pytest printed "ignoring pytest config in pyproject.toml". Removed the duplicate block and moved `addopts` into `pytest.ini`. | `pyproject.toml`, `pytest.ini` |
| F9 | P3 | `brief_from_fixture` was annotated as returning a 3-tuple but returns 4 values. | `os/briefing.py` |
| — | — | First tests for the orchestrator, config and MINT draft (none existed before). | `tests/test_review_fixes.py` |
| **F10** | **P0** | **`ftn run` now goes through the Month 9 brief (user decision, 2026-10-04 07:35).** `run_workflow` calls `brief_from_fixture`, the same path as `ftn brief`, for any dated DayContext fixture. `ticket.session_ticket`, `ticket.mint_draft`, `ticket.selected_module` and `m9.{candidates,fingerprint,...}` are copied from the kernel unchanged. `ticket.actionable_for_mint` is only true when **(kernel session ticket) ∧ (kernel draft `actionable_for_mint` is true) ∧ paper mode**. The old four-number measurement and the fixture `setup` booleans are kept as research context (`legacy_context`, the old keys under `ticket`, and `ticket.legacy_gate_ok` / `legacy_filter_reasons`). `prep` never calls the kernel. The decision journal now records the ticket authority. Documented in `README.md` ("Ticket authority"), `AGENT.md` §2 and `docs/SLICES.md` "Slice R". Tests in `tests/test_run_authority.py`: (1) legacy booleans are never actionable, even on an M9 fixture with no kernel ticket; (2) `run` session ticket, MINT draft, candidates and fingerprint equal `brief`'s for every dated fixture; (3) with a permissive draft patched in, only a kernel ticket can make `run` actionable; (4) `prep` never calls the kernel; (5) non-paper mode refuses; (6) the Model 13 fixture through `run` produces no ticket. | `workflow/orchestrator.py`, `journal/write.py`, `README.md`, `AGENT.md`, `docs/SLICES.md`, `tests/test_run_authority.py`, `tests/test_review_fixes.py` |
| **F11** | **P0** | **MINT gate chain replaces the hard-coded `false` (user decision, 07:42).** `os/mint_draft.py` now evaluates `kernel_ticket → side → risk → allowlist → mode`. A draft is `actionable_for_mint: true` only if all five pass. Every draft has `gates[]`, `blocked_by` (first failing gate) or `actionable_reason`, plus `blocked[]`, `side`, `entry_reference`, `stop_reference`, `risk_pct`, `risk_usd` and `size_units`. The gates: (1) **kernel ticket**: the kernel selected an entry model and persisted a session ticket for that same model. (2) **side**: from evidence only. (3) **risk**: caps from `config.yaml` (0.5% / 2% / 5%, = HERMES `research/risk/GATES.md`); always proposes at the cap, never above; needs a protective stop; reads the daily-loss and drawdown book from `dispatch/out/paper_book.json` (flat if absent); missing inputs → HOLD. (4) **allowlist**: `config.yaml mint_allowlist`, Path A (`survives` + `board_ref`) or Path B (`paper_pilot` + `stamp` + `expires` + `kill`); the referenced file must exist and pilots expire. (5) **mode**: paper only. Live orders are still refused (`adapters/live.py`) and there is no broker routing. `briefing.draft_status()` is the single status used by `brief` (new "MINT draft (gate chain)" section), `run` (`ticket.blocked_by` / `ticket.actionable_reason`, `m9.mint_status`) and the desk. | `os/mint_draft.py`, `os/briefing.py`, `os/handoff.py` (`last`, `execution_context`), `workflow/orchestrator.py`, `config.yaml`, `docs/MINT_ALLOWLIST.md`, `docs/templates/PAPER_PILOT_STAMP_TEMPLATE.md`, `tests/test_gate_chain.py` |
| F12 | P1 | **README quick start uses a real Month 9 path.** `run`/`brief` on `fixtures/m9_raw_eurusd.json` (bar-derived raid/MSS → REV session ticket, MINT blocked by allowlist), `run` on `m9_rev_no_raid.json` (explained `no_trade`) and `desk-snapshot`. The undated `sample_eurusd.json` is documented as legacy context only. | `README.md` |
| F13 | P1 | **Collision-proof journal and dispatch names.** New `run_id` = UTC time with microseconds + 8 hex chars. Files: `ftn_<run_id>.json`, `<run_id>_DECISION.md`, written in exclusive-create mode so an existing journal is never overwritten. The journal also records ticket authority, `blocked_by` and `actionable_reason`. | `workflow/orchestrator.py`, `journal/write.py` |
| F14 | P1 | **No default bullish bias (was D2).** `detect_bias` returns `undetermined` when there is no explicit `--bias` and no `htf_bias`; `count_four` returns nothing for a non-directional bias; the kernel FTN annotation withholds the count when daytrade IOF is not bullish/bearish (`four_reason: bias_undetermined`). The briefing says "No four-count: bias undetermined … Directional targets are withheld rather than assumed." `legacy_filter_reasons` gains `bias_undetermined`. No existing fixture hit this path, so no gold changed. | `engine/levels.py`, `models/ftn.py`, `os/briefing.py`, `os/handoff.py`, `workflow/orchestrator.py` |
| F15 | P1 | **CONSO side from the raided edge (was D4).** `models/conso.raided_edge()` / `conso_side()`: raid at or through the box low → `low` → buy; through the high → `high` → sell; anything else → `None` (side gate blocks). IOF is ignored for CONSO side. The CONSO stop reference is the raided edge. The handoff carries `execution_context.conso_raided_edge`; this is evidence, not a direction field, so the handoff ban list still holds. | `models/conso.py`, `os/handoff.py`, `os/mint_draft.py` |
| F16 | P2 | **Desk draws one fixture (was D6).** New `python3 -m ftn desk-snapshot --fixture …` (`os/desk_snapshot.py`) writes `desk/js/os_state.{js,json}` from the same kernel path. It contains candles (`bars_m15`), ranges, PD arrays (from the fixture's `pd_matrix`), the FTN four, the Market State rail and `mint_status`. `app.js` no longer imports `FIXTURE`. Pivots, CBDR/Asian/Flout, PD bands and levels all come from the snapshot; synthetic candles are used only if the fixture has no bars, and the desk says so. A new rail card and the ticket modal show the same MINT gate status. The committed snapshot is regenerated from `m9_raw_eurusd.json`. JS passes `node --check`; served and curl'd: all assets 200. | `os/desk_snapshot.py`, `__main__.py`, `desk/js/app.js`, `desk/js/data.js`, `desk/index.html`, `desk/js/os_state.{js,json}` |
| F17 | P2 | **Strict config parser (was D8).** PyYAML is not a dependency (the core is stdlib-only), so `config_load.py` now parses the YAML subset the file actually uses: nested mappings, inline `{ }`, scalar and inline-mapping lists, `[]`, quoted strings, comments. It validates against an explicit schema and raises `ConfigError("config.yaml:LINE: …")` / `"config.yaml.path: …"` for unknown keys, duplicates, wrong types, out-of-range caps, bad `HH:MM`, killzones not in sessions, `raise_requires` other than `human`, bad allowlist entries, and `mode: live` without `live_enabled`. `FTN_CONFIG` overrides the path. The flat return keys are unchanged; `raw` (nested doc), `mint_allowlist` and `equity_usd` are added. | `config_load.py`, `tests/test_review_fixes2.py` |
| F18 | P1 | **Unsigned REV paper-pilot stamp prepared** (`docs/pilots/REV_PAPER_PILOT_STAMP_UNSIGNED.md`). Every factual field is filled in; the signature, date and approval fields are blank. REV is *not* allowlisted. The allowlist gate now also refuses unsigned stamps (`paper_pilot_stamp_unsigned`). Tests: signature rules, unsigned-stamp block, repo stamp unsigned and not allowlisted, the stamp's YAML snippet parses and expires. Suite 290 passed. | `docs/pilots/`, `os/mint_draft.py` |

---

## Needs a decision (not changed)

| # | Priority | Issue | Evidence | Options |
|---|---|---|---|---|
| D1 | ~~P0~~ | **Resolved (F10, F11).** `run` goes through the kernel, and MINT drafts are actionable only through the gate chain. | — | — |
| D2 | ~~P1~~ | **Resolved (F14).** | — | — |
| D3 | P1 | **M1–M7 / M10–M12 mostly echo labels.** Each month's flag is minted only by an `identified_*: present` hand label (e.g. `m12_topdown.classify_top_down`, `m11_mega`, `m10_confluence`, `m1_setup`). This is by design ("only input that mints the flag", `docs/MONTH1[0-2]_ESSENCE.md`), but it means those layers verify schema and isolation, not market reading. Only M8 (`m8_detect`) and M9 (`wr`, `raid`, `mss`, `box`, `pd_origin`) compute from numbers. | `os/m*_*.py` | Accept as "curriculum schema", or pick which months get detectors next. |
| D4 | ~~P2~~ | **Resolved (F15).** | — | — |
| D5 | P2 | **Handoff has no consumer.** `handoff.v1` (`kind: day_context_handoff`) is consumed nowhere in `/workspace/hermes`: no match for `day_context_handoff`, `handoff_latest`, `dayContext` or `ftn`. MINT reads `trading/dispatch/out/latest.json` from `scan_clears`. `HERMES_INTEGRATION_I0.md` Phase I slices I1d–I2 (desk `dayContext.js`, Mint read-only clearance) are not built. | — | Decide whether ftn-agent joins the monorepo (e.g. `research/` producer or `kernel/`), and wire desk I1d. |
| D6 | ~~P2~~ | **Resolved (F16).** Remaining: GBP/XAU and TF chips still have no data; `Run workflow` re-renders the snapshot (regenerate it with `ftn desk-snapshot`). | — | — |
| D7 | P3 | REV treats any `origin_pd_array` as "HTF PD at or around raid" (`models/rev.py`: `htf = ev.get("htf_pd_at_raid") or ctx.origin_pd_array`). Origin is the array price is leaving, which is not necessarily at the raid. **Left unchanged:** the blueprint (§6 "named extreme raid + (HTF PD \| NY/LC exception)") and the slice docs don't say which array counts, so there is no documented fix. Changing it would flip the gold result for `m9_reconstruction_eurusd`. | `models/rev.py` | Decide: require `htf_pd_at_raid` explicitly, or a price-overlap test between the raid and an HTF array. |
| D8 | ~~P3~~ | **Resolved (F17).** | — | — |
| D9 | P3 | Journal collisions **resolved (F13)**. Still open: `__main__.py` returns 0 for `no_trade` and `ok` is always true. | — | Minor. |
| D10 | **P0** | **The allowlist is empty, so no draft is actionable today.** This is deliberate. Adding REV (or any model) is the human step `docs/MINT_ALLOWLIST.md` describes: HERMES Wave 1 has zero SURVIVES (`hermes/trading/ALLOWLIST.md`), so the only route is a signed Path B paper-pilot stamp. The review did **not** create one; that would be the agent minting its own clearance. | `config.yaml mint_allowlist` | A human writes `docs/pilots/<MODEL>_PILOT_STAMP.md` from the template and adds the config entry. |
| D11 | P1 | **The arbiter only ever selects REV.** `os/candidates.py` never promotes CONSO/BB/PIP20 to `selected`; their best state is `unevaluated`, because their execution triggers aren't implemented. So only REV can reach a kernel ticket, and CONSO/BB/PIP20 drafts exist only in the synthetic gate tests. Blueprint §7 lists `REV > CONSO > PIP20 > BB`. | `os/candidates.py`, `models/{conso,bb,pip20}.py` | Define each model's execution confirmation, then let the arbiter select it. |
| D12 | P1 | **Stop references are `hermes_interpretation`.** REV/BB use the raided named extreme; CONSO uses the raided box edge; PIP20 uses 20 pips (blueprint §6). A labelled `evidence.stop_reference` overrides all of them. No lecture source pins the REV/BB/CONSO stop. | `os/mint_draft.py::_stop` | Sign off, or supply a lecture-cited rule per model. |
| D13 | P2 | **The paper book is a file FTN reads, not MINT's ledger.** Daily loss and drawdown come from `dispatch/out/paper_book.json` (flat if absent). Nothing writes that file yet, so the 2% and 5% gates only bite when someone mirrors MINT's P&L into it. FTN also sizes each ticket alone, not against aggregate cluster risk (GATES.md). | `os/mint_draft.py::load_book` | Have MINT export its book, or point FTN at it. |
| D14 | P2 | **Two allowlists.** FTN's `mint_allowlist` mirrors MINT's process, but MINT's real `trading/config.yaml strategy_allowlist` is separate, and MINT should re-check its own list. | — | Pick a single source of truth when FTN joins the monorepo (D5). |

Charter compliance otherwise holds: paper default, dual unlock, and `live.py` only fetches quotes behind `live_data_enabled` + `FTN_LIVE_DATA=1` and refuses orders. No secrets (`.env.example` only). The handoff omits the banned fields (BUY/SELL, confidence, rank).

---

## Behaviour changes (for the user)

### From the `run` re-route (07:35)

1. **`ftn run --fixture fixtures/sample_eurusd.json`** (the README quick start) now returns `kind: no_trade` with reason `fixture_not_m9_daycontext` and `actionable_for_mint: false`. Before, it returned an actionable `entry_candidate`. The fixture has no `date`, so the kernel can't run. The four numbers, PD overlap and setup values are still in the output.
2. **For dated Month 9 fixtures, `run` now has `brief`'s side effects.** It writes `session_*.json`, `handoff_*.json` and `mint_draft_*.json` to `dispatch/out/`. Running `run` again on the same date, symbol and session reports the **same** session ticket ID (one ticket per session), not a second one.
3. **`ticket.kind` values** are now `m9_session_ticket` | `no_trade` | `prep_only`. `run` no longer emits `entry_candidate` (in HERMES MINT that name means a research SURVIVES verdict).
4. ~~`actionable_for_mint` is always false~~. Superseded by the gate chain below.
5. **`ticket.gate_ok` is kept but always false (deprecated).** The old value is in `ticket.legacy_gate_ok`.
6. **The old filter reasons moved** (`compressed_atr`, `no_pd_array_overlap`, `setup_gate_incomplete` → `ticket.legacy_filter_reasons`). `no_trade_reasons` now holds authority reasons (`fixture_not_m9_daycontext`, `no_m9_session_ticket`, `prep_stage_only`, `non_paper_mode_refused`).
7. **New keys only, none removed:** `legacy_context`, `m9`, `ticket.authority`, `ticket.selected_module`, `ticket.session_ticket`, `ticket.mint_draft`. Exit code is still 0 and the `--out` behaviour is unchanged.
8. ~~Journal collisions~~. Fixed (F13).

### From the gate chain and the six fixes (07:42)

9. **MINT drafts can now be `actionable_for_mint: true`** (paper only) when kernel ticket, side, risk, allowlist and mode all pass. **With today's empty allowlist none are.** The 5 dated fixtures that reach a kernel ticket (all REV, side buy: `m9_raw_eurusd`, `m9_reconstruction_eurusd`, `m9_rev_inside_box`, `m9_calendar_watchlist`, `m9_calendar_idle`) pass kernel_ticket, side, risk and mode, and are `blocked_by: allowlist:not_on_mint_allowlist`. REV risk: $500 at 0.5%, stop at PDL 1.11420, ≈119k units. The other 41 dated fixtures produce **no draft**: the kernel selects nothing (`blocked_by: kernel_ticket:no_selected_candidate` in brief/desk, `run:no_m9_session_ticket` in run). That covers all the M1–M8, M10–M12, Charter, PAM1 and Model 13 fixtures, plus the M9 fixtures where REV doesn't confirm and CONSO/BB/PIP20 can't be selected (D11). With a human REV paper-pilot entry, those same 5 become actionable (tested).
10. **The draft schema grew:** `gates`, `blocked_by`, `blocked`, `actionable_reason`, `entry_reference`, `stop_reference`, `risk_pct`, `risk_usd`, `size_units`. `requires` is gone; its checks are now gates. The handoff gained `last` and `execution_context` (raid, box, `conso_raided_edge`, `stop_reference`, `pip`).
11. **`run` output:** `ticket.blocked_by` / `ticket.actionable_reason` and `m9.mint_status`. `brief` markdown gains a "MINT draft (gate chain)" section. `brief`, `run` and the desk show identical status (tested on every dated fixture).
12. **The draft `side` can now be `None`:** CONSO with no raided edge, or REV/BB/PIP20 with unclear IOF. That blocks at the side gate instead of guessing.
13. **No default bias:** a legacy fixture without `htf_bias` and no `--bias` gives no four-numbers (`four_reason: bias_undetermined`). The kernel briefing withholds the count when daytrade IOF is unclear.
14. **Config errors are now fatal:** a typo, unknown key or out-of-range cap in `config.yaml` raises `ConfigError` with the line or path. Before, it was silently ignored.
15. **File names:** dispatch files are `ftn_<YYYYmmddTHHMMSSffffffZ>-<hex8>.json` and journals are `<run_id>_DECISION.md`. `scanned_at` keeps its old format; `run_id` is new.
16. **Desk:** the chart shows the fixture's real 15m bars and its own PD arrays/ranges (`m9_raw_eurusd`, 2017-05-30), plus a MINT gate card. Regenerate with `python3 -m ftn desk-snapshot --fixture <dated fixture>`. The snapshot fingerprint format changed (sha256, F2).
17. **New CLI and env:** `ftn desk-snapshot`; `FTN_CONFIG`.

---

## Month 13 status

**Search for source on the box** (`rg` over `/workspace`, `/home/box` and `/tmp`, including `/tmp/ghchk/*` and the hermes-x investigations):
- No transcript, RAW pack or notes for `kNlySn81dmo` anywhere.
- No `MONTH13` / `PAM13` material.
- Only references found:
  - the canon URL row in `docs/CHARTER0_CANON.md`;
  - a one-line mention in `/workspace/ICT_Concept_Taxonomy_2026-09.txt` ("a Charter lecture on the later 2022 YouTube model");
  - "2022 Mentorship" rows in `research/.../HISTORIAN_DIFF_2026-09-13.md` ("still skeleton");
  - a third-party blog article in `repo-audit/ict-agent/knowledge/raw/.../complete-ict-trading-strategy-2022.md` (secondary, not used).
- `M13` matches in INV-002 `meta.json` are YouTube storyboard file names (noise).

**Source used:** the user-supplied notes `docs/review/MODEL13_SOURCE_FROM_USER.md`, which summarise kNlySn81dmo and cite the 2022 playlist. I did not watch the lecture or check these notes against it. Everything is tagged `user_supplied_lecture_notes_unsigned`.

**Terminology.** Core Content ends at M12. "Month 13" here means **Charter Model 13**, a **bridge/reference, not PAM13**. Peer status is a later decision that needs a **signed Model 13 Slice 0** (`docs/MONTH13_SLICE0_GLOSSARY.md`, signature line left blank).

**Built:**
- **`docs/MONTH13_RESEARCH_CARD.md`.** PAM1-style card: sources, framing, lecture-logic notes, glossary → fields, required vs confirming split, frozen boundary, open questions. Labelled throughout as lecture notes, not a detector spec. States that the lecture's ≤~2% risk is not an FTN cap (`config.yaml` stays 0.5%).
- **`docs/MONTH13_SLICE0_GLOSSARY.md`** (proposed, unsigned) and a `docs/SLICES.md` "Slice M13" entry.
- **The existing switch is extended, not duplicated.** `model13_bridge: present | none` already existed in `CharterState` (`os/pam_contracts.py`). It now:
  - requires an explicit literal `"present"` (`True`, `"yes"`, `"pam13"` → `none`);
  - reads from evidence as well as the charter block;
  - gains an optional sibling `CharterState.model13: Model13Card | None`.
- **`src/ftn/os/m13_contracts.py`** holds `Model13Card` (required: `direction`, `opposing_pd_objective_note`, `time_window_note`, `liquidity_raid_note`, `short_term_mss_note`, `fvg_entry_note`, `risk_frame_note`; confirming: `fvg_eq_side_note`, `ltf_refinement_note`, `target_ladder_note`, `index_timing_note`), descriptive completeness only, plus `MODEL13_REFERENCE` (citation metadata).
- **`src/ftn/os/m13_context.py`** holds `attach_model13`, `has_model13_evidence` and `model13_annotation`.
- **Wiring:**
  - DTR attaches the charter when Model 13 is labelled (`os/dtr.py`); charter recognition stays false (`no_identified_pam`).
  - `derive_charter` attaches the card after context ingest (`os/pam_recognize.py`).
  - The briefing shows the card with "not a PAM, a candidate or a ticket".
  - The handoff carries it through `asdict(charter)`.
  - The orchestrator adds `annotations.model13` only when `model13_bridge_enabled: true` (new key in `config.yaml`, **default false**). It is computed after the ticket.
- **Fixture:** `fixtures/m13_bridge_eurusd.json` (synthetic labels, no bars).
- **Still holds after F10:** `tests/test_run_authority.py::test_model13_fixture_through_run_makes_no_ticket`.
- **Tests** (`tests/test_model13.py`, 8): `pam13` is not in `PAM_IDS` and is dropped from `recognized_pams`; none by default on existing fixtures; a complete card does not mint the bridge; the bridge never sets charter recognition; no `session_`/`swing_`/`mint_draft_` files and no selected candidate; the candidate set is identical with and without Model 13 labels; the orchestrator is off by default and its ticket fields are unchanged when on; the handoff carries the bridge with empty `recognized_pams` and no ticket.

**To complete Model 13:**
1. Verify each note against kNlySn81dmo with timestamps (or add a transcript/RAW pack under hermes-x INV-001).
2. Sign Slice 0: bridge vs peer, and the required/confirming split. "FVG (ideal)" could make FVG confirming.
3. Map 2022 Mentorship episodes (base rules) vs the Charter amplification.
4. Decide whether the card may read M9's derived `raid`/`mss` evidence read-only.

---

## Intent analysis (independent)

**What it really is.** This is a *curriculum-as-code* project. The user is turning ICT's mentorship (Core Content M1–M12 plus the 34-lecture Charter, PAM1–12 + Model 13) into a typed, auditable ontology of market-reading states. The question being tested is stated outright: "can Hermes reconstruct Month-9 reasoning from a fixture without being told which model should win?" (`docs/MONTH9_BLUEPRINT.md` §13).

The product is not a signal bot. It is a **deterministic reasoning kernel** whose every field carries provenance:
- `ict_source` / `hermes_interpretation` / `hermes_governance` / `hermes_empirical` (blueprint §0.1, `Candidate.origin` in `os/contracts.py`);
- gold oracles kept physically separate from inputs (`load_day_context` rejects `expected_winner`/`pick`; `tests/test_reconstruction.py` "poisoning gold does not change engine output").

**Mental model.**
- Each month is "one process, not N bots" (`docs/MONTH5_ESSENCE.md`, `MONTH7_ESSENCE.md`, `MONTH8_ESSENCE.md`). It gets an optional `DayContext.monthN` layer that **annotates and never tickets**.
- The ladder annotation ≠ opportunity ≠ candidate ≠ ticket ≠ order is the core invariant (`docs/HERMES_INTEGRATION_I0.md`, `docs/INTEGRATION_SUITE.md` I0 1–10).
- M9 is the single execution governor (DTR kernel → frozen MarketState → REV/CONSO/BB/PIP20 → arbiter → one `session_ticket` per session). M7 OSOK is the only other paper ticket, on a weekly horizon (`os/m7_swing.py`).
- The Charter is a recognition layer that reads Core read-only and may recognise overlapping PAMs with no winner (`docs/CHARTER_ESSENCE.md`).
- Each month follows the same cadence: ESSENCE (frozen canon with video IDs) → SLICE0 glossary → SLICE1–N_SOURCE (code pasted into docs for review) → E2E briefing. This is a human-in-the-loop, sign-before-code way of working (85 `*_SOURCE.md` files). The `docs/` tree is a design-review ledger, not end-user documentation.

**Fit in HERMES-X.** The intended role is the **DayContext producer** for the monorepo:

```
ftn-agent → handoff.v1 → {HERMES Desk projection, MINT execution} → human
```

with Hermes X as investigator, not writer (`docs/HERMES_INTEGRATION_I0.md`, `docs/HERMES_X_BOUNDARY.md`, `os/x_ask.py`). MINT stays the only execution and P&L owner; the FTN draft is always `actionable_for_mint: false` and requires RISK + allowlist + human ack (`os/mint_draft.py`).

**What works:**
- The M9 kernel with real bar-derived detectors: W%R(10), named-extreme raid, MSS/displacement, compression box, origin/target PD, calendar focus, DXY relationship, session clocks (`os/{wr,raid,mss,box,pd_origin,calendar,dxy,clocks}.py`).
- M8 measurements (CBDR/Asian height, London gate; `os/m8_detect.py`).
- Governance tests, paper/live locks, and handoff field bans.

**What is aspirational:**
- M1–M7 and M10–M12 are mostly typed echoes of `identified_*` labels (D3).
- PAM2–12 have ids but no evidence contracts (only PAM1 has `pam1_evidence` / `pam1_complete`).
- No live tape: `live.py` gives quotes only, and the calendar is stubbed.
- The desk reads a static snapshot over synthetic candles (D6).
- No HERMES consumer of the handoff (D5).
- No empirical layer: `hermes_empirical` is defined but never emitted.

**Where it drifts from its own intent:**
1. The pre-OS `ftn run` path was a second ticket authority that marked fixture booleans `actionable_for_mint: true`. This was the clearest contradiction of "M9 sole authority" and "no invented SURVIVES". **Now fixed (F10).**
2. Unresolved directions were silently defaulted (bullish bias, sell side). **Fixed** (F4, F14, F15).
6. **The "harmony" chain (F11)** makes the intended architecture explicit: one ticket authority (the M9 kernel), one gate chain, one status rendered identically by brief, run and desk. Months 1–8, 10–12, the Charter and Model 13 stay context on the DayContext. Today no draft is actionable because the empty allowlist reflects the real HERMES state (zero SURVIVES), and the arbiter can only select REV (D11). The shape is right; the remaining gaps are evidence and human clearance.
3. The "fingerprint" was not reproducible (F2), and kernel state leaked across runs (F1). Both undercut the "auditable, reproducible reconstruction" premise and are now fixed.
4. Breadth has outrun depth. Twelve months plus the Charter got schemas before one month (M9) was validated on real tape, and nothing measures whether any candidate has an edge. The project's real bottleneck is evidence (real sessions plus `hermes_empirical` results), not more months. Model 13 should stay a bridge card until that exists.
5. The repo sits outside the monorepo and is only vendored as code into `ict-agent-lab` (no docs), so the design ledger and the code can diverge silently.

**Bottom line.** The user is building an ICT-literate, provenance-labelled day-context kernel. It is meant to let a human (and Hermes X) see *why* a paper setup would be considered, while hard-separating teaching, recognition, candidacy and execution. The governance and the M9 core reflect that intent well. With `run` now going through the kernel, the label-echo month layers and the unconnected handoff are where it is still a curriculum schema rather than a working research instrument.
