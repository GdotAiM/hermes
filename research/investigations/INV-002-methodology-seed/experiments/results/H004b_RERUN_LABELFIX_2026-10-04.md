# H004b RE-RUN (LABELFIX) — 2026-10-04
`CONTINUOUS-KAGGLE-NQ1M · labels=bar-close (corrected 2026-10-04) · roll undocumented · truncation CONFIRMED (ends 2025-12-11) · not MNQ Mar 2026 · not stream C · No MERCURY`

**Replaces (re-check of):** `H004b_EXPLORATORY_RESULTS_2026-09-13.md` · **Protocol:** `QUANT_H004b_FIRST_1000_FVG_PROTOCOL_2026-09-13.md` (frozen) · **Script:** `/workspace/h004b_run_labelfix.py` · **Day rows:** `H004b_day_rows_RERUN_LABELFIX_2026-10-04.csv`
**Object:** a **first-10:00-hour FVG vs later same-polarity control** test. It is **not** Silver Bullet proof or any named-model endorsement.

## Decision
| | OLD | NEW |
|---|---|---|
| Primary (OOS 2025, first-10:00-hour FVG vs later [11:00,15:00) control) | FAILS | **FAILS** |

**UNCHANGED.** OOS Δ = **0.0293 [−0.0439, 0.1024]** (old 0.0049 [−0.0683, 0.0780]). The CI includes 0, so the CI gate fails and the label is FAILS.
- OOS WF median Δ is now 0.0500 (old 0.0000).
- RTH sensitivity stays non-positive: −0.0098 [−0.0878, 0.0683].

No MERCURY; no trade permission.

## Window / horizon convention (bar-open; raw label = bar open + 1 min)
| Object | Bar-open definition | Raw-label range |
|---|---|---|
| Treatment window U (birth bar t; the 10:00 candle may be t) | births on bars opening **[10:00, 11:00)** | labels **10:01 … 11:00** |
| Later control universe | births on bars opening [11:00, 15:00) | labels 11:01 … 15:00 |
| RTH sensitivity universe | births on bars opening [09:30, 15:30) | labels 09:31 … 15:30 |
| Thin-RTH check | bars opening [09:30, 16:00) | labels 09:31 … 16:00 |
| Path / session cap for m and MFE/MAE | through the **last bar opening 15:59** | through label **16:00** |
| 60-min revisit deadline | leave-bar open + 60 min, inclusive (relative, so unaffected by the shift) | — |
| FVG detection | per bar-open calendar date | — |

**Implementation note.** The original cap was `ts > 16:00 → stop` on labels (last bar 15:59). With bar-open ts, that becomes a cap at 15:59 (`ENDMODE=datarule`). The pure-shift variant, which would include the bar opening 16:00, gave **identical** decision numbers; only later-control MFE/MAE moved.

## OLD vs NEW — every decision number
| Quantity | OLD | NEW |
|---|---|---|
| Exclusions sunday / holiday / early / event / thin_rth | 151 / 27 / 7 / 92 / 1 | 151 / 27 / 7 / 92 / 1 |
| **Paired N IS / OOS / Full** | 435 / 205 / 640 | **435 / 205 / 640** |
| P̂_treat / P̂_later OOS | 0.8146 / 0.8098 | 0.8293 / 0.8000 |
| **Δ OOS [CI]** | 0.0049 [−0.0683, 0.0780] | **0.0293 [−0.0439, 0.1024]** |
| Δ IS [CI] | −0.0230 [−0.0782, 0.0299] (0.7793 vs 0.8023) | −0.0230 [−0.0782, 0.0299] (0.7862 vs 0.8092) |
| Δ Full [CI] | −0.0141 [−0.0578, 0.0297] | −0.0063 [−0.0500, 0.0375] |
| **WF median Δ OOS / full** | 0.0000 / 0.0000 | **0.0500** / 0.0000 |
| RTH-sensitivity Δ OOS [CI] | −0.0293 [−0.1073, 0.0488] | −0.0098 [−0.0878, 0.0683] |
| RTH Δ Full [CI] | −0.0469 [−0.0906, −0.0031] | −0.0312 [−0.0734, 0.0109] |
| Never-leave share OOS treat / ctrl | 0.000 / 0.000 | 0.000 / 0.000 |
| Polarity OOS bull Δ / bear Δ | 0.0180 / −0.0106 | 0.0180 / 0.0426 |
| Mean zone width treat / later | 14.24 / 8.05 | 15.06 / 7.83 |
| Secondary-in-hour P̂ m | 0.7828 | 0.7797 |
| Gates: Δ>0 / CI>0 / WF>0 | PASS / FAIL / FAIL | PASS / FAIL / PASS |
| Decision | FAILS | **FAILS** |

## Boundary bars and changed days
- **The old treatment window was really bars opening [09:59, 10:59).** On **111 of 640 days (17%)**, the old "first 10:00-hour FVG" was born on the **09:59 bar** (raw label 10:00), which is outside the 10:00 hour.
  - All 111 of those days get a different treatment FVG in the re-run.
  - The other 529 days keep the same physical treatment bar and polarity.
- In the corrected run, the treatment is born on the bar opening exactly 10:00 on 107 days, and on the 10:59 edge bar on 0 days.
- Later control: 534/640 days keep the same physical control FVG. In the old run, 3 days drew a control born on the 10:59 bar (label 11:00), which is outside [11:00, 15:00). In the corrected run, no days draw on the 14:59 edge bar.
- Outcome m changed on 26 days (treatment) and 25 days (later control).
- Coverage and exclusion counts are unchanged.

## Data source and shift check
- Tape used: raw CSV `evidence/tape/KAGGLE_NQ_1M_2022_2025/Dataset_NQ_1min_2022_2025.csv` (1,048,575 rows; last raw label `12/11/2025 20:52` = last bar opening 2025-12-11 20:51 ET; Excel-cap truncation CONFIRMED).
- Shift applied immediately after load: `ts = to_datetime(label, "%m/%d/%Y %H:%M") − 1 min`; raw label kept as `label_et_raw`. Calendar date, HH:MM, and time-of-day are all derived from the bar-open `ts`.
- Parquet cross-check (`/workspace/marketdata/data/kaggle/NQ/1m_trade/*.parquet`, read with the marketdata venv because hxvenv has no pyarrow and its pip is broken): all 1,048,575 rows matched on `ts_ny` (tz stripped) == raw label − 1 min. Open/high/low/close mismatches: **0 / 0 / 0 / 0**. Spot rows, e.g. raw `12/12/2024 4:00` → ts_ny 2024-12-12 03:59, O/H/L/C 22951.50/22952.25/22949.75/22950.00 in both; raw `6/17/2025 13:37` → 13:36, 22536.75/22537.75/22531.50/22536.75 in both.
- Frozen protocol logic, seeds, splits, event calendar (`H001b_event_calendar_2023_2025.csv`, read and **not** rewritten), and holiday/early-close sets are unchanged.
- **Old-number check:** before the re-run, the original script was re-run with only its output paths redirected (`/workspace/labelfix/replay_*.py`). Its day-row CSV was **byte-identical** to the 2026-09-13 file, so the OLD column below is a verified reproduction.

## Appendix — full re-run output (script-generated, bar-open)
### [script output] H004b EXPLORATORY RESULTS — 2026-09-13

**Stream label (mandatory):** `CONTINUOUS-KAGGLE-NQ1M` · **roll undocumented** · **Excel truncation FLAG** · **not MNQ Mar 2026** · **not stream C** · **not Silver Bullet proof**

| Field | Value |
|-------|-------|
| Hypothesis | H004b (exploratory) |
| Protocol | `QUANT_H004b_FIRST_1000_FVG_PROTOCOL_2026-09-13.md` |
| Packaging | SURVIVED (`CASSANDRA_H004b_REDTEAM`) · R1 classic-wick birth amended |
| ORION | Exploratory RUN authorized |
| Vocabulary | **first-10:00-hour FVG vs later control** — not Silver Bullet brand proof |
| Primary m | I(revisit zone within 60m after leave); never-leave → m=1 |
| Primary control | Uniform draw [11:00,15:00) same polarity; seed `H004b_later_{date}` |
| Sensitivity | Random RTH [09:30,15:30); seed `H004b_rth_{date}` — cannot sole-SURVIVES |
| Split | Calendar **2023–2024 IS / 2025 OOS** |
| Events | CPI/FOMC/NFP excluded (H001b calendar) |
| Holidays | Excluded as H001b (+ CME early closes) |
| Script | `/workspace/h004b_run_labelfix.py` |
| **No MERCURY** | SURVIVES ≠ trade permission |

#### Tape integrity

- Path: `/home/box/hermes-x/investigations/INV-002-methodology-seed/evidence/tape/KAGGLE_NQ_1M_2022_2025/Dataset_NQ_1min_2022_2025.csv`
- Rows loaded: **1,048,575**
- Last timestamp (bar open): **2025-12-11 20:51:00** (= raw label 20:52)
- **FLAG:** n = 1,048,575 — Excel-row truncation CONFIRMED (DATA 2026-10-04) (ends ~2025-12-11).
- VWAP columns **ignored** (OHLCV only).
- Instrument: NQ continuous · roll **undocumented** · **not MNQ Mar 2026** · **not stream C**.

#### Coverage table (mandatory before Δ)

| Bucket | N |
|--------|--:|
| Calendar days 2023–2025 on tape | 918 |
| Sundays | 151 |
| Holidays | 27 |
| Early closes | 7 |
| Event (CPI/FOMC/NFP) | 92 |
| Thin day / thin RTH | 1 |
| no_first10_fvg | 0 |
| first10_but_no_later_same_polarity | 0 |
| later_control_collide_drop | 0 |
| **Paired days (eligible)** | **640** |
| Paired IS (2023–2024) | 435 |
| Paired OOS (2025) | 205 |
| Of pairs with RTH sensitivity | 640 |

**Coverage projection:** paired N=640 ≥ 20 required before publishing Δ → PASS.

#### Decision

**Primary decision label:** `FAILS`

Reason: OOS Δ=0.0293 CI=[-0.0439,0.1024] not entirely >0

This tests **first-10:00-hour FVG vs later control** on CONTINUOUS-KAGGLE-NQ1M. **Not** Silver Bullet proof. **No MERCURY.**

#### Primary estimand — later same-polarity control

| Split | N_pairs | P̂ m treat | P̂ m later | Δ | 95% CI (paired boot 10k) | NL treat | NL ctrl |
|-------|--------:|----------:|----------:|---|--------------------------|---------:|--------:|
| Full | 640 | 0.8000 | 0.8063 | -0.0063 | [-0.0500, 0.0375] | 0.000 | 0.000 |
| IS 2023–2024 | 435 | 0.7862 | 0.8092 | -0.0230 | [-0.0782, 0.0299] | 0.000 | 0.000 |
| OOS 2025 | 205 | 0.8293 | 0.8000 | 0.0293 | [-0.0439, 0.1024] | 0.000 | 0.000 |

**OOS never-leave rates:** treat=0.000, control=0.000.
Never-leave gap not tagged WIDTH-DEPENDENT (threshold: treat > ctrl + 0.10).

#### Walk-forward (paired blocks, step ≥20)

- WF median Δ (all pairs chronological): **0.0000**
- Fold Δs: 0.1500, -0.2000, 0.0000, -0.1500, 0.1000, 0.0000, -0.1500, 0.0500, -0.1500, -0.0500, -0.1000, 0.2000, 0.1500, -0.0500, 0.1000, -0.1500, 0.1500, -0.2000, -0.0500, -0.2500, 0.0500, 0.0000, 0.0500, 0.1500, 0.1000, 0.1000, 0.0500, 0.0000, -0.1500, -0.1000, 0.1500, 0.0000
- OOS-only WF median Δ: **0.0500**
- OOS fold Δs: 0.0000, 0.2000, 0.0500, 0.0500, 0.1000, -0.0500, -0.1000, -0.1000, 0.1000, 0.0500, 0.0000

#### RTH sensitivity (cannot sole-SURVIVES)

| Split | N_pairs | P̂ m treat | P̂ m RTH | Δ | 95% CI |
|-------|--------:|----------:|--------:|---|--------|
| Full RTH | 640 | 0.8000 | 0.8313 | -0.0312 | [-0.0734, 0.0109] |
| IS RTH | 435 | 0.7862 | 0.8276 | -0.0414 | [-0.0943, 0.0115] |
| OOS RTH | 205 | 0.8293 | 0.8390 | -0.0098 | [-0.0878, 0.0683] |

**RTH sensitivity outcome:** primary not positive; RTH Δ=-0.0098 CI=[-0.0878, 0.0683] N=205 (reported; cannot sole-SURVIVES)

#### Polarity stratum (descriptive)

| Split / polarity | N_pairs | Δ | 95% CI |
|-----------------|--------:|---|--------|
| OOS bull | 111 | 0.0180 | [-0.0811, 0.1171] |
| IS bull | 220 | 0.0000 | [-0.0727, 0.0727] |
| OOS bear | 94 | 0.0426 | [-0.0638, 0.1489] |
| IS bear | 215 | -0.0465 | [-0.1256, 0.0326] |

#### Zone width / body-expand (descriptive)

- Mean treat zone width: 15.06 pts; later: 7.83 pts
- Body-expanded treat share: 1.000
- Mean MFE treat (descriptive): 56.43; MAE: 62.53 (anchor = birth bar close; cannot flip SURVIVES)

#### Secondary (descriptive only — not SURVIVES object)

- Days with second FVG in [10:00,11:00): 640
- P̂ m secondary: 0.7797

#### Falsification checklist (OOS)

| Criterion | Result |
|-----------|--------|
| N_pairs ≥ 80 | 205 → PASS |
| Δ > 0 | 0.0293 → PASS |
| CI entirely > 0 | [-0.0439, 0.1024] → FAIL |
| WF median Δ > 0 | 0.0500 → PASS |
| RTH does not flip | primary not positive; RTH Δ=-0.0098 CI=[-0.0878, 0.0683] N=205 (reported; cannot sole-SURVIVES) |
| **Decision** | **FAILS** |

#### Reproducibility

- Python: `/workspace/hxvenv/bin/python /workspace/h004b_run_labelfix.py`
- Bootstrap seed: `np.random.default_rng(20260913)`
- Later control seed: `SHA256("H004b_later_{YYYY-MM-DD}")[:16]`
- RTH control seed: `SHA256("H004b_rth_{YYYY-MM-DD}")[:16]`
- Birth: classic wick FVG only; body gap expands zone (UNION) after birth — no body-only birth (R1)
- Event calendar: reused `H001b_event_calendar_2023_2025.csv`
- Day-level CSV: `/home/box/hermes-x/investigations/INV-002-methodology-seed/experiments/results/H004b_day_rows_RERUN_LABELFIX_2026-10-04.csv`

---
*Exploratory CONTINUOUS-KAGGLE-NQ1M only. Roll undocumented · Excel truncation FLAG · not MNQ Mar 2026 · not stream C · not Silver Bullet proof. No MERCURY.*

