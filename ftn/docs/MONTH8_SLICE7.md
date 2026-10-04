# Month 8 Slice 7 — DTR wiring

In `build_context`: if raw has `month8` / `ict_day` or `ranges.cbdr`,
set `month8=derive_month8_profile(raw_with_updated_evidence)`.
Else `month8=None`.

Does not mutate M9 sentiment, Hermes profile, or candidate states.
M9 reconstruction golds still pass.
