# H002b EXPLORATORY RESULTS — 2026-09-13

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
| Script | `/workspace/h002b_run.py` |

## Tape integrity

- Path: `/home/box/hermes-x/investigations/INV-002-methodology-seed/evidence/tape/KAGGLE_NQ_1M_2022_2025/Dataset_NQ_1min_2022_2025.csv`
- Rows loaded: **1,048,575**
- Last timestamp: **2025-12-11 20:52:00**
- **FLAG:** n = 1,048,575 — possible Excel-row truncation.
- Instrument: NQ continuous · roll undocumented · VWAP ignored.
- Labels: CONTINUOUS-KAGGLE-NQ1M · not stream C · not MNQ Mar 2026.

## Code freeze

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

## Decision

| Layer | Label |
|-------|-------|
| **PRIMARY (protocol-locked hard majority)** | **REJECTED as board SURVIVES** (CASSANDRA) |
| **BOARD CALL** | **FAILS** (vs IS empirical-frequency constant prior) |

CASSANDRA: hard one-hot IS-majority + clipped log-loss is a strawman; mechanical lift≠precursor skill. Empirical-prior descriptive lift≈0.017 CI includes ≤0 → **FAILS**. Bal-acc≈0.37≈chance. Persistence same artifact. Re-lock baseline → **H002c** (OOS peeked).

This is a **PARAMETER classifier implementing 003–005 precursor** — **not** Observed class identity. It is **not a panacea** (Passed 005). No MERCURY · no trade permission · persistence sensitivity cannot sole-SURVIVES.

## Coverage / exclusions

| Pool / gate | Count |
|-------------|------:|
| Primary non-event valid (class+y) | 634 |
| Primary IS 2023–2024 | 427 |
| Primary OOS 2025 | 207 |
| All-days valid (incl. events) | 725 |
| Coverage ≥20 | PASS |
| OOS N≥80 | PASS |

Exclusion reasons (calendar years ≥2023, all ex-Sunday W-eligible rows):

| excl_reason | N |
|-------------|--:|
| (none / eligible path) | 725 |
| holiday | 22 |
| no_atr | 15 |

## Class counts (PARAMETER classifier)

| Class | IS | OOS |
|-------|---:|----:|
| expansion↑ | 68 | 22 |
| expansion↓ | 60 | 26 |
| compression | 22 | 8 |
| consolidation | 277 | 151 |
| **total** | **427** | **207** |

**Rare-class note:** compression OOS n=8 is thin (above OOS<5 flag but sparse); neither y is rare (IS=3, OOS=3).

### y distribution

| y | IS | OOS |
|---|---:|----:|
| high | 226 | 99 |
| low | 198 | 105 |
| neither | 3 | 3 |
| **total** | **427** | **207** |

IS-majority y (baseline constant): **high**

## PRIMARY — multinomial class→y vs IS-majority (non-event)

Window W=[07:00,09:00). ATR_ref = median prior 20 ex-Sunday 7–9 R (days < D).
y = first side swept of 7–9 H/L after 09:30 by T*=12:00; dual same-bar excluded.

| Metric | Value |
|--------|------:|
| OOS N | 207 |
| L_base (IS-majority) | 18.805384 |
| L_model | 0.749479 |
| Lift = L_base − L_model | 18.055906 |
| Bootstrap 95% CI(lift) 10k | [15.597970, 20.493273] |
| WF median lift (step 20) | 17.361712 |
| Balanced accuracy (descriptive) | 0.3734 |

WF fold lifts: 13.5646, 22.7122, 22.7867, 17.3617, 15.1670, 13.6786, 20.8797, 19.0649, 17.2864, 19.2021, 14.7503


### Baseline construction note (protocol-locked)

`L_base` uses the **IS-majority hard constant**: probability 1 on the IS modal y (`high`) and 0 elsewhere, per Lock 4 (“IS-majority class constant predictor”). Under multiclass log-loss with probability clipping this yields a large absolute `L_base` whenever OOS y ≠ majority (here ~52% of OOS days). Soft multinomial probabilities therefore produce a large mechanical lift. **Balanced accuracy (descriptive) = 0.3734** (3-class) and accuracy ≈ 0.54 vs majority-rate ≈ 0.48 on OOS — discrimination is weak.

**Descriptive (non-decision) empirical-prior constant baseline** (IS class frequencies, not locked primary): L_base≈0.7660, L_model≈0.7495, lift≈0.0165, bootstrap 95% CI ≈ [-0.0253, 0.0566] (includes ≤0). Cannot flip the locked primary decision; informs “not a panacea”.

OOS compression n=8 is thin (rare-class caution for that cell). Dual same-bar exclusions: 0 in this tape pass.

## Persistence sensitivity (cannot sole-SURVIVES)

Previous calendar trading day’s class → y. OOS lift=18.030897 CI=[15.626542, 20.442310] L_model=0.774487.
Sensitivity only — **cannot sole-SURVIVES**.

## Descriptive horizons (cannot flip SURVIVES)

- 10:00: OOS N=207 rates: high=0.469, low=0.483, neither=0.048
- 11:00: OOS N=207 rates: high=0.478, low=0.507, neither=0.014

## All-days dual-report (descriptive; primary = non-event)

all-days descriptive OOS N=238 L_base=18.4762 L_model=0.7574 lift=17.7188 CI=[15.4504,19.9582] (not primary)

## Bias hunt checklist

- [x] CONTINUOUS-KAGGLE-NQ1M; truncation FLAG; not stream C; not MNQ Mar 2026
- [x] T*=12:00 primary; 10:00/11:00 descriptive
- [x] y = first side swept ∈ {high, low, neither}; dual same-bar excluded
- [x] Primary score = OOS log-loss lift vs IS-majority; bal-acc descriptive
- [x] Persistence = sensitivity only
- [x] Thresholds frozen 20 / 1.0 / 0.5 / 0.5; no retune from other hyps; §3 hash OK
- [x] ATR days < D; ex Sundays; calendar IS/OOS; primary = non-event
- [x] SURVIVES vocab = PARAMETER precursor + “not a panacea”; no MERCURY; do not run H002

## Paths

- Results: `/home/box/hermes-x/investigations/INV-002-methodology-seed/experiments/results/H002b_EXPLORATORY_RESULTS_2026-09-13.md`
- Day rows: `/home/box/hermes-x/investigations/INV-002-methodology-seed/experiments/results/H002b_day_rows.csv`
- Event calendar: `/home/box/hermes-x/investigations/INV-002-methodology-seed/experiments/results/H001b_event_calendar_2023_2025.csv`
- Script: `/workspace/h002b_run.py`

## CASSANDRA results red-team (2026-09-13)

`reviews/CASSANDRA_H002b_RESULTS_REDTEAM_2026-09-13.md` — **REJECT board SURVIVES.**

Preferred board call: **FAILS** (vs proper IS empirical-frequency constant baseline).  
Packaging underspecified hard-majority log-loss. **H002c** required if re-locking baseline (this OOS already peeked).  
Vocab stands: PARAMETER / not panacea / no MERCURY / not Observed identity. Rare compression OOS n=8 noted.

**QUANT agrees:** do not narrate SURVIVES or strong predictive edge.

## ORION BOARD LOCK (2026-09-13)

**H002b = FAILS** (Option A). CASSANDRA rejects protocol SURVIVES; soft empirical-prior is the scientific comparison.  
Ban strong-edge / SURVIVES narration. **H002c not queued** unless human/ORION opens on unseen weeks.  
**Wave 1 Kaggle exploratory chapter CLOSED.** No MERCURY.
