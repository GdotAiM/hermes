# Month 6 Slice 8 — full source copy

DTR attaches `DayContext.month6` when swing/monthly evidence exists.
No persist file. No `session_ticket`. M7/M8/M9 golds unchanged.

Repo paths under `ftn-agent/`.

---

## What Slice 8 is

```
raw
 ↓
existing DTR (M9 + M8 + M7)
 ↓
swing evidence?
    ├── month6 / ict_swing
    ├── pair_institutional.sponsorship.monthly
    └── origin starts with M_
         ↓ yes
    derive_month6(raw_m6)
         ↓
    replace(ctx, month6=..., month7=..., month8=...)
```

`derive_month6` is the S7 pipeline (env → evidence → family → risk → MD → opportunity). DTR does not write a swing file.

---

## 1. Import — `src/ftn/os/dtr.py`

```python
from ftn.os.m6_opportunity import derive_month6
```

---

## 2. Attach block

```python
    month6 = None
    inst_sp = ((raw.get("pair_institutional") or {}).get("sponsorship") or {})
    swing_ev = bool(
        raw.get("month6")
        or raw.get("ict_swing")
        or inst_sp.get("monthly")
        or str(origin or raw.get("origin_pd_array") or "").startswith("M_")
    )
    if swing_ev:
        raw_m6 = dict(raw)
        raw_m6["evidence"] = ev
        if origin:
            raw_m6["origin_pd_array"] = origin
        month6 = derive_month6(raw_m6)
    month7 = None
    # existing weekly_ev / month8 blocks unchanged
    return replace(
        ctx,
        ...
        month8=month8,
        month7=month7,
        month6=month6,
    )
```

Shallow copy + resolved origin, same pattern as M7/M8.

Note: `M_` origin also still qualifies M7 `weekly_ev`. That is acceptable: M6 and M7 may both attach. They remain separate fields.

---

## 3. Test — `test_month6_slice8_dtr`

```python
def test_month6_slice8_dtr():
    from ftn.os.dtr import build_context
    ctx = build_context(ROOT / "fixtures/m6_evidence_xauusd.json")
    assert ctx.month6 is not None
    assert ctx.month6.swing_family == "bull"
    assert ctx.month6.swing_opportunity.flag is True
    assert ctx.session_ticket is None
    ctx9 = build_context(ROOT / "fixtures/m9_reconstruction_eurusd.json")
    assert ctx9.profile in {
        "expansion", "consolidation", "reversal_watch", "continuation", "unclear"
    }
```

Also required: `test_reconstruct_matches_gold`, `test_month7_slice10_matrix`, `test_month8_slice9_matrix` — all pass.

---

## 4. What Slice 8 does not do

- No briefing section (Slice 9)
- No desk chips (Slice 9)
- No persist / paper_swing_m6
- No `evaluate_candidates` row
- Does not require `ctx.month6` on M9 fixtures

---

## 5. Next permitted

Slice 9 — `## Month 6` briefing + desk chips. Display only.
