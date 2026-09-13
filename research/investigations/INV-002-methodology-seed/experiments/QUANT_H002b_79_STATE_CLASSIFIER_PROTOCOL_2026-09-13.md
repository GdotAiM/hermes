# QUANT H002b — Experiment Protocol (PACKAGING · NO RUN)
**Hypothesis ID:** **H002b** (NEW id)  
**Supersedes for decision-readiness:** H002 `QUANT_H002_79_STATE_CLASSIFIER_PROTOCOL_2026-09-13.md` (**audit draft only — do not run H002**)  
**Investigation:** INV-002-methodology-seed · Wave 1  
**Parents (Passed Observed only):** C-METH-003, C-METH-004, C-METH-005  
**CASSANDRA:** `reviews/CASSANDRA_H002_REDTEAM_2026-09-13.md` → **DID NOT SURVIVE** → this rewrite  
**Author:** QUANT · **Filed:** 2026-09-13  
**Revision class:** Pre-reg packaging rewrite — **no results peeked**  
**Run status:** Packaging **SURVIVED** (`reviews/CASSANDRA_H002b_REDTEAM_2026-09-13.md`). All 10 locks PASS. **No RUN** until ORION auth + coverage ≥20. Confirm §3 hash at code freeze. Do not run H002.  
**No MERCURY**

---

## 0. Why H002b

H002 failed packaging on unlocked score/horizon/baseline, unfrozen IS/OOS, MNQ/stream-C identity, and cross-hyp threshold leakage risk after H001b/H003c/H004b peeks on the same tape. All ten ORION must-locks are frozen below.

---

## 0b. Cross-hyp leakage ban (Lock 7)

Do **not** retune §3 PARAMETER thresholds using outcomes already seen from H001b / H003c / H004b (or any other hyp) on CONTINUOUS-KAGGLE. Thresholds below are frozen **now**, before any H002b RUN. Sensitivity grid only **after** primary OOS is filed.

---



## 0c. CASSANDRA H002b packaging SURVIVED (2026-09-13)

`reviews/CASSANDRA_H002b_REDTEAM_2026-09-13.md` — all 10 locks PASS; no CRITICAL residuals.  
Still blocked: ORION exploratory auth + coverage projection ≥20. Confirm §3 freeze hash at code freeze. No MERCURY. Do not run H002.

---

## 1. Statement (locked)

On **CONTINUOUS-KAGGLE-NQ1M** 1m (America/New_York):

- Classify each trading day (**ex Sundays**, Passed **003**) in **07:00–09:00 ET** into a **PARAMETER** four-class state (§3).  
- Test whether that class predicts **post-09:30** first side swept of the 7–9 HH/LL by **T\*=12:00** better than an **IS-majority constant** baseline under **multiclass log-loss lift**.  
- This is a **PARAMETER classifier implementing 003–005 precursor** — **not** Observed trending/consolidating/reversing identity.  
- Prose on any SURVIVES **must** include **“not a panacea”** (Passed **005**).

---

## 2. Tape / population (Locks 1 + 8)

| Field | Lock |
|-------|------|
| Stream | **`CONTINUOUS-KAGGLE-NQ1M` only** |
| File | `evidence/tape/KAGGLE_NQ_1M_2022_2025/Dataset_NQ_1min_2022_2025.csv` |
| Labels (every memo) | roll **undocumented** · **Excel truncation FLAG** · **not MNQ Mar 2026** · **not stream C** · no 2026 lecture-day identity |
| Bar | 1m · naive ET; ETH required for 7–9 |
| Days | Ex **Sundays** (003); RTH days with path through T* |
| Events | Descriptive strata only (H001b-style CPI/FOMC/NFP) — primary pool may include or exclude with both reported; pre-reg primary = **non-event** days |
| IS / OOS | **Calendar 2023–2024 / 2025** |
| Min N | **≥80** OOS days with valid class + y; else INCONCLUSIVE |
| Coverage | Project ≥20 RTH days before N≥80 claim |

VWAP ignored.

---

## 3. Classifier — PARAMETER thresholds FROZEN (Locks 6–7)

Window \(W=[07:00,09:00)\) ET:

- \(H,L\) = HH/LL in \(W\); \(R=H-L\)  
- \(O\) = open of first bar in \(W\); \(C\) = close of last bar in \(W\)  
- \(ATR_{ref}\) = **median** of prior **20** days’ 7–9 ranges — days **strictly before D** only (Lock 7)

### §3 freeze table (hash before RUN)

| Parameter | Frozen value |
|-----------|--------------|
| ATR lookback | **20** sessions (ex Sundays) |
| Expansion multiplier | **1.0** × ATR_ref |
| Body fraction | **0.5** |
| Compression multiplier | **0.5** × ATR_ref |

| Class | Rule |
|-------|------|
| **expansion↑** | \(C>O\) and \(R \ge 1.0\times ATR_{ref}\) and \((C-O)/R \ge 0.5\) |
| **expansion↓** | \(C<O\) and \(R \ge 1.0\times ATR_{ref}\) and \((O-C)/R \ge 0.5\) |
| **compression** | \(R \le 0.5\times ATR_{ref}\) |
| **consolidation** | else |

**Sensitivity grid (post-primary-OOS only):** expand mult ∈ {0.8, 1.0, 1.2}; compression ∈ {0.4, 0.5, 0.6}. Cannot flip SURVIVES alone.

Lecture “reversing” ≠ fifth primary class (descriptive only).

**§3 freeze hash (sha256 of canonical table text):** `074d6a83ccf5289cf654b26c4cd747ea9b3bbe1c4671c1c65aa598b9f3eb3464`

---

## 4. Primary target y (Locks 2–3)

| Field | Lock |
|-------|------|
| Horizon **T\*** | **12:00 ET only** (primary) |
| 10:00 / 11:00 | Descriptive only — cannot flip SURVIVES |
| Box | 7–9 \(H,L\) from §3 |
| **y** | First side swept after 09:30 by T* ∈ {**high**, **low**, **neither**} |
| high | First touch of \(H\) before \(L\) (and before T*) |
| low | First touch of \(L\) before \(H\) |
| neither | Neither extreme touched by T* |
| Dual same-bar | Exclude day from primary (coverage) |

Secondary descriptive: range expansion \((HH-LL)_{[09:30,T*)}/R\); chop = expansion <1.0 **and** ≥3 direction changes of 5m closes with bar timestamps **< T\*** (PARAMETER chop; Lock 7).

---

## 5. Model, baseline, score (Locks 4–5)

| Field | Lock |
|-------|------|
| Model | Multinomial logistic (or equivalent) of **class → y**; fit on **IS only** |
| **PRIMARY baseline** | **IS-majority class** constant predictor for all OOS days (predicts the IS modal y for every OOS day) |
| Persistence | Previous-day class → y model = **sensitivity only** — **cannot sole-SURVIVES** |
| **PRIMARY score** | OOS multiclass **log-loss** \(L\) |
| **Lift** | \(L_{\text{base}} - L_{\text{model}}\) (higher better) |
| Balanced accuracy | **Descriptive only** |
| Bootstrap | 10_000 day-level resamples on OOS for CI(lift) |

---

## 6. Falsification (Lock 9)

**FAILS** if OOS \(N≥80\): lift ≤0 or CI(lift) includes ≤0.

**SURVIVES** only if all hold:

1. OOS \(N≥80\)  
2. lift >0 and CI(lift) entirely >0  
3. Walk-forward median lift >0  
4. Prose = **PARAMETER classifier implementing 003–005 precursor** + mandatory **“not a panacea” (005)**  
5. Persistence sensitivity does **not** become the sole claimed win  

**Banned:** Observed trending/consolidating/reversing identity confirmed; deterministic post-9:30 claims; Silver Bullet / MERCURY / trade permission; MNQ Mar 2026 / stream C identity.

**INCONCLUSIVE:** N<80 / coverage / tape.

---

## 7. Bias hunt

- [x] CONTINUOUS-KAGGLE-NQ1M; truncation FLAG; not stream C; not MNQ Mar 2026  
- [x] T*=12:00 primary; 10:00/11:00 descriptive  
- [x] y = first side swept ∈ {high, low, neither}  
- [x] Primary score = OOS log-loss lift vs IS-majority baseline; bal-acc descriptive  
- [x] Persistence = sensitivity only  
- [x] Thresholds frozen 20 / 1.0 / 0.5 / 0.5; grid post-OOS only  
- [x] ATR days < D; chop bars < T*; ban retune from other hyp peeks; §3 hash  
- [x] Calendar IS/OOS; N≥80; coverage≥20; event strata descriptive; ex Sundays  
- [x] SURVIVES vocab = PARAMETER precursor + “not a panacea”; no MERCURY  
- [x] New id H002b; H002 audit only  

---

## 8. RUN blockers

1. CASSANDRA packaging re-review of **H002b** → must SURVIVE  
2. ORION exploratory auth after packaging clear  
3. Coverage projection ≥20  
4. Confirm §3 freeze hash recorded pre-code  
5. **No run until packaging SURVIVES** · do not run H002  

---

## 9. Paths

- This: `experiments/QUANT_H002b_79_STATE_CLASSIFIER_PROTOCOL_2026-09-13.md`  
- Audit: `experiments/QUANT_H002_79_STATE_CLASSIFIER_PROTOCOL_2026-09-13.md`  
- Red team: `reviews/CASSANDRA_H002_REDTEAM_2026-09-13.md`  
- Parents: `claims/C-METH-003.md`, `004`, `005`  
