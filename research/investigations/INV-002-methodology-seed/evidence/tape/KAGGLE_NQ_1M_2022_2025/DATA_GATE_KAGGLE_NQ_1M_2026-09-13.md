# DATA GATE — KAGGLE_NQ_1M_2022_2025
**Gate ID:** DATA_GATE_KAGGLE_NQ_1M_2026-09-13  
**Also named:** `DATA_GATE_KAGGLE_NQ1M_2026-09-13.md` (symlink)  
**Stream path:** `investigations/INV-002-methodology-seed/evidence/tape/KAGGLE_NQ_1M_2022_2025/`  
**Stream label (required in every result memo):** `CONTINUOUS-KAGGLE-NQ1M`  
**Owner:** DATA  
**Date:** 2026-09-13  
**Verdict:** **PASS WITH CONDITIONS** (formal — not proposed)  
**ORION auth:** H001b / H003c exploratory on this stream after this gate

## Scope
| Allowed | Forbidden |
|---------|-----------|
| Wave 1 **exploratory** H001b / H003c / H002 / H004 on **pre-2026** 1m bars | Lecture-day / Mar–Aug **2026** identity |
| Pref/Popen locks below for H001b on this continuous NQ 1m | Treating results as **MNQ Mar 2026** / stream C |
| Coverage projections & OOS on 2023–2025 | SURVIVES without `CONTINUOUS-KAGGLE-NQ1M` + roll-undocumented label |

## Registry
| Field | Value |
|-------|--------|
| SOURCE | Kaggle `tgtanalytics/nq-futures-1min-bar-2022-2025` → `Dataset_NQ_1min_2022_2025.csv` |
| TIMEZONE | `timestamp ET` = **America/New_York** wall clock (naive ET) |
| GRANULARITY | **1-minute** OHLCV (+ undocumented `Vwap_RTH` / `Vwap_ETH` — not primary) |
| DATE RANGE | 2022-12-26 18:01 → 2025-12-11 20:52 ET · **no 2026** |
| INSTRUMENT | **NQ continuous** · roll **undocumented** · label `CONTINUOUS-KAGGLE-NQ1M` |
| INTEGRITY | n=1,048,575 · 0 dup · 0 mono (parsed) · 0 OHLC · possible Excel-row truncation |

## H001b open locks (DATA freeze on this stream)

### \(P_{ref}\) — Pref @ **16:14 ET**
| Case | Policy |
|------|--------|
| Normal prior RTH | \(P_{ref}\) = **close of the 16:14 ET** 1m bar (ICT “4:14 p.m. final print”) |
| Missing 16:14 bar | **Exclude** day \(D\) from primary; count in coverage |
| Prior session early-close / holiday | **Exclude** day \(D\) from primary (no reliable 16:14 RTH analogue). PARAMETER alt only with ORION ack + separate one-pager |
| Spot-check | 20 random weekdays: all had both 16:14 and 09:30. Full weekday rates ≈ 16:14 **735/772**, 09:30 **765/772** — exclusions real; report counts |

### \(P_{open}\) — Popen @ **09:30 ET**
| Case | Policy |
|------|--------|
| Primary | **Open of the 09:30 ET** 1m bar |
| Sensitivity (co-report) | First trade in 09:30 minute if vendor ever distinguishes (this CSV = bar open only) |
| Missing 09:30 bar | Exclude day; count in coverage |
| ASR 9:00 | **Rejected** (C-METH-008) — never use 09:00 as RTH open on this gate |

### Early-close / holiday policy
1. Build exclusion set from CME equity-index early closes + US market holidays intersecting the sample (2022-12 → 2025-12).  
2. If prior calendar session is holiday/early-close → exclude \(D\) from H001b primary.  
3. Report \(N_{excl}\) and list in coverage appendix.  
4. Do **not** invent a “last RTH minute” substitute in primary.

## Conditions (hard)
1. Stamp **`CONTINUOUS-KAGGLE-NQ1M`** + **roll undocumented** on every decision memo.  
2. No 2026 lecture-day claims.  
3. Not stream C / not MNQ Mar 2026.  
4. H001b must implement Pref 16:14 / Popen 09:30 locks above.  
5. H003c may run exploratory under same stream label; still ETH needed for 07:00–09:00.  
6. VWAP columns not primary until construction documented.  
7. Extend event calendar for 2023–2025 before event-stratified OOS (INV-001 file is 2026-only).

## Verdict
**PASS WITH CONDITIONS** — QUANT may run H001b/H003c **exploratory** on this disk path. LEDGER: formal gate **filed**.
