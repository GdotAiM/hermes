# NOWICK-1 REPORT: no-premium / no-discount wick candles, open revisit & sweep

**Label: IN-SAMPLE, BURNED-WINDOW EXPLORATION. Descriptive, not confirmatory. No trade rule tested.**
Data: Dukascopy BID+ASK 1m, US100 + US500, trading days 2025-08-25 .. 2026-09-25 (NY 17:00 roll), canonical burned export
`/workspace/ftn-demo-output/data` (decompressed sha256 verified in code). Nothing dated ≥ 2026-09-26 read. Prereg: `PREREG.md` (committed before any statistic).
Code: `nowick.py` (seeded, ~15 s). Raw outputs: `results_cells.csv`, `results_ordering.csv`, `results_killzones.csv`.

## Interpretation (as stated by the user)
Bullish candle with **no discount (lower) wick** = open == low (tolerance); bearish candle with **no premium (upper) wick** = open == high.
Folklore: the "naked"/"unfilled" open gets revisited and swept. Primary definition TOL: wick ≤ 2% of range and ≤ 1 spread; EXACT: wick = 0.
Filters: range ≥ 0.5 ATR14, body ≥ 30% of range. Control: same direction, wick ≥ 10% of range, matched on body/ATR × range/ATR quintiles.

## Headline
1. **Revisit rates are high, but that is just distance.** No-wick opens are revisited 50–60% within 5 bars, 70–80% within 20, 83–88% within 50, and 90%+ by end of next trading day (15m). Those rates sit at or **below** every baseline.
2. **The effect runs against the folklore.** On 15m, no-wick opens are revisited **less** often than matched with-wick controls over short horizons: −5 to −8 pp at 5 bars in all four instrument × direction cells. US100 bull −8.4 pp [−12.4, −4.7] (Holm p 0.001), US500 bull −8.0 pp [−11.7, −4.0] (Holm p 0.003). US500 1H bear 5b: −16.0 pp (Holm p 0.047). By 50 bars / next day the gap goes to ~0. **No cell shows a positive effect after Holm.**
3. The block-bootstrap null (b) and the distance null (c) roughly match the no-wick rates (within ~±3 pp on 15m). So the naked open behaves like any level at the same ATR distance. The matched with-wick candle is the one that is revisited a little *more* (likely mean reversion after a candle that already showed two-sided trade).
4. **Sweep ≈ revisit.** Once the open is touched, it is almost always run by ≥ 1 spread (revisit − sweep gap 0–3 pp). "Revisit" and "sweep the open/low" are practically the same event at these spreads.
5. **Order: the opposite extreme is usually taken first.** For no-wick candles, the candle's opposite extreme (bull high / bear low) goes first 64–75% of the time, versus the open first 20–26%. Controls: 53–63% vs 17–25%, with far more same-bar ambiguity. Continuation first, then the return to the open.
6. **Killzones (15m, 20 bars, raw):** no-wick revisit is below the unmatched with-wick controls in every killzone. The highest no-wick revisit rates are NY AM (80–84%), the lowest NY PM (62–79%). The 1H killzone cells are too small (N 12–32) to read.
7. **4H / Daily are underpowered.** 4H N = 13–41 per cell, Daily N = 1–6 (no CI). A no-wick daily candle on the 17:00 roll is rare in this window. Nothing can be said about daily/weekly folklore from this sample.

## Headline table: 20-bar horizon (intraday) / 5-day (daily), TOL definition
| inst | TF | dir | N | revisit % | sweep % | matched baseline % | diff pp [95% CI] | Holm p | med bars→revisit |
|---|---|---|---|---|---|---|---|---|---|
| US100 | 15m | bull | 968 | 72.5 | 71.9 | 77.2 | -4.7 [-8.0, -1.4] | 0.319 | 4 |
| US100 | 15m | bear | 812 | 76.7 | 75.5 | 80.1 | -3.3 [-7.1, +0.4] | 1.000 | 4 |
| US100 | 1H | bull | 169 | 76.3 | 76.3 | 79.3 | -3.1 [-11.6, +5.4] | 1.000 | 4 |
| US100 | 1H | bear | 124 | 77.4 | 76.6 | 82.5 | -3.9 [-11.7, +3.6] | 1.000 | 3 |
| US100 | 4H | bull | 35 | 80.0 | 80.0 | 73.8 | +6.9 [-14.6, +25.0] | 1.000 | 2.5 |
| US100 | 4H | bear | 13 | 69.2 | 69.2 | 84.0 | -17.4 [-45.6, +10.2] | 1.000 | 3 |
| US100 | D | bull | 6 | 66.7 | 66.7 | 46.7 | — | 1.000 | 1 |
| US100 | D | bear | 1 | 100.0 | 100.0 | — | — | 1.000 | 4 |
| US500 | 15m | bull | 1029 | 72.9 | 70.6 | 78.4 | -5.4 [-8.4, -1.8] | 0.080 | 4 |
| US500 | 15m | bear | 914 | 78.6 | 75.9 | 80.5 | -2.0 [-4.9, +1.0] | 1.000 | 3 |
| US500 | 1H | bull | 190 | 74.2 | 73.7 | 78.1 | -3.7 [-12.8, +5.1] | 1.000 | 4 |
| US500 | 1H | bear | 165 | 76.4 | 73.9 | 83.4 | -7.0 [-14.0, -0.7] | 1.000 | 4 |
| US500 | 4H | bull | 40 | 77.5 | 77.5 | 79.3 | -3.6 [-22.4, +14.2] | 1.000 | 2 |
| US500 | 4H | bear | 36 | 75.0 | 75.0 | 84.4 | -10.1 [-27.6, +6.4] | 1.000 | 3 |
| US500 | D | bull | 4 | 0.0 | 0.0 | 72.2 | — | 1.000 | 8 |
| US500 | D | bear | 4 | 50.0 | 50.0 | 100.0 | — | 1.000 | 3 |

Note: "revisit %" is the raw rate; diff uses the matched rate (no-wick candles in control-less bins dropped), so diff ≠ revisit − baseline exactly.
Holm family = all 68 revisit cells (inst × TF × dir × horizon); sweep cells are a separate 68-cell family. Effect CI = cluster bootstrap by trading day (2000 resamples); p = normal approximation from the bootstrap SE.

## Full table (all horizons; sweep, nulls (b)/(c), EXACT variant)
| inst | TF | dir | horizon | N | revisit % | sweep % | baseline (a) % | diff pp [95% CI] | Holm p | null (b) % | null (c) % | med bars→revisit | N exact / rev % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| US100 | 15m | bull | 5b | 968 | 50.5 | 49.8 | 59.0 | -8.4 [-12.4, -4.7] | 0.001 | 53.1 | 55.8 | 4 | 430 / 49.5 |
| US100 | 15m | bull | 20b | 968 | 72.5 | 71.9 | 77.2 | -4.7 [-8.0, -1.4] | 0.319 | 72.6 | 74.7 | 4 | 430 / 72.1 |
| US100 | 15m | bull | 50b | 967 | 83.8 | 83.2 | 86.2 | -2.4 [-5.1, +0.3] | 1.000 | 83.4 | 84.1 | 4 | 429 / 83.4 |
| US100 | 15m | bull | sameday | 968 | 80.6 | 80.0 | 82.5 | -1.9 [-4.8, +1.0] | 1.000 | — | 80.7 | 4 | 430 / 80.0 |
| US100 | 15m | bull | nextday | 966 | 90.4 | 90.1 | 91.4 | -1.0 [-3.3, +1.2] | 1.000 | — | 90.1 | 4 | 429 / 90.7 |
| US100 | 15m | bear | 5b | 812 | 55.2 | 52.8 | 60.5 | -5.4 [-9.2, -1.5] | 0.506 | 51.0 | 58.2 | 4 | 304 / 50.3 |
| US100 | 15m | bear | 20b | 812 | 76.7 | 75.5 | 80.1 | -3.3 [-7.1, +0.4] | 1.000 | 73.7 | 77.5 | 4 | 304 / 73.7 |
| US100 | 15m | bear | 50b | 809 | 85.4 | 84.8 | 87.1 | -1.7 [-4.7, +1.2] | 1.000 | 83.8 | 85.9 | 4 | 303 / 79.9 |
| US100 | 15m | bear | sameday | 812 | 83.0 | 82.4 | 82.7 | +0.3 [-3.1, +3.7] | 1.000 | — | 81.7 | 4 | 304 / 78.0 |
| US100 | 15m | bear | nextday | 809 | 93.0 | 92.5 | 92.8 | +0.2 [-1.5, +1.9] | 1.000 | — | 92.2 | 4 | 303 / 89.8 |
| US100 | 1H | bull | 5b | 170 | 53.5 | 52.4 | 56.3 | -3.0 [-12.8, +6.4] | 1.000 | 56.4 | 57.5 | 4 | 71 / 57.7 |
| US100 | 1H | bull | 20b | 169 | 76.3 | 76.3 | 79.3 | -3.1 [-11.6, +5.4] | 1.000 | 77.4 | 77.5 | 4 | 71 / 73.2 |
| US100 | 1H | bull | 50b | 169 | 87.0 | 87.0 | 87.1 | +0.1 [-6.4, +6.2] | 1.000 | 84.7 | 85.2 | 4 | 71 / 83.1 |
| US100 | 1H | bull | sameday | 170 | 67.6 | 67.1 | 67.4 | -0.2 [-9.6, +8.4] | 1.000 | — | 64.4 | 4 | 71 / 64.8 |
| US100 | 1H | bull | nextday | 169 | 82.8 | 82.8 | 84.4 | -1.5 [-9.5, +5.1] | 1.000 | — | 81.7 | 4 | 71 / 81.7 |
| US100 | 1H | bear | 5b | 125 | 56.0 | 54.4 | 62.3 | -5.7 [-15.5, +3.9] | 1.000 | 51.6 | 59.6 | 3 | 51 / 54.9 |
| US100 | 1H | bear | 20b | 124 | 77.4 | 76.6 | 82.5 | -3.9 [-11.7, +3.6] | 1.000 | 74.6 | 78.7 | 3 | 51 / 72.5 |
| US100 | 1H | bear | 50b | 123 | 86.2 | 85.4 | 90.2 | -2.7 [-9.6, +3.9] | 1.000 | 85.0 | 87.5 | 3 | 51 / 78.4 |
| US100 | 1H | bear | sameday | 125 | 63.2 | 62.4 | 66.9 | -3.0 [-12.0, +5.9] | 1.000 | — | 63.7 | 3 | 51 / 58.8 |
| US100 | 1H | bear | nextday | 124 | 83.9 | 83.1 | 86.7 | -1.6 [-9.0, +5.4] | 1.000 | — | 83.6 | 3 | 51 / 76.5 |
| US100 | 4H | bull | 5b | 35 | 60.0 | 60.0 | 62.1 | -0.8 [-25.8, +19.9] | 1.000 | 64.7 | 58.0 | 2.5 | 16 / 62.5 |
| US100 | 4H | bull | 20b | 35 | 80.0 | 80.0 | 73.8 | +6.9 [-14.6, +25.0] | 1.000 | 81.3 | 78.1 | 2.5 | 16 / 87.5 |
| US100 | 4H | bull | 50b | 35 | 80.0 | 80.0 | 76.2 | +4.4 [-16.3, +21.4] | 1.000 | 88.6 | 79.8 | 2.5 | 16 / 87.5 |
| US100 | 4H | bull | sameday | 35 | 51.4 | 51.4 | 50.7 | +0.9 [-24.6, +21.0] | 1.000 | — | 43.3 | 2.5 | 16 / 56.2 |
| US100 | 4H | bull | nextday | 35 | 74.3 | 74.3 | 65.2 | +9.0 [-12.1, +28.1] | 1.000 | — | 65.6 | 2.5 | 16 / 81.2 |
| US100 | 4H | bear | 5b | 13 | 53.8 | 53.8 | 65.7 | -15.7 [-46.8, +15.4] | 1.000 | 57.3 | 61.5 | 3 | 5 / 60.0 |
| US100 | 4H | bear | 20b | 13 | 69.2 | 69.2 | 84.0 | -17.4 [-45.6, +10.2] | 1.000 | 76.9 | 82.2 | 3 | 5 / 60.0 |
| US100 | 4H | bear | 50b | 13 | 69.2 | 69.2 | 84.9 | -18.3 [-48.1, +10.8] | 1.000 | 86.9 | 81.7 | 3 | 5 / 60.0 |
| US100 | 4H | bear | sameday | 13 | 38.5 | 38.5 | 45.0 | -11.6 [-43.3, +21.1] | 1.000 | — | 37.3 | 3 | 5 / 40.0 |
| US100 | 4H | bear | nextday | 13 | 69.2 | 69.2 | 73.6 | -6.9 [-38.3, +19.5] | 1.000 | — | 72.2 | 3 | 5 / 60.0 |
| US100 | D | bull | 5b | 6 | 66.7 | 66.7 | 46.7 | — | 1.000 | 62.5 | 51.4 | 1 | 5 / 60.0 |
| US100 | D | bull | 20b | 6 | 83.3 | 83.3 | 80.0 | — | 1.000 | 86.7 | 76.5 | 1 | 5 / 80.0 |
| US100 | D | bear | 5b | 1 | 100.0 | 100.0 | — | — | 1.000 | 35.0 | 71.4 | 4 | 1 / 100.0 |
| US100 | D | bear | 20b | 1 | 100.0 | 100.0 | — | — | 1.000 | 75.0 | 85.7 | 4 | 1 / 100.0 |
| US500 | 15m | bull | 5b | 1029 | 52.1 | 47.4 | 60.2 | -8.0 [-11.7, -4.0] | 0.003 | 54.4 | 57.5 | 4 | 560 / 52.1 |
| US500 | 15m | bull | 20b | 1029 | 72.9 | 70.6 | 78.4 | -5.4 [-8.4, -1.8] | 0.080 | 73.5 | 76.3 | 4 | 560 / 73.4 |
| US500 | 15m | bull | 50b | 1029 | 82.9 | 81.5 | 86.4 | -3.5 [-6.3, -0.9] | 0.650 | 83.3 | 85.1 | 4 | 560 / 82.5 |
| US500 | 15m | bull | sameday | 1029 | 79.9 | 78.4 | 83.5 | -3.6 [-6.6, -0.7] | 1.000 | — | 81.7 | 4 | 560 / 79.6 |
| US500 | 15m | bull | nextday | 1029 | 89.6 | 88.8 | 91.5 | -1.9 [-4.2, +0.2] | 1.000 | — | 90.8 | 4 | 560 / 88.6 |
| US500 | 15m | bear | 5b | 915 | 59.0 | 53.1 | 63.6 | -4.8 [-8.1, -0.6] | 0.853 | 53.0 | 61.3 | 3 | 503 / 59.2 |
| US500 | 15m | bear | 20b | 914 | 78.6 | 75.9 | 80.5 | -2.0 [-4.9, +1.0] | 1.000 | 74.2 | 79.1 | 3 | 503 / 79.7 |
| US500 | 15m | bear | 50b | 914 | 87.7 | 86.0 | 87.9 | -0.2 [-2.7, +2.4] | 1.000 | 84.5 | 87.1 | 3 | 503 / 88.9 |
| US500 | 15m | bear | sameday | 915 | 84.3 | 82.5 | 83.8 | +0.5 [-2.5, +3.6] | 1.000 | — | 83.3 | 3 | 503 / 86.3 |
| US500 | 15m | bear | nextday | 914 | 93.7 | 92.5 | 94.2 | -0.6 [-2.5, +1.2] | 1.000 | — | 93.3 | 3 | 503 / 94.0 |
| US500 | 1H | bull | 5b | 192 | 47.4 | 46.4 | 61.4 | -13.8 [-23.0, -4.6] | 0.199 | 52.2 | 58.6 | 4 | 78 / 46.2 |
| US500 | 1H | bull | 20b | 190 | 74.2 | 73.7 | 78.1 | -3.7 [-12.8, +5.1] | 1.000 | 77.1 | 76.6 | 4 | 78 / 64.1 |
| US500 | 1H | bull | 50b | 190 | 84.2 | 83.7 | 86.8 | -2.3 [-9.2, +5.6] | 1.000 | 83.7 | 84.9 | 4 | 78 / 76.9 |
| US500 | 1H | bull | sameday | 192 | 54.7 | 53.6 | 66.7 | -11.6 [-21.5, -1.8] | 1.000 | — | 63.9 | 4 | 78 / 53.8 |
| US500 | 1H | bull | nextday | 190 | 80.5 | 80.0 | 83.8 | -3.1 [-10.1, +4.2] | 1.000 | — | 81.3 | 4 | 78 / 70.5 |
| US500 | 1H | bear | 5b | 165 | 48.5 | 46.7 | 64.5 | -16.0 [-25.4, -6.8] | 0.047 | 49.5 | 58.5 | 4 | 54 / 44.4 |
| US500 | 1H | bear | 20b | 165 | 76.4 | 73.9 | 83.4 | -7.0 [-14.0, -0.7] | 1.000 | 75.4 | 78.1 | 4 | 54 / 70.4 |
| US500 | 1H | bear | 50b | 162 | 85.8 | 84.0 | 91.2 | -5.4 [-11.1, -0.0] | 1.000 | 85.6 | 88.0 | 4 | 52 / 76.9 |
| US500 | 1H | bear | sameday | 165 | 66.1 | 63.6 | 67.3 | -1.2 [-9.2, +6.8] | 1.000 | — | 63.0 | 4 | 54 / 63.0 |
| US500 | 1H | bear | nextday | 165 | 82.4 | 80.6 | 88.7 | -6.3 [-12.6, -0.1] | 1.000 | — | 84.1 | 4 | 54 / 75.9 |
| US500 | 4H | bull | 5b | 40 | 62.5 | 62.5 | 60.1 | -0.6 [-18.9, +17.9] | 1.000 | 59.2 | 57.9 | 2 | 11 / 36.4 |
| US500 | 4H | bull | 20b | 40 | 77.5 | 77.5 | 79.3 | -3.6 [-22.4, +14.2] | 1.000 | 78.2 | 77.5 | 2 | 11 / 54.5 |
| US500 | 4H | bull | 50b | 39 | 76.9 | 76.9 | 79.9 | -4.9 [-23.9, +13.6] | 1.000 | 86.0 | 77.5 | 2 | 11 / 54.5 |
| US500 | 4H | bull | sameday | 41 | 48.8 | 48.8 | 40.0 | +4.8 [-13.3, +22.1] | 1.000 | — | 39.7 | 2 | 11 / 36.4 |
| US500 | 4H | bull | nextday | 40 | 72.5 | 72.5 | 68.6 | +1.7 [-16.1, +19.4] | 1.000 | — | 65.6 | 2 | 11 / 54.5 |
| US500 | 4H | bear | 5b | 36 | 55.6 | 55.6 | 63.0 | -7.5 [-26.7, +11.1] | 1.000 | 53.5 | 58.1 | 3 | 6 / 50.0 |
| US500 | 4H | bear | 20b | 36 | 75.0 | 75.0 | 84.4 | -10.1 [-27.6, +6.4] | 1.000 | 73.8 | 82.6 | 3 | 6 / 83.3 |
| US500 | 4H | bear | 50b | 36 | 75.0 | 75.0 | 82.2 | -7.2 [-24.7, +10.3] | 1.000 | 85.1 | 82.5 | 3 | 6 / 83.3 |
| US500 | 4H | bear | sameday | 36 | 47.2 | 47.2 | 35.8 | +11.5 [-6.4, +28.1] | 1.000 | — | 38.2 | 3 | 6 / 50.0 |
| US500 | 4H | bear | nextday | 36 | 66.7 | 66.7 | 73.1 | -6.4 [-25.4, +10.5] | 1.000 | — | 70.7 | 3 | 6 / 83.3 |
| US500 | D | bull | 5b | 4 | 0.0 | 0.0 | 72.2 | — | 1.000 | 75.0 | 52.5 | 8 | 1 / 0.0 |
| US500 | D | bull | 20b | 4 | 25.0 | 25.0 | 100.0 | — | 1.000 | 87.5 | 68.3 | 8 | 1 / 0.0 |
| US500 | D | bear | 5b | 4 | 50.0 | 50.0 | 100.0 | — | 1.000 | 67.5 | 87.5 | 3 | 3 / 33.3 |
| US500 | D | bear | 20b | 3 | 66.7 | 66.7 | 100.0 | — | 1.000 | 78.3 | 90.5 | 9.5 | 3 / 66.7 |


## Revisit vs opposite extreme (scan window: 200 bars 15m, 60 1H, 20 4H/D)
| inst | TF | dir | group | N | open first % | opposite extreme first % | same bar % |
|---|---|---|---|---|---|---|---|
| US100 | 15m | bull | TOL | 968 | 24.8 | 69.1 | 6.1 |
| US100 | 15m | bull | WICK | 5154 | 20.3 | 60.0 | 19.8 |
| US100 | 15m | bear | TOL | 812 | 23.2 | 68.8 | 8.0 |
| US100 | 15m | bear | WICK | 4821 | 20.8 | 56.1 | 23.1 |
| US100 | 1H | bull | TOL | 170 | 20.6 | 74.7 | 4.1 |
| US100 | 1H | bull | WICK | 1133 | 16.6 | 62.9 | 20.5 |
| US100 | 1H | bear | TOL | 125 | 26.4 | 64.0 | 9.6 |
| US100 | 1H | bear | WICK | 1035 | 21.6 | 55.7 | 22.6 |
| US100 | 4H | bull | TOL | 35 | 22.9 | 74.3 | 2.9 |
| US100 | 4H | bull | WICK | 342 | 19.6 | 62.0 | 18.4 |
| US100 | 4H | bear | TOL | 13 | 15.4 | 76.9 | 7.7 |
| US100 | 4H | bear | WICK | 253 | 20.6 | 54.2 | 25.3 |
| US100 | D | bull | TOL | 6 | 16.7 | 50.0 | 33.3 |
| US100 | D | bull | WICK | 67 | 19.4 | 59.7 | 19.4 |
| US100 | D | bear | TOL | 1 | 0.0 | 100.0 | 0.0 |
| US100 | D | bear | WICK | 51 | 37.3 | 47.1 | 15.7 |
| US500 | 15m | bull | TOL | 1029 | 23.9 | 68.0 | 8.1 |
| US500 | 15m | bull | WICK | 5073 | 21.1 | 59.4 | 19.5 |
| US500 | 15m | bear | TOL | 915 | 26.4 | 65.0 | 8.5 |
| US500 | 15m | bear | WICK | 4753 | 22.7 | 54.9 | 22.4 |
| US500 | 1H | bull | TOL | 192 | 21.4 | 73.4 | 5.2 |
| US500 | 1H | bull | WICK | 1129 | 20.2 | 59.5 | 20.3 |
| US500 | 1H | bear | TOL | 165 | 25.5 | 66.1 | 8.5 |
| US500 | 1H | bear | WICK | 1005 | 21.8 | 52.9 | 25.3 |
| US500 | 4H | bull | TOL | 41 | 19.5 | 73.2 | 7.3 |
| US500 | 4H | bull | WICK | 349 | 18.9 | 61.9 | 18.6 |
| US500 | 4H | bear | TOL | 36 | 27.8 | 69.4 | 2.8 |
| US500 | 4H | bear | WICK | 253 | 25.3 | 51.8 | 22.9 |
| US500 | D | bull | TOL | 4 | 0.0 | 100.0 | 0.0 |
| US500 | D | bull | WICK | 74 | 17.6 | 52.7 | 28.4 |
| US500 | D | bear | TOL | 4 | 0.0 | 75.0 | 25.0 |
| US500 | D | bear | WICK | 50 | 26.0 | 52.0 | 22.0 |


## Killzones (15m / 1H, 20-bar revisit; control column is unmatched, descriptive)
| inst | TF | dir | killzone | N no-wick | revisit 20b % | N wick ctrl | ctrl revisit 20b % (unmatched) |
|---|---|---|---|---|---|---|---|
| US100 | 15m | bull | Asia | 188 | 73.9 | 885 | 78.6 |
| US100 | 15m | bull | London | 136 | 68.4 | 781 | 83.5 |
| US100 | 15m | bull | NYAM | 136 | 82.4 | 771 | 86.9 |
| US100 | 15m | bull | NYPM | 106 | 63.2 | 517 | 76.0 |
| US100 | 15m | bull | other | 402 | 72.4 | 2196 | 80.1 |
| US100 | 15m | bear | Asia | 152 | 69.1 | 838 | 84.2 |
| US100 | 15m | bear | London | 110 | 78.2 | 690 | 86.1 |
| US100 | 15m | bear | NYAM | 123 | 79.7 | 719 | 87.8 |
| US100 | 15m | bear | NYPM | 68 | 79.4 | 590 | 84.2 |
| US100 | 15m | bear | other | 359 | 78.0 | 1981 | 85.6 |
| US100 | 1H | bull | Asia | 25 | 96.0 | 135 | 82.2 |
| US100 | 1H | bull | London | 32 | 90.6 | 172 | 83.1 |
| US100 | 1H | bull | NYAM | 17 | 52.9 | 195 | 77.9 |
| US100 | 1H | bull | NYPM | 14 | 57.1 | 104 | 77.9 |
| US100 | 1H | bull | other | 81 | 72.8 | 524 | 80.9 |
| US100 | 1H | bear | Asia | 28 | 78.6 | 136 | 88.2 |
| US100 | 1H | bear | London | 17 | 88.2 | 156 | 88.5 |
| US100 | 1H | bear | NYAM | 15 | 66.7 | 157 | 82.8 |
| US100 | 1H | bear | NYPM | 12 | 83.3 | 111 | 83.8 |
| US100 | 1H | bear | other | 52 | 75.0 | 472 | 85.2 |
| US500 | 15m | bull | Asia | 201 | 69.2 | 806 | 81.3 |
| US500 | 15m | bull | London | 127 | 71.7 | 822 | 83.7 |
| US500 | 15m | bull | NYAM | 144 | 81.2 | 759 | 86.0 |
| US500 | 15m | bull | NYPM | 120 | 64.2 | 490 | 77.1 |
| US500 | 15m | bull | other | 437 | 74.6 | 2192 | 81.7 |
| US500 | 15m | bear | Asia | 186 | 82.3 | 764 | 83.1 |
| US500 | 15m | bear | London | 125 | 80.0 | 705 | 85.7 |
| US500 | 15m | bear | NYAM | 121 | 84.3 | 734 | 86.2 |
| US500 | 15m | bear | NYPM | 69 | 62.3 | 593 | 82.3 |
| US500 | 15m | bear | other | 413 | 77.5 | 1954 | 85.6 |
| US500 | 1H | bull | Asia | 27 | 77.8 | 126 | 86.5 |
| US500 | 1H | bull | London | 28 | 78.6 | 185 | 83.8 |
| US500 | 1H | bull | NYAM | 22 | 68.2 | 210 | 82.4 |
| US500 | 1H | bull | NYPM | 29 | 72.4 | 106 | 81.1 |
| US500 | 1H | bull | other | 84 | 73.8 | 498 | 81.1 |
| US500 | 1H | bear | Asia | 25 | 88.0 | 118 | 88.1 |
| US500 | 1H | bear | London | 24 | 87.5 | 157 | 89.2 |
| US500 | 1H | bear | NYAM | 21 | 71.4 | 174 | 79.9 |
| US500 | 1H | bear | NYPM | 13 | 69.2 | 115 | 88.7 |
| US500 | 1H | bear | other | 82 | 72.0 | 438 | 86.1 |


## Deviations / caveats (disclosed)
- Median bars-to-revisit is computed over revisits within the full scan window (200/60/20/20 bars), not only the 50-bar horizon. Nearly every cell gives 3–4 bars, so a revisit, when it happens, happens fast.
- Null (b) is computed only for bar horizons (not same/next day). Daily-cell CIs are absent because N ≤ 6.
- Matched baseline drops no-wick candles in bins without a control (count in `results_cells.csv: dropped`, ≤ 10 per cell).
- Levels on BID; sweep threshold = candle median spread (ASK−BID). The same-bar case in the ordering table cannot be resolved without 1m sequencing (not done).
- Same burned window as all prior HERMES-X work: any result here is hypothesis-generating only.

## Follow-up hypotheses (ICT terms; each falsifiable, each with its baseline; all need fresh / held-out data to confirm)
1. **H-NW1 Displacement + naked open as draw on liquidity.** A no-wick 15m candle with body ≥ 1.5 ATR (displacement) that leaves an FVG gets its open revisited within the same session *more* often than matched displacement candles with a wick. Falsified if diff ≤ 0 (cluster CI). Baseline: (a) matched on body/ATR, and (c). (The current result suggests the opposite for ordinary candles; this tests whether displacement changes the sign.)
2. **H-NW2 FVG left by the no-wick candle.** When the no-wick candle creates an FVG, the FVG midpoint (CE) is reached before the open in ≥ 60% of revisits. Falsified if CE-first ≤ the rate for FVGs from with-wick candles of the same size.
3. **H-NW3 Premium/discount of the dealing range.** A bullish no-wick candle forming in *discount* (below the 50% of the prior-day / Asia range) has a lower 20-bar open-revisit rate than one in premium. Falsified if discount − premium ≥ 0. Baseline: the same split for matched controls (difference-in-differences).
4. **H-NW4 True-day opening price (00:00 NY) / NY open 09:30.** A daily candle (00:00-NY true day) whose open == low/high is revisited before 16:00 less often than the matched day open with a wick. Falsified by diff ≥ 0. Needs a longer *unburned* sample (daily N is tiny here).
5. **H-NW5 Daily no-wick open: next day vs next week.** The open of a no-wick daily candle is revisited within the next week in ≥ X% (set from the (c) distance baseline + 5 pp). Falsified if within the distance baseline ± CI. Requires multi-year data outside the burned window.
6. **H-NW6 Continuation-first structure.** After a no-wick candle, the opposite extreme is taken before the open revisit more often than for matched controls (here 64–75% vs 53–63%, but with same-bar ambiguity). Falsified if the gap vanishes once same-bar cases are resolved on 1m. Baseline: matched controls with 1m sequencing.
7. **H-NW7 Killzone conditioning.** No-wick candles printed at the NY AM open (07:00–10:00) have a higher same-session open-revisit rate than London/Asia ones, beyond what their ATR distance predicts. Falsified if the killzone effect disappears in a logistic model with distance/ATR as covariate.
8. **H-NW8 Cost-aware "fade to the open" (only as a pre-declared rule).** Example rule declared before any R is computed: after a 15m TOL no-wick bull candle in NY AM, limit sell at close + 0.25 ATR, target = candle open, stop = 1 ATR beyond entry, exit at 15:59 NY, costs = pinned spread+slip on ASK/BID. Falsified if mean R ≤ 0 net of costs on held-out data. Baseline: the same rule on matched with-wick candles and random-time entries. (Given finding 2, the prior is negative.)
9. **H-NW9 Sweep-and-reverse at the naked open (Turtle-soup).** When the naked open *is* swept, price closes back above it (bull) within 3 bars more often than at matched with-wick opens. Falsified if diff ≤ 0. This tests whether the open behaves as liquidity (stop-run) rather than a plain level.
10. **H-NW10 Weekly analogue.** The Sunday-open (weekly) candle with open == low/high gets its open revisited within the week less often than distance predicts. Needs years of data; falsified if the rate is inside the (c) band.

---
# ADDENDUM 1 RESULTS (2026-10-12): in-sample burned exploration, prereg Addendum 1 (69597c4)

Code `addendum1.py` (~60 s, seed 20261012). Outputs: `add1_timing.csv`, `add1_pd_did.csv`, `add1_opens.csv`, `add1_weekly.csv`, `survival_15m.png`, `survival_1H.png`.

## A. Timing to revisit / sweep
Controls are reweighted to the no-wick body×range bins. Bars are counted after the candle close. Minutes are at 1m resolution from the close; `>X` = not reached within the scan.
Every N < 30 cell is **INSUFFICIENT**: all D cells, 4H bear US100.

| inst | TF | dir | group | N | rev p25/p50/p75/p90 bars | ≤1 / 3 / 5 / 10 / 20 / 50 bars % | never % | rev p25/p50/p75/p90 min (1m) | sweep p50/p90 min (1m) |
|---|---|---|---|---|---|---|---|---|---|
| US100 | 15m | bull | no-wick | 964 | 2/5/23/132 | 20.3 / 40.6 / 50.6 / 63.3 / 72.5 / 83.8 | 7.9 | 20/77/364/>3000 | 83/>3000 |
| US100 | 15m | bull | control(w) | 5114 | 1/4/16/89 | 25.6 / 48.2 / 59.0 / 69.7 / 77.2 / 86.2 | 7.1 | 15/51/276/2341 | 54/2736 |
| US100 | 15m | bear | no-wick | 804 | 2/4/18/87 | 22.5 / 43.9 / 55.1 / 67.2 / 76.6 / 85.3 | 5.8 | 18/61/298/1982 | 68/2299 |
| US100 | 15m | bear | control(w) | 4789 | 1/3/13/89 | 27.9 / 50.7 / 60.5 / 72.8 / 80.1 / 87.1 | 5.4 | 13/46/211/2301 | 51/2459 |
| US100 | 1H | bull | no-wick | 169 | 2/5/18/>60 | 15.4 / 43.2 / 53.3 / 66.3 / 76.3 / 87.0 | 11.8 | 102/288/1513/>3600 | 302/>3600 |
| US100 | 1H | bull | control(w) | 1125 | 2/4/14/>60 | 23.2 / 45.5 / 56.3 / 69.1 / 79.3 / 87.3 | 11.8 | 69/251/926/>3600 | 267/>3600 |
| US100 | 1H | bear | no-wick | 122 | 1/4/18/>60 | 25.4 / 47.5 / 55.7 / 64.8 / 77.9 / 86.9 | 10.7 | 72/228/1363/>3600 | 252/>3600 |
| US100 | 1H | bear | control(w) | 1020 | 1/3/12/48 | 32.9 / 53.6 / 62.4 / 73.4 / 82.3 / 90.6 | 7.8 | 42/162/904/>3600 | 167/>3600 |
| US100 | 4H | bull | no-wick | 35 | 1/4/14/>20 | 25.7 / 48.6 / 60.0 / 74.3 / 80.0 / 80.0 | 20.0 | 205/845/3904/>4800 | 845/>4800 |
| US100 | 4H | bull | control(w) | 338 | 2/3/>20/>20 | 19.1 / 52.5 / 58.9 / 64.8 / 71.1 / 71.1 | 28.9 | 251/572/>4800/>4800 | 572/>4800 |
| US100 | 4H | bear | no-wick INSUFFICIENT | 13 | 3/5/>20/>20 | 15.4 / 38.5 / 53.8 / 69.2 / 69.2 / 69.2 | 30.8 | 513/1298/>4800/>4800 | 1312/>4800 |
| US100 | 4H | bear | control(w) | 247 | 1/3/10/>20 | 31.4 / 52.2 / 65.0 / 75.8 / 84.8 / 84.8 | 15.2 | 176/606/3901/>4800 | 606/>4800 |
| US100 | D | bull | no-wick INSUFFICIENT | 6 | 1/1/9/>20 | 50.0 / 66.7 / 66.7 / 83.3 / 83.3 / 83.3 | 16.7 | 1016/1120/18396/>28800 | 1128/>28800 |
| US100 | D | bull | control(w) | 63 | 2/3/>20/>20 | 14.3 / 50.0 / 50.0 / 71.4 / 71.4 / 71.4 | 28.6 | 2715/3883/>28800/>28800 | 3883/>28800 |
| US100 | D | bear | no-wick INSUFFICIENT | 1 | 4/4/4/4 | 0.0 / 0.0 / 100.0 / 100.0 / 100.0 / 100.0 | 0.0 | 7695/7695/7695/7695 | 7699/7699 |
| US100 | D | bear | control(w) | 49 | 1/1/1/1 | — / — / — / — / — / — | — | 61/61/61/61 | 61/61 |
| US500 | 15m | bull | no-wick | 1026 | 2/5/25/153 | 22.3 / 42.8 / 52.0 / 63.7 / 72.9 / 82.9 | 8.8 | 18/70/400/>3000 | 91/>3000 |
| US500 | 15m | bull | control(w) | 5031 | 1/3/15/87 | 27.0 / 50.0 / 60.2 / 70.6 / 78.4 / 86.5 | 6.9 | 14/46/242/1935 | 64/2880 |
| US500 | 15m | bear | no-wick | 909 | 1/4/14/72 | 26.6 / 49.0 / 59.1 / 71.1 / 78.8 / 87.8 | 5.2 | 14/49/230/1517 | 68/2019 |
| US500 | 15m | bear | control(w) | 4713 | 1/3/12/73 | 31.0 / 54.3 / 63.5 / 73.6 / 80.4 / 87.8 | 4.4 | 11/38/200/1413 | 49/1583 |
| US500 | 1H | bull | no-wick | 190 | 2/6/22/>60 | 17.4 / 36.8 / 47.9 / 61.1 / 74.2 / 84.2 | 15.3 | 116/401/2021/>3600 | 418/>3600 |
| US500 | 1H | bull | control(w) | 1120 | 1/3/16/>60 | 26.9 / 50.4 / 60.4 / 70.9 / 77.1 / 86.8 | 12.7 | 58/195/1317/>3600 | 211/>3600 |
| US500 | 1H | bear | no-wick | 161 | 2/6/17/>60 | 24.8 / 43.5 / 49.1 / 66.5 / 77.6 / 86.3 | 11.8 | 61/332/1156/>3600 | 345/>3600 |
| US500 | 1H | bear | control(w) | 993 | 1/3/12/42 | 32.2 / 56.3 / 64.7 / 73.0 / 83.4 / 91.3 | 7.5 | 45/128/845/>3600 | 142/>3600 |
| US500 | 4H | bull | no-wick | 40 | 2/4/10/>20 | 22.5 / 47.5 / 62.5 / 75.0 / 77.5 / 77.5 | 22.5 | 261/773/4166/>4800 | 773/>4800 |
| US500 | 4H | bull | control(w) | 344 | 2/3/14/>20 | 23.9 / 52.1 / 61.2 / 71.2 / 79.8 / 79.8 | 20.2 | 271/769/4117/>4800 | 781/>4800 |
| US500 | 4H | bear | no-wick | 36 | 2/4/19/>20 | 13.9 / 44.4 / 55.6 / 69.4 / 75.0 / 75.0 | 25.0 | 294/930/>4800/>4800 | 931/>4800 |
| US500 | 4H | bear | control(w) | 247 | 2/4/12/>20 | 25.0 / 43.0 / 62.5 / 73.5 / 83.7 / 83.7 | 16.3 | 290/1089/4126/>4800 | 1119/>4800 |
| US500 | D | bull | no-wick INSUFFICIENT | 4 | 8/>20/>20/>20 | 0.0 / 0.0 / 0.0 / 25.0 / 25.0 / 25.0 | 75.0 | 16022/>28800/>28800/>28800 | >28800/>28800 |
| US500 | D | bull | control(w) | 72 | 3/3/10/12 | 11.1 / 72.2 / 72.2 / 83.3 / 100.0 / 100.0 | 0.0 | 4001/6051/19915/22992 | 6051/22992 |
| US500 | D | bear | no-wick INSUFFICIENT | 4 | 1/3/18/>20 | 25.0 / 50.0 / 50.0 / 50.0 / 75.0 / 75.0 | 25.0 | 787/3880/>28800/>28800 | 3880/>28800 |
| US500 | D | bear | control(w) | 45 | 1/2/2/3 | 41.7 / 100.0 / 100.0 / 100.0 / 100.0 / 100.0 | 0.0 | 929/2736/5314/6187 | 2736/6203 |

**Read:**
- On 15m and 1H the no-wick open is revisited **later** than the matched control: median 1m time 61–77 vs 46–51 min (US100 15m), 49–70 vs 38–46 min (US500 15m), 228–401 vs 128–251 min (1H). At 1 bar, 15–27% vs 23–33% have revisited.
- By 20–50 bars the curves converge, and the never-revisited share in the scan is similar (5–15%).
- Sweep times trail revisit times by only a few minutes.
- Plots: `research/nowick/survival_15m.png`, `research/nowick/survival_1H.png`.

## B. Premium / discount DiD (Q4)
Zone A = aligned (bull in discount / bear in premium of the prior-20-session range); zone B = the opposite half. DiD = (no-wick − matched control)_A − (same)_B. Prediction: DiD < 0.

| inst | TF | dir | horizon | N no-wick A / B | revisit % A / B | matched diff pp A / B | DiD pp [95% CI] | Holm p |
|---|---|---|---|---|---|---|---|---|
| US100 | 15m | bull | 20b | 268 / 626 | 73.9 / 72.0 | -4.6 / -5.3 | +0.8 [-6.4, +8.0] | 1.000 |
| US100 | 15m | bull | sameday | 268 / 626 | 81.0 / 80.8 | -0.3 / -2.8 | +2.4 [-4.0, +8.6] | 1.000 |
| US100 | 15m | bear | 20b | 537 / 217 | 75.2 / 80.6 | -2.7 / -1.0 | -1.6 [-10.3, +5.7] | 1.000 |
| US100 | 15m | bear | sameday | 537 / 217 | 82.9 / 84.3 | +2.5 / -0.3 | +2.8 [-4.9, +8.6] | 1.000 |
| US100 | 1H | bull | 20b | 50 / 107 | 76.0 / 75.7 | -4.7 / -3.1 | -1.6 [-19.1, +17.2] | 1.000 |
| US100 | 1H | bull | sameday | 50 / 108 | 66.0 / 68.5 | -1.4 / +1.0 | -2.4 [-21.2, +17.3] | 1.000 |
| US100 | 1H | bear | 20b INSUFFICIENT | 89 / 26 | 77.5 / 80.8 | -5.6 / +1.2 | -6.7 [-22.0, +10.3] | 1.000 |
| US100 | 1H | bear | sameday INSUFFICIENT | 90 / 26 | 65.6 / 65.4 | -2.9 / +3.0 | -5.8 [-31.6, +21.5] | 1.000 |
| US100 | 4H | bull | 20b INSUFFICIENT | 8 / 26 | 100.0 / 73.1 | +24.0 / +1.5 | +22.5 [-18.7, +62.0] | 1.000 |
| US100 | 4H | bull | sameday INSUFFICIENT | 8 / 26 | 37.5 / 57.7 | -1.2 / +1.1 | -2.3 [-69.6, +53.7] | 1.000 |
| US100 | 4H | bear | 20b INSUFFICIENT | 10 / 3 | 60.0 / 100.0 | -23.8 / +2.2 | -26.0 [-64.5, +12.9] | 1.000 |
| US100 | 4H | bear | sameday INSUFFICIENT | 10 / 3 | 40.0 / 33.3 | -5.6 / -24.4 | +18.8 [-103.1, +105.8] | 1.000 |
| US500 | 15m | bull | 20b | 246 / 679 | 71.5 / 72.6 | -3.5 / -7.7 | +4.2 [-3.6, +12.1] | 1.000 |
| US500 | 15m | bull | sameday | 246 / 679 | 80.5 / 78.9 | -0.6 / -5.6 | +5.0 [-1.9, +11.7] | 1.000 |
| US500 | 15m | bear | 20b | 664 / 200 | 77.3 / 81.0 | -3.3 / +1.5 | -4.8 [-12.9, +3.4] | 1.000 |
| US500 | 15m | bear | sameday | 665 / 200 | 84.7 / 82.5 | +1.3 / -0.5 | +1.8 [-5.2, +9.4] | 1.000 |
| US500 | 1H | bull | 20b | 54 / 123 | 70.4 / 74.0 | -7.7 / -3.2 | -4.6 [-25.0, +18.4] | 1.000 |
| US500 | 1H | bull | sameday | 54 / 125 | 57.4 / 52.8 | -13.5 / -14.8 | +1.2 [-19.7, +25.2] | 1.000 |
| US500 | 1H | bear | 20b | 124 / 33 | 76.6 / 81.8 | -4.1 / -5.9 | +1.7 [-12.8, +17.2] | 1.000 |
| US500 | 1H | bear | sameday | 124 / 33 | 67.7 / 63.6 | +3.5 / -9.9 | +13.4 [-8.9, +34.6] | 1.000 |
| US500 | 4H | bull | 20b INSUFFICIENT | 15 / 24 | 80.0 / 75.0 | -11.4 / +6.5 | -17.9 [-55.9, +20.4] | 1.000 |
| US500 | 4H | bull | sameday INSUFFICIENT | 15 / 25 | 53.3 / 48.0 | +6.5 / +9.9 | -3.4 [-47.9, +38.5] | 1.000 |
| US500 | 4H | bear | 20b INSUFFICIENT | 29 / 5 | 75.9 / 80.0 | -4.0 / -13.3 | +9.3 [-32.6, +60.6] | 1.000 |
| US500 | 4H | bear | sameday INSUFFICIENT | 29 / 5 | 48.3 / 40.0 | +9.3 / +12.5 | -3.2 [-74.4, +67.9] | 1.000 |

Family summary (revisit and sweep cells together):

| family | cells | min raw p | min Holm p | share DiD < 0 |
|---|---|---|---|---|
| 20sess_OTE | 48.0 | 0.021 | 1.000 | 46% |
| curday_aligned | 48.0 | 0.010 | 0.490 | 42% |
| primary | 48.0 | 0.100 | 1.000 | 54% |

**Read:** the Q4 hypothesis is **not supported**.
- No cell survives Holm in any family; the minimum Holm p in the primary family is 1.0.
- DiD signs split about 50/50, and the 15m CIs straddle 0 by ±6–8 pp.
- Sweep cells and the alternative definitions (current-day range, OTE band) look the same; all are in `add1_pd_did.csv`.

## C. Daily / weekly / true-day / 09:30 opens (Q5)

### (i) Daily no-wick candles (17:00 roll)

| inst | dir | group | horizon | N | revisit % | sweep % | status |
|---|---|---|---|---|---|---|---|
| US100 | bull | TOL | 1d | 6 | 50.0 | 50.0 | INSUFFICIENT |
| US100 | bull | TOL | 5d | 6 | 66.7 | 66.7 | INSUFFICIENT |
| US100 | bull | TOL | 20d | 6 | 83.3 | 83.3 | INSUFFICIENT |
| US100 | bull | WICK | 1d | 66 | 34.8 | 34.8 | ok |
| US100 | bull | WICK | 5d | 65 | 63.1 | 63.1 | ok |
| US100 | bull | WICK | 20d | 62 | 83.9 | 83.9 | ok |
| US100 | bear | TOL | 1d | 1 | 0.0 | 0.0 | INSUFFICIENT |
| US100 | bear | TOL | 5d | 1 | 100.0 | 100.0 | INSUFFICIENT |
| US100 | bear | TOL | 20d | 1 | 100.0 | 100.0 | INSUFFICIENT |
| US100 | bear | WICK | 1d | 51 | 49.0 | 49.0 | ok |
| US100 | bear | WICK | 5d | 50 | 84.0 | 84.0 | ok |
| US100 | bear | WICK | 20d | 49 | 95.9 | 95.9 | ok |
| US500 | bull | TOL | 1d | 4 | 0.0 | 0.0 | INSUFFICIENT |
| US500 | bull | TOL | 5d | 4 | 0.0 | 0.0 | INSUFFICIENT |
| US500 | bull | TOL | 20d | 4 | 25.0 | 25.0 | INSUFFICIENT |
| US500 | bull | WICK | 1d | 73 | 42.5 | 42.5 | ok |
| US500 | bull | WICK | 5d | 73 | 69.9 | 69.9 | ok |
| US500 | bull | WICK | 20d | 70 | 85.7 | 85.7 | ok |
| US500 | bear | TOL | 1d | 4 | 25.0 | 25.0 | INSUFFICIENT |
| US500 | bear | TOL | 5d | 4 | 50.0 | 50.0 | INSUFFICIENT |
| US500 | bear | TOL | 20d | 3 | 66.7 | 66.7 | INSUFFICIENT |
| US500 | bear | WICK | 1d | 50 | 40.0 | 40.0 | ok |
| US500 | bear | WICK | 5d | 49 | 75.5 | 75.5 | ok |
| US500 | bear | WICK | 20d | 44 | 95.5 | 95.5 | ok |

### (ii) Weekly no-wick candles

- US100: 0 no-wick weeks; US500: 1 (it needs 14 prior weeks for ATR14, leaving about 42 usable weeks).
- **INSUFFICIENT**. US500 detail: TOL N=1 (revisited within 4 weeks), WICK N=8.

### (iii) 60-min candles opening at 00:00 and 09:30 NY vs 60 random clock times

Revisit or sweep of the candle's open within 360 min after its close (1m BID). The rank is the percentile among the 60 baseline clock times.

| inst | clock | subset | N | revisit % | sweep % | median min to touch | baseline revisit p5/p50/p95 % | rank of revisit | rank of median time |
|---|---|---|---|---|---|---|---|---|---|
| US100 | 00:00 | all | 281 | 74.7 | 73.3 | 31.5 | 65.2/77.8/86.8 | 20% | 38% |
| US100 | 09:30 | all | 281 | 51.6 | 50.2 | 28 | 65.2/77.8/86.8 | 0% | 18% |
| US100 | 00:00 | nowick INSUFFICIENT | 11 | 63.6 | 63.6 | 88 | 33.0/69.0/84.8 | 42% | 40% |
| US100 | 09:30 | nowick INSUFFICIENT | 14 | 35.7 | 35.7 | 72 | 33.0/69.0/84.8 | 7% | 20% |
| US500 | 00:00 | all | 278 | 83.5 | 78.4 | 31 | 64.2/80.9/88.6 | 75% | 57% |
| US500 | 09:30 | all | 282 | 58.5 | 57.1 | 21 | 64.2/80.9/88.6 | 2% | 13% |
| US500 | 00:00 | nowick INSUFFICIENT | 13 | 69.2 | 61.5 | 32 | 28.3/60.8/91.1 | 63% | 5% |
| US500 | 09:30 | nowick INSUFFICIENT | 14 | 28.6 | 28.6 | 76.5 | 28.3/60.8/91.1 | 5% | 37% |

**Read:**
- The **09:30 open is revisited least of all clock times** (US100 51.6%, rank 0th; US500 58.5%, rank 2nd vs baseline median 78–81%). It is in absolute points, not ATR-normalized: the 09:30 hour is the largest-range hour, so its close sits farther from its open. This is a volatility effect, not evidence of a special 'unfilled' open.
- The **00:00 true-day open** is unremarkable (rank 20th US100, 75th US500).
- No-wick subsets are N = 11–14: **INSUFFICIENT**.

### Power note
- Detecting a 10 pp difference (75% vs 85%) at 80% power, two-sided α = 0.05, needs about **250 events per arm**.
- Observed frequencies in this window:
  - daily no-wick: about 1–6 per direction per instrument-year, so roughly **40–250 instrument-years**;
  - weekly no-wick: about 0–1 per instrument-year, so effectively unreachable;
  - no-wick 00:00 / 09:30 hours: about 11–14 per instrument-year, so roughly **18–23 instrument-years** per clock time.
- Confirmation needs fresh multi-year data: new instruments DAX/Dow/gold 2023+ once DATA's screening remediation passes, or the forward test. No sealed data was opened.

## Addendum 1 deviations (disclosed; no pre-registered definition changed)
- (A) Cells whose control bins contain no no-wick candle return NaN control rates (US100 D bear, N = 1). Already INSUFFICIENT.
- (A) Candles whose scan window runs past 2026-09-25 16:14 NY are excluded (censoring), so N is slightly below the main table.
- (B) The daily TF is excluded, as pre-registered. Cells with a zone N < 30 (all 4H, some 1H) are flagged INSUFFICIENT but kept in the Holm family as declared.
- (C-iii) A clock candle is used only if it has ≥ 30 of 60 1m bars and does not cross the 17:00 roll. Doji (close == open) are skipped (no direction).
- (C-ii) The weekly bar ATR14 needs 14 prior weeks, which shrinks the usable sample.
- `nowick.py` gained a weekly bar key (Sunday 17:00 NY roll, W-SUN periods on the +7h shift). Existing TF results are unchanged (re-verified: `results_cells.csv` is identical).

---
# ADDENDUM 2 RESULTS (2026-10-12): lower-timeframe path into the revisit (prereg Addendum 2, 3beea5b)

In-sample burned exploration. Code `addendum2.py` (~25 s). Outputs: `add2_features.csv`, `add2_features_by_window.csv`, `add2_sequences.csv`, `add2_extras.csv`, `add2_killzones.csv`, `add2_events.csv.gz`, `example_{1,2,3}.png`.
Pooled over US100/US500 and both directions. Bull wording: the open lies below; bear is mirrored.

## Feature frequency (Holm within each comparison, 18 tests)

| TF | feature | TOL revisited % | (a) matched WICK revisited % | (a) diff pp [CI], Holm p | (b) TOL not revisited % | (b) diff pp [CI], Holm p |
|---|---|---|---|---|---|---|
| 15m | OPP | 70.2 (N 3357) | 80.6 (N 18325) | -10.3 [-12.3, -8.2], 0.000 | 93.6 (N 346) | -23.4 [-26.8, -19.9], 0.000 |
| 15m | MSS1 | 80.9 (N 3357) | 67.4 (N 18325) | +13.4 [+11.5, +15.5], 0.000 | 32.4 (N 346) | +48.5 [+43.6, +53.4], 0.000 |
| 15m | MSS5 | 30.5 (N 3357) | 24.0 (N 18325) | +6.5 [+4.2, +8.7], 0.000 | 1.2 (N 346) | +29.3 [+27.2, +31.5], 0.000 |
| 15m | DISP | 30.9 (N 3357) | 25.6 (N 18325) | +5.3 [+3.2, +7.4], 0.000 | 5.5 (N 346) | +25.4 [+21.9, +28.6], 0.000 |
| 15m | FVG1 | 86.6 (N 3357) | 83.2 (N 18325) | +3.4 [+1.9, +5.0], 0.000 | 94.8 (N 346) | -8.2 [-11.0, -4.9], 0.000 |
| 15m | FVG5 | 52.9 (N 3357) | 46.2 (N 18325) | +6.7 [+4.3, +9.1], 0.000 | 24.3 (N 346) | +28.6 [+23.9, +33.3], 0.000 |
| 15m | SWP5 | 83.2 (N 3357) | 81.6 (N 18325) | +1.6 [+0.1, +3.1], 0.168 | 92.8 (N 346) | -9.6 [-12.8, -5.9], 0.000 |
| 15m | SESS | 40.0 (N 3357) | 35.6 (N 18325) | +4.4 [+2.1, +6.6], 0.001 | 56.6 (N 346) | -16.6 [-24.6, -8.6], 0.000 |
| 15m | DRIFT | 5.2 (N 3357) | 5.4 (N 18325) | -0.2 [-1.0, +0.7], 1.000 | 2.0 (N 346) | +3.2 [+1.0, +4.8], 0.006 |
| 1H | OPP | 69.8 (N 533) | 79.8 (N 3735) | -10.0 [-14.9, -5.3], 0.000 | 90.8 (N 109) | -21.0 [-28.7, -12.4], 0.000 |
| 1H | MSS1 | 97.6 (N 533) | 91.8 (N 3735) | +5.7 [+4.0, +7.5], 0.000 | 69.7 (N 109) | +27.8 [+18.5, +36.7], 0.000 |
| 1H | MSS5 | 71.9 (N 533) | 54.2 (N 3735) | +17.7 [+12.4, +23.0], 0.000 | 19.3 (N 109) | +52.6 [+42.2, +61.5], 0.000 |
| 1H | DISP | 62.7 (N 533) | 48.0 (N 3735) | +14.7 [+8.7, +20.7], 0.000 | 24.8 (N 109) | +37.9 [+27.6, +48.0], 0.000 |
| 1H | FVG1 | 98.7 (N 533) | 96.0 (N 3735) | +2.7 [+1.6, +3.8], 0.000 | 100.0 (N 109) | -1.3 [-2.4, -0.5], 0.023 |
| 1H | FVG5 | 83.5 (N 533) | 76.1 (N 3735) | +7.4 [+3.3, +11.6], 0.003 | 86.2 (N 109) | -2.7 [-10.6, +5.5], 0.640 |
| 1H | SWP5 | 95.3 (N 533) | 96.2 (N 3735) | -0.9 [-3.1, +1.1], 1.000 | 99.1 (N 109) | -3.8 [-6.2, -0.9], 0.022 |
| 1H | SESS | 56.5 (N 533) | 53.6 (N 3735) | +2.9 [-2.9, +8.8], 1.000 | 78.9 (N 109) | -22.4 [-33.3, -10.5], 0.001 |
| 1H | DRIFT | 0.2 (N 533) | 0.8 (N 3735) | -0.6 [-1.1, -0.1], 0.062 | 0.0 (N 109) | +0.2 [+0.0, +0.6], 0.640 |

### Same comparison (a) stratified by window-length tertile (TOL-revisit tertiles)

| TF | tertile | group | N | OPP | MSS1 | MSS5 | DISP | FVG1 | FVG5 | SWP5 | SESS | DRIFT |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 15m | 0 | TOL | 1115 | 30.5 | 55.8 | 0.0 | 4.3 | 61.4 | 3.2 | 64.8 | 8.4 | 14.5 |
| 15m | 0 | WICK | 9201 | 55.9 | 35.4 | 0.0 | 2.2 | 58.4 | 3.2 | 66.8 | 12.5 | 12.9 |
| 15m | 1 | TOL | 1120 | 82.1 | 89.3 | 16.8 | 17.7 | 98.8 | 58.1 | 87.9 | 37.6 | 0.6 |
| 15m | 1 | WICK | 5182 | 94.2 | 81.6 | 13.5 | 16.1 | 98.5 | 55.3 | 86.6 | 36.2 | 0.8 |
| 15m | 2 | TOL | 1122 | 98.0 | 97.4 | 74.5 | 70.4 | 99.6 | 97.0 | 96.8 | 73.8 | 0.4 |
| 15m | 2 | WICK | 3942 | 99.0 | 95.7 | 71.8 | 71.1 | 99.5 | 96.6 | 96.5 | 68.2 | 0.3 |
| 1H | 0 | TOL | 177 | 31.1 | 94.9 | 44.1 | 27.7 | 96.0 | 53.7 | 90.4 | 20.9 | 0.6 |
| 1H | 0 | WICK | 1985 | 62.3 | 86.3 | 24.8 | 17.1 | 91.4 | 51.4 | 92.8 | 31.7 | 1.5 |
| 1H | 1 | TOL | 178 | 82.6 | 99.4 | 80.3 | 66.3 | 100.0 | 98.9 | 96.6 | 64.6 | 0.0 |
| 1H | 1 | WICK | 994 | 91.8 | 95.0 | 68.2 | 56.3 | 99.7 | 95.7 | 99.0 | 64.2 | 0.3 |
| 1H | 2 | TOL | 178 | 95.5 | 98.3 | 91.0 | 93.8 | 100.0 | 97.8 | 98.9 | 83.7 | 0.0 |
| 1H | 2 | WICK | 756 | 97.7 | 98.2 | 91.5 | 95.1 | 99.9 | 98.0 | 99.1 | 81.3 | 0.0 |

## Most common sequences (revisited events)

| TF | group | sequence | n | share % |
|---|---|---|---|---|
| 15m | TOL | SWEEP > FVG > MSS > REV | 1122 | 33.4 |
| 15m | TOL | SWEEP > FVG > MSS > DISP > REV | 514 | 15.3 |
| 15m | TOL | SWEEP > FVG > DISP > MSS > REV | 409 | 12.2 |
| 15m | TOL | SWEEP > MSS > FVG > REV | 290 | 8.6 |
| 15m | TOL | SWEEP > FVG > REV | 247 | 7.4 |
| 15m | WICK | SWEEP > FVG > MSS > REV | 4803 | 26.2 |
| 15m | WICK | SWEEP > FVG > REV | 2884 | 15.7 |
| 15m | WICK | SWEEP > REV | 2511 | 13.7 |
| 15m | WICK | DRIFT > REV | 1902 | 10.4 |
| 15m | WICK | SWEEP > FVG > MSS > DISP > REV | 1764 | 9.6 |
| 1H | TOL | SWEEP > FVG > MSS > DISP > REV | 146 | 27.4 |
| 1H | TOL | SWEEP > FVG > DISP > MSS > REV | 144 | 27.0 |
| 1H | TOL | SWEEP > FVG > MSS > REV | 126 | 23.6 |
| 1H | TOL | SWEEP > MSS > FVG > REV | 37 | 6.9 |
| 1H | TOL | SWEEP > MSS > FVG > DISP > REV | 22 | 4.1 |
| 1H | WICK | SWEEP > FVG > MSS > REV | 1209 | 32.4 |
| 1H | WICK | SWEEP > FVG > MSS > DISP > REV | 682 | 18.3 |
| 1H | WICK | SWEEP > FVG > DISP > MSS > REV | 628 | 16.8 |
| 1H | WICK | SWEEP > MSS > FVG > REV | 442 | 11.8 |
| 1H | WICK | SWEEP > FVG > REV | 224 | 6.0 |

## Descriptive extras

| TF | group | revisited | N | CE1 reached given FVG1 % | OB retest given DISP % | median window min |
|---|---|---|---|---|---|---|
| 15m | TOL | False | 346 | 96.0 | 52.6 | 52 |
| 15m | TOL | True | 3357 | 77.6 | 50.8 | 49 |
| 15m | WICK | True | 18325 | 71.8 | 52.0 | 21 |
| 1H | TOL | False | 109 | 95.4 | 48.1 | 186 |
| 1H | TOL | True | 533 | 88.4 | 53.3 | 197 |
| 1H | WICK | True | 3735 | 79.6 | 54.1 | 86 |

Killzone of the turn / revisit for TOL revisits: `add2_killzones.csv`. NY AM has the most revisits (15m: 716 of 3357; turns 610). The 'other' hours dominate overall (1244 / 1261).

## Read (honest)
1. **The common lower-timeframe path is the generic ICT reversal sequence.**
   - Sequence: sweep of the far side (candle extreme / 5m swing / session) > 1m FVG toward the open > 1m MSS > (5m displacement) > revisit.
   - `SWEEP > FVG > MSS > REV` is the modal sequence on 15m (33.4% of TOL revisits; 48.7% including the `> DISP` tail). On 1H, the three SWEEP > FVG > MSS/DISP variants cover 78%.
   - Only 5.2% (15m) / 0.2% (1H) of revisits are a straight drift with none of the features.
2. **But it is not specific to no-wick candles.** The matched wicked controls show the same modal sequence (15m 26.2%, 1H 32.4%) and the same feature mix.
   - The (a) differences are mostly significant after Holm, but they are dominated by **window length**: no-wick revisits take about 2× longer (median 49 vs 21 min on 15m).
   - Within window-length tertiles, most gaps shrink to ≤ 5 pp.
   - What survives stratification: no-wick revisits in short windows take the candle's opposite extreme **less** often (15m tertile 0: 30% vs 56%; 1H: 31% vs 62%) and show a 1m MSS **more** often (56% vs 35%; 95% vs 86%). In other words, the quick no-wick revisits are 'fail to extend, shift structure, return', not 'sweep the high, then return'.
3. **'Does the feature predict the revisit' (b) is largely mechanical.**
   - MSS toward the open (+49 pp on 15m), MSS5, DISP and FVG5 are much more frequent before revisits. But a move toward the open *is* what produces those features, so this is close to tautological. It is not a usable ex-ante signal: the feature is defined inside the window that ends at the revisit.
   - Not-revisited events show *more* far-side sweeps (OPP 94% vs 70%; SESS 57% vs 40%), i.e. continuation away from the open.
   - An ex-ante test would have to fix a decision time (e.g. the first 1m MSS after the close) and measure the subsequent revisit. Proposed as a follow-up.
4. **FVG CE retrace:** given a 1m FVG toward the open, its CE is reached before the revisit in 78% (15m) / 88% (1H) of no-wick revisits vs 72% / 80% for controls.
   - OB mid-body retest after displacement is about a coin flip (48–54%) in every group.

## Example charts (pre-declared selection: first 3 by date of 15m TOL revisits with the modal sequence `SWEEP > FVG > MSS > REV`, window 30–180 min)
- `research/nowick/example_1.png`, `research/nowick/example_2.png`, `research/nowick/example_3.png`: 1m BID candles with the no-wick candle shaded, open (dashed), opposite extreme (dotted), revisit (purple); the features found are listed in the title.

## Addendum 2 deviations (disclosed)
- Charts annotate the candle, open, extreme and revisit, and list the detected features in the title; individual MSS/FVG levels are not drawn.
- 5m bars are built with the main `bars()` (≥ 50% of 1m minutes present).
- No pre-registered definition changed.

## Follow-ups from Addendum 2
- **H-NW11 (ex-ante):** after a 15m no-wick candle, if a 1m MSS toward the open prints *before* the candle's opposite extreme is taken, the open is revisited within 20 bars more often than without it. Decision time = the MSS bar; baseline = matched wicked candles with the same trigger. Falsified if diff ≤ 0 on fresh data.
- **H-NW12:** for the 1m FVG toward the open, CE-first then revisit (78%) vs controls (72%), tested as a pre-declared entry at CE with the stop beyond the turn, cost-aware, on held-out data only.

# Addendum 3: H-NW11 illustrative equity curve (EXPLORATORY, IN-SAMPLE on the burned window, NOT EVIDENCE)
The rules are in PREREG.md Addendum 3 and were committed (c64e842) before any R was computed. Code: `addendum3.py`. Outputs: `add3_signals.csv`, `add3_trades_{halted,unhalted}.csv`, `add3_summary.csv` and `hnw11_equity.png`. It was run with /workspace/cb-venv/bin/python, because the system python has no matplotlib.

**Rules in short.**
- Events: TOL no-wick candles on 15m and 1H, US100 and US500.
- Entry: the first 1m BID close through the latest confirmed 1m swing, toward the open, before the far extreme is taken or the open is touched, within 20 TF bars.
- Stop: beyond the MSS swing plus the H016 buffer. A stop closer than 4× friction is widened to 10.2 / 4.88 pt.
- Target: the no-wick open.
- Time stop: 20 TF bars or the 17:00 NY day roll.
- Fills: correct-side BID/ASK with the DATA slippage floors.

**Headline: the rule loses money on the data it was derived from.**

| | trades | win rate | mean R [95% day-cluster CI] | final equity | return | max DD |
|---|---|---|---|---|---|---|
| All signals (no book) | 1557 | 47.5% | −0.196 [−0.254, −0.140] | – | – | – |
| Book, 5% DD halt | 69 | 63.8% | −0.138 [−0.388, 0.061] | $9,529 | −4.7% | 5.17%; **halted 2025-09-10 14:47 NY** |
| Book, unhalted | 1382 | 47.8% | −0.195 [−0.256, −0.137] | $2,548 | −74.5% | 74.7% |

**Split by instrument and timeframe (unhalted book).**

| | N | win | mean R [CI] |
|---|---|---|---|
| US100 15m | 545 | 51.6% | −0.134 [−0.211, −0.050] |
| US100 1H | 135 | 31.9% | −0.237 [−0.475, 0.017] |
| US500 15m | 544 | 51.1% | −0.218 [−0.288, −0.143] |
| US500 1H | 158 | 37.3% | −0.285 [−0.466, −0.103] |

The halted-book split is in `add3_summary.csv`. Every halted cell has N ≤ 28.

**Why it loses.**
- Average target hit +0.60 R (median +0.37 R), average stop −1.11 R. Time exits are 2%.
- The open is usually close to the entry relative to a structural stop. 42% of stops had to be widened to the minimum, which makes it worse.
- About a 50% hit rate cannot pay for a reward-to-risk ratio of about 0.5.
- Addendum 2's "fail to extend, MSS, return" pattern is real as a description. Traded this way, the revisit is too close to cover the stop and costs.

**Caveats.**
- In-sample on the burned window; the idea was chosen after looking at this data. A different stop or target choice could look different, but tuning it here would be overfitting.
- Bars after 2026-09-25 were not read.

# Addendum 4: H-NW11 variant family (EXPLORATORY, IN-SAMPLE on the burned window, NOT EVIDENCE)
The rules are in PREREG.md Addendum 4 and were committed (ff9195c) before any R was computed. Code: `addendum4.py`. Outputs: `add4_signals.csv.gz`, `add4_summary.csv` (it also has the per-instrument/TF mean R) and `add4_equity.png`.
- The R CI is a 95% day-cluster bootstrap on all signals.
- p is one-sided for mean R > 0, Holm-adjusted across the 7 variants.
- Haircut = mean R − 1.352 × SE.

| Variant | N | Win | Mean R [CI] | Holm p | Haircut R | Halted final (halt date) | Unhalted final | Unhalted max DD |
|---|---|---|---|---|---|---|---|---|
| V1 FVG-CE entry (H-NW12) | 505 | 34.5% | −0.233 [−0.349, −0.099] | 1.0 | −0.319 | $9,768 (2025-09-17) | $5,706 | 47.0% |
| V2 partial + 2R runner | 1557 | 32.8% | −0.191 [−0.252, −0.133] | 1.0 | −0.232 | $9,591 (2025-09-12) | $2,952 | 70.9% |
| V3 far stop, open ≥ 1.5R | 214 | 28.0% | −0.241 [−0.428, −0.036] | 1.0 | −0.377 | $9,698 (2025-10-12) | $7,792 | 25.7% |
| V4 London/NY AM only | 432 | 48.4% | −0.248 [−0.359, −0.138] | 1.0 | −0.323 | $9,507 (2025-11-05) | $5,956 | 40.7% |
| V5 premium/discount | 850 | 46.2% | −0.211 [−0.284, −0.140] | 1.0 | −0.261 | $9,512 (2025-09-12) | $4,397 | 56.5% |
| V6 fade failed MSS (2R) | 657 | 41.1% | +0.044 [−0.081, +0.167] | 1.0 (raw 0.25) | −0.040 | $9,479 (2025-09-01) | $11,628 | 19.8% |
| V7 prior-day bias | 786 | 47.1% | −0.183 [−0.266, −0.096] | 1.0 | −0.243 | $9,631 (2025-09-16) | $4,887 | 52.0% |

Every variant hit the 5% halt at some point in the window.

**Reading.**
- Every "trade toward the open" variant stays clearly negative. Moving the entry (CE), the target (2R runner), the stop (far extreme with an R:R filter), or filtering by session, premium/discount or bias does not fix the structural problem.
- The only non-negative variant is V6, the opposite trade: continuation after the MSS fails. Its CI includes 0, its Holm p is 1.0 and its haircut R is negative. It is also positive on US100 (+0.06 / +0.14 R) and flat on US500 (+0.02 / −0.01 R).
- **Forward-test verdict (pre-declared bar):** none qualifies. V6 is the only candidate worth writing up as a new forward-only hypothesis (continuation after a failed fade at a no-wick candle). It would need fresh data and its own prereg; nothing here supports it.
