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

---
# ADDENDUM 2 (2026-10-12, committed before any new statistic): lower-timeframe path into the revisit
Same data, window and sealing as above. Exploration only.

**Events.** 15m and 1H, both instruments, both directions.
- TOL no-wick and WICK control candles.
- "Revisited" = 1m first touch of the open within the Addendum 1 scan (3000 / 3600 min).
- Candles whose scan runs past the data end are excluded.

**Window.**
- Revisited events: [candle close, revisit minute), with the revisit bar excluded.
- Not-revisited TOL events: [close, close + M), where M = the median revisit minutes of revisited TOL events in the same instrument × TF × direction cell.
- Notation: s = +1 for bull (the open lies below; "toward the open" = down), mirrored for bear.
- The *turn* is the minute of the window's extreme away from the open (bull: max high), first occurrence.

**Feature definitions** (BID 1m; 5m bars are clock-aligned from 1m; 5m ATR14 = mean true range of the prior 14 5m bars). Fractal swing = a bar whose low (high) is strictly below (above) the 2 bars on each side; it is confirmed 2 bars later.
- **F1 OPP**: the window takes the candle's opposite extreme (bull: high > candle high).
- **F2a MSS1 / F2b MSS5**: the last confirmed 1m (5m) swing on the open side (bull: swing low) is confirmed at or before the turn, with its bar no earlier than 60 min before the candle close. MSS = a 1m (5m) close beyond it toward the open, after the turn and before the revisit (5m bar closed before the revisit).
- **F3 DISP**: a 5m bar fully inside the window, with body ≥ 1.5 × 5m ATR14, closing toward the open.
- **F4a FVG1 / F4b FVG5**: a 3-bar FVG pointing toward the open (bull: high[i] < low[i−2]), with all three bars inside the window.
  - Descriptive add-on **CE1**: given FVG1, price retraces to the first FVG1's CE (midpoint) before the revisit.
- **F5a SWP5**: in [close, turn], price exceeds a 5m swing on the far side (bull: swing high) that was confirmed before the candle close, within the prior 24 5m bars.
- **F5b SESS**: in [close, turn], price exceeds the trading-session extreme on the far side up to the candle close (NY 17:00 roll).
- **F6 OB** (descriptive, given DISP): OB = the last 5m bar of the opposite colour within the 12 bars before the first DISP bar. Retest = a 1m price reaching the OB mid-body after the DISP bar closes and before the revisit.
- **F7 KZ** (descriptive): the killzone of the turn minute and of the revisit minute (Asia / London / NYAM / NYPM / other, as in the main PREREG).
- **F8 DRIFT**: none of OPP, MSS1, MSS5, DISP, FVG1, FVG5, SWP5, SESS.

**Comparisons.** Pooled over instrument and direction, per TF.
- (a) TOL revisited vs WICK revisited, with controls reweighted to the TOL body×range quintile bins.
- (b) TOL revisited vs TOL not revisited.
- Effect = difference in feature frequency. 95% CI by date-cluster bootstrap (2000 resamples). p from the bootstrap SE.
- **Holm** within each comparison over 9 binary features (OPP, MSS1, MSS5, DISP, FVG1, FVG5, SWP5, SESS, DRIFT) × 2 TF = 18 tests. CE1, OB, KZ are descriptive.
- Known confounds, disclosed in advance: window length differs between groups (controls revisit faster; non-revisit windows are set to the median). Feature frequency rises with window length, so the report also gives window-length-stratified rates (tertiles) for comparison (a).

**Sequence.** For TOL revisits, the tokens are ordered by first time: SWEEP (earliest of OPP / SWP5 / SESS), MSS (earliest of MSS1 / MSS5), DISP, FVG (earliest of FVG1 / FVG5), each once, then REV. Reported: the top sequences and their shares per TF.

**Charts.** 3 example 15m TOL revisits carrying the modal non-empty sequence: the first 3 by date with window length 30–180 min (pre-declared selection, not cherry-picked). 1m candles with annotations.

## Addendum 3: H-NW11 illustrative equity curve. Rules written before any R is computed
**Status: EXPLORATORY, IN-SAMPLE on the burned window 2025-08-25..2026-09-25. NOT EVIDENCE.** The idea came from looking at this same data (Addendum 2), so any result here is optimistic by construction. Bars after 2026-09-25 are not read.

**Events.** NOWICK-1 `TOL` no-wick candles (nowick.features, unchanged) on 15m and 1H, US100 and US500 (BID chart). Bull no-wick (open = low) means a SHORT toward the open; bear no-wick means a LONG. The **far extreme** is the candle's high for bull and its low for bear.

**Signal (1m, scan from the first 1m bar after the candle closes).** Described in bull view (short); bear is mirrored.
- The 1m swing low is the Addendum 2 `swings()` (2 bars each side). It counts at bar k only if it is confirmed (s + 2 ≤ k − 1) and formed at or after candle close − 60 min.
- The **MSS** at bar k is the first 1m BID close below the most recent such swing low.
- The far extreme must not be taken (BID high ≤ candle high on every 1m bar from the close through k), and the open must not yet be touched.
- If the far extreme is taken or the open is touched before an MSS, the event is dead.
- The MSS must occur within 20 TF bars of the candle close (300 min on 15m, 1200 min on 1H) and before the end of the trading day (17:00 NY roll). At most one trade per candle.

**Entry.** At the close of the MSS bar. Short fills at BID close − market slip; long fills at ASK close + market slip.

**Stop.**
- Short: the highest BID high from the swing low through the MSS bar (the swing that made the MSS), plus a buffer of max(1 pt, assumed spread + stop slip).
- Long: the lowest BID low − max(1 pt, stop slip). (This is the H016 buffer convention.)
- If |signal close − stop| < min_risk = 4 × (assumed spread + 2 × slip), the stop is **widened** to min_risk (US100 10.2 pt, US500 4.88 pt).

**Target.** The no-wick open (a limit).
- Short: exits when ASK low < open, filled at open + limit slip.
- Long: exits when BID high > open, filled at open − limit slip.
- Stop fills: short when ASK high ≥ stop, at max(stop, ASK open) + stop slip; long when BID low ≤ stop, at min(stop, BID open) − stop slip.
- If the stop and the target are both touched in the same 1m bar, the stop is assumed (conservative).

**Time stop.** A fixed bar count: 20 TF bars after the candle close (15m: 300 min; 1H: 1200 min), or the 16:59 NY trading-day roll, whichever comes first. The exit is at that 1m bar's correct-side close ∓ market slip.

**Costs.** Real correct-side BID/ASK prices (the measured spread) plus the DATA slippage floors from ftn/os/instruments.py: US100 0.50/0.50/0.25, US500 0.25/0.25/0.10 (stop/market/limit). Assumed spreads (for buffers and min stop): US100 1.55, US500 0.72. ASK minutes missing from the feed are forward-filled.

**R.** (exit fill − entry fill) × side / |signal close − stop|.

**Book.**
- Starts at $10,000 and risks 0.5% of current realized equity per trade (size = risk$ / planned risk points).
- No overlapping positions per instrument; 15m and 1H share the instrument slot, and the first in time wins.
- Daily loss cap: no new entries for the rest of the trading day once realized P&L that day ≤ −2% of start-of-day equity.
- 5% max drawdown from the realized-equity peak halts all trading. The date is reported, and the unhalted curve is reported too (same rules without the halt).

**Reported.**
- Final equity, return %, trade count, win rate (R > 0), mean R with a 95% day-cluster bootstrap CI (2000 draws, seed 20261012), and max drawdown.
- Splits by instrument and timeframe.
- Equity PNG `research/nowick/hnw11_equity.png`.

## Addendum 4: H-NW11 variant family. Rules written before any R is computed
**Status: EXPLORATORY, IN-SAMPLE on the burned window, NOT EVIDENCE.** The family is fixed at 7 variants, chosen from Addendum 3's diagnosis (winners about +0.6 R vs losers about −1.1 R because the open sits close relative to the structural stop) and not tuned. Everything not stated below is identical to Addendum 3: events, the MSS signal (bar k, swing s), costs and fills, stop-first on ambiguous bars, the time stop (20 TF bars / day roll), min_risk widening, the book ($10k, 0.5% risk, 2% daily cap, 5% DD halt plus an unhalted curve, one position per instrument), and the bootstrap.

"Bull view" below means the short trade taken after a bull no-wick candle; bear is mirrored.

**Variants.**
- **V1 (H-NW12): FVG CE entry.**
  - FVG: the latest 1m bearish FVG (L[g−2] > H[g]) with s < g ≤ k.
  - Entry: a limit sell at its CE (L[g−2] + H[g])/2, filled when BID high ≥ CE on a bar after k, at CE − limit slip.
  - Cancellation: the order is cancelled if the open is touched, the far extreme is taken, or the time stop arrives first.
  - Stop and target: the Addendum 3 stop (min_risk widening measured from the CE) and the open as target.
  - No FVG means no trade.
- **V2: partial at the open plus 2R runner.** The Addendum 3 entry and stop. Half the size exits at the open (limit). The other half targets entry ∓ 2 × risk, with the stop unchanged. R is the average of the two halves. If the open is beyond 2R, both halves target 2R.
- **V3: far-extreme stop with a 1.5R filter.** Stop = far extreme + Addendum 3 buffer, min_risk widened. Trade only if |signal close − open| ≥ 1.5 × risk. Target is the open.
- **V4: killzone filter.** Addendum 3 trades with the MSS bar in London (02:00–05:00 NY) or NY AM (07:00–10:00 NY) only.
- **V5: premium/discount filter.** Addendum 3 trades where the signal close is in the premium (short) or discount (long) half of the previous trading day's BID high–low range.
- **V6: fade on a failed MSS.**
  - Trigger: after an Addendum 3 signal, if the far extreme is taken (BID high > candle high) before the open is touched and before the time stop.
  - Entry: long in the continuation direction at the close of that 1m bar (ASK close + market slip).
  - Stop: the lowest BID low from k to that bar, − max(1, stop slip), min_risk widened.
  - Target: entry + 2 × risk. Same time stop.
- **V7: HTF bias alignment.** Addendum 3 trades where the previous trading day's BID candle closed in the trade's direction (short needs a bearish previous day).

**Statistics.**
- Per variant: trades, win rate, mean R with a 95% day-cluster CI (all signals, no book), and the halted and unhalted book.
- One-sided bootstrap p for mean R > 0 (share of draws ≤ 0), Holm-adjusted across the 7.
- Haircut: mean R − SE × E[max of 7 iid N(0,1)] (= 1.352 × SE), a deflated-Sharpe-style correction for picking the best of 7.
- **Forward-test bar.** A variant is "worth a fresh-data forward test" only if Holm p < 0.05 AND the haircut mean R > 0 AND the unhalted book is not halted-worthy (max DD < 20%). Otherwise none.
- Comparison PNG: `research/nowick/add4_equity.png`.

## Addendum 5: FVG / iFVG entries toward the open, no MSS. Rules written before any R is computed
**Status: EXPLORATORY, IN-SAMPLE on the burned window, NOT EVIDENCE.** The family is fixed at 6 variants (3 entries × 2 targets), not tuned. Everything not stated below is identical to Addendum 4: events (TOL, 15m + 1H, US100 + US500), the scan window (from the first 1m bar after the candle close to e = min(close + 20 TF bars, the day roll)), costs and fills, stop-first, min_risk widening, the book, the bootstrap and the forward-test bar.

"Bull view" = the short toward an open below; bear is mirrored. An event is dead from the first bar whose BID low ≤ open or BID high > far extreme. No entry can occur on or after that bar.

**Entries (no MSS needed).**
- **A, FVG CE limit.**
  - FVG: the first 1m bearish FVG (L[g−2] > H[g]) with g − 2 ≥ the first bar after the close, completed before the event dies.
  - Entry: a limit sell at CE = (L[g−2] + H[g])/2, live from bar g+1. It fills on the first bar with BID high ≥ CE at CE − limit slip, provided that bar is before the event dies or the time stop.
  - Stop: H[g−2] (candle 1 high) + max(1, assumed spread + stop slip).
- **B, iFVG inversion.**
  - Opposing FVG: the first 1m bullish FVG (H[g−2] < L[g]) with g − 2 ≥ the first bar after the close.
  - Inversion: the first later bar q with BID close < H[g−2] (closed through the gap's bottom), before the event dies.
  - Entry: market at BID close[q] − market slip.
  - Stop: the highest BID high over g−2..q + buffer. Only the first opposing FVG is used.
- **C, first of A or B.** Whichever entry fills first (A on a tie). Its own stop.

Every stop is widened to min_risk from the reference price (CE for A, BID close for B) if it is closer. One trade per candle per variant.

**Targets.**
- **"open":** the no-wick open (limit).
- **"2R":** reference ∓ 2 × risk (limit), ignoring the open.
- Time stop as in Addendum 3. R = (exit fill − entry fill) × side / |reference − stop|.

**Variants:** A_open, B_open, C_open, A_2R, B_2R, C_2R.

**Statistics.**
- As Addendum 4, plus avg win R and avg loss R.
- Holm across the 6. Haircut = mean R − 1.267 × SE (E[max of 6 iid N(0,1)]).
- Forward-test bar: Holm p < 0.05 AND haircut > 0 AND unhalted max DD < 20%.
- PNG: `research/nowick/add5_equity.png`.

## Addendum 6: deliberate fit on US100, single test on US500. Design written before any R is computed
**Status: EXPLORATORY, IN-SAMPLE (burned window 2025-08-25..2026-09-25), NOT EVIDENCE.** US100 and US500 are highly correlated over the same window, so the US500 test is only a weak independence check. The GER40/US30/XAU screening data is not used.

**Fit (US100 only).** A free grid search over TOL no-wick events on 15m and 1H. Costs, fills, stop-first, the 4× min-stop widening and the book are the same as in Addendum 3. The grid has 7,680 configs, all counted as tried.

The main dimensions:
- **Direction:** toward the open, or continuation (trade in the candle's direction).
- **Entry (1m):**
  - **immediate:** the close of the first 1m bar after the candle.
  - **MSS:** a close through the latest confirmed 1m swing (formed ≥ close − 60 min) in the trade direction.
  - **FVG_CE:** a limit at the CE of the first trade-direction 1m FVG formed after the close.
  - **iFVG:** the first opposing 1m FVG, entered at the first close back through it.
- **Entry validity:**
  - **Toward:** the entry must come before the open is touched or the far extreme is taken.
  - **Continuation:** the entry must come before the open is touched.
  - **Both:** the entry must come before the time stop.
- **Stop:**
  - **swing:** the extreme from the setup start through the entry.
  - **fvg:** the FVG candle-1 / iFVG range extreme (falls back to swing for immediate/MSS).
  - **far:** toward → the far extreme; continuation → the open.
  - **atr1:** 1.0 × the TF ATR14 from the reference.
  - All stops carry the Addendum 3 buffers and min_risk widening.
- **Target:**
  - **open:** toward only.
  - **1.5R, 2R, 3R:** from the reference.
  - **opp:** the previous trading day's high (long) or low (short); no trade if it is behind the reference.
- **Time stop:** 10 or 20 TF bars after the candle close, capped at the day roll.

**Filters** (every combination):
- **Killzone:** all sessions, or London + NY AM only.
- **Premium/discount** (previous day's range): off or on.
- **Prior-day bias:** off or on.
- **TF:** both, 15m only, or 1H only.

**Selection.**
- The winner is the best US100 mean R among configs with ≥ 150 US100 trades (all signals). The top 5 are kept.
- Haircut for the fit: mean R − SE × sqrt(2 ln 7680) (≈ 4.23 SE, the expected max of 7,680 iid normals; conservative given the correlated configs).
- The winner and top 5 are frozen in `research/nowick/add6_frozen.json` and committed BEFORE any US500 R exists. `addendum6.py test` refuses to run unless that file is committed and unmodified.

**Test (US500, run once).**
- Per config: trades, win rate, mean R with a 95% day-cluster CI, and a one-sided bootstrap p for mean R > 0.
- Also per config: the $10k book (0.5% / 2% / 5% halted and unhalted) and max DD.
- PNG: `research/nowick/add6_equity.png` (fit US100 vs test US500).
