# Month 7 Slice 2 — full source copy

Dealing range + IPDA from **labeled** HTF arrays. Does **not** name `ict_weekly_profile`.

Repo paths under `ftn-agent/`.

---

## What Slice 2 is

```
labeled from_array / to_array / weekly sponsorship / ipda days
        ↓
derive_month7_range()
        ↓
DealingRange + IpdaWindow
ict_weekly_profile = none
manipulation_template = none
osok_opportunity = false
swing_ticket = None
```

Same guard as M8 Slice 2: environment first, path/profile later.

---

## 1. `src/ftn/os/m7_range.py`

```python
"""Month-7 Slice 2: dealing range + IPDA from labeled arrays.

Does not name ict_weekly_profile.
"""

from __future__ import annotations

from ftn.os.m7_contracts import (
    DealingRange,
    IctWeeklyProfile,
    IntraweekContrary,
    IpdaWindow,
    Lrlr,
    ManipulationTemplate,
    Month7State,
    OsokOpportunity,
    parse_month7,
)


def _tf_from_id(aid: str | None) -> str:
    if not aid:
        return "none"
    a = aid.upper()
    if a.startswith("M_") or a.startswith("MN") or "MONTH" in a:
        return "monthly"
    if a.startswith("W_") or "WEEK" in a:
        return "weekly"
    if a.startswith("D_") or a.startswith("PD"):
        return "daily"
    if a.startswith("H4") or a.startswith("4H"):
        return "h4"
    return "none"


def _direction(raw: dict) -> str:
    inst = raw.get("pair_institutional") or {}
    return (
        (inst.get("sponsorship") or {}).get("weekly")
        or inst.get("state")
        or "unclear"
    )


def labeled_dealing_range(raw: dict) -> DealingRange:
    m7 = raw.get("month7") or raw.get("ict_week") or {}
    explicit = m7.get("dealing_range") or raw.get("dealing_range") or {}
    frm = explicit.get("from_array_id")
    to = explicit.get("to_array_id")
    if not frm:
        origin = raw.get("origin_pd_array")
        if origin and _tf_from_id(origin) in {"monthly", "weekly"}:
            frm = origin
    if not to:
        targets = list(raw.get("opposing_target_arrays") or [])
        to = targets[0] if targets else None
    if not frm and not to:
        return DealingRange()
    direction = explicit.get("direction") or _direction(raw)
    if direction not in {"bullish", "bearish", "unclear"}:
        direction = "unclear"
    return DealingRange(
        from_array_id=frm,
        from_tf=explicit.get("from_tf") or _tf_from_id(frm),
        to_array_id=to,
        to_tf=explicit.get("to_tf") or _tf_from_id(to),
        direction=direction,
        origin="ict_source",
    )


def labeled_ipda(raw: dict) -> IpdaWindow:
    m7 = raw.get("month7") or raw.get("ict_week") or {}
    block = m7.get("ipda_window") if isinstance(m7.get("ipda_window"), dict) else {}
    days = block.get("days") if block else m7.get("ipda_window")
    if days is None:
        days = raw.get("ipda_days")
    if days not in (20, 40, 60):
        days = None
    return IpdaWindow(days=days, origin="ict_source")


def derive_month7_range(raw: dict) -> Month7State:
    base = parse_month7(raw) or Month7State()
    return Month7State(
        dealing_range=labeled_dealing_range(raw),
        ict_weekly_profile=IctWeeklyProfile(),
        manipulation_template=ManipulationTemplate(),
        ipda_window=labeled_ipda(raw),
        lrlr=Lrlr(),
        intraweek_contrary=IntraweekContrary(),
        osok_opportunity=OsokOpportunity(),
        swing_ticket=None,
        ict_guidance=base.ict_guidance,
    )
```

Prefix TF inference (`M_` / `W_` / `D_` / `H4`) is Hermes convenience, same idea as M8 HTF prefix.

IPDA days are **labeled** (20/40/60). Slice 2 does not pick a window from volatility.

---

## 2. Evidence fixture — `fixtures/m7_evidence_eurusd.json`

No `ict_weekly_profile` key.

```json
{
  "symbol": "EURUSD",
  "date": "2017-03-15",
  "focus_pair": "EURUSD",
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
    "notes": "M7 evidence Slice 2. Labeled arrays only. No weekly profile."
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

## 3. Test — `test_month7_slice2_range`

```python
def test_month7_slice2_range():
    raw = json.loads((ROOT / "fixtures/m7_evidence_eurusd.json").read_text())
    st = derive_month7_range(raw)
    assert st.dealing_range.from_array_id == "M_DISCOUNT"
    assert st.dealing_range.to_array_id == "W_PREMIUM"
    assert st.dealing_range.direction == "bullish"
    assert st.ipda_window.days == 20
    assert st.ict_weekly_profile.name == "none"
    assert st.osok_opportunity.flag is False
    assert st.swing_ticket is None
    raw2 = json.loads((ROOT / "fixtures/m7_reconstruction_eurusd.json").read_text())
    st2 = derive_month7_range(raw2)
    assert st2.ict_weekly_profile.name == "none"
```

Known-state provided profile is **stripped** by Slice 2 derive. `parse_month7` still returns it for schema tests.

---

## 4. What Slice 2 does not do

- Does not watch Tuesday/Wednesday path  
- Does not set LRLR from price  
- Does not mint `swing_ticket`  
- Does not attach `month7` in DTR  

---

## 5. Next permitted

Slice 3 — weekly profile from week-to-date path + HTF bias.  
`derive_month7_range` on a path fixture must still return `none`.
