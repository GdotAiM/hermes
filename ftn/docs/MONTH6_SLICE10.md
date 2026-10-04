# Month 6 Slice 10 — reconstruction freeze

CASES_M6 in tests/test_reconstruction.py

| Fixture | Family | Sequence | Opportunity | MD |
|---------|--------|----------|-------------|-----|
| m6_evidence_xauusd.json | bull | mw_bullish_daily_correcting | true | incomplete |

Engine src/ftn/os/m6_* must not mention .expected.json.
Known-state m6_reconstruction_xauusd.json stays schema-only (not in this matrix).

Month 6 slices 0–10 complete. Layer is swing annotation, not an M9 child.
