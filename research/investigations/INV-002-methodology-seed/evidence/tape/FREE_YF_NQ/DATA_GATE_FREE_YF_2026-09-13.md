# DATA GATE — FREE_YF_NQ (Wave 2)
**Gate ID:** DATA_GATE_FREE_YF_2026-09-13  
**Stream path:** `investigations/INV-002-methodology-seed/evidence/tape/FREE_YF_NQ/`  
**Owner:** DATA  
**Date:** 2026-09-13  
**Verdict:** **PASS WITH CONDITIONS**

## Scope
| Allowed | Forbidden |
|---------|-----------|
| INV-002 Wave 2 **H008 / H009 / H010** HTF / weekly / state pilots at **1wk / 1d / 1h** | Wave 1 **H001–H004** (need 1m + stream C) |
| Descriptive HTF liquidity / DOL / regime work on `NQ=F` (+ `QQQ` 1d cross-check) | INV-001 H1b / C90x 1m lunch hyps |
| QUANT designs + packaging on this resolution | Claiming Mar 2026 **MNQ** contract fidelity |

## Registry (verified 2026-09-13)

| Field | Value |
|-------|--------|
| SOURCE | Yahoo Finance via `yfinance` (keyless). Retrieval stamp in `META.json` `2026-09-13T10:09:30Z` |
| TIMEZONE | Daily/weekly: treat `Date` as **America/New_York** RTH calendar dates. 1h: timestamps already offset-aware (`-04:00` EDT on this pull) — still convert explicitly in code before session clocks |
| GRANULARITY | `NQ=F` **1wk**, **1d**, **1h**; `QQQ` **1d** only. **No 1m** |
| DATE RANGE | See file table below |
| INSTRUMENT | Primary: **`NQ=F`** continuous front-month proxy. Companion: **`QQQ`** equity ETF (not futures) |
| KNOWN LIMITATIONS | Continuous roll undocumented; ≠ MNQ Mar 2026; 1h ≈60d only; holiday/roll gaps possible; Yahoo OHLC is vendor-adjusted black box |

### Files (integrity check)

| File | Rows | Start | End | Dup timestamps | Mono non-dec | OHLC violations |
|------|------|-------|-----|----------------|--------------|-----------------|
| `NQ=F_1wk.csv` | 261 | 2021-09-13 | 2026-09-07 | 0 | yes | 0 |
| `NQ=F_1d.csv` | 502 | 2024-09-13 | 2026-09-11 | 0 | yes | 0 |
| `NQ=F_1h.csv` | 1121 | 2026-07-05 18:00-04:00 | 2026-09-11 16:00-04:00 | 0 | yes | 0 |
| `QQQ_1d.csv` | 501 | 2024-09-12 | 2026-09-11 | 0 | yes | 0 |

Columns: Date/Datetime, Open, High, Low, Close, Volume. No look-ahead columns observed.

## Conditions (must hold for any QUANT RUN)
1. **Resolution lock:** Do not upsample or invent 1m from this stream.
2. **Instrument lock:** State `NQ=F` continuous — never label results as MNQ Mar 2026 / stream C.
3. **QQQ:** Cross-check / SMT-style only; do not pool QQQ dollars with NQ points without an explicit transform hyp.
4. **1h “intraday”:** Hourly proxy only — not ICT 1m session delivery (Wave 2 brief already notes this).
5. **Event days:** If stratifying 2026 US dates, cite INV-001 `EVENT_CALENDAR_CPI_FOMC_NFP.md`.
6. **Reproducibility:** Re-pull may differ slightly; pin these CSVs + `META.json` hash for a given run memo.
7. **Packaging:** CASSANDRA packaging + ORION protocols still required before SURVIVES/FAILS language.

## Flags
| Flag | Detail |
|------|--------|
| SUSPICIOUS | Continuous futures — roll path unknown |
| AMBIGUOUS | Daily bar timezone = calendar date assumption (Yahoo session labeling) |
| MISSING | 1m tape; contract-month MNQ; full multi-year 1h |
| INCONSISTENT | Fail if any Wave 1 protocol cites this stream as stream C substitute |

## Relation to stream C / Wave 1 shared tape
- Physical stack for Wave 1 remains `INV-001 …/tape/STREAM_C_REQUIREMENTS.md` + `WAVE1_SHARED_TAPE_REQUIREMENTS.md`.
- FREE_YF_NQ is a **separate** keyless HTF pilot stream — not a fork of stream C.

## Verdict line for ORION / QUANT
**PASS WITH CONDITIONS** — Wave 2 HTF only (H008–H010). **NOT** cleared for Wave 1 1m hyps.
