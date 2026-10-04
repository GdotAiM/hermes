# Month 7 Slice 8 — full source copy

DTR attaches DayContext.month7 when weekly evidence exists.
persist=False — DTR does not write swing files.
Does not write session_ticket. M8/M9 golds unchanged.

## Attach block in src/ftn/os/dtr.py

```python
from ftn.os.m7_swing import derive_month7_swing

    month7 = None
    ev_path = (ev.get("week_path") or raw.get("week_path"))
    origin_tf = str(origin or raw.get("origin_pd_array") or "")
    weekly_ev = bool(
        raw.get("month7")
        or raw.get("ict_week")
        or ev_path
        or raw.get("ipda_days")
        or origin_tf.startswith("W_")
        or origin_tf.startswith("M_")
    )
    if weekly_ev:
        raw_m7 = dict(raw)
        raw_m7["evidence"] = ev
        if origin:
            raw_m7["origin_pd_array"] = origin
        month7 = derive_month7_swing(raw_m7, persist=False)
    # month8 block unchanged
    return replace(..., month8=month8, month7=month7)
```

## Test

Path fixture through DTR: classic_tuesday_low_of_week, OSOK true, session_ticket None.
M9 reconstruction gold still matches.

## Next

Slice 9 briefing + desk chips.
