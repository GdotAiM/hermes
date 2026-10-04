# H002b RE-RUN (LABELFIX) — 2026-10-04
`CONTINUOUS-KAGGLE-NQ1M · labels=bar-close (corrected 2026-10-04) · roll undocumented · truncation CONFIRMED (ends 2025-12-11) · not MNQ Mar 2026 · not stream C · No MERCURY`

**Replaces (re-check of):** `H002b_EXPLORATORY_RESULTS_2026-09-13.md` · **Protocol:** `QUANT_H002b_79_STATE_CLASSIFIER_PROTOCOL_2026-09-13.md` (frozen) · **§3 freeze hash:** `074d6a83ccf5289cf654b26c4cd747ea9b3bbe1c4671c1c65aa598b9f3eb3464`, **verified OK** before fitting · **Script:** `/workspace/h002b_run_labelfix.py` · soft-prior computation `/workspace/labelfix/h002b_softprior.py` (it reproduces the old memo's soft-prior numbers exactly on the old rows) · **Day rows:** `H002b_day_rows_RERUN_LABELFIX_2026-10-04.csv`
This is a **PARAMETER classifier implementing the 003–005 precursor**. It is not an Observed class identity, and it is **not a panacea** (Passed 005).

## Decision
| Layer | OLD | NEW |
|---|---|---|
| Protocol-locked hard IS-majority baseline | mechanical pass (lift ≈18; REJECTED as board SURVIVES by CASSANDRA) | mechanical pass (lift ≈18; still REJECTED; one-hot clipped log-loss strawman) |
| **BOARD CALL (soft IS empirical-prior baseline)** | **FAILS** | **FAILS** |

**UNCHANGED: board-locked FAILS.**
- Soft empirical-prior OOS lift = **0.0157 [-0.0250, 0.0558]** (old 0.0165 [-0.0253, 0.0566]). The CI includes ≤0.
- The locked hard-majority lift is **17.9913 [15.5459, 20.4583]** (old 18.0559). That number is a clipping artifact and does not drive the decision.
- Balanced accuracy is 0.3564, about chance for 3 classes.

There is no strong edge, and this is not a panacea. No MERCURY.

## Window / horizon convention (bar-open; raw label = bar open + 1 min)
| Object | Bar-open definition | Raw-label range |
|---|---|---|
| 7–9 window W (O79, H79, L79, C79, R79; ATR_ref = median R of prior 20 ex-Sunday days < D) | bars opening **[07:00, 09:00)**. O79 = open of the 07:00 bar; C79 = close of the 08:59 bar | labels **07:01 … 09:00** (O = open of label 07:01, C = close of label 09:00) |
| y path start | from the bar opening 09:30 | from label 09:31 |
| T* = 12:00 (primary y horizon) | through the last bar opening 11:59, i.e. [09:30, 12:00) | labels 09:31 … 12:00 |
| 10:00 / 11:00 descriptive | [09:30, 10:00) / [09:30, 11:00) | labels 09:31 … 10:00 / … 11:00 |
| Chop (5m closes < T*) | 5m buckets of bar-open timestamps < 12:00 | — |

The end-comparison change (`<= T*` → `< T*` in bar-open time) is the same as for H003c. The pure-shift variant (through label 12:01) gives **identical** decision numbers; only y_1000 and range-expansion descriptives move.

## OLD vs NEW — every decision number
| Quantity | OLD | NEW |
|---|---|---|
| **Primary N IS / OOS** (non-event, class+y valid) | 427 / 207 | **427 / 206** |
| All-days valid (incl. events) | 725 | 724 |
| Excl holiday / no_atr / no_path | 22 / 15 / 0 | 22 / 15 / 1 (2025-01-09 closure) |
| Class IS ↑/↓/comp/cons | 68 / 60 / 22 / 277 | 65 / 62 / 22 / 278 |
| Class OOS ↑/↓/comp/cons | 22 / 26 / 8 / 151 | 23 / 25 / 8 / 150 |
| y IS high/low/neither | 226 / 198 / 3 | 227 / 197 / 3 |
| y OOS high/low/neither | 99 / 105 / 3 | 99 / 105 / 2 |
| Locked hard: L_base / L_model | 18.8054 / 0.7495 | 18.7217 / 0.7304 |
| **Locked hard-majority lift [CI]** | 18.0559 [15.5980, 20.4933] | **17.9913 [15.5459, 20.4583]** |
| Locked hard WF median lift (step 20) | 17.3617 | 19.0919 |
| Persistence (sensitivity) hard lift [CI] | 18.0309 [15.6265, 20.4423] | 17.9709 [15.5411, 20.4311] |
| Soft prior (IS y freq) | [0.5293, 0.4637, 0.007] | [0.5316, 0.4614, 0.007] |
| Soft: L_base / L_model | 0.7660 / 0.7495 | 0.7461 / 0.7304 |
| **Soft empirical-prior lift [CI]** | **0.0165 [-0.0253, 0.0566]** | **0.0157 [-0.0250, 0.0558]** |
| Soft WF median lift (step 20; descriptive, computed now for both) | 0.0111 | 0.0183 |
| OOS accuracy vs majority-rate | 0.5411 vs 0.4783 | 0.5194 vs 0.4806 |
| Balanced accuracy (descriptive) | 0.3734 | 0.3564 |
| Dual same-bar exclusions | 0 | 0 |
| Board decision | FAILS | **FAILS** |

## Boundary bars and changed days
- **The 7–9 window edges did change.** The old W was raw labels [07:00, 09:00), which is bars [06:59, 08:59). The corrected W is bars [07:00, 09:00).
  - Of 766 W-eligible rows: O79 changed on 734, C79 on 742, H79 on 65, L79 on 59, R79 on 121.
  - ATR_ref changed on 211 rows.
- The y path now starts at the real cash-open bar instead of the 09:29 bar.
- **Class changed on 13 of 633 primary days (OOS: 4). y changed on 3 primary days (OOS: 0).**
- 2025-01-09 leaves the pool: it has no bar opening ≥09:30.

## Data source and shift check
- Tape used: raw CSV `evidence/tape/KAGGLE_NQ_1M_2022_2025/Dataset_NQ_1min_2022_2025.csv` (1,048,575 rows; last raw label `12/11/2025 20:52` = last bar opening 2025-12-11 20:51 ET; Excel-cap truncation CONFIRMED).
- Shift applied immediately after load: `ts = to_datetime(label, "%m/%d/%Y %H:%M") − 1 min`; raw label kept as `label_et_raw`. Calendar date, HH:MM, and time-of-day are all derived from the bar-open `ts`.
- Parquet cross-check (`/workspace/marketdata/data/kaggle/NQ/1m_trade/*.parquet`, read with the marketdata venv because hxvenv has no pyarrow and its pip is broken): all 1,048,575 rows matched on `ts_ny` (tz stripped) == raw label − 1 min. Open/high/low/close mismatches: **0 / 0 / 0 / 0**. Spot rows, e.g. raw `12/12/2024 4:00` → ts_ny 2024-12-12 03:59, O/H/L/C 22951.50/22952.25/22949.75/22950.00 in both; raw `6/17/2025 13:37` → 13:36, 22536.75/22537.75/22531.50/22536.75 in both.
- Frozen protocol logic, seeds, splits, event calendar (`H001b_event_calendar_2023_2025.csv`, read and **not** rewritten), and holiday/early-close sets are unchanged.
- **Old-number check:** before the re-run, the original script was re-run with only its output paths redirected (`/workspace/labelfix/replay_*.py`). Its day-row CSV was **byte-identical** to the 2026-09-13 file, so the OLD column below is a verified reproduction.

## Appendix — full re-run output (script-generated, bar-open)
The script's automatic "Decision" line below is the **protocol-locked hard-majority gate**. CASSANDRA rejected it as a board SURVIVES and ORION locked the board call as FAILS. It is relabelled here so it cannot be misread.

### [script output] H002b EXPLORATORY RESULTS — 2026-09-13

**Stream label (mandatory):** `CONTINUOUS-KAGGLE-NQ1M` · **roll undocumented** · **Excel truncation FLAG** · **not stream C** · **not MNQ Mar 2026** · no 2026 lecture-day identity

| Field | Value |
|-------|-------|
| Hypothesis | H002b (exploratory) — 7–9 PARAMETER state → first-side-swept y by 12:00 |
| Protocol | `QUANT_H002b_79_STATE_CLASSIFIER_PROTOCOL_2026-09-13.md` |
| Classifier | **PARAMETER** four-class (§3 freeze) — **not** Observed trending/consolidating/reversing identity |
| Parents | C-METH-003, C-METH-004, C-METH-005 (Passed Observed only) |
| DATA gate | `DATA_GATE_KAGGLE_NQ_1M_2026-09-13.md` · PASS WITH CONDITIONS |
| Primary pool | **non-event** days (H001b CPI/FOMC/NFP calendar) |
| Split | Calendar **IS 2023–2024 / OOS 2025** |
| Score | OOS multiclass log-loss lift vs IS-majority constant |
| Vocabulary | SURVIVES ≠ trade permission · **No MERCURY** · do not run H002 |
| §3 freeze hash | `074d6a83ccf5289cf654b26c4cd747ea9b3bbe1c4671c1c65aa598b9f3eb3464` (OK) |
| Script | `/workspace/h002b_run_labelfix.py` |

#### Tape integrity

- Path: `/home/box/hermes-x/investigations/INV-002-methodology-seed/evidence/tape/KAGGLE_NQ_1M_2022_2025/Dataset_NQ_1min_2022_2025.csv`
- Rows loaded: **1,048,575**
- Last timestamp (bar open): **2025-12-11 20:51:00** (= raw label 20:52)
- **FLAG:** n = 1,048,575 — Excel-row truncation CONFIRMED (DATA 2026-10-04).
- Instrument: NQ continuous · roll undocumented · VWAP ignored.
- Labels: CONTINUOUS-KAGGLE-NQ1M · not stream C · not MNQ Mar 2026.

#### Code freeze

Canonical §3 table sha256 verified **before** fitting:

```
ATR lookback=20
Expansion multiplier=1.0
Body fraction=0.5
Compression multiplier=0.5
expansion↑: C>O and R>=1.0*ATR and (C-O)/R>=0.5
expansion↓: C<O and R>=1.0*ATR and (O-C)/R>=0.5
compression: R<=0.5*ATR
consolidation: else
```

**Hash:** `074d6a83ccf5289cf654b26c4cd747ea9b3bbe1c4671c1c65aa598b9f3eb3464` = expected `074d6a83ccf5289cf654b26c4cd747ea9b3bbe1c4671c1c65aa598b9f3eb3464` → **OK**

#### Decision

| Layer | Label |
|-------|-------|
| **Protocol-locked hard-majority gate (NOT the board call)** | mechanical pass, REJECTED; **board = FAILS** (soft empirical prior) |

Hard-majority gate mechanics (rejected baseline): lift>0, CI(lift) entirely >0, WF median lift>0; PARAMETER classifier implementing 003–005 precursor — not a panacea (005). Persistence is sensitivity only.

This is a **PARAMETER classifier implementing 003–005 precursor** — **not** Observed class identity. It is **not a panacea** (Passed 005). No MERCURY · no trade permission · persistence sensitivity cannot sole-SURVIVES.

#### Coverage / exclusions

| Pool / gate | Count |
|-------------|------:|
| Primary non-event valid (class+y) | 633 |
| Primary IS 2023–2024 | 427 |
| Primary OOS 2025 | 206 |
| All-days valid (incl. events) | 724 |
| Coverage ≥20 | PASS |
| OOS N≥80 | PASS |

Exclusion reasons (calendar years ≥2023, all ex-Sunday W-eligible rows):

| excl_reason | N |
|-------------|--:|
| (none / eligible path) | 724 |
| holiday | 22 |
| no_atr | 15 |
| no_path | 1 |

#### Class counts (PARAMETER classifier)

| Class | IS | OOS |
|-------|---:|----:|
| expansion↑ | 65 | 23 |
| expansion↓ | 62 | 25 |
| compression | 22 | 8 |
| consolidation | 278 | 150 |
| **total** | **427** | **206** |

**Rare-class note:** no class below informal thinness flags (IS<10 / OOS<5).

### y distribution

| y | IS | OOS |
|---|---:|----:|
| high | 227 | 99 |
| low | 197 | 105 |
| neither | 3 | 2 |
| **total** | **427** | **206** |

IS-majority y (baseline constant): **high**

#### PRIMARY — multinomial class→y vs IS-majority (non-event)

Window W=[07:00,09:00). ATR_ref = median prior 20 ex-Sunday 7–9 R (days < D).
y = first side swept of 7–9 H/L after 09:30 by T*=12:00; dual same-bar excluded.

| Metric | Value |
|--------|------:|
| OOS N | 206 |
| L_base (IS-majority) | 18.721703 |
| L_model | 0.730434 |
| Lift = L_base − L_model | 17.991270 |
| Bootstrap 95% CI(lift) 10k | [15.545883, 20.458319] |
| WF median lift (step 20) | 19.091942 |
| Balanced accuracy (descriptive) | 0.3564 |

WF fold lifts: 11.9983, 24.5177, 21.0100, 19.1368, 13.3538, 15.4560, 19.0919, 20.8203, 15.5170, 19.1964, 17.3246

### Baseline construction note (protocol-locked)

`L_base` uses the **IS-majority hard constant**: probability 1 on the IS modal y and 0 elsewhere (Lock 4). Soft model probs → large mechanical lift under clipped log-loss. Balanced accuracy is descriptive. Empirical-prior constant is descriptive only and cannot flip the locked primary decision.

#### Persistence sensitivity (cannot sole-SURVIVES)

Previous calendar trading day’s class → y. OOS lift=17.970877 CI=[15.541127, 20.431115] L_model=0.750827.
Sensitivity only — **cannot sole-SURVIVES**.

#### Descriptive horizons (cannot flip SURVIVES)

- 10:00: OOS N=206 rates: high=0.471, low=0.485, neither=0.044
- 11:00: OOS N=206 rates: high=0.481, low=0.510, neither=0.010

#### All-days dual-report (descriptive; primary = non-event)

all-days descriptive OOS N=237 L_base=18.4020 L_model=0.7378 lift=17.6642 CI=[15.3902,19.9589] (not primary)

#### Bias hunt checklist

- [x] CONTINUOUS-KAGGLE-NQ1M; truncation FLAG; not stream C; not MNQ Mar 2026
- [x] T*=12:00 primary; 10:00/11:00 descriptive
- [x] y = first side swept ∈ {high, low, neither}; dual same-bar excluded
- [x] Primary score = OOS log-loss lift vs IS-majority; bal-acc descriptive
- [x] Persistence = sensitivity only
- [x] Thresholds frozen 20 / 1.0 / 0.5 / 0.5; no retune from other hyps; §3 hash OK
- [x] ATR days < D; ex Sundays; calendar IS/OOS; primary = non-event
- [x] SURVIVES vocab = PARAMETER precursor + “not a panacea”; no MERCURY; do not run H002

#### Paths

- Results: this file (`H002b_RERUN_LABELFIX_2026-10-04.md`)
- Day rows: `/home/box/hermes-x/investigations/INV-002-methodology-seed/experiments/results/H002b_day_rows_RERUN_LABELFIX_2026-10-04.csv`
- Event calendar: `/home/box/hermes-x/investigations/INV-002-methodology-seed/experiments/results/H001b_event_calendar_2023_2025.csv`
- Script: `/workspace/h002b_run_labelfix.py`


