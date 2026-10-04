# Screening protocol: Addendum for batch 3 (simple session-level rules E1–E5)

This addendum was committed and pushed on 2026-10-04, **before any market data was read for batch 3**. The only runs before the commit were the unit tests on a synthetic toy random walk (`tests/test_screening.py::test_batch3_rules_mechanics`). `PROTOCOL.md` v1 applies unless this addendum overrides it. In particular these are unchanged: the stages, cluster bootstrap B = 10,000 with seed 20261004, α_screen = 0.10, N_NULL = 50 per null type, era costs ×1.5, μ_plan = 0.5 × min(burned era mean, S1 mean), power at one-sided α = 0.025, holdout day counts US100 1,004 / US500 1,612, and the S1/S2/S3/gate thresholds.

**Status of the windows.** These rules are new. The burned US100/US500 window (2025-08-25..2026-09-25) acts as **discovery / description**: no parameter is fitted on it. **S1** (GER40, US30, XAUUSD, 2023-01-01..2026-09-25, `/workspace/screening-data`, BID) is the real out-of-sample test.

**Sealing.** The H017 holdout is SEALED. Nothing is read from US100 2019-01-01..2022-12-23, US500 before 2025-06-01, the 2019–20 backfill, `/workspace/marketdata`, or any bar after 2026-09-25. No frozen worktree, tag or pinned file is touched.

## A. Candidates (Holm family = these 5, for S1 and for S3)

All rules use 1m BID bars on the NY wall clock (bar time = bar open) and take at most **one trade per instrument per NY day** (the first signal). Entry is a market order at the **close of the signal bar**. Common definitions:

**Trade day.** A NY weekday that:
- is not an NYSE full closure (the batch 2 list `adapters.NYSE_CLOSED`);
- has ≥ 120 of the 150 bars in 09:30–11:59; and
- has ≥ 14 prior eligible sessions.

**Sessions and levels.**
- **Session(D)** = bars in [D−1 18:00, D 17:00). It is eligible with ≥ 60 bars, and NYSE-closure dates are not used as sessions.
- **ATR** = mean (high − low) of the 14 most recent eligible sessions before D.
- **PDH/PDL** = high/low of the most recent eligible session before D.
- **Asia** = [D−1 19:00, D 00:00); **London** = [D 02:00, D 05:00). Each needs ≥ 30 bars, otherwise it is ignored (e.g. GER40 has no Asia bars).
- **SH/SL** = the max high / min low over the available Asia and London ranges.
- **OR** = high/low of 09:30–09:59, needing ≥ 20 bars.

**Signal window and exits.**
- Signal bars must open in [09:30, 11:30). For E4/E5 the window is [10:00, 11:30).
- Exits are checked from the bar after entry:
  - stop: if the bar trades through the stop, exit at the stop, or at the bar open if it gapped through;
  - target: at **2R**; if stop and target are both touched in the same bar, the **stop** is assumed;
  - time exit: at the close of the last bar before **12:00**.
- **R** = (direction × (exit − entry) − F) / risk, where risk = |entry − stop| and F = the round-trip friction (section C).

| ID | Rule | Signal | Stop | Target |
|---|---|---|---|---|
| E1 | **Asia/London range stop-hunt reversal** | Side X is active only if the 09:30 open is inside the level (below SH for shorts, above SL for longs). Sweep = the first window bar with high > SH (or low < SL). Reclaim = a close back inside (< SH / > SL) on the sweep bar or one of the next 4 bars (N = 5). If there is no reclaim, that side is finished for the day. If both sides fire, the earlier reclaim is taken. | Sweep extreme (max high / min low from the sweep bar to the reclaim bar) ± 0.05 ATR, widened if needed so that risk ≥ 0.10 ATR | 2R |
| E2 | **PDH/PDL sweep reversal** | Same as E1, with PDH/PDL as the levels | same as E1 | 2R |
| E3 | **Previous-day range breakout continuation** (control for E2) | Only if PDL ≤ 09:30 open ≤ PDH. The first window bar that closes > PDH gives a long; < PDL gives a short. | Entry ∓ 0.25 ATR | 2R |
| E4 | **30m opening-range breakout** | The first bar in [10:00, 11:30) that closes > OR high gives a long; < OR low gives a short. | Entry ∓ 0.25 ATR | 2R |
| E5 | **30m opening-range fade** (exact mirror of E4) | The same signal bar as E4, traded in the opposite direction | Entry ± 0.25 ATR | 2R |

**Parameters**, fixed and round: N = 5 bars, buffer 0.05 ATR, risk floor 0.10 ATR, fixed stop 0.25 ATR, target 2R, ATR over 14 sessions, OR = 30 minutes, signals until 11:30, flat at 12:00. They are not tuned, and no variant is added after results. All distances are ATR-scaled, so no tick or ρ mapping is needed.

## B. Code
- `research/screening/batch3/rules.py`: rules, with constants as above.
- `research/screening/run_batch3.py`: stages; a copy of the batch 2 runner, with the burned set = US100 + US500 for all rules.
- The sha256 values are recorded in `batch3/code_hashes.txt` in this commit.

## C. Costs (same as batch 2 primary)
- F = spread_assumed + slip_market + slip_stop, charged once per trade (a round trip in points):
  - US100 2.55
  - US500 1.22
  - GER40 4.392
  - US30 5.720
  - XAUUSD 1.402
- Era R (power): R_era = R − 0.5 × F / risk.

## D. Stages
- **S1:** the 3 instruments pooled, 2023-01-01..2026-09-25 (the first ~14 sessions are used up as ATR warm-up). Holm across the 5 rules. Pass needs p ≤ 0.10, ≥ 30 trades, and a strict majority of the instruments with ≥ 20 trades positive.
- **S2:** 4 burned folds (the batch 1 equal-trading-day folds) and 4 S1 calendar-year folds. Each needs ≥ 3 of 4 positive, and a fold with n < 10 counts as not positive.
- **S3:** null A (shuffled day) and null B (random walk), 50 replicates each, on burned US100 + US500 BID, with seeds 20261004 + k. p = (1 + #null mean ≥ real) / 51, max over the two nulls. Holm across the 5 rules ≤ 0.10 **and** real burned mean > 0.
- **Gate:** S1, S2 and S3 all pass, **and** projected holdout power ≥ 0.80. Holdout = US100 (1,004 days) + US500 (1,612 days). The trade rate is burned trades per burned trading day.

## E. Reporting
- The report gives a batch-1-style table and per-rule detail.
- Any deviation is dated and listed. Rules that do not qualify stay discarded; they are not re-tuned.
