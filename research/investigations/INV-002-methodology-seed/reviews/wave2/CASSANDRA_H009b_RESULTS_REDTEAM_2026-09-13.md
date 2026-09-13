# CASSANDRA — Result Red Team: H009b Pilot (FREE_YF)
**Target:** `experiments/wave2/results/H009b_PILOT_RESULTS_2026-09-13.md`  
**Artifact:** `H009b_unique_weeks.csv` (53 unique-first rows)  
**Protocol:** `QUANT_H009b_NEAREST_PWPM_PROTOCOL_2026-09-13.md`  
**Date:** 2026-09-13  
**Requestor:** ORION  

---

## Verdict

**AGREE: INCONCLUSIVE (N_OOS = 22 < 80).**  

**Do not upgrade to SURVIVES** despite Δ>0, CI>0, WF median>0. Directional numbers are **pilot / underpowered** only.

**No MERCURY. No Wave 1 claim.**

---

## Gate check

| Gate | Memo | CASSANDRA |
|------|------|-----------|
| OOS N≥80 | FAIL (22) | **Agree — decisive** |
| OOS Δ>0 | 0.3636 | Pass numerically; **not actionable** under N fail |
| OOS Δ CI entirely >0 | [0.0455, 0.6364] | Pass numerically; **wide / fragile** |
| WF median Δ>0 | 0.4000 | Pass numerically; **few folds on thin OOS** |
| L4 primary | Yes; L2 sensitivity | **PASS** |
| Proxy / CONTINUOUS-YF / no Sunday-open | Disclaimers present | **PASS** |
| Unique-first 52.5% | “OK” vs <50% flag | **PASS formal**; see Attack 3 |

---

## ATTACK 1 — SURVIVES gravity / false precision

**PROBLEM:** OOS P̂≈0.73 and Δ≈0.36 with CI above 0 invite “it works” narration. Protocol forbids SURVIVES without N≥80.

**WHY IT MATTERS:** Exactly the foil-gravity failure mode. Intelligence TLDR must lead with **INCONCLUSIVE**, not the point estimate.

**EVIDENCE REQUIRED:** ORION/Intelligence Summary first sentence = INCONCLUSIVE + N_OOS=22. Ban “promising edge” / “confirms 022” without N caveat.

**TEST:** Fail any draft that omits INCONCLUSIVE or implies SURVIVES.

**SEVERITY:** **HIGH** (process / narrative)

---

## ATTACK 2 — Foil OOS rate 0.36 vs E=0.25

**PROBLEM:** Under correct L4 uniform foil, E[acc_rand]=0.25. ALL foil≈0.245 (good); OOS foil=0.364 (elevated). With N=22 this can be noise (SE≈0.09), but also flags possible foil/path coupling or seed luck.

**WHY IT MATTERS:** Inflated foil lowers Δ; here foil is *high* so Δ is *conservative* on OOS — not an auto-cheat toward SURVIVES. Still need implementation audit before any future decision run.

**EVIDENCE REQUIRED:** Confirm U drawn independent of L*; success = first unique touch among L4 equals U. Recompute OOS foil mean over 10 seeds.

**TEST:** Multi-seed foil mean ∈ [0.15, 0.35] on OOS before trusting CI in a powered run.

**SEVERITY:** **MEDIUM**

---

## ATTACK 3 — Unique-first 52.5% barely clears flag

**PROBLEM:** Protocol external-validity flag at <50%. Memo at 52.5% says OK. Nearly half of processed weeks never enter the accuracy estimand (dual/neither first touch).

**WHY IT MATTERS:** Restricted estimand — “among orderly unique-first weeks.” Positive Δ may not generalize to all weeks.

**EVIDENCE REQUIRED:** Always state restricted estimand in TLDR (memo does). Soft: report dual-touch and neither rates.

**TEST:** Keep 52.5% as formal OK; do not treat as strong coverage.

**SEVERITY:** **MEDIUM**

---

## ATTACK 4 — Week HH/LL source vs protocol

**PROBLEM:** Protocol locks PWH/PWL from `NQ=F_1wk.csv`. Results tape line: prior week/month HH/LL **aggregated from daily** “for path consistency.” ISO week cited vs protocol Yahoo week index.

**WHY IT MATTERS:** Different prior extremes → different L* and first-touch. Silent PARAMETER drift from locked protocol.

**EVIDENCE REQUIRED:** Diff weekly-file HH/LL vs daily-aggregated ISO-week HH/LL on ≥20 weeks; if mismatch rate material → **NEW run id** or protocol amend pre-decision (ORION ack).

**TEST:** Before any N≥80 decision run, freeze one week definition + one HH/LL source in protocol and results META.

**SEVERITY:** **HIGH**

---

## ATTACK 5 — Underpowered walk-forward

**PROBLEM:** WF median Δ=0.40 with OOS N=22 and step-10 folds is a thin diagnostic, not a stability proof.

**WHY IT MATTERS:** False precision on “WF pass.”

**EVIDENCE REQUIRED:** Report number of WF windows and per-window Δ; or defer WF until N_OOS≥80.

**TEST:** Label WF as **exploratory** in this pilot.

**SEVERITY:** **MEDIUM**

---

## ATTACK 6 — L2 sensitivity N≠L4 N

**PROBLEM:** L2 OOS N=37 vs L4 OOS N=22 — different unique-first filters. Acc 0.89 looks hotter; cannot cross-compare to L4 or promote.

**WHY IT MATTERS:** Cherry-pick risk if someone cites L2.

**EVIDENCE REQUIRED:** Already “sensitivity only” — enforce in prose.

**TEST:** Ban L2 in any SURVIVES/022 confirmation sentence.

**SEVERITY:** **LOW** (handled if prose holds)

---

## Decision

| Claim | Allowed? |
|-------|----------|
| **INCONCLUSIVE (N_OOS<80)** | **YES — required** |
| SURVIVES Observed nearest-side (022) | **NO** |
| “Directional pilot interest under proxies” | YES only with INCONCLUSIVE first + CONTINUOUS-YF / Mon-open labels |
| MERCURY / Wave 1 | **NO** |

**HYPOTHESIS DID NOT SURVIVE a decision review** (correctly; N gate). Packaging still SURVIVED; pilot execution acceptable for a first FREE_YF cut pending Attack 4 freeze before powered re-run.

---

## Path

`investigations/INV-002-methodology-seed/reviews/wave2/CASSANDRA_H009b_RESULTS_REDTEAM_2026-09-13.md`
