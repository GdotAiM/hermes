# Screening batch 1: C1 REV baseline, C2 Wednesday-only, C3 US500-only

> **Screening, not evidence.** Protocol `research/screening/PROTOCOL.md` v1 was committed (`d42f966`) before any run.
> The burned window is burned, and C2 was chosen by looking at it. A PASS here would only *earn* a holdout; the holdout (US100 2019-01-01..2022-12-23, US500 before 2025-06-01) stays SEALED and was not opened, decoded or hashed.

## Data

- Burned: US100/US500 canonical BID+ASK tape 2025-08-25..2026-09-25 (trading days {'US100': 272, 'US500': 272}), 258 registered trades.
- S1: fresh Dukascopy BID+ASK 1m, UTC days 2023-01-01..2026-09-25:
  - GER40: {'first_bar': '2023-01-01 19:15:00', 'last_bar': '2026-09-25 15:59:00', 'trading_days': 958, 'status': 'ok'}
  - US30: {'first_bar': '2023-01-02 18:00:00', 'last_bar': '2026-09-25 16:14:00', 'trading_days': 928, 'status': 'ok'}
  - XAUUSD: {'first_bar': '2023-01-02 18:00:00', 'last_bar': '2026-09-25 16:59:00', 'trading_days': 936, 'status': 'ok'}

S1 instrument specs (protocol §2 rules, measured on 2025-08-25..2026-09-25 of the new data; fixed before outcomes):

| instrument | pip | range_scale | spread_assumed | slip stop/market | slip limit | min_risk |
|---|---:|---:|---:|---:|---:|---:|
| GER40 | 1.0 | 4.944 | 2.624 | 0.884 | 0.442 | 17.568 |
| US30 | 1.0 | 9.068 | 2.17 | 1.775 | 0.887 | 22.880 |
| XAUUSD | 0.1 | 14.761 | 0.84 | 0.281 | 0.141 | 5.608 |

## C1: REV baseline

| set | N | mean R | 95% CI (cluster) | win | total R |
|---|---:|---:|---|---:|---:|
| burned US100/US500 | 258 | +0.100 | [-0.096, +0.300] | 40.3% | +25.9 |
| S1 pooled (GER40, US30, XAUUSD) | 1195 | -0.130 | [-0.205, -0.055] | 35.0% | -155.8 |
| S1 GER40 | 522 | -0.182 | [-0.283, -0.082] | 33.9% | -94.8 |
| S1 US30 | 367 | -0.076 | [-0.216, +0.068] | 35.7% | -27.8 |
| S1 XAUUSD | 306 | -0.108 | [-0.242, +0.033] | 35.9% | -33.2 |

- **S1 FAIL**: one-sided p = 0.9997, Holm = 1.0000 (needs ≤ 0.10, ≥ 30 trades, and a majority of instruments positive: False).
- **S2 FAIL**: burned folds positive 3/4 2025-08-25..2025-12-01 n=39 +0.434, 2025-12-02..2026-03-12 n=66 +0.327, 2026-03-13..2026-06-18 n=78 -0.216, 2026-06-22..2026-09-25 n=75 +0.056; S1 year folds positive 0/4 2023 n=239 -0.207, 2024 n=281 -0.211, 2025 n=374 -0.087, 2026 n=301 -0.048.
- **S3 PASS**: shuffled-day p = 0.020 (null mean -0.052, p95 +0.051, ~241 trades/rep); random-walk p = 0.039 (null mean -0.077, p95 +0.054, ~258 trades/rep); max = 0.039, Holm = 0.078.
- **Holdout power**: era-cost (×1.5) burned mean +0.056 (×2.0: +0.012); μ_plan = 0.5 × min(+0.056, S1 -0.130) = -0.065; σ 1.408, deff 1.34; projected holdout N = 1203 (US100 0.537/day, US500 0.412/day); **power = 0.025**; ceiling if S1 ≥ burned (μ_plan = 0.5 × burned era mean) = 0.087 (unshrunk 0.224; N for 0.8 at μ_plan: n/a, μ_plan ≤ 0).
- **Gate: does NOT qualify**.

## C2: REV Wednesday-only

| set | N | mean R | 95% CI (cluster) | win | total R |
|---|---:|---:|---|---:|---:|
| burned US100/US500 | 53 | +0.572 | [+0.102, +1.020] | 52.8% | +30.3 |
| S1 pooled (GER40, US30, XAUUSD) | 231 | -0.027 | [-0.206, +0.156] | 37.7% | -6.3 |
| S1 GER40 | 99 | -0.071 | [-0.299, +0.169] | 39.4% | -7.1 |
| S1 US30 | 67 | +0.107 | [-0.246, +0.470] | 41.8% | +7.1 |
| S1 XAUUSD | 65 | -0.098 | [-0.400, +0.221] | 30.8% | -6.3 |

- **S1 FAIL**: one-sided p = 0.6175, Holm = 1.0000 (needs ≤ 0.10, ≥ 30 trades, and a majority of instruments positive: False).
- **S2 FAIL**: burned folds positive 2/4 2025-08-25..2025-12-01 n=6 +1.449, 2025-12-02..2026-03-12 n=15 +0.548, 2026-03-13..2026-06-18 n=14 -0.265, 2026-06-22..2026-09-25 n=18 +0.953; S1 year folds positive 2/4 2023 n=42 -0.015, 2024 n=57 -0.261, 2025 n=76 +0.059, 2026 n=56 +0.086.
- **S3 PASS**: shuffled-day p = 0.020 (null mean -0.046, p95 +0.382, ~46 trades/rep); random-walk p = 0.020 (null mean -0.088, p95 +0.274, ~51 trades/rep); max = 0.020, Holm = 0.059.
- **Holdout power**: era-cost (×1.5) burned mean +0.526 (×2.0: +0.479); μ_plan = 0.5 × min(+0.526, S1 -0.027) = -0.014; σ 1.458, deff 1.41; projected holdout N = 243 (US100 0.118/day, US500 0.077/day); **power = 0.025**; ceiling if S1 ≥ burned (μ_plan = 0.5 × burned era mean) = 0.658 (unshrunk 0.997; N for 0.8 at μ_plan: n/a, μ_plan ≤ 0).
- **Gate: does NOT qualify**.

## C3: REV US500-only

| set | N | mean R | 95% CI (cluster) | win | total R |
|---|---:|---:|---|---:|---:|
| burned US100/US500 | 112 | +0.188 | [-0.068, +0.457] | 44.6% | +21.0 |
| S1 pooled (GER40, US30) | 889 | -0.138 | [-0.223, -0.048] | 34.6% | -122.6 |
| S1 GER40 | 522 | -0.182 | [-0.283, -0.082] | 33.9% | -94.8 |
| S1 US30 | 367 | -0.076 | [-0.216, +0.068] | 35.7% | -27.8 |

- **S1 FAIL**: one-sided p = 0.9988, Holm = 1.0000 (needs ≤ 0.10, ≥ 30 trades, and a majority of instruments positive: False).
- **S2 FAIL**: burned folds positive 3/4 2025-08-25..2025-12-01 n=19 +0.588, 2025-12-02..2026-03-12 n=28 +0.513, 2026-03-13..2026-06-18 n=34 -0.378, 2026-06-22..2026-09-25 n=31 +0.269; S1 year folds positive 0/4 2023 n=213 -0.248, 2024 n=207 -0.215, 2025 n=262 -0.023, 2026 n=207 -0.093.
- **S3 PASS**: shuffled-day p = 0.039 (null mean -0.024, p95 +0.123, ~104 trades/rep); random-walk p = 0.020 (null mean -0.117, p95 +0.112, ~117 trades/rep); max = 0.039, Holm = 0.078.
- **Holdout power**: era-cost (×1.5) burned mean +0.128 (×2.0: +0.067); μ_plan = 0.5 × min(+0.128, S1 -0.138) = -0.069; σ 1.422, deff 1.00; projected holdout N = 664 (US500 0.412/day); **power = 0.025**; ceiling if S1 ≥ burned (μ_plan = 0.5 × burned era mean) = 0.210 (unshrunk 0.637; N for 0.8 at μ_plan: n/a, μ_plan ≤ 0).
- **Gate: does NOT qualify**.

## Summary

| candidate | burned N | burned mean R [CI] | S1 N | S1 mean R [CI] | S1 | S2 | S3 | holdout power | power ceiling | qualifies |
|---|---:|---|---:|---|---|---|---|---:|---:|---|
| C1 REV baseline | 258 | +0.100 [-0.096, +0.300] | 1195 | -0.130 [-0.205, -0.055] | FAIL | FAIL | PASS | 0.025 | 0.087 | no |
| C2 REV Wednesday-only | 53 | +0.572 [+0.102, +1.020] | 231 | -0.027 [-0.206, +0.156] | FAIL | FAIL | PASS | 0.025 | 0.658 | no |
| C3 REV US500-only | 112 | +0.188 [-0.068, +0.457] | 889 | -0.138 [-0.223, -0.048] | FAIL | FAIL | PASS | 0.025 | 0.210 | no |

Holm per stage across the 3 candidates of this batch at α_screen = 0.10 (S1 and S3). S2 is rule-based.
Power ceiling = the gate power when S1 is at least as good as the burned era-cost mean. This is the most S1 could give; it is a derived bound, not a protocol change.

## Reading (screening caveats)

- No candidate qualifies. Each one fails S1 and S2, and the gate power is 0.025 because μ_plan ≤ 0. Even if S1 had matched the burned era-cost mean, the power ceiling stays below 0.8 for all three (C2 comes closest, and only because of its selection-inflated burned mean on 53 trades).
- S1: REV loses on all three new instruments. Pooled C1 is −0.130R, and the GER40 CI excludes 0. The costs come from the declared scaling rules (p90 killzone spread, slippage floors). A gross-of-cost sensitivity was not pre-registered and is not reported. GER40's NY AM killzone is the Frankfurt afternoon, and the attached US macro calendar does not matter there (REV does not read it).
- S3: the burned REV mean beats both null types (shuffled days, matched random walk). The nulls are negative on average (costs), so the rule does not profit on pure noise, but S3 was run on the same burned window the rule was fixed on.
- C2 (Wednesday) was picked as the best of 18 burned splits. Its S1 mean is −0.027R (2 of 3 instruments negative), which is consistent with a selection artefact.
- Era costs (×1.5) and the US500 holdout start date (2019-01-02) are planning assumptions, because the holdout is sealed.

