# Tape stream C — requirements stub (INV-001)
**Owner:** DATA  
**Status:** REQUIREMENTS ONLY — tape **not filed**  
**Date:** 2026-09-13  
**Blocks:** QUANT runs on hyps derived from C90xGr3kW8Y Passed Observed (esp. C-2026-014 / 015)

## Required registry fields (must be filled when tape arrives)

| Field | Required value / rule |
|-------|------------------------|
| SOURCE | Named vendor/feed + retrieval method + file path(s). No anonymous CSV. |
| TIMEZONE | Store UTC timestamps **and** `America/New_York`. Lecture calendar uses ET; **2026-03-11 = EDT**. |
| GRANULARITY | **1-minute** OHLC minimum (sub-1m optional later; lecture chart is 1m). |
| DATE RANGE | **At least 2026-03-10 and 2026-03-11** (prior-day lunch + lecture/CPI-day context). Prefer full RTH+ETH Globex sessions spanning both dates. |
| INSTRUMENT | **MNQ** Micro E-mini Nasdaq-100 **March 2026** contract as on lecture chart. If continuous used later, document roll method + adjustment separately — do not silently substitute. |
| KNOWN LIMITATIONS | Missing bars policy; holiday/early-close; spread/slippage not in OHLC; any vendor delay |

## Continuity / integrity checks before QUANT
- [ ] No duplicate timestamps
- [ ] Monotonic time within session
- [ ] Contract month matches Mar 2026 (or documented map from continuous → Mar 2026 levels)
- [ ] Session filter stated: ETH vs RTH (lecture uses lunch 11:30–13:30 chart labels + 13:30–14:00 PM OR — ETH required for lunch)
- [ ] OHLC integrity (H≥max(O,C), L≤min(O,C), H≥L)
- [ ] No look-ahead columns
- [ ] Alignable to lecture timestamps in `evidence/C90xGr3kW8Y/`

## Lecture alignment targets
| Lecture | video_id | Chart dates shown | Use |
|---------|----------|-------------------|-----|
| NY Lunch Algorithmic Theory | `C90xGr3kW8Y` | Tue Mar 10, 2026 (prior day) / lecture 2026-03-11 | Reproduce lunch raid + PM OR + prior-day FVG carry |

## Explicitly out of scope for stream C v0
- US100 CFD (different session/basis) unless a separate stream is registered
- NQ full-size without documenting 2× MNQ scaling
- Taxonomy-derived windows without Passed Observed citation

## Gate rule
Until a concrete tape meeting this stub is filed under `evidence/tape/` with a DATA_GATE amendment:
- **QUANT = HOLD** (designs allowed; no run)
- Claim Pass on speech/chart Observed may proceed without the tape

## Acceptance path
1. Place raw files + checksum manifest in `evidence/tape/C_MNQ_20260310-20260311/` (or equivalent).
2. Write `META.md` filling SOURCE/TZ/GRANULARITY/DATE RANGE/INSTRUMENT/LIMITATIONS.
3. Ask DATA to amend `DATA_GATE_2026-09-13.md` (or new dated gate) → PASS WITH CONDITIONS for QUANT on this stream only.
