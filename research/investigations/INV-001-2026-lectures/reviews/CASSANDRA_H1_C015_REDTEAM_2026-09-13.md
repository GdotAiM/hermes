# CASSANDRA — Red Team Review: QUANT H1 / C-2026-015
**Target:** `experiments/QUANT_H1_C015_PROTOCOL_2026-09-13.md`  
**Investigation:** INV-001  
**Date:** 2026-09-13  
**Requestor:** ORION (pre-tape; no run)  
**Parents:** Passed Observed C-2026-009 (+ 001–004)  
**Verdict:** **HOLD — DO NOT RUN until HIGH items below are locked or re-hyp’d**  
**Survived?** Protocol packaging does **not** clear red team as written. Several attacks are addressable without killing H1; two are structural (control mismatch; lecture-word ↔ mechanical map).

---

## Scope

Attack packaging and design risk **before** any OHLC results. Priority asks from ORION: (1) 11:30 PARAMETER vs Observed, (2) nearest vs “first” FVG, (3) B=4 HOD/LOD band, (4) CPI / day selection, (5) small N before expansion. Additional attacks found in protocol review.

Format per agent charter: PROBLEM / WHY IT MATTERS / EVIDENCE REQUIRED / TEST / SEVERITY.

---

## ATTACK 1 — Lunch start 11:30 is PARAMETER, not Observed speech

**PROBLEM:** Primary lunch window is locked as **PARAMETER [11:30, 13:30)** from arithmetic (Passed 001 length 2h + Passed 002 end 13:30). Spoken start is **not** Observed; chart ~11:30 and “10 o’clock” misspeak are explicitly non-Observed on C-2026-002. Protocol §0b correctly labels PARAMETER, but §2/§3.2 still make **11:30 the primary population gate** for raid/FVG birth. That silently imports taxonomy/chart into the treatment definition while the claim parent (C-2026-009) only says “2-hour lunch window.”

**WHY IT MATTERS:** If the true spoken object is “2h ending 13:30” with ambiguous start, fixing start at 11:30 changes which raids and which FVGs enter treatment. A “survives” result could be an artifact of the PARAMETER clock, then narrated as confirming the lecture. Confirmation bias + hidden assumption.

**EVIDENCE REQUIRED:** (a) ASR/spot-check that no spoken start binds 11:30 (already in C-002 amend — keep cited). (b) Pre-registered sensitivity: primary endpoint repeated on **[12:00, 13:30)** and optionally **[11:00, 13:30)** without retuning other knobs. (c) Explicit rule: SURVIVES language may not claim “Observed 11:30 lunch.”

**TEST:** Run (after tape) primary on PARAMETER [11:30,13:30) **and** sensitivity [12:00,13:30) as co-reported; if Δ sign/CI conclusion flips across windows, mark **CLOCK-DEPENDENT** — do not promote as lecture confirmation. Before run: amend §9 so SURVIVES requires agreement of primary + at least one pre-reg sensitivity window, **or** demote 11:30 to sensitivity and promote [12:00,13:30) if ORION prefers speech-minimal clock.

**SEVERITY:** **HIGH**

---

## ATTACK 2 — “Nearest pre-raid FVG” vs lecture “first” ambiguity

**PROBLEM:** Lecture (C-2026-009): “first fair value gap right before the liquidity is taken.” Protocol §3.3 maps this to **latest birth time ≤ τ_raid** (nearest in time), matching polarity, and explicitly rejects “chronologically first FVG of the lunch window.” That is a **reasonable interpretation**, not a forced reading. “First … right before” can mean (A) nearest prior matching FVG, (B) first FVG of the impulsive leg into the raid, or (C) first FVG after some displacement/MSS marker the protocol never defines.

**WHY IT MATTERS:** Wrong map = testing a different claim than the one ranked NEW-as-package. Nearest-in-time favors late micro-gaps that may be noise; “first of lunch” favors early gaps that may already be mid-filled. Either choice can manufacture or kill edge. Selection of definition after seeing charts would be post-hoc; here it is pre-registered — good — but still may not be the lecture object.

**EVIDENCE REQUIRED:** Timestamped quote + chart context from C90xGr3kW8Y (~00:10:09–00:10:37 and ~00:27:16–00:27:36) showing **which** FVG the speaker points to on the demo bar (order of print vs proximity). ATLAS/DATA: one annotated still or ASR+cursor note: nearest vs first-of-leg.

**TEST:** Pre-register **two** treatment defs as co-primary only if ORION accepts multiplicity correction; better: lock one as primary (nearest, current) and one as **pre-registered rival** (first eligible FVG in lunch with matching polarity, or first after first fractal swing of lunch). Rival reported; only primary falsifies. If demo chart clearly shows non-nearest, **NEW hyp ID** required — do not amend H1 in place.

**SEVERITY:** **HIGH**

---

## ATTACK 3 — HOD/LOD touch band B = 4 MNQ points

**PROBLEM:** Primary success = FVG zone overlaps \([H_{D+1}-B,\ H_{D+1}]\) or \([L_{D+1},\ L_{D+1}+B]\) with **B=4**. Lecture says revisit “many times” makes the high or low — not “within 4 points.” B is an unanchored PARAMETER. At MNQ ~4 pts is small vs daily range but large vs 1m noise; also interacts with zone **width** (wide FVGs touch the band more often by geometry).

**WHY IT MATTERS:** Inflates success rates for both treatment and control, but not necessarily equally (treatment FVGs from lunch raids may systematically differ in width/location vs random RTH FVGs). False precision: “near HOD/LOD” sounds lecture-faithful while B is researcher-chosen. Overfitting risk if B was mentally fit to the lecture chart day.

**EVIDENCE REQUIRED:** (a) Statement that B was chosen **before** any D+1 OHLC inspection (protocol claims this — keep audit). (b) Distribution of FVG zone widths for treatment vs control. (c) Sensitivity B∈{0,2,4,8} already listed — must be **pre-outcome** and not used to pick a survivor story.

**TEST:** Primary falsification at **B=0** (exact overlap with HOD or LOD **print** as zone overlap with the extreme bar’s extreme — define precisely) **or** keep B=4 but require SURVIVES also at B=0 secondary gate. Report width-stratified Δ (tertiles of zone height). If only B≥4 survives, label **BUFFER-DEPENDENT**, not lecture confirmation.

**SEVERITY:** **HIGH**

---

## ATTACK 4 — CPI contamination / day selection

**PROBLEM:** Protocol excludes CPI and FOMC from primary and reports CPI stratum separately — good. Residual risks: (1) other event days (NFP, FOMC minutes, unexpected prints) not listed; (2) **excluding** event days changes the estimand away from “next RTH session” as traders experience it; (3) lecture chart date 2026-03-11 sits in a real macro calendar — pilot plumbing on lecture-aligned dates invites narrative contamination even if not used for SURVIVES/FAILS; (4) “raid days only” already selects a conditioned population (see Attack 6).

**WHY IT MATTERS:** Event days can dominate HOD/LOD formation; pooling or silent inclusion biases Δ. Over-exclusion can make a fragile lunch pattern look clean. Selection bias + regime dependence.

**EVIDENCE REQUIRED:** Locked event calendar file (CPI + FOMC + NFP at minimum) with timezone. Count of excluded days vs eligible. Explicit estimand sentence: “H1 primary = non-event RTH days after lunch-raid treatment.”

**TEST:** Pre-register exclusion set **before** tape expansion beyond pilot. Report N and Δ for: primary non-event; CPI-only stratum; all-days pooled (descriptive). If pooled flips conclusion vs primary, flag **EVENT-SENSITIVE**. Do not use 2026-03-10..11 for any decision metric (already stated — enforce in code + review checklist).

**SEVERITY:** **MEDIUM** (controls present; gaps remain)

---

## ATTACK 5 — Small N before expansion / pilot temptation

**PROBLEM:** Decision rule N≥80 pairs is sound; pilot 2026-03-10..11 is plumbing-only. Risks: (1) walk-forward and 60/40 split on thin post-expansion history still underpowered; (2) coverage filters (need raid + matching pre-raid FVG + next full RTH) may yield << calendar days; (3) pressure to “peek” pilot chart because it is the lecture example; (4) expansion “subsequent MNQ months/years” without power analysis may stop at first pretty OOS.

**WHY IT MATTERS:** Small samples → false precision on Δ and bootstrap CI. Lecture-day peek → look-ahead / confirmation. Stopping rules ambiguous → optional stopping bias.

**EVIDENCE REQUIRED:** Expected yield model: P(raid)×P(pre-raid FVG)×P(full next RTH) under DATA once stream C exists — before claiming N≥80 is reachable in horizon T. Hard stop: no SURVIVES/FAILS language until N≥80 OOS (already in §9).

**TEST:** After stream C for ≥20 consecutive RTH days (still no hyp test): report coverage diagnostics only. Gate expansion: do not open OOS decision until projected N_pairs ≥80 under frozen defs. Document any human chart viewing of pilot in an audit note (even “plumbing debug”).

**SEVERITY:** **MEDIUM** (rule exists; operational failure is the risk)

---

## ATTACK 6 — Control is not time-/regime-matched (structural)

**PROBLEM:** Treatment FVG is a **lunch-window, polarity-matched, pre-raid** gap. Control (§5) is a **uniform random other RTH FVG** the same day (full RTH primary). That confounds: time-of-day, proximity to a liquidity event, polarity, and likely zone geometry. A positive Δ may only mean “FVGs near lunch raids differ from random RTH FVGs,” not that the **packaged lecture sequence** predicts next-day HOD/LOD better than a fair foil.

Secondary time-matched control exists but is secondary and allows either polarity.

**WHY IT MATTERS:** Wrong null → false discovery of “H1 edge.” Highest scientific risk in the design after lecture-map risk.

**EVIDENCE REQUIRED:** Pre-registered primary control that matches: (i) birth in lunch window, (ii) same polarity rule XOR explicitly random polarity, (iii) **not** conditioned on being immediately pre-raid — e.g. random lunch FVG of matching polarity with birth in [11:30, τ_raid), or a random lunch FVG on days **without** a raid (different estimand — specify).

**TEST:** Elevate time-matched same-polarity lunch FVG to **co-primary or sole primary control**. Keep random RTH FVG as negative/weak control only. If Δ vs weak control >> Δ vs matched control, current H1 overclaims packaging.

**SEVERITY:** **CRITICAL**

---

## ATTACK 7 — Treatment-day selection (raid required; last raid only)

**PROBLEM:** Days without a mechanically defined turtle-soup raid contribute no treatment unit; multiple raids → **last** before 13:30. Coverage is reported (good) but primary Δ is estimated on a selected subset. Raid definition itself stacks PARAMETERS: fractal swing (3 lower highs), N_raid=15m, running lunch HOD break.

**WHY IT MATTERS:** Selected high-activity lunch days may have next-day extremes that revisit many prior levels (including random FVGs), shrinking or inflating Δ unpredictably. “Last raid” may not match the lecture’s pedagogical raid. Extra knobs → overfitting surface even if frozen.

**EVIDENCE REQUIRED:** Lecture demo: which raid if multiple? ASR. Coverage table before any Δ claim. Sensitivity N_raid∈{10,15,20} and first-raid vs last-raid as labeled sensitivity **after** primary OOS only if primary locked.

**TEST:** Pre-register first-raid vs last-raid as rival treatment clock (report; one primary). If coverage <30% of RTH days, state external validity limit in any ORION summary.

**SEVERITY:** **MEDIUM**

---

## ATTACK 8 — Wide-zone geometric touch vs “makes the high or low”

**PROBLEM:** Success is zone **overlap** with a B-band at the extreme, not “the high/low was made **from** that level” or “price turned there.” A tall FVG can overlap the HOD band while the actual turning price is elsewhere. Ex-post HOD/LOD metric is acknowledged as non-trade (§10) but will be narrated as method confirmation.

**WHY IT MATTERS:** Narrative fallacy / false precision. Level-revisit frequency ≠ causal delivery of the extreme.

**EVIDENCE REQUIRED:** Secondary metric already lists exact touch and MAE/MFE — promote a **turn metric**: did the session extreme print occur while price was interacting with the zone (e.g. extreme bar overlaps zone), reported beside primary.

**TEST:** Require reporting of “extreme bar overlaps zone” rate for treatment vs control; if primary B-overlap succeeds but extreme-bar overlap does not, do not claim lecture confirmation.

**SEVERITY:** **MEDIUM**

---

## ATTACK 9 — Lecture-aligned seed dates (hindsight gravity)

**PROBLEM:** Pilot period ≥2026-03-10..11 is the lecture chart context. Even plumbing-only invites fitting code paths, raid defs, and FVG picks to the known example.

**WHY IT MATTERS:** Look-ahead / confirmation bias in implementation; silent hyperparameter freeze after watching the demo tape.

**EVIDENCE REQUIRED:** Code + protocol hash frozen before any plot of D+1 outcomes; plumbing tests use synthetic or scrambled timestamps where possible; human viewing log.

**TEST:** Separate `plumbing_ok` flag from any numeric touch rates on pilot days in artifacts (NaN / redacted in decision tables).

**SEVERITY:** **LOW** (already policy; enforce operationally)

---

## ATTACK 10 — Falsification / multiplicity

**PROBLEM:** §9 FAILS if CI includes ≤0 — appropriate for superiority vs control. Sensitivities (B, N_raid, windows) after OOS can still generate a survivor story if ORION summarizes carelessly. H2/H3 parallel designs increase family-wise error if later “jointly claimed.”

**WHY IT MATTERS:** Multiple comparisons; optional narrative cherry-pick.

**EVIDENCE REQUIRED:** Single primary endpoint sentence in ORION summary. Any sensitivity that changes decision → NEW hyp or explicit multiplicity note.

**TEST:** Checklist item on Intelligence Summary: one Δ only for H1 claim.

**SEVERITY:** **LOW** (protocol mostly correct)

---

## What is already strong (credit, not attacks)

- Pre-registration lock + NEW hyp ID on post-peek changes.
- PARAMETER label for 11:30 in §0b (must not be forgotten in prose).
- Plumbing pilot ≠ decision sample.
- Bootstrap CI + OOS + walk-forward median gate.
- CPI/FOMC stratification intent.
- Explicit non-trade primary (blocks MERCURY misuse without new hyp).

---

## Required locks before RUN (gate for ORION / QUANT / DATA)

| # | Lock | Owner | Blocks run? |
|---|------|-------|-------------|
| 1 | Primary **control** = lunch time-matched, same-polarity FVG (random RTH demoted) | QUANT | **YES** |
| 2 | Written ORION/ATLAS note: nearest-pre-raid = accepted map of “first … right before,” or rival def + primary pick | ORION / ATLAS | **YES** |
| 3 | B policy: primary B=0 **or** SURVIVES requires B=0 agreement; width strata reported | QUANT | **YES** |
| 4 | Clock policy: 11:30 PARAMETER cannot appear as Observed in summaries; sensitivity window co-reported | ORION / QUANT | **YES** for claim language; run OK if labeled |
| 5 | Event calendar file (CPI, FOMC, NFP) path cited in protocol | DATA / MACRO | Soft — before expansion beyond pilot |
| 6 | Coverage + projected N≥80 before OOS decision | QUANT / DATA | Soft — before SURVIVES/FAILS |
| 7 | Tape stream C | DATA | **YES** (already) |

---

## Decision

**HYPOTHESIS DID NOT SURVIVE RED TEAM REVIEW** as a run-ready protocol.

H1 remains **interesting** and still ORION #1 on information gain **if** Attack 6 (control) and Attack 2 (lecture map) are fixed under the same hyp ID **only when** changes are labeling/control elevation already foreshadowed — else **NEW hyp ID** per §0.

**Do not** clear MERCURY/RISK wrappers. **Do not** treat any future pilot touch rate as evidence.

---

## File path

`investigations/INV-001-2026-lectures/reviews/CASSANDRA_H1_C015_REDTEAM_2026-09-13.md`
