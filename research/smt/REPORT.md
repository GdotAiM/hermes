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
