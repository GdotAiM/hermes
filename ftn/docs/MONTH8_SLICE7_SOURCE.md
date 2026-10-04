# Month 8 Slice 7 — full source copy

DTR wiring only. Month 8 hangs on `DayContext.month8`. M9 construction is unchanged.

Repo paths under `ftn-agent/`.

---

## What Slice 7 is

```
raw
 │
 ▼
existing build_context()
 │
 ├── M9: institutional, sentiment, Hermes profile, raid/MSS/box, DXY, origin
 │
 └── Month 8 available?
        │
        ├── yes → month8 = derive_month8_profile(raw + updated evidence + origin)
        └── no  → month8 = None
```

Available means any of:

- `raw["month8"]`
- `raw["ict_day"]`
- `raw["ranges"]["cbdr"]`

Most M9 fixtures *have* a CBDR range box, so they get a Month8State. That is allowed. What is **not** allowed is changing M9 gold fields (sentiment, Hermes profile, IOF, origin, candidate states).

---

## 1. Import in `src/ftn/os/dtr.py`

```python
from ftn.os.m8_profile import derive_month8_profile
```

All other M9 imports unchanged.

---

## 2. Attachment before `replace`

```python
    month8 = None
    if raw.get("month8") or raw.get("ict_day") or (raw.get("ranges") or {}).get("cbdr"):
        raw_m8 = dict(raw)
        raw_m8["evidence"] = ev
        if origin:
            raw_m8["origin_pd_array"] = origin
        month8 = derive_month8_profile(raw_m8)
    return replace(
        ctx,
        pair_institutional=inst,
        sentiment=sent,
        profile=profile,
        evidence=ev,
        origin_pd_array=origin,
        opposing_target_arrays=tuple(targets),
        focus_pair=focus["focus_pair"] or ctx.focus_pair or raw.get("symbol") or "",
        dxy=dxy,
        month8=month8,
    )
```

`raw_m8` is a shallow copy so DTR evidence (raid/MSS/box) and the resolved `origin_pd_array` reach Slice 6 HTF annotate and Slice 3 path read. The original `raw` dict is not mutated.

`replace(..., month8=month8)` overwrites whatever `load_day_context` parsed from a known-state `month8` block. Detector output wins over provided state when DTR runs.

---

## 3. Test — `test_month8_slice7_dtr`

```python
def test_month8_slice7_dtr():
    from ftn.os.dtr import build_context
    ctx = build_context(ROOT / "fixtures/m8_path_eurusd.json")
    assert ctx.month8 is not None
    assert ctx.month8.ict_london_profile == "normal_protraction_sell"
    ctx9 = build_context(ROOT / "fixtures/m9_reconstruction_eurusd.json")
    assert ctx9.profile in {
        "expansion", "consolidation", "reversal_watch", "continuation", "unclear"
    }
```

Also still required: `test_reconstruct_matches_gold` and the full CASES matrix. Those passed after this wire.

---

## 4. What Slice 7 does not do

- Does not add a Month-8 candidate to `evaluate_candidates`  
- Does not change arbiter order  
- Does not write briefing text or desk chips (Slice 8)  
- Does not require Month 8 to construct `DayContext`  
- Does not freeze `month8` into M9 gold files  

---

## 5. Next permitted

Slice 8 — briefing section `## Month 8 (ICT day)` + desk chips. Not a second desk.
