# CASSANDRA — H003 re-attack (locked paired random-side control)
**Target:** `experiments/QUANT_H003_79_SWEEP_OPPOSITE_PROTOCOL_2026-09-13.md` (updated unpark; §4 single primary)  
**Prior:** `reviews/CASSANDRA_H003_REDTEAM_2026-09-13.md` (HOLD — control fork / invalid no-sweep baseline)  
**Date:** 2026-09-13  
**Requestor:** QUANT/ORION — packaging only; attack new primary control  
**Verdict:** **HOLD — DO NOT RUN**  
**Survived?** **No** — “or” fork removed (good), but the new paired random-side control is **ambiguous** and, on the natural reading, **structurally biased** (Δ expected ≤ 0).

---

## What improved

- Single primary control declared; no-sweep baseline demoted to descriptive (addresses prior CRITICAL fork + stacked both-extremes).
- Coverage / N≥80 / event calendar / IS-OOS / no MERCURY language added (partial hygiene parity).
- Dual-sweep same-bar exclude rule noted.

---

## ATTACK C1 — Paired random-side control is ill-posed on first-sweep days

**PROBLEM:** Primary control (§4): on the **same** first-sweep days, assign a **random side** “as if it were the first sweep,” then \(P(\text{hit opposite of random side})\), paired vs actual first-sweep success.

Natural algorithmic reading for day with actual first sweep = **high** at \(\tau_s\):

| Random draw | “Opposite of random” | After \(\tau_s\)? |
|-------------|----------------------|-------------------|
| high (matches actual) | \(L_{79}\) | = treatment success |
| low (≠ actual) | \(H_{79}\) | \(H_{79}\) **already traded at \(\tau_s\)** (the sweep). Overlap of \(H_{79}\) after/at sweep is ~automatic |

So \(\mathbb{E}[I_{ctrl}] \approx \tfrac12 P(\text{treat}) + \tfrac12 \cdot 1\), hence  
\(\mathbb{E}[\Delta] = P(\text{treat}) - \big(\tfrac12 P(\text{treat}) + \tfrac12\big) = \tfrac12\big(P(\text{treat})-1\big) \le 0\).

**FAILS becomes the default**, not a discovery. SURVIVES is nearly unreachable even if bread-and-butter is real.

If QUANT meant a different procedure (e.g. random side judged from **09:30**, not from \(\tau_s\); or success never credits the already-swept extreme), the protocol **does not say so**. Ambiguity = researcher degrees of freedom.

**WHY IT MATTERS:** Control choice was the entire point of this packaging pass. A null that forces Δ≤0 (or an underspecified null) fails the scientific job — either auto-FAILS a true effect or allows silent reinterpretation after peek.

**EVIDENCE REQUIRED:** ≤15-line null algorithm with: (1) when random side is drawn; (2) time origin for control success (09:30 vs \(\tau_s\)); (3) whether the realized sweep extreme can satisfy control success; (4) seed; (5) worked numeric example on a swept-high day.

**TEST:** Reject current §4 primary until rewritten. Preferred replacements (pick **one** pre-peek):

**A. Random side at 09:30 (all eligible range days, not only sweep days):**  
Draw \(S\); success = touch opposite of \(S\) by horizon from 09:30. Treatment stays sweep-conditioned. Different samples — report clearly; optionally IPW/match on \(R_{79}\).

**B. Second-extreme / order foil (sweep days that eventually touch both):**  
Among days that touch both 7–9 extremes by horizon, test whether “first then opposite” ordering frequency / time-to-second beats a pre-reg null (e.g. random order of the two touch times). Different estimand — label it.

**C. Level foil on sweep days:**  
After actual \(\tau_s\), compare hit of true opposite vs hit of a Unif level in the open half of the remaining range (fill-depth style) — isolates “opposite boundary” vs “any deep retrace.”

Do **not** keep “random side on same first-sweep days” without killing auto-credit of the already-swept extreme.

**SEVERITY:** **CRITICAL**

---

## ATTACK C2 — Still no range-width strata / RANGE-DEPENDENT gate

**PROBLEM:** Prior HIGH Attack 4 uncleared. First-sweep days select expansion mornings; Δ (even with a fixed control) can be width-driven.

**WHY IT MATTERS:** Confounding; lecture SURVIVES overclaim.

**EVIDENCE REQUIRED:** Tertiles of \(H_{79}-L_{79}\); RANGE-DEPENDENT if only widest tertile carries Δ.

**TEST:** Add to §5 before RUN.

**SEVERITY:** **HIGH**

---

## ATTACK C3 — Horizon multiplicity uncleared

**PROBLEM:** Primary horizon 12:00 with co-report 10:00/11:00; §5 does not freeze which horizon owns FAILS/SURVIVES (implied 12:00 only — say it).

**WHY IT MATTERS:** Multiple comparisons.

**EVIDENCE REQUIRED:** One sentence: falsification horizon = 12:00 ET only; others descriptive.

**TEST:** Amend §5.

**SEVERITY:** **HIGH** (easy fix)

---

## ATTACK C4 — Equal-lows vs full HH/LL map uncleared

**PROBLEM:** C-METH-006 allows relative-equal lows **or** range extreme. Protocol still full \(H_{79}/L_{79}\) only.

**WHY IT MATTERS:** Wrong object risk.

**EVIDENCE REQUIRED:** ATLAS demo lock before RUN (or rival equal-lows map).

**TEST:** Gate RUN on ATLAS note path.

**SEVERITY:** **HIGH**

---

## ATTACK C5 — Pierce sensitivity still post-OOS only

**PROBLEM:** +2 pts sweep buffer is “post-OOS descriptive.” Touch vs takeout still open (prior MEDIUM).

**WHY IT MATTERS:** PARAMETER; lecture “swept below.”

**EVIDENCE REQUIRED:** Mandatory co-report pierce before citing SURVIVES as lecture confirmation.

**TEST:** Soft lock in H003b.

**SEVERITY:** **MEDIUM**

---

## Decision

**HYPOTHESIS DID NOT SURVIVE RED TEAM REVIEW** (recontrol pass).

Removing the no-sweep fork was necessary but not sufficient. **H003b** (or ORION-acked rewrite of §4–5) required: valid null algorithm + horizon lock + range strata + ATLAS map gate.

**No RUN. No MERCURY.** Prior `CASSANDRA_H003_REDTEAM_2026-09-13.md` HOLD stands, upgraded by this recontrol failure mode.

---

## Path

`investigations/INV-002-methodology-seed/reviews/CASSANDRA_H003_RECONTROL_2026-09-13.md`
