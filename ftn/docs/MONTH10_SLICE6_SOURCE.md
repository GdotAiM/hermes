# Month 10 Slice 6 — reconstruction freeze

CASES_M10

| Fixture | Identified | Asset | Flag | Ticket |
|---------|------------|-------|------|--------|
| m10_evidence_eurusd.json | present | index | true | none |

Direct derive_month10() and DTR must agree.
Engine m10_* / dtr / briefing must not mention *.expected.json.
Known-state m10_reconstruction_eurusd.json stays schema-only.

Month 10 S0–S6 complete. Multi-asset annotation. No Slice 7.
Does not write M5 confirming or M6 gates.

```python
CASES_M10 = [
    ("m10_evidence_eurusd.json", "present", "index", True),
]
```

```python
def test_month10_slice6_matrix():
    import json
    from ftn.os.m10_confluence import derive_month10
    from ftn.os.dtr import build_context
    for name, ident, asset, flag in CASES_M10:
        raw = json.loads((ROOT / "fixtures" / name).read_text())
        assert "pick" not in raw and "expected_winner" not in raw
        st = derive_month10(raw)
        assert st.identified_multi_asset == ident
        assert st.asset_class == asset
        assert st.multi_asset_context.flag is flag
        ctx = build_context(ROOT / "fixtures" / name)
        assert ctx.month10 is not None
        assert ctx.month10.multi_asset_context.flag is flag
        assert ctx.session_ticket is None


def test_month10_engine_never_opens_gold():
    roots = [
        ROOT / "src/ftn/os/m10_contracts.py",
        ROOT / "src/ftn/os/m10_context.py",
        ROOT / "src/ftn/os/m10_confluence.py",
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
    test_month2_slice1_schema()
    test_month1_slice1_schema()
    test_month10_slice1_schema()
    test_month10_slice2_context()
    test_month10_slice3_flag()
    test_month10_slice4_dtr()
    test_month10_slice5_brief()
    test_month10_slice6_matrix()
    test_month10_engine_never_opens_gold()
    test_month1_slice2_context()
    test_month1_slice3_setup()
    test_month1_slice4_dtr()
    test_month1_slice5_brief()
    test_month1_slice6_matrix()
    test_month1_engine_never_opens_gold()
    test_integration_i2_attach()
    test_integration_i3_ticket_isolation()
    test_integration_i4_brief()
    test_integration_i5_golds()
    test_month2_slice2_context()
    test_month2_slice3_frame()
    test_month2_slice4_dtr()
    test_month2_slice5_brief()
    test_month2_slice6_matrix()
    test_month2_engine_never_opens_gold()
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
