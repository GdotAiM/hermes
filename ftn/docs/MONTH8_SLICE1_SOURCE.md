# Month 8 slice 1 — source copy

Read-only dump of the three pieces you asked for. Source of truth remains the files under `ftn-agent/`.

---

## 1. `src/ftn/os/m8_contracts.py`

```python
"""Month-8 contracts. ICT day-trade layer on Market State. No detectors here."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal, Optional

CbdrClass = Literal["ideal", "expanded", "wide", "unknown"]
LondonProfile = Literal[
    "normal_protraction_buy",
    "normal_protraction_sell",
    "delayed_protraction_buy",
    "delayed_protraction_sell",
    "none",
]
Draw = Literal["high", "low", "none"]


@dataclass(frozen=True)
class IctTrueDay:
    timezone: str = "America/New_York"
    asian: tuple = ("20:00", "00:00")
    london_kz: tuple = ("01:00", "05:00")
    london_close: tuple = ("10:00", "12:00")
    ny_am: tuple = ("07:00", "10:00")
    cbdr_window: tuple = ("14:00", "20:00")
    origin: str = "ict_source"


@dataclass(frozen=True)
class CbdrState:
    height_pips: Optional[float] = None
    body_height_pips: Optional[float] = None
    wick_high: Optional[float] = None
    wick_low: Optional[float] = None
    body_high: Optional[float] = None
    body_low: Optional[float] = None
    classification: CbdrClass = "unknown"
    daytrade_classic: bool = False  # True only when classification == ideal (<40)
    origin: str = "ict_source"


@dataclass(frozen=True)
class LondonGate:
    allowed: bool = False
    reason: Optional[str] = None  # wide_cbdr | poor_consolidation | adr_spent | news | none
    origin: str = "ict_source"


@dataclass(frozen=True)
class DailyExtremeProjection:
    draw: Draw = "none"
    sd_levels: tuple = ()
    source_range: str = "cbdr"
    selected_level: Optional[float] = None
    basis: tuple = ()
    origin: str = "ict_source"


@dataclass(frozen=True)
class HtfOverlap:
    present: bool = False
    array_id: Optional[str] = None
    timeframe: Optional[str] = None
    relationship: Optional[str] = None
    origin: str = "ict_source"


@dataclass(frozen=True)
class Month8State:
    """ICT day-trade layer. Distinct from Hermes `profile`."""

    ict_true_day: IctTrueDay = field(default_factory=IctTrueDay)
    cbdr: CbdrState = field(default_factory=CbdrState)
    asian_height_pips: Optional[float] = None
    london_session_gate: LondonGate = field(default_factory=LondonGate)
    ict_london_profile: LondonProfile = "none"
    daily_extreme_projection: DailyExtremeProjection = field(
        default_factory=DailyExtremeProjection
    )
    daytrade_opportunity: bool = False
    htf_entry_overlap: HtfOverlap = field(default_factory=HtfOverlap)
    ict_guidance: dict = field(
        default_factory=lambda: {
            "approx_setups_per_day": 2,
            "adr_capture_pct": "65-75",
            "note": "guidance not hermes_governance",
        }
    )


def classify_cbdr(height_pips: float | None) -> str:
    if height_pips is None:
        return "unknown"
    if height_pips < 40:
        return "ideal"
    if height_pips < 50:
        return "expanded"
    return "wide"


def parse_month8(raw: dict | None) -> Month8State | None:
    if not raw:
        return None
    block = raw.get("month8") or raw.get("ict_day")
    if not block:
        return None
    cb = block.get("cbdr") or {}
    height = cb.get("height_pips")
    cls = cb.get("classification") or classify_cbdr(height)
    gate = block.get("london_session_gate") or {}
    proj = block.get("daily_extreme_projection") or {}
    ov = block.get("htf_entry_overlap") or {}
    return Month8State(
        cbdr=CbdrState(
            height_pips=height,
            body_height_pips=cb.get("body_height_pips"),
            wick_high=cb.get("wick_high"),
            wick_low=cb.get("wick_low"),
            body_high=cb.get("body_high"),
            body_low=cb.get("body_low"),
            classification=cls,
            daytrade_classic=cls == "ideal",
        ),
        asian_height_pips=block.get("asian_height_pips"),
        london_session_gate=LondonGate(
            allowed=bool(gate.get("allowed", False)),
            reason=gate.get("reason"),
        ),
        ict_london_profile=block.get("ict_london_profile") or "none",
        daily_extreme_projection=DailyExtremeProjection(
            draw=proj.get("draw") or "none",
            sd_levels=tuple(proj.get("sd_levels") or ()),
            source_range=proj.get("source_range") or "cbdr",
            selected_level=proj.get("selected_level"),
            basis=tuple(proj.get("basis") or ()),
        ),
        daytrade_opportunity=bool(block.get("daytrade_opportunity", False)),
        htf_entry_overlap=HtfOverlap(
            present=bool(ov.get("present", False)),
            array_id=ov.get("array_id"),
            timeframe=ov.get("timeframe"),
            relationship=ov.get("relationship"),
        ),
    )
```

---

## 2. Optional `DayContext.month8` (M9 fixtures still load)

In `src/ftn/os/contracts.py`:

**Field on `DayContext`**

```python
evidence: dict = field(default_factory=dict)
month8: object = None  # Month8State | None; optional ICT day-trade layer
```

**Loader helper**

```python
def _month8(raw: dict):
    from ftn.os.m8_contracts import parse_month8
    return parse_month8(raw)
```

**Wired in `load_day_context`**

```python
evidence=raw.get("evidence") or {},
month8=_month8(raw),
```

`parse_month8` returns `None` unless the JSON has a `month8` or `ict_day` block. Month-9 fixtures have neither, so `ctx.month8 is None` and existing golds are unchanged.

Hermes `profile` stays on `DayContext.profile`. ICT London profile lives only under `ctx.month8.ict_london_profile`.

---

## 3. `fixtures/m8_reconstruction_eurusd.json`

No `pick`. No `expected_winner`. `cbdr.classification` omitted so the loader derives `ideal` from `height_pips: 26`.

```json
{
  "symbol": "EURUSD",
  "date": "2017-04-12",
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
    "previous_day": {
      "high": 1.0621,
      "low": 1.0574,
      "close": 1.0598
    },
    "asian": {
      "high": 1.0611,
      "low": 1.0592
    },
    "cbdr": {
      "high": 1.0608,
      "low": 1.0582
    },
    "named_extremes": {
      "pdh": 1.0621,
      "pdl": 1.0574
    }
  },
  "adr5": {
    "high": 1.064,
    "low": 1.056,
    "remaining": 55
  },
  "pair_institutional": {
    "sponsorship": {
      "weekly": "bearish",
      "daily": "bearish",
      "h4": "bearish"
    },
    "daytrade_iof": {
      "daily": "bearish",
      "h4": "bearish",
      "m60": "bearish"
    }
  },
  "dxy": {
    "relationship": "supportive",
    "from": "discount",
    "institutional": {
      "state": "bullish"
    }
  },
  "sentiment": {
    "direction": "bearish",
    "expected_delivery": "lower",
    "indicator": {
      "value": -22.0,
      "state": "bearish"
    },
    "reference_open": "gmt0",
    "asian_range": {
      "high": 1.0611,
      "low": 1.0592
    },
    "liquidity_probe": {
      "preferred_side": "buy_side",
      "observed_side": "buy_side"
    },
    "judas_side": "buy_side",
    "reaction": {
      "pd_array_reaction": "pending"
    }
  },
  "origin_pd_array": "D_FVG_bear",
  "opposing_target_arrays": ["PDL"],
  "scenarios": {
    "primary": "London normal protraction sell: rally after 00:00 NY into CBDR/Asian high, then delivery lower toward daily discount.",
    "contrary": "Acceptance above projected 2SD high / failure to leave the buy-side probe."
  },
  "evidence": {
    "session": "london",
    "notes": "M8 reconstruction. Evidence-only. No pick/winner key. month8 block is labeled ICT state for contract freeze — detectors not implemented yet."
  },
  "month8": {
    "asian_height_pips": 19,
    "cbdr": {
      "height_pips": 26,
      "body_height_pips": 24,
      "body_high": 1.0606,
      "body_low": 1.0582,
      "wick_high": 1.0608,
      "wick_low": 1.0581
    },
    "london_session_gate": {
      "allowed": true,
      "reason": null
    },
    "ict_london_profile": "normal_protraction_sell",
    "daily_extreme_projection": {
      "draw": "high",
      "source_range": "cbdr",
      "sd_levels": [
        {"sd": 1, "price": 1.0634},
        {"sd": 2, "price": 1.066},
        {"sd": 3, "price": 1.0686}
      ],
      "selected_level": 1.0634,
      "basis": ["bearish_iof", "sell_day_projects_high"]
    },
    "daytrade_opportunity": true,
    "htf_entry_overlap": {
      "present": true,
      "array_id": "D_FVG_bear",
      "timeframe": "daily",
      "relationship": "seed_only"
    }
  }
}
```
