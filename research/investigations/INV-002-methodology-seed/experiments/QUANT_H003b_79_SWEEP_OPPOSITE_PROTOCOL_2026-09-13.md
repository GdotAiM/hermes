# QUANT H003b — Experiment Protocol (DRAFT ONLY · NO RUN)
**Hypothesis ID:** **H003b**  
**Supersedes for packaging:** H003 `QUANT_H003_79_SWEEP_OPPOSITE_PROTOCOL_2026-09-13.md` (do not run H003)  
**Investigation:** INV-002 · Wave 1  
**Parents (Passed Observed only):** C-METH-003, C-METH-004, C-METH-006  
**CASSANDRA:** `reviews/CASSANDRA_H003_REDTEAM_2026-09-13.md` + `reviews/CASSANDRA_H003_RECONTROL_2026-09-13.md` → HOLD; H003b adopts **Foil A**  
**Author:** QUANT · **Filed:** 2026-09-13  
**Revision class:** Pre-reg — **no peek**  
**Run status:** Packaging **SURVIVED** as **Rival B** only (`CASSANDRA_H003b_REDTEAM`). **Not lecture confirmation.** Lecture primary = **H003c**. SELECTION-DEPENDENT + mandatory tertile match in §0e/§5. No run.

---

## 0. Why H003b

CASSANDRA CRITICAL: H003’s control cell forked incompatible designs; no-sweep “both extremes” baseline is structurally ≈0; random-side-on-sweep-days sanity is ill-posed (Attack 3).  

H003b locks **one** primary control (CASSANDRA-recommended family), kills invalid baselines, adds range strata / single horizon / hygiene parity with H001b.


---

## 0b. ORION STOP ack (2026-09-13)

ORION STOP requirements mapped:

1. **CRITICAL:** Single primary = §4.1 random-side-at-09:30 on **all** eligible range days; no-sweep \(P(	ext{both})\) **banned** as falsification baseline. Paired order foil on days touching ≥1 extreme = §4.3 (fully specified co-report; ORION “and/or”).  
2. **HIGH:** Sweep-day random-side sanity **killed**; \(R_{79}\) width tertiles + RANGE-DEPENDENT; primary horizon **12:00 only**; ATLAS equal-lows vs HH/LL **waits** before RUN.


---

## 0c. RECONTROL ack — Foil A locked (2026-09-13)

`CASSANDRA_H003_RECONTROL_2026-09-13.md` killed paired random-side **on first-sweep days** (auto-hit bias).  
H003b §4.1 = **Foil A** with explicit time origin 09:30 and no auto-credit of swept extreme unless it is opposite(\(S\)). Horizon §5 = 12:00 only; range tertiles + RANGE-DEPENDENT already in §5.


---

## 0d. ATLAS box lock → H003c (2026-09-13)

`evidence/L81eMQhmXmc/H003_BOX_LOCK.md`: demo primary = REL/REH sweep → opposite beige HH/LL.  
Full range-extreme sweep (this file’s treatment) = **Rival B**. New hyp **H003c** filed; this file retained as rival packaging / Foil A donor. No peek/run.


---

## 0e. CASSANDRA H003b packaging SURVIVED (2026-09-13) — rival map only

`reviews/CASSANDRA_H003b_REDTEAM_2026-09-13.md` — Foil A control cleared.  
**ORION / ATLAS:** H003b treatment (sweep \(H_{79}/L_{79}\)) is **Rival B**, not lecture demo.  
**Do not narrate H003b SURVIVES as lecture confirmation.** Lecture-faithful primary = **H003c** (REL/REH → opposite HH/LL).

**SELECTION-DEPENDENT (HIGH residual):** before any rival-map SURVIVES claim, recompute Δ with control universe = days touching ≥1 of \(\{H_{79},L_{79}\}\) by \(T^*\) (same Foil A random-side rule). If only the full eligible-universe Δ works → label **SELECTION-DEPENDENT** — do not claim even rival-map confirmation without that label. Tertile match/reweight of control to treatment \(R_{79}\) bins is **mandatory** (not optional).

---

## 1. Statement

Given **07:00–09:00 ET** HH/LL (003/004), if after **09:30** one boundary is swept first, \(P(\text{reach opposite boundary by primary horizon})\) exceeds the pre-registered control rate (§4).  

Passed **006:** bread-and-butter = one-side 7–9 sweep → opposite end.  

**MAE/MFE = descriptive only.** Any entry/stop/target = **NEW hyp**. **No MERCURY.** SURVIVES ≠ trade permission.

---

## 2. Population / instrument

| Field | Lock |
|-------|------|
| Instrument | MNQ prefer (stream C) / NQ documented · 1m · America/New_York |
| Days | Ex Sundays (003); ETH 07:00–09:00 + RTH through horizon |
| Events | Non-CPI/FOMC/NFP primary — INV-001 `EVENT_CALENDAR_CPI_FOMC_NFP.md` |
| Min N | **80** treatment days with defined first sweep; else INCONCLUSIVE |
| Coverage | ≥20 RTH days projection before claiming N≥80 |
| Tape | Shared stream C / WAVE1 |

---

## 3. Definitions

### 3.1 7–9 range

\(W = [07:00, 09:00)\) ET primary (**PARAMETER**; co-report inclusive \([07:00, 09:00]\) — Attack 8).  

\(H_{79}, L_{79}\) = max high / min low in \(W\).  
Exclude if \(R_{79}=H_{79}-L_{79} < 2\) MNQ pts (PARAMETER).

**ATLAS gate (Attack 6):** Before RUN, ATLAS notes whether demo “relative-equal lows” ≠ range LL. If distinct → equal-lows primary becomes **NEW hyp** or H003c; until then primary = **full range extreme** with rival note “equal-lows TBD.”

### 3.2 First sweep (treatment)

Primary horizon **\(T^\* = 12:00\) ET only** for FAILS/SURVIVES (Attack 5).  
10:00 / 11:00 = descriptive only — cannot flip SURVIVES.

After 09:30 until \(T^\*\):

- Sweep high first: first `high ≥ H_{79}` before any `low ≤ L_{79}`  
- Sweep low first: mirror  
- Same-bar dual sweep: **exclude** from treatment  
- Neither: not in treatment sample (coverage)

**Primary sweep def = touch (0 buffer).**  
Mandatory co-report: pierce = `high ≥ H_{79} + 0.25` (1 tick) or +2 pts — if decision flips → **SWEEP-DEF-DEPENDENT**.

### 3.3 Success (treatment)

After \(\tau_s\), overlap opposite extreme by \(T^\*\).

---

## 4. Primary control — SINGLE LOCK (CRITICAL fix)

### 4.1 PRIMARY null = RECONTROL **Foil A** (≤15 lines)

**Chosen foil:** Random side at **09:30** on **all eligible 7–9 range days** (not only first-sweep days).  
Foil B (order) / Foil C (level) = §4.3 co-report only — **not** primary.

```
1. Eligible day d: valid R79 (same §2 exclusions). NOT conditioned on a sweep.
2. At 09:30 ET (before any RTH sweep clock): draw S_d ∈ {high, low} with p=1/2.
   Seed: H003b_A_{YYYYMMDD}. Time origin for control = 09:30, NOT τ_s.
3. I_ctrl,d = 1 iff opposite(S_d) is touched on [09:30, T*=12:00]
   (touch: high≥H79 or low≤L79 as applicable).
4. Realized sweep extreme CAN satisfy control only if it is the opposite of S_d
   (i.e. if S_d=high, need L79; sweeping H79 alone does NOT auto-credit I_ctrl).
5. Treatment (separate sample): days with actual first sweep; I_treat=1 iff
   opposite of actual first sweep touched on (τ_s, T*].
6. Δ = P̂_treat − P̂_ctrl; bootstrap 10_000 resampling days in each pool;
   report N_treat, N_ctrl; match/report within R79 tertiles.
```

**Worked example (swept-high day):** Actual first sweep = high at 10:12.  
- Treatment: success iff \(L_{79}\) touched by 12:00 after 10:12.  
- If \(S=\) high: \(I_{ctrl}=1\) iff \(L_{79}\) touched in [09:30,12:00] (same economic opposite; **not** auto from the high sweep).  
- If \(S=\) low: \(I_{ctrl}=1\) iff \(H_{79}\) touched in [09:30,12:00] — the 10:12 high sweep **can** credit this, but only because opposite-of-low = high; that is intentional for Foil A on all-days universe, not the broken “random after \(\tau_s\)” null.  
- Broken null (REJECTED): random side drawn as-if at \(\tau_s\) on sweep-only days → when \(S\neq\) actual, opposite = already-swept extreme → auto-hit → \(\mathbb{E}[\Delta]\le 0\).

### 4.2 Killed / demoted controls

| Control | Status |
|---------|--------|
| No-sweep days \(P(\text{both extremes})\) | **KILLED** as Δ baseline — structurally ≈0 (Attack 2). Coverage diagnostic only, label **INVALID as Δ baseline** |
| Random-side on sweep days “≈0.5 sanity” | **KILLED** — ill-posed (Attack 3) |
| 30m OR first sweep | Descriptive only — different object (015) |

### 4.3 Paired order foil (ORION “and/or” — co-report; not sole SURVIVES path)

**Universe:** days that touch **≥1** of \(\{H_{79},L_{79}\}\) by \(T^\*\).

1. Let \(E_1\) = chronologically first extreme touched; \(E_2\) = the other.  
2. \(I_{treat} = 1\) if \(E_2\) is also touched by \(T^\*\) after first touch of \(E_1\).  
3. **Control (paired):** draw \(S \in \{H_{79},L_{79}\}\) with p=1/2 (seed `H003b_pair_{date}`). \(I_{ctrl} = 1\) if the opposite of \(S\) is touched by \(T^\*\) (same path; does **not** reuse “first sweep then randomize” after \(	au_s\)).  
4. Report paired \(\Delta_{pair} = \mathbb{E}[I_{treat}-I_{ctrl}]\) with bootstrap — **descriptive / co-report**.  

Lecture **SURVIVES** still requires §4.1 primary Δ gates (§5). Promoting §4.3 to sole primary needs ORION ack (still pre-peek OK).

---

## 5. Falsification

**Falsification horizon = 12:00 ET only**; 10:00/11:00 descriptive — cannot flip SURVIVES.

**FAILS** if OOS \(N_{treat}≥80\): Δ≤0 or 95% CI includes ≤0 (primary control §4.1, horizon \(T^\*=12:00\), touch sweep).  

**SURVIVES (Rival B — HH/LL sweep map only)** — **never lecture confirmation** (use H003c):

1. OOS Δ>0 and CI entirely above 0 (Foil A)  
2. Walk-forward median Δ>0  
3. **SELECTION-DEPENDENT gate:** Δ also >0 with CI>0 when control universe = days touching ≥1 of \(\{H_{79},L_{79}\}\) by \(T^*\) (same Foil A). Else label **SELECTION-DEPENDENT**  
4. **Tertile match mandatory** before citing Δ  
5. **RANGE-DEPENDENT gate:** mid \(R_{79}\) tertile Δ>0 with CI>0 — else **RANGE-DEPENDENT**  
6. SURVIVES ≠ MERCURY permission; ≠ lecture confirmation  

**INCONCLUSIVE:** N<80, tape/coverage fail, or ATLAS equal-lows unresolved when demo requires it.

IS 60% / OOS 40% time-ordered; walk-forward step 20 days.

---

## 6. Metrics

\(N_{treat}\), \(N_{ctrl}\), \(P_{treat}\), \(P_{ctrl}\), Δ, CI; tertile Δ; time-to-target / MAE / MFE **descriptive**; pierce sensitivity; window inclusivity sensitivity; coverage (no-sweep rate, dual-sweep excludes).

---

## 7. Bias hunt

- [x] Single primary control; no-sweep both-extremes killed  
- [x] Random-side-on-sweep sanity killed  
- [x] Primary horizon 12:00 only  
- [x] Range tertiles + RANGE-DEPENDENT  
- [ ] ATLAS equal-lows vs HH/LL before RUN  
- [x] Pierce co-report  
- [x] MAE/MFE non-trade  
- [x] Event calendar cite  
- [x] No lunch import  

---

## 8. RUN blockers

1. CASSANDRA re-review H003b packaging  
2. ATLAS equal-lows note  
3. Shared stream C + coverage projection  
4. No MERCURY/RISK  

---

## 9. Paths

- This: `experiments/QUANT_H003b_79_SWEEP_OPPOSITE_PROTOCOL_2026-09-13.md`  
- Prior: `experiments/QUANT_H003_79_SWEEP_OPPOSITE_PROTOCOL_2026-09-13.md`  
- Red team: `reviews/CASSANDRA_H003_REDTEAM_2026-09-13.md`
