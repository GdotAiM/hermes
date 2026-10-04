# Month-9 OS — shipped slices

Frozen spec: `docs/MONTH9_BLUEPRINT.md` (v2.1)  
These are the **actual** files on disk, not planned work.

---

## Slice 1 — contracts + reconstruction fixture

**Purpose:** freeze Market State as data. No model may write back. Fixture must not name a winner.

| File | What it is |
|------|------------|
| `src/ftn/os/__init__.py` | Package exports |
| `src/ftn/os/contracts.py` | Frozen dataclasses: `DayContext`, `InstitutionalContext`, `Sentiment`, `WilliamsR`, `Probe`, `PdMatrix`, `MarketState`, `Candidate` |
| `src/ftn/os/contracts.py` → `freeze_market_state()` | Snapshot + fingerprint; `DayContext` is `@dataclass(frozen=True)` |
| `src/ftn/os/contracts.py` → `load_day_context()` | Loads JSON; **raises** if fixture contains `expected_winner` or `pick` |
| `fixtures/m9_reconstruction_eurusd.json` | Evidence-only fixture (2017-05-30 EURUSD). No winner key |
| `fixtures/m9_reconstruction_eurusd.expected.json` | Gold file kept **separate**. Engine never opens this |

What the fixture contains (inputs only):

- Sentiment bullish, W%R(10) 15m = −82
- Probe sell-side preferred **and** observed
- Sponsorship bullish; daytrade IOF bullish / qualified (`m60_countertrend`)
- DXY supportive from premium
- Profile `reversal_watch`
- Origin `D_FVG_bull`
- Evidence: PDL raid taken, `htf_pd_at_raid`, `mss: true`, `box: null`

---

## Slice 2 — DTR briefing writer

**Purpose:** print Market State as a human briefing. Still no broker path.

| File | What it is |
|------|------------|
| `src/ftn/os/briefing.py` | `render_briefing()`, `brief_from_fixture()` |
| `src/ftn/__main__.py` | `python3 -m ftn brief --fixture … --out …` |

Command:

```bash
cd ftn-agent
PYTHONPATH=src python3 -m ftn brief \
  --fixture fixtures/m9_reconstruction_eurusd.json \
  --out docs/M9_RECONSTRUCTION_BRIEFING.md
```

---

## Slice 3 — candidate logger + reconstruction markdown

**Purpose:** score eligibility from the **same frozen snapshot**. Persist selected / suppressed / invalidated / ineligible / annotate. Do not read the gold file.

| File | What it is |
|------|------------|
| `src/ftn/os/candidates.py` | `evaluate_candidates(MarketState)` |
| `docs/M9_RECONSTRUCTION_BRIEFING.md` | Generated briefing (also copied to `artifacts/M9_RECONSTRUCTION_BRIEFING.md`) |

Rules used (governance labeled):

| Module | Result on this fixture | Why |
|--------|------------------------|-----|
| REV | `selected` | named extreme raid + HTF PD + MSS |
| CONSO | `ineligible` | `box` is null |
| PIP20 | `ineligible` | profile = `reversal_watch` |
| BB | `invalidated` | named extreme + HTF array |
| FTN | `annotate` | objectives only |

Arbiter policy string on the briefing: `REV_preempts_CONSO_when_HTF_turn_confirmed` (`hermes_governance`).

---

## What is *not* a slice yet

- Deriving profile / raid / MSS from OHLC (evidence fields are still fixture-provided)
- Full REV / BB / CONSO / PIP20 model packages
- Desk Market State rail
- Live calendar / DXY feeds
- MINT order path

---

## Also on disk (pre-OS FTN agent)

| Path | Note |
|------|------|
| `docs/MONTH9_BLUEPRINT.md` | v2.1 freeze + §3.5 immutability |
| `docs/WORKFLOW.md` | Original FTN filling-the-numbers workflow |
| `src/ftn/engine/levels.py` | Existing FTN number engine |
| `src/ftn/workflow/orchestrator.py` | Existing `ftn run` paper workflow |
| `desk/` | Existing FTN desk |
| `fixtures/sample_eurusd.json` | Old FTN-only fixture (not the reconstruction case) |


---

## Reconstruction oracle (test)

| File | Role |
|------|------|
| `tests/test_reconstruction.py` | Harness **may** open `*.expected.json`. Production code may not. |
| Assertions | fixture has no winner; loader rejects `expected_winner`; candidate states match gold; **poisoning gold does not change engine output**; REV consumes MarketState fingerprint |

Run:

```bash
cd ftn-agent && PYTHONPATH=src python3 tests/test_reconstruction.py
```

---

## Slice 4 — REV (narrow)

| File | What it answers |
|------|-----------------|
| `src/ftn/models/rev.py` | Eligible? Execution confirmed? What evidence? |
| Input | `MarketState` only — not raw fixture path |
| Eligibility (`ict_source`) | named extreme raid + (HTF PD at raid or session exception) + clear daytrade IOF |
| Execution (`hermes_interpretation`) | LTF MSS / displacement |
| Output | `{candidate, eligibility, execution, evidence}` |

`evaluate_candidates()` now takes REV from this module instead of inlining it.

---

## Hermes X boundary (not implemented here)

Repo: https://github.com/GdotAiM/hermes-x

Month-9 OS is the deterministic kernel. Hermes X is the investigator around it (claims, beliefs ledger, INV-001 lectures). It should ask "why was REV selected?" and receive fingerprint + candidates + provenance + suppressed set. It must not invent Month-9 rules or write Market State.


### Slice 4 extra fixtures (negative / partial REV)

| Fixture | Expected REV | Also |
|---------|--------------|------|
| `m9_rev_no_raid.json` | ineligible | no raid taken |
| `m9_rev_unnamed_no_htf.json` | ineligible | unnamed swing, no HTF PD |
| `m9_rev_eligible_no_mss.json` | unevaluated | eligible, MSS false |
| `m9_rev_inside_box.json` | selected | CONSO suppressed (preemption) |


## Slice 5 — CONSO (narrow)

| File | Role |
|------|------|
| `src/ftn/models/conso.py` | Box + play: fade_edge (EQ), expansion_inside, breakout_use |
| `fixtures/m9_conso_fade_only.json` | Box raid of low, no named HTF turn → CONSO unevaluated, REV ineligible |
| `m9_rev_inside_box.json` | Same fade play **and** REV selected → CONSO `suppressed` not ineligible |

CONSO now competes. Suppression means it was eligible (`fade_edge` → EQ) and governance chose REV.


## Slice 6 — BB (narrow)

| File | Role |
|------|------|
| `src/ftn/models/bb.py` | side + engine offset/reacc + protraction_stage from Market State |
| `fixtures/m9_bb_offset.json` | unnamed session-swing soup, profile continuation |
| `m9_rev_no_raid.json` | BB `waiting_judas_completion` (Judas flagged, raid not taken) |

Governance: if REV is eligible, BB is `invalidated` even if BB itself formed an offset engine.


## Slice 7 — PIP20 (narrow)

| File | Role |
|------|------|
| `src/ftn/models/pip20.py` | +20 / −20 opportunity in `asia_ny_stops` or `ny_expansion` |
| `fixtures/m9_pip20_ny.json` | NY expansion raid, continuation profile, ADR remaining 34 |
| Governance | Eligible PIP20 **suppresses** eligible BB (`PIP20_stricter_offset`) |

London BB offset fixture has no PIP20 window → PIP20 ineligible, BB stays unevaluated.


## Slice B1 — FTN annotate

| File | Role |
|------|------|
| `src/ftn/models/ftn.py` | `annotate_ftn(MarketState)` via existing `engine/levels.py` |
| Briefing | New **FTN objectives** section; never an entry ticket |


## Slice B2 — session_ticket

| File | Role |
|------|------|
| `src/ftn/os/session_ticket.py` | persist/load one paper ticket per date+symbol+session |
| `dispatch/out/session_*.json` | store |
| Second `ftn brief` | same candidate log; briefing notes no second entry |

Governance only. Does not change who was selected.


## Slice C — DTR builder (first cut)

| File | Derives |
|------|---------|
| `src/ftn/os/institutional.py` | daytrade state + confidence from D/4H/60m (no monthly vote) |
| `src/ftn/os/sentiment.py` | direction / expected delivery / preferred probe; W%R(10) as input |
| `src/ftn/os/profile.py` | hermes_interpretation profile from box / named raid / window |
| `src/ftn/os/dtr.py` | `build_context()` then freeze |
| `fixtures/m9_raw_eurusd.json` | **no** `profile` or IOF `state` labels |

Not yet: calendar→pair selection, DXY relationship engine, PD lookback 20/40 from OHLC.


## Slice D — Desk Market State rail

Right rail loads `desk/js/os_state.js` from the OS snapshot.


## Slice E — Hermes X handoff

`src/ftn/os/handoff.py` → `dispatch/out/handoff_latest.json`


## Slice F1 — Williams %R from 15m bars

`src/ftn/os/wr.py` computes %R(10). Sentiment uses bars when `bars_m15` is present; typed `indicator.value` is optional.
`fixtures/m9_raw_eurusd.json` no longer ships a hand-typed WR value.


## Slice F2 — named-extreme raid from bars

`src/ftn/os/raid.py` compares 15m highs/lows to `ranges.named_extremes`.
Raw fixture no longer ships `raid.taken`. Detector marks PDL taken when a bar low prints through 1.11420.
MSS is still a labeled field (F3).


## Slice F3 — MSS / displacement from bars

`src/ftn/os/mss.py` looks after the raid bar for a close through the prior swing and a range >= 1.4× median.
Raw fixture no longer ships `mss: true`. REV execution still confirms on the derived flag.


## Slice F4 — consolidation box from compression

`src/ftn/os/box.py` uses pre-raid 15m window vs previous-day range (width ≤ 45% of PD).
Raw reversal tape: no box. Fade fixture: box derived, profile consolidation, CONSO unevaluated.


## Slice F5 — origin / target PD arrays

`src/ftn/os/pd_origin.py` picks origin as the nearest in-range array behind price in IOF direction; targets are arrays ahead.
Raw fixture no longer ships `origin_pd_array`. Detector returns `D_FVG_bull` + `PDH_liq`.


## Slice G1 — calendar focus pair

`src/ftn/os/calendar.py`: first medium/high event in London/NY KZ → focus_pair.
Else first watchlist name. Else `idle=true` (symbol fallback only for research tape).


## Slice G2 — DXY relationship

`src/ftn/os/dxy.py`: EUR/GBP/XAU bullish vs DXY bearish = supportive; same-direction = contradictory.


## Slice G3 — session clocks

`src/ftn/os/clocks.py` maps session + optional NY `clock` to protraction_stage and pip20_window.
London → gmt_0000. 08:20 → cme_0820 + ny_expansion. 19:00 → ny_midnight + asia_ny_stops.


## Slice H — Hermes X investigator (read-only)

`src/ftn/os/x_ask.py` answers why a module was selected from a handoff JSON.
Writes `docs/X_WHY_REV.md`. X may file a claim; it must not mutate DayContext.


## Slice I — MINT paper draft

`src/ftn/os/mint_draft.py` → `dispatch/drafts/ftn_draft_latest.json` (opt-in: `FTN_WRITE_MINT_DRAFT=1`)
`actionable_for_mint: false`. Requires board SURVIVES + allowlist + RISK + human ack. No broker.
Superseded by HERMES_INTEGRATION_I0: not a contract (MINT rejects it), no buy/sell
`side` — only `direction_hypothesis` (IOF label). Never written to `dispatch/out/`.


## Slice J — live DATA adapters (opt-in)

`src/ftn/adapters/live.py`
Default off. Quotes only if `live_data_enabled: true` AND `FTN_LIVE_DATA=1`.
`python3 -m ftn live-probe` shows data_allowed=false and orders refused.
Trading `live_enabled` remains false. Stub still refuses live orders.


## Slice M13 — Model 13 bridge ("Month 13") — added in 2026-10-04 review

| File | Role |
|------|------|
| `docs/MONTH13_RESEARCH_CARD.md` | Lecture-note card for Charter Model 13 (kNlySn81dmo); not a detector spec |
| `docs/MONTH13_SLICE0_GLOSSARY.md` | Proposed, unsigned glossary |
| `src/ftn/os/m13_contracts.py` | `Model13Card`, `explicit_bridge()`, reference metadata |
| `src/ftn/os/m13_context.py` | attach explicit `model13_bridge` + card to `CharterState`; orchestrator annotation |
| `fixtures/m13_bridge_eurusd.json` | synthetic labeled card |
| `tests/test_model13.py` | never a PAM, never a ticket, none by default |

Extends the existing `CharterState.model13_bridge`; no `pam13`.


## Slice R — `ftn run` routed through the Month-9 kernel (2026-10-04 decision)

| File | Role |
|------|------|
| `src/ftn/workflow/orchestrator.py` | `run` calls `brief_from_fixture`; ticket/draft are the kernel's; legacy FTN measurement = research context |
| `src/ftn/journal/write.py` | decision journal records ticket authority |
| `tests/test_run_authority.py` | legacy booleans never actionable; `run` tickets == `brief` tickets for every dated fixture; prep never calls kernel; Model 13 through `run` makes no ticket |


## Slice G — MINT gate chain + harmony (2026-10-04)

| File | Role |
|------|------|
| `src/ftn/os/mint_draft.py` | research draft: kernel_ticket → direction → risk → allowlist → mode → contract (I0: never actionable); `blocked_by` |
| `src/ftn/os/briefing.py` | `draft_status()` — the single research-draft status shown by `ftn brief` |
| `src/ftn/config_load.py` | strict YAML-subset parser + schema (`ConfigError`), `mint_allowlist`, `FTN_CONFIG` |
| `docs/MINT_ALLOWLIST.md` | how the allowlist is populated; empty today |
| `tests/test_gate_chain.py` | every gate passing/blocked; run == brief == desk on all dated fixtures |
