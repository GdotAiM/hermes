# Month 8 Slice 3 + 40/50 lock (review copy)

## Locked sentence

CBDR `<40` = classic (`ict_source`). CBDR `≥50` = wide avoidance (`ict_source`).  
CBDR `40–<50` = expanded / non-classic. Hermes **refuses classic London** there:

`allowed=false`, `reason=expanded_cbdr`, `origin=hermes_interpretation`

until a lecture review promotes it to `ict_source`.

## Slice 3 rule

`ideal CBDR + bearish IOF` **does not** name a profile.

Profile comes from `evidence.path_after_anchor` after NY `00:00`:

- bearish IOF + first move **up** + HH vs Asian/CBDR + by 02:00 → `normal_protraction_sell`
- bearish IOF + up without the classic early rally → `delayed_protraction_sell`
- bullish mirror → buy profiles
- no path / gate closed → `none`

## Files

- `src/ftn/os/m8_profile.py`
- `fixtures/m8_path_eurusd.json` — path observations, **no** `ict_london_profile`
- Evidence fixture still has **no** path → Slice 3 on it stays `none`

## Tests

- Slice 2 on the path fixture still outputs `profile=none`
- Slice 3 on the path fixture → `normal_protraction_sell`
- Slice 3 on evidence-only (IOF forced bearish, no path) → `none`
- Expanded gate origin is `hermes_interpretation`; wide is `ict_source`
