# CASSANDRA — H009b packaging score (for ORION)
**Target:** `experiments/wave2/QUANT_H009b_NEAREST_PWPM_PROTOCOL_2026-09-13.md`  
**Date:** 2026-09-13  
**Parents:** C-METH-022 / 023 / 025 — **Passed Observed**

---

## Verdict

**SURVIVED** (packaging)

**RUN: HOLD** — FREE_YF DATA gate only (design clear).

---

## Scorecard

| Item | Score |
|------|-------|
| Primary = nearest-side distance picker | **PASS** |
| Candidate set | **L4 = {PWH,PWL,PMH,PML}** (not PWH/PWL-only; two-way = sensitivity) |
| Bull/bear | **Rival only** — PASS |
| Passed Observed parents | **PASS** |
| Mon-open / Fri-close | PARAMETER proxies — labeled; Sunday-open identity **banned** |
| Foil | Uniform on L4 (E[acc]=0.25) — PASS |
| CONTINUOUS-YF / no Wave 1 / no MERCURY | PASS |

Note: ORION ask text said “|P0−PWH| vs |P0−PWL|” — that is the **L2 sensitivity** map. Locked primary on disk is **L4** (022 fidelity). Score uses the file.

---

## Prior reviews

- `CASSANDRA_H009_REDTEAM` — H009 HOLD (wrong picker)  
- `CASSANDRA_H009b_REDTEAM` + `CONFIRM` — SURVIVED; R2 L4 closed  

---

## Path

`reviews/wave2/CASSANDRA_H009b_ORION_SCORE_2026-09-13.md`
