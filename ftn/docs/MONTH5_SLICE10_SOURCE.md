# Month 5 Slice 10 — full source copy

Reconstruction freeze. No new detectors. Formalize S2–S9 and prove the engine never reads gold files.

Repo paths under `ftn-agent/`.

---

## What Slice 10 is

```
CASES_M5  →  derive_month5 + build_context
engine sources  →  must not mention *.expected.json
M6 CASES_M6 + M7 CASES_M7 + M8 CASES_M8 + M9 gold  →  still pass
```

Gold / `*.expected.json` remain harness-only.

Known-state `m5_reconstruction_eurusd.json` stays a schema fixture. It is **not** in this matrix.

---

## 1. Matrix

```python
CASES_M5 = [
    ("m5_evidence_eurusd.json", "in_progress", 60, "breaker_swing_point", True),
]
```

| Fixture | Quarterly | IPDA | Swing | Opportunity |
|---------|-----------|------|-------|-------------|
| m5_evidence_eurusd.json | in_progress | 60 | breaker_swing_point | true |

No `pick` / `expected_winner`. Confirming 10Y notes remain false on this fixture; opportunity is still true.

---

## 2. test_month5_slice10_matrix

Direct detector and DTR path must agree. `session_ticket` is None.

---

## 3. test_month5_engine_never_opens_gold

Scans: m5_contracts, m5_env, m5_float, m5_swing, m5_confirm, m5_pd, m5_setup, m5_opportunity, dtr, briefing.

---

## 4. Month 5 complete map

```
src/ftn/os/m5_contracts.py     S1
src/ftn/os/m5_env.py           S2  quarterly + IPDA
src/ftn/os/m5_float.py         S3  open float + pools
src/ftn/os/m5_swing.py         S4  institutional swing
src/ftn/os/m5_confirm.py       S5  confirming
src/ftn/os/m5_pd.py            S6  HTF PD identity
src/ftn/os/m5_setup.py         S7  setup / entry / mgmt
src/ftn/os/m5_opportunity.py   S8  position_opportunity
src/ftn/os/dtr.py              S9  month5= attach
src/ftn/os/briefing.py         S9  ## Month 5
src/ftn/os/handoff.py          S9  market_state.month5
desk/                          S9  chips
tests/test_reconstruction.py   S10 CASES_M5
```

Invariant: Month 5 describes the position. Month 9 still selects the session ticket.

---

## 5. What Slice 10 does not do

- No new fields
- No paper_position_m5
- No evaluate_candidates row
- Does not make ctx.month5 required for M6–M9

---

## 6. Status

S0–S10 complete. Next work is a new phase, not Month 5 Slice 11.
