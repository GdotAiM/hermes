# H001b EXPLORATORY RESULTS — 2026-09-13

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
| Script | `/workspace/h001b_run.py` |

## Tape integrity

- Path: `/home/box/hermes-x/investigations/INV-002-methodology-seed/evidence/tape/KAGGLE_NQ_1M_2022_2025/Dataset_NQ_1min_2022_2025.csv`
- Rows loaded: **1,048,575**
- Last timestamp: **2025-12-11 20:52:00**
- **FLAG:** n = 1,048,575 — possible Excel-row truncation (ends ~2025-12-11).
- VWAP columns **ignored** (OHLCV only).
- Instrument: NQ continuous · roll undocumented.

## Decision labels (OOS = 2025)

| Layer | Label |
|-------|-------|
| **PRIMARY (verify product)** | **VERIFY COMPLETE (frequency filed)** |
| **SECONDARY (CE-specialness)** | **FAILS (CE-specialness)** |

Banned prose not used: bare “H001b SURVIVES”; “confirms/consistent with 70%”; “70% verified”.
**VERIFY COMPLETE (frequency filed) ≠ trade permission / edge.** No MERCURY.

## Coverage / exclusions

| Reason | Count |
|--------|------:|
| Candidate RTH days 2023–2025 | 761 |
| Excl: holiday prior session | 21 |
| Excl: early-close prior session | 7 |
| Excl: no prior RTH activity | 0 |
| Excl: missing 16:14 Pref | 2 |
| Excl: missing 09:30 Popen | 0 |
| Excl: no [09:30,10:00] window | 0 |
| Excl: flat gap \|G\| < 0.25 | 2 |
| Excl: CPI/FOMC/NFP event day | 91 |
| **Eligible primary N** | **638** |
| Days with Pref+Popen (pre flat/event filter) | 731 |

| Split | N eligible |
|-------|----------:|
| IS 2023–2024 | 433 |
| OOS 2025 | 205 |
| Full 2023–2025 | 638 |

Coverage projection: OOS N and full N both exceed protocol min 80 when eligible — verify product power gate checked against OOS N.

## PRIMARY VERIFY — P̂(hit CE by 10:00 inclusive)

Hit = any 1m bar in [09:30, 10:00] ET inclusive with `low ≤ CE ≤ high`.
Bootstrap: 10,000 day-level resamples, 95% percentile CI.

| Population | N | P̂ | 95% CI |
|------------|--:|----|--------|
| IS 2023–2024 | 433 | 0.5543 | [0.5081, 0.6005] |
| OOS 2025 | 205 | 0.5561 | [0.4878, 0.6244] |
| Full 2023–2025 | 638 | 0.5549 | [0.5157, 0.5940] |

**Cited verify number = OOS 2025.** Foil 0.70 plotted conceptually as withdrawn FOIL only — distance to 0.70 is **not** a decision criterion.

### Sensitivity — [09:30, 10:00) exclude 10:00 bar

| Population | N | P̂_sens | 95% CI |
|------------|--:|--------|--------|
| IS 2023–2024 | 433 | 0.5543 | [0.5081, 0.6005] |
| OOS 2025 | 205 | 0.5512 | [0.4829, 0.6195] |
| Full 2023–2025 | 638 | 0.5533 | [0.5157, 0.5925] |

Deadline dependence flag: **not flagged** (inclusive vs exclusive OOS CIs).

### Time-to-CE (hits only, minutes after 09:30; inclusive rule)

| Population | median TTE | mean TTE |
|------------|----------:|---------:|
| IS 2023–2024 | 3.0 | 6.3 |
| OOS 2025 | 2.0 | 5.0 |
| Full 2023–2025 | 3.0 | 5.9 |

## SECONDARY — CE-specialness Δ = mean(I_CE − I_U)

Null: one `U ~ Unif(min(Pref,Popen), max(...))` per day; seed string `H001b_null_{YYYY-MM-DD}` → SHA256 → numpy Generator; U rounded to nearest 0.25 before overlap.

| Population | N | Δ̂ | 95% CI |
|------------|--:|----|--------|
| IS 2023–2024 | 433 | -0.0393 | [-0.0808, 0.0023] |
| OOS 2025 | 205 | -0.0683 | [-0.1268, -0.0146] |
| Full 2023–2025 | 638 | -0.0486 | [-0.0815, -0.0141] |

Secondary decision uses **OOS only**, N≥80, Δ>0 and CI entirely above 0 for SURVIVES; else FAILS. Geometric bias: levels near open are easier — see fill-depth.

### Fill-depth curve (touch rate of Popen + d·(Pref−Popen), d∈{0,0.25,0.5,0.75,1.0})

| d | IS | OOS | Full |
|--:|---:|----:|-----:|
| 0 | 1.0000 | 1.0000 | 1.0000 |
| 0.25 | 0.7552 | 0.7610 | 0.7571 |
| 0.5 | 0.5543 | 0.5561 | 0.5549 |
| 0.75 | 0.4157 | 0.4537 | 0.4279 |
| 1.0 | 0.3372 | 0.3512 | 0.3417 |

## Appendix A — Flat-gap sensitivity (\|G\| < 0.25 kept; events still excluded)

| Variant | N | P̂ | 95% CI |
|---------|--:|----|--------|
| Primary (flats excluded) | 638 | 0.5549 | [0.5157, 0.5940] |
| With flats | 640 | 0.5563 | [0.5172, 0.5938] |

## Appendix B — Event calendar source list (2023–2025)

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

## Appendix C — Spot-check ≥10 random eligible days (Pref / Popen)

| date | prior | Pref | Popen | G | CE | U | hit_CE | hit_excl10 | hit_U | TTE |
|------|-------|-----:|------:|--:|---:|--:|-------:|-----------:|------:|----:|
| 2023-04-03 | 2023-03-31 | 15831.00 | 15730.25 | -100.75 | 15780.75 | 15744.75 | 1.0 | 1.0 | 1.0 | 19 |
| 2023-04-04 | 2023-04-03 | 15792.25 | 15810.25 | 18.00 | 15801.25 | 15804.75 | 1.0 | 1.0 | 1.0 | 4 |
| 2023-04-13 | 2023-04-12 | 15485.25 | 15543.25 | 58.00 | 15514.25 | 15542.50 | 0.0 | 0.0 | 0.0 |  |
| 2023-08-07 | 2023-08-04 | 17713.75 | 17779.75 | 66.00 | 17746.75 | 17777.25 | 1.0 | 1.0 | 1.0 | 15 |
| 2024-04-09 | 2024-04-08 | 20007.50 | 20081.50 | 74.00 | 20044.50 | 20042.50 | 1.0 | 1.0 | 1.0 | 6 |
| 2024-04-15 | 2024-04-12 | 19882.00 | 20033.50 | 151.50 | 19957.75 | 19985.25 | 1.0 | 1.0 | 1.0 | 6 |
| 2024-07-19 | 2024-07-18 | 21328.50 | 21313.25 | -15.25 | 21321.00 | 21318.75 | 1.0 | 1.0 | 1.0 | 0 |
| 2024-11-21 | 2024-11-20 | 21961.75 | 22071.75 | 110.00 | 22016.75 | 22022.00 | 1.0 | 1.0 | 1.0 | 5 |
| 2025-01-17 | 2025-01-16 | 22110.00 | 22568.50 | 458.50 | 22339.25 | 22425.75 | 0.0 | 0.0 | 1.0 |  |
| 2025-04-01 | 2025-03-31 | 20127.75 | 20091.00 | -36.75 | 20109.50 | 20107.50 | 1.0 | 1.0 | 1.0 | 3 |
| 2025-07-08 | 2025-07-07 | 23347.75 | 23430.00 | 82.25 | 23389.00 | 23413.75 | 1.0 | 1.0 | 1.0 | 7 |
| 2025-11-13 | 2025-11-12 | 25902.25 | 25720.00 | -182.25 | 25811.25 | 25843.00 | 0.0 | 0.0 | 0.0 |  |

## Appendix D — Holiday / early-close exclusion sets

### US equity holidays intersecting sample
2022-12-26, 2023-01-02, 2023-01-16, 2023-02-20, 2023-04-07, 2023-05-29, 2023-06-19, 2023-07-04, 2023-09-04, 2023-11-23, 2023-12-25, 2024-01-01, 2024-01-15, 2024-02-19, 2024-03-29, 2024-05-27, 2024-06-19, 2024-07-04, 2024-09-02, 2024-11-28, 2024-12-25, 2025-01-01, 2025-01-20, 2025-02-17, 2025-04-18, 2025-05-26, 2025-06-19, 2025-07-04, 2025-09-01, 2025-11-27, 2025-12-25

### CME equity-index early closes
2022-11-25, 2022-12-23, 2023-07-03, 2023-11-24, 2023-12-24, 2024-07-03, 2024-11-29, 2024-12-24, 2025-07-03, 2025-11-28, 2025-12-24

## Reproducibility

- Python: `/workspace/hxvenv/bin/python /workspace/h001b_run.py`
- Bootstrap seed base: `np.random.default_rng(20260913)`
- Null U seed: `SHA256("H001b_null_{date}")[:16]` → Generator
- Day-level CSV: `H001b_day_rows.csv`

---
*Exploratory CONTINUOUS-KAGGLE only. Not stream C / not MNQ Mar 2026. No MERCURY.*
