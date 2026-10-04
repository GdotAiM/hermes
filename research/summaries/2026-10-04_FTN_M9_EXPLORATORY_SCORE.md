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
| Kernel sessions scanned (US100) | 544 (London + NY AM) · tickets 186 · gate-chain tradeable (all gates but allowlist) 9 · blocked by side-vs-raid (D18) 170 · blocked by risk 7 |
| Kernel module mix | {'REV': 186} |
| US100 base expectancy (2R/stop/16:00, after costs) | **-0.121R** · N=9 · bootstrap 95% CI [-0.839, +0.699] · win rate 33.3% |
| Fragility | ex-top-1% -0.382 · ex-small-stop (<p25) -0.269 · longs 3 / shorts 6 · exits {'stop': 5, 'target': 2, 'time': 2} |
| Random-entry foil (US100) | kernel mean at the **40.1th pct** of 2000 foil means (foil median +0.014) |
| US100 kernel side as-is (pre-D18; admits REV buys after high raids / sells after low raids) | -0.149R · N=139 · CI [-0.348, +0.056] · win 36.0% · modules {'REV': 186} · foil pct 9.6 |
| US500 disclosure (same rules, never pooled) | +0.394R · N=13 · CI [-0.342, +1.102] · win 53.8% · modules {'REV': 168} · foil pct 78.8 |
| US500 kernel side as-is (pre-D18) | -0.178R · N=130 · CI [-0.381, +0.037] · win 39.2% · modules {'REV': 168} · foil pct 23.8 |
| US100 with interpretation triggers ON (CONSO/BB/PIP20; disclosure) | +0.139R · N=12 · CI [-0.555, +0.916] · win 41.7% · modules {'REV': 186, 'PIP20': 3} · foil pct 65.5 |

### Hypotheses — US100 decision series (gate chain incl. D18); Holm across the evaluated family

| ID | Month | Variable | Metric | N true / false | true vs false | Δ (95% CI) | p one-sided | p Holm | Read |
|---|---|---|---|---|---|---|---|---|---|
| FTN-H001 | M1 | `m1_correct_side_of_eq` | mean_R | 7 / 2 | — | — | — | — | not_evaluable_n<10 |
| FTN-H002 | M2 | `m2_false_breakout` | mean_R | 2 / 7 | — | — | — | — | not_evaluable_n<10 |
| FTN-H003 | M3 | `m3_iof_aligned` | mean_R | 6 / 3 | — | — | — | — | not_evaluable_n<10 |
| FTN-H004 | M4 | `m4_fvg_in_displacement` | mean_R | 7 / 2 | — | — | — | — | not_evaluable_n<10 |
| FTN-H005 | M5 | `m5_ipda20_discount` | mean_R | 2 / 7 | — | — | — | — | not_evaluable_n<10 |
| FTN-H006 | M6 | `m6_with_20d_swing` | mean_R | 7 / 2 | — | — | — | — | not_evaluable_n<10 |
| FTN-H007 | M7 | `m7_osok_profile` | win_rate | 7 / 2 | — | — | — | — | not_evaluable_n<10 |
| FTN-H008 | M8 | `m8_cbdr_tight` | mean_R | 2 / 7 | — | — | — | — | not_evaluable_n<10 |
| FTN-H009 | M8 | `m8_ny_continues_london` | mean_R | 2 / 6 | — | — | — | — | not_evaluable_n<10 |
| FTN-H010 | M10 | `m10_us500_confirms` | mean_R | 9 / 0 | — | — | — | — | not_evaluable_n<10 |
| FTN-H011 | M11 | `m11_smt_divergence` | mean_R | 3 / 6 | — | — | — | — | not_evaluable_n<10 |
| FTN-H012 | M12 | `m12_topdown_agree` | mean_R | 7 / 2 | — | — | — | — | not_evaluable_n<10 |
| FTN-H013 | M13 | `m13_bridge_window_fvg` | mean_R | 5 / 4 | — | — | — | — | not_evaluable_n<10 |

### Hypotheses — US100 kernel side as-is (pre-D18 disclosure); Holm across the evaluated family

| ID | Month | Variable | Metric | N true / false | true vs false | Δ (95% CI) | p one-sided | p Holm | Read |
|---|---|---|---|---|---|---|---|---|---|
| FTN-H001 | M1 | `m1_correct_side_of_eq` | mean_R | 7 / 132 | — | — | — | — | not_evaluable_n<10 |
| FTN-H002 | M2 | `m2_false_breakout` | mean_R | 23 / 116 | -0.221 vs -0.135 | -0.087 [-0.720, +0.558] | 0.623 | 1.000 | no evidence after Holm |
| FTN-H003 | M3 | `m3_iof_aligned` | mean_R | 103 / 36 | -0.177 vs -0.069 | -0.108 [-0.599, +0.385] | 0.671 | 1.000 | no evidence after Holm |
| FTN-H004 | M4 | `m4_fvg_in_displacement` | mean_R | 111 / 28 | -0.129 vs -0.228 | +0.099 [-0.439, +0.597] | 0.356 | 1.000 | no evidence after Holm |
| FTN-H005 | M5 | `m5_ipda20_discount` | mean_R | 24 / 115 | -0.047 vs -0.170 | +0.123 [-0.390, +0.661] | 0.319 | 1.000 | no evidence after Holm |
| FTN-H006 | M6 | `m6_with_20d_swing` | mean_R | 89 / 50 | -0.189 vs -0.078 | -0.111 [-0.545, +0.318] | 0.694 | 1.000 | no evidence after Holm |
| FTN-H007 | M7 | `m7_osok_profile` | win_rate | 7 / 132 | — | — | — | — | not_evaluable_n<10 |
| FTN-H008 | M8 | `m8_cbdr_tight` | mean_R | 78 / 61 | +0.023 vs -0.369 | +0.393 [-0.009, +0.780] | 0.032 | 0.287 | no evidence after Holm |
| FTN-H009 | M8 | `m8_ny_continues_london` | mean_R | 63 / 25 | +0.076 vs -0.306 | +0.381 [-0.143, +0.875] | 0.095 | 0.757 | no evidence after Holm |
| FTN-H010 | M10 | `m10_us500_confirms` | mean_R | 115 / 24 | -0.043 vs -0.656 | +0.612 [+0.125, +1.050] | 0.011 | 0.109 | no evidence after Holm |
| FTN-H011 | M11 | `m11_smt_divergence` | mean_R | 21 / 118 | -0.329 vs -0.117 | -0.212 [-0.761, +0.402] | 0.760 | 1.000 | no evidence after Holm |
| FTN-H012 | M12 | `m12_topdown_agree` | mean_R | 88 / 51 | -0.144 vs -0.158 | +0.014 [-0.418, +0.447] | 0.475 | 1.000 | no evidence after Holm |
| FTN-H013 | M13 | `m13_bridge_window_fvg` | mean_R | 5 / 134 | — | — | — | — | not_evaluable_n<10 |

## WHAT CHANGED?
- The REV side check (D18) is new in this change. Of 186 US100 kernel tickets, 170 had a daytrade-IOF side that *agreed* with the raid (e.g. a buy after a PDH raid). That is a continuation, not a reversal, and the gate chain now blocks it. The as-is stream is kept as a disclosure row.
- First run. Hypotheses and scores were produced in the same change, so this is **not** a pre-registration. Any claim worth keeping needs a fresh prereg on untouched or forward data.

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

## NEXT
- CASSANDRA red-team, then DATA gate. If a row is worth testing, write a fresh prereg (new ID) on forward data.

Reproduce: `cd ftn && PYTHONPATH=src python3 -m ftn score --asof 2026-10-04` (bars default to `/workspace/ict-blueprint/research/model-u-longrun/data/US{100,500}_1m.csv.gz`; override `--bars-us100/--bars-us500`).
