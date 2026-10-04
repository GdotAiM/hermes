# INTELLIGENCE SUMMARY — FTN Month 9 kernel × month-layer hypotheses (EXPLORATORY)

> Run of the FTN-D22 rule (REV stop beyond the raid). The "WHAT CHANGED" text below is the generic re-score text from score.py (pinned unchanged by the prereg). The three-way comparison is in `research/summaries/2026-10-04_FTN_D22_REV_STOP_BEYOND_RAID_COMPARISON.md`.
**Date:** 2026-10-04  
**Owner:** FTN research bridge (agent-generated) · CASSANDRA **not yet reviewed** · DATA **not yet reviewed**  
**Tape:** historical = `DUKASCOPY-CFD-USATECHIDXUSD-BID1M` (decision) · `DUKASCOPY-CFD-USA500IDXUSD-BID1M` (disclosure, never pooled) · 2025-08-25→2026-09-25 · **burned** (same tape/calendar as H013/H014) · not CME futures

> **EXPLORATORY — pending CASSANDRA + DATA review. Not a board result. No SURVIVES language.** Paper-only research. No trades, broker calls or allowlist changes are authorized by this file. The MINT allowlist stays empty.

## WHAT DID WE THINK?
The FTN context months (M1–M8, M10–M12, Model 13) each make lecture-derived claims about when a setup works. They were turned into 13 typed hypotheses (`research/protocols/preregs/FTN_HYPOTHESES_EXPLORATORY_2026-10-04.json`) and scored only on tickets issued by the unchanged Month 9 kernel. The conditioning formulas are `hermes_interpretation`.

## WHAT DID WE OBSERVE?
| Layer | Result |
|-------|--------|
| Kernel sessions scanned (US100) | 544 (London + NY AM) · tickets 185 · gate-chain tradeable (all gates but allowlist + I0 contract) 185 · blocked by direction-vs-raid (D18) 0 · sessions where REV was refused because both/neither extremes were raided 1 · blocked by risk 0 |
| Kernel module mix | {'REV': 185} |
| US100 base expectancy (2R/stop/16:00, after costs) | **-0.018R** · N=185 · bootstrap 95% CI [-0.227, +0.195] · win rate 38.4% |
| Fragility | ex-top-1% -0.029 · ex-small-stop (<p25) +0.085 · longs 79 / shorts 106 · exits {'stop': 111, 'target': 64, 'time': 10} |
| Random-entry foil (US100) | kernel mean at the **89.7th pct** of 2000 foil means (foil median -0.147) |
| US500 disclosure (same rules, never pooled) | +0.010R · N=167 · CI [-0.211, +0.233] · win 43.1% · modules {'REV': 167} · foil pct 98.5 |
| US100 with interpretation triggers ON (CONSO/BB/PIP20; disclosure) | -0.003R · N=188 · CI [-0.209, +0.205] · win 38.8% · modules {'REV': 185, 'PIP20': 3} · foil pct 93.2 |

### Hypotheses — US100 decision series (gate chain incl. D18); Holm across the evaluated family

| ID | Month | Variable | Metric | N true / false | true vs false | Δ (95% CI) | p one-sided | p Holm | Read |
|---|---|---|---|---|---|---|---|---|---|
| FTN-H001 | M1 | `m1_correct_side_of_eq` | mean_R | 183 / 2 | — | — | — | — | not_evaluable_n<10 |
| FTN-H002 | M2 | `m2_false_breakout` | mean_R | 44 / 141 | -0.058 vs -0.005 | -0.053 [-0.534, +0.426] | 0.577 | 1.000 | no evidence after Holm |
| FTN-H003 | M3 | `m3_iof_aligned` | mean_R | 125 / 60 | -0.049 vs +0.047 | -0.096 [-0.532, +0.331] | 0.665 | 1.000 | no evidence after Holm |
| FTN-H004 | M4 | `m4_fvg_in_displacement` | mean_R | 101 / 84 | +0.050 vs -0.099 | +0.149 [-0.274, +0.563] | 0.251 | 1.000 | no evidence after Holm |
| FTN-H005 | M5 | `m5_ipda20_discount` | mean_R | 145 / 40 | -0.022 vs -0.004 | -0.018 [-0.508, +0.458] | 0.524 | 1.000 | no evidence after Holm |
| FTN-H006 | M6 | `m6_with_20d_swing` | mean_R | 67 / 118 | -0.027 vs -0.013 | -0.014 [-0.437, +0.411] | 0.527 | 1.000 | no evidence after Holm |
| FTN-H007 | M7 | `m7_osok_profile` | win_rate | 109 / 76 | +0.431 vs +0.316 | +0.115 [-0.025, +0.256] | 0.077 | 0.928 | no evidence after Holm |
| FTN-H008 | M8 | `m8_cbdr_tight` | mean_R | 101 / 84 | -0.214 vs +0.218 | -0.433 [-0.841, -0.017] | 0.979 | 1.000 | no evidence after Holm |
| FTN-H009 | M8 | `m8_ny_continues_london` | mean_R | 33 / 88 | +0.015 vs -0.090 | +0.105 [-0.503, +0.705] | 0.354 | 1.000 | no evidence after Holm |
| FTN-H010 | M10 | `m10_us500_confirms` | mean_R | 69 / 116 | +0.157 vs -0.122 | +0.280 [-0.144, +0.704] | 0.101 | 1.000 | no evidence after Holm |
| FTN-H011 | M11 | `m11_smt_divergence` | mean_R | 38 / 147 | -0.043 vs -0.011 | -0.032 [-0.530, +0.479] | 0.540 | 1.000 | no evidence after Holm |
| FTN-H012 | M12 | `m12_topdown_agree` | mean_R | 12 / 173 | -0.256 vs -0.001 | -0.255 [-0.856, +0.438] | 0.712 | 1.000 | no evidence after Holm |
| FTN-H013 | M13 | `m13_bridge_window_fvg` | mean_R | 27 / 158 | -0.084 vs -0.007 | -0.078 [-0.708, +0.556] | 0.588 | 1.000 | no evidence after Holm |

### Hypotheses — US500 disclosure series (separate family, never pooled); Holm across the evaluated family

| ID | Month | Variable | Metric | N true / false | true vs false | Δ (95% CI) | p one-sided | p Holm | Read |
|---|---|---|---|---|---|---|---|---|---|
| FTN-H001 | M1 | `m1_correct_side_of_eq` | mean_R | 165 / 2 | — | — | — | — | not_evaluable_n<10 |
| FTN-H002 | M2 | `m2_false_breakout` | mean_R | 52 / 115 | +0.108 vs -0.035 | +0.143 [-0.330, +0.631] | 0.287 | 1.000 | no evidence after Holm |
| FTN-H003 | M3 | `m3_iof_aligned` | mean_R | 108 / 59 | -0.058 vs +0.133 | -0.190 [-0.662, +0.271] | 0.788 | 1.000 | no evidence after Holm |
| FTN-H004 | M4 | `m4_fvg_in_displacement` | mean_R | 89 / 78 | +0.050 vs -0.037 | +0.087 [-0.345, +0.525] | 0.346 | 1.000 | no evidence after Holm |
| FTN-H005 | M5 | `m5_ipda20_discount` | mean_R | 130 / 37 | -0.116 vs +0.449 | -0.565 [-1.088, -0.023] | 0.982 | 1.000 | no evidence after Holm |
| FTN-H006 | M6 | `m6_with_20d_swing` | mean_R | 53 / 114 | +0.155 vs -0.058 | +0.213 [-0.261, +0.691] | 0.198 | 1.000 | no evidence after Holm |
| FTN-H007 | M7 | `m7_osok_profile` | win_rate | 101 / 66 | +0.455 vs +0.394 | +0.062 [-0.089, +0.216] | 0.269 | 1.000 | no evidence after Holm |
| FTN-H008 | M8 | `m8_cbdr_tight` | mean_R | 91 / 76 | +0.015 vs +0.004 | +0.011 [-0.442, +0.454] | 0.487 | 1.000 | no evidence after Holm |
| FTN-H009 | M8 | `m8_ny_continues_london` | mean_R | 36 / 69 | -0.072 vs -0.008 | -0.063 [-0.643, +0.509] | 0.588 | 1.000 | no evidence after Holm |
| FTN-H010 | M10 | `m10_us500_confirms` | mean_R | 0 / 0 | — | — | — | — | not_evaluable_n<10 |
| FTN-H011 | M11 | `m11_smt_divergence` | mean_R | 0 / 0 | — | — | — | — | not_evaluable_n<10 |
| FTN-H012 | M12 | `m12_topdown_agree` | mean_R | 12 / 155 | +0.528 vs -0.031 | +0.558 [-0.128, +1.239] | 0.101 | 1.000 | no evidence after Holm |
| FTN-H013 | M13 | `m13_bridge_window_fvg` | mean_R | 34 / 133 | -0.042 vs +0.023 | -0.065 [-0.573, +0.459] | 0.592 | 1.000 | no evidence after Holm |

## WHAT CHANGED?
- REV direction now comes from the raid (user decision on D18): low raided → bullish, high raided → bearish, both or neither → undetermined, no ticket. The D18 direction-vs-raid gate stays as a safety net (US100 blocks: 0). See BEFORE vs AFTER below.
- Hypotheses and scores were produced in the same change, so this is **not** a pre-registration. Any claim worth keeping needs a fresh prereg on untouched or forward data.

## WHAT SURVIVED?
- Nothing is claimed to survive. This file asserts no result beyond the numbers above.

## WHAT FAILED?
- Read the table: any row whose CI includes 0 or whose Holm p ≥ 0.05 shows no evidence for its claim.

## CAVEATS (binding on any citation)
- Burned tape (H013/H014 used the same Dukascopy BID series and calendar).
- Every bar formula is `hermes_interpretation`: IOF = candle colour, daily FVGs from session OHLC, CBDR scaled relative to its own median, OSOK = Mon–Wed opposite-side raid, SMT = US500 not taking its own extreme.
- Exit = fixed 2R / stop / 16:00 (interpretation; MONTH9 docs give no REV exit). Stop = raided extreme (D12).
- The REV origin rule is permissive (D7): almost any daily FVG below/above price satisfies `htf_pd`.
- Feature groups overlap, so the hypotheses are not independent. Holm is conservative under dependence.
- **This tape cannot confirm anything.** It was already used for H013/H014 and for the first FTN score; every re-score on it (including this one) is exploratory.

## NEXT
- CASSANDRA red-team, then DATA gate. If a row is worth testing, write a fresh prereg (new ID) before looking at untouched data: sessions after 2026-09-25 (forward), or a separate pull/feed that H013/H014 never touched (e.g. the `/workspace/marketdata` pull once DATA certifies it, or CME futures).

Reproduce: `cd ftn && PYTHONPATH=src python3 -m ftn score --asof 2026-10-04` (bars default to `/workspace/ict-blueprint/research/model-u-longrun/data/US{100,500}_1m.csv.gz`; override `--bars-us100/--bars-us500`).
