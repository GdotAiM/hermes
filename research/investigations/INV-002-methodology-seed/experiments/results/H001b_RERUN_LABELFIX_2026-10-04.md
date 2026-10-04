# H001b RE-RUN (LABELFIX) — 2026-10-04
`CONTINUOUS-KAGGLE-NQ1M · labels=bar-close (corrected 2026-10-04) · roll undocumented · truncation CONFIRMED (ends 2025-12-11) · not MNQ Mar 2026 · not stream C · No MERCURY`

**Supersedes:** `H001b_EXPLORATORY_RESULTS_2026-09-13.md` (now SUSPENDED) · **Protocol:** `QUANT_H001b_RTH_ORG_CE_PROTOCOL_2026-09-13.md` (frozen, unchanged) · **DATA:** `ADDENDUM_2026-10-04_LABEL_CONVENTION.md` §2 locks, condition 8 · **Script:** `/workspace/h001b_run_labelfix.py` (copy of `/workspace/h001b_run.py`; only change is the label−1 min shift, plus output paths and reading the frozen event-calendar CSV instead of rewriting it, with an assert that the in-code calendar still equals the CSV) · **Day rows:** `H001b_day_rows_RERUN_LABELFIX_2026-10-04.csv`

## Decision (OOS = 2025)
| Layer | OLD (2026-09-13, label-as-open) | NEW (bar-open, corrected) |
|---|---|---|
| **PRIMARY (verify product)** | VERIFY COMPLETE (frequency filed) | **VERIFY COMPLETE (frequency filed)** |
| **SECONDARY (CE-specialness)** | FAILS (CE-specialness) | **FAILS (CE-specialness)** |

The cited verify number is OOS 2025: **P̂(hit CE by 10:00 incl.) = 0.5882 [0.5196, 0.6569], N=204** (old 0.5561 [0.4878, 0.6244], N=205). 0.70 is a withdrawn **FOIL only**. It is not a pass/fail target, and nothing here relates P̂ to it. VERIFY COMPLETE ≠ trade permission or edge. No MERCURY.
CE-specialness OOS Δ = **−0.0490 [−0.1029, 0.0049]** (old −0.0683 [−0.1268, −0.0146]). SURVIVES needs Δ>0 and a CI entirely above 0, so the label is FAILS. Δ is still negative, but its CI now reaches just past 0, where the old CI excluded 0.

## Window / horizon convention (bar-open; raw label = bar open + 1 min)
| Object | Bar-open definition | Raw-label range |
|---|---|---|
| Pref | close of the bar opening **16:14** on prior RTH session | close of label **16:15** |
| Popen | open of the bar opening **09:30** on day D | open of label **09:31** |
| Missing-bar exclusion | missing bar 16:14 / 09:30 | missing label 16:15 / 09:31 |
| Primary CE window ("by 10:00 inclusive of the 10:00 bar") | bars opening **[09:30, 10:00]** | labels **09:31 … 10:01** |
| Sensitivity (exclude 10:00 bar) | bars opening [09:30, 10:00) | labels 09:31 … 10:00 |
| Time-to-CE | minutes from 09:30 bar open to the first hit bar's open | — |
| RTH-activity day (prior-session finder only) | any bar opening in [09:30, 16:00] (logic unchanged) | labels 09:31 … 16:01 |
| Calendar date | date of the bar open | label 00:00 belongs to the previous date |

## OLD vs NEW — every decision number
| Quantity | OLD | NEW |
|---|---|---|
| Candidate RTH days 2023–2025 | 761 | 760 |
| Excl holiday-prior / early-close-prior | 21 / 7 | 21 / 7 |
| Excl missing Pref bar / missing Popen bar | 2 / 0 | 1 / 0 |
| Excl flat gap \|G\|<0.25 | 2 | 0 |
| Excl CPI/FOMC/NFP | 91 | 92 |
| Days with Pref+Popen | 731 | 731 |
| **N eligible IS / OOS / Full** | 433 / 205 / 638 | **435 / 204 / 639** |
| P̂ IS 2023–24 [CI] | 0.5543 [0.5081, 0.6005] | 0.5632 [0.5172, 0.6092] |
| **P̂ OOS 2025 [CI]** | 0.5561 [0.4878, 0.6244] | **0.5882 [0.5196, 0.6569]** |
| P̂ Full [CI] | 0.5549 [0.5157, 0.5940] | 0.5712 [0.5321, 0.6088] |
| P̂_sens (excl. 10:00 bar) IS / OOS / Full | 0.5543 / 0.5512 [0.4829, 0.6195] / 0.5533 | 0.5540 / 0.5637 [0.4951, 0.6324] / 0.5571 |
| Deadline-dependence flag | not flagged | not flagged |
| TTE median / mean, OOS (min) | 2.0 / 5.0 | 2.0 / 5.9 |
| TTE median / mean, IS (min) | 3.0 / 6.3 | 3.0 / 5.8 |
| Δ CE-specialness IS [CI] | −0.0393 [−0.0808, 0.0023] | −0.0322 [−0.0736, 0.0092] |
| **Δ CE-specialness OOS [CI]** | −0.0683 [−0.1268, −0.0146] | **−0.0490 [−0.1029, 0.0049]** |
| Δ Full [CI] | −0.0486 [−0.0815, −0.0141] | −0.0376 [−0.0704, −0.0047] |
| Fill-depth OOS d=0 / .25 / .5 / .75 / 1.0 | 1.0000 / 0.7610 / 0.5561 / 0.4537 / 0.3512 | 1.0000 / 0.7647 / 0.5882 / 0.4657 / 0.3676 |
| Flat-gap sensitivity (flats kept) N, P̂ | 640, 0.5563 [0.5172, 0.5938] | 639, 0.5712 [0.5321, 0.6088] (no flats remain) |
| PRIMARY label | VERIFY COMPLETE (frequency filed) | VERIFY COMPLETE (frequency filed) |
| SECONDARY label | FAILS | FAILS |

There is no walk-forward in the H001b protocol.

## What moved (day level) and cross-check against DATA's addendum
On H001b's own day rows (730 days with Pref+Popen in both runs):
- **Popen** moved on **712/730 = 97.5%** of days. Median |Δ| 3.25 pts, p90 9.25.
- **Pref** moved on 706/730 = 96.7%. Median |Δ| 2.00 pts.
- **CE** changed on **696** days (any tick) and moved **≥2 ticks** on **637/730 = 87.3%**. Median |ΔCE| 2.00 pts, p90 5.25.
- **Gap sign flipped on 17 days:** 2023-01-16, 2023-03-22, 2023-09-08, 2023-10-31, 2024-02-05, 2024-03-04, 2024-05-16, 2024-09-13, 2024-10-09, 2024-11-12, 2025-01-28, 2025-02-06, 2025-03-13, 2025-04-28, 2025-05-30, 2025-06-09, 2025-07-14.
- On the 637 days eligible in both runs, hit_CE changed on **19** days (14 0→1, 5 1→0). hit_U changed on 28.
- Eligibility changes:
  - 2023-09-08 and 2024-10-09 were flat-gap exclusions under the old prices. Both are gap-flip days, and both are now eligible (IS).
  - 2025-01-09 (market closure for the national day of mourning) drops out of the candidate set. In the old run it was OOS-eligible with a one-bar window: label 09:30, which is really the 09:29 pre-open bar.
  - 2025-01-10: the old exclusion was missing 16:14 on 01-09. Its prior session is now 01-08, so it is excluded as an NFP event day.

**DATA cross-check.** I recomputed DATA's §3 statistic the way DATA defines it, on all raw-tape weekdays:
- Popen differs on **97.4%** of days (n=764). Median 3.25, p90 9.25, max 44.75.
- Pref differs on 96.7% (n=735), median 2.00.
- CE moves ≥2 ticks on **84.8%** (n=758), median 2.00.
- Gap sign flips on **17 of 758** days.

**This matches DATA exactly:** 97.4%, 3.25, 9.25, 44.75; 96.7%, 2.0; 84.8%; 17/758. H001b's own 730-day pool gives 87.3% for "≥2 ticks" because its population is different (it excludes holiday-prior and early-close-prior days). That is not a material disagreement.

## Data source and shift check
- Tape used: raw CSV `evidence/tape/KAGGLE_NQ_1M_2022_2025/Dataset_NQ_1min_2022_2025.csv` (1,048,575 rows; last raw label `12/11/2025 20:52` = last bar opening 2025-12-11 20:51 ET; Excel-cap truncation CONFIRMED).
- Shift applied immediately after load: `ts = to_datetime(label, "%m/%d/%Y %H:%M") − 1 min`; raw label kept as `label_et_raw`. Calendar date, HH:MM, and time-of-day are all derived from the bar-open `ts`.
- Parquet cross-check (`/workspace/marketdata/data/kaggle/NQ/1m_trade/*.parquet`, read with the marketdata venv because hxvenv has no pyarrow and its pip is broken): all 1,048,575 rows matched on `ts_ny` (tz stripped) == raw label − 1 min. Open/high/low/close mismatches: **0 / 0 / 0 / 0**. Spot rows, e.g. raw `12/12/2024 4:00` → ts_ny 2024-12-12 03:59, O/H/L/C 22951.50/22952.25/22949.75/22950.00 in both; raw `6/17/2025 13:37` → 13:36, 22536.75/22537.75/22531.50/22536.75 in both.
- Frozen protocol logic, seeds, splits, event calendar (`H001b_event_calendar_2023_2025.csv`, read and **not** rewritten), and holiday/early-close sets are unchanged.
- **Old-number check:** before the re-run, the original script was re-run with only its output paths redirected (`/workspace/labelfix/replay_*.py`). Its day-row CSV was **byte-identical** to the 2026-09-13 file, so the OLD column below is a verified reproduction.

## Appendix — full re-run output (script-generated, bar-open)
### [script output] H001b EXPLORATORY RESULTS — 2026-09-13

**Stream label (mandatory):** `CONTINUOUS-KAGGLE-NQ1M` · **roll undocumented** · **not MNQ Mar 2026** · **no 2026 lecture-day identity/calibration**

| Field | Value |
|-------|-------|
| Hypothesis | H001b (exploratory falsification) |
| Protocol | `QUANT_H001b_RTH_ORG_CE_PROTOCOL_2026-09-13.md` |
| DATA gate | `DATA_GATE_KAGGLE_NQ_1M_2026-09-13.md` · PASS WITH CONDITIONS |
| Pref / Popen | Pref = close 16:14 ET prior session; Popen = open 09:30 ET day D |
| CE | `(Pref+Popen)/2` rounded to nearest 0.25 (half away from 0) before overlap |
| Primary estimand | P̂(hit CE by 10:00 inclusive) + bootstrap 95% CI (10k day-level) |
| Foil | 0.70 = **FOIL only** (C-METH-009 withdrawn) — never pass/fail target |
| Split | 2023–2024 IS / 2025 OOS (ORION) |
| Vocabulary | VERIFY COMPLETE ≠ trade permission · **No MERCURY** |
| Script | `/workspace/h001b_run_labelfix.py` |

#### Tape integrity

- Path: `/home/box/hermes-x/investigations/INV-002-methodology-seed/evidence/tape/KAGGLE_NQ_1M_2022_2025/Dataset_NQ_1min_2022_2025.csv`
- Rows loaded: **1,048,575**
- Last timestamp (bar open): **2025-12-11 20:51:00** (= raw label 20:52)
- **FLAG:** n = 1,048,575 — Excel-row truncation CONFIRMED (DATA 2026-10-04) (ends ~2025-12-11).
- VWAP columns **ignored** (OHLCV only).
- Instrument: NQ continuous · roll undocumented.

#### Decision labels (OOS = 2025)

| Layer | Label |
|-------|-------|
| **PRIMARY (verify product)** | **VERIFY COMPLETE (frequency filed)** |
| **SECONDARY (CE-specialness)** | **FAILS (CE-specialness)** |

Banned prose not used: bare “H001b SURVIVES”; “confirms/consistent with 70%”; “70% verified”.
**VERIFY COMPLETE (frequency filed) ≠ trade permission / edge.** No MERCURY.

#### Coverage / exclusions

| Reason | Count |
|--------|------:|
| Candidate RTH days 2023–2025 | 760 |
| Excl: holiday prior session | 21 |
| Excl: early-close prior session | 7 |
| Excl: no prior RTH activity | 0 |
| Excl: missing 16:14 Pref | 1 |
| Excl: missing 09:30 Popen | 0 |
| Excl: no [09:30,10:00] window | 0 |
| Excl: flat gap \|G\| < 0.25 | 0 |
| Excl: CPI/FOMC/NFP event day | 92 |
| **Eligible primary N** | **639** |
| Days with Pref+Popen (pre flat/event filter) | 731 |

| Split | N eligible |
|-------|----------:|
| IS 2023–2024 | 435 |
| OOS 2025 | 204 |
| Full 2023–2025 | 639 |

Coverage projection: OOS N and full N both exceed protocol min 80 when eligible — verify product power gate checked against OOS N.

#### PRIMARY VERIFY — P̂(hit CE by 10:00 inclusive)

Hit = any 1m bar in [09:30, 10:00] ET inclusive with `low ≤ CE ≤ high`.
Bootstrap: 10,000 day-level resamples, 95% percentile CI.

| Population | N | P̂ | 95% CI |
|------------|--:|----|--------|
| IS 2023–2024 | 435 | 0.5632 | [0.5172, 0.6092] |
| OOS 2025 | 204 | 0.5882 | [0.5196, 0.6569] |
| Full 2023–2025 | 639 | 0.5712 | [0.5321, 0.6088] |

**Cited verify number = OOS 2025.** Foil 0.70 plotted conceptually as withdrawn FOIL only — distance to 0.70 is **not** a decision criterion.

### Sensitivity — [09:30, 10:00) exclude 10:00 bar

| Population | N | P̂_sens | 95% CI |
|------------|--:|--------|--------|
| IS 2023–2024 | 435 | 0.5540 | [0.5080, 0.6000] |
| OOS 2025 | 204 | 0.5637 | [0.4951, 0.6324] |
| Full 2023–2025 | 639 | 0.5571 | [0.5180, 0.5947] |

Deadline dependence flag: **not flagged** (inclusive vs exclusive OOS CIs).

### Time-to-CE (hits only, minutes after 09:30; inclusive rule)

| Population | median TTE | mean TTE |
|------------|----------:|---------:|
| IS 2023–2024 | 3.0 | 5.8 |
| OOS 2025 | 2.0 | 5.9 |
| Full 2023–2025 | 2.0 | 5.8 |

#### SECONDARY — CE-specialness Δ = mean(I_CE − I_U)

Null: one `U ~ Unif(min(Pref,Popen), max(...))` per day; seed string `H001b_null_{YYYY-MM-DD}` → SHA256 → numpy Generator; U rounded to nearest 0.25 before overlap.

| Population | N | Δ̂ | 95% CI |
|------------|--:|----|--------|
| IS 2023–2024 | 435 | -0.0322 | [-0.0736, 0.0092] |
| OOS 2025 | 204 | -0.0490 | [-0.1029, 0.0049] |
| Full 2023–2025 | 639 | -0.0376 | [-0.0704, -0.0047] |

Secondary decision uses **OOS only**, N≥80, Δ>0 and CI entirely above 0 for SURVIVES; else FAILS. Geometric bias: levels near open are easier — see fill-depth.

### Fill-depth curve (touch rate of Popen + d·(Pref−Popen), d∈{0,0.25,0.5,0.75,1.0})

| d | IS | OOS | Full |
|--:|---:|----:|-----:|
| 0 | 1.0000 | 1.0000 | 1.0000 |
| 0.25 | 0.7333 | 0.7647 | 0.7433 |
| 0.5 | 0.5632 | 0.5882 | 0.5712 |
| 0.75 | 0.4276 | 0.4657 | 0.4397 |
| 1.0 | 0.3448 | 0.3676 | 0.3521 |

#### Appendix A — Flat-gap sensitivity (\|G\| < 0.25 kept; events still excluded)

| Variant | N | P̂ | 95% CI |
|---------|--:|----|--------|
| Primary (flats excluded) | 639 | 0.5712 | [0.5321, 0.6088] |
| With flats | 639 | 0.5712 | [0.5321, 0.6088] |

#### Appendix B — Event calendar source list (2023–2025)

Primary excludes union of CPI ∪ FOMC decision day ∪ NFP on calendar date D.

| Source | URL / note |
|--------|------------|
| CPI | BLS CPI release schedule; OMB PFEI 2024 PDF; FRED CPI calendar 2025 |
| NFP | BLS Employment Situation schedule; 2025 lapse revisions at bls.gov/bls/2025-lapse-revised-release-dates.htm |
| FOMC | https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm (decision = 2nd day) |
| Holidays | NYSE US equity holidays 2022–2025 |
| Early closes | CME equity-index early closes: Jul 3 / day-after-Thanksgiving / Christmas Eve |

Event rows in run table: **97** (unique dates may be fewer if multi-type).

### Event dates used

| event_date | event_type |
|------------|------------|
| 2023-01-06 | NFP |
| 2023-01-12 | CPI |
| 2023-02-01 | FOMC |
| 2023-02-03 | NFP |
| 2023-02-14 | CPI |
| 2023-03-10 | NFP |
| 2023-03-14 | CPI |
| 2023-03-22 | FOMC |
| 2023-04-07 | NFP |
| 2023-04-12 | CPI |
| 2023-05-03 | FOMC |
| 2023-05-05 | NFP |
| 2023-05-10 | CPI |
| 2023-06-02 | NFP |
| 2023-06-13 | CPI |
| 2023-06-14 | FOMC |
| 2023-07-07 | NFP |
| 2023-07-12 | CPI |
| 2023-07-26 | FOMC |
| 2023-08-04 | NFP |
| 2023-08-10 | CPI |
| 2023-09-01 | NFP |
| 2023-09-13 | CPI |
| 2023-09-20 | FOMC |
| 2023-10-06 | NFP |
| 2023-10-12 | CPI |
| 2023-11-01 | FOMC |
| 2023-11-03 | NFP |
| 2023-11-14 | CPI |
| 2023-12-08 | NFP |
| 2023-12-12 | CPI |
| 2023-12-13 | FOMC |
| 2024-01-05 | NFP |
| 2024-01-11 | CPI |
| 2024-01-31 | FOMC |
| 2024-02-02 | NFP |
| 2024-02-13 | CPI |
| 2024-03-08 | NFP |
| 2024-03-12 | CPI |
| 2024-03-20 | FOMC |
| 2024-04-05 | NFP |
| 2024-04-10 | CPI |
| 2024-05-01 | FOMC |
| 2024-05-03 | NFP |
| 2024-05-15 | CPI |
| 2024-06-07 | NFP |
| 2024-06-12 | CPI |
| 2024-06-12 | FOMC |
| 2024-07-05 | NFP |
| 2024-07-11 | CPI |
| 2024-07-31 | FOMC |
| 2024-08-02 | NFP |
| 2024-08-14 | CPI |
| 2024-09-06 | NFP |
| 2024-09-11 | CPI |
| 2024-09-18 | FOMC |
| 2024-10-04 | NFP |
| 2024-10-10 | CPI |
| 2024-11-01 | NFP |
| 2024-11-07 | FOMC |
| 2024-11-13 | CPI |
| 2024-12-06 | NFP |
| 2024-12-11 | CPI |
| 2024-12-18 | FOMC |
| 2025-01-10 | NFP |
| 2025-01-15 | CPI |
| 2025-01-29 | FOMC |
| 2025-02-07 | NFP |
| 2025-02-12 | CPI |
| 2025-03-07 | NFP |
| 2025-03-12 | CPI |
| 2025-03-19 | FOMC |
| 2025-04-04 | NFP |
| 2025-04-10 | CPI |
| 2025-05-02 | NFP |
| 2025-05-07 | FOMC |
| 2025-05-13 | CPI |
| 2025-06-06 | NFP |
| 2025-06-11 | CPI |
| 2025-06-18 | FOMC |
| 2025-07-03 | NFP |
| 2025-07-15 | CPI |
| 2025-07-30 | FOMC |
| 2025-08-01 | NFP |
| 2025-08-12 | CPI |
| 2025-09-05 | NFP |
| 2025-09-11 | CPI |
| 2025-09-17 | FOMC |
| 2025-10-03 | NFP |
| 2025-10-24 | CPI |
| 2025-10-29 | FOMC |
| 2025-11-07 | NFP |
| 2025-11-20 | NFP |
| 2025-12-05 | NFP |
| 2025-12-10 | FOMC |
| 2025-12-16 | NFP |
| 2025-12-18 | CPI |

#### Appendix C — Spot-check ≥10 random eligible days (Pref / Popen)

| date | prior | Pref | Popen | G | CE | U | hit_CE | hit_excl10 | hit_U | TTE |
|------|-------|-----:|------:|--:|---:|--:|-------:|-----------:|------:|----:|
| 2023-04-03 | 2023-03-31 | 15832.50 | 15735.00 | -97.50 | 15783.75 | 15749.25 | 1.0 | 1.0 | 1.0 | 18 |
| 2023-04-05 | 2023-04-04 | 15750.25 | 15698.50 | -51.75 | 15724.50 | 15740.25 | 0.0 | 0.0 | 0.0 |  |
| 2023-04-13 | 2023-04-12 | 15485.75 | 15552.50 | 66.75 | 15519.25 | 15551.50 | 0.0 | 0.0 | 1.0 |  |
| 2023-08-08 | 2023-08-07 | 17835.75 | 17727.25 | -108.50 | 17781.50 | 17775.75 | 0.0 | 0.0 | 0.0 |  |
| 2024-04-08 | 2024-04-05 | 19980.25 | 20024.00 | 43.75 | 20002.25 | 20002.00 | 1.0 | 1.0 | 1.0 | 2 |
| 2024-04-12 | 2024-04-11 | 20186.75 | 19990.50 | -196.25 | 20088.75 | 20045.75 | 0.0 | 0.0 | 0.0 |  |
| 2024-07-18 | 2024-07-17 | 21439.00 | 21574.00 | 135.00 | 21506.50 | 21567.50 | 1.0 | 1.0 | 1.0 | 11 |
| 2024-11-20 | 2024-11-19 | 21985.75 | 21951.25 | -34.50 | 21968.50 | 21959.50 | 0.0 | 0.0 | 0.0 |  |
| 2025-01-16 | 2025-01-15 | 22286.25 | 22406.50 | 120.25 | 22346.50 | 22318.75 | 1.0 | 1.0 | 1.0 | 2 |
| 2025-03-31 | 2025-03-28 | 20121.00 | 19875.50 | -245.50 | 19998.25 | 20036.50 | 0.0 | 0.0 | 0.0 |  |
| 2025-07-08 | 2025-07-07 | 23353.00 | 23429.50 | 76.50 | 23391.25 | 23414.25 | 1.0 | 1.0 | 1.0 | 6 |
| 2025-11-13 | 2025-11-12 | 25904.00 | 25733.75 | -170.25 | 25819.00 | 25848.50 | 0.0 | 0.0 | 0.0 |  |

#### Appendix D — Holiday / early-close exclusion sets

### US equity holidays intersecting sample
2022-12-26, 2023-01-02, 2023-01-16, 2023-02-20, 2023-04-07, 2023-05-29, 2023-06-19, 2023-07-04, 2023-09-04, 2023-11-23, 2023-12-25, 2024-01-01, 2024-01-15, 2024-02-19, 2024-03-29, 2024-05-27, 2024-06-19, 2024-07-04, 2024-09-02, 2024-11-28, 2024-12-25, 2025-01-01, 2025-01-20, 2025-02-17, 2025-04-18, 2025-05-26, 2025-06-19, 2025-07-04, 2025-09-01, 2025-11-27, 2025-12-25

### CME equity-index early closes
2022-11-25, 2022-12-23, 2023-07-03, 2023-11-24, 2023-12-24, 2024-07-03, 2024-11-29, 2024-12-24, 2025-07-03, 2025-11-28, 2025-12-24

#### Reproducibility

- Python: `/workspace/hxvenv/bin/python /workspace/h001b_run_labelfix.py`
- Bootstrap seed base: `np.random.default_rng(20260913)`
- Null U seed: `SHA256("H001b_null_{date}")[:16]` → Generator
- Day-level CSV: `H001b_day_rows_RERUN_LABELFIX_2026-10-04.csv`

---
*Exploratory CONTINUOUS-KAGGLE only. Not stream C / not MNQ Mar 2026. No MERCURY.*

