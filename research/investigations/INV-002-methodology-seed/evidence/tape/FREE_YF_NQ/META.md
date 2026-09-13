# Tape stream — FREE_YF_NQ (keyless)

| Field | Value |
|-------|--------|
| SOURCE | Yahoo Finance via `yfinance` (no API key) |
| INSTRUMENT | `NQ=F` continuous (primary); `QQQ` daily cross-check |
| TIMEZONE | Daily = session calendar dates (treat as ET RTH days). Intraday: convert to America/New_York before clocks |
| GRANULARITY | 1wk / 1d / 1h (not 1m) |
| USE | INV-002 Wave 2: **H008, H009, H010** pilots |
| NOT FOR | Wave 1 H001–H004 / INV-001 H1b (need stream C 1m MNQ/NQ) |

## Known limitations
- Continuous futures rolls undocumented
- Not Mar 2026 MNQ contract tape
- 1h history short (~60d)
- No Asia/London session precision on daily bars

## Gate
DATA may PASS WITH CONDITIONS for Wave 2 HTF/weekly pilots only. QUANT RUN on H008–H010 allowed only after protocols + CASSANDRA packaging, and only on this stream’s resolution.

## DATA gate
**PASS WITH CONDITIONS** — see `DATA_GATE_FREE_YF_2026-09-13.md`
Wave 2 HTF only. Not for Wave 1 / stream C / 1m.
