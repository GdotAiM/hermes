# QUANT H1b — Experiment Protocol (DRAFT ONLY · NO RUN)
**Hypothesis ID:** **H1b** / C-2026-015 (pre-reg revision after CASSANDRA HOLD)  
**Supersedes for run-clearance:** H1 `QUANT_H1_C015_PROTOCOL_2026-09-13.md` (retained as audit; **do not run H1**)  
**Investigation:** INV-001  
**Lecture:** C90xGr3kW8Y · ICT 2026 New York Lunch Algorithmic Theory · 2026-03-11  
**Parents (Passed Observed):** C-2026-009 (+ supporting 001–004)  
**CASSANDRA:** `reviews/CASSANDRA_H1_C015_REDTEAM_2026-09-13.md` → HOLD; H1 did not survive as run-ready  
**Author:** QUANT  
**Filed:** 2026-09-13  
**Revision class:** Pre-registration revision — **no results peeked**; not a post-hoc amend of H1 locks  
**Run status:** **HOLD** — CASSANDRA packaging **SURVIVED** (`reviews/CASSANDRA_H1b_C015_REDTEAM_2026-09-13.md`); R1/R2/R4/R5 hygiene in §0d. **No run** until stream C + coverage projection (event calendar **filed** 2026-09-13). No MERCURY/RISK.

---

## 0. Why H1b (not amend-in-place)

CASSANDRA Attack 6 (control mismatch) is **CRITICAL**. Elevating the matched control and changing primary B policy are structural enough that ORION ordered a **new file / H1b** id. Other H1 mechanics that remain compatible are carried forward explicitly below.

**Rule:** Further post-filing changes to population, raid/FVG defs, touch metric, control, or falsification without peek still need ORION acknowledgment; **any change after peeking tape = NEW hyp ID** (not H1b amend).


---

## 0c. ATLAS FVG-map lock (2026-09-13) — Attack 2 closed

ATLAS filed `evidence/C90xGr3kW8Y/FVG_DEMO_LOCK.md`.  
**PRIMARY:** nearest / last inefficiency immediately before the raid (demo: BISI under lunch high).  
**RIVAL (report only):** first FVG of the impulsive leg.  
§3.3 updated to match. No other H1b locks changed. No tape peeked.


---

## 0d. CASSANDRA H1b hygiene amend (2026-09-13) — in-place, no peek

CASSANDRA: **HYPOTHESIS SURVIVED** packaging (`reviews/CASSANDRA_H1b_C015_REDTEAM_2026-09-13.md`). ORION: may **NOT** run; apply R1/R2/R4/R5 in place.

Applied: WIDTH-DEPENDENT SURVIVES gate (R1); rival/control collision rule (R2); hardened CLOCK-DEPENDENT vocabulary (R4); primary B=0 = containment only (R5).  
External RUN gates remaining: stream C + coverage projection. Event calendar **CLEARED** 2026-09-13. No MERCURY/RISK.

---

## 1. Statement (locked)

A **nearest pre-raid, polarity-matched lunch FVG** (treatment; §3.3 primary map), when carried into the **next RTH session**, is **associated with the next session’s high or low** (B=0 primary; §4) **more often than** a **time-matched same-polarity lunch FVG that is not the treatment FVG** (primary control; §5).

Random full-RTH FVG is **secondary descriptive only** — not part of the primary falsification.

---

## 2. Population / instrument / period / session

| Field | Lock |
|-------|------|
| Population | CME equity-index micro futures sessions with a complete RTH day after a prior RTH day |
| Instrument | **MNQ Mar 2026** · **1-minute** OHLC · **America/New_York** (EDT on 2026-03-11); continuous only if DATA documents roll |
| Period (pilot seed) | ≥ **2026-03-10 .. 2026-03-11** — **plumbing only**; **zero** decision metrics, touch rates redacted/NaN in decision tables |
| Expansion | Only after DATA amends stream C; same frozen defs |
| Lunch — Observed | **End 13:30 ET** (Passed **002**); **length 2 hours** (Passed **001**) |
| Lunch — PARAMETER start | **11:30 ET = PARAMETER** (arithmetic 13:30−2h). **Not Observed speech.** Not taxonomy import. |
| Primary lunch window | **PARAMETER [11:30, 13:30) ET** |
| Co-reported sensitivity window | **[12:00, 13:30) ET** — mandatory co-report (same defs). If Δ sign/CI decision flips vs primary → label **CLOCK-DEPENDENT**; do not promote as lecture confirmation |
| Next session | Next **RTH** **[09:30, 16:00] ET**; exclude if RTH < 390 minutes |
| SURVIVES language ban | **SURVIVES must not claim “Observed 11:30 lunch.”** Summaries must say PARAMETER start |

**Estimand (explicit):** H1b primary = non-event RTH days (§7) after a lunch-raid treatment unit, comparing treatment FVG vs matched lunch control on next-day extreme association.

---

## 3. Mechanical definitions (no discretion)

### 3.1 Fair Value Gap (FVG) — 1m

On completed bars \(t-2, t-1, t\):

- **Bullish FVG:** `low[t] > high[t-2]` → zone `[high[t-2], low[t]]`
- **Bearish FVG:** `high[t] < low[t-2]` → zone `[high[t], low[t-2]]`

Birth = bar \(t\) close. Primary touch uses zone high/low bounds (not midpoint).

### 3.2 Turtle-soup / liquidity raid (lunch window)

Inside the active lunch window \(W\) (primary \(W=[11:30,13:30)\); sensitivity rerun with \(W=[12:00,13:30)\)):

**Buy-side turtle-soup raid** if all hold:
1. New high of lunch window so far.
2. Exceeds prior fractal swing high: high[i] > high[i−1] and high[i] > high[i+1], with i+1 completed before raid, inside \(W\).
3. Within **N_raid = 15** minutes, close back below broken swing high.

Sell-side = mirror.  
\(\tau_{raid}\) = reclaim close.  
Multiple raids → **last** with \(\tau_{raid}\) before window end (primary). **Rival (report only):** first raid in window — sensitivity after primary OOS only; not for picking survivors.

No raid → no treatment unit (coverage diagnostic).

### 3.3 FVG map — ATLAS locked (Attack 2)

**Source lock:** `evidence/C90xGr3kW8Y/FVG_DEMO_LOCK.md` (ATLAS · 2026-09-13)  
**ORION:** use as Attack 2 lock for H1b.

| Role | Definition | Status |
|------|------------|--------|
| **PRIMARY treatment** | **Nearest / last inefficiency immediately before the raid** — eligible FVGs with birth ∈ \(W\), birth < \(\tau_{raid}\), polarity matches raid (buy-side→bullish / BISI; sell-side→bearish); take **latest birth** (last/nearest under the raid extreme). Demo points to **BISI under lunch high**, not lower mid-impulse boxes. | **LOCKED** by ATLAS |
| **RIVAL treatment (report only)** | **First FVG of the impulsive leg** (earliest eligible matching-polarity FVG on the displacement/impulse into the raid — not nearest). Visible as lower boxes on demo (~25,000); speaker does **not** point to those when stating the rule. | Pre-registered rival; **does not** drive SURVIVES/FAILS |

**How to read lecture “first”:** ATLAS: “first fair value gap right before the liquidity is taken” = the FVG in that pocket immediately before the take — **not** “first FVG printed in the impulse.”

**If future demo re-read disagrees with this lock:** **NEW hyp ID** — do not amend H1b primary in place.

### 3.4 Treatment level

\(L\) = primary treatment FVG zone on day \(D\); evaluate on \(D+1\) RTH.

---

## 4. Outcome metric (primary = B=0)

On day \(D+1\) RTH: \(H_{D+1}\) = RTH high; \(L_{D+1}\) = RTH low.

**Zone overlap:** any 1m bar with `low ≤ zone_high` and `high ≥ zone_low`.

### Primary success (B = 0) — containment only (R5)

**Normative primary (locked):** success iff the session extreme **price level** lies inside the FVG zone:

`zone_low ≤ H_{D+1} ≤ zone_high` **OR** `zone_low ≤ L_{D+1} ≤ zone_high`

No buffer. No alternate extreme-bar-overlap rule in primary.  
**Extreme-bar overlap** (session extreme bar’s range overlaps zone) is **secondary only** (§4 secondary / §8) — never coded as primary B=0.

### SURVIVES gate on buffer

- Primary falsification uses **B=0** only.  
- Sensitivity B∈{2,4,8} may be reported **after** primary OOS as descriptive.  
- If a narrative ever cites B>0, it must also show **B=0 agreement**; if only B≥4 “works,” label **BUFFER-DEPENDENT** — not lecture confirmation. **SURVIVES requires B=0 success on the primary Δ.**

### Width strata (mandatory report)

Split treatment and control zones into tertiles by zone height (points). Report Δ within each tertile. Wide-zone geometric bias must be visible.

### Secondary metrics (not primary falsification)

- Extreme-bar overlap rate: session extreme bar’s range overlaps zone (turn-adjacent)  
- MAE/MFE of first zone touch vs extreme  
- Time-of-day of first zone touch  
- B∈{2,4,8} sensitivity (post primary OOS only for decision hygiene)

---

## 5. Control (CRITICAL fix)

### Primary control — time-matched, same-polarity lunch FVG

For each treatment day \(D\) with valid treatment FVG \(L\):

1. Eligible controls: all FVGs with birth ∈ \(W\), birth < \(\tau_{raid}\), **same polarity** as treatment, **excluding** the treatment FVG itself.  
2. Draw **one** uniformly at random (seed recorded) → \(L_{ctrl}\).  
3. If no eligible control FVG: day contributes **no pair** (count in coverage: “raid+treatment but no matched control”).  
4. Apply identical §4 B=0 success rule on \(D+1\).

**Paired design:** one (treatment, matched-control) pair per eligible day.

**Estimand note:** Control is lunch-born and polarity-matched but **not** required to be “immediately pre-raid” in the nearest sense — it is a random other same-window same-polarity FVG. This isolates the packaging (nearest-pre-raid selection) from generic lunch FVG behavior.

### Rival analysis control rule (R2) — mandatory when citing Δ_rival

Primary control excludes only the **nearest (primary) treatment**. The rival (first-of-impulse) FVG can still be drawn as control, which corrupts Δ_rival.

**When reporting Δ_rival**, use **(b)** (locked): **drop pairs where control FVG == rival FVG**, then recompute descriptive Δ_rival on the remaining pairs. Also report N dropped.

Do **not** use Δ_rival for SURVIVES/FAILS. Primary Δ unchanged (still excludes primary treatment only).

### Secondary controls (descriptive only — not falsification)

| Control | Use |
|---------|-----|
| Random other **RTH** FVG same day (exclude treatment) | Weak / negative control — H1 legacy; may show large Δ that **overclaims** packaging if matched Δ is null |
| Random lunch FVG **either polarity** | Polarity confound check |
| Random lunch FVG on **no-raid** days | Different estimand; report separately if ORION wants external foil |

---

## 6. Entry / exit / stop / target / risk

Level-revisit frequency test only — **no fills** in H1b primary.  
Any MERCURY trade wrap = **NEW** hypothesis; RISK caps apply then.

---

## 7. Events, sample, splits

### Event calendar (exclude from primary)

Pre-register exclusion file path (DATA/MACRO to file; cite when present):

**FILED 2026-09-13:** `investigations/INV-001-2026-lectures/evidence/EVENT_CALENDAR_CPI_FOMC_NFP.md`  
CSV: `investigations/INV-001-2026-lectures/evidence/EVENT_CALENDAR_CPI_FOMC_NFP_2026.csv`


- US **CPI** release days  
- **FOMC** decision days  
- **NFP** (Employment Situation) release days  

Primary = **non-event** days under that calendar.  
Also report strata: CPI-only; NFP-only; all-days pooled (**descriptive**). If pooled flips vs primary → **EVENT-SENSITIVE**.

Half-days / holidays: exclude.

### Sample / power

| Item | Lock |
|------|------|
| Decision N | **N ≥ 80** paired days (treatment + primary control both defined); else **INCONCLUSIVE** |
| Matched-control miss (R3) | Report % of treatment days with no eligible control; if miss **>25%**, ORION summary must state restricted estimand (multi-gap lunch days) |
| Before claiming N≥80 reachable | After stream C covers ≥20 consecutive RTH days: publish **coverage projection only** — \(\hat P(raid)×\hat P(treatment FVG)×\hat P(matched control)×\hat P(full D+1)\) — **no Δ**, no SURVIVES/FAILS |
| Pilot 2026-03-10..11 | Plumbing / `plumbing_ok` only; **no** decision metrics |
| IS / OOS | 60% / 40% time-ordered after expansion; single OOS look |
| Walk-forward | After OOS; expanding; step 20 days; median Δ > 0 required for SURVIVES |

---

## 8. Metrics (report set)

- N pairs; coverage (raid rate; treatment FVG rate; matched-control availability)  
- \(p_{treat}\), \(p_{ctrl}\), \(\Delta = p_{treat}-p_{ctrl}\) at **B=0**  
- Bootstrap 95% CI on Δ (**10_000** resamples)  
- Same Δ on sensitivity window [12:00,13:30)  
- Width-tertile Δ  
- Rival treatment Δ (first FVG of impulsive leg) — descriptive; **R2:** drop pairs where control == rival  
- Secondary weak RTH-control Δ — descriptive  
- Extreme-bar overlap rates  

---

## 9. Falsification (pre-committed)

On **OUT-OF-SAMPLE**, N≥80 pairs, **B=0**, primary window, vs **matched lunch control**:

**FAILS** if:
1. \(\Delta \le 0\), **or**
2. Bootstrap 95% CI for Δ includes ≤0

**SURVIVES (lecture confirmation)** only if **all** hold:
1. OOS Δ > 0 and CI entirely above 0 (primary matched control, B=0, nearest treatment, PARAMETER [11:30,13:30))  
2. Walk-forward median Δ > 0  
3. Sensitivity window [12:00,13:30) does **not** flip the decision (same sign and CI entirely above 0). **If it flips:** do **not** use bare “H1b SURVIVES.” At most **SURVIVES (PARAMETER-clock only)** — a **different claim label** requiring NEW hyp id or explicit non-lecture tag (**R4**). Never narrate PARAMETER-only edge as lecture confirmation.  
4. SURVIVES prose **never** claims Observed 11:30  
5. B=0 is the cited endpoint (no B>0-only survival story)  
6. **WIDTH-DEPENDENT gate (R1):** if overall Δ would otherwise SURVIVE but **only** the widest width tertile shows Δ>0 with CI>0 while narrow and mid tertiles do not → label **WIDTH-DEPENDENT** — **do not** promote as lecture confirmation

**INCONCLUSIVE:** N<80, coverage projection fails to support N≥80 in available tape, or DATA gate fail. (ATLAS FVG map resolved via `FVG_DEMO_LOCK.md`.)

**Multiplicity:** One primary Δ (matched control, B=0, nearest/last pre-raid treatment per ATLAS lock, PARAMETER [11:30,13:30)). Rival (first-of-impulse) / secondary are not alternative paths to SURVIVES.

---

## 10. Bias hunt checklist

- [ ] Look-ahead / completed bars only  
- [ ] No future bars in raid/FVG  
- [ ] Matched control elevated (Attack 6 addressed)  
- [ ] 11:30 PARAMETER; co-report [12:00,13:30); SURVIVES language ban  
- [x] ATLAS FVG map lock (`FVG_DEMO_LOCK.md`) — nearest/last primary; first-of-impulse rival  
- [x] Rival/control collision rule (R2): drop pairs where control == rival for Δ_rival  
- [x] CLOCK-DEPENDENT vocabulary hardened (R4): lecture SURVIVES vs PARAMETER-clock-only  
- [x] B=0 containment-only primary (R5); width tertiles + WIDTH-DEPENDENT SURVIVES gate (R1)  
- [x] CPI + FOMC + **NFP** exclusions — calendar filed `evidence/EVENT_CALENDAR_CPI_FOMC_NFP.md`  
- [ ] No pilot decision metrics; coverage projection before N≥80 claim  
- [ ] Random RTH control not used for falsification  
- [ ] No post-peek revision without NEW id  

---

## 11. DATA / ATLAS blockers (do not run until)

1. Tape stream **C** (MNQ Mar 2026, 1m, ET, ≥2026-03-10..11 + expansion)  
2. ~~Event calendar (CPI, FOMC, NFP)~~ — **DONE** `evidence/EVENT_CALENDAR_CPI_FOMC_NFP.md` (+ `_2026.csv`)  
3. ~~ATLAS co-sign on §3.3~~ — **DONE** (`FVG_DEMO_LOCK.md`: nearest/last pre-raid primary; first-of-impulse rival)  
4. Coverage projection on ≥20 RTH days before OOS decision  
5. Prefer: CASSANDRA re-review of H1b if ORION queues it  

---

## 12. Downstream

- **CASSANDRA:** H1b packaging **SURVIVED**; hygiene R1/R2/R4/R5 applied (§0d)  
- **ATLAS:** FVG map lock **filed** — `evidence/C90xGr3kW8Y/FVG_DEMO_LOCK.md`  
- **DATA:** event calendar **filed**; stream C + coverage projection still blocking RUN  
- **ORION:** H1b packaging cleared; remaining RUN gates = stream C + calendar + coverage; H2/H3 draft; no runs; no MERCURY/RISK  
- **RISK / MERCURY:** no wrappers  

---

## 13. Paths

- This file: `investigations/INV-001-2026-lectures/experiments/QUANT_H1b_C015_PROTOCOL_2026-09-13.md`  
- Prior (do not run): `experiments/QUANT_H1_C015_PROTOCOL_2026-09-13.md`  
- Red team: `reviews/CASSANDRA_H1_C015_REDTEAM_2026-09-13.md`
