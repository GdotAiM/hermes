# CASSANDRA — Red Team Review: QUANT H001 (RTH ORG CE by 10:00)
**Target:** `experiments/QUANT_H001_RTH_ORG_CE_PROTOCOL_2026-09-13.md`  
**Investigation:** INV-002-methodology-seed · Wave 1  
**Date:** 2026-09-13  
**Requestor:** ORION (verify-don’t-accept; 0.70 = FOIL only)  
**Parents:** Passed C-METH-008, 009, 015  
**Verdict:** **HOLD — DO NOT RUN** until HIGH estimand/null locks below are fixed (new file H001b or ORION-acked in-place amend — no peek)  
**Survived?** Packaging does **not** clear red team as decision-ready. Foil discipline and parent clock locks are strong; primary falsification is misaligned with the lecture ask.

---

## Scope

Attack design before tape. Mission: **verify-don’t-accept** time-to-half / P(hit CE by 10:00). 0.70 is withdrawn (C-METH-009) — foil only. Format: PROBLEM / WHY IT MATTERS / EVIDENCE REQUIRED / TEST / SEVERITY.

---

## Credit (not attacks)

- 9:30-only open; ASR 9:00 rejected (matches C-METH-008 amend).
- 0.70 labeled FOIL; never a SURVIVES target (matches C-METH-009).
- Overnight ORG CE vs 30m OR mid explicitly separated (015).
- No INV-001 lunch import; no MERCURY wrap.
- Event strata + coverage projection + N≥80 + pre-reg lock.

---

## ATTACK 1 — Primary estimand ≠ lecture verify ask

**PROBLEM:** C-METH-009 asks students to **keep a running frequency** of time-to-half / hit-by-10:00 and compute their own probability — verify, don’t accept ~70%. Protocol’s primary **FAILS/SURVIVES** gate (§5) is instead \(\Delta = P(\text{touch CE}) - P(\text{touch random gap level})\) (“CE-specialness”). Unconditional \(\hat P(\text{hit})\) is reported but is **not** the decision object. A world where \(\hat P \approx 0.68\) with tight CI (the actual verify product) can still **FAILS** if CE is no more special than a random interior level — or **SURVIVES** specialness while \(\hat P\) is 0.40. Neither maps cleanly to “did we verify the offered rate?”

**WHY IT MATTERS:** Wrong question dressed as H001. Confirmation/narrative risk: ORION summaries say “H001 SURVIVED” while readers hear “~70% verified” or the reverse. Selection of a clever null displaces the parent claim.

**EVIDENCE REQUIRED:** Single primary deliverable sentence aligned to C-METH-009: calibrated \(\hat P(\text{hit by 10:00})\) + CI on pre-reg population (non-event primary). CE-vs-random Δ as **secondary** scientific question (optional SURVIVES label with different name).

**TEST:** Amend §5:  
- **Primary verify product:** report \(\hat P\), CI, time-to-CE distro; foil 0.70 drawn on chart; **no pass/fail vs 0.70**.  
- **Optional secondary:** CE-specialness Δ vs pre-reg null (see Attack 2).  
- Ban bare “H001 SURVIVES” unless qualified: `SURVIVES (CE-specialness)` vs `VERIFY COMPLETE (frequency filed)` — never equate to 70% confirmation.

**SEVERITY:** **CRITICAL**

---

## ATTACK 2 — Random-gap-level null underspecified (+ geometry)

**PROBLEM:** §5 null #1: “random price level between \(P_{ref}\) and \(P_{open}\) (uniform on the gap segment) is touched by 10:00 — same path.” Missing: (a) one draw per day vs mean over many levels; (b) paired indicator on same path; (c) seed; (d) open/ref endpoints included in Unif? Geometrically, under partial gap fills from \(P_{open}\) toward \(P_{ref}\), levels **near the open** are touched more often than CE (midpoint is deeper). So \(E[P(\text{random})] > P(\text{CE})\) is the naive baseline — CE “FAILS specialness” may be the default, not a discovery. The interesting verify number remains \(P(\text{CE})\), not Δ.

**WHY IT MATTERS:** Ambiguous null → researcher degrees of freedom; geometric bias → predictable FAILS on specialness even when frequency estimate is solid. False precision on Δ.

**EVIDENCE REQUIRED:** Locked algorithm: e.g. each eligible day draw \(U \sim \mathrm{Unif}(\min(P_{ref},P_{open}), \max(\cdot))\) once (seeded); \(I_{CE}\), \(I_U\) on same [09:30,10:00] path; \(\Delta = \mathbb{E}[I_{CE}-I_U]\); bootstrap on days. Also report fill-depth curve: touch rate by normalized gap depth \(d \in [0,1]\).

**TEST:** Pre-RUN: write §5.1 null procedure ≤15 lines. If fill-depth curve is monotone decreasing from open, do not narrate Δ≤0 as “gap CE fails” without stating geometric expectation.

**SEVERITY:** **HIGH**

---

## ATTACK 3 — 16:14 prior print (futures vs equities; early closes)

**PROBLEM:** Parent locks “4:14 p.m. ET final print.” Equity cash session ends 16:00; index futures continue. Protocol uses 16:14 bar close / last print in that minute — good ICT match — but: early-close prior days, holidays, missing 16:14 bar, and whether “final print” means last trade in 16:14 vs settlement vs 16:00 cash close are not fully gated. Wrong \(P_{ref}\) shifts CE systematically.

**WHY IT MATTERS:** Hidden assumption in every CE. Contamination across DST, half-days, roll weeks.

**EVIDENCE REQUIRED:** DATA one-pager: for MNQ 1m ET, define \(P_{ref}\) on normal days, early closes, and day-after-holiday. Cite lecture chart if 16:14 overlay visible in L81eMQhmXmc evidence pack.

**TEST:** Exclude early-close prior days from primary **or** pre-reg alternate \(P_{ref}\) rule. Spot-check 10 random days: 16:14 bar exists and matches META.

**SEVERITY:** **HIGH**

---

## ATTACK 4 — 09:30 open print choice

**PROBLEM:** Default = 09:30 bar **open**; alt = “official RTH open print.” Opening auction / first printed trade can differ from bar open depending on vendor. Gap \(G\) and CE move with that choice.

**WHY IT MATTERS:** Vendor/parameter sensitivity on the entire study.

**EVIDENCE REQUIRED:** DATA locks one definition in stream C META before coverage projection. Sensitivity: bar-open vs first trade in 09:30 minute — report both; primary uses locked one.

**TEST:** Freeze in protocol §2 with path to META field. If Δ or \(\hat P\) flips across open defs, label **OPEN-PRINT-DEPENDENT**.

**SEVERITY:** **HIGH**

---

## ATTACK 5 — “By 10:00” includes the 10:00 bar

**PROBLEM:** Hit window **[09:30, 10:00] ET inclusive of the 10:00 bar**. Spoken “by 10:00 a.m.” may mean ≤10:00:00 (before 10:00 candle) or through the 10:00 minute. Inclusive adds up to 60 seconds of path; at 1m resolution this is one bar — material for borderline hits.

**WHY IT MATTERS:** PARAMETER disguised as obvious clock. Inflates \(\hat P\) vs a strict <10:00 rule.

**EVIDENCE REQUIRED:** ASR/context around C-METH-009 timestamp; if unclear, mark PARAMETER.

**TEST:** Primary = inclusive as written **or** switch to [09:30, 10:00) and co-report the other as sensitivity. Co-report mandatory; flip ⇒ **DEADLINE-DEPENDENT**.

**SEVERITY:** **MEDIUM**

---

## ATTACK 6 — Flat-gap exclusion \(|G| < 0.25\) MNQ pts

**PROBLEM:** Flat exclusion threshold is an unanchored PARAMETER (tick-ish but not derived from lecture).

**WHY IT MATTERS:** Small gaps may dominate “easy CE hits” (CE≈open). Excluding them changes \(\hat P\); including them dilutes.

**EVIDENCE REQUIRED:** Pre-reg justification (e.g. 1 tick MNQ = 0.25) + sensitivity \(|G|<0.25\) vs \(<1\) vs no exclusion.

**TEST:** Lock 0.25 as PARAMETER; report \(\hat P\) with and without flats in appendix; primary = exclude flats as written.

**SEVERITY:** **LOW**

---

## ATTACK 7 — Conditional model multiplicity

**PROBLEM:** Logistic on gap size, direction, event flag (and later 7–9 state) with OOS Brier/log-loss vs intercept — good intent — but feature set can expand when H002 classifier joins; multiple metrics (log-loss / Brier) allow cherry-pick.

**WHY IT MATTERS:** Multiple comparisons; optional stopping when H002 freezes.

**EVIDENCE REQUIRED:** Single primary OOS score pre-reg (recommend **Brier**); feature list frozen before fit; H002 join = NEW hyp or H001b amend with ORION ack **before peek**.

**TEST:** §5 lists one score only. Any added feature after first OOS look → NEW id.

**SEVERITY:** **MEDIUM**

---

## ATTACK 8 — Narrative conflation with 30m opening range

**PROBLEM:** Deadline 10:00 = end of first 30m OR (015). Hit-by-10:00 is “overnight-gap CE touched inside the OR window” even though CE ≠ OR mid. Easy to smuggle OR folklore into results prose.

**WHY IT MATTERS:** Narrative fallacy; cross-contamination with 015.

**EVIDENCE REQUIRED:** Results template sentence: “overnight ORG CE (16:14→09:30), not 30m OR midpoint.”

**TEST:** Checklist on Intelligence Summary; fail review if OR-mid language appears.

**SEVERITY:** **LOW**

---

## ATTACK 9 — Foil gravity (operational)

**PROBLEM:** Protocol correctly bans 0.70 as criterion. Humans still regress to “close to 70% = confirmed.”

**WHY IT MATTERS:** Exactly the failure mode C-METH-009 warns against.

**EVIDENCE REQUIRED:** SURVIVES/VERIFY vocabulary from Attack 1; plot foil as dashed “withdrawn lecture mention.”

**TEST:** Any draft saying “consistent with 70%” without CI-overlap caveats fails CASSANDRA prose review.

**SEVERITY:** **MEDIUM** (process)

---

## Required locks before RUN

| # | Lock | Owner | Blocks RUN? |
|---|------|-------|-------------|
| 1 | Primary estimand = verify frequency \(\hat P\)+CI; CE-specialness demoted/renamed | QUANT / ORION | **YES** |
| 2 | Null algorithm fully specified (+ fill-depth curve) | QUANT | **YES** if specialness kept |
| 3 | \(P_{ref}\) 16:14 policy (early close / holiday) | DATA | **YES** |
| 4 | \(P_{open}\) META lock + sensitivity | DATA / QUANT | **YES** |
| 5 | 10:00 inclusivity co-report | QUANT | Soft |
| 6 | Shared stream C / coverage projection | DATA / QUANT | **YES** (already) |
| 7 | Single conditional OOS score frozen | QUANT | Soft |

---

## Decision

**HYPOTHESIS DID NOT SURVIVE RED TEAM REVIEW** as run-/decision-ready.

Strong verify-don’t-accept **intent** and foil labeling; **CRITICAL** misalignment of FAILS/SURVIVES with C-METH-009’s actual ask, plus **HIGH** null and print-definition holes.

**Do not RUN. No MERCURY.** Prefer **H001b** once estimand/null/print locks are rewritten.

---

## Path

`investigations/INV-002-methodology-seed/reviews/CASSANDRA_H001_REDTEAM_2026-09-13.md`
