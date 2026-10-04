# Month 8 Slice 3 — full source copy

Everything that landed for Slice 3 (profile from post-00:00 path) plus the 40/50 provenance patch Slice 3 depends on.

Repo paths are under `ftn-agent/`.

---

## What Slice 3 is

```
Slice 2: CBDR class + London gate
Slice 3: IOF + path_after_anchor (NY 00:00) → ict_london_profile
```

Ideal CBDR + bearish IOF **without a path** must stay `none`.

---

## 1. `src/ftn/os/m8_profile.py`

```python
"""Month-8 Slice 3: ICT London profile from post-00:00 NY path + IOF.

Ideal CBDR + bearish IOF alone must not name a profile.
"""

from __future__ import annotations

from ftn.os.m8_contracts import Month8State, LondonProfile
from ftn.os.m8_detect import derive_month8_measures


def _iof(raw: dict) -> str:
    inst = raw.get("pair_institutional") or {}
    return inst.get("state") or (inst.get("daytrade_iof") or {}).get("daily") or "unclear"


def read_path(raw: dict) -> dict:
    ev = raw.get("evidence") or {}
    path = ev.get("path_after_anchor") or raw.get("path_after_anchor") or {}
    return {
        "anchor": path.get("anchor") or "00:00",
        "first_move": path.get("first_move"),  # up | down | none
        "window": path.get("window") or "",
        "higher_high_vs_asian_or_cbdr": bool(path.get("higher_high_vs_asian_or_cbdr")),
        "lower_low_vs_asian_or_cbdr": bool(path.get("lower_low_vs_asian_or_cbdr")),
        "move_started_by_0200": path.get("move_started_by_0200"),
    }


def classify_london_profile(iof: str, path: dict, gate_allowed: bool) -> tuple[str, str]:
    if not gate_allowed:
        return "none", "london_not_allowed"
    first = path.get("first_move")
    if not first or first == "none":
        return "none", "no_post_anchor_path"
    early = path.get("move_started_by_0200")
    if early is None:
        early = path.get("window") in {"00:00-02:00", "00:00-02:00 NY"}
    if iof == "bearish" and first == "up":
        if path.get("higher_high_vs_asian_or_cbdr") and early:
            return "normal_protraction_sell", "post_anchor_rally_then_iof"
        return "delayed_protraction_sell", "bearish_iof_without_classic_early_rally"
    if iof == "bullish" and first == "down":
        if path.get("lower_low_vs_asian_or_cbdr") and early:
            return "normal_protraction_buy", "post_anchor_decline_then_iof"
        return "delayed_protraction_buy", "bullish_iof_without_classic_early_decline"
    return "none", "path_does_not_match_iof"


def derive_month8_profile(raw: dict) -> Month8State:
    base = derive_month8_measures(raw)
    path = read_path(raw)
    profile, why = classify_london_profile(_iof(raw), path, base.london_session_gate.allowed)
    return Month8State(
        ict_true_day=base.ict_true_day,
        cbdr=base.cbdr,
        asian_height_pips=base.asian_height_pips,
        london_session_gate=base.london_session_gate,
        ict_london_profile=profile,  # type: ignore[arg-type]
        daily_extreme_projection=base.daily_extreme_projection,
        daytrade_opportunity=profile != "none" and base.london_session_gate.allowed,
        htf_entry_overlap=base.htf_entry_overlap,
        ict_guidance=base.ict_guidance,
    )
```

`why` is computed but not stored on `Month8State` yet.

---

## 2. Gate provenance patch in `src/ftn/os/m8_detect.py`

Required so Slice 3 does not inherit a silent 40–50 hard law as ICT.

```python
def london_gate_from_measures(cbdr: CbdrState, asian_pips: float | None, adr_remaining=None, news: bool = False) -> LondonGate:
    """Wide (>=50) is ICT-source avoidance. Expanded (40-<50) refuse-classic is Hermes interpretation."""
    if news:
        return LondonGate(allowed=False, reason="news", origin="ict_source")
    if cbdr.classification == "wide":
        return LondonGate(allowed=False, reason="wide_cbdr", origin="ict_source")
    if asian_pips is not None and asian_pips > 40:
        return LondonGate(allowed=False, reason="poor_consolidation", origin="ict_source")
    if adr_remaining is not None and adr_remaining <= 0:
        return LondonGate(allowed=False, reason="adr_spent", origin="ict_source")
    if cbdr.classification == "expanded":
        return LondonGate(allowed=False, reason="expanded_cbdr", origin="hermes_interpretation")
    if cbdr.classification == "ideal":
        return LondonGate(allowed=True, reason=None, origin="ict_source")
    return LondonGate(allowed=False, reason="unknown_cbdr", origin="hermes_interpretation")
```

Locked sentence (`docs/MONTH8_40_50.md`):

> CBDR &lt;40 is the classic condition; CBDR ≥50 is the explicit wide-CBDR avoidance condition (`ict_source`). The 40–&lt;50 band is expanded/non-classic and its treatment must be attributed as Hermes interpretation unless the lecture explicitly establishes it as a hard avoidance rule.

---

## 3. Path fixture — `fixtures/m8_path_eurusd.json`

No `ict_london_profile`. No `pick`. Path is observations after NY 00:00.

```json
{
  "symbol": "EURUSD",
  "date": "2017-04-14",
  "focus_pair": "EURUSD",
  "last": 1.0614,
  "timezone": "America/New_York",
  "calendar": [],
  "watchlist": ["EURUSD"],
  "opens": {
    "gmt0": 1.0598,
    "ny_midnight": 1.0599
  },
  "ranges": {
    "previous_day": { "high": 1.0621, "low": 1.0574, "close": 1.0598 },
    "asian": { "high": 1.0611, "low": 1.0592 },
    "cbdr": { "high": 1.0608, "low": 1.0582 },
    "named_extremes": { "pdh": 1.0621, "pdl": 1.0574 }
  },
  "adr5": { "high": 1.064, "low": 1.056, "remaining": 55 },
  "pair_institutional": {
    "sponsorship": { "weekly": "bearish", "daily": "bearish", "h4": "bearish" },
    "daytrade_iof": { "daily": "bearish", "h4": "bearish", "m60": "bearish" },
    "state": "bearish"
  },
  "dxy": {
    "relationship": "supportive",
    "from": "discount",
    "institutional": { "state": "bullish" }
  },
  "sentiment": {
    "direction": "bearish",
    "expected_delivery": "lower",
    "indicator": { "value": -22.0, "state": "bearish" },
    "reference_open": "gmt0",
    "asian_range": { "high": 1.0611, "low": 1.0592 },
    "liquidity_probe": { "preferred_side": "buy_side", "observed_side": "buy_side" },
    "judas_side": "buy_side",
    "reaction": { "pd_array_reaction": "pending" }
  },
  "origin_pd_array": "D_FVG_bear",
  "opposing_target_arrays": ["PDL"],
  "scenarios": {
    "primary": "London normal protraction sell: rally after 00:00 NY into CBDR/Asian high, then delivery lower toward daily discount.",
    "contrary": "Acceptance above projected 2SD high / failure to leave the buy-side probe."
  },
  "evidence": {
    "session": "london",
    "notes": "M8 path evidence. Post-00:00 observations only. No ict_london_profile key.",
    "path_after_anchor": {
      "anchor": "00:00",
      "clock": "America/New_York",
      "first_move": "up",
      "window": "00:00-02:00",
      "higher_high_vs_asian_or_cbdr": true,
      "lower_low_vs_asian_or_cbdr": false,
      "move_started_by_0200": true
    }
  },
  "month8": {
    "cbdr": {
      "height_pips": 26,
      "body_height_pips": 24,
      "body_high": 1.0606,
      "body_low": 1.0582,
      "wick_high": 1.0608,
      "wick_low": 1.0581
    },
    "asian_height_pips": 19
  }
}
```

Note: `scenarios.primary` still *describes* the lecture idea. The detector does **not** read that string. Profile is taken only from `path_after_anchor` + IOF + gate.

---

## 4. Gold — `fixtures/m8_path_eurusd.expected.json`

Harness only. Engine must not open this file.

```json
{
  "fixture": "fixtures/m8_path_eurusd.json",
  "fixture_kind": "path_evidence",
  "note": "Oracle for Slice 3. Engine must not open this file.",
  "expected_derived": {
    "cbdr_classification": "ideal",
    "london_allowed": true,
    "ict_london_profile": "normal_protraction_sell",
    "daytrade_opportunity": true
  }
}
```

---

## 5. Tests in `tests/test_reconstruction.py`

```python
def test_month8_slice2_does_not_name_profile():
    import json
    from ftn.os.m8_detect import derive_month8_measures
    raw = json.loads((ROOT / "fixtures/m8_path_eurusd.json").read_text())
    st = derive_month8_measures(raw)
    assert st.ict_london_profile == "none"


def test_month8_profile_from_path():
    import json
    from ftn.os.m8_profile import derive_month8_profile
    raw = json.loads((ROOT / "fixtures/m8_path_eurusd.json").read_text())
    assert "ict_london_profile" not in (raw.get("month8") or {})
    st = derive_month8_profile(raw)
    assert st.cbdr.classification == "ideal"
    assert st.london_session_gate.allowed is True
    assert st.ict_london_profile == "normal_protraction_sell"
    assert st.daytrade_opportunity is True
    raw2 = json.loads((ROOT / "fixtures/m8_evidence_eurusd.json").read_text())
    raw2["pair_institutional"]["state"] = "bearish"
    st2 = derive_month8_profile(raw2)
    assert st2.ict_london_profile == "none"


def test_month8_expanded_gate_is_hermes():
    from ftn.os.m8_contracts import CbdrState
    from ftn.os.m8_detect import london_gate_from_measures
    cb = CbdrState(height_pips=45, classification="expanded")
    g = london_gate_from_measures(cb, 20)
    assert g.allowed is False and g.reason == "expanded_cbdr"
    assert g.origin == "hermes_interpretation"
    wide = london_gate_from_measures(CbdrState(height_pips=55, classification="wide"), 20)
    assert wide.origin == "ict_source" and wide.reason == "wide_cbdr"
```

All three pass.

---

## 6. Decision table Slice 3 implements

| Gate | IOF | first_move | HH vs range | by 02:00 | Profile |
|------|-----|------------|-------------|----------|---------|
| closed | * | * | * | * | `none` |
| open | * | missing | * | * | `none` |
| open | bearish | up | yes | yes | `normal_protraction_sell` |
| open | bearish | up | no or late | | `delayed_protraction_sell` |
| open | bullish | down | yes | yes | `normal_protraction_buy` |
| open | bullish | down | no or late | | `delayed_protraction_buy` |
| open | mismatch | | | | `none` |

---

## 7. Not in Slice 3

- CBDR standard-deviation **projection** detector  
- HTF overlap detector  
- Reading 15m bars instead of `path_after_anchor` labels  
- Wiring `month8` into DTR `build_context` / briefing / desk  

Those stay later slices.
