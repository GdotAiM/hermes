# QUANT H003 — Experiment Protocol (DRAFT · PACKAGING RED-TEAM)
**Hypothesis ID:** H003  
**Investigation:** INV-002 · Wave 1  
**Parents (Passed Observed only):** C-METH-003, C-METH-004, C-METH-006  
**ORION:** Unparked for CASSANDRA packaging review after H001b SURVIVED (2026-09-13)  
**Author:** QUANT · **Filed:** 2026-09-13 · **Updated:** 2026-09-13 (unpark)  
**Run status:** **SUPERSEDED by H003b** — do not run. See `QUANT_H003b_79_SWEEP_OPPOSITE_PROTOCOL_2026-09-13.md`

---

## 0. Lock

Pre-reg before peek. No INV-001 lunch import. RTH open **9:30 ET** (Passed open clock).  
H001 superseded by H001b — do not run H001. **No MERCURY/RISK.**

CASSANDRA: attack **control choice** and sweep definition before any RUN clearance.

---

## 1. Statement

Given the **07:00–09:00 ET** range (Passed **003/004**), if after **09:30** one boundary is **swept first**, then \(P(\text{reach opposite boundary})\) exceeds a pre-registered baseline. Report time-to-target, MAE, MFE.

Passed **006:** one-side sweep of 7–9 → aim opposite end = “bread-and-butter.”

---

## 2. Population / instrument

| Field | Lock |
|-------|------|
| Instrument | **MNQ** prefer (shared stream C) / NQ documented · 1m · America/New_York |
| Days | Trading days ex Sundays (003); need ETH 07:00–09:00 + RTH through primary horizon |
| Event primary | Non-CPI/FOMC/NFP — cite INV-001 `EVENT_CALENDAR_CPI_FOMC_NFP.md` |
| Tape | Shared stream C / WAVE1 — one stack |
| Min N | **80** paired (or treated) days for decision; else INCONCLUSIVE |
| Coverage | Project on ≥20 RTH days before claiming N≥80 |

---

## 3. Definitions

### 3.1 7–9 range

Window \(W=[07:00, 09:00)\) ET:

- \(H_{79}\) = max high in \(W\)  
- \(L_{79}\) = min low in \(W\)  
- Exclude if \(H_{79}-L_{79} < 2\) MNQ pts (PARAMETER degenerate floor)

**Tick levels:** \(H_{79}\), \(L_{79}\) from 1m highs/lows (already on tick grid).

### 3.2 First sweep after 09:30

Primary horizon end **12:00 ET**; co-report 10:00 / 11:00.

- **Sweep high first:** first time `high ≥ H_{79}` before any `low ≤ L_{79}`  
- **Sweep low first:** first time `low ≤ L_{79}` before any `high ≥ H_{79}`  
- **Neither by horizon:** no treatment unit (coverage)

\(	au_s\) = sweep time. Buffer beyond extreme: **0 pts** primary; sensitivity +2 pts (post-OOS descriptive).

### 3.3 Opposite target + success

- Swept high first → target \(L_{79}\)  
- Swept low first → target \(H_{79}\)  

**Success:** after \(	au_s\), any bar overlaps target before horizon (`low ≤ target ≤ high`).

### 3.4 Path metrics

Time-to-target (minutes); MAE (adverse from sweep extreme before target/horizon); MFE (favorable toward target).

---

## 4. Controls (locked for packaging attack)

Ambiguous “or” removed — **one primary**:

| Role | Definition |
|------|------------|
| **PRIMARY control** | On the **same** first-sweep days: assign a **random side** (seeded) as if it were the first sweep; measure \(P(\text{hit opposite of random side})\) by same horizon. Paired Δ vs actual first-sweep success. |
| **Secondary A** | Days with valid 7–9 range but **no** one-side sweep by 12:00 — descriptive only (different estimand) |
| **Secondary B** | First sweep of **09:30–10:00** high/low (30m OR, C-METH-015) — different object; descriptive; do not conflate with 7–9 box |

**Primary Δ:** \(P(\text{opp}|\text{actual first sweep}) - P(\text{opp}|\text{random side})\) on same days.  
Bootstrap 10_000 on days.  

If CASSANDRA rejects this control, ORION-acked amend or **NEW hyp id** (no peek).

---

## 5. Falsification

**FAILS** if OOS N≥80: Δ≤0 or bootstrap 95% CI includes ≤0.  
**SURVIVES** if Δ>0, CI entirely above 0, walk-forward median Δ>0 — label **SURVIVES (7–9 opposite after first sweep)**.  
**INCONCLUSIVE** if N<80 / tape / coverage fail.

IS 60% / OOS 40% time-ordered; walk-forward step 20 days.

Ban: treating SURVIVES as MERCURY permission.

---

## 6. Bias hunt

- [ ] Look-ahead / completed bars only  
- [ ] Sweep side unique (ties: if same bar sweeps both — exclude or rule: **exclude** dual-sweep bars as treatment)  
- [ ] Primary = random-side paired control (not no-sweep)  
- [ ] No 30m OR conflation in prose  
- [ ] Event calendar  
- [ ] No lunch import  

---

## 7. Blockers

1. CASSANDRA packaging red-team (queued)  
2. Shared stream C + coverage projection  
3. No MERCURY/RISK  

## 8. Path

`experiments/QUANT_H003_79_SWEEP_OPPOSITE_PROTOCOL_2026-09-13.md`
