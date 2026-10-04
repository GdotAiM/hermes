# Month 7 Slice 10 — reconstruction freeze

CASES_M7 in tests/test_reconstruction.py

| Fixture | Profile | OSOK | LRLR |
|---------|---------|------|------|
| m7_path_eurusd.json | classic_tuesday_low_of_week | true | low |
| m7_evidence_eurusd.json | none | false | unclear |

Engine src/ftn/os/m7_* must not mention .expected.json.
Known-state m7_reconstruction_eurusd.json stays schema-only (not in this matrix).

Month 7 slices 0–10 complete. Layer is context + paper swing, not an M9 child.
