# H009b Powered Re-run — Kaggle daily aggregate
**Run date:** 2026-09-13  
**Authorization:** ORION RUN AUTHORIZATION — H009b powered re-run on Kaggle daily aggregate  
**Protocol:** `QUANT_H009b_NEAREST_PWPM_PROTOCOL_2026-09-13.md` §0e freeze  
**Parents:** C-METH-022/023/025 Passed Observed (nearest-side)

## Labels (mandatory)

`CONTINUOUS-KAGGLE-NQ1M` · **daily-agg from 1m** · roll undocumented · **Excel truncation to 2025-12-11** · not MNQ Mar 2026 · no lecture-day identity  
**No MERCURY. No Yahoo 1wk.csv.**

## Aggregation policy (PARAMETER — frozen)

| Lock | Value |
|------|--------|
| **Primary daily OHLC** | **Full ET calendar day** — all 1m bars with that ET date |
| Sensitivity | RTH-only [09:30, 16:00] ET inclusive — co-report only |
| Prior-week HH/LL | Daily-aggregated **ISO-week** max High / min Low (§0e freeze) |
| Prior-month HH/LL | Prior calendar month from same daily series |
| \(P_0\) | **PARAMETER Mon-open proxy** = first ISO-week day with 09:30 ET bar **open** (else first day open). Not Sunday Globex open |
| Bull/bear opposite | Rival only — not primary |

## Pre-registered split

| Split | Rule |
|-------|------|
| IS | unique-first weeks with `week_start` ≤ **2024-06-30** |
| OOS | `week_start` > **2024-06-30** |

## Sample

| Pool | N |
|------|---|
| Daily bars (full ET) | 923 (2022-12-26 → 2025-12-11) |
| Weeks processed | 154 |
| Unique-first L4 | 82 (53.2%) |
| IS | 44 |
| **OOS** | **38** |

## Primary — L4 nearest-side vs 4-way random foil

| Split | N | P̂(hit predicted) | 95% CI (acc) | Foil acc | Δ | 95% CI (Δ) |
|-------|---|-------------------|--------------|----------|---|------------|
| ALL | 82 | 0.6829 | [0.5854, 0.7805] | 0.2805 | 0.4024 | [0.2683, 0.5366] |
| IS ≤2024-06-30 | 44 | 0.6364 | [0.5000, 0.7727] | 0.3409 | 0.2955 | [0.0909, 0.5000] |
| **OOS >2024-06-30** | **38** | **0.7368** | **[0.6053, 0.8684]** | **0.2105** | **0.5263** | **[0.3684, 0.6842]** |

Bootstrap 10_000; foil seed 20260913. Walk-forward median Δ: **0.5667**

### Foil audit vs E=0.25

| Split | Foil acc | vs 0.25 |
|-------|----------|---------|
| IS | 0.3409 | +0.0909 |
| OOS | 0.2105 | -0.0395 |

## Sensitivity

| Check | Result |
|-------|--------|
| Fri-close \(P_0\) OOS acc | 0.7632 (Mon-open 0.7368) |
| RTH-agg OOS (N=41) | acc=0.7073 foil=0.2927 Δ=0.4146 CI=(0.21951219512195125, 0.5853658536585367) |

## Decision gates

| Gate | Result |
|------|--------|
| OOS N≥80 | FAIL (38) |
| Δ>0 | PASS |
| Δ CI entirely >0 | PASS |
| WF median Δ>0 | PASS |

## Decision

**INCONCLUSIVE (N_OOS < 80)**

## Intelligence-ready TLDR

Kaggle 1m → full-ET daily agg, ISO-week nearest-side L4 at Mon 09:30 open vs 4-way random foil. Pre-reg OOS after 2024-06-30: N=38, P̂=0.737, foil=0.211, Δ=0.526 [0.368, 0.684]. **INCONCLUSIVE (N_OOS < 80)**. Not Sunday-open identity; not Yahoo weekly file.

## Artifacts

- `H009b_KAGGLE_daily_agg_FULL_ET.csv` — daily OHLC cache  
- `H009b_KAGGLE_unique_weeks.csv` — unique-first weeks  
- This file  

**Operator:** QUANT

## Canonical tape aggregates (ORION/DATA)

Run used equivalent full-ET calendar-day aggregation (QUANT scratch matched ORION daily OHLC exactly on all 923 days). Prefer citing:

- `evidence/tape/KAGGLE_NQ_1M_2022_2025/NQ_daily_agg_from_1m_ET.csv`
- `evidence/tape/KAGGLE_NQ_1M_2022_2025/NQ_isoweek_agg_from_1m_ET.csv`
- `DAILY_AGG_NOTE.md` (full ET day = PARAMETER)

Decision unchanged: **INCONCLUSIVE** (OOS N=38 < 80).
