# Month 5 Slice 10 — reconstruction freeze

CASES_M5 in tests/test_reconstruction.py

| Fixture | Quarterly | IPDA | Swing | Opportunity |
|---------|-----------|------|-------|-------------|
| m5_evidence_eurusd.json | in_progress | 60 | breaker_swing_point | true |

Engine src/ftn/os/m5_* must not mention .expected.json.
Known-state m5_reconstruction_eurusd.json stays schema-only (not in this matrix).

Direct derive_month5() and DTR build_context() must agree.
session_ticket remains None.

Month 5 slices 0–10 complete. Layer is position annotation, not an M9 child.
