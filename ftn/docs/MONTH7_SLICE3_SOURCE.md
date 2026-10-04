# Month 7 Slice 3 — full source copy

ICT weekly profile from **week-to-date path + weekly sponsorship**.  
Bias + dealing range alone stay `none`. No OSOK. No swing ticket.

Repo paths under `ftn-agent/`.

---

## What Slice 3 is

```
derive_month7_range()          # S2 environment
        +
evidence.week_path
weekly sponsorship
        ↓
classify_weekly_profile()
        ↓
ict_weekly_profile name | none
```

Thursday / midweek / Friday / S&D glossary names are **not** minted. Those need later path fields.

---

## 1. `src/ftn/os/m7_profile.py`

```python
"""Month-7 Slice 3: ICT weekly profile from week-to-date path + HTF bias.

Range + bias alone must not name a profile.
Does not set OSOK or swing_ticket.
"""

from __future__ import annotations

from ftn.os.m7_contracts import IctWeeklyProfile, Month7State
from ftn.os.m7_range import derive_month7_range


def _bias(raw: dict) -> str:
    inst = raw.get("pair_institutional") or {}
    return (inst.get("sponsorship") or {}).get("weekly") or inst.get("state") or "unclear"


def read_week_path(raw: dict) -> dict:
    ev = raw.get("evidence") or {}
    p = ev.get("week_path") or raw.get("week_path") or {}
    return {
        "extreme_low_day": (p.get("extreme_low_day") or "").lower(),
        "extreme_high_day": (p.get("extreme_high_day") or "").lower(),
        "ran_htf_discount_on": (p.get("ran_htf_discount_on") or "").lower(),
        "ran_htf_premium_on": (p.get("ran_htf_premium_on") or "").lower(),
        "monday_hovered_above_discount": bool(p.get("monday_hovered_above_discount")),
        "monday_hovered_below_premium": bool(p.get("monday_hovered_below_premium")),
    }


def classify_weekly_profile(bias: str, path: dict) -> tuple[str, str]:
    if not any(path.values()):
        return "none", "no_week_path"
    low = path.get("extreme_low_day")
    high = path.get("extreme_high_day")
    if bias == "bullish":
        if low == "tuesday" and path.get("ran_htf_discount_on") == "tuesday":
            return "classic_tuesday_low_of_week", "tue_low_into_htf_discount"
        if low == "wednesday" and path.get("ran_htf_discount_on") == "wednesday":
            return "wednesday_low_of_week", "wed_low_into_htf_discount"
        return "none", "bullish_path_insufficient"
    if bias == "bearish":
        if high == "tuesday" and path.get("ran_htf_premium_on") == "tuesday":
            return "classic_tuesday_high_of_week", "tue_high_into_htf_premium"
        if high == "wednesday" and path.get("ran_htf_premium_on") == "wednesday":
            return "wednesday_high_of_week", "wed_high_into_htf_premium"
        return "none", "bearish_path_insufficient"
    return "none", "bias_unclear"


def derive_month7_profile(raw: dict) -> Month7State:
    base = derive_month7_range(raw)
    name, why = classify_weekly_profile(_bias(raw), read_week_path(raw))
    state = "watching" if name != "none" else "none"
    return Month7State(
        dealing_range=base.dealing_range,
        ict_weekly_profile=IctWeeklyProfile(name=name, state=state, origin="ict_source"),
        manipulation_template=base.manipulation_template,
        ipda_window=base.ipda_window,
        lrlr=base.lrlr,
        intraweek_contrary=base.intraweek_contrary,
        osok_opportunity=base.osok_opportunity,
        swing_ticket=None,
        ict_guidance=base.ict_guidance,
    )
```

`any(path.values())` treats an all-empty path as no evidence. Monday hover flags are stored for Slice 4 templates; they do not by themselves name a profile.

---

## 2. Path fixture — `fixtures/m7_path_eurusd.json`

No `ict_weekly_profile` key.

```json
{
  "symbol": "EURUSD",
  "date": "2017-03-14",
  "last": 1.0662,
  "timezone": "America/New_York",
  "watchlist": ["EURUSD"],
  "pair_institutional": {
    "sponsorship": { "weekly": "bullish", "daily": "bullish", "h4": "bullish" },
    "state": "bullish"
  },
  "origin_pd_array": "W_FVG_bull",
  "opposing_target_arrays": ["WPH"],
  "ipda_days": 20,
  "evidence": {
    "notes": "M7 path Slice 3. Week-to-date observations. No profile key.",
    "week_path": {
      "extreme_low_day": "tuesday",
      "extreme_high_day": "",
      "ran_htf_discount_on": "tuesday",
      "ran_htf_premium_on": "",
      "monday_hovered_above_discount": true,
      "monday_hovered_below_premium": false
    }
  },
  "month7": {
    "dealing_range": {
      "from_array_id": "M_DISCOUNT",
      "from_tf": "monthly",
      "to_array_id": "W_PREMIUM",
      "to_tf": "weekly",
      "direction": "bullish"
    },
    "ipda_window": { "days": 20 }
  }
}
```

---

## 3. Decision table (this slice)

| Bias | extreme low/high day | ran HTF array that day | Profile |
|------|----------------------|------------------------|---------|
| bullish | low = tuesday | discount tuesday | `classic_tuesday_low_of_week` |
| bullish | low = wednesday | discount wednesday | `wednesday_low_of_week` |
| bearish | high = tuesday | premium tuesday | `classic_tuesday_high_of_week` |
| bearish | high = wednesday | premium wednesday | `wednesday_high_of_week` |
| * | missing path | | `none` |
| bullish | no matching pair | | `none` |

---

## 4. Test — `test_month7_slice3_profile`

```python
assert derive_month7_range(path).ict_weekly_profile.name == "none"
st = derive_month7_profile(path)
assert st.ict_weekly_profile.name == "classic_tuesday_low_of_week"
assert st.osok_opportunity.flag is False
assert st.swing_ticket is None
assert derive_month7_profile(evidence_no_path).ict_weekly_profile.name == "none"
```

---

## 5. Next permitted

Slice 4 — `manipulation_template` (liquidity pool / OB / retest) as a **separate** field. Do not collapse it into the weekly profile name.
