# QUANT H001b — Experiment Protocol (DRAFT ONLY · NO RUN)
**Hypothesis ID:** **H001b**  
**Supersedes for decision-readiness:** H001 `QUANT_H001_RTH_ORG_CE_PROTOCOL_2026-09-13.md` (audit only; **do not run H001**)  
**Investigation:** INV-002-methodology-seed · Wave 1  
**Parents (Passed Observed only):** C-METH-008, C-METH-009, C-METH-015  
**CASSANDRA:** `reviews/CASSANDRA_H001_REDTEAM_2026-09-13.md` → HOLD; H001 not decision-ready  
**Author:** QUANT · **Filed:** 2026-09-13  
**Revision class:** Pre-reg revision — **no results peeked**  
**Run status:** **CLEAR TO RUN (exploratory)** on `CONTINUOUS-KAGGLE-NQ1M` after DATA formal gate 2026-09-13 — Pref/Popen locked in `evidence/tape/KAGGLE_NQ_1M_2022_2025/PREF_POPEN_POLICY.md` + `DATA_GATE_KAGGLE_NQ_1M_2026-09-13.md`. Stream C MNQ Mar 2026 still missing for lecture-aligned claims. Coverage projection still required before SURVIVES.

---

## 0. Why H001b

CASSANDRA **CRITICAL:** H001’s FAILS/SURVIVES gate was CE-vs-random-level “specialness,” which is **not** C-METH-009’s verify-don’t-accept product (running frequency of hit-by-10:00).  

H001b restores primary estimand = \(\hat P(\text{hit CE by 10:00})\) + CI. CE-specialness Δ is **secondary**, separately labeled — **never** bare SURVIVES for specialness alone.


---

## 0b. CASSANDRA H001b packaging SURVIVED (2026-09-13)

`reviews/CASSANDRA_H001b_REDTEAM_2026-09-13.md` — design cleared. Optional R1 tick-rounding frozen in §3.0.  
External RUN gates unchanged: stream C + \(P_{ref}\)/\(P_{open}\) META + coverage projection. No MERCURY.

---

## 1. Statement (locked)

On **NASDAQ index futures (1m)**:

- **RTH ORG** = prior day **16:14 ET** final print → **09:30 ET** RTH open (Passed **008**; ASR 9:00 rejected).  
- **CE** = midpoint of that gap.  
- **Primary product (C-METH-009):** estimate \(\hat P(\text{price reaches CE by 10:00 ET})\) with CI on the pre-reg population — **verify, don’t accept**.  

**0.70 is FOIL only** (Passed **009** withdraws it). Never a pass/fail target. Ban prose: “consistent with 70%,” “confirms ~70%,” or bare “H001b SURVIVES” meaning rate confirmation.

C-METH-**015**: 30m opening/dealing range ≠ overnight ORG CE. Results must say: “overnight ORG CE (16:14→09:30), **not** 30m OR midpoint.”

---

## 2. Population / instrument / prints

| Field | Lock |
|-------|------|
| Instrument | **MNQ** prefer (shared stream C) or NQ with scale note — no mix |
| Bar | 1m · America/New_York · DST-aware |
| Tape | Shared INV-001 stream C / WAVE1 — one stack |
| Flat gap | Exclude \|G\| < **0.25** MNQ pts as PARAMETER (1 tick); appendix \(\hat P\) with/without flats |
| Event primary | Non-CPI/FOMC/NFP via INV-001 `EVENT_CALENDAR_CPI_FOMC_NFP.md` |
| Min N (verify product) | **80** non-event RTH days; else INCONCLUSIVE |
| Coverage | Project on ≥20 RTH days before claiming N≥80 reachable |

### 2.1 \(P_{ref}\) — 16:14 policy (DATA co-lock required before RUN)

| Prior-day type | Rule |
|----------------|------|
| Normal RTH | \(P_{ref}\) = **last trade / bar close in 16:14 ET** minute on MNQ 1m (ICT 4:14 p.m. final print) |
| Early close | **Exclude** day \(D\) from primary if prior session is early-close / holiday (no reliable 16:14 RTH analogue) — PARAMETER alternative only with DATA one-pager + ORION ack. **Estimand:** primary \(\hat P\) = **normal-prior-session days only**; report exclusion count in coverage |
| Missing 16:14 bar | Exclude day; count in coverage |
| Not used | Cash 16:00 close; futures settlement; 16:00 bar — unless DATA META explicitly overrides (would be NEW note) |

DATA files policy path in stream C META before coverage projection. Spot-check ≥10 random days: 16:14 exists.

### 2.2 \(P_{open}\) — 09:30 META lock (DATA)

**Primary (pending META freeze):** 09:30 ET minute bar **open**.  
**Sensitivity (mandatory co-report):** first trade timestamped in 09:30 minute if vendor distinguishes.  

If \(\hat P\) decision narrative flips across defs → label **OPEN-PRINT-DEPENDENT**.  
Freeze chosen primary in stream C META field before RUN.

---

## 3. Gap, CE, hit

\(G = P_{open} - P_{ref}\); \(\mathrm{CE} = (P_{ref}+P_{open})/2\).

### 3.0 Tick rounding (CASSANDRA R1 — pre-code LOW)

**Locked:** Before overlap tests, round **both** CE and null level \(U\) to the **nearest 0.25** MNQ point (half-toward-even / banker's optional; default = round half away from 0 to nearest 0.25 grid).  
\(P_{ref}\) / \(P_{open}\) stay as META prints; compute raw CE then round. Do **not** mix raw-float overlap with tick-rounded levels in the same run.

### 3.1 Hit deadline (MEDIUM co-report)

| Rule | Window | Role |
|------|--------|------|
| **Primary** | **[09:30, 10:00] ET inclusive of 10:00 bar** — any bar with `low ≤ CE ≤ high` | As H001; mark **PARAMETER** if ASR “by 10:00” ambiguous |
| **Sensitivity** | **[09:30, 10:00)** — exclude 10:00 bar | Mandatory co-report |

If \(\hat P\) CI conclusions flip → **DEADLINE-DEPENDENT**.

Time-to-CE = first hit bar minutes after 09:30 (misses = NA).

---

## 4. Primary deliverable — VERIFY product (CRITICAL)

**This is the H001b decision object aligned to C-METH-009.**

1. On primary population (non-event, flats excluded, print rules locked):  
   \(\hat P = \frac{1}{N}\sum I(\text{hit CE by deadline})\)  
2. Bootstrap 95% CI (10_000 resamples, day-level).  
3. Time-to-CE distribution on hits.  
4. Plot foil **0.70** as dashed line labeled **FOIL (C-METH-009 withdrawn)** — visual only.  
5. Strata (descriptive): gap tertile × direction; event vs non-event.

### Vocabulary (foil-gravity ban)

| Label | Meaning | Allowed? |
|-------|---------|----------|
| **VERIFY COMPLETE (frequency filed)** | \(\hat P\)+CI+distro filed under frozen protocol; foil plotted | **Yes** — process only. **≠ trade permission / edge** (R3). No MERCURY until separate hyp |
| **SURVIVES (CE-specialness)** | Secondary Δ only (§5) | Yes if §5 gates met — **separate sentence** |
| Bare “H001b SURVIVES” | Ambiguous | **Banned** |
| “Confirms / consistent with 70%” | Foil gravity | **Banned** (fails CASSANDRA prose) |
| “70% verified” | Equating foil to result | **Banned** |

**There is no FAILS vs 0.70.** Distance to 0.70 is never a criterion.

IS/OOS/walk-forward still apply for **stability of \(\hat P\)** reporting (show OOS \(\hat P\) as the cited verify number; IS for plumbing only).

---

## 5. Secondary — CE-specialness (optional; separately labeled)

### 5.1 Null algorithm (fully specified; ≤ geometric bias documentation)

For each eligible day \(d\) with \(a=\min(P_{ref},P_{open})\), \(b=\max(\cdot)\):

1. Draw **one** \(U_d \sim \mathrm{Unif}(a,b)\) with seed `H001b_null_{date}` recorded (one draw per day).  
2. Endpoints **included** in the continuous Unif sense (P(exact endpoint)=0).  
3. On the **same** [09:30, primary deadline] path:  
   \(I_{CE,d} = 1\{\text{path overlaps CE}\}\)  
   \(I_{U,d} = 1\{\text{path overlaps }U_d\}\)  
4. \(\Delta = \mathbb{E}[I_{CE}-I_U]\) estimated by mean over days; bootstrap 10_000 on days.

**Also report fill-depth curve:** for normalized depth \(d \in \{0, 0.25, 0.5, 0.75, 1.0\}\) from open toward ref, touch rate of level \(P_{open} + d(P_{ref}-P_{open})\).  

If curve is monotone decreasing from open, **do not** narrate \(\Delta\le 0\) as “gap CE fails” without stating geometric expectation (levels near open are easier).

### 5.2 Decision label (secondary only)

**SURVIVES (CE-specialness)** iff OOS N≥80: \(\Delta>0\), CI entirely above 0, walk-forward median \(\Delta>0\).  
**FAILS (CE-specialness)** iff Δ≤0 or CI includes ≤0.  

Never promote specialness survival as verify-of-70% or as the sole H001b headline.

---

## 6. Conditionals (MEDIUM multiplicity control)

**Optional** secondary model: logistic \(I_{hit} \sim\) gap size + direction + event flag.  

| Lock | Value |
|------|-------|
| Single OOS score | **Brier score** only (not log-loss cherry-pick) |
| Features | Frozen list above **before** any fit |
| H002 7–9 class join | **NEW hyp** or H001b amend with ORION ack **before peek** — not silent add |

Conditional “lift” may be reported; it is **not** the primary verify product.

---

## 7. Bias hunt

- [x] Primary = \(\hat P\)+CI verify product (not specialness)  
- [x] Tick rounding: CE and U to nearest 0.25 before overlap (R1)  
- [x] 0.70 FOIL; foil-gravity prose banned  
- [x] Null algorithm specified + fill-depth curve  
- [ ] DATA \(P_{ref}\) 16:14 early-close/holiday policy filed  
- [ ] DATA \(P_{open}\) META lock  
- [x] 10:00 inclusivity co-report  
- [x] Single Brier score for conditionals  
- [x] No 30m OR-mid conflation  
- [x] No INV-001 lunch  

---

## 8. RUN blockers

1. Shared stream C / WAVE1 tape  
2. Coverage projection ≥20 RTH days  
3. DATA \(P_{ref}\) / \(P_{open}\) META locks  
4. CASSANDRA re-clear H001b if ORION queues  
5. H003–H004–H002 remain draft until H001b clears packaging  

**No MERCURY/RISK.** Standing ban (R3): **VERIFY COMPLETE ≠ trade permission** — filing \(\hat P\) is not scientific endorsement of an edge.


---

## 9. Paths

- This file: `experiments/QUANT_H001b_RTH_ORG_CE_PROTOCOL_2026-09-13.md`  
- Prior: `experiments/QUANT_H001_RTH_ORG_CE_PROTOCOL_2026-09-13.md`  
- Red team: `reviews/CASSANDRA_H001_REDTEAM_2026-09-13.md`
