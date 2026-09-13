# QUANT H004 — Experiment Protocol (DRAFT ONLY · NO RUN)
**Hypothesis ID:** H004  
**Investigation:** INV-002 · Wave 1  
**Parents (Passed Observed only):** C-METH-010, C-METH-011  
**ORION rank:** #3 in draft order  
**Author:** QUANT · **Filed:** 2026-09-13  
**Run status:** **HOLD** — shared tape  
**Note:** CASSANDRA to set final control (later same-day FVG vs random RTH FVG) before RUN.

---

## 0. Lock

Pre-reg. No lunch import. 1m chart. Silver Bullet branding ≠ mechanism — test **first FVG in 10:00 hour** as stated (010).

---

## 1. Statement

On **1m**, take the **first FVG that forms in the 10:00 ET hour** (10:00 candle may qualify; or first immediately after) (**010**). Include **volume imbalance** where bodies do not meet (**011**). Event-study: returns / MFE / MAE / revisit vs **later same-day FVGs** (selection-bias control). Falsify if first-10:00 FVG metrics are not better than later same-day FVGs (or random RTH FVG — CASSANDRA).

---

## 2. Population / instrument

MNQ prefer · 1m · America/New_York · shared tape · RTH days with full 10:00–16:00 (or through study horizon).

---

## 3. Definitions

### 3.1 FVG (1m) + volume imbalance

Standard 3-candle FVG:

- Bullish: `low[t] > high[t-2]` → zone `[high[t-2], low[t]]`  
- Bearish: `high[t] < low[t-2]` → zone `[high[t], low[t-2]]`  

**Volume imbalance extension (011):** if adjacent bodies do not meet (body gap) while wicks may overlap, **expand** the inefficiency zone to include the body gap. Exact body rule:

- Body of bar i = `[min(open,close), max(open,close)]`  
- If bars \(t-2\) and \(t\) form classic FVG **or** bodies of \(t-1\) and neighbors leave an unfilled body gap contiguous with the FVG, merge into one zone (DATA/ATLAS may refine on demo stills without changing birth-time rule).

Birth time = close of bar \(t\).

### 3.2 First FVG in 10:00 hour

Window \(U = [10:00, 11:00)\) ET.

Eligible: FVG with birth ∈ \(U\) (10:00 bar may be bar \(t\)).  
**Treatment** = eligible FVG with **earliest birth** in \(U\).  
If none: day excluded (coverage).

### 3.3 Event-study outcomes (from birth)

Horizons: +15m, +30m, +60m, rest-of-RTH.

| Metric | Definition |
|--------|------------|
| Directional MFE | Favorable excursion in FVG direction (bullish FVG → upside from birth mid or CE of zone) |
| MAE | Adverse excursion |
| Revisit | Time to first return into zone after leaving (if leaves) |
| Touch rate of zone mid | Optional |

**Primary comparison metric (pre-reg):** rest-of-RTH **MFE − |MAE|** (signed edge proxy) or, simpler for falsification: **P(price revisits zone within 60m)** — CASSANDRA may pick one before RUN; default primary = **60m revisit rate** (level utility) + report MFE/MAE.

---

## 4. Controls

| Control | Definition | Role |
|---------|------------|------|
| **Primary (ORION)** | Later same-day RTH FVGs: randomly sample one FVG with birth ∈ [11:00, 15:00) same day | Selection-bias: is “first in 10:00 hour” special vs later |
| **Alternate (CASSANDRA)** | Random RTH FVG any time 09:30–15:30 ex treatment | Broader null |
| **Secondary** | Second FVG in 10:00 hour (if exists) | Within-hour order |

When citing rival/later control, exclude treatment from draw. If control coincides with a labeled rival, drop pair (H1b R2 hygiene).

---

## 5. Falsification

**FAILS** if OOS N≥80: \(\Delta = m_{\text{first10}} - m_{\text{later}}\) ≤0 or CI includes ≤0 on primary metric.  
**SURVIVES** if Δ>0, CI>0, walk-forward median Δ>0.  
Label **HOUR-DEPENDENT** if only works on event days or only one polarity.

Event calendar stratification as H001.

---

## 6. Blockers

Shared tape; CASSANDRA control finalization; coverage projection; no MERCURY/RISK.

## 7. Path

`experiments/QUANT_H004_FIRST_1000_FVG_PROTOCOL_2026-09-13.md`
