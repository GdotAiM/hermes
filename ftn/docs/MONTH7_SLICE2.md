# Month 7 Slice 2 — dealing range + IPDA

File: `src/ftn/os/m7_range.py`
Evidence fixture: `fixtures/m7_evidence_eurusd.json` (no weekly profile key)

`derive_month7_range` fills DealingRange + IpdaWindow and **forces**
`ict_weekly_profile=none`, no OSOK, no swing ticket.

Labeled arrays: M_DISCOUNT → W_PREMIUM, bullish, IPDA 20.
