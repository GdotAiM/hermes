# 7PM range sweep: prereg (no R computed yet)
**Status: EXPLORATORY, IN-SAMPLE on the burned window 2025-08-25..2026-09-25, NOT EVIDENCE.**
- **Data:** US100 and US500 1m BID and ASK from `/workspace/ftn-demo-output/data` (sha-checked). No bars after 2026-09-25 17:00 NY, no holdout or screening data, no downloads.
- **Times:** NY.

**Range.** For each evening D (Sun–Thu), RH/RL = the highest BID high / lowest BID low of the 1m bars 19:00–19:59. It needs ≥ 45 bars and RH > RL. Mid = (RH + RL)/2.

**Trade window: 20:00 D → 07:59 D+1, cutoff 08:00 NY.** Fixed in advance. Why 08:00:
- It keeps the trade in the overnight (Asia + London) flow the 7PM range describes.
- It exits before the 08:30 US news releases and the NY pre-market/RTH regime change.
- 12 h is long enough for the opposite side to be reached on most nights.
- The last trade window ends 2026-09-25 08:00.

**Sweep.**
- The first 1m bar from 20:00 whose BID high > RH (high sweep → short) or BID low < RL (low sweep → long).
- If both happen in the same first bar, the day is ambiguous and skipped.
- Only the first sweep counts. One trade per day per instrument per variant.

**Entries** (short case; long mirrored):
- **b, market:** at the close of the sweep bar, BID close − market slip.
- **a, close back inside:** at the first 1m BID close < RH at or after the sweep bar.
- **c, MSS back inside:**
  - The swing: the latest confirmed 1m swing low (2 bars each side, confirmed s + 2 ≤ k − 1), formed at or after 19:00.
  - The trigger: the first bar k at or after the sweep with BID close < that swing low, and also < RH.
- **For a and c:** no entry if the target is reached (BID low ≤ target) before the entry bar or by the cutoff.

**Stop.**
- Short: the highest BID high from the sweep bar through the entry bar + max(1, assumed spread + stop slip). Long: the lowest BID low − max(1, stop slip).
- If |entry reference − stop| < min_risk = 4 × (assumed spread + 2 × market slip) (US100 10.2, US500 4.88), the stop is widened to min_risk.

**Targets.**
- **opp:** the opposite extreme (RL for a short).
- **mid:** the midpoint. Skip if the entry reference is already at or beyond it.

**Variants (6):** a_opp, a_mid, b_opp, b_mid, c_opp, c_mid.

**Fills and costs** (as in NOWICK Addendum 3: real ASK series + the DATA slippage floors US100 0.5/0.5/0.25, US500 0.25/0.25/0.10; assumed spreads 1.55/0.72):
- **Short:** stopped when ASK high ≥ stop, filled at max(stop, ASK open) + stop slip. Target hit when ASK low < target, filled at target + limit slip.
- **Long:** stopped when BID low ≤ stop, filled at min(stop, BID open) − stop slip. Target hit when BID high > target, filled at target − limit slip.
- **Same bar:** stop first.
- **Time exit:** at the last bar before 08:00, at the correct-side close ∓ market slip. Missing ASK minutes are forward-filled.
- **R** = (exit − entry fill) × side / |entry reference − stop|.

**Book.**
- $10k, 0.5% of realized equity per trade.
- No new entries for the rest of the day once that day's realized P&L ≤ −2% (day = evening D).
- A 5% max DD from the peak halts the book; the unhalted curve is reported too.
- One position per instrument. Each variant is simulated as its own book across both instruments.

**Statistics.**
- Per variant (pooled, and per instrument): trades, win rate, avg win R / avg loss R, mean R with a 95% day-cluster bootstrap CI (2,000 draws, seed 20261012), and a one-sided p for mean R > 0.
- Holm across the 6 pooled p. Haircut = mean R − 1.267 × SE.
- Halted / unhalted final equity and max DD. PNG `research/7pm/equity.png`.
- Forward-test bar: Holm p < 0.05, haircut > 0, the same sign on both instruments, and unhalted max DD < 20%.

**Descriptive.**
- P(a side is swept by 08:00); P(the opposite side is reached after the first sweep, by 08:00); minutes from the sweep to the opposite side (median); P(the mid is reached).
- **Null:** the same statistics for the 1-h ranges starting at every other hour h (00:00–23:00, h ≠ 19). The follow window is 12 h from h+1, clipped at the weekend gap, and only windows inside the data are used.
- **Effect:** P_opp(19:00) − the mean of P_opp(other hours), day-cluster bootstrap CI.
- **Caveat, disclosed:** different hours have different volatility profiles. A per-hour figure is also given.

## Addendum 1 (user correction): 6PM range. Written before any R is computed
- **What changes:** only the windows. Range = 18:00–18:59 NY (needs ≥ 45 bars). Trade window = 19:00 D → 07:59 D+1 (cutoff 08:00 unchanged).
- **Unchanged:** the 6 variants, sweep/entry/stop/target definitions, costs and fills, the book, the bootstrap, Holm, the haircut and the forward-test bar.
- **Null:** the same other-hours null (1-h ranges at every hour, 12-h follow), now comparing hour 18 against the rest, plus the rank of hour 18.
- **Data-quality check, reported:** 18:00 is the session reopen after the 17:00 roll. The report gives:
  - 1m bar counts per 18:00 hour (share of nights < 45 bars, i.e. excluded);
  - the minutes of ASK missing;
  - the median and p95 ASK − BID close spread in the 18:00 hour vs 19:00–07:59.
- **Outputs:** suffix `_6pm` (`results_6pm.csv`, `descriptive_6pm.csv`, `null_6pm.csv`, `trades_6pm.csv`) and `research/7pm/equity_6pm.png`.
