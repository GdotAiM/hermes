# Shared tape requirements — INV-002 Wave 1 (H001–H004)
**Owner:** DATA  
**Filed:** 2026-09-13  
**Status:** REQUIREMENTS STUB — tape **not filed**  
**Coordination:** **One physical tape stack** shared with INV-001 stream C. Do **not** maintain a second vendor dump.

## Design principle
| Layer | Location | Role |
|-------|----------|------|
| **Physical store** | Prefer `investigations/INV-001-2026-lectures/evidence/tape/` (stream C root) once human files data | Single SOURCE of OHLC |
| **INV-001 view** | `STREAM_C_REQUIREMENTS.md` | MNQ Mar 2026 · 1m · ET · ≥ 2026-03-10..11 (expand later) |
| **INV-002 view** | This file | Wave 1 H001–H004 date/session needs on **same** NQ/MNQ 1m America/New_York stack |

When stream C arrives, register once; both investigations **cite** the same META path. Expansion of date range for Wave 1 **extends** stream C, it does not fork it.

## Required registry fields (same discipline as stream C)

| Field | Wave 1 lock |
|-------|-------------|
| SOURCE | Named vendor/feed + path; shared with stream C META |
| TIMEZONE | UTC + **America/New_York** (DST-aware) |
| GRANULARITY | **1-minute** OHLC minimum |
| DATE RANGE | TBD after ATLAS claim extract — must cover RTH sessions needed for H001–H004 (pre-market 07:00–09:00 ET, RTH open→10:00, and 10:00 hour). Minimum: continuous enough history for power (QUANT to state N); **do not** invent dates before claims lock windows |
| INSTRUMENT | **MNQ or NQ** — prefer **MNQ** to stay identical to INV-001 stream C (Mar 2026 contract or documented continuous). If NQ used, document 2× scale vs MNQ and do not mix silently |
| KNOWN LIMITATIONS | Gaps, holidays, ETH vs RTH filter, roll/adjustment, no look-ahead |

## Wave 1 hyp → session needs (provisional until ATLAS Observed)

| Hyp | Working window (from BRIEF; **not Observed until claims**) | Tape need |
|-----|--------------------------------------------------------------|-----------|
| H001 | RTH 50% gap by **10:00 ET** | RTH from 09:30 + prior session for gap; 1m |
| H002 | **07:00–09:00** pre-market → RTH | ETH/pre-market bars required |
| H003 | One-side sweep of **7–9** range → opposite | Same as H002 + RTH continuation |
| H004 | First qualifying FVG in **10:00 hour** | 10:00–11:00 ET 1m |

**Soft rule:** Windows above are ORION backlog labels until claim cards Pass. Tape stub may list them as *target coverage*; QUANT must not treat them as lecture-Observed clocks without DATA Pass.

## Integrity checks (shared with stream C)
- No duplicate timestamps; monotonic within session  
- OHLC integrity; holiday calendar  
- Session filter explicit (ETH required for 7–9 work)  
- Alignable to INV-002 evidence video packs when demos show dates  
- Event stratification: cite INV-001 `EVENT_CALENDAR_CPI_FOMC_NFP.md` for CPI/FOMC/NFP when Wave 1 runs on 2026+ US dates  

## Anti-duplication checklist
- [ ] Single vendor archive path recorded in stream C META  
- [ ] INV-002 STATUS links that path (no copy of raw files into INV-002 unless symlink/pointer)  
- [ ] Continuous vs front-month policy identical across INV-001 and INV-002  
- [ ] Coverage projection (≥20 RTH days) computed once, reused  

## Gate
- QUANT Wave 1 **HOLD** until shared tape exists + META filled.  
- Claim extraction on the six golden videos may proceed on captions/video without tape.
