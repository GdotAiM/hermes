# Integration suite — FROZEN (I0–I5)

Not a month. No new fields. No new detectors. No gold changes.

## I0 invariants

1. Attachment is per-layer evidence. Missing M5 does not drop M1.
2. A true M1 flag does not mint an M9 ticket.
3. A true M4 catalog does not mint M5 position_opportunity.
4. A true M6 swing_opportunity does not mint M7 paper_swing in DTR (persist=False).
5. M3 IOF labels do not write pair_institutional.
6. M1 dealing_range_side does not write M5 nearest PD ids.
7. Briefing order: Market State → M1 → … → M8 → M9 candidates.
8. Integration attachment is observational only. I1–I5 must not derive, reinterpret, or arbitrate any month-owned flag.
9. The integration fixture contains evidence, not expected outcomes.
10. No new detectors, opportunity rules, or gold edits.

## I1 fixture

`fixtures/integration_m1_m9_eurusd.json`

Labeled combined evidence. No pick / expected_winner keys.

## I2–I5 tests

`test_integration_i2_attach`
`test_integration_i3_ticket_isolation`
`test_integration_i4_brief`
`test_integration_i5_golds`

## Status

I0–I5 COMPLETE. Integration frozen.

Next permitted: Month 10 Slice 0 glossary. No m10_contracts.py until Slice 0 is signed.
