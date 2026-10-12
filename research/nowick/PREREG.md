# NOWICK-1 — "No premium/discount wick" candle open revisit study (PREREG)

Status: **descriptive, in-sample, burned-window exploration. Not confirmatory.** Written and committed before any statistic was computed.
Date: 2026-10-12. Branch: `research/nowick-study` (from origin/main b5b27af).

## Question (user)
"Investigate candlesticks without a premium or discount wick: how often do we trade back to them and sweep that candle's low/open, and what other hypotheses can we test."

## Interpretation
- **Bullish no-discount-wick candle**: close > open and NO lower wick, i.e. open == low within tolerance.
- **Bearish no-premium-wick candle**: close < open and NO upper wick, i.e. open == high within tolerance.
- ICT folklore: such an "unfilled"/"naked" open tends to be revisited and swept. For these candles the open *is* the low (bull) / high (bear), so "sweep the low/open" is one level.

## Data (hard limits)
- US100, US500 Dukascopy 1m **BID + ASK**, canonical burned export `/workspace/ftn-demo-output/data/US{100,500}_1m_{bid,ask}.csv.gz`
  (decompressed sha256 checked: US100 bid 6afa3130…, ask fcc3c877…; US500 bid 9d68787c…, ask ff63783f…).
- Trading days 2025-08-25 .. 2026-09-25 only (NY 17:00 roll). Nothing dated 2026-09-26 or later is read; the loader asserts it.
  No `/workspace/marketdata` certified ranges, no 2019-20 backfill, no forward/H016b/H017 material.
- Candles are built from BID. Per-candle spread = median (ASK close − BID close) over the candle's matched minutes.

## Timeframes
15m, 1H (clock-aligned, NY time), 4H (bins starting 17:00, 21:00, 01:00, 05:00, 09:00, 13:00 NY), Daily (NY 17:00 → 17:00). Bars with fewer than 50% of expected 1m minutes are dropped.

## Candle filters
- ATR14 = 14-bar simple mean true range on the same timeframe (needs 14 prior bars).
- Minimum: range ≥ 0.5 × ATR14 and body/range ≥ 0.30.
- **No-wick (primary, "TOL")**: same-side wick ≤ 2% of range AND ≤ 1 × candle spread.
- **No-wick (exact, "EXACT")**: same-side wick == 0 (BID prices to 0.001).
- **Control ("WICK")**: same-side wick ≥ 10% of range (passes the same min filters).

## Outcomes (measured on BID bars after the candle closes; the candle itself excluded)
- **Revisit**: bull: some later bar low ≤ open; bear: some later bar high ≥ open.
- **Sweep**: trades through the open by ≥ max(1 candle spread, 0.001): bull low ≤ open − spread; bear high ≥ open + spread.
- Horizons: intraday TFs: next 5 / 20 / 50 bars, plus end of same trading day and end of next trading day (NY 17:00). Daily: next 5 / 20 days.
- Bars-to-revisit (median, among revisits within the largest bar horizon).
- Ordering vs opposite extreme (largest bar horizon): bull: did price first exceed the candle high or first revisit the open (same-bar = ambiguous). Bear mirrored.
- Time-of-day: candle open hour mapped to killzones (NY): Asia 20:00–00:00, London 02:00–05:00, NY AM 07:00–10:00, NY PM 13:30–16:00, other.

## Baselines
- **(a) Matched controls (primary)**: WICK candles of the same instrument/TF/direction, matched by bins of body/ATR (quintiles) × range/ATR (quintiles), quintile edges from the pooled TOL+WICK set. Baseline rate = control rates reweighted to the no-wick bin distribution (bins with no control dropped and counted). Note: for a control the *open* is inside the candle (wick beyond it), the revisit target is still the open.
- **(b) Block bootstrap of real paths**: for each no-wick candle, 20 future-path blocks drawn from random other bars of the same instrument/TF, path expressed in ATR units relative to that bar's close and rescaled by the candle's ATR; revisit if the path reaches the candle's (open − close). Preserves volatility and drift of the window, destroys any link to the candle.
- **(c) Distance-conditioned**: rate of revisit for ALL same-direction candles passing the min filters, binned by body/ATR deciles, evaluated at the no-wick candles' distances.
- **Effect** = no-wick rate − baseline (a). 95% CI by cluster bootstrap over trading days (2000 resamples; days resampled jointly for treatment and control). Two-sided p from the bootstrap SE (normal approx). **Holm** across all primary cells (instrument × TF × direction × horizon, TOL variant, revisit and sweep outcomes as separate families each Holm-adjusted). EXACT, baselines (b)/(c), killzones, ordering are descriptive only.

## Not done
No trade rule is evaluated here. Any "fade to the open" R would require a separate, pre-declared, cost-aware rule (listed as a follow-up hypothesis only).

---
# ADDENDUM 1 (2026-10-12, committed before any new statistic)
Same data, window and rules as above. All results remain in-sample burned exploration.

## A. Timing
- Groups: TOL no-wick vs WICK controls, per instrument × TF × direction (15m/1H/4H/D).
- Controls are reweighted to the no-wick body/ATR × range/ATR quintile-bin distribution, exactly as in baseline (a).
- Bar resolution: first later bar touching the open (revisit) / through it by ≥ 1 spread (sweep), within the scan window (200 / 60 / 20 / 20 bars).
  - Reported: p25/p50/p75/p90 bars; % within 1/3/5/10/20/50 bars; % never revisited within the scan.
  - A censored percentile is reported as ">scan".
- 1m resolution: the first BID 1m bar after the candle close that touches / sweeps the open, scanned up to the same clock length (scan bars × TF minutes). Minutes are counted from the candle close to the end of that 1m bar.
  - Same percentiles in minutes.
- Survival curves (fraction not yet revisited vs minutes, 1m resolution), no-wick vs weighted control, for 15m and 1H: PNGs.
- Descriptive; no tests.

## B. Premium / discount (Q4)
- Position of the candle open within a dealing range:
  - **Primary**: prior 20 completed sessions' high–low (from daily bars; the current session is excluded).
  - **Alternative**: the current session's high–low before the candle opens. Needs ≥ 60 min of session elapsed and range > 0, else unclassified.
- Zone A ("aligned"): bull in discount (pos < 0.5) / bear in premium (pos > 0.5). Zone B: the opposite half.
- **Secondary OTE band**: zone A restricted to the OTE band (bull pos in [0.21, 0.38], i.e. a 62–79% retracement from the high; bear pos in [0.62, 0.79]) vs zone B.
- Outcomes: revisit and sweep at 20 bars and same session (intraday TFs only). The daily TF is excluded (N too small).
- Effect = DiD = (no-wick − matched control)_A − (no-wick − matched control)_B.
  - The matched control uses the quintile reweighting within each zone.
  - 95% CI by day-cluster bootstrap (2000 resamples, the same day draw for both zones).
  - p from the bootstrap SE.
- **Holm** over the primary family (20-session range × inst × TF{15m, 1H, 4H} × dir × outcome × horizon = 48 cells). The alternative range and OTE band are Holm-adjusted as separate families and are descriptive.
- Hypothesis direction: DiD < 0 (aligned no-wick opens revisited less).

## C. Daily / weekly / true-day / 09:30 opens (Q5)
- (i) **Daily no-wick** (17:00 roll): revisit / sweep rate within 1 / 5 / 20 days vs matched controls; this is the existing D cells, re-reported with N.
- (ii) **Weekly** candles (Sunday 17:00 NY → Friday close): no-wick on that side, revisit within 1 / 4 weeks; controls = wicked weeks.
- (iii) **Clock-time opens**:
  - For each trading day, the 60-minute candle starting at 00:00 NY and at 09:30 NY.
  - Measured from the candle close up to 360 minutes on 1m BID: first-touch time of its open, revisit rate, sweep rate. Reported for all candles, and for no-wick candles (same TOL rule, using the 1H ATR14 at that time).
  - Baseline: 60 clock-time minutes drawn once (seed 20261012) uniformly from [18:00, 09:45) NY, excluding 00:00 and 09:30, treated identically.
  - Reported: the percentile rank of 00:00 / 09:30 among the 60 baseline times for revisit rate and median first-touch minutes.
- Any cell with N < 30 is marked **INSUFFICIENT**, with a power note: the N per arm needed to detect a 10 pp difference at 80% power / α = 0.05, and the implied years of data at the observed event frequency.
- Confirmation requires fresh multi-year data (new instruments 2023+ after DATA's screening remediation, or the forward test). No sealed data is opened.
