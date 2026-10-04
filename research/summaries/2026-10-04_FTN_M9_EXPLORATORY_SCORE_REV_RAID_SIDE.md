# INTELLIGENCE SUMMARY — FTN Month 9 kernel × month-layer hypotheses (EXPLORATORY)
**Date:** 2026-10-04  
**Owner:** FTN research bridge (agent-generated) · CASSANDRA **not yet reviewed** · DATA **not yet reviewed**  
**Tape:** historical = `DUKASCOPY-CFD-USATECHIDXUSD-BID1M` (decision) · `DUKASCOPY-CFD-USA500IDXUSD-BID1M` (disclosure, never pooled) · 2025-08-25→2026-09-25 · **burned** (same tape/calendar as H013/H014) · not CME futures

> **EXPLORATORY — pending CASSANDRA + DATA review. Not a board result. No SURVIVES language.** Paper-only research. No trades, broker calls or allowlist changes are authorized by this file. The MINT allowlist stays empty.

## WHAT DID WE THINK?
The FTN context months (M1–M8, M10–M12, Model 13) each make lecture-derived claims about when a setup works. They were turned into 13 typed hypotheses (`research/protocols/preregs/FTN_HYPOTHESES_EXPLORATORY_2026-10-04.json`) and scored only on tickets issued by the unchanged Month 9 kernel. The conditioning formulas are `hermes_interpretation`.

## WHAT DID WE OBSERVE?
| Layer | Result |
|-------|--------|
| Kernel sessions scanned (US100) | 544 (London + NY AM) · tickets 185 · gate-chain tradeable (all gates but allowlist + I0 contract) 49 · blocked by direction-vs-raid (D18) 0 · sessions where REV was refused because both/neither extremes were raided 1 · blocked by risk 136 |
| Kernel module mix | {'REV': 185} |
| US100 base expectancy (2R/stop/16:00, after costs) | **+0.155R** · N=49 · bootstrap 95% CI [-0.264, +0.571] · win rate 42.9% |
| Fragility | ex-top-1% +0.117 · ex-small-stop (<p25) -0.085 · longs 22 / shorts 27 · exits {'stop': 27, 'target': 20, 'time': 2} |
| Random-entry foil (US100) | kernel mean at the **87.8th pct** of 2000 foil means (foil median -0.098) |
| US500 disclosure (same rules, never pooled) | -0.068R · N=46 · CI [-0.522, +0.378] · win 45.7% · modules {'REV': 167} · foil pct 88.2 |
| US100 with interpretation triggers ON (CONSO/BB/PIP20; disclosure) | +0.200R · N=52 · CI [-0.202, +0.618] · win 44.2% · modules {'REV': 185, 'PIP20': 3} · foil pct 93.8 |

### Hypotheses — US100 decision series (gate chain incl. D18); Holm across the evaluated family

| ID | Month | Variable | Metric | N true / false | true vs false | Δ (95% CI) | p one-sided | p Holm | Read |
|---|---|---|---|---|---|---|---|---|---|
| FTN-H001 | M1 | `m1_correct_side_of_eq` | mean_R | 47 / 2 | — | — | — | — | not_evaluable_n<10 |
| FTN-H002 | M2 | `m2_false_breakout` | mean_R | 20 / 29 | +0.164 vs +0.149 | +0.015 [-0.810, +0.866] | 0.493 | 1.000 | no evidence after Holm |
| FTN-H003 | M3 | `m3_iof_aligned` | mean_R | 26 / 23 | -0.080 vs +0.421 | -0.501 [-1.313, +0.330] | 0.879 | 1.000 | no evidence after Holm |
| FTN-H004 | M4 | `m4_fvg_in_displacement` | mean_R | 28 / 21 | +0.140 vs +0.176 | -0.035 [-0.868, +0.795] | 0.526 | 1.000 | no evidence after Holm |
| FTN-H005 | M5 | `m5_ipda20_discount` | mean_R | 37 / 12 | +0.111 vs +0.293 | -0.183 [-1.112, +0.718] | 0.649 | 1.000 | no evidence after Holm |
| FTN-H006 | M6 | `m6_with_20d_swing` | mean_R | 14 / 35 | +0.191 vs +0.141 | +0.050 [-0.925, +0.997] | 0.474 | 1.000 | no evidence after Holm |
| FTN-H007 | M7 | `m7_osok_profile` | win_rate | 24 / 25 | +0.500 vs +0.360 | +0.140 [-0.143, +0.390] | 0.236 | 1.000 | no evidence after Holm |
| FTN-H008 | M8 | `m8_cbdr_tight` | mean_R | 19 / 30 | +0.123 vs +0.176 | -0.052 [-0.911, +0.816] | 0.550 | 1.000 | no evidence after Holm |
| FTN-H009 | M8 | `m8_ny_continues_london` | mean_R | 10 / 26 | -0.166 vs +0.183 | -0.349 [-1.313, +0.678] | 0.765 | 1.000 | no evidence after Holm |
| FTN-H010 | M10 | `m10_us500_confirms` | mean_R | 43 / 6 | — | — | — | — | not_evaluable_n<10 |
| FTN-H011 | M11 | `m11_smt_divergence` | mean_R | 17 / 32 | -0.324 vs +0.410 | -0.735 [-1.554, +0.131] | 0.952 | 1.000 | no evidence after Holm |
| FTN-H012 | M12 | `m12_topdown_agree` | mean_R | 7 / 42 | — | — | — | — | not_evaluable_n<10 |
| FTN-H013 | M13 | `m13_bridge_window_fvg` | mean_R | 8 / 41 | — | — | — | — | not_evaluable_n<10 |

### Hypotheses — US500 disclosure series (separate family, never pooled); Holm across the evaluated family

| ID | Month | Variable | Metric | N true / false | true vs false | Δ (95% CI) | p one-sided | p Holm | Read |
|---|---|---|---|---|---|---|---|---|---|
| FTN-H001 | M1 | `m1_correct_side_of_eq` | mean_R | 44 / 2 | — | — | — | — | not_evaluable_n<10 |
| FTN-H002 | M2 | `m2_false_breakout` | mean_R | 25 / 21 | -0.316 vs +0.228 | -0.544 [-1.452, +0.381] | 0.877 | 1.000 | no evidence after Holm |
| FTN-H003 | M3 | `m3_iof_aligned` | mean_R | 22 / 24 | -0.129 vs -0.012 | -0.117 [-1.046, +0.781] | 0.595 | 1.000 | no evidence after Holm |
| FTN-H004 | M4 | `m4_fvg_in_displacement` | mean_R | 28 / 18 | +0.242 vs -0.549 | +0.791 [-0.150, +1.749] | 0.049 | 0.343 | no evidence after Holm |
| FTN-H005 | M5 | `m5_ipda20_discount` | mean_R | 33 / 13 | -0.345 vs +0.636 | -0.982 [-1.874, -0.085] | 0.975 | 1.000 | no evidence after Holm |
| FTN-H006 | M6 | `m6_with_20d_swing` | mean_R | 16 / 30 | +0.160 vs -0.189 | +0.349 [-0.608, +1.276] | 0.239 | 1.000 | no evidence after Holm |
| FTN-H007 | M7 | `m7_osok_profile` | win_rate | 24 / 22 | +0.542 vs +0.364 | +0.178 [-0.098, +0.451] | 0.182 | 1.000 | no evidence after Holm |
| FTN-H008 | M8 | `m8_cbdr_tight` | mean_R | 26 / 20 | -0.127 vs +0.009 | -0.135 [-1.053, +0.784] | 0.602 | 1.000 | no evidence after Holm |
| FTN-H009 | M8 | `m8_ny_continues_london` | mean_R | 7 / 26 | — | — | — | — | not_evaluable_n<10 |
| FTN-H010 | M10 | `m10_us500_confirms` | mean_R | 0 / 0 | — | — | — | — | not_evaluable_n<10 |
| FTN-H011 | M11 | `m11_smt_divergence` | mean_R | 0 / 0 | — | — | — | — | not_evaluable_n<10 |
| FTN-H012 | M12 | `m12_topdown_agree` | mean_R | 9 / 37 | — | — | — | — | not_evaluable_n<10 |
| FTN-H013 | M13 | `m13_bridge_window_fvg` | mean_R | 8 / 38 | — | — | — | — | not_evaluable_n<10 |

## WHAT CHANGED?
- REV direction now comes from the raid (user decision on D18): low raided → bullish, high raided → bearish, both or neither → undetermined, no ticket. The D18 direction-vs-raid gate stays as a safety net (US100 blocks: 0). See BEFORE vs AFTER below.
- Versus the first score's **legacy (IOF-side, pre-D18) disclosure stream** (US100 N=139, −0.149R [−0.348, +0.056], foil 9.6th pct): its two best rows do not carry over. H010 (M10 US500 confirms) was Δ +0.612 [+0.125, +1.050], p 0.011, Holm 0.109 → now not evaluable (43 / 6). H008 (M8 tight CBDR) was Δ +0.393, Holm 0.287 → now Δ −0.052 [−0.911, +0.816], Holm 1.000. No row reaches Holm p < 0.05 before or after, on either instrument.
- **New finding (REPORT D22):** with the raid-side direction, 136 / 185 US100 and 121 / 167 US500 tickets are blocked by `risk:stop_not_protective`. REV's stop is the raided *level* (PDH/PDL price, D12), and at the MSS close price is often still beyond that level, so the stop sits on the wrong side. An ICT stop would sit beyond the raid's extreme (the high/low printed by the raid). Not changed here; the 49 / 46 tradeable tickets are the ones where entry is already back inside the level.
- Hypotheses and scores were produced in the same change, so this is **not** a pre-registration. Any claim worth keeping needs a fresh prereg on untouched or forward data.

## BEFORE vs AFTER (REV direction from the raid; D18 gate kept as safety net)

Before = `research/evidence/quant/FTN_M9_SCORE_2026-10-04_before_rebased.json` (REV side from the daytrade IOF, D18 blocking incoherent ones).

| Series | Tickets before → after | Tradeable N before → after | Mean R before → after (95% CI) | Foil pct before → after | D18 blocks before → after |
|---|---|---|---|---|---|
| US100_base | 186 → 185 | 9 → 49 | -0.121 [-0.839, +0.699] → +0.155 [-0.264, +0.571] | 40.1 → 87.8 | 170 → 0 |
| US500_base | 168 → 167 | 13 → 46 | +0.394 [-0.342, +1.102] → -0.068 [-0.522, +0.378] | 78.8 → 88.2 | 151 → 0 |
| US100_interp | 189 → 188 | 12 → 52 | +0.139 [-0.555, +0.916] → +0.200 [-0.202, +0.618] | 65.5 → 93.8 | 170 → 0 |

| Series | Hypothesis | before: status / Δ / p Holm | after: status / Δ (95% CI) / p Holm | Changed? |
|---|---|---|---|---|
| US100_base | FTN-H001 | not_evaluable_n<10 (7/2) | not_evaluable_n<10 (47/2) | — |
| US100_base | FTN-H002 | not_evaluable_n<10 (2/7) | evaluated (20/29) / +0.015 [-0.810, +0.866] / 1.000 | evaluability |
| US100_base | FTN-H003 | not_evaluable_n<10 (6/3) | evaluated (26/23) / -0.501 [-1.313, +0.330] / 1.000 | evaluability |
| US100_base | FTN-H004 | not_evaluable_n<10 (7/2) | evaluated (28/21) / -0.035 [-0.868, +0.795] / 1.000 | evaluability |
| US100_base | FTN-H005 | not_evaluable_n<10 (2/7) | evaluated (37/12) / -0.183 [-1.112, +0.718] / 1.000 | evaluability |
| US100_base | FTN-H006 | not_evaluable_n<10 (7/2) | evaluated (14/35) / +0.050 [-0.925, +0.997] / 1.000 | evaluability |
| US100_base | FTN-H007 | not_evaluable_n<10 (7/2) | evaluated (24/25) / +0.140 [-0.143, +0.390] / 1.000 | evaluability |
| US100_base | FTN-H008 | not_evaluable_n<10 (2/7) | evaluated (19/30) / -0.052 [-0.911, +0.816] / 1.000 | evaluability |
| US100_base | FTN-H009 | not_evaluable_n<10 (2/6) | evaluated (10/26) / -0.349 [-1.313, +0.678] / 1.000 | evaluability |
| US100_base | FTN-H010 | not_evaluable_n<10 (9/0) | not_evaluable_n<10 (43/6) | — |
| US100_base | FTN-H011 | not_evaluable_n<10 (3/6) | evaluated (17/32) / -0.735 [-1.554, +0.131] / 1.000 | evaluability |
| US100_base | FTN-H012 | not_evaluable_n<10 (7/2) | not_evaluable_n<10 (7/42) | — |
| US100_base | FTN-H013 | not_evaluable_n<10 (5/4) | not_evaluable_n<10 (8/41) | — |
| US500_base | FTN-H001 | not_evaluable_n<10 (11/2) | not_evaluable_n<10 (44/2) | — |
| US500_base | FTN-H002 | not_evaluable_n<10 (4/9) | evaluated (25/21) / -0.544 [-1.452, +0.381] / 1.000 | evaluability |
| US500_base | FTN-H003 | not_evaluable_n<10 (8/5) | evaluated (22/24) / -0.117 [-1.046, +0.781] / 1.000 | evaluability |
| US500_base | FTN-H004 | not_evaluable_n<10 (11/2) | evaluated (28/18) / +0.791 [-0.150, +1.749] / 0.343 | evaluability |
| US500_base | FTN-H005 | not_evaluable_n<10 (2/11) | evaluated (33/13) / -0.982 [-1.874, -0.085] / 1.000 | evaluability |
| US500_base | FTN-H006 | not_evaluable_n<10 (10/3) | evaluated (16/30) / +0.349 [-0.608, +1.276] / 1.000 | evaluability |
| US500_base | FTN-H007 | not_evaluable_n<10 (11/2) | evaluated (24/22) / +0.178 [-0.098, +0.451] / 1.000 | evaluability |
| US500_base | FTN-H008 | not_evaluable_n<10 (6/7) | evaluated (26/20) / -0.135 [-1.053, +0.784] / 1.000 | evaluability |
| US500_base | FTN-H009 | not_evaluable_n<10 (3/8) | not_evaluable_n<10 (7/26) | — |
| US500_base | FTN-H010 | not_evaluable_n<10 (0/0) | not_evaluable_n<10 (0/0) | — |
| US500_base | FTN-H011 | not_evaluable_n<10 (0/0) | not_evaluable_n<10 (0/0) | — |
| US500_base | FTN-H012 | not_evaluable_n<10 (10/3) | not_evaluable_n<10 (9/37) | — |
| US500_base | FTN-H013 | not_evaluable_n<10 (6/7) | not_evaluable_n<10 (8/38) | — |

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
