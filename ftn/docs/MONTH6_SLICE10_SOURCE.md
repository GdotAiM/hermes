# Month 6 Slice 10 — full source copy

Reconstruction freeze. No new detectors. Formalize the matrix already proven in Slices 2–9 and prove the engine never reads gold files.

Repo paths under `ftn-agent/`.

---

## What Slice 10 is

```
CASES_M6  →  derive_month6 + build_context
engine sources  →  must not mention *.expected.json
M7 CASES_M7 + M8 CASES_M8 + M9 gold  →  still pass
```

Gold / `*.expected.json` remain harness-only. The test file may name them. `src/ftn/os/m6_*` (and DTR/briefing) may not.

Known-state `m6_reconstruction_xauusd.json` stays a schema fixture. It is **not** in this matrix.

---

## 1. Matrix — CASES_M6 in tests/test_reconstruction.py

```python
CASES_M6 = [
    ("m6_evidence_xauusd.json", "bull", "mw_bullish_daily_correcting", True, "incomplete"),
]
```

| Fixture | Family | Sequence | Opportunity | MD |
|---------|--------|----------|-------------|-----|
| m6_evidence_xauusd.json | bull | mw_bullish_daily_correcting | true | incomplete |

Fixture has no `pick` / `expected_winner`. MD incomplete is expected: seasonal is labeled, management / major-market are not.

---

## 2. test_month6_slice10_matrix

```python
def test_month6_slice10_matrix():
    import json
    from ftn.os.m6_opportunity import derive_month6
    from ftn.os.dtr import build_context
    for name, fam, seq, opp, md in CASES_M6:
        raw = json.loads((ROOT / "fixtures" / name).read_text())
        assert "pick" not in raw and "expected_winner" not in raw
        st = derive_month6(raw)
        assert st.swing_family == fam
        assert st.sequential_pattern.name == seq
        assert st.swing_opportunity.flag is opp
        assert st.million_dollar_swing.state == md
        ctx = build_context(ROOT / "fixtures" / name)
        assert ctx.month6 is not None
        assert ctx.month6.swing_family == fam
        assert ctx.month6.sequential_pattern.name == seq
```

Direct detector and DTR path must agree.

---

## 3. test_month6_engine_never_opens_gold

```python
def test_month6_engine_never_opens_gold():
    roots = [
        ROOT / "src/ftn/os/m6_contracts.py",
        ROOT / "src/ftn/os/m6_env.py",
        ROOT / "src/ftn/os/m6_evidence.py",
        ROOT / "src/ftn/os/m6_family.py",
        ROOT / "src/ftn/os/m6_risk.py",
        ROOT / "src/ftn/os/m6_md.py",
        ROOT / "src/ftn/os/m6_opportunity.py",
        ROOT / "src/ftn/os/dtr.py",
        ROOT / "src/ftn/os/briefing.py",
    ]
    for path in roots:
        txt = path.read_text()
        assert ".expected.json" not in txt, path.name
```

---

## 4. Month 6 complete map

```
src/ftn/os/m6_contracts.py     S1  glossary + parse
src/ftn/os/m6_env.py           S2  suitability + htf_draw
src/ftn/os/m6_evidence.py      S3  required vs confirming
src/ftn/os/m6_family.py        S4  M/W/D sequence
src/ftn/os/m6_risk.py          S5  risk frame
src/ftn/os/m6_md.py            S6  six-gate composite
src/ftn/os/m6_opportunity.py   S7  swing_opportunity
src/ftn/os/dtr.py              S8  month6= attach
src/ftn/os/briefing.py         S9  ## Month 6
src/ftn/os/handoff.py          S9  market_state.month6
desk/index.html + js/app.js    S9  chips
tests/test_reconstruction.py   S10 CASES_M6
```

Invariant: Month 6 describes the swing. Month 9 still selects the session ticket.

---

## 5. What Slice 10 does not do

- No new fields
- No extra sequences
- Does not add M6 to evaluate_candidates
- Does not persist paper_swing_m6
- Does not make ctx.month6 required for M7/M8/M9

---

## 6. Status

S0–S10 complete. Next work is a new phase, not Month 6 Slice 11.
