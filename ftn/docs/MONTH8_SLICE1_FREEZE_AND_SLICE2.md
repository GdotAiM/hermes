# Month 8 — Slice 1 freeze + Slice 2 (review copy)

What changed after your “not quite evidence-only” review.

---

## 1. Fixture roles (clarified, not redesigned)

| File | Kind | Contains derived M8 conclusions? |
|------|------|----------------------------------|
| `fixtures/m8_reconstruction_eurusd.json` | **known-state** | Yes: gate, profile, opportunity, projection. Schema test only. |
| `fixtures/m8_evidence_eurusd.json` | **evidence** | No. Measurements only. |

Neither file has `pick` or `expected_winner`.

Known-state `evidence.notes` now say so explicitly:

```text
M8 KNOWN-STATE reconstruction fixture (Slice 1).
Not evidence-only: gate/profile/opportunity/projection are provided state.
No pick/expected_winner.
```

---

## 2. `IctTrueDay` (contract tweak only)

ICT day ≠ broker/MT4 midnight is now fields, not a comment on tuples.

```python
@dataclass(frozen=True)
class IctTrueDay:
    """ICT day != broker/MT4 midnight. All windows are New York local."""

    clock: str = "America/New_York"
    day_anchor: str = "00:00"
    asian: tuple = ("20:00", "00:00")
    london_kz: tuple = ("01:00", "05:00")
    london_close: tuple = ("10:00", "12:00")
    ny_am: tuple = ("07:00", "10:00")
    cbdr_window: tuple = ("14:00", "20:00")
    origin: str = "ict_source"
```

Everything else in `m8_contracts.py` is unchanged (CBDR 40/50 classes, two profile fields, HTF `seed_only`, guidance ≠ governance).

---

## 3. Slice 2 — `src/ftn/os/m8_detect.py`

Derives **only**:

- CBDR `classification` + `daytrade_classic`
- `london_session_gate`

Does **not** name `ict_london_profile`. That is price-after-00:00 (Slice 3).

```python
"""Month-8 Slice 2: derive CBDR class + London gate from measurements.

Does not name ict_london_profile. That needs price-behavior evidence (Slice 3+).
"""

from __future__ import annotations

from ftn.os.m8_contracts import (
    CbdrState,
    LondonGate,
    Month8State,
    classify_cbdr,
    parse_month8,
)


def measure_cbdr(block: dict | None) -> CbdrState:
    block = block or {}
    height = block.get("height_pips")
    if height is None and block.get("body_high") is not None and block.get("body_low") is not None:
        height = round((float(block["body_high"]) - float(block["body_low"])) * 10000, 1)
    cls = classify_cbdr(height)
    return CbdrState(
        height_pips=height,
        body_height_pips=block.get("body_height_pips"),
        wick_high=block.get("wick_high"),
        wick_low=block.get("wick_low"),
        body_high=block.get("body_high"),
        body_low=block.get("body_low"),
        classification=cls,
        daytrade_classic=cls == "ideal",
    )


def london_gate_from_measures(
    cbdr: CbdrState,
    asian_pips: float | None,
    adr_remaining=None,
    news: bool = False,
) -> LondonGate:
    if news:
        return LondonGate(allowed=False, reason="news")
    if cbdr.classification == "wide":
        return LondonGate(allowed=False, reason="wide_cbdr")
    if asian_pips is not None and asian_pips > 40:
        return LondonGate(allowed=False, reason="poor_consolidation")
    if adr_remaining is not None and adr_remaining <= 0:
        return LondonGate(allowed=False, reason="adr_spent")
    if cbdr.classification == "expanded":
        return LondonGate(allowed=False, reason="expanded_cbdr")
    if cbdr.classification == "ideal":
        return LondonGate(allowed=True, reason=None)
    return LondonGate(allowed=False, reason="unknown_cbdr")


def derive_month8_measures(raw: dict) -> Month8State:
    """Fill classification + gate. Leave profile/opportunity/projection as provided or none."""
    base = parse_month8(raw) or Month8State()
    m8 = raw.get("month8") or raw.get("ict_day") or {}
    ranges = raw.get("ranges") or {}
    cb_src = m8.get("cbdr") or ranges.get("cbdr") or {}
    if "height_pips" not in cb_src and cb_src.get("high") is not None:
        cb_src = dict(cb_src)
        cb_src["height_pips"] = round((float(cb_src["high"]) - float(cb_src["low"])) * 10000, 1)
    cbdr = measure_cbdr(cb_src)
    asian = m8.get("asian_height_pips")
    if asian is None:
        ar = ranges.get("asian") or {}
        if ar.get("high") is not None:
            asian = round((float(ar["high"]) - float(ar["low"])) * 10000, 1)
    news = any(str(e.get("impact", "")).lower() == "high" for e in (raw.get("calendar") or []))
    rem = (raw.get("adr5") or {}).get("remaining")
    gate = london_gate_from_measures(cbdr, asian, rem, news)
    return Month8State(
        ict_true_day=base.ict_true_day,
        cbdr=cbdr,
        asian_height_pips=asian,
        london_session_gate=gate,
        ict_london_profile=base.ict_london_profile,
        daily_extreme_projection=base.daily_extreme_projection,
        daytrade_opportunity=base.daytrade_opportunity,
        htf_entry_overlap=base.htf_entry_overlap,
        ict_guidance=base.ict_guidance,
    )
```

Gate order (Hermes reading of lecture 3 + 6, attributable later if you want different order):

1. high-impact news → avoid (`news`)  
2. CBDR ≥ 50 → avoid (`wide_cbdr`)  
3. Asian > 40 pips → avoid (`poor_consolidation`)  
4. ADR remaining ≤ 0 → avoid (`adr_spent`)  
5. CBDR 40–&lt;50 → avoid (`expanded_cbdr`) — caution band is not “classic London”  
6. CBDR &lt; 40 → allow  

---

## 4. Evidence fixture — `fixtures/m8_evidence_eurusd.json`

Same tape measurements as the known-state day. `month8` block is **only** raw range sizes.

```json
{
  "symbol": "EURUSD",
  "date": "2017-04-13",
  "focus_pair": "EURUSD",
  "last": 1.0614,
  "timezone": "America/New_York",
  "calendar": [],
  "watchlist": ["EURUSD"],
  "opens": { "gmt0": 1.0598, "ny_midnight": 1.0599 },
  "ranges": {
    "previous_day": { "high": 1.0621, "low": 1.0574, "close": 1.0598 },
    "asian": { "high": 1.0611, "low": 1.0592 },
    "cbdr": { "high": 1.0608, "low": 1.0582 },
    "named_extremes": { "pdh": 1.0621, "pdl": 1.0574 }
  },
  "adr5": { "high": 1.064, "low": 1.056, "remaining": 55 },
  "pair_institutional": {
    "sponsorship": { "weekly": "bearish", "daily": "bearish", "h4": "bearish" },
    "daytrade_iof": { "daily": "bearish", "h4": "bearish", "m60": "bearish" }
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
    "notes": "M8 evidence-only. No london gate, profile, opportunity, or projection."
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

Gold (harness only): `fixtures/m8_evidence_eurusd.expected.json`

```json
{
  "fixture": "fixtures/m8_evidence_eurusd.json",
  "fixture_kind": "evidence",
  "note": "Oracle for Slice 2 measure detector. Engine must not open this file.",
  "expected_derived": {
    "cbdr_classification": "ideal",
    "london_allowed": true,
    "london_reason": null,
    "ict_london_profile": "none",
    "daytrade_opportunity": false
  }
}
```

Detector result on this tape: **ideal + London allowed**. Profile stays `none`. Opportunity stays false.

---

## 5. Tests added

- `test_month8_contracts_and_fixture` — known-state schema (Slice 1)  
- `test_month8_evidence_derives_gate` — evidence → class + gate, profile still `none` (Slice 2)

Both pass.

---

## 6. Still not Slice 3

Slice 3 is the real reconstruction question:

> From IOF + post-00:00 NY path, can we name `normal_protraction_sell` without the fixture saying so?

Not implemented. Review Slice 2 gate order first if you want that band (`expanded` → avoid) tightened or loosened.
