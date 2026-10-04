# Month 8 essence (signed)

ICT Day Trading Model as one process, not eight strategies.

WEEKLY / DAILY DRAW → ICT TRUE DAY → CBDR + ASIAN → LONDON GATE
  → ICT LONDON PROFILE → DAILY EXTREME PROJECTION
  → DAY-TRADE OPPORTUNITY → OPTIONAL HTF OVERLAP

## Frozen decisions

- ~2 setups/day = ICT guidance, not Hermes law. `session_ticket` stays 1/session.
- CBDR: `<40` ideal, `40–<50` expanded, `≥50` wide. Do not collapse to one number.
- NY-only = `ict_london_profile=none` + `london_session_gate.avoid`. No `ny_only_profile`.
- HTF overlap annotates. Never changes size language.

## Two profile fields

- `ict_london_profile` — London delivery pattern (ICT).
- Hermes `profile` — broader market condition (M9). Do not collapse.
