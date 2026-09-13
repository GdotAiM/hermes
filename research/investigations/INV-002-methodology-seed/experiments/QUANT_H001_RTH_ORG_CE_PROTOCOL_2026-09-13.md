# QUANT H001 — Experiment Protocol (DRAFT ONLY · NO RUN)
**Hypothesis ID:** H001  
**Investigation:** INV-002-methodology-seed · Wave 1  
**Parents (Passed Observed only):** C-METH-008, C-METH-009, C-METH-015  
**ORION rank:** #1 (verify-don’t-accept number)  
**Source specs:** `reviews/ORION_WAVE1_HYP_SPECS_2026-09-13.md`  
**Author:** QUANT  
**Filed:** 2026-09-13  
**Run status:** **HOLD** — shared tape (INV-001 stream C / WAVE1) not filed

---

## 0. Pre-registration lock

Frozen before any OHLC results. Post-peek rule change = **NEW hyp ID**.  
**Do not** import INV-001 lunch clocks (11:30, CISD, ASR 9:00 open).  
**RTH open = 9:30 ET only** (C-METH-008 amended; ASR 9:00 rejected).

---

## 1. Statement (locked)

On **NASDAQ index futures (1m)**, define the **RTH opening-range gap (ORG)** as:

- Prior session **16:14 ET** (4:14 p.m.) **final print** → current day **09:30 ET** RTH opening price (Passed **008**).  
- **CE** = midpoint of that gap (half / consequent encroachment).

**Primary question:** Does price **reach CE by 10:00 ET**? Estimate unconditional \(P(\text{hit})\) and conditionals given gap size, gap direction, prior-day trend, pre-market 07:00–09:00 state, and event-day stratum.

**Not a claim:** \(P \approx 0.70\). Lecture offers ~70% then withdraws it (Passed **009**). **0.70 is a foil / reference line only** — never a SURVIVES target.

C-METH-**015** (Passed): dealing/opening range = **30 minutes**; reject 5m/15m OR defs. H001’s object is the **overnight RTH ORG** (16:14→09:30), **not** the 30m cash-open OR. Do not conflate; 015 blocks importing retail 5/15m OR into this test.

---

## 2. Population / instrument / period / session

| Field | Lock |
|-------|------|
| Population | NASDAQ index futures RTH days with prior RTH session (ex Sundays for 7–9 state; standard US holiday exclusions) |
| Instrument | **MNQ** preferred (identical to INV-001 stream C) or **NQ** with documented 2× scale — **do not mix** |
| Bar size | **1-minute** OHLC |
| Timezone | **America/New_York**; UTC + ET wall-clock; DST-aware |
| Period | Shared stream C / WAVE1 date range once filed; QUANT states N after coverage projection |
| Prior print | **16:14 ET** bar close (or last print in that minute) of prior RTH day |
| RTH open | **09:30 ET** opening price (first 09:30 bar open, or official RTH open print — DATA to lock one; default = 09:30 bar **open**) |
| Deadline | **10:00 ET** — hit if CE traded by then (see §4) |
| Pre-market state window | **07:00–09:00 ET** (Passed 003) — for conditionals only |
| Shared tape | `INV-001 .../evidence/tape/` + `WAVE1_SHARED_TAPE_REQUIREMENTS.md` — one stack |

---

## 3. Mechanical definitions

### 3.1 Gap and CE

Let \(P_{ref}\) = prior day 16:14 ET final print.  
Let \(P_{open}\) = 09:30 ET RTH open.

- Gap size \(G = P_{open} - P_{ref}\) (signed points).  
- Gap direction: **up** if \(G > 0\), **down** if \(G < 0\), **flat** if \(G = 0\) (exclude flat from primary or report separately — pre-reg: **exclude** \(|G| < 0.25\) MNQ pts as flat).  
- \(\mathrm{CE} = (P_{ref} + P_{open}) / 2\).

### 3.2 Hit by 10:00 ET

**Hit** = within **[09:30, 10:00] ET** inclusive of the 10:00 bar, any 1m bar overlaps CE:

`low ≤ CE ≤ high`

Time-to-CE = timestamp of first such bar (minutes after 09:30).  
Miss = no overlap by end of 10:00 bar.

### 3.3 Conditioning features (report; not all in primary falsification)

| Feature | Definition |
|---------|------------|
| Gap size | \|G\| in points; tertiles for strata |
| Gap direction | up / down |
| Prior-day trend | Sign of prior RTH close − prior RTH open (or 09:30→16:00); PARAMETER label if not lecture-specified |
| Pre-market 7–9 state | Shared classifier with H002 (§3.4) once locked; until then report HH-LL range of 07:00–09:00 and close vs open of that window |
| Event day | Cite INV-001 `EVENT_CALENDAR_CPI_FOMC_NFP.md` — primary = non-CPI/FOMC/NFP |

### 3.4 Pre-market state (pointer to H002)

Do **not** invent a full classifier here. For H001 conditionals, use at minimum:

- \(R_{79}\) = high−low of [07:00, 09:00)  
- Direction: close of 08:59 bar vs open of 07:00 bar  

Full expansion↑/↓/consolidation/compression = **H002** lock; H001 may join after H002 defs freeze (same tape).

### 3.5 30m OR (015) — out of primary

Optional descriptive: 09:30–10:00 is also the first 30m OR window (Passed 015). H001 hit-by-10:00 is CE of **overnight gap**, not OR midpoint. Do not substitute OR mid for CE.

---

## 4. Primary metrics

- \(N\) eligible days  
- Unconditional \(\hat P(\text{hit by 10:00})\)  
- Bootstrap 95% CI (10_000)  
- Distribution of time-to-CE on hits  
- Foil line: plot 0.70 as reference **only** — label **FOIL (C-METH-009 withdrawn)**  

**Conditionals (descriptive + optional model):** hit rate by gap tertile × direction; by event vs non-event; by coarse 7–9 state.

**Costs:** N/A for hit-frequency primary (level touch, not trade). If later trade wrap → NEW hyp.

---

## 5. Null / falsification

### Pre-registered nulls

1. **Unconditional:** \(\hat P(\text{hit})\) not distinguishable from a **time-matched null**: probability that a **random price level** between \(P_{ref}\) and \(P_{open}\) (uniform on the gap segment) is touched by 10:00 — same path. (Tests whether CE is special vs any gap level.)  
2. **Foils:** distance of \(\hat P\) from 0.70 is **not** a pass/fail — report only.  
3. **Conditional lift:** a pre-registered logistic (gap size, direction, event flag) must improve OOS log-loss / Brier vs intercept-only; else “conditionals do not improve.”

### Decision labels

**FAILS (unconditional CE-specialness)** if OOS CI for \(\Delta = P(\text{touch CE}) - P(\text{touch random gap level})\) includes ≤0 (N≥80).  

**INCONCLUSIVE** if N<80 or tape/coverage fail.  

**SURVIVES (descriptive CE-specialness)** only if Δ>0 with CI entirely above 0 **and** walk-forward median Δ>0 — **never** phrased as “70% confirmed.”  

**SURVIVES (conditional utility)** only if OOS model beats intercept on pre-reg score — separate sentence from CE-specialness.

---

## 6. Sample splits

| Item | Lock |
|------|------|
| Min N | **80** RTH days for unconditional decision |
| Coverage projection | Required on ≥20 RTH days of shared tape before claiming N≥80 reachable |
| IS / OOS | 60% / 40% time-ordered |
| Walk-forward | After OOS; step 20 days |
| Event primary | Non-event days; event strata descriptive |
| Pilot | No lecture-demo day decision metrics |

---

## 7. Bias hunt

- [ ] 9:30 open only (no 9:00)  
- [ ] 16:14 prior print exact; holiday/early-close prior day policy  
- [ ] CE not confused with 30m OR mid (015)  
- [ ] 0.70 foil not used as success criterion  
- [ ] No INV-001 lunch import  
- [ ] Look-ahead: hit uses bars ≤10:00 only  
- [ ] MNQ/NQ not mixed  
- [ ] Event calendar cited  

---

## 8. DATA blockers

1. Shared stream C / WAVE1 tape META filled  
2. Coverage projection ≥20 RTH days  
3. Event calendar (already filed under INV-001 — cite)  
4. CASSANDRA red-team H001 before RUN (ORION standing order)

---

## 9. Downstream

- **CASSANDRA:** attack CE-vs-random-level null; 16:14 print choice; open print choice; foil misuse  
- **ORION:** H001 draft filed — awaiting tape + red team  
- **No MERCURY/RISK** wrappers  

## 10. Path

`investigations/INV-002-methodology-seed/experiments/QUANT_H001_RTH_ORG_CE_PROTOCOL_2026-09-13.md`
