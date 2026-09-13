# QUANT H004b — Experiment Protocol (PACKAGING · NO RUN)
**Hypothesis ID:** **H004b** (NEW id)  
**Supersedes for decision-readiness:** H004 `QUANT_H004_FIRST_1000_FVG_PROTOCOL_2026-09-13.md` (**audit draft only — do not run H004**)  
**Investigation:** INV-002-methodology-seed · Wave 1  
**Parents (Passed Observed only):** C-METH-010, C-METH-011  
**CASSANDRA:** `reviews/CASSANDRA_H004_REDTEAM_2026-09-13.md` → **DID NOT SURVIVE** → this rewrite  
**Author:** QUANT · **Filed:** 2026-09-13  
**Revision class:** Pre-reg packaging rewrite — **no results peeked**  
**Run status:** Packaging **SURVIVED** (`reviews/CASSANDRA_H004b_REDTEAM_2026-09-13.md`). §3.1 hygiene applied (classic-wick birth). **No RUN** until ORION auth + coverage projection ≥20. Do not run H004.  
**No MERCURY**

---

## 0. Why H004b

H004 failed packaging on unlocked primary control, vague volume-imbalance merge, unlocked primary metric / leave-revisit / MFE anchor, and MNQ/stream-C identity. All eight ORION must-locks are frozen below.

---



## 0b. CASSANDRA H004b packaging SURVIVED (2026-09-13)

`reviews/CASSANDRA_H004b_REDTEAM_2026-09-13.md` — all 8 locks PASS.  
Pre-RUN hygiene applied in §3.1: **classic wick FVG required for birth**; body gap expands zone only.  
Still blocked: ORION exploratory auth + coverage projection ≥20 days. No MERCURY. Do not run H004.

---

## 1. Statement (locked)

On **CONTINUOUS-KAGGLE-NQ1M** 1m (America/New_York):

- **Treatment:** first FVG that forms in the **10:00 ET hour** \(U=[10:00,11:00)\) — 10:00 candle may qualify (Passed **010**).  
- Include **volume imbalance** where bodies do not meet (Passed **011**), via the **frozen PARAMETER merge** in §3.1.  
- **Primary comparison:** revisit utility metric \(m\) on treatment vs **later same-day same-polarity** control FVG (§4).  

**Vocabulary:** this tests **first-10:00-hour FVG vs later control** — **not** Silver Bullet brand proof, not a named-model endorsement.

---

## 2. Tape / population (Lock 1 + 6)

| Field | Lock |
|-------|------|
| Stream | **`CONTINUOUS-KAGGLE-NQ1M` only** |
| File | `evidence/tape/KAGGLE_NQ_1M_2022_2025/Dataset_NQ_1min_2022_2025.csv` |
| Labels (every memo) | roll **undocumented** · **Excel truncation FLAG** (n≈1,048,575 → ~2025-12-11) · **not MNQ Mar 2026** · **not stream C identity** · no 2026 lecture-day calibration |
| Bar | 1m · naive ET wall clock |
| Days | RTH days with path through study horizon; exclude Sundays |
| Events | Primary = non-CPI/FOMC/NFP (H001b-style 2023–2025 calendar); report event stratum descriptive |
| IS / OOS | **Calendar 2023–2024 / 2025** (match H001b) — frozen |
| Min N | **≥80 paired days** (treatment + primary control both defined); else INCONCLUSIVE |
| Coverage | Project on ≥20 RTH days before claiming N≥80 reachable; mandatory coverage table before Δ |

VWAP ignored (OHLCV only).

---

## 3. Definitions

### 3.1 FVG + volume-imbalance merge (Lock 3) — ≤10 lines · PARAMETER implementation of 011

**CASSANDRA H004b hygiene (2026-09-13):** birth requires **classic wick FVG**; body gap **expands zone only** — never body-only birth (011 fidelity).

```
Body[i] = [min(O[i],C[i]), max(O[i],C[i])]

# BIRTH gate (required): classic wick FVG only
Classic bullish at t: low[t] > high[t-2]
  wick_gap = [high[t-2], low[t]]
Classic bearish at t: high[t] < low[t-2]
  wick_gap = [high[t], low[t-2]]
If no classic wick FVG → no birth at t (body gap alone does NOT birth).

# ZONE expand (011) — only after classic birth, same polarity:
Body gap bullish: Body[t].low > Body[t-2].high → body_gap = [Body[t-2].high, Body[t].low]
Body gap bearish: Body[t].high < Body[t-2].low → body_gap = [Body[t].high, Body[t-2].low]
Zone = [min(lowers of wick_gap ∪ body_gap), max(uppers of wick_gap ∪ body_gap)]
  If no body gap: zone = wick_gap.
Use only bars ≤ t. Birth time = close of bar t.
```

**PARAMETER** label on expand mechanics (011 states “include volume imbalance”; this freezes implementation).  
**Ban:** post-code demo redesign without **NEW hyp id**. ATLAS may calibrate stills against this freeze only.

### 3.2 Treatment — first FVG in 10:00 hour (010)

| Field | Lock |
|-------|------|
| Window | \(U=[10:00, 11:00)\) ET |
| Eligible | FVG births with birth ∈ \(U\) (10:00 bar may be \(t\)) |
| Treatment | Earliest birth in \(U\) |
| Birth-minute tie (Lock 5) | Lowest bar index; if still tied → **bullish before bearish** |
| No FVG in \(U\) | Day excluded (coverage: `no_first10_fvg`) |

### 3.3 Leave / revisit / primary metric \(m\) (Locks 4–5)

| Term | Lock |
|------|------|
| Overlap | Bar overlaps zone iff `low ≤ zone_high` and `high ≥ zone_low` |
| **Leave** | First bar **after birth** with **no** overlap with zone |
| **Revisit** | Later bar (after leave) that **overlaps** zone |
| **Primary \(m\)** | \(I(\)revisit within **60m** after leave\()\). **If never leaves** within path window → \(m=1\) |
| Path window for \(m\) | From birth through +60m after leave, capped at rest-of-available session on tape (document end) |
| MFE / MAE | **DESCRIPTIVE only** at +15 / +30 / +60 / rest-of-RTH — **cannot flip SURVIVES** |
| Never-leave report (R2) | Mandatory treat vs control never-leave rates; if treat ≫ control → **WIDTH-DEPENDENT** descriptive |
| MFE/MAE anchor | **Birth bar close** (PARAMETER) |

---

## 4. Controls (Lock 2)

### 4.1 PRIMARY control — later same-day same-polarity

```
Universe: FVG births same calendar day in [11:00, 15:00) ET,
          same polarity as treatment, excluding treatment.
Draw: one FVG uniformly; seed = H004b_later_{YYYY-MM-DD}
Empty universe → day drops (coverage: "first10_but_no_later_same_polarity")
Δ = m_treat − m_later on paired days only (bootstrap on pairs).
```

### 4.2 SENSITIVITY — random RTH (cannot sole-SURVIVES)

One FVG drawn uniformly from births in **[09:30, 15:30)** ET, same polarity, excluding treatment; seed `H004b_rth_{date}`.  
If this Δ flips sign/CI conclusion vs primary → label **CONTROL-DEPENDENT** — **do not** claim SURVIVES on primary alone.

### 4.3 SECONDARY — descriptive only

Second FVG in \([10:00,11:00)\) if exists — within-hour order; **not** a SURVIVES object.

If control draw would equal a labeled secondary/rival object, exclude that draw and re-sample once; if still collide, drop pair (R2 hygiene).

---

## 5. Falsification (Lock 7)

**FAILS** if OOS \(N_{\text{pairs}}≥80\): \(\Delta≤0\) or CI(\(\Delta\)) includes ≤0 on primary \(m\) (later control).

**SURVIVES** only if **all** hold on OOS:

1. \(N_{\text{pairs}}≥80\)  
2. \(\Delta>0\), CI(\(\Delta\)) entirely >0 (bootstrap 10_000 on pairs)  
3. Walk-forward median \(\Delta>0\) (step ≥20 pairs)  
4. Random-RTH sensitivity **does not flip** (else **CONTROL-DEPENDENT**, not SURVIVES)

**INCONCLUSIVE:** \(N_{\text{pairs}}<80\) / coverage / tape.

**Banned prose:** Silver Bullet proof; bare “H004b SURVIVES” without “first-10:00-hour FVG vs later control”; MERCURY/trade permission; MNQ Mar 2026 identity.

Polarity / event strata = descriptive; label **HOUR-DEPENDENT** / **EVENT-DEPENDENT** if only one stratum carries Δ.

IS/OOS = calendar **2023–2024 / 2025**.

---

## 6. Bias hunt

- [x] Tape = CONTINUOUS-KAGGLE-NQ1M; truncation FLAG; not stream C / not MNQ Mar 2026  
- [x] Primary control locked (later [11:00,15:00) same polarity + seed)  
- [x] Random RTH = sensitivity only  
- [x] Volume-imbalance: classic wick birth required; body gap expands zone only (CASSANDRA hygiene); PARAMETER; no post-code demo redesign  
- [x] Primary \(m\) = 60m revisit after leave; never-leaves → 1  
- [x] Leave / revisit / birth-close MFE anchor / birth-minute tie frozen  
- [x] Calendar IS/OOS; N≥80 pairs; coverage ≥20  
- [x] SURVIVES vocabulary = first-10:00-hour vs later — not Silver Bullet proof  
- [x] No MERCURY  
- [x] New id H004b; H004 retained as audit draft  

---

## 7. RUN blockers

1. CASSANDRA packaging re-review of **H004b** → must SURVIVE  
2. ORION exploratory auth after packaging clear  
3. Coverage projection (≥20 days) before N≥80 claim  
4. Event calendar 2023–2025 (H001b-style) cited  
5. **No run until packaging SURVIVES**

---

## 8. Paths

- This: `experiments/QUANT_H004b_FIRST_1000_FVG_PROTOCOL_2026-09-13.md`  
- Audit draft: `experiments/QUANT_H004_FIRST_1000_FVG_PROTOCOL_2026-09-13.md`  
- Red team: `reviews/CASSANDRA_H004_REDTEAM_2026-09-13.md`  
- Parents: `claims/C-METH-010.md`, `claims/C-METH-011.md`  
