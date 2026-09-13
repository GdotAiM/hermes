# CASSANDRA — Red Team Re-Review: QUANT H1b / C-2026-015
**Target:** `experiments/QUANT_H1b_C015_PROTOCOL_2026-09-13.md`  
**Prior:** `reviews/CASSANDRA_H1_C015_REDTEAM_2026-09-13.md` (H1 HOLD)  
**Investigation:** INV-001  
**Date:** 2026-09-13  
**Trigger:** QUANT filed H1b after ORION accepted HOLD; standing order to re-review when filed  
**Peek status:** Accepted as pre-reg revision (no tape results claimed)  
**Verdict:** **HYPOTHESIS SURVIVED RED TEAM REVIEW** (packaging / pre-reg design)  
**Run clearance:** **NOT GRANTED** — external gates remain (ATLAS FVG map, DATA stream C, event calendar, coverage projection). Residual MEDIUM items below should be locked before RUN, not used as quiet post-peek knobs.

---

## Disposition of prior attacks

| Prior # | Issue | H1b status | Notes |
|--------:|-------|------------|-------|
| 6 | Control mismatch (CRITICAL) | **CLEARED** | Primary = time-matched same-polarity lunch FVG; random RTH demoted to descriptive |
| 1 | 11:30 PARAMETER vs Observed | **CLEARED** (conditional) | PARAMETER label + co-report [12:00,13:30) + SURVIVES language ban + flip ⇒ no lecture SURVIVES |
| 2 | Nearest vs “first” FVG | **CLEARED** (ATLAS) | `evidence/C90xGr3kW8Y/FVG_DEMO_LOCK.md` — nearest/BISI at raid; first-of-impulse = rival only |
| 3 | B=4 buffer | **CLEARED** | B=0 primary; width tertiles; B>0 descriptive only |
| 4 | CPI / day selection | **CLEARED** (soft DATA) | CPI+FOMC+NFP; strata; calendar file still a DATA blocker |
| 5 | Small N / pilot temptation | **CLEARED** | Coverage projection; pilot metrics banned |
| 7 | Last-raid selection | **OPEN residual** | First-raid rival after OOS only — acceptable if not survivor-picked |
| 8 | Geometric touch ≠ turn | **PARTIALLY CLEARED** | Extreme-bar overlap secondary; B=0 still pure containment — see new Attack R1 |
| 9 | Lecture-aligned seed | **CLEARED** | Plumbing / NaN policy retained |
| 10 | Multiplicity | **CLEARED** | One primary Δ stated |

---

## New / residual attacks on H1b

### ATTACK R1 — B=0 containment still favors wide zones

**PROBLEM:** Locked B=0 success is `zone_low ≤ H_{D+1} ≤ zone_high` (or LOD). A sufficiently wide FVG that spans a large fraction of the prior day’s lunch range can contain next-day extremes by geometry. Width tertiles are reported but **not** part of the SURVIVES gate.

**WHY IT MATTERS:** False precision / narrative fallacy: “makes the high or low” can be large-box containment. Treatment vs control may differ in width distribution even after polarity/time match (nearest-pre-raid gaps may be systematically tighter or wider).

**EVIDENCE REQUIRED:** Width distribution treatment vs control; tertile-specific Δ; optionally max zone height cap pre-registered.

**TEST:** Before RUN, add to §9: if overall SURVIVES but **only** the widest tertile shows Δ>0 with CI>0 while narrow/mid do not, label **WIDTH-DEPENDENT** — do not promote as lecture confirmation. Prefer also reporting extreme-bar overlap Δ beside primary in any ORION summary.

**SEVERITY:** **MEDIUM**

---

### ATTACK R2 — Rival treatment vs control collision

**PROBLEM:** Primary control is drawn from eligible lunch same-polarity FVGs **excluding the nearest (primary) treatment**. The rival treatment is **first-of-window**. That rival FVG remains eligible for the control draw. Control can equal the rival, making descriptive Δ_rival ill-defined or biased toward null/noise.

**WHY IT MATTERS:** Corrupt rival diagnostic → false reassurance that nearest vs first “doesn’t matter,” or false conflict. Does **not** break primary Δ, but breaks Attack-2 insurance.

**EVIDENCE REQUIRED:** Explicit rule for rival analysis sample.

**TEST:** Pre-RUN lock (ORION ack, same H1b file amend allowed as labeling/diagnostic hygiene if no peek): when reporting Δ_rival, either (a) redraw control excluding **both** primary treatment and rival FVG, or (b) drop pairs where control == rival, or (c) use a fixed second draw seeded for rival-only. State which in §5/§8.

**SEVERITY:** **MEDIUM** (primary OK; rival path not yet safe)

---

### ATTACK R3 — Matched-control availability selects choppy lunches

**PROBLEM:** Pair requires ≥2 same-polarity FVGs in \(W\) before \(\tau_{raid}\) (treatment + ≥1 control). Days with a single clean pre-raid FVG drop out (“raid+treatment but no matched control”).

**WHY IT MATTERS:** Selection bias toward multi-gap lunch sessions (often faster/choppier). Estimand becomes “nearest vs other lunch FVG on multi-gap raid days,” narrower than C-2026-009’s plain packaging claim.

**EVIDENCE REQUIRED:** Coverage line for matched-control failure rate; comparison of next-day range or ATLAS day-type on included vs excluded treatment days.

**TEST:** Report exclusion rate; if matched-control miss >25% of treatment days, ORION summary must state restricted estimand. Optional secondary: synthetic control = time-shifted FVG from prior non-event day (new hyp if used for falsification).

**SEVERITY:** **MEDIUM**

---

### ATTACK R4 — Soft escape on CLOCK-DEPENDENT SURVIVES

**PROBLEM:** §9 SURVIVES clause 3 allows “pre-declared CLOCK-DEPENDENT non-promotion if ORION accepts PARAMETER-clock edge only.” Default correctly denies lecture SURVIVES on flip, but the escape invites reframing a PARAMETER-only edge as a win.

**WHY IT MATTERS:** Reopens Attack 1 via narrative: organization could claim “H1b survived” meaning clock-edge while readers hear lecture confirmation.

**EVIDENCE REQUIRED:** Hard vocabulary split in ORION/Intelligence Summary templates.

**TEST:** Lock language: **SURVIVES (lecture confirmation)** requires no clock flip. **SURVIVES (PARAMETER-clock only)** is a **different claim label** — requires NEW hyp id or explicit non-lecture tag, never bare “H1b SURVIVES.”

**SEVERITY:** **MEDIUM**

---

### ATTACK R5 — B=0 dual wording before lock line

**PROBLEM:** §4 first states success via extreme **bar** overlap OR zone contains extreme, then “Operational B=0 definition (locked)” is containment-only. Implementers may code the looser bar rule.

**WHY IT MATTERS:** Specification ambiguity → researcher degrees of freedom.

**EVIDENCE REQUIRED:** Single normative sentence; delete or clearly mark the bar-overlap sentence as secondary only.

**TEST:** QUANT one-line amend: primary = containment iff; extreme-bar overlap = secondary metric only (already listed). Do before code freeze.

**SEVERITY:** **LOW**

---

### ATTACK R6 — Raid stack still PARAMETER-heavy (carried)

**PROBLEM:** Fractal swing + N_raid=15 + last-raid primary unchanged. Sensitivities deferred post-OOS.

**WHY IT MATTERS:** Overfitting surface remains; acceptable for v1 if frozen and not peeked.

**EVIDENCE REQUIRED:** No change pre-run; audit that sensitivities stay post-primary.

**TEST:** Checklist on results memo: primary raid def only in SURVIVES sentence.

**SEVERITY:** **LOW**

---

## Cleared design claims (credit)

- CRITICAL control fix is real: estimand now isolates **nearest-pre-raid selection** vs other lunch same-polarity FVGs — the right scientific question for the package.
- B=0 + width strata + BUFFER-DEPENDENT label close the false-precision buffer hole.
- Clock PARAMETER discipline + co-report + language ban are enforceable if ORION prose complies.
- ATLAS gate before RUN is the correct handling of lecture-map ambiguity (not a silent assumption).
- Pilot / coverage / N≥80 / event calendar (incl. NFP) address operational failure modes from H1 review.
- H1b as new id (not silent amend) respects pre-reg ethics after structural change.

---

## Run blockers (unchanged external + residual locks)

| # | Blocker | Owner | Design fail? |
|---|---------|-------|--------------|
| 1 | Tape stream C | DATA | No |
| 2 | Event calendar file (CPI, FOMC, NFP) | DATA / MACRO | No |
| 3 | ATLAS co-sign on nearest map | ATLAS | **CLEARED** 2026-09-13 (`FVG_DEMO_LOCK.md`) |
| 4 | Coverage projection on ≥20 RTH days before OOS decision | QUANT / DATA | No |
| 5 | Fix rival/control collision rule (Attack R2) | QUANT (+ ORION ack) | Yes if rival Δ will be cited |
| 6 | WIDTH-DEPENDENT rule in §9 (Attack R1) | QUANT | Recommended before RUN |
| 7 | Harden CLOCK-DEPENDENT vocabulary (Attack R4) | ORION | Recommended before any SURVIVES prose |

Items 5–7 are **pre-run hygiene**, not reasons to reject H1b packaging wholesale. Items 1–4 remain hard RUN blocks.

---

## Decision

**HYPOTHESIS SURVIVED RED TEAM REVIEW** — H1b packaging addresses the H1 HOLD at CRITICAL/HIGH level with appropriate external gates.

**Do not RUN** until DATA blockers clear (stream C, event calendar, coverage projection) and residual R1/R2/R4 locks are acknowledged. ATLAS map gate: **cleared**.  
**Do not** wrap MERCURY/RISK.  
**Do not** run superseded H1.

ATLAS confirmed nearest; reversal of that lock would require **NEW hyp ID**.

---

## File path

`investigations/INV-001-2026-lectures/reviews/CASSANDRA_H1b_C015_REDTEAM_2026-09-13.md`

---

## Addendum — ATLAS FVG map (same day)

Reviewed `evidence/C90xGr3kW8Y/FVG_DEMO_LOCK.md` after STATUS showed lock filed during this re-review.

**Finding:** Demo cursor/speech at ~00:02:40 / ~00:10:21 / ~00:27:26 support **nearest inefficiency immediately before the raid** (BISI under raid high). Lower first-of-impulse boxes are visible and **not** the pointed object. Reading of “first … right before” as nearest-in-pocket is accepted.

**Effect:** Prior Attack 2 / H1b ATLAS RUN gate is **closed**. H1b primary map stands. Rival remains first-of-window/impulse for diagnostics only. If later evidence reverses this lock → NEW hyp ID.

**Unchanged:** RUN still blocked on tape stream C, event calendar, coverage projection, and recommended residual locks R1/R2/R4.

