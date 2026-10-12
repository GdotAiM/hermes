# 7PM (19:00–20:00 NY) range sweep: REPORT (EXPLORATORY, IN-SAMPLE on the burned window, NOT EVIDENCE)
- **Prereg:** `PREREG.md`, commit 2c83300, committed before any R.
- **Code:** `sweep7pm.py`.
- **Outputs:** `descriptive.csv`, `null.csv`, `null_by_hour_*.csv`, `results.csv`, `trades.csv`, `equity.png` (left: unhalted $10k books; right: the null by range hour).
- **Data:** US100 and US500 1m BID/ASK, 2025-08-24 → 2026-09-25 (281 evenings each). Trade window 20:00 → 08:00 NY.

## Descriptive

| | US100 | US500 |
|---|---|---|
| a side swept by 08:00 | 100% (0 ambiguous) | 100% |
| first sweep = high | 53.7% | 52.3% |
| opposite side reached after the first sweep (by 08:00) | **66.6%** | **66.6%** |
| midpoint reached after the sweep | 82.2% | 80.8% |
| minutes from sweep to opposite side, median / p75 | 103 / 325 | 98 / 333 |

**Null: the same stat for a 1-h range at every other hour, 12-h follow window.**

| | US100 | US500 |
|---|---|---|
| P(opposite reached), other hours | 64.7% | 65.5% |
| 19:00 − other hours | +1.9 pp [−3.7, +7.3] | +1.0 pp [−4.7, +6.4] |
| rank of 19:00 among 24 hours | 13th | 13th |

The 7PM range behaves like any 1-h range. A 1-h range is almost always taken within 12 h, and the opposite side follows about two-thirds of the time regardless of the hour.

## Trading variants (correct-side BID/ASK + DATA slippage floors, 4× min stop, stop-first)

| Variant | N | Win | Avg win / avg loss R | Mean R [95% day-cluster CI] | Haircut R | US100 / US500 mean R | Halted final (halt, NY) | Unhalted final | Unhalted max DD |
|---|---|---|---|---|---|---|---|---|---|
| a_opp (close back inside → opposite) | 545 | 38.2% | +1.51 / −1.12 | −0.118 [−0.268, +0.031] | −0.215 | −0.052 / −0.184 | $10,132 (2025-10-15 20:30) | $7,098 | 42.0% |
| a_mid | 532 | 51.1% | +0.70 / −1.10 | −0.178 [−0.279, −0.070] | −0.246 | −0.137 / −0.219 | $9,819 (2025-10-15) | $6,172 | 41.2% |
| b_opp (market on sweep → opposite) | 562 | 29.9% | +2.43 / −1.15 | −0.084 [−0.277, +0.128] | −0.216 | −0.028 / −0.140 | $10,113 (2025-10-02) | $7,588 | 43.4% |
| b_mid | 560 | 41.3% | +1.25 / −1.15 | −0.158 [−0.301, −0.010] | −0.251 | −0.115 / −0.201 | $9,935 (2025-10-13) | $6,306 | 41.8% |
| c_opp (1m MSS back inside → opposite) | 510 | 48.4% | +0.87 / −1.04 | −0.117 [−0.227, −0.001] | −0.189 | −0.069 / −0.165 | $10,397 (2025-11-17) | $7,330 | 37.4% |
| c_mid | 418 | 56.7% | +0.41 / −0.89 | −0.157 [−0.243, −0.070] | −0.213 | −0.127 / −0.186 | $9,663 (2025-11-20) | $7,180 | 30.7% |

- Holm p = 1.0 for all 6. Every pooled mean R is negative, on both instruments, and every halted book hit the 5% DD halt in Oct–Nov 2025.
- **Forward-test verdict (pre-declared bar):** none.

## Reading
- The "sweep one side, run to the other" path is common (two-thirds of nights). But it is no more common than for any other hour's range, and the trade loses after costs.
- The sweep extreme is usually close to the entry, so 57–92% of stops (a and b entries) had to be widened to the 4× cost minimum. The opposite side is far relative to that risk only when the range is wide.
- A sweep is followed by a further run in the sweep direction often enough to stop the trade before the reversal: 30–48% wins on the opposite target.
- US100 is less negative than US500 for every variant, but no US100 CI is above 0.

## Caveats
- In-sample on one year of burned data; US100 and US500 are highly correlated.
- 1m bars can't order a stop and a target in the same bar, so stop-first (conservative).
- Overnight ASK gaps are forward-filled.
- The null compares follow windows that cross different sessions per hour.
