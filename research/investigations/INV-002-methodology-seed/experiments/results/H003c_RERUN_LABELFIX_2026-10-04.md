# H003c RE-RUN (LABELFIX) — 2026-10-04
`CONTINUOUS-KAGGLE-NQ1M · labels=bar-close (corrected 2026-10-04) · roll undocumented · truncation CONFIRMED (ends 2025-12-11) · not MNQ Mar 2026 · not stream C · No MERCURY`

**Supersedes:** `H003c_EXPLORATORY_RESULTS_2026-09-13.md` (now SUSPENDED) · **Protocol:** `QUANT_H003c_REL_TO_RANGE_PROTOCOL_2026-09-13.md` (frozen) · **Detector:** **PARAMETER REL detector** (1-bar fractal + τ_eq=2.0). It is **not** a red-line identity, and nothing here says it matches the red line. · **Script:** `/workspace/h003c_run_labelfix.py` · **Day rows:** `H003c_day_rows_RERUN_LABELFIX_2026-10-04.csv`

## Decision
| | OLD (label-as-open) | NEW (bar-open) |
|---|---|---|
| **PRIMARY (time-ordered 60/40, script-locked)** | FAILS (primary REL/REH→range + Foil A) | **INCONCLUSIVE (OOS N_treat = 52 < 80)** |
| Calendar co-report (2023–24 IS / 2025 OOS) | FAILS (OOS N_treat 114) | INCONCLUSIVE (OOS N_treat 41 < 80) |

**CHANGED: FAILS → INCONCLUSIVE, on power.** The power loss comes from the protocol's frozen dual-same-bar exclusion meeting the real 09:30 cash-open bar (explained below). It is **not** a rescue. The point estimate moves further negative: OOS Δ **−0.2692 [−0.4123, −0.1235]** and WF median **−0.2630**. Nothing in this re-run supports SURVIVES. No MERCURY.

## Window / horizon convention (bar-open; raw label = bar open + 1 min)
| Object | Bar-open definition | Raw-label range |
|---|---|---|
| 7–9 window W (REL/REH pools, H79/L79) | bars opening **[07:00, 09:00)** | labels **07:01 … 09:00** |
| Post-open touch scan start / Foil A draw "@09:30" | from the bar opening **09:30** | from label **09:31** |
| T* = 12:00 (primary horizon; Foil A control on the same path) | through the **last bar opening 11:59**, i.e. bars [09:30, 12:00) | labels **09:31 … 12:00** |
| 10:00 / 11:00 descriptive horizons | bars [09:30, 10:00) / [09:30, 11:00) | labels 09:31 … 10:00 / 09:31 … 11:00 |

**Implementation note.** The original code used `tod <= 12:00` on raw labels, which happened to end at the right bar (label 12:00 = bar 11:59). After the shift, the DATA §2 rule ("ends at 12:00 = last bar opening 11:59") needs `tod < 12:00`. I changed only those end comparisons (`ENDMODE=datarule`). The pure-shift variant (`tod <= 12:00` in bar-open time, i.e. through label 12:01) was also run as a sensitivity.
- **OOS decision numbers are identical under both variants:** N_treat 52, Δ −0.2692 [−0.4123, −0.1235], WF −0.2630.
- Only IS/Full control rates and the descriptive rival rates move, by ≤0.005.

## OLD vs NEW — every decision number
| Quantity | OLD | NEW |
|---|---|---|
| Candidate days / eligible-range days | 762 / 641 | 762 / 640 |
| Excl holiday / early close / event / no_path | 22 / 7 / 92 / 0 | 22 / 7 / 92 / 1 (2025-01-09 closure) |
| Excl dual same-bar (REL+REH, or REL/REH+range) | 298 (77 + 221) | **517 (194 + 323)** |
| **N_treat IS / OOS / Full (60/40)** | 204 / 139 / 343 | **71 / 52 / 123** |
| N_ctrl IS / OOS / Full | 384 / 257 / 641 | 384 / 256 / 640 |
| P̂_treat / P̂_ctrl OOS | 0.5971 / 0.7471 | 0.4808 / 0.7500 |
| Δ IS [CI] | −0.1069 [−0.1880, −0.0283] | −0.2696 [−0.3963, −0.1439] |
| **Δ OOS [CI]** | −0.1500 [−0.2474, −0.0520] | **−0.2692 [−0.4123, −0.1235]** |
| Δ Full [CI] | −0.1243 [−0.1859, −0.0637] | −0.2691 [−0.3629, −0.1750] |
| **WF median Δ (step 20 treat days)** | −0.1429 (17 folds) | **−0.2630** (6 folds) |
| Pierce-0.25 OOS Δ [CI] | −0.1500 [−0.2464, −0.0568] | −0.2692 [−0.4153, −0.1259] |
| 10:00 / 11:00 descriptive OOS Δ | −0.3370 / −0.2075 | −0.4615 / −0.3269 |
| SELECTION gate (ctrl = touched H79 or L79) Δ [CI] | −0.1313 [−0.1950, −0.0687] | −0.2749 [−0.3701, −0.1813] |
| Tertile-reweighted Δ [CI] | −0.1126 [−0.1742, −0.0511] | −0.2252 [−0.3210, −0.1325] |
| Mid-tertile Δ [CI] | −0.1625 [−0.2649, −0.0590] | −0.2683 [−0.4390, −0.0976] |
| Rival B full N, P̂, Δ | 635, 0.4882, −0.2513 | 635, 0.4866, −0.2540 |
| Rival A full N, P̂ | 282, 0.7553 | 225, 0.6889 |
| Calendar IS 2023–24 N_treat, Δ [CI] | 229, −0.1309 [−0.2063, −0.0546]* | 82, −0.2745 [−0.3889, −0.1588] |
| Calendar OOS 2025 N_treat, Δ [CI] | 114, −0.1111 [−0.2201, −0.0031]* | **41**, −0.2585 [−0.4195, −0.0976] |
| Calendar SELECTION OOS 2025 (N_ctrl), Δ [CI] | (203) −0.1221 [−0.2274, −0.0147]* | (203) −0.2659 [−0.4319, −0.1045] |
| Decision label | FAILS | **INCONCLUSIVE (OOS N_treat < 80)** |

*The OLD calendar CIs are as filed. Recomputing them on the old day rows gives the same point estimates and CIs within ±0.001 (the bootstrap draw order differs).

## Why treatment N collapses (mechanism; no retune)
- Under both conventions, the first REL/REH touch τ is on the **first path bar** on almost every treatment day: **338/343** old, **122/123** new. By 09:30, price has usually already traded through the near-mid REL/REH.
- The old first path bar was raw label 09:30, which is really the **09:29 pre-open bar**: low volume, median range ≈8 pts. The corrected first bar is the **09:30 cash-open bar**: median range ≈25 pts (DATA §1).
- The wider bar touches REL and REH, or REL/REH plus H79/L79, **on the same bar** far more often. The frozen protocol excludes those days as dual same-bar.
- Old treatment days (343) now break down as:
  - 118 still treatment (116 on the same side)
  - 112 → dual REL/REH+range
  - 112 → dual REL+REH
  - 1 → no_path
- 7–9 levels changed on some days, because W lost the 06:59 bar and gained the 08:59 bar: H79 62, L79 59, L_rel 46, H_reh 49 days.
- Foil A I_ctrl changed on 0 days that are eligible in both runs.

**Flag for the board:** the H003c treatment is effectively defined by the state of the opening bar, so the estimand is fragile to the first-bar definition. Reported only; no parameter was changed.

## Data source and shift check
- Tape used: raw CSV `evidence/tape/KAGGLE_NQ_1M_2022_2025/Dataset_NQ_1min_2022_2025.csv` (1,048,575 rows; last raw label `12/11/2025 20:52` = last bar opening 2025-12-11 20:51 ET; Excel-cap truncation CONFIRMED).
- Shift applied immediately after load: `ts = to_datetime(label, "%m/%d/%Y %H:%M") − 1 min`; raw label kept as `label_et_raw`. Calendar date, HH:MM, and time-of-day are all derived from the bar-open `ts`.
- Parquet cross-check (`/workspace/marketdata/data/kaggle/NQ/1m_trade/*.parquet`, read with the marketdata venv because hxvenv has no pyarrow and its pip is broken): all 1,048,575 rows matched on `ts_ny` (tz stripped) == raw label − 1 min. Open/high/low/close mismatches: **0 / 0 / 0 / 0**. Spot rows, e.g. raw `12/12/2024 4:00` → ts_ny 2024-12-12 03:59, O/H/L/C 22951.50/22952.25/22949.75/22950.00 in both; raw `6/17/2025 13:37` → 13:36, 22536.75/22537.75/22531.50/22536.75 in both.
- Frozen protocol logic, seeds, splits, event calendar (`H001b_event_calendar_2023_2025.csv`, read and **not** rewritten), and holiday/early-close sets are unchanged.
- **Old-number check:** before the re-run, the original script was re-run with only its output paths redirected (`/workspace/labelfix/replay_*.py`). Its day-row CSV was **byte-identical** to the 2026-09-13 file, so the OLD column below is a verified reproduction.

## Appendix — full re-run output (script-generated, bar-open, ENDMODE=datarule)
### [script output] H003c EXPLORATORY RESULTS — 2026-09-13

**Stream label (mandatory):** `CONTINUOUS-KAGGLE-NQ1M` · **roll undocumented** · **not MNQ Mar 2026** · **no 2026 lecture-day identity/calibration**

| Field | Value |
|-------|-------|
| Hypothesis | H003c (exploratory) — REL/REH → opposite 7–9 range extreme |
| Protocol | `QUANT_H003c_REL_TO_RANGE_PROTOCOL_2026-09-13.md` |
| Detector | **PARAMETER** 1-bar fractal + τ_eq=2.0 — **not** lecture-locked red-line |
| ATLAS | `H003_BOX_LOCK.md` · `H003c_REL_DETECTOR_LOCK.md` |
| DATA gate | `DATA_GATE_KAGGLE_NQ_1M_2026-09-13.md` · PASS WITH CONDITIONS |
| Control | Foil A @09:30 all eligible range days · seed `H003c_A_{YYYY-MM-DD}` |
| Horizon | T*=12:00 ET only (10:00/11:00 descriptive) |
| Split | time-ordered 60% IS / 40% OOS on eligible-range calendar |
| Vocabulary | SURVIVES ≠ trade permission · **No MERCURY** · no red-line identity |
| Script | `/workspace/h003c_run_labelfix.py` |

#### Tape integrity

- Path: `/home/box/hermes-x/investigations/INV-002-methodology-seed/evidence/tape/KAGGLE_NQ_1M_2022_2025/Dataset_NQ_1min_2022_2025.csv`
- Rows loaded: **1,048,575**
- Last timestamp (bar open): **2025-12-11 20:51:00** (= raw label 20:52)
- **FLAG:** n = 1,048,575 — Excel-row truncation CONFIRMED (DATA 2026-10-04).
- Instrument: NQ continuous · roll undocumented.

#### Decision

| Layer | Label |
|-------|-------|
| **PRIMARY** | **INCONCLUSIVE (OOS N_treat < 80)** |

Banned prose not used: “matches the red line”; bare lecture SURVIVES; H003b/Rival-B as lecture confirmation.

#### Coverage / exclusions

| Reason / pool | Count |
|---------------|------:|
| n_candidate | 762 |
| excl_sunday | 0 |
| excl_holiday | 22 |
| excl_early_close | 7 |
| excl_thin_w | 0 |
| excl_no_path | 1 |
| excl_R79 | 0 |
| excl_event | 92 |
| excl_dual | 517 |
| n_eligible_range | 640 |
| n_has_rel | 640 |
| n_has_reh | 640 |
| n_treat | 123 |
| n_rivalB | 635 |
| n_rivalA | 225 |
| n_no_rel_reh | 0 |

| Split | N_treat | N_ctrl (eligible range) |
|-------|--------:|------------------------:|
| IS | 71 | 384 |
| OOS | 52 | 256 |
| Full | 123 | 640 |

#### PRIMARY — REL/REH sweep → opposite HH/LL vs Foil A

Touch primary. W=[07:00,09:00). L_rel = mean(pair) tick-round 0.25; pair = closest-to-mid among τ_eq=2.0 swing-low pairs.

| Population | N_treat | P̂_treat | N_ctrl | P̂_ctrl | Δ | 95% CI(Δ) |
|------------|--------:|----------|-------:|--------|---|-----------|
| IS 60% | 71 | 0.4648 | 384 | 0.7344 | -0.2696 | [-0.3963, -0.1439] |
| OOS 40% | 52 | 0.4808 | 256 | 0.7500 | -0.2692 | [-0.4123, -0.1235] |
| Full | 123 | 0.4715 | 640 | 0.7406 | -0.2691 | [-0.3629, -0.1750] |

Walk-forward median Δ (step 20 treat days): **-0.2630**
WF fold Δs: -0.3067, -0.3445, -0.1434, -0.2529, -0.2015, -0.2730

### Pierce co-report (sweep def = pierce 0.25)

OOS pierce treatment N=52 P̂=0.4808 Δ=-0.2692 [-0.4153, -0.1259]

### Descriptive horizons (cannot flip SURVIVES)

- 10:00: OOS N=52 P̂_treat=0.2885 Δ=-0.4615
- 11:00: OOS N=52 P̂_treat=0.4231 Δ=-0.3269

#### SELECTION-DEPENDENT gate

Control universe = eligible-range days touching ≥1 of {H79,L79} by 12:00; same Foil A.

| OOS-like full | N_treat=123 N_ctrl=635 Δ=-0.2749 [-0.3701, -0.1813] |

#### Tertile match (mandatory)

R79 tertile edges (from treatment): e1=80.17, e2=113.58
Reweighted Δ: -0.2252 [-0.3210, -0.1325] (P_treat=0.4715, P_ctrl_w=0.6968)

| Tertile | N_treat | N_ctrl | P_treat | P_ctrl | Δ | 95% CI |
|---------|--------:|-------:|--------:|-------:|---|--------|
| 0 | 41 | 422 | 0.5854 | 0.7796 | -0.1943 | [-0.3508, -0.0408] |
| 1 | 41 | 123 | 0.4634 | 0.7317 | -0.2683 | [-0.4390, -0.0976] |
| 2 | 41 | 95 | 0.3659 | 0.5789 | -0.2131 | [-0.3877, -0.0313] |

**RANGE-DEPENDENT mid tertile:** Δ=-0.2683 [-0.4390, -0.0976]

#### Rival maps (not lecture SURVIVES path)

### Rival B (ex-H003b) — first HH/LL sweep → opposite
Full: N_treat=635 P̂=0.4866 Δ=-0.2540 [-0.3044, -0.2008]

### Rival A — REL sweep → aim REH
Full: N=225 P̂=0.6889 (descriptive rate only; no Foil A Δ claimed as primary)

### Detector rivals (τ / selection) — coverage only

| Variant | N days with REL |
|---------|----------------:|
| τ=2.0 closest-mid (primary) | 640 |
| τ=4.0 closest-mid | 640 |
| τ=8.0 closest-mid | 640 |
| τ=2.0 lowest-mean selection | 640 |

#### Appendix — Spot-check 12 random treatment days

| date | H79 | L79 | R79 | L_rel | H_reh | side | I_treat | I_ctrl | S |
|------|----:|----:|----:|------:|------:|------|--------:|------:|---|
| 2023-03-03 | 14797.25 | 14733.75 | 63.50 | 14758.25 | 14764.50 | REH | 0.0 | 1.0 | low |
| 2023-03-06 | 15037.25 | 14956.00 | 81.25 | 15008.50 | 14989.25 | REH | 0.0 | 0.0 | high |
| 2023-03-09 | 14913.25 | 14806.75 | 106.50 | 14818.00 | 14878.00 | REH | 0.0 | 1.0 | low |
| 2023-06-30 | 17608.25 | 17513.50 | 94.75 | 17532.00 | 17540.00 | REH | 0.0 | 0.0 | high |
| 2024-05-31 | 20362.00 | 20208.25 | 153.75 | 20258.75 | 20275.50 | REH | 1.0 | 1.0 | high |
| 2024-08-16 | 21033.50 | 20880.50 | 153.00 | 20979.00 | 20951.00 | REL | 0.0 | 0.0 | high |
| 2024-11-18 | 21781.50 | 21679.50 | 102.00 | 21727.25 | 21735.00 | REH | 0.0 | 1.0 | low |
| 2025-01-08 | 22305.50 | 22133.50 | 172.00 | 22218.75 | 22192.00 | REH | 0.0 | 1.0 | low |
| 2025-02-04 | 22410.50 | 22313.00 | 97.50 | 22358.25 | 22364.00 | REL | 1.0 | 0.0 | high |
| 2025-05-01 | 20744.25 | 20658.00 | 86.25 | 20698.00 | 20705.00 | REL | 1.0 | 1.0 | high |
| 2025-10-13 | 25122.75 | 24989.50 | 133.25 | 25053.25 | 25058.25 | REH | 1.0 | 1.0 | low |
| 2025-11-05 | 25852.50 | 25714.75 | 137.75 | 25777.25 | 25787.00 | REH | 0.0 | 0.0 | high |

#### Reproducibility

- Python: `/workspace/hxvenv/bin/python /workspace/h003c_run_labelfix.py`
- Bootstrap seed: `np.random.default_rng(20260913)`
- Foil A seed: `SHA256("H003c_A_{YYYY-MM-DD}")[:16]`
- Day-level CSV: `H003c_day_rows_RERUN_LABELFIX_2026-10-04.csv`
- Event calendar: reused `H001b_event_calendar_2023_2025.csv`

---
*Exploratory CONTINUOUS-KAGGLE only. PARAMETER detector — not stream C / not MNQ Mar 2026 / not red-line identity. No MERCURY.*

