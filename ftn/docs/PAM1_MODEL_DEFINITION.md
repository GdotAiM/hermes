# PAM1 Model Definition — FROZEN (research)

Status: Research definition — **implementation not yet authorized.**

## Charter identity

- `pam_id`: pam1
- `pam_horizon`: intraday_scalp
- Named model: ICT Charter Price Action Model 1 — Intraday Scalping
- Theme: Previous Day High & Low

## Canon (one model, three lectures)

1. https://www.youtube.com/watch?v=vCvRrINpknI — primary
2. https://www.youtube.com/watch?v=rNn0JkItAGo — amplified
3. https://www.youtube.com/watch?v=4f1vjQMlV50 — trade plan & algorithmic theory

## Purpose

Intraday **New York** scalp: directional retracement into **OTE**, targeting **previous daily liquidity** inside the relevant **IPDA data range**.

## Directional premise

**Bullish:** bullish IOF / HTF sponsorship; daily structure incl. swing high taken in 20-day IPDA range; not premium; upside previous-daily objective available.  
**Bearish:** inverse.

## Liquidity objective

Previous daily highs/lows **within the active IPDA data range** (not necessarily “yesterday only”). Primary lookback **20 trading days**; **40-day** when objective extends beyond 20-day range.

## Session / time

- NY session / NY Kill Zone
- Core algorithmic window ≈ **07:00–10:00** New York; monitor retracement through broader ≈07:00–11:00 in original material
- **No new PAM1 trade after 10:00** NY under the algorithmic trade plan
- Execution chart: **5-minute**
- Days: Mon–Wed preferred; Thu conditional; **Friday excluded**

## Named setup

**OTE** (Optimal Trade Entry).

Bullish: HTF premise → retrace lower → bullish OTE → NY window → prior-day high objective.  
Bearish: inverse toward prior-day low.

Trade-plan entry level: **~62% Fib** with stated ±5-pip spread adjustment.

## Structural / confirming anatomy (not sole recognition rule)

liquidity run → displacement → MSS → return to institutional reference (breaker / OB) → delivery toward opposing liquidity.

**Must not** become: `MSS ∧ OB ∧ raid ∧ … → PAM1`.

## Invalidation / management (trade plan, not recognition)

- Protective stop on NY retracement / OTE anchor (with stated spread allowance)
- **No re-entry that day** if stopped
- Partials, stop trail, successive daily-liquidity / extension objectives; optional runner

## Required conceptual evidence (model instance)

explicit pam1 id · direction · IPDA context · HTF sponsorship · previous-daily objective · NY window · OTE · directional link entry→objective

## Confirming only

raid · displacement · MSS · breaker · OB · premium/discount · London context · calendar · 40-day · extension beyond prior day

## Core relationship

**Read-only** consumption of M1–M12 / Market State. No recompute, overwrite, or mutation.  
PAM1 does **not** create M7 `paper_swing` or M9 `session_ticket`.

## Recognition boundary (Charter S0–S6)

```
identified_pam == present AND named pam1 in evidence
    → recognized_pams may contain pam1
```

Market evidence **describes** the instance; it does **not** silently manufacture Charter recognition.

## Non-goals

No Core-coexistence inference · no PAM ranking · no paper swing · no session ticket · no broker · no PAM2–12 in this pilot
