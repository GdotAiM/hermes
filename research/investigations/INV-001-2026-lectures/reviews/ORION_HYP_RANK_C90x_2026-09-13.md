# ORION — ≤3 hypotheses (from Passed Observed only)
**Investigation:** INV-001  
**Lecture:** C90xGr3kW8Y  
**Date:** 2026-09-13  
**Parents Passed:** C-2026-001, 002, 003, 004, 005, 006, 009  
**Instrument lock (chart):** MNQ Mar 2026 · 1m · America/New_York  
**QUANT status:** HOLD — designs allowed; no run until tape stream C filed

## Ranking criteria
Expected information gain → Decision impact → Cost → Time → Reproducibility

---

### H1 — C-2026-015 (from Passed 009) · **HIGHEST VALUE**
**Statement:** A first FVG printed immediately before a lunch-window turtle-soup raid, projected into the next session, is touched at or near that next session’s high or low more often than a randomly chosen prior-day FVG.

**Why #1:** HISTORIAN: only **NEW-as-package** in this pilot. Highest information gain vs “same OR skeleton, new clock.”

**Parents:** Passed 009 (+ supporting 001–004)  
**Diff:** NEW (package) / REPACKAGE (components)  
**Needs for QUANT:** 1m MNQ (or documented continuous) with lunch window end 13:30 ET; define FVG/turtle-soup mechanically; next-session HOD/LOD touch metric; OOS after in-sample on non-CPI days first.

**Falsify if:** Touch rate ≤ random prior-day FVG control (pre-registered).

---

### H2 — C-2026-014 (from Passed 001–006) · **CLOCK TRANSPLANT**
**Statement:** On MNQ, a liquidity raid inside the 2-hour NY lunch window ending 13:30 ET, followed by a first-instance FVG entry in 13:30–14:00 ET, has expectancy different from the same entry rule in a random 30-minute RTH window.

**Why #2:** Tests whether PM OR packaging beats generic timing (REPACKAGE of 2024 OR / 2025 Venom onto PM clock). High decision impact for session models; lower novelty than H1.

**Parents:** Passed 001–006  
**Diff:** REPACKAGE / REFINE  
**Needs for QUANT:** Same tape; mechanical raid + first-FVG; costs/slippage; exclude or stratify CPI days (C-012).

**Falsify if:** No significant expectancy difference vs random 30m control after costs.

---

### H3 — Stand-aside / lunch non-hold filter (from Passed 005 + 004) · **RISK UTILITY**
**Statement:** During the NY lunch window (2h ending 13:30 ET), long holds of a bullish lunch imbalance underperform stand-aside / short-bias rules conditioned on a buy-side raid into the lunch close (as taught: do not expect bullish hold; seek liquidity).

**Why #3:** Directly serves RISK/MERCURY no-trade discipline; lower information gain on “edge,” high on process survival. Mechanically derived from Passed 004–005; not a separate ATLAS hyp card yet — QUANT must pre-register exact stand-aside rule with DATA.

**Parents:** Passed 004, 005  
**Diff:** REFINE  
**Falsify if:** Bullish hold of lunch imbalance during that window has non-negative expectancy after costs vs stand-aside.

---

## Explicitly not ranked for QUANT yet
| Item | Reason |
|------|--------|
| H-CISD-PRE (G1) | CISD not spoken in this lecture |
| H-SD (G1 titles) | Not in this pilot body |
| Taxonomy 11:30 start | Not speech-Observed (chart label only) |
| C-2026-012 CPI | Event track — MACRO, not session set |
| London / MOC / SB | Absent from this lecture |

## Highest-value next experiment
1. **DATA:** File tape stream C for MNQ Mar 2026, 1m, ET, ≥ 2026-03-10..11 (then expand sample).  
2. **QUANT:** Design H1 first (protocol only — no peek).  
3. **CASSANDRA:** Attack H1 packaging (selection of “first FVG before raid,” HOD/LOD vagueness, CPI contamination).
