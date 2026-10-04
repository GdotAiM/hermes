# Month 8 Slice 3 — FROZEN

Status: complete. Do not add projection, HTF overlap, DTR wiring, or desk in this slice.

## Pipeline locked

RAW EVIDENCE → Slice 2 (CBDR class + London gate) → Slice 3 (IOF + path_after_anchor) → ict_london_profile
Profile does not choose a trade. M9 candidates / session_ticket still own that.

## Guard that must not regress

derive_month8_profile(evidence_without_path) → ict_london_profile == none
even if IOF is forced bearish.

## Slice 4 research (not implemented)

Current Hermes rule:

- bearish + up + HH + early → normal_protraction_sell
- bearish + up + anything else → delayed_protraction_sell

That second arm may be stronger than the tape proves. Slice 4 should test whether
"not classic early rally" is delayed_protraction or none, against the lecture/path dataset.
Do not change the classifier until that review.
