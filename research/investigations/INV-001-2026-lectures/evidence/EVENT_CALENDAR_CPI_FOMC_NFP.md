# Event calendar — CPI / FOMC / NFP (INV-001)
**Path for QUANT H1b cite:** `investigations/INV-001-2026-lectures/evidence/EVENT_CALENDAR_CPI_FOMC_NFP.md`  
**Machine table:** `EVENT_CALENDAR_CPI_FOMC_NFP_2026.csv` (same folder)  
**Owner:** DATA  
**Filed:** 2026-09-13  
**Timezone:** **America/New_York** (store event local wall-clock; DST-aware — e.g. 2026-03-11 = **EDT**)  
**Status:** **STUB + 2026 schedule populated** from official BLS / Fed calendars. Soft run gate for H1b.  
**Coverage projection:** waits until stream C has **≥20 RTH days** (ORION). Stream C tape still human-pending.

## SOURCE / TIMEZONE / GRANULARITY / DATE RANGE / INSTRUMENT / LIMITATIONS

| Field | Value |
|-------|-------|
| SOURCE | CPI: https://www.bls.gov/schedule/news_release/cpi.htm · NFP (Employment Situation): https://www.bls.gov/schedule/news_release/empsit.htm · FOMC: https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm (tentative schedule press release 2024-08-09) |
| TIMEZONE | America/New_York |
| GRANULARITY | Calendar **date** of release/decision (primary exclusion key). Optional clock: CPI/NFP **08:30 ET**; FOMC statement **~14:00 ET** / presser **~14:30 ET** on decision day |
| DATE RANGE | Calendar year **2026** fully listed below; expand prior/next years only with same official sources before OOS on those years |
| INSTRUMENT | N/A (macro calendar). Used to stratify **MNQ** session tests under H1b |
| KNOWN LIMITATIONS | Schedules can revise; unscheduled FOMC / emergency meetings not listed; other events (PPI, PCE, minutes-only days) **not** in primary exclusion set unless ORION expands; half-days/holidays excluded separately in H1b §7 |

## H1b use rules (locked intent)
Cite this file from `experiments/QUANT_H1b_C015_PROTOCOL_2026-09-13.md` §7.

| Stratum | Rule |
|---------|------|
| **Primary** | Non-event RTH days: date **not** in CPI ∪ FOMC_decision ∪ NFP |
| **CPI-only** | Descriptive stratum |
| **NFP-only** | Descriptive stratum |
| **FOMC decision** | Exclude from primary (contamination) |
| **All-days pooled** | Descriptive only; if flips vs primary → **EVENT-SENSITIVE** |
| **Pilot 2026-03-10..11** | Plumbing only — **2026-03-11 is CPI** (Feb 2026 CPI, 08:30 ET). No SURVIVES/FAILS / OOS decision metrics on these dates |
| **OOS decision** | Forbidden until this calendar is cited in the run memo **and** stream C coverage projection (≥20 RTH days) exists |

## Soft run gate
| Gate | Status |
|------|--------|
| Event calendar file exists | **CLEAR** (this file) |
| Stream C tape filed | **BLOCKED** (human) |
| Coverage projection ≥20 RTH days | **BLOCKED** until stream C |
| OOS / SURVIVES decision | **BLOCKED** until above |

---

## 2026 — CPI (BLS, 08:30 ET)

| event_date (ET) | event_type | reference_period | release_time_et | notes |
|-----------------|------------|------------------|-----------------|-------|
| 2026-01-13 | CPI | Dec 2025 | 08:30 | |
| 2026-02-13 | CPI | Jan 2026 | 08:30 | |
| **2026-03-11** | CPI | Feb 2026 | 08:30 | **Lecture C90xGr3kW8Y day; C-2026-012** |
| 2026-04-10 | CPI | Mar 2026 | 08:30 | |
| 2026-05-12 | CPI | Apr 2026 | 08:30 | |
| 2026-06-10 | CPI | May 2026 | 08:30 | |
| 2026-07-14 | CPI | Jun 2026 | 08:30 | |
| 2026-08-12 | CPI | Jul 2026 | 08:30 | |
| 2026-09-11 | CPI | Aug 2026 | 08:30 | |
| 2026-10-14 | CPI | Sep 2026 | 08:30 | |
| 2026-11-10 | CPI | Oct 2026 | 08:30 | |
| 2026-12-10 | CPI | Nov 2026 | 08:30 | |

## 2026 — NFP / Employment Situation (BLS, 08:30 ET)

| event_date (ET) | event_type | reference_period | release_time_et | notes |
|-----------------|------------|------------------|-----------------|-------|
| 2026-01-09 | NFP | Dec 2025 | 08:30 | |
| 2026-02-11 | NFP | Jan 2026 | 08:30 | |
| 2026-03-06 | NFP | Feb 2026 | 08:30 | Before lecture week |
| 2026-04-03 | NFP | Mar 2026 | 08:30 | |
| 2026-05-08 | NFP | Apr 2026 | 08:30 | |
| 2026-06-05 | NFP | May 2026 | 08:30 | |
| 2026-07-02 | NFP | Jun 2026 | 08:30 | |
| 2026-08-07 | NFP | Jul 2026 | 08:30 | |
| 2026-09-04 | NFP | Aug 2026 | 08:30 | |
| 2026-10-02 | NFP | Sep 2026 | 08:30 | |
| 2026-11-06 | NFP | Oct 2026 | 08:30 | |
| 2026-12-04 | NFP | Nov 2026 | 08:30 | |

## 2026 — FOMC decision days (Fed; statement ~14:00 ET)

Exclusion key = **decision day** (second day of two-day meeting).

| meeting | decision_date (ET) | event_type | SEP | notes |
|---------|-------------------|------------|-----|-------|
| 2026-01-27..28 | 2026-01-28 | FOMC | no | |
| 2026-03-17..18 | 2026-03-18 | FOMC | yes | After lecture pilot week |
| 2026-04-28..29 | 2026-04-29 | FOMC | no | |
| 2026-06-16..17 | 2026-06-17 | FOMC | yes | |
| 2026-07-28..29 | 2026-07-29 | FOMC | no | |
| 2026-09-15..16 | 2026-09-16 | FOMC | yes | MACRO track (separate from INV-001 session hyps) |
| 2026-10-27..28 | 2026-10-28 | FOMC | no | |
| 2026-12-08..09 | 2026-12-09 | FOMC | yes | |

## Explicitly not Observed / not auto-excluded
- FOMC **minutes** release days (unless ORION expands set)
- PPI, PCE, retail sales, etc.
- Chart-only 11:30 lunch start (unrelated)

## Changelog
- 2026-09-13: Initial stub + full 2026 CPI/NFP/FOMC tables for H1b soft gate (DATA).
