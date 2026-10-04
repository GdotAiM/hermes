# Month 2 Slice 4 — full source copy

DTR attach only. Display is Slice 5. There is no Month 2 Slice 9.

Repo paths under `ftn-agent/`.

---

## What Slice 4 is

```
raw
 ↓
existing DTR
 ↓
risk-frame evidence?
    ├── month2
    ├── ict_risk
    ├── evidence.identified_low_risk_frame
    └── evidence.identified_high_reward_context
         ↓ yes
    derive_month2(raw_m2)   # S3 pipeline
         ↓
    replace(ctx, month2=...)
```

DTR is a context assembler. It does not write a paper file.
M2 does not write M6 RiskFrame.

---

## 1. Import

```python
from ftn.os.m2_frame import derive_month2
        month2 = derive_month2(raw_m2)
```

---

## 2. Attach block

```python
    month2 = None
    risk_ev = bool(
        raw.get("month2")
        or raw.get("ict_risk")
        or (raw.get("evidence") or {}).get("identified_low_risk_frame")
        or (raw.get("evidence") or {}).get("identified_high_reward_context")
    )
    if risk_ev:
        raw_m2 = dict(raw)
        raw_m2["evidence"] = ev
        month2 = derive_month2(raw_m2)
```

---

## 3. Evidence gate

Attachment ≠ flag. One identification field can attach M2 with `low_risk_frame=false`.

M9 fixture without those keys → `DayContext.month2 is None`.

---

## 4. Test — test_month2_slice4_dtr

```python
def test_month2_slice4_dtr():
    from ftn.os.dtr import build_context
    ctx = build_context(ROOT / "fixtures/m2_evidence_eurusd.json")
    assert ctx.month2 is not None
    assert ctx.month2.low_risk_frame.flag is True
    assert ctx.session_ticket is None
    ctx9 = build_context(ROOT / "fixtures/m9_reconstruction_eurusd.json")
    assert ctx9.month2 is None



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
    test_month2_slice2_context()
    test_month2_slice3_frame()
    test_month2_slice4_dtr()
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

## 5. What Slice 4 does not do

- No briefing / desk / handoff (Slice 5)
- No CASES_M2 freeze (Slice 6)
- No persist / lots / ticket

---

## Next permitted

Slice 5 — briefing + handoff + desk. Display only.
