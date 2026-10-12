# Screening batch 2: Model U v1 (H013) and MMXM v1–v5 (incl. v5 A = H014)

> **Provenance (added 2026-10-05, label only, per `PROTOCOL_DATA_CONDITIONS.md`):** design=in-sample-screening · data=dukascopy-screening-2023-20260925 (Dukascopy BID/ASK, DEUIDXEUR/USA30IDXUSD/XAUUSD) · screening-manifest content hash: pending (R1) · qc_gate=not_run · slip=provisional · session=cfd · n_instruments=3. Not confirmatory; no certified-untouched claim.

> **Screening, not evidence.** The protocol is `PROTOCOL.md` v1 + `PROTOCOL_BATCH2.md`, committed and pushed in `0a3b052` before any batch 2 run.
> The burned window is burned, and every candidate was developed on it. The H017 holdout was not read.

Costs: primary = pinned/declared friction F as a round trip (US100 2.55, US500 1.22, GER40 4.392, US30 5.720, XAUUSD 1.402 points). Frozen-cost burned numbers are co-reported. Holm runs across the 6 candidates at α_screen = 0.10 for S1 and S3.

## D1 Model U v1 (H013)

| set | N | mean R | 95% CI | win | total R |
|---|---:|---:|---|---:|---:|
| burned US100 (primary cost) | 256 | +0.185 | [-0.072, +0.460] | 0.37 | +47.3 |
| burned US100 (frozen cost) | 256 | +0.219 | [-0.038, +0.493] | 0.37 | +56.0 |
| burned US100 primary (disclosure) | 256 | +0.185 | [-0.072, +0.460] | 0.37 | +47.3 |
| burned US500 primary (disclosure) | 259 | -0.247 | [-0.438, -0.051] | 0.32 | -64.1 |
| S1 pooled | 2691 | -0.268 | [-0.332, -0.205] | 0.33 | -721.8 |
| S1 GER40 | 900 | -0.229 | [-0.338, -0.118] | 0.33 | -205.9 |
| S1 US30 | 893 | -0.291 | [-0.394, -0.181] | 0.30 | -260.2 |
| S1 XAUUSD | 898 | -0.285 | [-0.399, -0.167] | 0.36 | -255.7 |

- **S1 FAIL**: one-sided p = 1.0000, Holm = 1.0000; majority of instruments positive: False.
- **S2 FAIL**: burned folds positive 4/4 (n=61 +0.106, n=62 +0.384, n=67 +0.160, n=66 +0.095); S1 year folds positive 0/4 (2023 n=718 -0.364, 2024 n=726 -0.351, 2025 n=718 -0.218, 2026 n=529 -0.093).
- **S3 FAIL**: shuffled-day p = 0.275 (null mean +0.160, ~253 trades/rep); random-walk p = 0.039 (null mean -0.077, ~263 trades/rep); max 0.275, Holm 1.000.
- **Holdout power** (US100): era mean +0.139 (×2.0: +0.094); μ_plan -0.134; σ 2.176; deff 1.01; projected N 945; **power 0.025**, ceiling 0.163, unshrunk 0.500.
- **Gate: does NOT qualify**.

## D2 MMXM v1 default

| set | N | mean R | 95% CI | win | total R |
|---|---:|---:|---|---:|---:|
| burned US100+US500 (primary cost) | 0 | — | [—, —] | — | — |
| burned US100+US500 (frozen cost) | 0 | — | [—, —] | — | — |
| burned US100 primary (disclosure) | 0 | — | [—, —] | — | — |
| burned US500 primary (disclosure) | 0 | — | [—, —] | — | — |
| S1 pooled | 0 | — | [—, —] | — | — |
| S1 GER40 | 0 | — | [—, —] | — | — |
| S1 US30 | 0 | — | [—, —] | — | — |
| S1 XAUUSD | 0 | — | [—, —] | — | — |

- **S1 FAIL**: one-sided p = 1.0000, Holm = 1.0000; majority of instruments positive: False.
- **S2 FAIL**: burned folds positive 0/4 (n=0 —, n=0 —, n=0 —, n=0 —); S1 year folds positive 0/4 (2023 n=0 —, 2024 n=0 —, 2025 n=0 —, 2026 n=0 —).
- **S3 FAIL**: shuffled-day p = 1.000 (null mean -0.868, ~0 trades/rep); random-walk p = 1.000 (null mean —, ~0 trades/rep); max 1.000, Holm 1.000.
- **Holdout power** (US100+US500): era mean — (×2.0: —); μ_plan —; σ 0.000; deff 1.00; projected N 0; **power —**, ceiling —, unshrunk —.
- **Gate: does NOT qualify**.

## D3 MMXM v2 selected

| set | N | mean R | 95% CI | win | total R |
|---|---:|---:|---|---:|---:|
| burned US100+US500 (primary cost) | 40 | -0.184 | [-0.458, +0.107] | 0.40 | -7.3 |
| burned US100+US500 (frozen cost) | 40 | -0.128 | [-0.404, +0.165] | 0.40 | -5.1 |
| burned US100 primary (disclosure) | 20 | -0.324 | [-0.623, -0.020] | 0.35 | -6.5 |
| burned US500 primary (disclosure) | 20 | -0.043 | [-0.457, +0.403] | 0.45 | -0.9 |
| S1 pooled | 136 | -0.151 | [-0.307, +0.007] | 0.48 | -20.5 |
| S1 GER40 | 43 | +0.134 | [-0.151, +0.440] | 0.56 | +5.7 |
| S1 US30 | 55 | -0.096 | [-0.313, +0.127] | 0.56 | -5.3 |
| S1 XAUUSD | 38 | -0.552 | [-0.854, -0.237] | 0.26 | -21.0 |

- **S1 FAIL**: one-sided p = 0.9687, Holm = 1.0000; majority of instruments positive: False.
- **S2 FAIL**: burned folds positive 1/4 (n=15 -0.319, n=8 -0.177, n=11 +0.110, n=6 -0.390); S1 year folds positive 1/4 (2023 n=34 -0.532, 2024 n=38 -0.035, 2025 n=30 -0.297, 2026 n=34 +0.231).
- **S3 FAIL**: shuffled-day p = 0.039 (null mean -0.364, ~32 trades/rep); random-walk p = 0.784 (null mean -0.086, ~39 trades/rep); max 0.784, Holm 1.000.
- **Holdout power** (US100+US500): era mean -0.230 (×2.0: -0.276); μ_plan -0.115; σ 0.862; deff 1.10; projected N 192; **power 0.025**, ceiling 0.025, unshrunk 0.025.
- **Gate: does NOT qualify**.

## D4 MMXM v3 selected

| set | N | mean R | 95% CI | win | total R |
|---|---:|---:|---|---:|---:|
| burned US100+US500 (primary cost) | 29 | -0.063 | [-0.387, +0.296] | 0.45 | -1.8 |
| burned US100+US500 (frozen cost) | 29 | -0.018 | [-0.346, +0.349] | 0.45 | -0.5 |
| burned US100 primary (disclosure) | 16 | -0.115 | [-0.477, +0.257] | 0.44 | -1.8 |
| burned US500 primary (disclosure) | 13 | +0.002 | [-0.538, +0.623] | 0.46 | +0.0 |
| S1 pooled | 86 | -0.346 | [-0.519, -0.172] | 0.40 | -29.8 |
| S1 GER40 | 29 | -0.172 | [-0.506, +0.184] | 0.48 | -5.0 |
| S1 US30 | 35 | -0.333 | [-0.558, -0.101] | 0.43 | -11.7 |
| S1 XAUUSD | 22 | -0.597 | [-0.943, -0.261] | 0.23 | -13.1 |

- **S1 FAIL**: one-sided p = 0.9999, Holm = 1.0000; majority of instruments positive: False.
- **S2 FAIL**: burned folds positive 1/4 (n=11 +0.100, n=7 -0.464, n=6 -0.196, n=5 +0.302); S1 year folds positive 0/4 (2023 n=23 -0.454, 2024 n=23 -0.341, 2025 n=24 -0.280, 2026 n=16 -0.297).
- **S3 FAIL**: shuffled-day p = 0.039 (null mean -0.296, ~25 trades/rep); random-walk p = 0.412 (null mean -0.112, ~25 trades/rep); max 0.412, Holm 1.000.
- **Holdout power** (US100+US500): era mean -0.099 (×2.0: -0.135); μ_plan -0.173; σ 0.918; deff 1.02; projected N 136; **power 0.025**, ceiling 0.025, unshrunk 0.025.
- **Gate: does NOT qualify**.

## D5 MMXM v4 selected

| set | N | mean R | 95% CI | win | total R |
|---|---:|---:|---|---:|---:|
| burned US100+US500 (primary cost) | 32 | -0.024 | [-0.338, +0.298] | 0.50 | -0.8 |
| burned US100+US500 (frozen cost) | 32 | +0.025 | [-0.294, +0.355] | 0.50 | +0.8 |
| burned US100 primary (disclosure) | 15 | -0.201 | [-0.576, +0.160] | 0.47 | -3.0 |
| burned US500 primary (disclosure) | 17 | +0.133 | [-0.306, +0.610] | 0.53 | +2.3 |
| S1 pooled | 123 | -0.132 | [-0.301, +0.039] | 0.48 | -16.2 |
| S1 GER40 | 40 | +0.181 | [-0.112, +0.490] | 0.57 | +7.2 |
| S1 US30 | 48 | -0.103 | [-0.352, +0.147] | 0.56 | -5.0 |
| S1 XAUUSD | 35 | -0.530 | [-0.842, -0.213] | 0.26 | -18.5 |

- **S1 FAIL**: one-sided p = 0.9341, Holm = 1.0000; majority of instruments positive: False.
- **S2 FAIL**: burned folds positive 0/4 (n=11 -0.044, n=7 -0.194, n=9 +0.267, n=5 -0.265); S1 year folds positive 1/4 (2023 n=30 -0.489, 2024 n=35 -0.024, 2025 n=29 -0.293, 2026 n=29 +0.267).
- **S3 FAIL**: shuffled-day p = 0.118 (null mean -0.175, ~24 trades/rep); random-walk p = 0.333 (null mean -0.097, ~35 trades/rep); max 0.333, Holm 1.000.
- **Holdout power** (US100+US500): era mean -0.063 (×2.0: -0.103); μ_plan -0.066; σ 0.866; deff 1.10; projected N 156; **power 0.025**, ceiling 0.025, unshrunk 0.025.
- **Gate: does NOT qualify**.

## D6 MMXM v5 A (H014)

| set | N | mean R | 95% CI | win | total R |
|---|---:|---:|---|---:|---:|
| burned US100+US500 (primary cost) | 46 | +0.197 | [-0.049, +0.451] | 0.65 | +9.1 |
| burned US100+US500 (frozen cost) | 46 | +0.241 | [-0.006, +0.501] | 0.65 | +11.1 |
| burned US100 primary (disclosure) | 21 | +0.085 | [-0.220, +0.384] | 0.57 | +1.8 |
| burned US500 primary (disclosure) | 25 | +0.291 | [-0.038, +0.630] | 0.72 | +7.3 |
| S1 pooled | 164 | -0.115 | [-0.244, +0.014] | 0.48 | -18.8 |
| S1 GER40 | 58 | -0.035 | [-0.238, +0.177] | 0.48 | -2.0 |
| S1 US30 | 61 | -0.093 | [-0.280, +0.088] | 0.52 | -5.7 |
| S1 XAUUSD | 45 | -0.247 | [-0.511, +0.023] | 0.40 | -11.1 |

- **S1 FAIL**: one-sided p = 0.9595, Holm = 1.0000; majority of instruments positive: False.
- **S2 FAIL**: burned folds positive 2/4 (n=11 +0.175, n=13 -0.053, n=16 +0.607, n=6 -0.316); S1 year folds positive 0/4 (2023 n=43 -0.230, 2024 n=45 -0.044, 2025 n=38 -0.126, 2026 n=38 -0.056).
- **S3 FAIL**: shuffled-day p = 0.314 (null mean +0.164, ~41 trades/rep); random-walk p = 0.020 (null mean -0.062, ~41 trades/rep); max 0.314, Holm 1.000.
- **Holdout power** (US100+US500): era mean +0.161 (×2.0: +0.124); μ_plan -0.057; σ 0.787; deff 1.18; projected N 226; **power 0.025**, ceiling 0.292, unshrunk 0.806.
- **Gate: does NOT qualify**.

## Summary

| candidate | burned N | burned mean R [CI] | S1 N | S1 mean R [CI] | S1 | S2 | S3 | holdout power | power ceiling | qualifies |
|---|---:|---|---:|---|---|---|---|---:|---:|---|
| D1 Model U v1 (H013) | 256 | +0.185 [-0.072, +0.460] | 2691 | -0.268 [-0.332, -0.205] | FAIL | FAIL | FAIL | 0.025 | 0.163 | no |
| D2 MMXM v1 default | 0 | — [—, —] | 0 | — [—, —] | FAIL | FAIL | FAIL | — | — | no |
| D3 MMXM v2 selected | 40 | -0.184 [-0.458, +0.107] | 136 | -0.151 [-0.307, +0.007] | FAIL | FAIL | FAIL | 0.025 | 0.025 | no |
| D4 MMXM v3 selected | 29 | -0.063 [-0.387, +0.296] | 86 | -0.346 [-0.519, -0.172] | FAIL | FAIL | FAIL | 0.025 | 0.025 | no |
| D5 MMXM v4 selected | 32 | -0.024 [-0.338, +0.298] | 123 | -0.132 [-0.301, +0.039] | FAIL | FAIL | FAIL | 0.025 | 0.025 | no |
| D6 MMXM v5 A (H014) | 46 | +0.197 [-0.049, +0.451] | 164 | -0.115 [-0.244, +0.014] | FAIL | FAIL | FAIL | 0.025 | 0.292 | no |

Power ceiling = gate power if S1 ≥ burned era mean (μ_plan = 0.5 × burned era mean). It is a derived bound, not a protocol change.

## Reading (screening caveats)

- **No candidate qualifies.** All six fail S1, S2 and S3, and the gate power is ≤ 0.025 for every candidate with trades because μ_plan ≤ 0 (the S1 mean is negative for every one).
- **D1 Model U v1:** positive on burned US100 (+0.185R at primary cost; +0.219R at frozen cost), with 4 of 4 burned folds positive. It loses on all three new instruments in every year 2023–2026 (pooled −0.268R, CI excludes 0). The shuffled-day null averages +0.160R, close to the real mean (p = 0.275), so the burned edge is not distinguishable from what the rule earns on day-shuffled US100 paths. The random-walk null is negative (p = 0.039). Burned US500 (disclosure) is −0.247R/trade.
- **D6 MMXM v5 A:** burned +0.197R on 46 trades (frozen cost +0.241R). S1 is −0.115R on 164 trades, with all four S1 years negative. S3 shuffled-day p = 0.314 (null +0.164R). Even with S1 ≥ burned, the power ceiling is 0.292 (projected N ≈ 226).
- **D2 MMXM v1 default** generates no trades on any tape. This matches its historical run (`/workspace/mmxm/output/cfd_v1`: 0 orders); it is reported as is.
- **D3–D5** (the v2–v4 selections, two of which were already NOT QUALIFIED in their own studies) are negative or flat on burned and negative on S1.
- **Caveats:**
  - The S1 tick, swing-distance and cost scaling (addendum §C) is a declared rule, not a fitted value. Prices moved a lot over 2023–2026 (e.g. gold), and the fixed-tick mapping uses the batch-1 median close.
  - Era costs ×1.5 and the holdout day counts are planning assumptions, because the holdout is sealed.
  - The H013/H014 forward tests are unaffected by this screen; it is not evidence about them beyond the transfer and null checks.

