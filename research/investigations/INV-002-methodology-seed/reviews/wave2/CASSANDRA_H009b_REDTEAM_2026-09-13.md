# CASSANDRA — Red Team Re-Review: QUANT H009b
**Target:** `experiments/wave2/QUANT_H009b_NEAREST_PWPM_PROTOCOL_2026-09-13.md`  
**Prior:** `CASSANDRA_H009_REDTEAM_2026-09-13.md` (HOLD — wrong picker)  
**Date:** 2026-09-13  
**Parents:** C-METH-**022, 023, 025** — **DATA Passed** (ORION 2026-09-13 upgrade; cards verified Passed)  
**Tape:** FREE_YF_NQ · CONTINUOUS-YF  
**Verdict:** **HYPOTHESIS SURVIVED RED TEAM REVIEW** (packaging — nearest-side clears H009 CRITICAL)  
**Run clearance:** **NOT GRANTED** — residuals below + FREE_YF DATA gate / no peek

---

## Disposition of H009 attacks

| Prior | Issue | H009b status |
|-------|-------|--------------|
| CRITICAL | Bull/bear picker ≠ nearest-side | **CLEARED** — nearest-side primary; bull/bear rival only |
| HIGH | Hold vocabulary inflation | **PARTIAL** — prose bans good; **header/§0 still say Hold** though DATA **Passed** — stale |
| HIGH | Yahoo week / Sunday open / rolls | **CLEARED** (design) — Mon Open proxy + Fri close co-report + ROLL-DEPENDENT |
| MEDIUM | Unique-first selection | **CLEARED** — coverage + <50% flag |
| MEDIUM | Test A muddle | **CLEARED** — descriptive rival only |
| LOW | Event filter | **CLEARED** — EVENT-SENSITIVE co-report |

---

## Upgrade scoring (022/023/025 now Passed)

ORION: score H009b with nearest-side as **Passed Observed**, not PARAMETER-only.

| Element | Match to Passed cards? | Label for SURVIVES |
|---------|------------------------|--------------------|
| Nearest-side distance rule | **Yes** (022) | Observed structure |
| Candidates {PWH,PWL,PMH,PML} | 022 asks week **or** month high vs low — **four-way** | H009b primary is **two-way** only; four-way co-report → **week-subset** unless elevated |
| Sunday open \(P_0\) | 022 Sunday open; tape has Mon Open / Fri close | **PARAMETER proxy** — ban “Sunday-open identity” |
| Fri close notepad (023) | Co-report \(P_0\) | Good sensitivity |
| Daily transpose / drop opposite (025) | First-touch of predicted extreme on daily | Aligned |

---

## Residual attacks

### ATTACK R1 — Stale Hold headers after DATA Pass

**PROBLEM:** Lines 5, 18, 22, 100, 113 still treat 022/023 as Hold/ASR and force SURVIVES = “PARAMETER nearest-side…” only.

**WHY IT MATTERS:** Under-claims Observed 022; confuses ORION summaries.

**EVIDENCE REQUIRED:** Amend header/§0/§6/§7: parents **Passed**. Allow SURVIVES label: **Observed nearest-side (022) · PARAMETER Mon-open proxy · CONTINUOUS-YF** — still ban Sunday-open identity and Wave 1 claims.

**TEST:** In-place amend (no peek) before RUN.

**SEVERITY:** **HIGH** (labeling; easy fix)

---

### ATTACK R2 — Two-way primary vs four-way Observed (022)

**PROBLEM:** Passed 022 nearest-side includes previous-**month** high/low in the spoken alternative set. H009b primary \(L=\{PWH,PWL\}\); \(L_4\) co-report only.

**WHY IT MATTERS:** “Observed 022 SURVIVES” on two-way alone overclaims the card. Month levels can be nearer than week levels.

**EVIDENCE REQUIRED:** Either (A) elevate **four-way** to primary for lecture SURVIVES, two-way = sensitivity; or (B) keep two-way primary but SURVIVES prose = **week-only subset of 022** (not full card).

**TEST:** Lock A or B in §6 before RUN. Prefer **A** for Wave-2 #1 fidelity.

**SEVERITY:** **HIGH**

---

### ATTACK R3 — Mon Open ≠ Sunday open (remaining PARAMETER)

**PROBLEM:** Acknowledged. FREE_YF daily cannot see Sunday ETH open.

**WHY IT MATTERS:** Anchor error vs 022.

**EVIDENCE REQUIRED:** Already — ANCHOR-DEPENDENT Fri close co-report. Keep mandatory. Optional: first print Monday 00:00 ETH if ever on tape = NEW note.

**TEST:** SURVIVES must include **PARAMETER Mon-open proxy**.

**SEVERITY:** **MEDIUM** (unavoidable on this tape; must stay labeled)

---

## Credit

- Implements ORION/CASSANDRA nearest-side fix; §4 clean; foil correct (0.5 / 0.25).  
- Roll / unique-first / event / rival hygiene Wave-2-grade.  
- Honest Sunday-open gap on daily Yahoo.

---

## RUN blockers

1. FREE_YF DATA gate PASS WITH CONDITIONS (ORION/DATA)  
2. Amend stale Hold → Passed + SURVIVES vocabulary (R1)  
3. Lock four-way primary **or** week-subset label (R2)  
4. No MERCURY · No Wave 1 on FREE_YF · No peek  

---

## Decision

**HYPOTHESIS SURVIVED RED TEAM REVIEW** — nearest-side packaging clears H009 HOLD.

**Do not RUN** until R1/R2 labeling locks + tape gate. Do not run superseded H009.

When R1/R2 done: SURVIVES may cite **Passed 022 nearest-side** with mandatory **PARAMETER Mon-open proxy** and either **four-way primary** or **week-subset** disclaimer.

---

## Path

`investigations/INV-002-methodology-seed/reviews/wave2/CASSANDRA_H009b_REDTEAM_2026-09-13.md`
