# QUANT Experiment Protocol — HERMES-X

**Owner:** QUANT  
**Pipeline:** ATLAS / MACRO / HISTORIAN / DATA → **QUANT** → CASSANDRA → RISK → MERCURY → ORION  
**Mode:** Paper only. Objective is falsification and replication, not confirmation.

## Required fields (every hypothesis)

| Field | Requirement |
|-------|-------------|
| Population | What universe (e.g. ES futures RTH, SPX cash, HY ETF) |
| Instrument | Exact symbol / contract |
| Period | Start–end dates; bar size |
| Session | RTH / ETH / event window |
| Sample | N expected; minimum N for decision |
| Entry | Exact trigger (no discretionary override) |
| Exit | Time stop / signal exit |
| Stop | Hard stop or explicit $ risk |
| Target | Take-profit or measured objective |
| Risk | Per-trade % of $100k (≤ 0.5% hard cap at RISK) |
| Benchmark | Buy-hold / random entry / same-session baseline |
| Metrics | N, win rate, avg win/loss, expectancy, PF, max DD, MAE, MFE, trade frequency |
| Dependence | Regime / session / instrument / DOW splits |
| Falsification | Pre-committed: what result kills the claim |
| Sample split | IN-SAMPLE / OUT-OF-SAMPLE / WALK-FORWARD / PAPER / LIVE labeled |

## Bias hunt (mandatory checklist)

- [ ] Look-ahead / future leak
- [ ] Data leakage (labels, features from after entry)
- [ ] Selection / survivorship
- [ ] Overfitting / multiple-testing without correction
- [ ] Unrealistic fills (mid vs ask, no slippage/spread)
- [ ] Regime dependence ignored
- [ ] Hypothesis revised after seeing results without marking NEW

## Decision labels

- **SURVIVES** — passes pre-committed metrics OOS / walk-forward
- **FAILS** — falsification criteria hit
- **INCONCLUSIVE** — underpowered (N too small) or data quality gate fails
- **NEW HYPOTHESIS** — any post-result change to rules

## Paper risk reminder

RISK hard caps: 0.5% / trade, 2% / day, 5% portfolio DD. QUANT does not size for live; MERCURY proposes, RISK gates.
