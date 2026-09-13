# H003c EXPLORATORY RESULTS — 2026-09-13

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
| Script | `/workspace/h003c_run.py` |

## Tape integrity

- Path: `/home/box/hermes-x/investigations/INV-002-methodology-seed/evidence/tape/KAGGLE_NQ_1M_2022_2025/Dataset_NQ_1min_2022_2025.csv`
- Rows loaded: **1,048,575**
- Last timestamp: **2025-12-11 20:52:00**
- **FLAG:** n = 1,048,575 — possible Excel-row truncation.
- Instrument: NQ continuous · roll undocumented.

## Decision

| Layer | Label |
|-------|-------|
| **PRIMARY** | **FAILS (primary REL/REH→range + Foil A)** |

Banned prose not used: “matches the red line”; bare lecture SURVIVES; H003b/Rival-B as lecture confirmation.

## Coverage / exclusions

| Reason / pool | Count |
|---------------|------:|
| n_candidate | 762 |
| excl_sunday | 0 |
| excl_holiday | 22 |
| excl_early_close | 7 |
| excl_thin_w | 0 |
| excl_no_path | 0 |
| excl_R79 | 0 |
| excl_event | 92 |
| excl_dual | 298 |
| n_eligible_range | 641 |
| n_has_rel | 641 |
| n_has_reh | 641 |
| n_treat | 343 |
| n_rivalB | 635 |
| n_rivalA | 282 |
| n_no_rel_reh | 0 |

| Split | N_treat | N_ctrl (eligible range) |
|-------|--------:|------------------------:|
| IS | 204 | 384 |
| OOS | 139 | 257 |
| Full | 343 | 641 |

## PRIMARY — REL/REH sweep → opposite HH/LL vs Foil A

Touch primary. W=[07:00,09:00). L_rel = mean(pair) tick-round 0.25; pair = closest-to-mid among τ_eq=2.0 swing-low pairs.

| Population | N_treat | P̂_treat | N_ctrl | P̂_ctrl | Δ | 95% CI(Δ) |
|------------|--------:|----------|-------:|--------|---|-----------|
| IS 60% | 204 | 0.6275 | 384 | 0.7344 | -0.1069 | [-0.1880, -0.0283] |
| OOS 40% | 139 | 0.5971 | 257 | 0.7471 | -0.1500 | [-0.2474, -0.0520] |
| Full | 343 | 0.6152 | 641 | 0.7395 | -0.1243 | [-0.1859, -0.0637] |

Walk-forward median Δ (step 20 treat days): **-0.1429**
WF fold Δs: -0.1429, 0.0333, -0.1429, -0.1895, -0.2278, -0.0389, -0.1179, -0.0609, 0.0227, -0.1597, -0.2955, -0.1097, 0.0500, -0.2838, -0.1857, 0.0821, -0.1931

### Pierce co-report (sweep def = pierce 0.25)

OOS pierce treatment N=139 P̂=0.5971 Δ=-0.1500 [-0.2464, -0.0568]

### Descriptive horizons (cannot flip SURVIVES)

- 10:00: OOS N=139 P̂_treat=0.4101 Δ=-0.3370
- 11:00: OOS N=139 P̂_treat=0.5396 Δ=-0.2075

## SELECTION-DEPENDENT gate

Control universe = eligible-range days touching ≥1 of {H79,L79} by 12:00; same Foil A.

| OOS-like full | N_treat=343 N_ctrl=635 Δ=-0.1313 [-0.1950, -0.0687] |

## Tertile match (mandatory)

R79 tertile edges (from treatment): e1=59.00, e2=88.75
Reweighted Δ: -0.1126 [-0.1742, -0.0511] (P_treat=0.6152, P_ctrl_w=0.7278)

| Tertile | N_treat | N_ctrl | P_treat | P_ctrl | Δ | 95% CI |
|---------|--------:|-------:|--------:|-------:|---|--------|
| 0 | 115 | 267 | 0.7130 | 0.7903 | -0.0772 | [-0.1755, 0.0148] |
| 1 | 117 | 206 | 0.6239 | 0.7864 | -0.1625 | [-0.2649, -0.0590] |
| 2 | 111 | 168 | 0.5045 | 0.6012 | -0.0967 | [-0.2164, 0.0232] |

**RANGE-DEPENDENT mid tertile:** Δ=-0.1625 [-0.2649, -0.0590]

## Rival maps (not lecture SURVIVES path)

### Rival B (ex-H003b) — first HH/LL sweep → opposite
Full: N_treat=635 P̂=0.4882 Δ=-0.2513 [-0.3029, -0.1981]

### Rival A — REL sweep → aim REH
Full: N=282 P̂=0.7553 (descriptive rate only; no Foil A Δ claimed as primary)

### Detector rivals (τ / selection) — coverage only

| Variant | N days with REL |
|---------|----------------:|
| τ=2.0 closest-mid (primary) | 641 |
| τ=4.0 closest-mid | 641 |
| τ=8.0 closest-mid | 641 |
| τ=2.0 lowest-mean selection | 641 |

## Appendix — Spot-check 12 random treatment days

| date | H79 | L79 | R79 | L_rel | H_reh | side | I_treat | I_ctrl | S |
|------|----:|----:|----:|------:|------:|------|--------:|------:|---|
| 2023-03-27 | 15482.25 | 15436.00 | 46.25 | 15459.25 | 15459.25 | REL | 1.0 | 1.0 | low |
| 2023-04-11 | 15708.25 | 15650.25 | 58.00 | 15675.75 | 15680.75 | REH | 1.0 | 1.0 | high |
| 2023-07-28 | 18098.25 | 18033.25 | 65.00 | 18069.50 | 18065.75 | REH | 0.0 | 0.0 | high |
| 2024-04-18 | 19418.25 | 19357.25 | 61.00 | 19387.25 | 19388.50 | REL | 1.0 | 1.0 | high |
| 2024-04-22 | 18997.50 | 18940.00 | 57.50 | 18967.00 | 18974.25 | REH | 1.0 | 1.0 | low |
| 2024-08-07 | 19894.75 | 19811.00 | 83.75 | 19844.75 | 19850.25 | REH | 1.0 | 1.0 | low |
| 2024-11-27 | 22168.75 | 22114.50 | 54.25 | 22140.50 | 22141.50 | REL | 0.0 | 1.0 | high |
| 2025-01-27 | 22086.75 | 21906.00 | 180.75 | 21998.50 | 22010.50 | REH | 0.0 | 0.0 | high |
| 2025-03-14 | 20445.50 | 20336.00 | 109.50 | 20387.75 | 20389.50 | REL | 1.0 | 0.0 | high |
| 2025-06-23 | 22378.25 | 22269.00 | 109.25 | 22310.75 | 22317.50 | REH | 1.0 | 1.0 | high |
| 2025-10-30 | 26543.50 | 26346.75 | 196.75 | 26513.50 | 26431.75 | REL | 0.0 | 1.0 | high |
| 2025-11-05 | 25852.50 | 25714.75 | 137.75 | 25777.25 | 25787.00 | REH | 0.0 | 0.0 | high |

## Reproducibility

- Python: `/workspace/hxvenv/bin/python /workspace/h003c_run.py`
- Bootstrap seed: `np.random.default_rng(20260913)`
- Foil A seed: `SHA256("H003c_A_{YYYY-MM-DD}")[:16]`
- Day-level CSV: `H003c_day_rows.csv`
- Event calendar: reused `H001b_event_calendar_2023_2025.csv`

---
*Exploratory CONTINUOUS-KAGGLE only. PARAMETER detector — not stream C / not MNQ Mar 2026 / not red-line identity. No MERCURY.*

## Calendar split (ORION preferred: 2023–2024 IS / 2025 OOS)

Primary memo above used time-ordered 60/40. Calendar cut co-report:

| Population | N_treat | P̂_treat | N_ctrl | P̂_ctrl | Δ | 95% CI(Δ) |
|------------|--------:|----------|-------:|--------|---|-----------|
| IS 2023-2024 | 229 | 0.6070 | 435 | 0.7379 | -0.1309 | [-0.2063, -0.0546] |
| OOS 2025 | 114 | 0.6316 | 206 | 0.7427 | -0.1111 | [-0.2201, -0.0031] |
| Full | 343 | 0.6152 | 641 | 0.7395 | -0.1243 | [-0.1861, -0.0635] |

SELECTION-DEPENDENT OOS 2025: N_ctrl=203 Δ=-0.1221 [-0.2274, -0.0147]

**Calendar OOS also FAILS** (Δ CI entirely <0; N_treat=114≥80).
