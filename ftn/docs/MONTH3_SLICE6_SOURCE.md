# Month 3 Slice 6 — full source copy

Reconstruction freeze. No new detectors.

Repo paths under `ftn-agent/`.

---

## What Slice 6 is

```
CASES_M3  →  derive_month3 + build_context
engine sources  →  must not mention *.expected.json
M4–M9 golds     →  still pass
```

Known-state `m3_reconstruction_eurusd.json` is schema-only. Not in this matrix.

---

## 1. Matrix

```python
CASES_M3 = [
    ("m3_evidence_eurusd.json", "monthly", "present", True),
]
```

| Fixture | TF | Anticipated | Next | Ticket |
|---------|----|-------------|------|--------|
| m3_evidence_eurusd.json | monthly | present | true | none |

No `pick` / `expected_winner`.

---

## 2. Tests

```python
def test_month3_slice6_matrix():
    import json
    from ftn.os.m3_setup import derive_month3
    from ftn.os.dtr import build_context
    for name, tf, ant, nxt in CASES_M3:
        raw = json.loads((ROOT / "fixtures" / name).read_text())
        assert "pick" not in raw and "expected_winner" not in raw
        st = derive_month3(raw)
        assert st.selected_timeframe == tf
        assert st.anticipated_setup == ant
        assert st.next_setup.flag is nxt
        ctx = build_context(ROOT / "fixtures" / name)
        assert ctx.month3 is not None
        assert ctx.month3.next_setup.flag is nxt
        assert ctx.session_ticket is None


def test_month3_engine_never_opens_gold():
    roots = [
        ROOT / "src/ftn/os/m3_contracts.py",
        ROOT / "src/ftn/os/m3_context.py",
        ROOT / "src/ftn/os/m3_setup.py",
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
    test_month3_slice1_schema()
    test_month3_slice2_context()
    test_month3_slice3_setup()
    test_month3_slice4_dtr()
    test_month3_slice5_brief()
    test_month3_slice6_matrix()
    test_month3_engine_never_opens_gold()
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

---

## 3. Month 3 complete map

```
src/ftn/os/m3_contracts.py     S1
src/ftn/os/m3_context.py       S2
src/ftn/os/m3_setup.py         S3
src/ftn/os/dtr.py              S4  month3= attach
src/ftn/os/briefing.py         S5  ## Month 3
src/ftn/os/handoff.py          S5  market_state.month3
desk/                          S5  chips
tests/test_reconstruction.py   S6  CASES_M3
```

Invariant: Month 3 describes institutional context and anticipation.
Month 9 still selects the session ticket. M3 never writes pair_institutional.

---

## 4. What Slice 6 does not do

- No new fields
- No paper_setup_m3
- No evaluate_candidates row
- Does not make ctx.month3 required for M4–M9
- No Slice 7

---

## 5. Status

S0–S6 complete. Next work is a new phase, not Month 3 Slice 7.
