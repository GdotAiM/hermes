# SMT divergence study: prereg (no results computed yet)
**Status: EXPLORATORY, IN-SAMPLE on the burned window 2025-08-25..2026-09-25, NOT EVIDENCE.**

**Data decision.**
- **FX on the box:** `/workspace/marketdata` holds EURUSD/GBPUSD 1m **BID only** (HistData fallback, plus sparse Dukascopy verification days).
  - There is no ASK side, so real costs cannot be computed.
  - It is not DATA-certified.
  - 2026-05-11..09-24 is banned (HistData stale-print defect).
- FX is therefore NOT used. The study runs on **US100 vs US500** 1m BID+ASK from `/workspace/ftn-demo-output/data` (sha-checked), cut at 2026-09-25 16:15 NY.
- No downloads, no holdout or screening data.

**Bars.** Trading day = 18:00 → 16:14 NY (`tday = (t + 6 h).date`). 5m and 15m BID bars are built from 1m, keeping bars with ≥ 50% of minutes on both instruments (the timestamp intersection).

**Swings.** 5-bar fractal (2 left, 2 right) on the TF bar low/high, confirmed at the close of bar s+2.

**SMT detection** (bullish SMT at lows; highs mirrored):
- **Pair:** a US100 swing low at s_A and a US500 swing low at s_B with |s_A − s_B| ≤ 2 TF bars (nearest; each swing used once). Levels L_A, L_B.
- **Tolerance:** tol_i = 0.02 × ATR14_TF(i) (the ATR of the 14 bars before the pair).
- **Break:** instrument i breaks at bar t if low_i[t] < L_i − tol_i, scanning from max(s_A, s_B)+3 for at most 48 TF bars. t* = the first bar where either breaks.
- **Decision time:** T0 = the close of bar t*+2.
  - **SMT:** exactly one instrument broke in [t*, t*+2] (the leader); the other's low stayed ≥ L − tol through t*+2.
  - **Both-break (null 1):** both broke in [t*, t*+2].
- Measured on 5m (primary) and 15m (secondary).

**Steps after T0** (1m BID, per instrument, each instrument measured with its own levels). Horizon = T0 + 8 h, capped at that trading day's 16:14 bar.
- **Step 2, opposite liquidity:**
  - **Internal:** the nearest confirmed TF swing high (bullish case) above the T0 close, formed within the 48 TF bars before T0.
  - **External:** the nearest of {prior trading-day high, current trading-day high up to T0} above the T0 close.
  - "Taken" = the first 1m bar with high > level, after T0, within the horizon.
- **Step 3, return to the SMT area** (after step 2i is taken, within the horizon):
  - **R1:** 1m low ≤ the instrument's own SMT swing level L_i (primary).
  - **R2:** low ≤ the CE = (L_i + internal level)/2.
- **Reported, per TF and instrument:**
  - P(2i), P(2e), P(R1 | 2i), P(R2 | 2i);
  - the full sequence P(2i ∧ R1) unconditional;
  - median minutes T0→2i and 2i→R1.

**Nulls.**
- **Null 1, matched:** both-break events with identical definitions.
- **Null 2, random swings:** every single-instrument swing break on that instrument (any fractal swing low/high broken within 48 bars, regardless of the other instrument), with T0 = the break bar + 2.
- **Primary descriptive effect:** Δ = P(2i ∧ R1 | SMT) − P(2i ∧ R1 | null 1), on 5m pooled over instruments; also vs null 2. 95% day-cluster bootstrap (2,000, seed 20261012).

**Trades (5m SMT; each instrument traded on its own levels; one position per instrument).**
- **Setup:** after step 2i (taking bar tk), trade back toward the SMT area: short for a bullish SMT, long for a bearish one.
- **Triggers:**
  - **MSS:** the first 1m close at/after tk beyond the latest confirmed 1m swing (2/2 fractal) formed ≥ tk − 30 min, in the trade direction. Entry at that close (market, correct side ∓ slip).
  - **FVG:** the first 1m FVG in the trade direction with candle 1 ≥ tk. Limit at its CE, filled when the BID high (short) / ASK low (long) reaches it.
- **Entry window:** before the target is touched and before the horizon end.
- **Stop:** the extreme from tk through the entry bar + buffer (short: max(1, assumed spread + stop slip); long: max(1, stop slip)), widened to min_risk = 4 × (assumed spread + 2 × market slip) (US100 10.2, US500 4.88).
- **Targets:** R1 (L_i) or CE (R2). Skip if the reference is already beyond the target.
- **Exits:** time exit at the horizon end. Fills, costs and stop-first as in NOWICK Addendum 3 (DATA slippage floors).
- **Variants (4):** MSS_R1, MSS_CE, FVG_R1, FVG_CE.

**Statistics.**
- Per variant (pooled, and by instrument): trades, win rate, avg win/loss R, mean R with the day-cluster CI, one-sided p.
- Holm over 4. Haircut = mean R − 1.029 × SE (E[max of 4 iid N(0,1)]).
- $10k book: 0.5% risk, 2% daily cap, 5% DD halt; halted + unhalted, max DD.
- Forward-test bar: Holm p < 0.05, haircut > 0, the same sign on both instruments, and unhalted max DD < 20%.

**Charts.**
- `smt_rates.png` (step rates vs nulls) and `equity.png`.
- 3 examples: the first 3 by date of 5m bullish-or-bearish SMTs with a full 2i → R1 sequence on US100 (pre-declared selection): `example_1..3.png`.
