# SMT divergence study: REPORT (EXPLORATORY, IN-SAMPLE on the burned window 2025-08-25..2026-09-25, NOT EVIDENCE)
- **Prereg:** `PREREG.md`, commit 5e8bddb, committed before any result.
- **Code:** `smt.py`.
- **Outputs:** `events.csv.gz`, `descriptive.csv`, `effects.csv`, `trades.csv`, `results.csv`, `smt_rates.png`, `equity.png`, `example_1..3.png`.

## Data
- **FX:** `/workspace/marketdata` has EURUSD/GBPUSD 1m, but BID only (HistData fallback; Dukascopy only on sparse verification days).
  - It is not DATA-certified, and 2026-05-11..09-24 is banned for the HistData stale-print defect.
  - With no ASK side, real costs can't be computed, so FX was **not used**.
- **Study pair:** US100 vs US500 (Dukascopy BID+ASK, burned window).
- **For a proper FX run:**
  - Dukascopy EURUSD + GBPUSD 1m **BID and ASK** for an agreed window (e.g. 2019–2025 for fitting plus a reserved untouched span).
  - DATA's sign-off on the source, the burned/untouched split and the FX slippage floors.
  - Possibly DXY as a third leg.
  - No download was started.

## Descriptive (5m primary)

| 5m, US100 / US500 | SMT | Both-break (null 1) | Every swing break (null 2) |
|---|---|---|---|
| events | 4,734 / 4,734 | 9,085 / 9,085 | 15,255 / 15,151 |
| P(internal liquidity taken), 8 h | 79.7% / 80.0% | 75.9% / 77.3% | 76.4% / 77.5% |
| P(external taken) | 50.7% / 51.1% | 45.8% / 46.1% | 46.4% / 46.5% |
| P(return to SMT level \| internal taken) | 69.9% / 71.0% | 79.2% / 79.7% | 78.3% / 78.6% |
| P(return to CE \| internal taken) | 82.5% / 83.6% | 88.1% / 88.4% | 87.6% / 88.0% |
| P(full sequence: internal then SMT level) | **55.7% / 56.8%** | **60.1% / 61.6%** | **59.8% / 60.9%** |
| median min T0 → internal / internal → return | 12 / 37–38 | 26 / 16–17 | 22–23 / 17–19 |

**Effects (SMT − null, pooled, 95% day-cluster CI).**

| | vs null 1 | vs null 2 |
|---|---|---|
| 5m P(sequence) | −4.6 pp [−6.3, −2.8] | −4.1 pp [−5.3, −2.8] |
| 5m P(internal) | +3.3 pp [+1.8, +4.7] | +2.9 pp [+1.8, +4.1] |
| 5m P(return \| internal) | −9.0 pp [−10.6, −7.4] | −8.0 pp [−9.2, −6.7] |
| 15m P(sequence) | −6.5 pp [−9.2, −3.6] | −5.4 pp [−7.6, −3.1] |

Each instrument separately has the same signs; the CIs exclude 0 except 15m US100 P(internal) vs null 1.

**Reading.** The user is right that the three-step path is frequent: more than half of 5m SMTs see internal liquidity taken and then the SMT level revisited within 8 h. But it is **less** frequent than after an ordinary swing break.
- After an SMT, price does reach the opposite side faster and slightly more often (+3 pp). That is consistent with the SMT marking a turn.
- It then returns to the SMT level *less* often (−8 to −9 pp) and more slowly (a median of about 37 vs about 17 min).
- The "return to the SMT point" leg is where SMT is worse than the baseline.

## Trades (5m SMT; enter after internal liquidity is taken; target the SMT level R1 or the CE; real costs)

| Variant | N | Win | Avg win / loss R | Mean R [95% CI] | Haircut | US100 / US500 | Halted final (halt, NY) | Unhalted final | Unhalted max DD |
|---|---|---|---|---|---|---|---|---|---|
| MSS_R1 | 6211 | 45.1% | +0.96 / −1.04 | −0.135 [−0.172, −0.095] | −0.155 | −0.103 / −0.167 | $9,528 (2025-08-28) | $1,746 | 84.8% |
| MSS_CE | 4327 | 49.9% | +0.69 / −0.97 | −0.144 [−0.184, −0.101] | −0.165 | −0.104 / −0.183 | $9,505 (2025-09-01) | $1,509 | 86.4% |
| FVG_R1 | 5020 | 30.1% | +1.86 / −1.05 | −0.174 [−0.226, −0.122] | −0.202 | −0.153 / −0.195 | $9,528 (2025-08-27) | $1,077 | 89.6% |
| FVG_CE | 3423 | 36.1% | +1.38 / −1.05 | −0.171 [−0.226, −0.114] | −0.200 | −0.142 / −0.201 | $9,490 (2025-08-27) | $1,114 | 89.0% |

- Holm p = 1.0 for all 4. Every CI is below 0 on both instruments, and every halted book halted within the first week.
- **Forward-test verdict:** none.

## Caveats
- One year, in-sample, burned data. A highly correlated index pair gives frequent but tiny divergences: the 0.02-ATR tolerance makes many SMTs.
- FX (the user's main use case) is untested.
- Trades on both instruments from the same SMT are correlated.
- Stop-first on same-bar touches.
- The examples are the first 3 by date (pre-declared), not curated.

# Addendum 1: first leg toward the opposite liquidity, London-volatility filter (EXPLORATORY, IN-SAMPLE on the burned window, NOT EVIDENCE)
- **Prereg:** 2b82185, committed before any R.
- **Code:** `addendum1.py`. **Outputs:** `addendum1_trades.csv`, `addendum1_results.csv`, `addendum1_equity.png`.
- **Filter F:** 5m SMT confirmed 09:30–11:30 NY, and that instrument's London range ≥ its trailing-20 median.
- **Columns:** CI = 95% day-cluster bootstrap; haircut = mean R − 1.267 × SE; Holm over 6.

| Variant | N | Win | Avg win / loss R | Mean R [CI] | Haircut | US100 / US500 mean R (N) | Halted final (halt, NY) | Unhalted final | Unhalted max DD |
|---|---|---|---|---|---|---|---|---|---|
| F_SMT_int | 454 | 57.0% | +0.57 / −0.85 | −0.044 [−0.164, +0.095] | −0.129 | −0.072 (225) / −0.016 (229) | $9,544 (2025-11-03) | $9,371 | 13.3% |
| F_SMT_ext | 513 | 43.5% | +1.22 / −0.99 | −0.030 [−0.190, +0.147] | −0.139 | +0.006 (258) / −0.066 (255) | $10,164 (2026-02-02) | $9,755 | 18.7% |
| F_MSS_int | 157 | 69.4% | +0.52 / −0.97 | **+0.066 [−0.104, +0.233]** | −0.041 | −0.048 (82) / +0.191 (75) | $10,331 (never halted) | $10,331 | 3.3% |
| F_MSS_ext | 308 | 53.6% | +0.94 / −0.98 | +0.046 [−0.123, +0.222] | −0.066 | +0.090 (152) / +0.002 (156) | $9,767 (2026-02-02) | $9,816 | 9.9% |
| U_SMT_int (unfiltered control) | 9162 | 49.6% | +0.60 / −0.88 | −0.147 [−0.174, −0.120] | −0.165 | −0.124 / −0.170 | $9,456 (2025-08-26) | $280 | 97.2% |
| F_SMT_scaled (London-scaled stop, 2R) | 513 | 35.7% | +1.91 / −1.06 | −0.001 [−0.171, +0.177] | −0.112 | +0.012 / −0.015 | $10,355 (2025-11-21) | $10,322 | 18.9% |

**Notes.**
- Holm p = 1.0 for all 6 (the best raw one-sided p is 0.22, F_MSS_int). Every haircut is negative.
- **Forward-test verdict (pre-declared bar):** none.
- The unhalted book takes fewer trades than the signal count: one position per instrument, plus the 2% daily cap.

**Reading.**
- Trading the first leg *toward* the opposite liquidity is unprofitable unfiltered: −0.147 R on 9,162 trades, with the CI well below 0.
- Restricting to NY AM SMTs after an above-median London session moves every variant to around 0 R (−0.04 to +0.07).
- That shift is about +0.1 to +0.2 R, but it was not a pre-registered test (filtered vs unfiltered overlap and differ in session), and no filtered variant is distinguishable from 0.
- The only variant above 0 on both instruments is F_MSS_ext (+0.09 / +0.00), and only barely.
- F_MSS_int is the best pooled variant (+0.066, never halted, max DD 3.3%), but it is positive only on US500 (N 75), so it fails sign agreement.

**If the user wants to pursue it.**
- The candidate would be "NY AM 5m SMT + above-median London range + 1m MSS entry, target external liquidity" (F_MSS_ext). It is the most balanced, but it is not a pre-registered winner.
- A forward-only prereg would be needed, and with N ≈ 300/year, a +0.05 R effect (SD ≈ 1) needs years. An honest next step is a fresh-data descriptive check, not a trading test.

**Caveats.**
- In-sample, one year, a highly correlated pair, and both instruments traded from the same SMT.
- The London filter uses the same-day 02:00–05:00 range, known before 09:30.
- 1m stop-first.

# Addendum 2: ICT intraday SD projections (EXPLORATORY, IN-SAMPLE on the burned window, NOT EVIDENCE)
- **Prereg:** 5595349, committed before any result.
- **Source and assumption:** the text of the X post "Intraday Standard Deviations by ICT" (video not seen). **Anchor definitions are our assumption.**
  - A1 = the 1m leg that made the first post-SMT MSS.
  - A2 = the SMT range (sweep extreme → high to T0).
  - Levels = hi + n × R.
- **Code:** `addendum2.py`. **Outputs:** `addendum2_levels.csv.gz`, `addendum2_descriptive.csv`, `addendum2_trades.csv`, `addendum2_results.csv`, `addendum2_equity.png`.

## Check 1: are the −2 / −2.5 SD levels special? (all 5m SMTs, both instruments, pooled)

| Anchor, n | Events | Reach: SD / C1 / C2 | P(reverse \| reach): SD / C1 / C2 | Δ vs C1 [CI] | Δ vs C2 [CI] | P(turn \| reach): SD / C1 / C2 |
|---|---|---|---|---|---|---|
| A1, 2 | 6,816 | 64.7 / 61.9 / 65.7% | 57.6 / 58.3 / 58.8% | −0.7 pp [−2.2, +0.9] | −1.2 pp [−3.5, +1.0] | 4.5 / 4.4 / 4.4% |
| A1, 2.5 | 6,816 | 59.2 / 61.9 / 59.7% | 58.2 / 58.0 / 58.5% | +0.2 pp [−1.3, +1.6] | −0.3 pp [−2.8, +2.1] | 5.0 / 4.4 / 4.3% |
| A2, 2 | 9,467 | 52.8 / 50.3 / 54.6% | 57.0 / 57.3 / 56.9% | −0.3 pp [−1.6, +1.0] | +0.2 pp [−2.1, +2.4] | 5.8 / 5.9 / 5.4% |
| A2, 2.5 | 9,467 | 46.9 / 50.2 / 48.7% | 56.9 / 57.6 / 58.1% | −0.7 pp [−2.3, +0.9] | −1.2 pp [−3.5, +0.9] | 6.1 / 5.9 / 4.8% |

- C1 = random multiples 1.5–3.0 of the same anchor. C2 = the same point distance from a random time in the same hour on another day.
- **Reading:** the SD levels are reached and reversed at the same rates as random levels at the same distance; all reversal Δs are within ±1.2 pp and the CIs span 0.
- The only nominal difference is A2 n = 2.5 "turn" vs C2: +1.3 pp [+0.2, +2.3], a 1-pp effect on a 5% base. With 48 descriptive comparisons, that is what chance produces.
- By instrument: same picture (`addendum2_descriptive.csv`).

## Check 2: SD exits on Addendum 1's filtered MSS entry (NY AM SMT, London ≥ median)

| Variant | N | Win | Avg win / loss R | Mean R [CI] | Haircut | US100 / US500 | Halted final (halt, NY) | Unhalted final | Unhalted max DD |
|---|---|---|---|---|---|---|---|---|---|
| A1_SD1 | 371 | 62.0% | +0.65 / −1.01 | +0.020 [−0.105, +0.140] | −0.066 | +0.039 / +0.000 | $9,706 (2026-06-26) | $10,490 | 8.2% |
| A1_SD2 | 371 | 51.5% | +1.12 / −1.00 | +0.091 [−0.078, +0.260] | −0.031 | +0.116 / +0.066 | $10,628 (2026-06-12) | $11,219 | 12.4% |
| A1_SD2.5 | 371 | 49.1% | +1.26 / −0.99 | **+0.114 [−0.070, +0.303]** | −0.016 | +0.082 / +0.146 | $10,852 (2026-06-17) | $11,691 | 11.8% |
| A1_P1_2.5 | 371 | 52.0% | +0.90 / −0.84 | +0.067 [−0.081, +0.211] | −0.037 | +0.060 / +0.073 | $10,318 (2026-06-18) | $11,158 | 10.1% |
| A2_SD1 | 360 | 56.7% | +0.89 / −0.97 | +0.084 [−0.069, +0.235] | −0.025 | +0.087 / +0.081 | $9,819 (2026-02-02) | $11,242 | 6.7% |
| A2_SD2 | 368 | 46.5% | +1.34 / −0.96 | +0.107 [−0.084, +0.317] | −0.039 | +0.118 / +0.096 | $10,627 (2026-02-02) | $11,670 | 13.2% |
| A2_SD2.5 | 369 | 44.4% | +1.42 / −0.96 | +0.097 [−0.102, +0.311] | −0.054 | +0.113 / +0.081 | $10,331 (2026-01-15) | $11,074 | 13.3% |
| A2_P1_2.5 | 360 | 47.8% | +1.09 / −0.84 | +0.084 [−0.082, +0.262] | −0.042 | +0.096 / +0.073 | $9,969 (2026-06-17) | $10,977 | 9.6% |

- All 8 are positive pooled and on both instruments (≥ 0), but every CI spans 0.
- Holm p ≥ 0.80 (best raw one-sided p 0.10, A1_SD2.5), every haircut is slightly negative, and every halted book hit the 5% halt at some point.
- **Forward-test verdict (pre-declared bar):** none.
- **Deviation, disclosed:** the MSS entry here is the first post-SMT MSS (it does not depend on the target), so N (371) differs from Addendum 1's F_MSS rows (157 / 308).

**Reading.**
- The SD levels are not special as price levels (check 1).
- As exits, further targets do better than near ones on this filtered entry: SD2–2.5 at about +0.10 R vs SD1 at about +0.02 to +0.08 R.
- That is more likely the filtered entry riding volatility-clustered NY AM expansion than ICT-specific levels, because random multiples at the same distance behave identically.
- The consistent sign across 8 variants and both instruments is the most encouraging thing in this branch so far. But the variants share the same 360–371 entries, so they are not independent confirmations.

## Caveats
- In-sample, one year, correlated instruments, and the anchors are assumed.
- The exit variants are nested on one entry set.
- 1m stop-first.

# Addendum 3: four confluence filters (EXPLORATORY, IN-SAMPLE on the burned window, NOT EVIDENCE)
- **Prereg:** 954f217, committed before any R.
- **Code:** `addendum3.py`. **Outputs:** `addendum3_trades.csv`, `addendum3_results.csv`, `addendum3_equity.png`.
- **Selection, disclosed:**
  - The base exit (A1 −2.5) was the best of Addendum 2's 8.
  - About **44 trading variants plus a 7,680-config grid** had been tried on this window before this addendum, and this adds 7 (+7 secondary).
  - Anything here is heavily selected.
- The base reproduces Addendum 2 exactly (371 trades, +0.114 R).

**Primary, A1 −2.5** (Holm over 7; haircut = mean R − 1.352 × SE; underpowered = N < 100):

| Variant | N (US100 / US500) | Win | Avg win / loss R | Mean R [95% CI] | Haircut | US100 / US500 mean R | Halted final (halt, NY) | Unhalted final | Unhalted max DD |
|---|---|---|---|---|---|---|---|---|---|
| base | 371 (187/184) | 49.1% | +1.26 / −0.99 | +0.114 [−0.070, +0.303] | **−0.009** | +0.082 / +0.146 | $10,852 (2026-06-17) | $11,691 | 11.8% |
| +F1 strong London | 291 (151/140) | 48.8% | +1.25 / −0.99 | +0.106 [−0.080, +0.312] | −0.033 | +0.087 / +0.128 | $10,132 (2026-06-19) | $11,158 | 9.3% |
| +F2 09:30–11:00 | 312 (158/154) | 47.8% | +1.25 / −0.98 | +0.081 [−0.114, +0.290] | −0.059 | +0.057 / +0.105 | $10,756 (2026-06-11) | $11,045 | 11.6% |
| +F3 divergence size | 326 (163/163) | 49.4% | +1.24 / −0.99 | +0.110 [−0.075, +0.310] | −0.021 | +0.089 / +0.130 | $10,262 (2026-01-12) | $11,260 | 10.5% |
| +F4 near prior-day H/L | 108 (50/58)* | 50.0% | +1.43 / −1.03 | +0.199 [−0.165, +0.569] | −0.050 | −0.014 / +0.384 | $10,611 (2026-06-19) | $10,925 | 9.3% |
| +F1+F2+F3+F4 | **64 (33/31), underpowered** | 46.9% | +1.30 / −1.03 | +0.062 [−0.373, +0.576] | −0.263 | −0.091 / +0.225 | $10,071 (2026-06-19) | $10,210 | 6.5% |
| +F1+F2+F3 | 222 (115/107) | 48.6% | +1.18 / −0.97 | +0.076 [−0.146, +0.319] | −0.086 | +0.060 / +0.092 | $9,935 (2026-01-30) | $10,687 | 7.8% |

\* F4 passes 100 pooled, but each instrument has < 100 and the signs disagree.

- Holm p = 0.70 for all 7. Every haircut is negative, and every halted book hit the 5% halt.
- **Forward-test verdict:** none.

**Secondary, A2 −2** (Holm over 7, separately):
- base +0.107 (368), F1 +0.101, F2 +0.064, **F3 +0.141 [−0.066, +0.358], Holm 0.63, haircut −0.004**, F4 +0.148 (107), F1234 +0.141 (63, underpowered), F123 +0.100.
- Same picture: positive point estimates, no CI excludes 0, Holm ≥ 0.63.

**Reading.**
- **None of the four confluences sharpens the setup.** F1, F2, F3 and their combination keep about +0.08 to +0.11 R and only cut N.
- F4 has the highest point estimate, but on 108 trades driven by US500 (+0.38) with US100 negative.
- All four together leaves 64 trades: uninformative.
- The filters don't add signal over the base on this window.

**Single best candidate for a forward-only prereg** (pre-declared rule: highest haircut, N ≥ 100, same sign on both instruments): **the base** = NY AM 5m SMT (09:30–11:30) + London range ≥ its 20-day median + first 1m MSS + A1 −2.5 exit + Addendum 2 stop.
- **Power:** in-sample mean R +0.114, SD 1.25, day-cluster design effect 1.98 (both instruments trade the same SMT), about 343 trades/year.
- With delta shrunk to half (+0.057 R, for selection after about 50 variants): **N ≈ 5,900 trades ≈ 17 years** at 80% power, α 0.05 one-sided.
- Even at the full in-sample +0.114 R: N ≈ 1,470 ≈ 4.3 years.
- Trading one instrument halves the design effect but also the rate, so it doesn't help much.
- Adding instruments (with DATA sign-off) is the only real lever.
- **Recommendation:** a fresh-data *descriptive* monitor (rate and mean R, no money), not a binding forward test, unless the user accepts a multi-year horizon.

## Caveats
- In-sample, one year, a highly correlated pair, and both instruments traded off the same SMT (DE ≈ 2).
- Anchors assumed (Addendum 2).
- 1m stop-first.
