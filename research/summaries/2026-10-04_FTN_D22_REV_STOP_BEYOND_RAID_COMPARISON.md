# INTELLIGENCE SUMMARY — FTN REV: stop beyond the raid (FTN-D22), three-way comparison (EXPLORATORY)
**Date:** 2026-10-04  
**Prereg:** `research/protocols/preregs/FTN_D22_REV_STOP_BEYOND_RAID_PREREG_2026-10-04.json` (committed before the code change and before scoring) · CASSANDRA **not yet reviewed** · DATA **not yet reviewed**  
**Tape:** Dukascopy CFD BID 1m, 2025-08-25 → 2026-09-25, **burned** (H013/H014 + two prior FTN scores) · not CME futures

> **EXPLORATORY — pending CASSANDRA + DATA review. Not a board result. No SURVIVES language.** Paper-only research; no trades, broker calls or allowlist changes are authorized by this file. **This tape cannot confirm anything.** Confirmation needs untouched data: forward sessions after 2026-09-25, or the `/workspace/marketdata` Dukascopy pull once DATA certifies it.

Same rules in every column except the REV change named in the header: entry = 15m ticket close, 2R / stop / 16:00 NY, costs 0.8 / 0.5 pt per side (US100 / US500), bootstrap 10k seed 20261004, 2,000-replicate random-entry foil, Holm across FTN-H001..H013 per instrument (min group n 10).

Sources: Before raid fix (IOF side + D18) = `research/evidence/quant/FTN_M9_SCORE_2026-10-04_before_rebased.json` · After raid fix (stop at raided level) = `research/evidence/quant/FTN_M9_SCORE_2026-10-04_rev_raid_side.json` · After D22 (stop beyond raid extreme) = `research/evidence/quant/FTN_M9_SCORE_2026-10-04_d22_stop_beyond_raid.json`

## US100

| | Before raid fix (IOF side + D18) | After raid fix (stop at raided level) | After D22 (stop beyond raid extreme) |
|---|---|---|---|
| Kernel tickets | 186 | 185 | 185 |
| Tradeable trades | 9 | 49 | 185 |
| Mean R after costs [95% CI] | -0.121 [-0.839, +0.699] | +0.155 [-0.264, +0.571] | -0.018 [-0.227, +0.195] |
| Win rate | 33.3% | 42.9% | 38.4% |
| Foil percentile | 40.1 | 87.8 | 89.7 |
| Blocked (by first failing gate) | side:rev_side_conflicts_with_raid 170 · risk:stop_not_protective 7 | risk:stop_not_protective 136 | none |

### Holm table — US100 (Δ = mean R true − false, 95% CI)

| Hypothesis | Before raid fix (IOF side + D18) | After raid fix (stop at raided level) | After D22 (stop beyond raid extreme) |
|---|---|---|---|
| FTN-H001 | n/e (7/2) | n/e (47/2) | n/e (183/2) |
| FTN-H002 | n/e (2/7) | +0.015 [-0.810, +0.866] · Holm 1.000 | -0.053 [-0.534, +0.426] · Holm 1.000 |
| FTN-H003 | n/e (6/3) | -0.501 [-1.313, +0.330] · Holm 1.000 | -0.096 [-0.532, +0.331] · Holm 1.000 |
| FTN-H004 | n/e (7/2) | -0.035 [-0.868, +0.795] · Holm 1.000 | +0.149 [-0.274, +0.563] · Holm 1.000 |
| FTN-H005 | n/e (2/7) | -0.183 [-1.112, +0.718] · Holm 1.000 | -0.018 [-0.508, +0.458] · Holm 1.000 |
| FTN-H006 | n/e (7/2) | +0.050 [-0.925, +0.997] · Holm 1.000 | -0.014 [-0.437, +0.411] · Holm 1.000 |
| FTN-H007 | n/e (7/2) | +0.140 [-0.143, +0.390] · Holm 1.000 | +0.115 [-0.025, +0.256] · Holm 0.928 |
| FTN-H008 | n/e (2/7) | -0.052 [-0.911, +0.816] · Holm 1.000 | -0.433 [-0.841, -0.017] · Holm 1.000 |
| FTN-H009 | n/e (2/6) | -0.349 [-1.313, +0.678] · Holm 1.000 | +0.105 [-0.503, +0.705] · Holm 1.000 |
| FTN-H010 | n/e (9/0) | n/e (43/6) | +0.280 [-0.144, +0.704] · Holm 1.000 |
| FTN-H011 | n/e (3/6) | -0.735 [-1.554, +0.131] · Holm 1.000 | -0.032 [-0.530, +0.479] · Holm 1.000 |
| FTN-H012 | n/e (7/2) | n/e (7/42) | -0.255 [-0.856, +0.438] · Holm 1.000 |
| FTN-H013 | n/e (5/4) | n/e (8/41) | -0.078 [-0.708, +0.556] · Holm 1.000 |

## US500

| | Before raid fix (IOF side + D18) | After raid fix (stop at raided level) | After D22 (stop beyond raid extreme) |
|---|---|---|---|
| Kernel tickets | 168 | 167 | 167 |
| Tradeable trades | 13 | 46 | 167 |
| Mean R after costs [95% CI] | +0.394 [-0.342, +1.102] | -0.068 [-0.522, +0.378] | +0.010 [-0.211, +0.233] |
| Win rate | 53.8% | 45.7% | 43.1% |
| Foil percentile | 78.8 | 88.2 | 98.5 |
| Blocked (by first failing gate) | side:rev_side_conflicts_with_raid 151 · risk:stop_not_protective 4 | risk:stop_not_protective 121 | none |

### Holm table — US500 (Δ = mean R true − false, 95% CI)

| Hypothesis | Before raid fix (IOF side + D18) | After raid fix (stop at raided level) | After D22 (stop beyond raid extreme) |
|---|---|---|---|
| FTN-H001 | n/e (11/2) | n/e (44/2) | n/e (165/2) |
| FTN-H002 | n/e (4/9) | -0.544 [-1.452, +0.381] · Holm 1.000 | +0.143 [-0.330, +0.631] · Holm 1.000 |
| FTN-H003 | n/e (8/5) | -0.117 [-1.046, +0.781] · Holm 1.000 | -0.190 [-0.662, +0.271] · Holm 1.000 |
| FTN-H004 | n/e (11/2) | +0.791 [-0.150, +1.749] · Holm 0.343 | +0.087 [-0.345, +0.525] · Holm 1.000 |
| FTN-H005 | n/e (2/11) | -0.982 [-1.874, -0.085] · Holm 1.000 | -0.565 [-1.088, -0.023] · Holm 1.000 |
| FTN-H006 | n/e (10/3) | +0.349 [-0.608, +1.276] · Holm 1.000 | +0.213 [-0.261, +0.691] · Holm 1.000 |
| FTN-H007 | n/e (11/2) | +0.178 [-0.098, +0.451] · Holm 1.000 | +0.062 [-0.089, +0.216] · Holm 1.000 |
| FTN-H008 | n/e (6/7) | -0.135 [-1.053, +0.784] · Holm 1.000 | +0.011 [-0.442, +0.454] · Holm 1.000 |
| FTN-H009 | n/e (3/8) | n/e (7/26) | -0.063 [-0.643, +0.509] · Holm 1.000 |
| FTN-H010 | n/e (0/0) | n/e (0/0) | n/e (0/0) |
| FTN-H011 | n/e (0/0) | n/e (0/0) | n/e (0/0) |
| FTN-H012 | n/e (10/3) | n/e (9/37) | +0.558 [-0.128, +1.239] · Holm 1.000 |
| FTN-H013 | n/e (6/7) | n/e (8/38) | -0.065 [-0.573, +0.459] · Holm 1.000 |

## READING (exploratory; no claim)

- **Blocked:** with the stop beyond the raid's extreme, no US100 or US500 kernel ticket is blocked by anything except the empty allowlist and the I0 contract gate (every draft is `blocked_by: allowlist:not_on_mint_allowlist`). The D18 direction gate fired 0 times. The stop-side check also fired 0 times. Both stay in place as safety nets.
- **US100:** 185 trades, −0.018R [−0.227, +0.195], ex-top-1% −0.029, foil 89.7th pct (foil median −0.147). That is no evidence of an edge. The +0.155R in the middle column came from the 49 tickets whose entry was already back inside the level, a selected subset.
- **US500:** 167 trades, +0.010R [−0.211, +0.233], ex-top-1% −0.002. The foil is at the 98.5th pct (foil median −0.214). The kernel beats random entries with the same stops, but its own mean is ≈ 0 with a CI spanning 0. On a burned tape that is a reason for a forward prereg, not a result.
- **Holm:** no hypothesis on either instrument reaches Holm p < 0.05 in any column. Two CIs exclude 0, both in the **opposite** direction to the lecture claim (Holm 1.000): US100 H008 (tight CBDR) Δ −0.433 and US500 H005 (IPDA-20 discount) Δ −0.565. The earlier H010 lead (legacy stream, Holm 0.109) is now Δ +0.280 [−0.144, +0.704], Holm 1.000.
- **Interpretation-trigger variant** (US100, disclosure): 188 trades, −0.003R.
- **What changed in fixtures:** the 4 bar-derived REV fixtures (`m9_raw_eurusd`, `m9_calendar_idle`, `m9_calendar_watchlist`, plus `m8_live_2026-09-17`, which has bars and a raid but no draft) gain `evidence.raid_extreme`. Their DayContext fingerprint therefore changes. The three REV ones move their draft stop from 1.11420 (PDL) to 1.11400 (raid low 1.11410 − 1 pip). `m9_reconstruction_eurusd` and `m9_rev_inside_box` have no bar-derived raid bar, so they use the level + buffer fallback (1.11410). The committed handoff.v1 samples are unchanged: stops are not in handoff.v1, and the sample fixtures carry no `raid_extreme`.

## NEXT
- CASSANDRA red-team, then DATA. If US500 is worth pursuing, register a new ID with this exact rule *before* reading any session after 2026-09-25, or any certified `/workspace/marketdata` session outside the burned window.
