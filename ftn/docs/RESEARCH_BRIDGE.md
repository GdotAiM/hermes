# FTN research bridge: month layers → hypotheses → exploratory scorer

**Status:** EXPLORATORY. Every output is pending CASSANDRA + DATA review. Nothing here
trades, routes or edits an allowlist.

## One ticket authority

```
Months 1–8, 10–12, Model 13  ──(context + typed Hypothesis records, never tickets)──┐
                                                                                    ▼
1m bars → bar-derived DayContext → Month 9 kernel (sole ticket authority) → session ticket
        → research-draft gate chain (kernel_ticket → direction → risk → allowlist → mode → contract) → draft
        → ftn score: R outcome, conditional comparisons, foil → research/
        → MINT read-only consumer (trading/src/mint/dispatch/ftn_gate.py)
```

## Pieces

| Piece | File | Notes |
|---|---|---|
| Hypothesis records | `src/ftn/research/hypotheses.py` | 13 claims, at least one per context month (M1–M8, M10–M12, M13). Fields: id, source month and slice, lecture, claim, metric, conditioning variable, expected direction, claim provenance (`ict_source` / `user_lecture_notes`), operationalisation (always `hermes_interpretation`). `python3 -m ftn hypotheses` prints them. |
| Bar-derived DayContext | `src/ftn/research/daycontext.py` | Causal: only bars before `t`. Interpretations listed under D16. |
| Kernel ticket log | `src/ftn/research/kernel_log.py` | London 02:00–05:00 and NY AM 07:00–10:00, evaluated at each 15m close. First selection per session = ticket. Ticket attached in memory exactly as `ftn brief` does; nothing persisted. |
| Outcome | `src/ftn/research/outcomes.py` | Stop = draft stop_reference; tradeable = every gate passes except the empty allowlist and the I0 contract gate; 2R target; 16:00 time exit; stop-first on ambiguous bars; costs 0.8 / 0.5 pt per side (US100 / US500). |
| Features | `src/ftn/research/features.py` | One bar formula per hypothesis. |
| Stats | `src/ftn/research/stats.py` | Percentile bootstrap (10,000, seed 20261004), one-sided permutation p, Holm over the family, random-entry foil. |
| Scorer | `src/ftn/research/score.py` / `python3 -m ftn score` | Writes the prereg-format family JSON, ticket/trade CSVs, a score JSON, and an INTELLIGENCE SUMMARY in house style. |
| Interpretation triggers | `src/ftn/models/triggers.py` | CONSO / BB / PIP20; `config.yaml interpretation_triggers.*` all **false** by default (D15). |
| MINT consumer | `trading/src/mint/dispatch/ftn_gate.py` | Strictly read-only and log-only: reads the opt-in research draft `ftn/dispatch/drafts/ftn_draft_latest.json`, flags inconsistencies (claims actionable, carries a side, contract gate not failing, gate order, blocked_by), and always returns `mint_decision: log_only`. It can never produce an `entry_candidate`. `scan_clears` embeds it as `ftn_gate_chain`. The DayContext itself is read by main's `mint.dispatch.ftn_context`. |

## Post-H015b fixes (branch `ftn/demo-fixes`; NOT part of H015b)

* **Cost model:** `correct_side` is the default (bid/ask fills + DATA slippage floors; CASSANDRA: binding for any H016).
  It needs `--asks-us100/--asks-us500`. `--cost-model flat` gives the legacy 0.8 / 0.5 pt per side, which is also
  reported as `*_flatcost` next to the default.
* **Book:** `--book flat` (default; every ticket gated against a flat book), `running` or `both` (`*_runningbook`:
  the 2% daily / 5% drawdown caps bind; reset rule `risk_caps.drawdown_reset`, a human decision).
* Month 8 units, REV min stop / buffer and the calendar: see `docs/POST_H015B_DEMO_FIXES.md` and `docs/BAR_DATA_LAYERS.md`.

## Run

```bash
cd ftn
PYTHONPATH=src python3 -m ftn hypotheses
PYTHONPATH=src python3 -m ftn score --asof 2026-10-04           # ~1 min; writes into ../research
PYTHONPATH=src python3 -m ftn score --no-write --bars-us100 PATH --bars-us500 PATH --cost-model flat
PYTHONPATH=src python3 -m ftn score --bars-us100 BID --bars-us500 BID --asks-us100 ASK --asks-us500 ASK --book both
```

The default bars are `/workspace/ict-blueprint/research/model-u-longrun/data/US{100,500}_1m.csv.gz`
(Dukascopy BID 1m, NY offsets; 2025-08-25 → 2026-09-25). They are **not** committed here,
and this tape is **burned** (H013/H014).
