# ADDENDUM 2026-10-04: label convention correction (DATA)
**Amends:** `DATA_GATE_KAGGLE_NQ_1M_2026-09-13.md` (original NOT rewritten; this addendum takes precedence where they conflict)
**Also amends:** `PREF_POPEN_POLICY.md`, `META.md` (timestamp semantics only)
**Owner:** DATA · **Date:** 2026-10-04 (SAST) · **Gate verdict:** stays **PASS WITH CONDITIONS**, plus condition 8 below
**Evidence:** `POST-WAVE1-LEADS/scripts/f2_kaggle_label_test.py`, `f2b_kaggle_pref_popen_shift.py` → `f2_kaggle_label_test.out`, `f2_kaggle_lag_corr.csv`, `f2_kaggle_minute_profile.csv`, `f2b_kaggle_pref_popen_shift.out`

## 1. Finding: `timestamp ET` is the bar CLOSE (end) minute, not the bar open
The 2026-09-13 gate assumed the timestamp was the bar's start time. That assumption was wrong.
The raw label **T** covers the minute **[T−1:00, T:00)** ET.

| Test (raw CSV, 2023–2025) | Result |
|---|---|
| 1m return correlation, NQ label T vs US100 CFD bar **opening** at T+k, RTH 09:35–15:55. Reference: Dukascopy BID (2024-10..2025-11), n≈80.7k | k=−2: −0.004 · **k=−1: 0.984** · k=0: −0.002 · k=+1: 0.028 · k=+2: −0.010 |
| Same test, reference HistData BID 2023–2025, n≈262k | k=−2: −0.002 · **k=−1: 0.990** · k=0: 0.000 · k=+1: 0.010 · k=+2: −0.006 |
| Cash-open spike: median volume / median range by raw label | 09:29: 699 / 8.5 · 09:30: 872 / 8.0 · **09:31: 4,931 / 25.5** · 09:32: 3,703 / 23.1 |
| Session boundaries | First bar after the CME halt is labelled **18:01** (764 rows); no label is ever 18:00. Label **17:00** exists (734 rows); 17:01 never does. File starts at `12/26/2022 18:01`. |
| Cash-close volume spike | label 15:59: 1,946 · **16:00: 8,124** · 16:01: 3,358. The 15:59–16:00 bar carries the close. |
| Truncation | 1,048,575 rows + header = 1,048,576, which is exactly Excel's row cap. The file **is** truncated (it ends 2025-12-11 20:52). This is now confirmed rather than "possible". |

**Correct reading:** canonical bar-open time = raw label − 1 minute.
`/workspace/marketdata` already applies this. `data/kaggle/NQ/1m_trade/*.parquet` has `ts_*` = label − 1 min, and the raw label is kept in `label_et_raw`.

## 2. Corrected Pref / Popen mapping (replaces the locks in the 2026-09-13 gate and PREF_POPEN_POLICY.md)
The locks keep their intent: the bar that **opens** at 16:14, and the bar that **opens** at 09:30.

| Symbol | Intent | Raw CSV row to use (`timestamp ET`) | Marketdata parquet (`ts_ny`, bar open) | What the 2026-09-13 lock actually used |
|---|---|---|---|---|
| Pref | close of the 16:14–16:15 bar ("4:14 final print") | **close of label 16:15** | close of `ts_ny` 16:14 | close of label 16:14 = close of the 16:13 bar (1 min early) |
| Popen | open of the 09:30–09:31 bar (cash open) | **open of label 09:31** | open of `ts_ny` 09:30 | open of label 09:30 = **09:29 bar open**, i.e. the price at 09:29:00 (pre-open) |
| Missing-bar exclusions | — | missing **16:15** / missing **09:31** | missing 16:14 / 09:30 | counted on labels 16:14 / 09:30 |

**General rule for every window on this tape.** The bar that opens at X ET has raw label X+1.
So a window of bars opening in [a, b) is raw labels a+1 … b. Examples:
- W = [07:00, 09:00) means labels 07:01 … 09:00.
- "from the 09:30 bar" starts at label 09:31.
- "through the 10:00 bar inclusive" ends at label 10:01.
- "ends at 12:00" (T*) means the last bar opening 11:59, i.e. label 12:00.

QUANT must state its convention for each horizon in the re-run memo.

## 3. Size of the error (raw tape, weekdays)
- Popen corrected − old: differs on 97.4% of days. Median |Δ| 3.25 pts, p90 9.25, max 44.75 (n=764).
- Pref corrected − old: differs on 96.7% of days. Median |Δ| 2.0 pts, p90 6.9, max 35.75 (n=735).
- CE = (Pref+Popen)/2 moves on most days. Median |ΔCE| 2.0 pts, p90 5.4. 84.8% of days move by ≥ 2 ticks.
- 17 of 758 days flip the sign of the Popen−Pref gap.
- Coverage counts are unchanged: labels 09:31 = 764 and 16:15 = 735, versus 765 and 735 for the old labels.

The old Popen was a **pre-open** (09:29) price. A "hit CE by 10:00" estimand starts its path one minute before the cash open, so it includes the last pre-open minute. That biases the hit rate, and the direction isn't known.

## 4. Required actions
| # | Action | Owner |
|---|---|---|
| 1 | **H001b**: re-run with Pref = close of raw label 16:15, Popen = open of raw label 09:31, and the CE window shifted +1 label. Report old vs new P̂, CI, Δ for IS 2023–24 and OOS 2025. The current result is **SUSPENDED** until the re-run. | QUANT |
| 2 | **H003c**: re-run. W = [07:00, 09:00) becomes labels 07:01–09:00. The control "Foil A @09:30" becomes label 09:31. The touch scan after 09:30 and the horizons 10:00/11:00/12:00 shift +1 label. Its result is also **SUSPENDED** until the re-run. | QUANT |
| 3 | **H002b, H004b** (same tape; 07:00–09:00 range, 09:30 start, 10:00/11:00 hour windows): re-check the window edges and re-run if any boundary bar is used. **H009b** Kaggle daily-agg: the calendar-day boundary moves 1 min. Expected impact is negligible, but confirm in one line. | QUANT |
| 4 | Every result memo on this tape adds the tag `labels=bar-close (corrected 2026-10-04)`. Prefer the marketdata parquet (bar-open `ts_ny`) for any new run. | QUANT / preregs |
| 5 | **Condition 8 (new, hard):** no inference from this tape may use the 2026-09-13 Pref/Popen locks. | DATA |

## 5. Other parts of the original gate
All remain in force: stream label, roll undocumented, no 2026, not stream C, VWAP not primary.
Also note: this tape (2022-12-26 → 2025-12-11) is **touched** for preregistration purposes. See `POST-WAVE1-LEADS/DATA_RULINGS_MARKETDATA_2026-10-04.md` §4.
