# QUANT H003c — Experiment Protocol (DRAFT ONLY · NO RUN)
**Hypothesis ID:** **H003c** (**NEW** hyp id per ATLAS box lock + H003b §3.1)  
**Investigation:** INV-002 · Wave 1  
**Parents (Passed Observed only):** C-METH-003, C-METH-004, C-METH-006  
**ATLAS lock:** `evidence/L81eMQhmXmc/H003_BOX_LOCK.md`  
**Prior packaging:** H003 / H003b (range-extreme sweep) → **RIVAL B** here — not demo primary  
**Author:** QUANT · **Filed:** 2026-09-13  
**Peek/run:** **none** · Packaging **SURVIVED**. §3.2 detector = **PARAMETER** (`H003c_REL_DETECTOR_LOCK.md`; `reviews/CASSANDRA_H003c_DETECTOR_PARAMETER_2026-09-13.md`). No red-line identity. No run.  
**No MERCURY**

---

## 0. Why H003c (NEW id)

ATLAS demo lock: bread-and-butter = sweep **7–9 REL** (red) after 09:30 → aim **opposite 7–9 range extreme** (beige HH/LL box).  

Full HH/LL sweep as treatment = **RIVAL B** (he does not sweep the box edge in the demo).  
Collapsing REL into HH/LL when they coincide still logs both series.

H003b’s Foil A control hygiene is **imported**; treatment object changes → **NEW hyp id** (not silent amend of H003b).


---

## 0f. ATLAS REL detector lock (2026-09-13)

`evidence/L81eMQhmXmc/H003c_REL_DETECTOR_LOCK.md`:

- §3.2 fractal + τ_eq=2.0 = **PARAMETER, not lecture-locked**. Do not write "matches the red line."
- 1-tick spot-check = **FAIL / blocked** until demo-session 1m tape exists; then pass only if |L_rel − L_red| ≤ 0.25.
- Rival selection: **human mid-box pair** (student-obvious); co-report.
- Rival τ ∈ {4, 8} pts (visual REL band); 1.0/2.0 = tight maps.
- **Ban:** narrating SURVIVES as confirming his exact red-line rule.

---

## 1. Statement

On MNQ/NQ 1m: inside **07:00–09:00 ET**, identify **REL/REH** pools and the **beige range** \(H_{79},L_{79}\). After **09:30**, if price **sweeps a 7–9 REL (or REH)** first, then \(P(\text{reach opposite 7–9 range extreme by }T^*=12:00)\) exceeds Foil A control rate (§5).

MAE/MFE descriptive only. SURVIVES ≠ trade permission.

---

## 2. Population / instrument

Same as H003b: MNQ prefer · 1m · America/New_York · ex Sundays · non-event primary (INV-001 calendar) · shared stream C · \(N_{treat}≥80\) · coverage projection ≥20 RTH days.

---

## 3. Two liquidity objects (do not collapse)

### 3.1 Beige range (target object)

\(W=[07:00,09:00)\) ET (PARAMETER; co-report inclusive).  
\(H_{79}, L_{79}\) = HH/LL in \(W\). Exclude if \(R_{79}<2\) pts.

### 3.2 REL / REH (sweep object) — **PARAMETER detector** (not lecture-locked)

**ATLAS:** `H003c_REL_DETECTOR_LOCK.md` — red line is a **visual pair of swing lows**, not a stated 1-bar fractal + 2.0-pt rule.  
Do **not** claim this detector “matches the red line.” Label every numeric rule below **PARAMETER / QUANT choice**.

Inside \(W\), fractal swing (**PARAMETER** — ATLAS-unspecified):  
- Swing low at i: `low[i]<low[i-1]` and `low[i]<low[i+1]` (completed).  
- Swing high: mirror.

**Equal tolerance (primary map):** \(\tau_{eq} = 2.0\) MNQ/NQ pts — **PARAMETER**, not Observed.  
**Rival τ (mandatory co-report):** \(\tau_{eq} \in \{4.0, 8.0\}\) (visual REL band). Tight rivals 1.0 descriptive only after OOS.  
If tape shows \(\tau_{eq}=2.0\) misses the lecture pair → retune **pre-peek** (ORION ack) or NEW id.

**REL cluster:** any pair of distinct swing lows with \(|\ell_a-\ell_b|≤\tau_{eq}\).  
**\(L_{rel}\) construction (PARAMETER):** mean(\(\ell_a,\ell_b\)) rounded to 0.25.  
Rival construction (descriptive): line at the **higher** of the two lows (resting liquidity — ATLAS note).

**Multiple pairs — primary selection (PARAMETER):** pair whose mean is **closest to mid-range** \((H_{79}+L_{79})/2\).  
**Rival selection (mandatory co-report):** **human mid-box pair** — the two swing lows a student would annotate as “relatively equal” (ATLAS 00:09:20); not lowest-mean. Cannot flip SURVIVES alone.  
Lowest-mean pair = additional descriptive rival only.

**REH:** mirror (unchecked on demo — no REH drawn). Same PARAMETER labels.

**No REL and no REH in \(W\):** no H003c treatment (coverage).

If \(L_{rel}\) within 0.25 of \(L_{79}\) (or REH≈\(H_{79}\)): maps coincide — still dual-log.

**1-tick demo spot-check:** **OPEN / FAIL until stream C** covers the exact demo session. Then compute \(L_{rel}\) and require \(|L_{rel}-L_{red}|≤0.25\). Visual axis read is approximate only (~21,020 on ATLAS lock frame — not a pass).

### 3.3 Primary treatment (DEMO / ATLAS PRIMARY)

After 09:30 until \(T^*=12:00\):

1. Detect first sweep among:  
   - REL sweep: `low ≤ L_{rel}` (touch primary; pierce `low ≤ L_{rel}-0.25` co-report)  
   - REH sweep: `high ≥ H_{reh}`  
2. If REL swept first → target = **\(H_{79}\)** (opposite **range** high).  
3. If REH swept first → target = **\(L_{79}\)**.  
4. If range HH/LL swept **before** any REL/REH: **not** primary treatment (may enter Rival B only).  
5. Dual same-bar: exclude.

\(\tau_s\) = first REL/REH sweep time.  
**Success:** after \(\tau_s\), path overlaps target range extreme by \(T^*\).

### 3.4 Rival maps (report; not primary SURVIVES)

| Rival | Sweep object | Target | ATLAS |
|-------|--------------|--------|-------|
| **B (ex-H003b)** | First touch of \(H_{79}\) or \(L_{79}\) | Opposite range extreme | He does **not** sweep box edge in demo |
| **A** | Sweep REL → aim REH (ignore HH/LL if differ) | REH | He does **not** aim REH in demo |

Rival Δ uses same Foil A control family where applicable; cannot grant lecture SURVIVES alone.

---

## 4. Primary control — Foil A (imported; adapted labels)

Same **RECONTROL Foil A** as H003b §4.1:

```
1. Eligible day: valid beige range (not conditioned on REL/REH sweep).
2. At 09:30 draw S ∈ {range_high, range_low} p=1/2; seed H003c_A_{date}.
3. I_ctrl = 1 iff opposite range extreme of S touched on [09:30, 12:00].
4. Swept REL does NOT auto-credit I_ctrl unless that event also touches opposite(S)
   as a range extreme touch (REL mid-box sweep ≠ auto range-high credit).
5. Treatment sample: days with primary REL/REH sweep; I_treat as §3.3.
6. Δ = P̂_treat − P̂_ctrl; bootstrap; N_treat, N_ctrl; R79 tertiles.
```

No-sweep \(P(\text{both extremes})\) **banned**. Sweep-day random-side sanity **banned**.

---

## 5. Falsification

**Horizon:** **12:00 ET only** (10:00/11:00 descriptive).

**FAILS** if OOS \(N_{treat}≥80\): Δ≤0 or CI includes ≤0 (primary REL/REH→range map + Foil A).  

**SURVIVES (PARAMETER REL/REH detector → opposite range extreme)** only if:

1. Δ>0, CI>0, walk-forward median Δ>0  
2. **SELECTION-DEPENDENT gate:** recompute Δ with control universe = days touching ≥1 of \(\{H_{79},L_{79}\}\) by \(T^*\) (same Foil A). If only full-eligible-universe Δ works → **SELECTION-DEPENDENT** — do not claim lecture SURVIVES.
3. **Tertile match mandatory** (control reweight/match to treatment \(R_{79}\) bins).
4. **RANGE-DEPENDENT gate:** mid \(R_{79}\) tertile also Δ>0 with CI>0 (else RANGE-DEPENDENT, not lecture confirmation)  
3. Pierce co-report does not flip without **SWEEP-DEF-DEPENDENT** label  
4. Prose cites ATLAS lock; does not claim HH/LL-sweep map  

**INCONCLUSIVE:** N<80 / tape / coverage / no REL-REH days.

IS/OOS 60/40; walk-forward step 20.

---

## 6. Bias hunt

- [x] Primary = REL/REH → opposite HH/LL (ATLAS)  
- [x] Rival B = full HH/LL sweep (H003b)  
- [x] Foil A @09:30 all range days  
- [x] Horizon 12:00; range tertiles  
- [x] Tick-round REL/REH levels to 0.25  
- [x] Cite `H003_BOX_LOCK.md`
- [x] SELECTION-DEPENDENT in §5
- [~] Spot-check \(L_{rel}\) vs demo red — visual done; computed **PENDING tape** (`SPOTCHECK_H003c_LREL_VS_DEMO_2026-09-13.md`)
- [x] Multi-REL selection = closest to mid-range (not lowest-mean)  
- [x] NEW id (not silent H003b amend)  
- [x] No MERCURY / no lunch import  

---

## 7. RUN blockers

1. ~~CASSANDRA packaging~~ — **SURVIVED**  
2. Computed \(L_{rel}\) vs demo red — visual reads are **calibration only** (~21,020 ATLAS / ~29,020 earlier misread); **numeric PENDING stream C**; pass proximity still ≠ Observed identity  
3. Shared stream C + coverage projection  
4. No MERCURY  

---

## 8. Paths

- This: `experiments/QUANT_H003c_REL_TO_RANGE_PROTOCOL_2026-09-13.md`  
- Lock: `evidence/L81eMQhmXmc/H003_BOX_LOCK.md`  
- Rival packaging: `experiments/QUANT_H003b_79_SWEEP_OPPOSITE_PROTOCOL_2026-09-13.md`
