# H009b Pilot Results — FREE_YF_NQ
**Run date:** 2026-09-13  
**Authorization:** ORION RUN AUTHORIZATION — H009b pilot on FREE_YF_NQ only  
**Protocol:** `experiments/wave2/QUANT_H009b_NEAREST_PWPM_PROTOCOL_2026-09-13.md`  
**Tape:** `evidence/tape/FREE_YF_NQ/NQ=F_1d.csv` (prior week/month HH/LL aggregated from daily for path consistency)  
**Parents:** C-METH-022/023/025 **Passed Observed**

## Disclaimers

- **CONTINUOUS-YF:** Yahoo `NQ=F` continuous; rolls undocumented — not Mar 2026 MNQ.  
- **PARAMETER Mon-open proxy:** \(P_0\) = first daily Open of ISO week. **Not** Sunday Globex open (022). Fri-close co-reported.  
- **No Wave 1. No MERCURY.**  
- Estimand: weeks with **unique** first touch among L4 `{PWH,PWL,PMH,PML}`.

## Sample

| Pool | N |
|------|---|
| Weeks processed | 101 |
| Unique-first L4 | 53 (52.5% of processed) |
| IS 60% | 31 |
| OOS 40% | 22 |

Unique-first share vs 50% flag: OK.

## Primary — L4 nearest-side vs random foil

| Split | N | P̂(hit predicted) | 95% CI (acc) | Foil acc | Δ | 95% CI (Δ) |
|-------|---|-------------------|--------------|----------|---|------------|
| ALL | 53 | 0.6981 | [0.5660, 0.8113] | 0.2453 | 0.4528 | [0.2830, 0.6226] |
| IS | 31 | 0.6774 | [0.5161, 0.8387] | 0.1613 | 0.5161 | [0.3226, 0.7097] |
| **OOS** | **22** | **0.7273** | **[0.5455, 0.9091]** | **0.3636** | **0.3636** | **[0.0455, 0.6364]** |

Bootstrap 10_000; foil seed 20260913. Walk-forward median Δ: **0.4000**

## Sensitivity

| Check | Result |
|-------|--------|
| Fri-close \(P_0\) OOS acc | 0.6818 (Mon-open 0.7273) |
| Two-way L2 OOS (N=37) | acc=0.8919 foil=0.4865 Δ=0.4054 (sensitivity only) |

## Decision gates

| Gate | Result |
|------|--------|
| OOS N≥80 | FAIL (22) |
| Δ>0 | PASS |
| Δ CI >0 | PASS |
| WF median Δ>0 | PASS |

## Decision

**INCONCLUSIVE (N_OOS < 80)**

## Intelligence-ready TLDR

On continuous Yahoo `NQ=F` daily, ISO-week **nearest-side** among prior-week/month highs/lows at **Mon open** vs four-way random foil (unique-first weeks): OOS N=22, P̂=0.727 (foil 0.364), Δ=0.364 [0.045, 0.636], WF median Δ=0.400. **INCONCLUSIVE (N_OOS < 80)**. Not Sunday-open identity; not Wave 1 / MNQ 1m.

## Artifacts

- `H009b_unique_weeks.csv`  
- This file  

**Operator:** QUANT

## Post-pilot hygiene (ORION/CASSANDRA)

- Prior-week HH/LL source **frozen PARAMETER**: daily-aggregated ISO-week (`NQ=F_1d.csv`). `NQ=F_1wk.csv` not primary.
- Foil OOS 0.36 vs E=0.25: within ~1.2 SE at N=22 — not a confirmed RNG bug; re-check on powered re-run.
- No SURVIVES. No powered re-run until OOS N path ≥80.
