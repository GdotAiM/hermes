# Month 4 Slice 4 — full source copy

DTR attach only. Display is Slice 5. No candidate, ticket, size, persist.

Repo paths under `ftn-agent/`.

---

## What Slice 4 is

```
raw
 ↓
existing DTR (M9 + M8 + M7 + M6 + M5)
 ↓
catalog evidence?
    ├── month4
    ├── ict_arrays
    ├── evidence.arrays
    └── raw.arrays
         ↓ yes
    derive_month4(raw_m4)   # S3 pipeline
         ↓
    replace(ctx, month4=...)
```

DTR is a context assembler. It does not write a paper file.

---

## 1. Import — src/ftn/os/dtr.py

```python
from ftn.os.m4_opportunity import derive_month4
```

---

## 2. Attach block

```python
    month4 = None
    arr_ev = bool(
        raw.get("month4")
        or raw.get("ict_arrays")
        or (raw.get("evidence") or {}).get("arrays")
        or raw.get("arrays")
    )
    if arr_ev:
        raw_m4 = dict(raw)
        raw_m4["evidence"] = ev
        if origin:
            raw_m4["origin_pd_array"] = origin
        month4 = derive_month4(raw_m4)
```

Shallow copy + resolved origin. Same pattern as M5–M8.

`replace(..., month4=month4)`.

---

## 3. Evidence gate

M4 attaches only when a catalog block exists.

An ordinary M9 fixture without `arrays` continues with:

```
DayContext.month4 is None
  or month4.arrays == ()
```

M4 remains optional. M9 gold must stay valid.

---

## 4. Test — test_month4_slice4_dtr

```python
ctx = build_context(ROOT / "fixtures/m4_evidence_eurusd.json")
assert ctx.month4 is not None
assert [a.kind for a in ctx.month4.arrays] == ["fvg", "liquidity_void"]
assert ctx.month4.array_opportunity.flag is True
assert ctx.session_ticket is None
ctx9 = build_context(ROOT / "fixtures/m9_reconstruction_eurusd.json")
assert ctx9.month4 is None or ctx9.month4.arrays == ()
```

Coexistence preserved. Opportunity true. Ticket none.

---

## 5. What Slice 4 does not do

- No `_month4_lines` briefing
- No desk chips
- No handoff `month4` key (Slice 5)
- No CASES_M4 freeze
- No persist / paper_array_m4
- No evaluate_candidates row

---

## Next permitted

Slice 5 — briefing + handoff + desk. Display only.
