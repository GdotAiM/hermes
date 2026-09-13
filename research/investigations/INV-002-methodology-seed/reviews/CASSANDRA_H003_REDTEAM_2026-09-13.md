# CASSANDRA — Red Team Review: QUANT H003 (7–9 sweep → opposite)
**Target:** `experiments/QUANT_H003_79_SWEEP_OPPOSITE_PROTOCOL_2026-09-13.md`  
**Investigation:** INV-002 · Wave 1  
**Date:** 2026-09-13  
**Requestor:** ORION (packaging only; stress **control choice**)  
**Parents:** Passed C-METH-003, 004, 006  
**Verdict:** **HOLD — DO NOT RUN**  
**Survived?** **No** — primary control is not a single locked design; selection/geometry risks dominate.

---

## Scope

Packaging attack before tape. ORION standing note: CASSANDRA attacks control before RUN. Format: PROBLEM / WHY IT MATTERS / EVIDENCE REQUIRED / TEST / SEVERITY.

---

## Credit

- Pre-reg lock; 9:30 open; no INV-001 lunch.
- Clear mechanical first-sweep definition (touch, 0 buffer primary).
- Horizons 10:00 / 11:00 / 12:00 reported (though multiplicity — Attack 5).
- Explicit invitation to replace control pre-peek — good process hygiene.
- No MERCURY stated in blockers.

---

## ATTACK 1 — Primary control is two incompatible designs in one cell

**PROBLEM:** §4 “Primary” control lists **both**: (A) no-sweep-by-12:00 days with \(P(\text{touch both extremes by 12:00})\), **or** (B) random pseudo-sweep side at 09:30 measuring opposite hit. These are different estimands, different samples, and different Δ numerators/denominators. Protocol does not pick one. Secondary “random-side on sweep days” is also ill-specified (see Attack 3).

**WHY IT MATTERS:** Researcher degrees of freedom on the exact object ORION asked CASSANDRA to police. Whichever control is quieter can be chosen post-hoc after peek — even if unintentional. Confirmation bias + false precision on Δ.

**EVIDENCE REQUIRED:** One primary control, ≤20 lines, frozen before RUN. Recommended default (pre-reg):

**Matched-time random-side control (all eligible 7–9 range days):**  
At 09:30, draw side \(S \in \{\text{high},\text{low}\}\) with p=1/2 (seeded). Success = touch opposite extreme by horizon **unconditional on an actual sweep**. Compare to treatment success on days with a real first sweep (same horizon). Report separately: treatment-only sample size vs control-all-days.

**Better scientific foil (co-primary or replacement):**  
Among days that touch **at least one** 7–9 extreme by horizon, compare \(P(\text{opp after first extreme})\) vs \(P(\text{opp if order reversed / random order})\) on the same day (paired). Reject no-sweep “both extremes” control.

**TEST:** Amend to **H003b** (or ORION-acked in-place if no peek) with exactly one primary control. Delete the “or” fork. No-sweep both-extremes control demoted or killed (Attack 2).

**SEVERITY:** **CRITICAL**

---

## ATTACK 2 — No-sweep “both extremes” control is stacked

**PROBLEM:** On days with **neither** extreme swept by 12:00, \(P(\text{touch both extremes by 12:00})\) is **≈0 by construction** (neither touched ⇒ both not touched). Using that as \(P_{\text{ctrl}}\) makes \(\Delta = P(\text{opp}|\text{sweep}) - \approx 0\) almost automatically positive whenever treatment rate >0.

**WHY IT MATTERS:** Guarantees a “SURVIVES”-shaped Δ without testing bread-and-butter. Fatal control bug if chosen.

**EVIDENCE REQUIRED:** Proof sketch in protocol that ctrl probability is not structurally near zero; or remove control.

**TEST:** Ban this control from falsification. If retained for descriptive coverage only, label **INVALID as Δ baseline**.

**SEVERITY:** **CRITICAL** (if used as primary; currently still on the table)

---

## ATTACK 3 — “Random-side on sweep days ≈0.5” sanity check is ill-posed

**PROBLEM:** Secondary: on days that already had a first sweep, “ignore actual first side; assign random side — should ≈0.5.” If actual first sweep was high at \(\tau_s\), and random assigns “low swept,” success = hit \(H_{79}\), which **already occurred** at \(\tau_s\). If random assigns the true side, success = opposite hit (same as treatment). Mixture is not a clean 0.5 null.

**WHY IT MATTERS:** False sanity check; can “confirm” or “refute” noise.

**EVIDENCE REQUIRED:** Drop or rewrite: e.g. only randomize on a held-out definition that does not reuse the realized first-sweep event.

**TEST:** Remove from §4 or replace with fill-depth / range-stratified baselines.

**SEVERITY:** **HIGH**

---

## ATTACK 4 — Selection: first-sweep days are not exchangeable with controls

**PROBLEM:** Treatment requires price to reach a 7–9 extreme after 09:30. That selects trending/expanding AM sessions. Opposite-boundary hit rate on those days can be high from **range expansion / mean reversion after extension**, not from the taught “sweep then aim opposite” package. Protocol does not stratify by \(H_{79}-L_{79}\) or by AM range vs prior ATR.

**WHY IT MATTERS:** Confounding; overfit to volatile days; narrative “bread-and-butter works” when “big mornings traverse ranges” is the real driver.

**EVIDENCE REQUIRED:** Pre-reg strata tertiles of 7–9 range width; report Δ within tertiles. Optional: match control days on \(R_{79}\) width (±bin).

**TEST:** SURVIVES lecture confirmation requires Δ>0 in **at least mid tertile**, not only widest (mirror H1b WIDTH-DEPENDENT idea). Label **RANGE-DEPENDENT** if only wide 7–9 bins work.

**SEVERITY:** **HIGH**

---

## ATTACK 5 — Horizon multiplicity (10:00 / 11:00 / 12:00)

**PROBLEM:** Primary horizon end **12:00**; also report 10:00 / 11:00. FAILS/SURVIVES cite one Δ but which horizon is primary for the gate is only implied (12:00). Three bites at the apple.

**WHY IT MATTERS:** Multiple comparisons; survivor horizon cherry-pick.

**EVIDENCE REQUIRED:** One primary horizon locked for §5 (recommend **11:00** or **12:00** with rationale). Others descriptive only — cannot flip SURVIVES.

**TEST:** §5 sentence: primary horizon = ____ only.

**SEVERITY:** **HIGH**

---

## ATTACK 6 — Lecture map: relative-equal lows vs full 7–9 HH/LL

**PROBLEM:** C-METH-006: sweep of **7–9 relative-equal lows (or the range extreme)** then aim opposite end. Protocol uses full \(H_{79}/L_{79}\) only. Equal-lows liquidity object ≠ always the range extreme.

**WHY IT MATTERS:** May test a broader, easier claim than the spoken bread-and-butter (equal lows). Or miss the lecture object.

**EVIDENCE REQUIRED:** ATLAS note: demo frames — equal lows vs range LL/HH. If equal lows distinct, primary should be equal-lows sweep with range opposite as target **or** dual map with rival.

**TEST:** ATLAS one-pager before RUN; if demo ≠ full-range extreme, **H003b** / NEW id for equal-lows primary.

**SEVERITY:** **HIGH**

---

## ATTACK 7 — Sweep = touch (0 buffer) vs “sweep” as takeout

**PROBLEM:** Primary sweep is `high ≥ H79` (touch). Spoken “swept below” often implies trade-through / liquidity takeout. Sensitivity +2 pts exists but is not in the SURVIVES gate.

**WHY IT MATTERS:** PARAMETER; false precision on touch vs pierce.

**EVIDENCE REQUIRED:** Co-report pierce (+1 tick or +2 pts) as mandatory sensitivity; if flip → **SWEEP-DEF-DEPENDENT**.

**TEST:** Lock primary touch **or** pierce; other co-reported; SURVIVES lecture claim needs agreement or explicit PARAMETER label.

**SEVERITY:** **MEDIUM**

---

## ATTACK 8 — Window [07:00, 09:00) excludes 09:00 bar

**PROBLEM:** Half-open window drops the 09:00 minute. Lecture “between 7 and 9” may include 09:00 print. Small but systematic HH/LL shift.

**WHY IT MATTERS:** Hidden clock PARAMETER (especially vs 9:30 open 30m later).

**EVIDENCE REQUIRED:** Co-report [07:00, 09:00] inclusive vs current; or ATLAS chart verticals.

**TEST:** Mark PARAMETER; sensitivity co-report.

**SEVERITY:** **LOW**

---

## ATTACK 9 — Trade-shaped metrics without trade hyp

**PROBLEM:** MAE/MFE invite MERCURY-style reading of a level-frequency test. Bread-and-butter is pedagogically a setup.

**WHY IT MATTERS:** Scope creep into implied edge.

**EVIDENCE REQUIRED:** Explicit: MAE/MFE descriptive only; any entry/stop/target = NEW hyp; no MERCURY.

**TEST:** Add sentence to §1/§6 mirroring H001b.

**SEVERITY:** **MEDIUM** (process)

---

## ATTACK 10 — Thin protocol vs H001b standard

**PROBLEM:** Missing: coverage projection gate, IS/OOS/walk-forward detail, foil-vocabulary table, event calendar path cite, degenerate 2-pt justification, print META alignment with shared tape.

**WHY IT MATTERS:** Operational failure when tape arrives; inconsistent Wave-1 quality bar.

**EVIDENCE REQUIRED:** Bring H003 to H001b hygiene level in H003b.

**TEST:** Checklist parity with H001b §6–8 before RUN.

**SEVERITY:** **MEDIUM**

---

## Required locks before RUN

| # | Lock | Blocks RUN? |
|---|------|-------------|
| 1 | Single primary control — **kill** no-sweep both-extremes as Δ baseline | **YES** |
| 2 | Rewrite/remove random-side-on-sweep-days sanity | **YES** |
| 3 | Range-width strata + RANGE-DEPENDENT rule | **YES** for lecture SURVIVES |
| 4 | One primary horizon for §5 | **YES** |
| 5 | ATLAS equal-lows vs HH/LL map | **YES** soft→hard if demo disagrees |
| 6 | Shared tape + coverage | **YES** (external) |
| 7 | Pierce sensitivity + MAE/MFE non-trade label | Soft |

---

## Decision

**HYPOTHESIS DID NOT SURVIVE RED TEAM REVIEW** as packaging-/decision-ready.

Core failure mode is **control choice** (ORION’s ask): the listed primary control fork includes a structurally invalid no-sweep baseline. Fix via **H003b** before any run.

**No MERCURY. Do not RUN.**

---

## Path

`investigations/INV-002-methodology-seed/reviews/CASSANDRA_H003_REDTEAM_2026-09-13.md`
