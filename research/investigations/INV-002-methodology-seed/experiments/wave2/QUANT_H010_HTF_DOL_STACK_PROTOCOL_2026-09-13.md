# QUANT H010 — HTF proximity improves DOL pick (DRAFT ONLY · NO RUN)
**Hypothesis ID:** H010  
**Wave 2** · ORION rank #2  
**Parents:** **C-METH-027, 028** — **Passed Observed** (DATA 2026-09-13); session midpoints still **unavailable** on FREE_YF  
**Tape:** FREE_YF_NQ — **daily primary**; **hourly secondary (~60d only)**  
**Filed:** 2026-09-13 · QUANT (revised)  
**HOLD** for DATA Pass + CASSANDRA  

---

## 0. Critical tape gap (027)

C-METH-027 asks Asia / London / NY AM / NY lunch **session** HH/LL **and midpoints**.  

**FREE_YF has no 15m (or 1m) session bars.** Session midpoints are **NOT** in this tape.  

H010 on FREE_YF = **daily / hourly proxy only**. Full 027 session stack = **BLOCKED** until finer tape — do not narrate SURVIVES as confirming session-midpoint DOL.

028’s HTF proximity claim (“higher TF nearby → more likely draw”) **can** be piloted with PW/PM/PD + last-3-day range on daily/hourly.

---

## 1. Statement (028-feasible slice)

Predict which of \(\{PWH,PWL,PDH,PDL\}\) (+ optional last-3-day high/low) is delivered first on the next daily bar path, using a rule that **weights higher-timeframe levels when nearer** (028). Compare vs daily-only nearest and vs random.

**Falsify:** HTF-aware ≤ daily-only and ≤ random OOS.

---

## 2. Levels at day D close → predict D+1

| Level | Source on FREE_YF |
|-------|-------------------|
| PWH/PWL | Prior week HH/LL (weekly csv) |
| PDH/PDL | Day D high/low |
| L3H/L3L | High/low of days D-2..D (dynamic — 028) |
| Session HH/LL/mid | **UNAVAILABLE** on FREE_YF — out of scope |

First-delivery proxy on D+1 daily OHLC: among levels touched that day, pick closest to Open (PARAMETER). Hourly ET path on 60d window = secondary **HOURLY-PROXY**.

---

## 3. Rulesets (PARAMETER packaging of 028)

**Daily-only:** predict \(\arg\min |x - C_D|\) for \(x \in \{PDH,PDL\}\).  

**HTF-aware:** among \(x \in \{PWH,PWL,PDH,PDL\}\), predict \(\arg\min |x-C_D|\) but if a weekly level is within \(0.25·ATR_{20}\) of \(C_D\) and a daily level is also near, **prefer weekly** (028 higher-TF priority). Exact band = PARAMETER; co-report \(0.5·ATR_{20}\).

**Random:** uniform on the four.

---

## 4. Falsification

N≥80 OOS days. FAILS if HTF accuracy does not beat both daily-only and random (bootstrap CI).  
SURVIVES must say **PARAMETER HTF band**, **CONTINUOUS-YF**, **no session-midpoint claim (027 gap)**.

## 5. Path

`experiments/wave2/QUANT_H010_HTF_DOL_STACK_PROTOCOL_2026-09-13.md`
