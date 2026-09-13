# QUANT H003 — Experiment Protocol (DRAFT ONLY · NO RUN)
**Hypothesis ID:** H003  
**Investigation:** INV-002 · Wave 1  
**Parents (Passed Observed only):** C-METH-003, C-METH-004, C-METH-006  
**ORION rank:** #2 in draft order (after H001)  
**Author:** QUANT · **Filed:** 2026-09-13  
**Run status:** **HOLD** — shared tape

---

## 0. Lock

Pre-reg before peek. No INV-001 lunch import. RTH open **9:30 ET**.  
CASSANDRA to attack **control choice** before RUN (ORION note).

---

## 1. Statement

Given the **07:00–09:00 ET** range (Passed **003/004**), if after **09:30** one boundary is **swept first**, then \(P(\text{reach opposite boundary})\) exceeds a pre-registered baseline. Report time-to-target, MAE, MFE.

Passed **006:** one-side sweep of 7–9 → aim opposite end = “bread-and-butter.”

---

## 2. Population / instrument

| Field | Lock |
|-------|------|
| Instrument | MNQ (prefer) / NQ documented · 1m · America/New_York |
| Days | Trading days ex Sundays (003); need ETH 07:00–09:00 + RTH |
| Tape | Shared stream C / WAVE1 |

---

## 3. Definitions

### 3.1 7–9 range

On day \(D\), window \(W=[07:00, 09:00)\) ET:

- \(H_{79}\) = max high in \(W\)  
- \(L_{79}\) = min low in \(W\)  
- Exclude if \(H_{79}-L_{79} < 2\) MNQ pts (degenerate)

### 3.2 First sweep after 09:30

In RTH after 09:30 (primary horizon end **12:00 ET**; also report 10:00 / 11:00):

- **Sweep high first:** first time `high ≥ H_{79}` before any `low ≤ L_{79}`  
- **Sweep low first:** first time `low ≤ L_{79}` before any `high ≥ H_{79}`  
- **Neither by horizon:** no treatment unit (coverage)

Sweep time \(\tau_s\). Buffer beyond extreme: **0 pts** primary (touch); sensitivity +2 pts.

### 3.3 Opposite target

- If swept high first → target = \(L_{79}\)  
- If swept low first → target = \(H_{79}\)  

**Success:** after \(\tau_s\), price overlaps target before horizon end.

### 3.4 Path metrics

- Time-to-target (minutes)  
- MAE: adverse excursion from sweep extreme toward continuation before target (points)  
- MFE: favorable toward target before target hit or horizon  

---

## 4. Controls (pre-reg; CASSANDRA to stress)

| Control | Definition | Role |
|---------|------------|------|
| **Primary** | Days with a defined 7–9 range but **no** one-side sweep by 12:00 — \(P(\text{touch both extremes by 12:00})\) or random: pick a random “pseudo-sweep” side at 09:30 and measure opposite hit | Isolates sweep conditioning |
| **Secondary** | Random-side: on sweep days, ignore actual first side; assign random side — should ≈0.5 if no edge | Sanity |
| **Secondary** | First sweep of **09:30–10:00 OR high/low** (30m OR per 015) instead of 7–9 — different object; descriptive only |

**Primary falsification Δ:** \(P(\text{opp}|\text{first sweep 7–9}) - P_{\text{ctrl}}\)  
CASSANDRA may replace primary control before RUN without peek → amend note or NEW id if structural.

---

## 5. Falsification

**FAILS** if OOS N≥80: Δ≤0 or bootstrap 95% CI includes ≤0.  
**SURVIVES** if Δ>0, CI>0, walk-forward median Δ>0.  
**INCONCLUSIVE** if N<80 / tape fail.

Event stratification: non-event primary (INV-001 calendar).

---

## 6. Blockers

Shared tape; coverage projection; CASSANDRA on control; no MERCURY/RISK.

## 7. Path

`experiments/QUANT_H003_79_SWEEP_OPPOSITE_PROTOCOL_2026-09-13.md`
