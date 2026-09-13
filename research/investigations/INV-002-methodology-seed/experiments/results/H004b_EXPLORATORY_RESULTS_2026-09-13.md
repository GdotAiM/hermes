# H004b EXPLORATORY RESULTS — 2026-09-13

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
| Script | `/workspace/h004b_run.py` |
| **No MERCURY** | SURVIVES ≠ trade permission |

## Tape integrity

- Path: `/home/box/hermes-x/investigations/INV-002-methodology-seed/evidence/tape/KAGGLE_NQ_1M_2022_2025/Dataset_NQ_1min_2022_2025.csv`
- Rows loaded: **1,048,575**
- Last timestamp: **2025-12-11 20:52:00**
- **FLAG:** n = 1,048,575 — possible Excel-row truncation (ends ~2025-12-11).
- VWAP columns **ignored** (OHLCV only).
- Instrument: NQ continuous · roll **undocumented** · **not MNQ Mar 2026** · **not stream C**.

## Coverage table (mandatory before Δ)

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

## Decision

**Primary decision label:** `FAILS`

Reason: OOS Δ=0.0049 CI=[-0.0683,0.0780] not entirely >0

This tests **first-10:00-hour FVG vs later control** on CONTINUOUS-KAGGLE-NQ1M. **Not** Silver Bullet proof. **No MERCURY.**

## Primary estimand — later same-polarity control

| Split | N_pairs | P̂ m treat | P̂ m later | Δ | 95% CI (paired boot 10k) | NL treat | NL ctrl |
|-------|--------:|----------:|----------:|---|--------------------------|---------:|--------:|
| Full | 640 | 0.7906 | 0.8047 | -0.0141 | [-0.0578, 0.0297] | 0.000 | 0.000 |
| IS 2023–2024 | 435 | 0.7793 | 0.8023 | -0.0230 | [-0.0782, 0.0299] | 0.000 | 0.000 |
| OOS 2025 | 205 | 0.8146 | 0.8098 | 0.0049 | [-0.0683, 0.0780] | 0.000 | 0.000 |

**OOS never-leave rates:** treat=0.000, control=0.000.
Never-leave gap not tagged WIDTH-DEPENDENT (threshold: treat > ctrl + 0.10).

## Walk-forward (paired blocks, step ≥20)

- WF median Δ (all pairs chronological): **0.0000**
- Fold Δs: 0.1000, -0.2500, 0.0500, -0.0500, -0.0500, 0.0000, -0.1500, 0.0500, -0.1500, -0.1000, -0.1000, 0.1500, 0.2000, -0.1500, 0.1000, -0.1500, 0.1000, 0.0500, 0.0000, -0.2500, 0.1000, -0.0500, -0.0500, 0.0500, 0.1000, 0.0500, 0.0500, -0.0500, -0.1000, -0.0500, 0.1000, 0.0000
- OOS-only WF median Δ: **0.0000**
- OOS fold Δs: -0.1000, 0.1000, 0.1000, -0.0500, 0.1000, -0.1000, -0.0500, -0.0500, 0.0500, 0.0500, 0.0000

## RTH sensitivity (cannot sole-SURVIVES)

| Split | N_pairs | P̂ m treat | P̂ m RTH | Δ | 95% CI |
|-------|--------:|----------:|--------:|---|--------|
| Full RTH | 640 | 0.7906 | 0.8375 | -0.0469 | [-0.0906, -0.0031] |
| IS RTH | 435 | 0.7793 | 0.8345 | -0.0552 | [-0.1080, -0.0023] |
| OOS RTH | 205 | 0.8146 | 0.8439 | -0.0293 | [-0.1073, 0.0488] |

**RTH sensitivity outcome:** primary not positive; RTH Δ=-0.0293 CI=[-0.1073, 0.0488] N=205 (reported; cannot sole-SURVIVES)

## Polarity stratum (descriptive)

| Split / polarity | N_pairs | Δ | 95% CI |
|-----------------|--------:|---|--------|
| OOS bull | 111 | 0.0180 | [-0.0901, 0.1261] |
| IS bull | 219 | 0.0091 | [-0.0639, 0.0822] |
| OOS bear | 94 | -0.0106 | [-0.1170, 0.0957] |
| IS bear | 216 | -0.0556 | [-0.1343, 0.0231] |

## Zone width / body-expand (descriptive)

- Mean treat zone width: 14.24 pts; later: 8.05 pts
- Body-expanded treat share: 1.000
- Mean MFE treat (descriptive): 57.38; MAE: 62.20 (anchor = birth bar close; cannot flip SURVIVES)

## Secondary (descriptive only — not SURVIVES object)

- Days with second FVG in [10:00,11:00): 640
- P̂ m secondary: 0.7828

## Falsification checklist (OOS)

| Criterion | Result |
|-----------|--------|
| N_pairs ≥ 80 | 205 → PASS |
| Δ > 0 | 0.0049 → PASS |
| CI entirely > 0 | [-0.0683, 0.0780] → FAIL |
| WF median Δ > 0 | 0.0000 → FAIL |
| RTH does not flip | primary not positive; RTH Δ=-0.0293 CI=[-0.1073, 0.0488] N=205 (reported; cannot sole-SURVIVES) |
| **Decision** | **FAILS** |

## Reproducibility

- Python: `/workspace/hxvenv/bin/python /workspace/h004b_run.py`
- Bootstrap seed: `np.random.default_rng(20260913)`
- Later control seed: `SHA256("H004b_later_{YYYY-MM-DD}")[:16]`
- RTH control seed: `SHA256("H004b_rth_{YYYY-MM-DD}")[:16]`
- Birth: classic wick FVG only; body gap expands zone (UNION) after birth — no body-only birth (R1)
- Event calendar: reused `H001b_event_calendar_2023_2025.csv`
- Day-level CSV: `/home/box/hermes-x/investigations/INV-002-methodology-seed/experiments/results/H004b_day_rows.csv`

---
*Exploratory CONTINUOUS-KAGGLE-NQ1M only. Roll undocumented · Excel truncation FLAG · not MNQ Mar 2026 · not stream C · not Silver Bullet proof. No MERCURY.*

## CASSANDRA results red-team (2026-09-13)

`reviews/CASSANDRA_H004b_RESULTS_REDTEAM_2026-09-13.md` — **Agree: FAILS**.

Hygiene PASS (N=205; never-leave 0/0). No SURVIVES / no Silver Bullet / no MERCURY. **Ban “near miss” prose.**  
Notes (non-rescuing): `no_first10_fvg=0`; body-expand share 1.0 + wider treat zones = optional QA only; RTH sensitivity also non-positive.

**Board decision (QUANT + CASSANDRA):** **FAILS** — first-10:00-hour FVG vs later same-polarity control on CONTINUOUS-KAGGLE-NQ1M.
