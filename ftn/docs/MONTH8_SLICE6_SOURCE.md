# Month 8 Slice 6 — full source copy

HTF overlap annotation. Lecture 8: the same day-trade idea can seed an HTF position. It does **not** change size, caps, candidate priority, or session tickets.

Repo paths under `ftn-agent/`.

---

## What Slice 6 is

```
origin_pd_array (or first daily matrix id)
        ↓
HtfOverlap(
  present=true,
  array_id=...,
  timeframe=daily|weekly|monthly,
  relationship="seed_only",
  origin="ict_source",
)
```

No array → `HtfOverlap()` defaults (`present=false`).

`daytrade_opportunity` is still only: named London profile **and** gate allowed. Overlap does not turn it on.

---

## 1. `src/ftn/os/m8_htf.py`

```python
"""Month-8 Slice 6: HTF overlap annotation.

Marks when the day-trade idea sits on an HTF PD array.
Never changes size, caps, candidate priority, or session tickets.
"""

from __future__ import annotations

from ftn.os.m8_contracts import HtfOverlap


def annotate_htf_overlap(raw: dict) -> HtfOverlap:
    origin = raw.get("origin_pd_array")
    if not origin:
        daily = (((raw.get("pd_matrix") or {}).get("htf") or {}).get("daily") or [])
        if daily:
            first = daily[0]
            origin = first.get("id") if isinstance(first, dict) else None
    if not origin:
        return HtfOverlap()
    # relationship is always seed_only — lecture 8, signed essence
    tf = "daily"
    if isinstance(origin, str) and origin.startswith("W_"):
        tf = "weekly"
    elif isinstance(origin, str) and origin.startswith("M_"):
        tf = "monthly"
    return HtfOverlap(
        present=True,
        array_id=str(origin),
        timeframe=tf,
        relationship="seed_only",
        origin="ict_source",
    )
```

Timeframe inference is prefix-only (`D_` default daily, `W_`, `M_`). That is Hermes convenience, not an ICT taxonomy.

---

## 2. Contract already frozen (`m8_contracts.py`)

```python
@dataclass(frozen=True)
class HtfOverlap:
    present: bool = False
    array_id: Optional[str] = None
    timeframe: Optional[str] = None
    relationship: Optional[str] = None
    origin: str = "ict_source"
```

No contract change in Slice 6. `relationship` is always `"seed_only"` when present.

---

## 3. Wiring — `derive_month8_profile`

```python
from ftn.os.m8_htf import annotate_htf_overlap

def derive_month8_profile(raw: dict) -> Month8State:
    base = derive_month8_measures(raw)
    path = read_path(raw)
    iof = _iof(raw)
    profile, why = classify_london_profile(iof, path, base.london_session_gate.allowed)
    proj = project_daily_extreme(base.cbdr, iof)
    return Month8State(
        ict_true_day=base.ict_true_day,
        cbdr=base.cbdr,
        asian_height_pips=base.asian_height_pips,
        london_session_gate=base.london_session_gate,
        ict_london_profile=profile,
        daily_extreme_projection=proj,
        daytrade_opportunity=profile != "none" and base.london_session_gate.allowed,
        htf_entry_overlap=annotate_htf_overlap(raw),
        ict_guidance=base.ict_guidance,
    )
```

Overlap is read from **raw Market State** (`origin_pd_array`), not from the London profile. A day can have HTF seed and `profile=none`.

---

## 4. Path fixture result

`origin_pd_array`: `"D_FVG_bear"`

```
HtfOverlap(
  present=True,
  array_id='D_FVG_bear',
  timeframe='daily',
  relationship='seed_only',
  origin='ict_source',
)
```

Empty raw `{}` → `present=False`.

---

## 5. Test — `test_month8_slice6_htf`

```python
def test_month8_slice6_htf():
    import json
    from ftn.os.m8_profile import derive_month8_profile
    from ftn.os.m8_htf import annotate_htf_overlap
    raw = json.loads((ROOT / "fixtures/m8_path_eurusd.json").read_text())
    st = derive_month8_profile(raw)
    assert st.htf_entry_overlap.present is True
    assert st.htf_entry_overlap.relationship == "seed_only"
    assert st.htf_entry_overlap.array_id == "D_FVG_bear"
    assert annotate_htf_overlap({}).present is False
```

Passes. Slice 4 and 5 tests still pass.

---

## 6. What Slice 6 does not do

- No `size_mult`, no lot field, no cap change  
- Does not reorder REV / CONSO / PIP20 / BB  
- Does not write `session_ticket`  
- Does not require a named London profile  
- Does not wire `dtr.build_context` (that is Slice 7)

---

## 7. Next permitted

Slice 7 — hang `month8=derive_month8_profile(raw)` on DTR `DayContext`. M9 reconstruction golds must still pass.
