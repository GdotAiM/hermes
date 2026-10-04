# Month 8 Slice 9 — reconstruction freeze

Matrix in `tests/test_reconstruction.py` as `CASES_M8`.

| Fixture | Profile | Gate |
|---------|---------|------|
| m8_path_eurusd.json | normal_protraction_sell | allow |
| m8_s4_late_rally.json | delayed_protraction_sell | allow |
| m8_s4_late_rally_window_only.json | delayed_protraction_sell | allow |
| m8_s4_no_hh.json | none | allow |
| m8_s4_first_move_only.json | none | allow |
| m8_evidence_eurusd.json | none | allow |

Engine modules must not contain `.expected.json`.
Gold files remain harness-only.

Month 8 slices 1–9 complete. Layer is context on DayContext.month8.
