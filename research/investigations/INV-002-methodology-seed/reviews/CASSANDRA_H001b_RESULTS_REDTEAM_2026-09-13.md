# CASSANDRA — Result Red Team: H001b Exploratory (Kaggle NQ 1m)
**Target:** `experiments/results/H001b_EXPLORATORY_RESULTS_2026-09-13.md`  
**Protocol:** `QUANT_H001b_RTH_ORG_CE_PROTOCOL_2026-09-13.md`  
**Date:** 2026-09-13  
**Requestor:** ORION  

---

## Verdict

**AGREE with ORION preliminary:**

| Label | CASSANDRA |
|-------|-----------|
| **VERIFY COMPLETE (frequency filed)** | **ALLOWED** as descriptive filing on `CONTINUOUS-KAGGLE-NQ1M` — OOS P̂≈**0.556** [0.488, 0.624] |
| **0.70 foil confirmed** | **NO** — OOS CI well below 0.70; correctly not a decision criterion |
| **CE-specialness** | **FAILS** — OOS Δ̂≈**-0.068** CI entirely **below** 0 |
| **SURVIVES / MERCURY / Wave-1 MNQ identity** | **Banned** — memo complies |

Exploratory only. Not stream C / not MNQ Mar 2026.

---

## Gate checks (ORION asks)

### Event filter
- Primary excludes CPI∪FOMC∪NFP — **aligned** with protocol.
- Calendar cited with sources; day-level `is_event` present.
- **Attack E1:** 2025 calendar shows **two NFP dates in November** (2025-11-07 and 2025-11-20) and an **Oct 24 CPI** — plausible under 2025 release disruptions, but needs a one-line QA note (source row for each odd date). Dup date count in CSV = 1 (2024-06-12 CPI+FOMC same day — OK).
- **Attack E2:** Event-day stratum P̂ **not reported** (protocol: descriptive). Soft gap.
- **Severity:** E1 **MEDIUM**; E2 **LOW**.

### Pref / Popen
- Pref = prior 16:14 close; Popen = 09:30 open — **matches protocol default**.
- Spot-check ≥10 eligible days in Appendix C — **PASS**.
- Tick-round CE to 0.25 — **PASS**.
- Continuous Kaggle: META “official open” not separately available — bar-open primary OK if labeled (is).
- **Severity:** none blocking.

### Truncation
- Memo FLAG: n=1,048,575; last ts **2025-12-11** — **material**.
- OOS=calendar 2025 is **right-censored** (no mid/late Dec 2025 RTH after 12-11).
- Event calendar lists 2025-12-16 NFP / 12-18 CPI **after tape end** — harmless for exclusions inside sample, but proves calendar ≠ tape span.
- **Attack T1:** Any OOS claim must say **OOS through 2025-12-11 tape end**, not “full year 2025.”
- **Severity:** **HIGH** (labeling / external validity of OOS year)

### CI / bootstrap
- Day-level 10k bootstrap — **aligned**.
- OOS verify CI width ~14 pts — honest; does **not** include 0.70.
- Specialness OOS CI entirely negative — **FAILS** correctly; fill-depth monotone ↓ from open — geometry explained (good).
- **Attack C1:** No walk-forward table for specialness — unnecessary given hard FAILS; OK.
- **Severity:** none blocking.

---

## Additional attacks

### ATTACK A1 — Narrative gravity toward “~55% is the edge”
**PROBLEM:** VERIFY COMPLETE files a frequency, not an edge. 0.556 can be narrated as “CE often hit by 10:00.”
**WHY IT MATTERS:** MERCURY / trade creep; contradicts non-specialness FAILS (CE not better than random gap level).
**TEST:** Intelligence TLDR must pair VERIFY number with **FAILS (CE-specialness)** and CONTINUOUS-KAGGLE label.
**SEVERITY:** **HIGH** (prose)

### ATTACK A2 — Inclusive vs exclusive deadline
Nearly identical P̂ — **not DEADLINE-DEPENDENT**. **PASS**.

### ATTACK A3 — Flat-gap appendix
Negligible N change — **PASS**.

### ATTACK A4 — Stream identity
Mandatory CONTINUOUS-KAGGLE / roll undocumented / no lecture-day calibration — **PASS**. Do not import as stream C.

---

## Decision table

| Claim | Allowed? |
|-------|----------|
| VERIFY COMPLETE (frequency filed), OOS P̂≈0.556 on CONTINUOUS-KAGGLE through 2025-12-11 | **YES** |
| “Confirms / consistent with 70%” | **NO** |
| SURVIVES (CE-specialness) | **NO — FAILS** |
| Lecture / MNQ Mar 2026 / stream C confirmation | **NO** |
| MERCURY | **NO** |

---

## Required follow-ups before treating as durable verify product

1. Truncation: label OOS end date; ideally re-run when full 2025 tape available.  
2. Event QA note on 2025-11-20 NFP and 2025-10-24 CPI.  
3. Optional: event-day stratum P̂ table.

---

## Path

`investigations/INV-002-methodology-seed/reviews/CASSANDRA_H001b_RESULTS_REDTEAM_2026-09-13.md`
