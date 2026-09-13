# QUANT H1 — Experiment Protocol (DRAFT ONLY · NO RUN)
**Hypothesis ID:** H1 / C-2026-015  
**Investigation:** INV-001  
**Lecture:** C90xGr3kW8Y · ICT 2026 New York Lunch Algorithmic Theory · 2026-03-11  
**Parents (Passed Observed):** C-2026-009 (+ supporting 001–004)  
**ORION rank:** #1 (highest information gain — NEW-as-package)  
**Author:** QUANT  
**Filed:** 2026-09-13  
**Run status:** **HOLD** — designs only until DATA files tape stream C (MNQ Mar 2026, 1m, America/New_York, ≥2026-03-10..11)

---

## 0. Pre-registration lock

This document freezes the testable claim **before** any OHLC is inspected for results.  
Any change to population, raid/FVG defs, touch metric, control, or falsification after peeking the tape = **NEW HYPOTHESIS** (do not amend this file in place).


---

## 0b. ORION acceptance amendment (2026-09-13) — labeling only

ORION accepted this H1 draft with **one labeling rule** (not a mechanics change):

- Lunch start **11:30 ET** must be tagged **PARAMETER** (arithmetic from Passed 001+002: 2h ending 13:30), **not Observed speech**.
- Keep sensitivity window **[12:00, 13:30)**.
- Do **not** amend other locks after this note without a **NEW hyp ID**.

---

## 1. Statement (locked)

A **first FVG** printed **immediately before** a **lunch-window turtle-soup raid**, when carried into the **next RTH session**, is **touched at or near that next session’s high or low** more often than a **randomly chosen prior-day FVG** (same day, same bar size).

---

## 2. Population / instrument / period / session

| Field | Lock |
|-------|------|
| Population | CME equity-index micro futures sessions with a complete RTH day after a prior RTH day |
| Instrument | **MNQ Mar 2026** (contract as on lecture chart). Continuous only if DATA documents roll method; default = front-month Mar 2026 for pilot dates |
| Bar size | **1-minute** OHLC |
| Timezone | **America/New_York**; store UTC + ET wall-clock; DST-aware (EDT on 2026-03-11) |
| Period (pilot seed) | ≥ **2026-03-10 .. 2026-03-11** (lecture-aligned), then expand only after DATA amends stream C |
| Sample expansion (pre-registered intent) | After pilot plumbing works: walk-forward on subsequent MNQ months / years with **same** mechanical defs — do not retune on pilot |
| Session — lunch window | **Observed end:** 13:30 ET (Passed **002**). **Observed length:** 2 hours (Passed **001**). **Start 11:30 ET = PARAMETER** (arithmetic 13:30−2h from Passed 001+002) — **not Observed speech**, not taxonomy import. Primary window: **PARAMETER [11:30, 13:30) ET**. Sensitivity (kept): **[12:00, 13:30)** robustness only — secondary, not primary. |
| Session — “next session” | Next **RTH** day **[09:30, 16:00] ET**. Holidays / early closes: exclude day if RTH < 390 minutes |
| ETH | Not used for HOD/LOD metric (RTH only) |

---

## 3. Mechanical definitions (no discretion)

### 3.1 Fair Value Gap (FVG) — 1m

On bars \(t-2, t-1, t\) (completed bars only):

- **Bullish FVG:** `low[t] > high[t-2]` → gap zone `[high[t-2], low[t]]`
- **Bearish FVG:** `high[t] < low[t-2]` → gap zone `[high[t], low[t-2]]`

FVG **birth time** = timestamp of bar \(t\) close.  
FVG **active** until midpoint of zone is traded through (optional invalidate flag recorded; primary touch metric uses zone high/low bounds, not midpoint).

### 3.2 Turtle-soup / liquidity raid (lunch window)

Inside lunch window \([11:30, 13:30)\) ET on day \(D\) — start **11:30 = PARAMETER**, end **13:30 = Observed**:

A **buy-side turtle-soup raid** occurs if **all** hold:
1. Price makes a **new high of the lunch window so far** (running HOD of lunch).
2. That high **exceeds** the prior **swing high** defined as: highest high of any completed 1m bar in \([11:30, \tau)\) that is followed by at least **3** lower highs before the raid bar (simple fractal: high[i] > high[i-1] and high[i] > high[i+1], with i+1 completed before raid).
3. Within **N_raid = 15** minutes after that break, price **closes back below** the broken swing high (failure / soup).

A **sell-side turtle-soup raid** = mirror (new lunch LOD through prior swing low, reclaim above within 15m).

**Raid time** \(\tau_{raid}\) = timestamp of the reclaim close.  
**Raid side** = buy-side or sell-side as above.

If multiple raids in the window: take the **last** raid whose \(\tau_{raid} < 13:30\) (matches “ahead of the 1:30 close” teaching). If none: day \(D\) contributes **no treatment unit**.

### 3.3 “First FVG printed immediately before” the raid

Search backward from \(\tau_{raid}\) within lunch window only:

- Eligible FVGs: birth time \(\in [11:30, \tau_{raid})\) and FVG **direction matches raid**  
  - buy-side raid → **bullish** FVG (inefficiency into the run)  
  - sell-side raid → **bearish** FVG  
- **First FVG before raid** = eligible FVG with **latest birth time ≤ \(\tau_{raid}\)** (closest in time before liquidity is taken).  
  Clarification: lecture “first fair value gap right before liquidity is taken” = nearest pre-raid FVG of matching polarity, not the chronologically first FVG of the lunch window.

If none: day \(D\) has a raid but **no treatment FVG** → exclude from treatment (count in denominator of “raid days without pre-raid FVG” as a coverage diagnostic only).

### 3.4 Treatment level carried to next day

Let \(L\) = the FVG zone from §3.3 on day \(D\).  
Day \(D+1\) RTH is the evaluation session.

---

## 4. Outcome metric (primary)

On day \(D+1\) RTH:

- \(H_{D+1}\) = RTH high; \(L_{D+1}\) = RTH low  
- **Touch** of zone \(L\): any 1m bar with `low ≤ zone_high` and `high ≥ zone_low` (overlap with FVG zone)

**Near HOD/LOD** (primary success):

Define proximity buffer **B = 4 MNQ points** (pre-registered; ≈ 4.0 index points on MNQ).

Success if **either**:
1. Zone overlaps \([H_{D+1} - B,\ H_{D+1}]\), **or**
2. Zone overlaps \([L_{D+1},\ L_{D+1} + B]\)

**Secondary (report only, not primary falsification):**
- Exact touch of HOD or LOD print within zone (B=0)
- MAE/MFE of first touch of zone relative to HOD/LOD distance
- Time-of-day of first zone touch on \(D+1\)

---

## 5. Control (pre-registered)

**Null comparator:** randomly chosen prior-day FVG.

For each treatment day \(D\) with a valid treatment FVG:

1. Collect all FVGs on day \(D\) with birth in **RTH [09:30, 16:00)** (or lunch-only sensitivity — primary = **full RTH**).
2. Exclude the treatment FVG itself.
3. Draw **one** FVG uniformly at random (seed recorded) → control zone \(L_{ctrl}\).
4. Apply **identical** §4 success rule on \(D+1\).

**Paired design:** each treatment day contributes one (treatment, control) pair.

**Additional negative control (secondary):** random **time-matched** FVG — pick a random birth minute in \([11:30, \tau_{raid})\) and take nearest FVG of **either** polarity (report separately).

---

## 6. Entry / exit / stop / target / risk

H1 is a **level-revisit frequency test**, not a trade system.

| Field | Lock |
|-------|------|
| Entry | None (no fills in primary test) |
| Exit | None |
| Stop / target | N/A for primary |
| Risk | N/A for primary; if MERCURY later wraps a trade rule, RISK caps apply (≤0.5%/trade) — that wrap is a **NEW** hypothesis |

Optional **exploratory** trade wrapper (NOT part of H1 falsification; label EXPLORATORY if ever coded): short/long from first \(D+1\) touch of \(L\) toward the nearer extreme — deferred; do not run with H1.

---

## 7. Sample / splits / stratification

| Item | Lock |
|------|------|
| Minimum N (pairs) for decision | **N ≥ 80** paired days with both treatment + control; else **INCONCLUSIVE** |
| Pilot plumbing | 2026-03-10..11 only validates code paths — **not** for SURVIVES/FAILS |
| IN-SAMPLE | First 60% of eligible calendar days after tape expansion (time-ordered) |
| OUT-OF-SAMPLE | Remaining 40% (time-ordered) — **single look**; no retune |
| WALK-FORWARD | After OOS: expanding window, step 20 days; report stability of touch-rate delta |
| PAPER / LIVE | Not applicable until RISK/MERCURY wrap (separate hyp) |

**Stratify / exclude (pre-registered):**
- **CPI / major US CPI release days** (C-012 track): primary test = **non-CPI days**; also report CPI-day stratum separately (do not pool for primary)
- FOMC decision days: exclude from primary (event contamination)
- Half-days / holidays: exclude

---

## 8. Metrics (report set)

- N treatment days, N pairs  
- Touch rate treatment vs control (primary success §4)  
- Paired difference \(\Delta = p_{treat} - p_{ctrl}\)  
- Exact McNemar or paired bootstrap 95% CI on \(\Delta\) (pre-register: **bootstrap, 10_000 resamples**)  
- Win-rate analogue = success rate; no avg win/loss for primary  
- Coverage: % lunch days with raid; % raids with pre-raid FVG  
- Dependence: DOW, month, trend day vs range day (ATLAS labels if filed), buy-side vs sell-side raid  

**Costs/slippage:** N/A for touch-frequency primary.

---

## 9. Falsification criteria (pre-committed)

**FAILS** if, on OUT-OF-SAMPLE with N≥80:

1. \(\Delta \le 0\), **or**
2. Bootstrap 95% CI for \(\Delta\) includes \(\le 0\) (not distinguishable from control)

**SURVIVES** only if OOS \(\Delta > 0\) and 95% CI entirely above 0, **and** walk-forward median \(\Delta > 0\).

**INCONCLUSIVE** if N<80 after available tape, or DATA quality gate fails mid-run.

**Multiple testing:** H1 primary endpoint is **one** \(\Delta\). Secondary metrics are descriptive. H2/H3 are separate hypotheses (do not pool p-values without correction if jointly claimed later).

---

## 10. Bias hunt checklist

- [ ] Look-ahead: FVG/raid use only completed bars; \(D+1\) HOD/LOD known only after session (metric is ex-post by design — OK for level study; not a trade fill claim)
- [ ] Data leakage: no future bars in raid/FVG construction
- [ ] Selection: last raid before 13:30 only; days without raid excluded from treatment (report coverage)
- [ ] Survivorship: fixed MNQ contract month per DATA; document rolls if continuous
- [ ] Overfitting: B=4 pts and N_raid=15m frozen; robustness B∈{2,4,8} and N_raid∈{10,15,20} reported as sensitivity **after** primary OOS (label sensitivity, not primary)
- [ ] Unrealistic fills: N/A primary
- [ ] Regime: CPI/FOMC stratified/excluded
- [ ] No post-hoc hyp revision without NEW id

---

## 11. DATA blockers (do not run until)

1. Tape stream **C** filed: MNQ Mar 2026, 1m, America/New_York, ≥2026-03-10..11, with SOURCE / continuity / gap policy  
2. DATA integrity: monotonic timestamps, no duplicates, holiday calendar  
3. Optional: CPI calendar file for stratification  

---

## 12. Downstream handoff

- **CASSANDRA:** attack packaging (selection of “first FVG before raid,” HOD/LOD buffer B, CPI contamination, lunch start arithmetic)  
- **RISK / MERCURY:** no paper size until a separate trade-wrapper hyp survives  
- **ORION:** H1 protocol filed — awaiting DATA stream C before any run

---

## 13. File path

`investigations/INV-001-2026-lectures/experiments/QUANT_H1_C015_PROTOCOL_2026-09-13.md`
