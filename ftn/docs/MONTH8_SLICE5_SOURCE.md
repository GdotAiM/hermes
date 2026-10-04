# Month 8 Slice 5 — full source copy

Daily extreme projection from CBDR standard deviations. Context only — not an entry, not a ticket.

Repo paths under `ftn-agent/`.

---

## What Slice 5 is

Lecture 4: project the day’s high or low from CBDR × 1 / 2 / 3 SD, **in the IOF direction**.

```
bearish IOF  →  draw = high   (sell day prints the high above CBDR)
bullish IOF  →  draw = low    (buy day prints the low below CBDR)
selected_level = 1 SD
origin = ict_source
```

Prefer **candle bodies**. Wicks only if bodies are missing.

Does **not**: pick a trade, change size, name a London profile, or wire DTR/desk.

---

## 1. `src/ftn/os/m8_project.py`

```python
"""Month-8 Slice 5: daily extreme projection from CBDR standard deviations.

Bearish IOF → project the day's HIGH above CBDR.
Bullish IOF → project the day's LOW below CBDR.
Selected level is context, not an entry.
"""

from __future__ import annotations

from ftn.os.m8_contracts import CbdrState, DailyExtremeProjection


def _height(cbdr: CbdrState) -> float | None:
    if cbdr.body_high is not None and cbdr.body_low is not None:
        return float(cbdr.body_high) - float(cbdr.body_low)
    if cbdr.height_pips is not None:
        return float(cbdr.height_pips) / 10000.0
    return None


def project_daily_extreme(cbdr: CbdrState, iof: str) -> DailyExtremeProjection:
    h = _height(cbdr)
    if h is None or h <= 0:
        return DailyExtremeProjection()
    if iof == "bearish":
        base = cbdr.body_high if cbdr.body_high is not None else None
        if base is None and cbdr.wick_high is not None:
            base = cbdr.wick_high
        if base is None:
            return DailyExtremeProjection()
        levels = tuple({"sd": n, "price": round(base + n * h, 5)} for n in (1, 2, 3))
        return DailyExtremeProjection(
            draw="high",
            sd_levels=levels,
            source_range="cbdr_bodies",
            selected_level=levels[0]["price"],
            basis=("bearish_iof", "sell_day_projects_high"),
            origin="ict_source",
        )
    if iof == "bullish":
        base = cbdr.body_low if cbdr.body_low is not None else None
        if base is None and cbdr.wick_low is not None:
            base = cbdr.wick_low
        if base is None:
            return DailyExtremeProjection()
        levels = tuple({"sd": n, "price": round(base - n * h, 5)} for n in (1, 2, 3))
        return DailyExtremeProjection(
            draw="low",
            sd_levels=levels,
            source_range="cbdr_bodies",
            selected_level=levels[0]["price"],
            basis=("bullish_iof", "buy_day_projects_low"),
            origin="ict_source",
        )
    return DailyExtremeProjection()
```

---

## 2. Contract already frozen (`m8_contracts.py`)

```python
@dataclass(frozen=True)
class DailyExtremeProjection:
    draw: Draw = "none"          # high | low | none
    sd_levels: tuple = ()
    source_range: str = "cbdr"
    selected_level: Optional[float] = None
    basis: tuple = ()
    origin: str = "ict_source"
```

No contract change in Slice 5.

---

## 3. Wiring — `derive_month8_profile` in `m8_profile.py`

Slice 5 is **not** inside the Slice 2 gate detector. Projection is attached when the profile layer runs, from CBDR + IOF only (path is irrelevant to SD math).

```python
from ftn.os.m8_project import project_daily_extreme

def derive_month8_profile(raw: dict) -> Month8State:
    base = derive_month8_measures(raw)
    path = read_path(raw)
    iof = _iof(raw)
    profile, why = classify_london_profile(iof, path, base.london_session_gate.allowed)
    proj = project_daily_extreme(base.cbdr, iof)
    return Month8State(
        ...
        daily_extreme_projection=proj,
        ...
    )
```

On the evidence fixture (no path) you still get a projection if IOF + CBDR exist. Profile stays `none`. That is intended: projection is a range objective, not a profile.

---

## 4. Numbers on the path fixture

Bodies: high `1.0606`, low `1.0582` → height `0.0024` (24 pips).  
IOF bearish → highs:

| SD | Price |
|----|-------|
| 1 | **1.06300** (`selected_level`) |
| 2 | 1.06540 |
| 3 | 1.06780 |

Bullish mirror on the same bodies: `draw=low`, 1 SD = `1.0582 − 0.0024 = 1.05580`.

The Slice 1 known-state fixture had `1.0634` as a *provided* label (different height basis). Slice 5 **recomputes** from bodies and does not read that gold field.

---

## 5. Test — `test_month8_slice5_projection`

```python
def test_month8_slice5_projection():
    import json
    from ftn.os.m8_profile import derive_month8_profile
    from ftn.os.m8_project import project_daily_extreme
    from ftn.os.m8_contracts import CbdrState
    raw = json.loads((ROOT / "fixtures/m8_path_eurusd.json").read_text())
    st = derive_month8_profile(raw)
    assert st.daily_extreme_projection.draw == "high"
    assert st.daily_extreme_projection.selected_level == 1.063
    assert st.daily_extreme_projection.origin == "ict_source"
    bull = project_daily_extreme(
        CbdrState(body_high=1.0606, body_low=1.0582, height_pips=24, classification="ideal"),
        "bullish",
    )
    assert bull.draw == "low" and bull.selected_level == 1.0558
```

Passes. Slice 4 regression still passes.

---

## 6. What Slice 5 does not do

- Does not set `daytrade_opportunity` from projection alone  
- Does not emit a session ticket  
- Does not implement 4 SD / news expansion  
- Does not mix Asian range into the SD stack (source is CBDR bodies)  
- Does not wire `build_context` or the desk  

Those stay Slices 6–8.

---

## 7. Next permitted

Slice 6 — HTF overlap annotate (`seed_only`, no size).
