# Charter Slice 4 — DTR attach

Attaches DayContext.charter when charter / ict_charter / identified_pam / recognized_pams exists.
Uses derive_charter(). persist none. session_ticket unchanged.
Does not write Core M1–M12 or pair_institutional.
M9 fixture without Charter evidence stays charter None.

## Import

```python
from ftn.os.pam_recognize import derive_charter
        charter = derive_charter(raw_ch)
```

## Attach block

```python
    charter = None
    ch_ev = bool(
        raw.get("charter")
        or raw.get("ict_charter")
        or (raw.get("evidence") or {}).get("identified_pam")
        or (raw.get("evidence") or {}).get("recognized_pams")
    )
    if ch_ev:
        raw_ch = dict(raw)
        raw_ch["evidence"] = ev
        charter = derive_charter(raw_ch)
```

## Test

```python
def test_charter_slice4_dtr():
    from ftn.os.dtr import build_context
    ctx = build_context(ROOT / "fixtures/charter_evidence_eurusd.json")
    assert ctx.charter is not None
    assert ctx.charter.recognized_pams[0].pam_id == "pam1"
    assert ctx.charter.charter_recognition.flag is True
    assert ctx.session_ticket is None
    ctx9 = build_context(ROOT / "fixtures/m9_reconstruction_eurusd.json")
    assert ctx9.charter is None



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
    test_month11_slice1_schema()
    test_month12_slice1_schema()
    test_charter_slice1_schema()
    test_charter_slice2_context()
    test_charter_slice3_recognition()
    test_charter_slice4_dtr()
    test_month12_slice2_context()
    test_month12_slice3_flag()
    test_month12_slice4_dtr()
    test_month12_slice5_brief()
    test_month12_slice6_matrix()
    test_month12_engine_never_opens_gold()
    test_month11_slice2_context()
    test_month11_slice3_flag()
    test_month11_slice4_dtr()
    test_month11_slice5_brief()
    test_month11_slice6_matrix()
    test_month11_engine_never_opens_gold()
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
