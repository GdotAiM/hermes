# Tape stream — KAGGLE_NQ_1M_2022_2025

| Field | Value |
|-------|--------|
| SOURCE | Kaggle `tgtanalytics/nq-futures-1min-bar-2022-2025` (user-uploaded zip) |
| FILE | `Dataset_NQ_1min_2022_2025.csv` (~70MB, 1,048,575 rows) |
| TIMEZONE | `timestamp ET` — America/New_York wall clock |
| GRANULARITY | 1-minute OHLCV (+ Vwap_RTH, Vwap_ETH undocumented) |
| DATE RANGE | 2022-12-26 18:01 ET → 2025-12-11 20:52 ET (**no 2026**) |
| INSTRUMENT | NQ continuous — roll **undocumented** |
| STREAM LABEL | `CONTINUOUS-KAGGLE-NQ1M` |
| LICENSE | Kaggle CC0 claim — research only; not CME redistribution |

## DATA gate — FORMAL
**PASS WITH CONDITIONS** — `DATA_GATE_KAGGLE_NQ_1M_2026-09-13.md`  
(alias `DATA_GATE_KAGGLE_NQ1M_2026-09-13.md`)

### H001b Pref / Popen locks (this stream)
- **Pref \(P_{ref}\):** close of **16:14 ET** 1m bar on prior normal RTH session  
- **Popen \(P_{open}\):** **open** of **09:30 ET** 1m bar  
- **Early-close / holiday prior session:** exclude day from H001b primary; report \(N_{excl}\)  
- **Missing 16:14 or 09:30:** exclude day  

### Integrity (DATA)
0 dup · 0 mono · 0 OHLC · no 2026 · n=1,048,575 (possible Excel-cap truncation)

### Not for
Lecture-day 2026 · MNQ Mar 2026 · stream C substitution without re-label
