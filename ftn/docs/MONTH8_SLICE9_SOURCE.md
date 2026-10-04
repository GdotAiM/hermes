# Month 8 Slice 9 — full source copy

Reconstruction freeze. No new detectors. Formalize the matrix already proven in Slices 1–8 and prove the engine never reads gold files.

Repo paths under `ftn-agent/`.

---

## What Slice 9 is

```
CASES_M8  →  derive_month8_profile + build_context
engine sources  →  must not mention *.expected.json
M9 CASES matrix  →  still pass
```

Gold / `*.expected.json` remain **harness-only**. The test file may name them. `src/ftn/os/*` may not.

---

## 1. Matrix — `CASES_M8` in `tests/test_reconstruction.py`

```python
CASES_M8 = [
    # fixture, expect_profile, expect_gate
    ("m8_path_eurusd.json", "normal_protraction_sell", True),
    ("m8_s4_late_rally.json", "delayed_protraction_sell", True),
    ("m8_s4_late_rally_window_only.json", "delayed_protraction_sell", True),
    ("m8_s4_no_hh.json", "none", True),
    ("m8_s4_first_move_only.json", "none", True),
    ("m8_evidence_eurusd.json", "none", True),
]
```

| Fixture | Path evidence | Profile | Gate |
|---------|---------------|---------|------|
| `m8_path_eurusd.json` | up + HH + by 02:00 | `normal_protraction_sell` | allow |
| `m8_s4_late_rally.json` | up + HH + `move_started_by_0200=false` | `delayed_protraction_sell` | allow |
| `m8_s4_late_rally_window_only.json` | up + HH + window `02:00-05:00` only | `delayed_protraction_sell` | allow |
| `m8_s4_no_hh.json` | up + early, no HH | `none` | allow |
| `m8_s4_first_move_only.json` | `first_move=up` only | `none` | allow |
| `m8_evidence_eurusd.json` | no path | `none` | allow |

All six fixtures have **no** `pick` / `expected_winner` / `ict_london_profile` in the `month8` block (path/evidence/S4). Known-state `m8_reconstruction_eurusd.json` stays a schema fixture, not in this matrix.

---

## 2. `test_month8_slice9_matrix`

```python
def test_month8_slice9_matrix():
    import json
    from ftn.os.m8_profile import derive_month8_profile
    from ftn.os.dtr import build_context
    for name, prof, gate in CASES_M8:
        raw = json.loads((ROOT / "fixtures" / name).read_text())
        raw.setdefault("pair_institutional", {})["state"] = (
            raw.get("pair_institutional", {}).get("state") or "bearish"
        )
        assert "pick" not in raw and "expected_winner" not in raw
        st = derive_month8_profile(raw)
        assert st.ict_london_profile == prof, name
        assert st.london_session_gate.allowed is gate
        ctx = build_context(ROOT / "fixtures" / name)
        assert ctx.month8 is not None
        assert ctx.month8.ict_london_profile == prof
```

Direct detector **and** DTR path must agree.

---

## 3. `test_month8_engine_never_opens_gold`

```python
def test_month8_engine_never_opens_gold():
    from pathlib import Path
    roots = [
        ROOT / "src/ftn/os/m8_contracts.py",
        ROOT / "src/ftn/os/m8_detect.py",
        ROOT / "src/ftn/os/m8_profile.py",
        ROOT / "src/ftn/os/m8_project.py",
        ROOT / "src/ftn/os/m8_htf.py",
        ROOT / "src/ftn/os/dtr.py",
        ROOT / "src/ftn/os/briefing.py",
    ]
    for path in roots:
        txt = path.read_text()
        assert ".expected.json" not in txt, path.name
        assert "m8_path_eurusd.expected" not in txt
```

Static check: kernel source must not mention gold filenames.

Existing M9 tests already prove editing a gold file does not change engine output (`test_gold_edit_does_not_change_engine`).

---

## 4. Related gold files (harness only)

```
fixtures/m8_reconstruction_eurusd.expected.json   known-state schema
fixtures/m8_evidence_eurusd.expected.json         Slice 2 class/gate
fixtures/m8_path_eurusd.expected.json             Slice 3 profile
```

These are **not** imported by `derive_month8_profile` or `build_context`.

---

## 5. Month 8 complete map

```
src/ftn/os/m8_contracts.py     S1
src/ftn/os/m8_detect.py        S2
src/ftn/os/m8_profile.py       S3 + S4 classifier
src/ftn/os/m8_project.py       S5
src/ftn/os/m8_htf.py           S6
src/ftn/os/dtr.py              S7 month8= attach
src/ftn/os/briefing.py         S8 _month8_lines
src/ftn/os/handoff.py          S8 market_state.month8
desk/index.html + js/app.js    S8 chips
tests/test_reconstruction.py   S9 CASES_M8
```

Invariant: Month 8 describes the day. Month 9 still selects the paper ticket.

---

## 6. What Slice 9 does not do

- No new fields  
- No classifier edits  
- No 4-SD / news expansion  
- No live data  
- Does not add Month 8 as an `evaluate_candidates` module
