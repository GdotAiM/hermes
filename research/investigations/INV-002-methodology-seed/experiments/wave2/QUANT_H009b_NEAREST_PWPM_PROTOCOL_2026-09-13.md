# QUANT H009b — Nearest-side PW/PM weekly extreme (DRAFT ONLY · NO RUN)
**Hypothesis ID:** **H009b**  
**Supersedes:** H009 `QUANT_H009_WEEKLY_DOL_PROTOCOL_2026-09-13.md` (do not run; bull/bear picker wrong object)  
**Wave 2** · ORION rank #1  
**Parents:** C-METH-**022, 023, 025** — **Passed Observed** (DATA Wave 2 gate 2026-09-13)  
**CASSANDRA:** packaging **SURVIVED** (`reviews/wave2/CASSANDRA_H009b_REDTEAM_2026-09-13.md`)  
**Tape:** FREE_YF_NQ — NQ=F **1wk + 1d**  
**Filed:** 2026-09-13 · QUANT · **Amended:** L4 primary + SURVIVES prose · **no peek/run** — FREE_YF gate remaining  

---

## 0. Why H009b

CASSANDRA CRITICAL: H009’s bull/bear prior-week close picker ≠ ATLAS/ORION **nearest-side** DOL (022).  

H009b primary = **distance at week open** from \(P_0\) to prior-week / prior-month extremes. Bull/bear opposite-extreme = **Rival only**.  

**Allowed SURVIVES prose:** nearest-side DOL (**Passed 022**) on CONTINUOUS-YF with explicit open-proxy labels.  
**Banned:** claiming Sunday Globex-open identity on daily Yahoo bars; Wave 1 / 1m claims; bull/bear as “DOL.”


---

## 0b. DATA Pass (2026-09-13)

C-METH-022 / 023 / 025 are **Passed Observed**.  

**Observed object (022):** at Sunday open, nearest of previous-week / previous-month high vs low = path of least resistance / DOL.  
**023:** weekly notepad map at Friday close / Saturday.  
**025:** transpose PW/PM to daily; drop unused opposite side.

H009b primary picker implements that **nearest-side** structure. Remaining PARAMETERs are **tape proxies only** (Mon Open / Fri close for Sunday Globex open; Yahoo week index; continuous NQ=F) — not the DOL rule itself.


---

## 0c. CASSANDRA H009b packaging SURVIVED (2026-09-13)

Nearest-side clears H009 CRITICAL. Residuals locked here:

1. Parents **Passed** 022/023/025.  
2. **Primary candidate set = L4** \(\{PWH,PWL,PMH,PML\}\) for 022 fidelity; **two-way** \(\{PWH,PWL\}\) = sensitivity only.  
3. SURVIVES label: **Observed nearest-side (022) · PARAMETER Mon-open proxy · CONTINUOUS-YF** — ban Sunday-open identity.  
4. Still **no RUN** without FREE_YF DATA gate.


---

## 0d. R2 locked — Option A (2026-09-13)

CASSANDRA CONFIRM residual R2: **Option A chosen** (already in §1/§3/§6).  

- **Primary = L4** `{PWH, PWL, PMH, PML}` — full 022 nearest-of-four  
- **Two-way** `{PWH, PWL}` = sensitivity only — **not** full-022 SURVIVES alone  
- SURVIVES prose may cite full Passed 022 nearest-side (with PARAMETER Mon-open proxy)

---

## 1. Statement (Passed Observed — nearest-side DOL)

At new-week open (**022** Sunday-open framing; FREE_YF uses **PARAMETER** Mon Open / Fri-close proxies), among  

\(L_4 \in \{PWH, PWL, PMH, PML\}\) (**primary** — week **and** month per 022),  

**predict** the extreme with **shortest distance** from week-open reference \(P_0\).  

Two-way \(L=\{PWH,PWL\}\) = **sensitivity only** (week-subset).  

Success = that extreme is the **first uniquely touched** level in the week’s daily path.  

Compare accuracy vs **random** among the same candidate set.

---

## 2. Population / instrument

| Field | Lock |
|-------|------|
| Instrument | NQ=F continuous (Yahoo) — **CONTINUOUS-YF** |
| Weekly / daily | `NQ=F_1wk.csv` / `NQ=F_1d.csv` |
| \(P_0\) primary | **First daily Open of week \(W\)** (Mon RTH proxy) — **PARAMETER** |
| \(P_0\) co-report | Prior **Friday close** — mandatory sensitivity; flip → **ANCHOR-DEPENDENT** |
| PWH/PWL | Prior Yahoo week High/Low |
| PMH/PML | Prior calendar month High/Low from daily |
| Week membership | Yahoo week index + daily dates in \(W\) — document in run memo |
| Roll weeks | Flag/exclude as co-report; flip → **ROLL-DEPENDENT** |
| Min N | 80 OOS **unique-first** weeks; else INCONCLUSIVE |
| Coverage | Report % eligible weeks excluded (no unique first / incomplete); if unique-first <50% of eligible → external-validity flag |
| Events | Primary = all weeks; co-report non-event (INV-001 calendar); flip → **EVENT-SENSITIVE** |

**Sunday open (022):** not on daily FREE_YF — Mon Open / Fri close are proxies only.

---

## 3. Primary picker — nearest-side (≤15 lines)

```
1. Build L4 = {PWH, PWL, PMH, PML}              # PRIMARY (022 fidelity)
   L2 = {PWH, PWL}                              # sensitivity only
2. P0 = first daily Open in week W              # PARAMETER Mon-open proxy
3. L* = argmin_{x in L4} |P0 - x|               # nearest-side
   Ties: exclude OR PARAMETER coin-flip; prefer weekly over monthly if both tied
4. Foil: U ~ uniform on L4; seed H009b_{YYYYWW}
5. Success: first unique touch in W among L4 equals L* (or U for foil)
6. Δ = acc_nearest - acc_random                 # E[acc_rand]=0.25 on L4
7. Sensitivity: repeat steps 3–6 on L2 only     # E[acc_rand]=0.5; not lecture SURVIVES alone
```

**Clean estimand:** among weeks with a **unique** first touch of **L4**, does nearest-side beat random?

---

## 4. Rival only (not primary SURVIVES)

| Rival | Rule |
|-------|------|
| **Bull/bear opposite-extreme** (old H009 §4) | Prior week \(C>O\) → predict PWL; else PWH |  
| Unif gap-level “delivery exists” | Descriptive VERIFY only — not SURVIVES |

Rival Δ cannot sole-grant “weekly DOL” SURVIVES.

---

## 5. Outcomes / metrics

- First unique touch among candidate set (daily High/Low vs level)  
- Same-day dual touch of both week extremes → **exclude** from first-touch accuracy (coverage)  
- Touch-either / touch-both by week end = **descriptive** only  
- Time-to-first (days) descriptive  

---

## 6. Falsification

**FAILS** if OOS N≥80 unique-first weeks on **L4**: Δ≤0 or bootstrap 95% CI for Δ includes ≤0  
(equivalently nearest accuracy CI includes ≤0.25).  

**SURVIVES label (locked):** **Observed nearest-side (022) · PARAMETER Mon-open proxy · CONTINUOUS-YF**  

Requires Δ>0, CI>0, walk-forward median Δ>0 on **L4**. Cite Passed 022/023/025.  
**Ban:** Sunday-open identity on daily Yahoo; Wave 1 claims; two-way-only as full 022 SURVIVES; bull/bear as DOL.  

If future Observed refinement of Sunday-open / month inclusion ≠ frozen proxies → **NEW hyp id** for the proxy change; nearest-side core stays 022.

IS/OOS 60/40 weeks; walk-forward step 10 weeks.

---

## 7. Prose ban table

| Allowed | Banned |
|---------|--------|
| **Observed nearest-side (022)** · PARAMETER Mon-open · CONTINUOUS-YF | Sunday-open identity; two-way as full 022; bull/bear as DOL |
| CONTINUOUS-YF / Mon-open / Fri-close **proxy** labels | Sunday Globex-open identity on daily Yahoo |
| Drop unused opposite (025) | Wave 1 / MNQ 1m claims from FREE_YF |
| Rival bull/bear labeled rival | Bare “H009 SURVIVED” for wrong object |

---

## 8. Blockers

1. ~~DATA Pass 022/023/025~~ — **DONE**  
2. ~~CASSANDRA packaging~~ — **SURVIVED** (`CASSANDRA_H009b_REDTEAM`)  
3. **FREE_YF DATA gate** — still required before RUN  
4. No MERCURY · No Wave 1 on FREE_YF · No peek  

## 9. Paths

- This: `experiments/wave2/QUANT_H009b_NEAREST_PWPM_PROTOCOL_2026-09-13.md`  
- Prior: `experiments/wave2/QUANT_H009_WEEKLY_DOL_PROTOCOL_2026-09-13.md`  
- Red team: `reviews/wave2/CASSANDRA_H009_REDTEAM_2026-09-13.md`  
- Re-review SURVIVED: `reviews/wave2/CASSANDRA_H009b_REDTEAM_2026-09-13.md`

---

## 0e. Pre-powered re-run freeze (ORION/CASSANDRA 2026-09-13)

**Pilot decision stands: INCONCLUSIVE** (`experiments/wave2/results/H009b_PILOT_RESULTS_2026-09-13.md`). Do **not** claim SURVIVES.

### Prior-week HH/LL source — PARAMETER (freeze ONE before powered re-run)

| Lock | Value |
|------|--------|
| **Frozen primary source** | **Daily-aggregated ISO-week** HH/LL from `NQ=F_1d.csv` (max High / min Low of days in prior ISO week) |
| Rival / unused for primary | `NQ=F_1wk.csv` Yahoo weekly bars — **not** primary until a NEW hyp id or ORION ack switches freeze |
| Rationale | Pilot used daily aggregation; must not silently switch to weekly file between runs |

### Foil OOS audit (CASSANDRA)

Pilot OOS foil hit rate ≈ **0.36** vs naive E\[foil\]=**0.25** under uniform 4-way random on unique-first weeks. With OOS N=22, binomial SE ≈ √(0.25·0.75/22)≈0.092 — 0.36 is within ~1.2 SE of 0.25; **not** evidence of foil bug by itself. Still: before powered re-run, re-check foil RNG (one draw per week, seed recorded) and report foil rate vs 0.25 on IS and OOS separately.

### Powered re-run gate

Re-run only when path to **OOS N≥80** unique-first weeks exists (longer FREE_YF history and/or denser HTF). Until then: no powered re-run; INCONCLUSIVE stands.

