# Month 4 Slice 6 — full source copy

Reconstruction freeze. No new detectors. Formalize S2–S5 and prove the engine never reads gold files.

Repo paths under `ftn-agent/`.

---

## What Slice 6 is

```
CASES_M4  →  derive_month4 + build_context
engine sources  →  must not mention *.expected.json
M5–M9 golds     →  still pass
```

Gold / `*.expected.json` remain harness-only.

Known-state `m4_reconstruction_eurusd.json` stays a schema fixture. It is **not** in this matrix.

---

## 1. Matrix

```python
CASES_M4 = [
    ("m4_evidence_eurusd.json", ("fvg", "liquidity_void"), "double_bottom", True),
]
```

| Fixture | Catalog | Pattern | Opp | Ticket |
|---------|---------|---------|-----|--------|
| m4_evidence_eurusd.json | fvg, liquidity_void | double_bottom | true | none |

No `pick` / `expected_winner`. Rates remain false on this fixture; opportunity is still true.

---

## 2. Tests

```python
def test_month4_slice6_matrix():
    import json
    from ftn.os.m4_opportunity import derive_month4
    from ftn.os.dtr import build_context
    for name, kinds, note, opp in CASES_M4:
        raw = json.loads((ROOT / "fixtures" / name).read_text())
        assert "pick" not in raw and "expected_winner" not in raw
        st = derive_month4(raw)
        assert tuple(a.kind for a in st.arrays) == kinds
        assert st.pattern_note == note
        assert st.array_opportunity.flag is opp
        ctx = build_context(ROOT / "fixtures" / name)
        assert ctx.month4 is not None
        assert tuple(a.kind for a in ctx.month4.arrays) == kinds
        assert ctx.month4.array_opportunity.flag is opp
        assert ctx.session_ticket is None


def test_month4_engine_never_opens_gold():
    roots = [
        ROOT / "src/ftn/os/m4_contracts.py",
        ROOT / "src/ftn/os/m4_catalog.py",
        ROOT / "src/ftn/os/m4_opportunity.py",
        ROOT / "src/ftn/os/dtr.py",
        ROOT / "src/ftn/os/briefing.py",
    ]
    for path in roots:
        txt = path.read_text()
        assert ".expected.json" not in txt, path.name



if __name__ == "__main__":
    test_fixture_has_no_winner()
    test_reconstruct_matches_gold()
    test_gold_edit_does_not_change_engine(Path("/tmp"))
    test_rev_reads_market_state_only()
    test_all_reconstruction_cases()
    test_conso_fade_play_and_preemption()
    test_bb_engines()
    test_pip20_window_and_bb_suppress()
    test_session_ticket_one_per_session()
    test_dtr_derives_unlabeled_raw()
    test_wr_from_bars()
    test_raid_from_bars()
    test_mss_from_bars()
    test_box_from_bars()
    test_origin_from_arrays()
    test_calendar_focus()
    test_dxy_relationship()
    test_session_clocks()
    test_x_ask_read_only()
    test_mint_draft_paper()
    test_live_data_off_by_default()
    test_month8_contracts_and_fixture()
    test_month8_evidence_derives_gate()
    test_month8_slice2_does_not_name_profile()
    test_month8_profile_from_path()
    test_month8_expanded_gate_is_hermes()
    test_month8_slice4_regression()
    test_month8_slice5_projection()
    test_month8_slice6_htf()
    test_month8_slice7_dtr()
    test_month8_slice8_brief()
    test_month8_slice9_matrix()
    test_month8_engine_never_opens_gold()
    test_month7_slice1_schema()
    test_month7_slice2_range()
    test_month7_slice3_profile()
    test_month7_slice4_template()
    test_month7_slice5_lrlr()
    test_month7_slice6_osok()
    test_month7_slice7_swing()
    test_month7_slice8_dtr()
    test_month7_slice9_brief()
    test_month7_slice10_matrix()
    test_month7_engine_never_opens_gold()
    test_month6_slice1_schema()
    test_month5_slice1_schema()
    test_month4_slice1_schema()
    test_month4_slice2_catalog()
    test_month4_slice3_opportunity()
    test_month4_slice4_dtr()
    test_month4_slice5_brief()
    test_month4_slice6_matrix()
    test_month4_engine_never_opens_gold()
    test_month5_slice2_env()
    test_month5_slice3_float()
    test_month5_slice4_swing()
    test_month5_slice5_confirm()
    test_month5_slice6_pd()
    test_month5_slice7_setup()
    test_month5_slice8_opportunity()
    test_month5_slice9_dtr_brief()
    test_month5_slice10_matrix()
    test_month5_engine_never_opens_gold()
    test_month6_slice2_env()
    test_month6_slice3_evidence()
    test_month6_slice4_family()
    test_month6_slice5_risk()
    test_month6_slice6_md()
    test_month6_slice7_opportunity()
    test_month6_slice8_dtr()
    test_month6_slice9_brief()
    test_month6_slice10_matrix()
    test_month6_engine_never_opens_gold()
    print("all reconstruction tests ok")
```

Direct detector and DTR path must agree. `session_ticket` is None.

---

## 3. Month 4 complete map

```
src/ftn/os/m4_contracts.py     S1
src/ftn/os/m4_catalog.py       S2
src/ftn/os/m4_opportunity.py   S3
src/ftn/os/dtr.py              S4  month4= attach
src/ftn/os/briefing.py         S5  ## Month 4
src/ftn/os/handoff.py          S5  market_state.month4
desk/                          S5  chips
tests/test_reconstruction.py   S6  CASES_M4
```

Invariant: Month 4 describes the PD-array catalog. Month 9 still selects the session ticket.

---

## 4. What Slice 6 does not do

- No new kinds
- No paper_array_m4
- No evaluate_candidates row
- Does not make ctx.month4 required for M5–M9
- No Slice 7

---

## 5. Status

S0–S6 complete. Next work is a new phase, not Month 4 Slice 7.
