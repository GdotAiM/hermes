# Month 6 Slice 1 — full source copy

Contracts + optional `DayContext.month6` + known-state fixture.
**No detectors.** Slice 0 glossary (six MD gates) is the enum.

Repo paths under `ftn-agent/`.

---

## What Slice 1 is

```
known-state fixture
        ↓
parse_month6()
        ↓
DayContext.month6
```

M9 fixtures without a `month6` / `ict_swing` block → `month6 is None`.

Unknown sequential names parse as `none`. Unknown family → `none`.

`swing_opportunity.flag=true` does **not** create a ticket. There is no M6 persist object.

---

## 1. `src/ftn/os/m6_contracts.py`

Full file as shipped.

```python
"""Month-6 Slice 1 contracts. No detectors.

Glossary: Slice 0 signed with six Million-Dollar gates.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal, Optional

SwingFamily = Literal["bull", "bear", "none"]
Suit = Literal["suitable", "unsuitable", "unclear"]
MdState = Literal["assembled", "incomplete", "none"]
SeqState = Literal["watching", "none"]

BULL_SEQUENCES = (
    "mwd_all_bullish",
    "mw_bullish_daily_correcting",
    "m_bullish_wd_correcting",
)
BEAR_SEQUENCES = (
    "mwd_all_bearish",
    "mw_bearish_daily_correcting",
    "m_bearish_wd_correcting",
)
SEQUENCES = BULL_SEQUENCES + BEAR_SEQUENCES + ("none",)

MD_GATES = (
    "seasonal_tendency",
    "major_market_analysis",
    "intermarket_analysis",
    "top_down_analysis",
    "setup",
    "management",
)

REQUIRED_EVIDENCE = ("htf_trend", "institutional_order_flow", "pd_arrays")
CONFIRMING_EVIDENCE = ("seasonal_tendency", "interest_rates", "cot", "intermarket")
```

Dataclasses: `MarketSelection`, `SequentialPattern`, `SupportingEvidence`, `RiskFrame`, `MillionDollarSwing` (`state` + `missing` tuple), `SwingOpportunity`, `Month6State`.

`parse_month6(raw)` reads `month6` or `ict_swing`. Missing block → `None`.

---

## 2. `DayContext` hook — `src/ftn/os/contracts.py`

```python
    month8: object = None
    month7: object = None
    month6: object = None  # Month6State | None

def _month6(raw: dict):
    from ftn.os.m6_contracts import parse_month6
    return parse_month6(raw)

# load_day_context:
        month8=_month8(raw),
        month7=_month7(raw),
        month6=_month6(raw),
```

---

## 3. Known-state fixture — `fixtures/m6_reconstruction_xauusd.json`

Not evidence-only. Family / MD state / opportunity are **provided**. No `pick`.

XAUUSD 2017-02-14. Monthly+weekly bullish, daily correcting → provided `mw_bullish_daily_correcting`. MD **incomplete** (missing `management`). Opportunity true. `session_ticket` absent.

```json
{
  "symbol": "XAUUSD",
  "date": "2017-02-14",
  "focus_pair": "XAUUSD",
  "last": 1234.5,
  "timezone": "America/New_York",
  "watchlist": ["XAUUSD"],
  "pair_institutional": {
    "sponsorship": {"monthly": "bullish", "weekly": "bullish", "daily": "bearish"},
    "state": "bullish"
  },
  "origin_pd_array": "M_OB_bull",
  "opposing_target_arrays": ["W_PREMIUM"],
  "evidence": {"notes": "M6 KNOWN-STATE. Provided fields. No pick."},
  "month6": {
    "market_selection": {"state": "suitable"},
    "swing_family": "bull",
    "sequential_pattern": {"name": "mw_bullish_daily_correcting", "state": "watching"},
    "supporting_evidence": {
      "htf_trend": true,
      "institutional_order_flow": true,
      "pd_arrays": true,
      "seasonal_tendency": true,
      "interest_rates": true,
      "cot": true,
      "intermarket": true
    },
    "risk_frame": {
      "stop_reference": "M_OB_bull",
      "target_reference": "W_PREMIUM",
      "reward_frame": "discount_to_premium"
    },
    "million_dollar_swing": {"state": "incomplete", "missing": ["management"]},
    "swing_opportunity": {"flag": true, "reason": "provided_state"}
  }
}
```

This fixture proves the OS can **represent** incomplete MD. It does not prove a detector computed those gates.

---

## 4. Test — `test_month6_slice1_schema`

```python
def test_month6_slice1_schema():
    from ftn.os.contracts import load_day_context
    from ftn.os.m6_contracts import MD_GATES, BULL_SEQUENCES
    ctx = load_day_context(ROOT / "fixtures/m6_reconstruction_xauusd.json")
    assert ctx.month6 is not None
    assert ctx.month6.swing_family == "bull"
    assert ctx.month6.sequential_pattern.name == "mw_bullish_daily_correcting"
    assert ctx.month6.million_dollar_swing.state == "incomplete"
    assert "management" in ctx.month6.million_dollar_swing.missing
    assert ctx.month6.swing_opportunity.flag is True
    assert ctx.session_ticket is None
    ctx9 = load_day_context(ROOT / "fixtures/m9_reconstruction_eurusd.json")
    assert ctx9.month6 is None
    assert len(MD_GATES) == 6
    assert "mwd_all_bullish" in BULL_SEQUENCES
```

M9 `test_reconstruct_matches_gold` still passes.

---

## 5. What Slice 1 does not do

- No suitability detector
- No M/W/D sequential classifier
- No MD gate assembly
- No DTR / briefing / desk
- Does not add a swing child to `evaluate_candidates`
- Does not write `paper_swing` or `session_ticket`

---

## 6. Next permitted

Slice 2 — market suitability + HTF draw from labeled sponsorship. Must not name `sequential_pattern`.
