# QUANT H009 — Weekly DOL / nearest PW–PM (DRAFT ONLY · NO RUN)
**Hypothesis ID:** H009  
**Wave 2** · ORION rank #1  
**Parents (ATLAS, pending DATA Pass):** **C-METH-022, 023, 025** (Hold/ASR)  
**Tape:** `evidence/tape/FREE_YF_NQ/` — NQ=F **1wk + 1d** only  
**Filed:** 2026-09-13 · QUANT (revised for nearest PW/PM)  
**Run status:** **SUPERSEDED by H009b** — do not run. See `QUANT_H009b_NEAREST_PWPM_PROTOCOL_2026-09-13.md`  

---

## 0. Scope

- FREE_YF weekly/daily only. **No Wave 1** on this tape.  
- Continuous **NQ=F** rolls → label **CONTINUOUS-YF**.  
- Parents not yet DATA-Passed — cite as **Hold/ASR**; mechanics below implement 022’s nearest-side idea on free bars.

---

## 1. Statement (from 022 / 023 / 025)

At the **new-week open** (Sunday open / Friday-close notepad — 023), frame DOL as a **nearest-side** question among:

\(\{PWH, PWL, PMH, PML\}\)

(previous-week high/low, previous-month high/low — 022).  

**Predicted draw** = the extreme with **shortest distance** from the week-open reference price (path of least resistance).  

Transpose those levels to daily (025); unused opposite-side levels can be ignored when not the draw.

**Test:** After the week opens, does price **touch the predicted extreme first** (daily path) more often than a **random choice** among the four (or among the two week extremes only — sensitivity)?  

**Falsify:** no lift vs random after OOS weeks.

---

## 2. Population / instrument

| Field | Lock |
|-------|------|
| Instrument | NQ=F continuous (Yahoo) |
| Weekly | `NQ=F_1wk.csv` for PW extremes |
| Daily | `NQ=F_1d.csv` for PM extremes + within-week path |
| Week-open reference | **PARAMETER:** first daily bar open of the new week (Mon RTH open proxy). Sunday Globex open **not** on daily FREE_YF — label **RTH-MON-PROXY** vs lecture Sunday open |
| Month | Calendar month: PMH/PML = prior calendar month high/low from daily bars |
| Min N | 80 OOS weeks with unique first-touch among candidates |
| Exclude | Incomplete current week; weeks missing prior week or prior month history |

---

## 3. Nearest-side picker (022)

At week-open reference price \(P_0\):

1. Build set \(L = \{PWH, PWL, PMH, PML\}\) (finite floats from prior completed week/month).  
2. Predicted level \(L^\* = \arg\min_{x \in L} |x - P_0|\) (ties: prefer **weekly** over monthly — PARAMETER; co-report random tie-break).  
3. **Drop unused opposites (025):** for reporting, mark non-predicted week/month extremes as “not the draw” — does not change \(L^\*\) definition.

---

## 4. Outcome (daily path inside week W)

- Touch of level \(x\): some daily bar in \(W\) with High≥x (if x is a high) or Low≤x (if x is a low).  
- **First touch** among the four: earliest date a member of \(L\) is touched; same-day multi-touch → exclude from first-touch accuracy (coverage) or Open-distance PARAMETER tie (descriptive).  
- Success: first uniquely touched member equals \(L^\*\).

---

## 5. Foil

Random draw \(U \sim\) uniform on \(L\); success if first touch equals \(U\).  
On unique-first weeks, \(E[\text{acc}_{rand}]=0.25\) for four-way; also report two-way foil (random among {PWH,PWL} only) as sensitivity.

**Δ:** \(\mathrm{acc}_{nearest} - \mathrm{acc}_{rand}\) (or vs 0.25).

---

## 6. Falsification

**FAILS** if OOS N≥80: nearest accuracy ≤ random (CI for Δ includes ≤0), or nearest accuracy CI includes ≤0.25 in four-way design.  
**SURVIVES (nearest PW/PM on CONTINUOUS-YF)** if Δ>0 with CI>0 and walk-forward median Δ>0 — prose must note **Hold parents pending DATA Pass**, **Mon-open proxy**, continuous rolls.  

**Ban:** Wave 1 / 1m claims; claiming Sunday-open identity on daily tape.

IS/OOS 60/40 weeks; walk-forward step 10 weeks.

---

## 7. Blockers

DATA Pass on 022/023/025; DATA FREE_YF gate; CASSANDRA packaging (esp. Mon proxy + four-way foil). No MERCURY.

## 8. Path

`experiments/wave2/QUANT_H009_WEEKLY_DOL_PROTOCOL_2026-09-13.md`
