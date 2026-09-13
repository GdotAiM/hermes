# CASSANDRA — Red Team Review: QUANT H009 (Weekly DOL)
**Target:** `experiments/wave2/QUANT_H009_WEEKLY_DOL_PROTOCOL_2026-09-13.md`  
**Investigation:** INV-002 · Wave 2  
**Date:** 2026-09-13  
**Requestor:** ORION (packaging; nearest-side DOL = PARAMETER until C-METH-022/023 Passed)  
**Parents:** C-METH-022, 023 — **Hold** (ASR; no DATA Pass)  
**Verdict:** **HOLD — DO NOT RUN**  
**Survived?** **No** — PARAMETER picker is the **wrong object** relative to ORION note and C-METH-022 ASR.

---

## Scope

Packaging only. No MERCURY. No Wave 1 on FREE_YF. Treat Week Lifecycle DOL vocabulary as **PARAMETER** until 022/023 Pass.

---

## Credit

- Explicit CONTINUOUS-YF / Yahoo week-boundary limitations.  
- No Wave 1 on this tape; no MERCURY.  
- Random-side foil → 0.5 null on unique-first weeks is clean for a binary picker.  
- Same-day dual-touch excluded from first-touch primary.  
- SURVIVES must say PARAMETER picker (intent right; object wrong — below).  
- Touch-rate descriptives separated from magic-% SURVIVES.

---

## ATTACK 1 — PARAMETER picker ≠ nearest-side DOL (022 / ORION)

**PROBLEM:** ORION: treat **nearest-side DOL** as PARAMETER until 022/023 Passed.  
C-METH-022 (Hold, ASR): at Sunday open, DOL is a **nearest-side** question — previous-week/month **high vs low**; shorter distance = path of least resistance.

H009 §4 instead locks:

> predicted side = direction of prior week’s close vs open (bull → expect PWL; bear → PWH)

That is a **trend / opposite-extreme** heuristic, **not** nearest-side distance from the week-open (or Friday close) to {PWH, PWL}. It does not implement 022’s structure even as PARAMETER, and it smuggles a different causal story (prior trend continuation/reversal) under the H009 DOL label.

§4 also contains drafting debris (“Actually re-read ORION…”, Test A/B muddle) — ambiguity on what is primary.

**WHY IT MATTERS:** Wrong hypothesis packaged as Wave-2 #1. Passing/failing the bull/bear picker says nothing about nearest-side DOL. Confirmation risk if ORION summaries say “H009 SURVIVED” meaning weekly DOL when the object was a different rule. Violates ORION’s explicit PARAMETER instruction.

**EVIDENCE REQUIRED:** Rewrite §4 primary picker to **PARAMETER nearest-side** pending 022 Pass:

1. Anchor \(P_0\) = Sunday/Monday week-open (first daily Open in \(W\)) **or** prior Friday close — pick one, label PARAMETER, co-report the other.  
2. Predicted DOL = \(\mathrm{PWH}\) if \(|P_0-\mathrm{PWH}| < |P_0-\mathrm{PWL}|\); else \(\mathrm{PWL}\); ties exclude or PARAMETER coin-flip.  
3. Optional descriptive (not primary until Observed): include prior-month H/L in the nearest-of-four set (022 mentions month) — else stay PWH/PWL only with explicit “week-only subset” label.  
4. Foil = random among the same candidate set.  
5. Success = first unique touch equals predicted extreme.  
6. Delete bull/bear close-open picker from primary (may live as **Rival PARAMETER** only, cannot sole-SURVIVES as “DOL”).  
7. Strip drafting notes from §4; one locked estimand.

**TEST:** File **H009b** (or ORION-acked in-place amend, no peek) with nearest-side picker. Re-review. Until then **HOLD**.

**SEVERITY:** **CRITICAL**

---

## ATTACK 2 — Parents still Hold — vocabulary inflation

**PROBLEM:** 022/023 are ASR Hold, not Passed. Protocol mostly labels PARAMETER, but statement still uses “DOL” heavily. Risk of narrating Hold ASR as Observed.

**WHY IT MATTERS:** Same class of failure as H003c red-line identity.

**EVIDENCE REQUIRED:** Every SURVIVES / summary: **PARAMETER nearest-side weekly extreme picker** (or whatever locked rule) — not “Observed DOL confirmed.” When 022/023 Pass, may force H009b/c if Observed rule ≠ frozen PARAMETER.

**TEST:** Prose ban table in §5 like H001b/H003c.

**SEVERITY:** **HIGH**

---

## ATTACK 3 — Continuous NQ=F / Yahoo week boundary

**PROBLEM:** Undocumented rolls; Yahoo week index Mon-labeled. Prior-week HH/LL can jump at rolls; week membership of daily bars can disagree with ICT Sunday-open framing (022 Sunday open).

**WHY IT MATTERS:** False touches; wrong prior week; Sunday-open nearest-side undefined on Mon-labeled weeks.

**EVIDENCE REQUIRED:** Run memo: week definition; how Sunday open maps; roll weeks flagged/excluded as sensitivity. Keep CONTINUOUS-YF label (already).

**TEST:** Exclude roll weeks as co-report; if Δ flips → **ROLL-DEPENDENT**.

**SEVERITY:** **HIGH**

---

## ATTACK 4 — Unique-first sample selection

**PROBLEM:** FAILS/SURVIVES on weeks with **unique** first touch only. Weeks that touch both same day or neither are dropped from accuracy — may bias toward orderly one-sided weeks.

**WHY IT MATTERS:** Selection; coverage must be reported; estimand is “among weeks with unique first touch.”

**EVIDENCE REQUIRED:** Coverage rates; INCONCLUSIVE if unique-first fraction too low; state restricted estimand in SURVIVES sentence.

**TEST:** Report % excluded; if unique-first <50% of eligible weeks, flag external validity.

**SEVERITY:** **MEDIUM**

---

## ATTACK 5 — Test A (Unif gap level) muddled with primary

**PROBLEM:** §4 introduces delivery-exists Unif foil then abandons clarity. Useful as VERIFY descriptive; dangerous if mixed into SURVIVES.

**WHY IT MATTERS:** Multiple endpoints.

**EVIDENCE REQUIRED:** Test A = descriptive only; one primary = nearest-side accuracy vs 0.5.

**TEST:** Clean §4 structure in H009b.

**SEVERITY:** **MEDIUM**

---

## ATTACK 6 — Event filter optional on primary

**PROBLEM:** Primary = all weeks; event stratum descriptive. Macro weeks may dominate extreme runs.

**WHY IT MATTERS:** Regime dependence — acceptable if labeled; optional tighten later.

**EVIDENCE REQUIRED:** Co-report non-event Δ; if flip → EVENT-SENSITIVE.

**TEST:** Soft.

**SEVERITY:** **LOW**

---

## Decision

**HYPOTHESIS DID NOT SURVIVE RED TEAM REVIEW** as packaging-ready.

**Required:** replace bull/bear picker with **PARAMETER nearest-side** (022-shaped) before any pilot. Then re-review as H009b.

**No RUN. No MERCURY. No Wave 1 on FREE_YF.**

---

## Path

`investigations/INV-002-methodology-seed/reviews/wave2/CASSANDRA_H009_REDTEAM_2026-09-13.md`
