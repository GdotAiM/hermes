# Post-H015b demo fixes (branch `ftn/demo-fixes`): NOT part of H015b

> **EXPLORATORY.** These changes come from the 2026-10-04 FTN end-to-end demo (burned window 2025-08-25 → 2026-09-25).
> They change files pinned by H015b (`prereg-H015b`, `harness-H015b-v2`), so **the H015b harness refuses to run on this
> branch** (`harness_hash_mismatch`, by design). H015b continues unchanged on `forward/h015-harness`.
> **Any test of the fixed REV needs a new prereg ID (e.g. H016)**, written before looking at untouched/forward data.
> CASSANDRA: correct-side bid/ask fills are BINDING for any H016. They are the scorer's default here; flat cost is the comparison.

| # | Fix | Where | Rule (one rule, not swept) |
|---|---|---|---|
| 1 | Month 8 ranges in instrument units | `os/instruments.py`, `os/m8_detect.py`, `os/m8_contracts.py`, `os/m8_project.py`, `os/m8_profile.py` | `pip` per instrument (FX 0.0001 / JPY 0.01 / XAU 0.1; US100/US500 1 index point). ICT's FX thresholds (CBDR ideal < 40, wide ≥ 50; Asian poor > 40) are scaled for indices by the ratio of median daily range to EURUSD's (burned window: EURUSD 61.5 pips, US100 414.7 pt → ×6.74 → ideal < 269.7, wide ≥ 337.2; US500 74.9 pt → ×1.22 → < 48.7 / ≥ 60.9). Index thresholds are labelled `hermes_interpretation`; FX is unchanged (`ict_source`). |
| 2 | Minimum stop distance | `os/instruments.py` (`min_risk`), `os/mint_draft.py::risk_gate` → `risk:stop_below_min_risk` | min risk = 4 × round-trip friction (assumed spread + 2 × stop/market slippage floor), i.e. friction ≤ 25% of 1R. US100 4 × (1.55 + 1.0) = **10.2 pt**; US500 4 × (0.72 + 0.5) = **4.88 pt**. FX: none (reconstruction fixtures unchanged). |
| 3 | REV stop buffer ≥ spread + slippage | `os/instruments.py::rev_stop_buffer`, `os/mint_draft.py::_stop` | Short (stopped on the ASK): max(1 pt, max(measured spread at signal, assumed spread) + stop slippage) → US100 ≥ 2.05 pt, US500 ≥ 1.0 pt (0.97 rounds up to the 1-pt floor). Long (stopped on the BID, the chart the raid low printed on): max(1 pt, stop slippage) = 1 pt. FX keeps the D22 1-pip buffer. Assumed spread = DATA's 2026 off-RTH p90 (US100 1.55, US500 0.72; the killzones are mostly before 09:30). |
| 4 | Risk-gate realism | `research/book.py` (`RunningBook`), `research/kernel_log.py`, `research/score.py`, `config.yaml risk_caps.drawdown_reset` | `ftn score --book running|both` replays a running paper book: 0.5% of equity per trade, P&L realised at exit, and the 2% daily and 5% drawdown caps bind. `--book flat` (default) keeps the H015b behaviour for comparison. **Drawdown reset (HUMAN DECISION, proposed `next_calendar_month`)**: once the 5% cap blocks a ticket, the book stays halted for the rest of that calendar month, then the high-water mark resets to current equity, standing in for a month-end human review. `none` = never reset. |
| 5 | Empty month layers | `research/events.py` + `research/data/us_macro_events.csv`, `research/daycontext.py` | FOMC/CPI/NFP schedule (from `/workspace/marketdata calendar("events")`) attached to every bar-derived day → Month 8 London gate `news`, calendar focus source. DXY: no series on the box → stays `unavailable`. See `BAR_DATA_LAYERS.md`. |
| — | Cost model | `research/outcomes.py::simulate_both`, `ftn score --cost-model correct_side` (default) `--asks-us100/--asks-us500` | Buys fill on ASK, sells on BID. DATA slippage floors (US100 0.50 stop/market, 0.25 limit; US500 0.25/0.10). Shorts are stopped on the ask high; limits must trade through. The `*_flatcost` stream = legacy 0.8/0.5 pt per side. |

REV trading against the candle-colour IOF is **by design** (REV fades the raid; a PDH raid usually happens on a bullish-coloured day).
On the burned window 169/185 US100 and 151/167 US500 REV tickets oppose the IOF. Left unchanged.

**Caveat on fix 2:** the friction rule is not swept, but it was motivated by the demo's observation (on this same burned tape) that
sub-5-pt stops lose. Its in-sample improvement is therefore not evidence. Only an H016 on untouched/forward data can test it.
