# QUANT H2 — Experiment Protocol (DRAFT ONLY · NO RUN)
**Hypothesis ID:** H2 / C-2026-014  
**Investigation:** INV-001  
**Lecture:** C90xGr3kW8Y  
**Parents (Passed Observed):** C-2026-001–006  
**ORION rank:** #2 (clock transplant / REPACKAGE)  
**Author:** QUANT  
**Filed:** 2026-09-13  
**Run status:** **HOLD** until DATA tape stream C filed  
**Dependency:** Prefer run **after** H1 plumbing validated on same tape (shared defs); do not peek H2 results before H1 OOS freeze if both coded in one notebook — separate result files.

---

## 0. Pre-registration lock

Frozen before any result peek. Post-peek rule change = **NEW HYPOTHESIS**.


---

## 0b. Labeling alignment with H1 (ORION 2026-09-13)

Lunch start **11:30 ET = PARAMETER** (not Observed speech). Same rule as H1 acceptance. Other H2 locks unchanged; further changes require **NEW hyp ID**.

---

## 1. Statement (locked)

On **MNQ**, a **liquidity raid** inside the **2-hour NY lunch window ending 13:30 ET**, followed by a **first-instance FVG entry in 13:30–14:00 ET**, has **expectancy different from** the **same entry rule** applied in a **random 30-minute RTH window**.

---

## 2. Population / instrument / period / session

| Field | Lock |
|-------|------|
| Instrument | MNQ Mar 2026 · 1m · America/New_York (same as H1 / DATA stream C) |
| Population | RTH sessions with complete lunch + PM OR |
| Period | Same expansion plan as H1; pilot plumbing 2026-03-10..11 only |
| Lunch | **PARAMETER [11:30, 13:30) ET** — start 11:30 = PARAMETER (arithmetic from Passed 001+002: 2h ending Observed 13:30); **not Observed speech**. Sensitivity (align H1): also report **[12:00, 13:30)** |
| PM OR / entry window (treatment) | **[13:30, 14:00) ET** (Passed 003) |
| Control window | Uniform random contiguous **30-minute** block with start ∈ RTH starts that keep the full 30m inside **[09:30, 16:00)**; drawn once per eligible day (seed recorded) |

---

## 3. Mechanical definitions

### 3.1 Lunch raid (gate for treatment day)

Reuse H1 §3.2 turtle-soup raid definition **or** simpler ORION-aligned gate (pre-register primary = **H1 turtle-soup** for consistency):

**Primary gate:** ≥1 valid turtle-soup raid in lunch with \(\tau_{raid} < 13:30\) (H1 §3.2).  
Days without raid: **no trade** (not a losing trade — excluded from expectancy sample; report coverage).

**Sensitivity gate (secondary):** any lunch-window break of AM RTH high (09:30–11:30 high) that fails back inside within 15m — report only.

### 3.2 Displacement + first FVG inside a 30m window W

Inside window \(W = [t_0, t_0+30m)\):

1. **Displacement:** a 1m close beyond the running high or low of \(W\) by **≥ 8 MNQ points** from the opposite extreme of \(W\) so far (range expansion filter). Record displacement side.
2. **First FVG after displacement:** first FVG (H1 §3.1) with birth ≥ displacement bar and birth < \(t_0+30m\), polarity **opposing** the displacement (entry for mean-reversion into FVG as in lecture short-into-bullish-FVG-after-buy-side example — wait:

Lecture example (Passed 006): after buy-side lunch run, **short** the first FVG in PM OR (bearish continuation / distribution into inefficiency).

So polarity rule:
- If lunch raid was **buy-side** → look for **bearish** first FVG after downward displacement in PM OR, **or** first FVG printed after displacement that price trades back into for a **short**.
- Simplify to lecture skeleton:

**Entry rule (locked):**
1. Require lunch **buy-side** raid (primary stratum). Sell-side raid = separate stratum (report; not pooled primary).
2. In window \(W\), detect **downward displacement**: close makes new window low and window range ≥ 8 pts.
3. **First FVG** after that displacement bar: nearest subsequent **bullish or bearish** FVG? Lecture: “first instance of a fair value gap” then “shorting” as price trades up into it → typically a **bearish FVG** (gap below) or a bullish FVG used as resistance after IFVG — ASR is ambiguous.

**Pre-registered disambiguation (must not change after peek):**
- **Primary:** first **bearish FVG** born after downward displacement in \(W\); **entry** = first later touch of that FVG zone from below (trade up into gap) → **short** at zone low (conservative: fill = zone_low on touch bar open if open inside zone else zone_low).
- **Sensitivity:** first FVG of **either** polarity after displacement; short only if touch from below into a bearish FVG or through a bullish FVG that has flipped (IFVG) — IFVG path is **secondary only** (C-007 REPACKAGE; keep out of primary).

### 3.3 Stops / targets / exit (trade test — required for expectancy)

| Field | Lock |
|-------|------|
| Side | Short (buy-side lunch raid stratum) |
| Entry | As §3.2 primary |
| Stop | 1m high of displacement swing + **2 pts**, or **12 pts** max risk from entry, whichever closer |
| Target | 1.5R (fixed R-multiple) **or** opposite lunch raid extreme (liquidity magnet), whichever hit first |
| Time stop | Flat at **15:55 ET** if still open |
| Skip | No entry if stop distance > **20 pts** (liquidity/gap day) |

Long mirror for sell-side lunch raid = **secondary stratum only**.

---

## 4. Control

Apply **identical** displacement → first bearish FVG → short rule inside the **random 30m RTH window** (no lunch-raid gate for control — tests whether PM-OR clock + lunch-raid conditioning beats generic timing).

**Alternative control (secondary):** same lunch-raid gate, but entry window = random 30m **outside** [13:30,14:00). Isolates clock vs raid.

Primary falsification uses **random 30m RTH** control per ORION statement.

---

## 5. Costs

| Item | Lock |
|------|------|
| Slippage | **0.5 MNQ point** per side |
| Spread | **0.25 point** round-turn proxy (or DATA-provided) |
| Commission | **$0.50** round-turn per side (micro) unless DATA specifies |
| Fill | Stop/target: stop on touch (conservative); target on touch |

---

## 6. Metrics

N, win rate, avg win/loss (R and $), expectancy ($/trade and R), profit factor, max DD ($ and %), MAE, MFE, trade frequency / day, % days with entry.

Paired or two-sample: treatment vs control expectancy difference \(\Delta_E\).

Bootstrap 10_000 on \(\Delta_E\).

---

## 7. Sample splits / stratification

Same as H1: N≥80 trades per arm preferred; else INCONCLUSIVE.  
Primary = **non-CPI**, exclude FOMC.  
IS 60% / OOS 40% time-ordered; walk-forward after.

---

## 8. Falsification

**FAILS** if OOS (N≥80 per arm or total trades gate met):  
bootstrap 95% CI for \(\Delta_E = E_{treat} - E_{ctrl}\) **includes 0** or \(\Delta_E \le 0\) after costs.

**SURVIVES** if CI entirely above 0 and walk-forward median \(\Delta_E > 0\).

---

## 9. Bias hunt

- [ ] Shared code with H1 must not leak H1 labels into H2 features  
- [ ] Random window seed fixed before run  
- [ ] No discretionary “which FVG”  
- [ ] Costs applied equally to both arms  
- [ ] Multiple-testing: H2 primary endpoint = one \(\Delta_E\); H1 separate  

---

## 10. DATA blockers

Same stream C as H1. Do not run.

---

## 11. Path

`investigations/INV-001-2026-lectures/experiments/QUANT_H2_C014_PROTOCOL_2026-09-13.md`
