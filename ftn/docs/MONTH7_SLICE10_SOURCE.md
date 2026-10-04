# Month 7 Slice 10 — full source copy

Reconstruction freeze. No new detectors. Formalize the matrix already proven in Slices 2-9 and prove the engine never reads gold files.

Repo paths under `ftn-agent/`.

---

## What Slice 10 is

```
CASES_M7  →  derive_month7_osok + build_context
engine sources  →  must not mention *.expected.json
M8 CASES_M8 + M9 gold  →  still pass
```

Gold / `*.expected.json` remain harness-only. The test file may name them. `src/ftn/os/m7_*` (and DTR/briefing) may not.

Known-state `m7_reconstruction_eurusd.json` stays a schema fixture. It is not in this matrix.

---

## 1. Matrix — CASES_M7 in tests/test_reconstruction.py

```python
CASES_M7 = [
    ("m7_path_eurusd.json", "classic_tuesday_low_of_week", True, "low"),
    ("m7_evidence_eurusd.json", "none", False, "unclear"),
]
```

| Fixture | Path evidence | Profile | OSOK | LRLR |
|---------|---------------|---------|------|------|
| m7_path_eurusd.json | Tue low into HTF discount + LRLR low | classic_tuesday_low_of_week | true | low |
| m7_evidence_eurusd.json | labeled range + IPDA only | none | false | unclear |

Both fixtures have no `pick` / `expected_winner`.

---

## 2. test_month7_slice10_matrix

```python
def test_month7_slice10_matrix():
    import json
    from ftn.os.m7_osok import derive_month7_osok
    from ftn.os.dtr import build_context
    for name, prof, osok, lrlr in CASES_M7:
        raw = json.loads((ROOT / "fixtures" / name).read_text())
        assert "pick" not in raw and "expected_winner" not in raw
        st = derive_month7_osok(raw)
        assert st.ict_weekly_profile.name == prof, name
        assert st.osok_opportunity.flag is osok
        assert st.lrlr.state == lrlr
        ctx = build_context(ROOT / "fixtures" / name)
        assert ctx.month7 is not None
        assert ctx.month7.ict_weekly_profile.name == prof
```

Direct detector and DTR path must agree. DTR uses persist=False, so this test does not require a new swing file.

---

## 3. test_month7_engine_never_opens_gold

```python
def test_month7_engine_never_opens_gold():
    roots = [
        ROOT / "src/ftn/os/m7_contracts.py",
        ROOT / "src/ftn/os/m7_range.py",
        ROOT / "src/ftn/os/m7_profile.py",
        ROOT / "src/ftn/os/m7_template.py",
        ROOT / "src/ftn/os/m7_lrlr.py",
        ROOT / "src/ftn/os/m7_osok.py",
        ROOT / "src/ftn/os/m7_swing.py",
        ROOT / "src/ftn/os/dtr.py",
        ROOT / "src/ftn/os/briefing.py",
    ]
    for path in roots:
        txt = path.read_text()
        assert ".expected.json" not in txt, path.name
```

Static check: kernel source must not mention gold filenames.

---

## 4. Month 7 complete map

```
src/ftn/os/m7_contracts.py     S1  glossary + parse
src/ftn/os/m7_range.py         S2  dealing range + IPDA
src/ftn/os/m7_profile.py       S3  weekly profile from week_path
src/ftn/os/m7_template.py      S4  manipulation template
src/ftn/os/m7_lrlr.py          S5  LRLR label
src/ftn/os/m7_osok.py          S6  OSOK + contrary
src/ftn/os/m7_swing.py         S7  paper swing persist
src/ftn/os/dtr.py              S8  month7= attach (persist=False)
src/ftn/os/briefing.py         S9  ## Month 7
src/ftn/os/handoff.py          S9  market_state.month7
desk/index.html + js/app.js    S9  chips
tests/test_reconstruction.py   S10 CASES_M7
```

Invariant: Month 7 describes the week and may hold a paper swing. Month 9 still selects the session ticket.

---

## 5. What Slice 10 does not do

- No new fields
- No classifier edits
- No extra weekly-profile names (Thu/Fri/S&D stay glossary-only until a later path slice)
- Does not add OSOK to evaluate_candidates
- Does not close swing tickets
- Does not make ctx.month7 required for M8/M9

---

## 6. Status

S0-S10 complete. Next work is a new phase, not Month 7 Slice 11.
