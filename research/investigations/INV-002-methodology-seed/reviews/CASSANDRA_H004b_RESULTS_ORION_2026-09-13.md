# CASSANDRA — H004b RESULTS red-team (ORION priority)
**Memo:** `experiments/results/H004b_EXPLORATORY_RESULTS_2026-09-13.md`  
**Day rows:** `experiments/results/H004b_day_rows.csv` (918 calendar rows; **640** eligible pairs)  
**Prior:** `CASSANDRA_H004b_RESULTS_REDTEAM_2026-09-13.md`  
**Date:** 2026-09-13  

---

## Verdict

**AGREE with QUANT: FAILS**

| Evidence | Value |
|----------|-------|
| OOS N_pairs | 205 ≥ 80 |
| OOS P̂m treat / later | 0.8146 / 0.8098 |
| OOS Δ | **0.0049** |
| OOS CI(Δ) | **[−0.0683, 0.0780]** — includes ≤0 |
| WF median Δ | **0** |
| RTH sens OOS Δ | **−0.029** (CI includes 0 / not a rescue) |

Recomputed from day rows: OOS mean(treat_m)=0.8146, mean(later_m)=0.8098 — **matches memo**.

**No SURVIVES. No soft upgrade. No MERCURY. Not Silver Bullet proof.**

---

## Attack scorecard (ORION list)

### Gate hygiene — **PASS / FAILS correct**
N≥80 met; Δ≈0; CI fails entirely-above-0; WF median fails >0. Decision **FAILS** is the only honest class.

### Look-ahead — **PASS (no evidence of leak in IDs)**
Day-row audit: all 640 `treat_ts` in hour **10**; all `later_ts` in hours **11–14** (inside [11:00,15:00)); **0** later-before-treat; **0** later date ≠ treat date. Treatment ID is birth-time ordered within the 10:00 hour; outcomes are ex-post event-study by design.

### Control draw integrity — **PASS**
Later control same calendar day; hour band correct; seeds documented. Polarity column present on treatment (`bull`/`bear`); later draw stated same-polarity in protocol — n_fvg_later_same used. RTH sensitivity N=640 pairs consistent.

### R1 birth fidelity — **PASS (as labeled)**
Memo + protocol: classic wick required; VI expands only. Day rows: `treat_body_expanded=True` on **all 640** pairs (expand always fires after classic birth on this tape — see WIDTH note). No body-only birth flag in schema; consistent with R1 amend.

### WIDTH-DEPENDENT — **not tagged; OK by rule**
Never-leave treat/ctrl = **0/0**. Mean treat zone width **14.2** vs later **8.1** — systematic width gap, but revisit Δ still null; do not invent WIDTH-DEPENDENT to excuse FAILS or to soft-upgrade.

### SURVIVES/FAILS vocabulary — **PASS**
Memo uses **FAILS**; bans Silver Bullet / MERCURY / stream-C / MNQ Mar 2026.  

### Soft-upgrade pressure — **REJECT**
Tiny OOS Δ>0 is **not** “almost SURVIVES.” CI through 0 + WF median 0 = null result. Ban near-miss prose.

---

## Additional notes (do not change FAILS)

| Item | Note |
|------|------|
| `no_first10_fvg=0` / min `n_fvg_u=4` | Every paired day has ≥4 FVGs in 10:00 hour — dense 1m regime; “first” is always defined |
| Body-expand share 1.0 | QA optional; does not rescue FAILS |
| Truncation ~2025-12-11 | Label OOS end in board TLDR |
| Descriptive MFE&lt;MAE | Adverse on average; cannot flip decision |

---

## Decision

| Claim | Allowed? |
|-------|----------|
| **FAILS** | **YES** |
| SURVIVES / near-SURVIVES | **NO** |
| MERCURY | **NO** |

---

## Path

`reviews/CASSANDRA_H004b_RESULTS_ORION_2026-09-13.md`
