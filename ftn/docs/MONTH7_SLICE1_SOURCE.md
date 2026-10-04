# Month 7 Slice 1 — full source copy

Contracts + optional `DayContext.month7` + known-state fixture.  
**No detectors.** Glossary is Slice 0.

Repo paths under `ftn-agent/`.

---

## What Slice 1 is

```
known-state fixture
        ↓
parse_month7()
        ↓
DayContext.month7
```

M9 fixtures without a `month7` / `ict_week` block → `month7 is None`.

Profile names unknown to `WEEKLY_PROFILES` parse as `none`. Same for templates.

`osok_opportunity.flag=true` does **not** create `swing_ticket`.

---

## 1. `src/ftn/os/m7_contracts.py`

Full file as shipped.

```python
"""Month-7 Slice 1 contracts. No detectors.

Glossary frozen from Slice 0 (lessons 2–3).
Hermes profile ≠ ict_weekly_profile.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal, Optional

Tf = Literal["monthly", "weekly", "daily", "h4", "none"]
Dir = Literal["bullish", "bearish", "unclear"]
LrlrState = Literal["low", "high", "unclear"]
Contrary = Literal["watch", "confirmed", "none"]
ProfState = Literal["watching", "invalidated", "none"]

WEEKLY_PROFILES = (
    "classic_tuesday_low_of_week",
    "classic_tuesday_high_of_week",
    "wednesday_low_of_week",
    "wednesday_high_of_week",
    "consolidation_thursday_reversal_bullish",
    "consolidation_thursday_reversal_bearish",
    "consolidation_midweek_rally",
    "consolidation_midweek_decline",
    "seek_and_destroy_bullish_friday",
    "seek_and_destroy_bearish_friday",
    "wednesday_weekly_reversal_bullish",
    "wednesday_weekly_reversal_bearish",
    "none",
)

MANIPULATION_TEMPLATES = (
    "classic_tuesday_low_liquidity_pool",
    "classic_tuesday_low_old_high_retest",
    "classic_tuesday_low_bullish_order_block",
    "classic_tuesday_high_liquidity_pool",
    "classic_tuesday_high_old_low_retest",
    "classic_tuesday_high_bearish_order_block",
    "wednesday_low_liquidity_pool",
    "wednesday_low_old_high_retest",
    "wednesday_low_bullish_order_block",
    "wednesday_high_liquidity_pool",
    "wednesday_high_old_low_retest",
    "wednesday_high_bearish_order_block",
    "consolidation_midweek_rally",
    "consolidation_midweek_decline",
    "consolidation_thursday_reversal_bullish",
    "consolidation_thursday_reversal_bearish",
    "seek_and_destroy_bullish_friday",
    "seek_and_destroy_bearish_friday",
    "wednesday_weekly_reversal_bullish",
    "wednesday_weekly_reversal_bearish",
    "none",
)
```

Dataclasses: `DealingRange`, `IctWeeklyProfile`, `ManipulationTemplate`, `IpdaWindow` (20|40|60|None), `Lrlr`, `IntraweekContrary`, `OsokOpportunity`, `SwingTicket` (`kind=paper_swing`, `origin=hermes_governance`), `Month7State`.

`parse_month7(raw)` reads `month7` or `ict_week`. Missing block → `None`.

---

## 2. `DayContext` hook — `src/ftn/os/contracts.py`

```python
    month8: object = None
    month7: object = None  # Month7State | None

def _month7(raw: dict):
    from ftn.os.m7_contracts import parse_month7
    return parse_month7(raw)

# load_day_context:
        month8=_month8(raw),
        month7=_month7(raw),
```

---

## 3. Known-state fixture — `fixtures/m7_reconstruction_eurusd.json`

Not evidence-only. Profile / template / opportunity are **provided**. No `pick`.

```json
{
  "symbol": "EURUSD",
  "date": "2017-03-14",
  "focus_pair": "EURUSD",
  "last": 1.0662,
  "timezone": "America/New_York",
  "calendar": [],
  "watchlist": ["EURUSD"],
  "opens": { "gmt0": 1.0648, "ny_midnight": 1.065 },
  "ranges": {
    "previous_day": { "high": 1.0681, "low": 1.0624, "close": 1.0648 },
    "named_extremes": { "pdh": 1.0681, "pdl": 1.0624 }
  },
  "pair_institutional": {
    "sponsorship": { "weekly": "bullish", "daily": "bullish", "h4": "bullish" },
    "daytrade_iof": { "daily": "bullish", "h4": "bullish", "m60": "unclear" },
    "state": "bullish"
  },
  "origin_pd_array": "W_FVG_bull",
  "opposing_target_arrays": ["WPH"],
  "scenarios": {
    "primary": "KNOWN-STATE M7 schema fixture. Not detector proof.",
    "contrary": "Wednesday weekly reversal if Tue low fails."
  },
  "evidence": {
    "notes": "M7 KNOWN-STATE. Profile/template/opportunity are provided. No pick."
  },
  "month7": {
    "dealing_range": {
      "from_array_id": "M_DISCOUNT",
      "from_tf": "monthly",
      "to_array_id": "W_PREMIUM",
      "to_tf": "weekly",
      "direction": "bullish"
    },
    "ict_weekly_profile": {
      "name": "classic_tuesday_low_of_week",
      "state": "watching"
    },
    "manipulation_template": {
      "name": "classic_tuesday_low_liquidity_pool",
      "pool_tf": "weekly"
    },
    "ipda_window": { "days": 20 },
    "lrlr": { "state": "low" },
    "intraweek_contrary": { "state": "watch" },
    "osok_opportunity": { "flag": true, "reason": "provided_state" },
    "swing_ticket": null,
    "ict_guidance": {
      "weekly_extreme_mon_wed": "often ~70-76%",
      "note": "guidance not hermes_governance"
    }
  }
}
```

---

## 4. Test — `test_month7_slice1_schema`

```python
def test_month7_slice1_schema():
    from ftn.os.contracts import load_day_context
    from ftn.os.m7_contracts import WEEKLY_PROFILES
    ctx = load_day_context(ROOT / "fixtures/m7_reconstruction_eurusd.json")
    assert ctx.month7 is not None
    assert ctx.month7.ict_weekly_profile.name == "classic_tuesday_low_of_week"
    assert ctx.month7.manipulation_template.name == "classic_tuesday_low_liquidity_pool"
    assert ctx.month7.osok_opportunity.flag is True
    assert ctx.month7.swing_ticket is None
    assert ctx.session_ticket is None
    ctx9 = load_day_context(ROOT / "fixtures/m9_reconstruction_eurusd.json")
    assert ctx9.month7 is None
    assert "classic_tuesday_low_of_week" in WEEKLY_PROFILES
```

M9 `test_reconstruct_matches_gold` still passes.

---

## 5. What Slice 1 does not do

- No dealing-range detector  
- No weekly-profile detector  
- No LRLR detector  
- No `swing_ticket` writer  
- No DTR / briefing / desk  
- Does not add OSOK to `evaluate_candidates`

---

## 6. Next permitted

Slice 2 — dealing range + IPDA from labeled HTF arrays. Must not name `ict_weekly_profile`.
