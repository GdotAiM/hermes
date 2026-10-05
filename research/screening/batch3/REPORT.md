# Screening batch 3: simple session-level rules E1–E5

> **Provenance (added 2026-10-05, label only, per `PROTOCOL_DATA_CONDITIONS.md`):** design=in-sample-screening · data=dukascopy-screening-2023-20260925 (Dukascopy BID/ASK, DEUIDXEUR/USA30IDXUSD/XAUUSD) · screening-manifest content hash: pending (R1) · qc_gate=not_run · slip=provisional · session=cfd · n_instruments=3. Not confirmatory; no certified-untouched claim.

> **Screening.** The protocol is `PROTOCOL.md` v1 + `PROTOCOL_BATCH3.md`, committed and pushed before any batch 3 data was read.
> The burned US100/US500 window is *discovery* for these new rules; S1 (GER40, US30, XAUUSD 2023-01..2026-09-25) is the real out-of-sample test. The H017 holdout was not read.

Costs: friction F as a round trip in points (US100 2.55, US500 1.22, GER40 4.392, US30 5.720, XAUUSD 1.402). Holm across the 5 rules at α_screen = 0.10 (S1, S3).

## E1 Asia/London range sweep reversal

| set | N | mean R | 95% CI | win | total R |
|---|---:|---:|---|---:|---:|
| burned US100+US500 (primary cost) | 252 | -0.231 | [-0.408, -0.054] | 0.32 | -58.3 |
| burned US100 | 121 | -0.230 | [-0.451, +0.001] | 0.31 | -27.9 |
| burned US500 | 131 | -0.232 | [-0.453, -0.004] | 0.32 | -30.4 |
| S1 pooled | 986 | -0.317 | [-0.398, -0.235] | 0.32 | -312.9 |
| S1 GER40 | 264 | -0.293 | [-0.439, -0.141] | 0.32 | -77.5 |
| S1 US30 | 407 | -0.238 | [-0.365, -0.113] | 0.31 | -97.1 |
| S1 XAUUSD | 315 | -0.439 | [-0.579, -0.299] | 0.32 | -138.4 |

- **S1 FAIL**: one-sided p = 1.0000, Holm = 1.0000; majority of instruments positive: False.
- **S2 FAIL**: burned folds positive 1/4 (n=53 -0.433, n=79 -0.339, n=57 -0.154, n=63 +0.003); S1 year folds positive 0/4 (2023 n=267 -0.366, 2024 n=269 -0.308, 2025 n=270 -0.372, 2026 n=180 -0.178).
- **S3 FAIL**: shuffled-day p = 0.745 (null mean -0.209, ~250 trades/rep); random-walk p = 0.961 (null mean -0.087, ~235 trades/rep); max 0.961, Holm 1.000.
- **Holdout power** (US100+US500): era mean -0.280 (×2.0: -0.328); μ_plan -0.159; σ 1.289; deff 1.24; projected N 1223; **power 0.025**, ceiling 0.025, unshrunk 0.025.
- **Gate: does NOT qualify**.

## E2 PDH/PDL sweep reversal

| set | N | mean R | 95% CI | win | total R |
|---|---:|---:|---|---:|---:|
| burned US100+US500 (primary cost) | 138 | -0.029 | [-0.252, +0.200] | 0.37 | -4.0 |
| burned US100 | 72 | +0.089 | [-0.237, +0.420] | 0.40 | +6.4 |
| burned US500 | 66 | -0.157 | [-0.463, +0.160] | 0.33 | -10.4 |
| S1 pooled | 651 | -0.122 | [-0.225, -0.015] | 0.39 | -79.1 |
| S1 GER40 | 162 | -0.277 | [-0.467, -0.084] | 0.34 | -44.9 |
| S1 US30 | 288 | +0.058 | [-0.108, +0.220] | 0.41 | +16.7 |
| S1 XAUUSD | 201 | -0.253 | [-0.433, -0.067] | 0.39 | -50.9 |

- **S1 FAIL**: one-sided p = 0.9872, Holm = 1.0000; majority of instruments positive: False.
- **S2 FAIL**: burned folds positive 3/4 (n=25 +0.050, n=45 +0.018, n=31 +0.131, n=37 -0.273); S1 year folds positive 0/4 (2023 n=178 -0.114, 2024 n=180 -0.273, 2025 n=167 -0.027, 2026 n=126 -0.041).
- **S3 FAIL**: shuffled-day p = 0.451 (null mean -0.046, ~137 trades/rep); random-walk p = 0.216 (null mean -0.079, ~148 trades/rep); max 0.451, Holm 1.000.
- **Holdout power** (US100+US500): era mean -0.074 (×2.0: -0.119); μ_plan -0.061; σ 1.374; deff 1.00; projected N 657; **power 0.025**, ceiling 0.025, unshrunk 0.025.
- **Gate: does NOT qualify**.

## E3 PD range breakout continuation

| set | N | mean R | 95% CI | win | total R |
|---|---:|---:|---|---:|---:|
| burned US100+US500 (primary cost) | 184 | -0.118 | [-0.267, +0.029] | 0.41 | -21.7 |
| burned US100 | 96 | -0.171 | [-0.356, +0.024] | 0.39 | -16.4 |
| burned US500 | 88 | -0.060 | [-0.248, +0.134] | 0.44 | -5.3 |
| S1 pooled | 808 | -0.116 | [-0.185, -0.047] | 0.40 | -94.0 |
| S1 GER40 | 203 | -0.030 | [-0.151, +0.097] | 0.46 | -6.0 |
| S1 US30 | 353 | -0.120 | [-0.230, -0.009] | 0.38 | -42.4 |
| S1 XAUUSD | 252 | -0.181 | [-0.298, -0.061] | 0.39 | -45.6 |

- **S1 FAIL**: one-sided p = 0.9994, Holm = 1.0000; majority of instruments positive: False.
- **S2 FAIL**: burned folds positive 1/4 (n=28 -0.236, n=64 +0.089, n=42 -0.192, n=50 -0.254); S1 year folds positive 0/4 (2023 n=211 -0.162, 2024 n=223 -0.075, 2025 n=222 -0.085, 2026 n=152 -0.159).
- **S3 FAIL**: shuffled-day p = 0.922 (null mean -0.007, ~162 trades/rep); random-walk p = 0.843 (null mean -0.037, ~172 trades/rep); max 0.922, Holm 1.000.
- **Holdout power** (US100+US500): era mean -0.138 (×2.0: -0.158); μ_plan -0.069; σ 0.933; deff 1.22; projected N 876; **power 0.025**, ceiling 0.025, unshrunk 0.025.
- **Gate: does NOT qualify**.

## E4 30m opening-range breakout

| set | N | mean R | 95% CI | win | total R |
|---|---:|---:|---|---:|---:|
| burned US100+US500 (primary cost) | 492 | -0.055 | [-0.161, +0.051] | 0.47 | -27.0 |
| burned US100 | 245 | -0.076 | [-0.187, +0.041] | 0.45 | -18.6 |
| burned US500 | 247 | -0.034 | [-0.153, +0.082] | 0.49 | -8.4 |
| S1 pooled | 2540 | -0.081 | [-0.121, -0.041] | 0.43 | -204.7 |
| S1 GER40 | 862 | -0.040 | [-0.095, +0.015] | 0.45 | -34.1 |
| S1 US30 | 826 | -0.048 | [-0.112, +0.015] | 0.45 | -39.8 |
| S1 XAUUSD | 852 | -0.153 | [-0.211, -0.096] | 0.41 | -130.8 |

- **S1 FAIL**: one-sided p = 1.0000, Holm = 1.0000; majority of instruments positive: False.
- **S2 FAIL**: burned folds positive 0/4 (n=103 -0.044, n=134 -0.006, n=126 -0.085, n=129 -0.085); S1 year folds positive 0/4 (2023 n=639 -0.138, 2024 n=699 -0.083, 2025 n=693 -0.043, 2026 n=509 -0.056).
- **S3 FAIL**: shuffled-day p = 0.647 (null mean -0.048, ~485 trades/rep); random-walk p = 0.608 (null mean -0.048, ~485 trades/rep); max 0.647, Holm 1.000.
- **Holdout power** (US100+US500): era mean -0.076 (×2.0: -0.097); μ_plan -0.040; σ 0.929; deff 1.67; projected N 2368; **power 0.025**, ceiling 0.025, unshrunk 0.025.
- **Gate: does NOT qualify**.

## E5 30m opening-range fade

| set | N | mean R | 95% CI | win | total R |
|---|---:|---:|---|---:|---:|
| burned US100+US500 (primary cost) | 492 | -0.025 | [-0.133, +0.087] | 0.41 | -12.2 |
| burned US100 | 245 | +0.031 | [-0.090, +0.156] | 0.45 | +7.7 |
| burned US500 | 247 | -0.081 | [-0.200, +0.042] | 0.38 | -19.9 |
| S1 pooled | 2540 | -0.088 | [-0.126, -0.048] | 0.43 | -223.6 |
| S1 GER40 | 862 | -0.103 | [-0.157, -0.049] | 0.44 | -89.0 |
| S1 US30 | 826 | -0.048 | [-0.115, +0.019] | 0.44 | -39.9 |
| S1 XAUUSD | 852 | -0.111 | [-0.172, -0.053] | 0.42 | -94.7 |

- **S1 FAIL**: one-sided p = 1.0000, Holm = 1.0000; majority of instruments positive: False.
- **S2 FAIL**: burned folds positive 2/4 (n=103 -0.044, n=134 -0.076, n=126 +0.018, n=129 +0.003); S1 year folds positive 0/4 (2023 n=639 -0.126, 2024 n=699 -0.125, 2025 n=693 -0.070, 2026 n=509 -0.014).
- **S3 FAIL**: shuffled-day p = 0.353 (null mean -0.034, ~485 trades/rep); random-walk p = 0.431 (null mean -0.032, ~485 trades/rep); max 0.431, Holm 1.000.
- **Holdout power** (US100+US500): era mean -0.046 (×2.0: -0.067); μ_plan -0.044; σ 0.990; deff 1.54; projected N 2368; **power 0.025**, ceiling 0.025, unshrunk 0.025.
- **Gate: does NOT qualify**.

## Summary

| candidate | burned N | burned mean R [CI] | S1 N | S1 mean R [CI] | S1 | S2 | S3 | holdout power | power ceiling | qualifies |
|---|---:|---|---:|---|---|---|---|---:|---:|---|
| E1 Asia/London range sweep reversal | 252 | -0.231 [-0.408, -0.054] | 986 | -0.317 [-0.398, -0.235] | FAIL | FAIL | FAIL | 0.025 | 0.025 | no |
| E2 PDH/PDL sweep reversal | 138 | -0.029 [-0.252, +0.200] | 651 | -0.122 [-0.225, -0.015] | FAIL | FAIL | FAIL | 0.025 | 0.025 | no |
| E3 PD range breakout continuation | 184 | -0.118 [-0.267, +0.029] | 808 | -0.116 [-0.185, -0.047] | FAIL | FAIL | FAIL | 0.025 | 0.025 | no |
| E4 30m opening-range breakout | 492 | -0.055 [-0.161, +0.051] | 2540 | -0.081 [-0.121, -0.041] | FAIL | FAIL | FAIL | 0.025 | 0.025 | no |
| E5 30m opening-range fade | 492 | -0.025 [-0.133, +0.087] | 2540 | -0.088 [-0.126, -0.048] | FAIL | FAIL | FAIL | 0.025 | 0.025 | no |

Power ceiling = gate power if S1 ≥ burned era mean (μ_plan = 0.5 × burned era mean). It is a derived bound, not a protocol change.

## Reading (screening caveats)

- **No rule qualifies.** All five fail S1, S2 and S3, and the gate power is 0.025 for each, because the burned era-cost mean and the S1 mean are both ≤ 0 for every rule (so even the power ceiling is 0.025).
- **S1 (the real out-of-sample test):** all five pooled S1 means are negative, and every CI excludes 0. Of the 15 rule × instrument cells, only E2 on US30 is positive (+0.058R, CI spans 0). No S1 calendar year is positive for any rule.
- **Burned (discovery):** every pooled burned mean is ≤ 0. The best single-instrument cells (E2 US100 +0.089R, E5 US100 +0.031R) do not carry over to US500 or to S1.
- **E1** (Asia/London sweep reversal) is the worst rule: −0.23R on burned and −0.32R on S1. Sweeps of the overnight range during NY AM did not reverse on average.
- **E4/E5** are exact mirrors and fire on the same 492 burned / 2,540 S1 signals. Both lose by about the cost, i.e. the 30-minute opening-range break carries no directional edge either way at 2R / 0.25 ATR.
- **S3:** the real burned means sit inside both null distributions (max p 0.43–0.96). The rules do no better than they do on shuffled-day or random-walk tape.
- **Caveats:** results are at realistic cost F only (gross was not pre-registered and is not reported). One fixed parameter set was tested per rule, by design. The rules are discarded, not re-tuned.

