# QUANT H002 — Experiment Protocol (DRAFT ONLY · NO RUN)
**Hypothesis ID:** H002  
**Investigation:** INV-002 · Wave 1  
**Parents (Passed Observed only):** C-METH-003, C-METH-004, C-METH-005  
**ORION rank:** #4 in draft order (classifier; precursor not panacea)  
**Author:** QUANT · **Filed:** 2026-09-13  
**Run status:** **HOLD** — shared tape  
**Dependency:** Classifier defs here are shared with H001 conditionals / H003 range.

---

## 0. Lock

Pre-reg. Ex Sundays (003). Post-9:30 behaviour predicted from 7–9 **precursor, not panacea** (005).  
Mechanical class defs below are **QUANT+DATA PARAMETERS** where lecture says “trending / consolidating / reversing” without numeric thresholds — labeled PARAMETER.

---

## 1. Statement

Classify each trading day (excl. Sundays) **07:00–09:00 ET** as **expansion↑ / expansion↓ / consolidation / compression** (mechanical). Test whether class predicts **post-09:30** path features (first side swept, range expansion, chop) at **10:00 / 11:00 / 12:00** horizons better than unconditional baseline. Falsify: no lift vs baseline after OOS.

---

## 2. Population / instrument

MNQ prefer · 1m · America/New_York · ETH required for 7–9 · shared tape.

---

## 3. Classifier (mechanical)

Window \(W=[07:00,09:00)\) ET:

- \(H, L\) = high/low in \(W\)  
- \(O\) = open of 07:00 bar; \(C\) = close of last bar in \(W\)  
- \(R = H - L\)  
- \(ATR_{ref}\) = median of prior **20** days’ 7–9 ranges (PARAMETER lookback)

| Class | Rule (PARAMETER thresholds) |
|-------|------------------------------|
| **expansion↑** | \(C > O\) and \(R \ge 1.0 \times ATR_{ref}\) and \((C-O)/R \ge 0.5\) |
| **expansion↓** | \(C < O\) and \(R \ge 1.0 \times ATR_{ref}\) and \((O-C)/R \ge 0.5\) |
| **compression** | \(R \le 0.5 \times ATR_{ref}\) |
| **consolidation** | else (range present but not directional expansion) |

Sensitivity: expansion multiplier ∈ {0.8, 1.0, 1.2}; compression ∈ {0.4, 0.5, 0.6} — report after primary OOS only.

Lecture “reversing” mapped into consolidation vs expansion opposite prior day — **descriptive only**, not a fifth primary class (avoid multiplicity).

---

## 4. Post-09:30 outcomes (labels)

At horizons T ∈ {10:00, 11:00, 12:00} ET:

| Feature | Definition |
|---------|------------|
| First side swept | First touch of 7–9 high vs low after 09:30 (same as H003 §3.2) |
| Range expansion | (high−low of [09:30, T)) / \(R\) |
| Chop | Range expansion < 1.0 **and** ≥3 direction changes of 5m closes (PARAMETER) |

**Primary predictive target:** first side swept ∈ {high, low, neither} — multiclass.  
Secondary: range expansion continuous; chop binary.

---

## 5. Baseline / falsification

**Baseline:** unconditional class frequencies / majority class; or previous-day class persistence.  

**Primary score:** OOS balanced accuracy / log-loss of class → first-side-swept vs intercept-only or majority baseline.  

**FAILS** if OOS lift ≤0 (no improvement vs baseline) on pre-reg score (N≥80 days).  
**SURVIVES** if lift>0 with bootstrap CI excluding 0 and walk-forward median lift>0.  
Prose must include **“not a panacea”** (005) — never claim deterministic post-9:30 read.

---

## 6. Linkage

- H001 may use coarse 7–9 features before this classifier freezes.  
- H003 uses same \(H,L\) box.  
Freeze classifier **before** any of H001/H002/H003 decision runs on shared tape.

---

## 7. Blockers

Shared tape; DATA ack on PARAMETER thresholds (or ATLAS demo stills); CASSANDRA on classifier leakage; coverage projection; no MERCURY/RISK.

## 8. Path

`experiments/QUANT_H002_79_STATE_CLASSIFIER_PROTOCOL_2026-09-13.md`
