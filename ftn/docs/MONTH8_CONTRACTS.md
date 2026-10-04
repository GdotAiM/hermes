# Month 8 contracts

## Slice 1 — frozen schema + known-state fixture

`fixtures/m8_reconstruction_eurusd.json` is a **known-state** reconstruction fixture.
It is **not** evidence-only. It supplies `ict_london_profile`, `london_session_gate`,
`daytrade_opportunity`, and `daily_extreme_projection` so the schema can be tested.

No `pick` / `expected_winner`.

`IctTrueDay.clock` = America/New_York, `day_anchor` = 00:00 NY (ICT day ≠ MT4 midnight).

## Slice 2 — measure detector

`src/ftn/os/m8_detect.py` derives only:

- CBDR classification (ideal / expanded / wide)
- London gate from CBDR + Asian width + ADR remaining + high-impact news

It does **not** name `ict_london_profile`. That needs price-behavior evidence (Slice 3).

Evidence fixture: `fixtures/m8_evidence_eurusd.json`

# Month 8 — locked sentence (40/50)

CBDR <40 is the classic condition; CBDR ≥50 is the explicit wide-CBDR avoidance
condition (ict_source). The 40–<50 band is expanded/non-classic. Hermes currently
refuses the *classic* London model there (`allowed=false`, reason=`expanded_cbdr`,
origin=`hermes_interpretation`) unless a later lecture review upgrades that to ict_source.
