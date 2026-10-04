# Month 7 blueprint (essence frozen)

Short-term / weekly layer on the existing OS.  
Not a second agent. Not a sixth M9 child.

Essence signed with four governance decisions. This document is the implementation contract.  
**Do not invent the full `ict_weekly_profile` enum in production code until Slice 0 lists names from lessons 2–3.**

---

## Frozen laws

| Question | Freeze |
|----------|--------|
| OSOK across sessions | Separate paper `swing_ticket` kind. Own lifecycle. Not an M9 candidate. Not a second `session_ticket`. |
| Day-trade seed | `htf_entry_overlap.relationship = seed_only` does **not** auto-create `swing_ticket`. |
| Weekly profiles | Lesson-2 **families** first. Lesson-3 = `manipulation_template`, separate field. |
| LRLR high resistance | Gates **OSOK only**. Never writes M8 `london_session_gate`. |
| Mon–Wed extreme ~70–76% | `ict_guidance` only. Not `after_wednesday → no_trade`. |
| Paper | Unchanged. Tickets ≠ orders. Dual live locks unchanged. |
| Hermes `profile` | Unchanged. Distinct from `ict_weekly_profile`. |

Invariant:

> Month 7 describes the weekly opportunity. Month 8 describes the day. Month 9 governs session execution. OSOK is a weekly-horizon paper position.

```
EXISTING FTN OS
        │
   ┌────┴────┐
   M7 weekly     M8 ICT day
   context       context
   └────┬────┘
        ▼
      M9 session OS
        │
   0 or 1 session_ticket
        │
   optional seed_only
        │
   separate swing_ticket (OSOK)
```

---

## Contracts (to add as `src/ftn/os/m7_contracts.py`)

Optional `DayContext.month7`. Absence = M7 not attached. M8/M9 golds must not require it.

```
DealingRange
  from_array_id: str | None
  from_tf: monthly | weekly | daily | none
  to_array_id: str | None
  to_tf: ...
  direction: bullish | bearish | unclear
  origin: ict_source

IctWeeklyProfile   # VALUES NOT FROZEN — Slice 0
  name: str          # only names from the Slice 0 glossary
  state: watching | invalidated | none
  origin: ict_source

ManipulationTemplate
  name: str | none   # Lesson 3, separate from weekly profile
  pool_tf: monthly | weekly | daily | none
  origin: ict_source

IpdaWindow
  days: 20 | 40 | 60 | none
  origin: ict_source

Lrlr
  state: low | high | unclear
  origin: ict_source   # or hermes_interpretation if we later encode a heuristic

IntraweekContrary
  state: watch | confirmed | none
  origin: ict_source

OsokOpportunity
  flag: bool
  reason: str
  # true does NOT mint swing_ticket

SwingTicket          # Hermes governance, paper
  id: str
  kind: paper_swing
  module: OSOK
  opened: date
  status: open | closed | none
  # may persist across sessions
  # must not satisfy session_ticket law

Month7State
  dealing_range: DealingRange
  ict_weekly_profile: IctWeeklyProfile
  manipulation_template: ManipulationTemplate
  ipda_window: IpdaWindow
  lrlr: Lrlr
  intraweek_contrary: IntraweekContrary
  osok_opportunity: OsokOpportunity
  swing_ticket: SwingTicket | None
  ict_guidance: {
    weekly_extreme_mon_wed: "often ~70-76%",
    note: "guidance not hermes_governance"
  }
```

`session_ticket` stays on `DayContext` as today. `swing_ticket` lives only under `month7`.

---

## Slice 0 — terminology extract (before any detector)

Read lessons 2 and 3 only. Output a glossary markdown:

- Exact ICT names for weekly profiles (no community “12 profiles” until the lecture says them).  
- Exact template names from lesson 3.  
- Freeze those two lists. Then Slices 1+ may use them.

Provisional **watch list** (not frozen): classic Tuesday low / Tuesday high / Wednesday low / Wednesday high. Anything else waits on Slice 0.

---

## Implementation slices (after Slice 0)

Same discipline as M8: contracts → environment → path/profile → research correction → projection-like fields already in dealing range → wire → brief → reconstruction.

| Slice | Deliverable | Must not |
|-------|-------------|----------|
| **0** | Glossary from L2/L3 | Code detectors |
| **1** | `m7_contracts.py` + `DayContext.month7` optional + known-state fixture | Detectors |
| **2** | Dealing range + IPDA window from labeled HTF arrays | Name a weekly profile |
| **3** | Weekly profile from **week-to-date path** + HTF bias (needs day-of-week + Mon–Wed extremes). No-path → `none` | OSOK from bias alone |
| **4** | Manipulation template field | Merge into weekly profile |
| **5** | LRLR gate on OSOK flag only | Touch `london_session_gate` |
| **6** | `osok_opportunity` + contrary watch | Auto `swing_ticket` |
| **7** | `swing_ticket` persist (disk, like session_ticket) paper-only | M9 candidate row |
| **8** | DTR attach `month7=` when weekly evidence exists | Break M8/M9 golds |
| **9** | Briefing `## Month 7` + desk chips (weekly profile / LRLR / OSOK / swing) | Strategy buttons |
| **10** | `CASES_M7` + engine must not read `*.expected.json` | New features |

Reconstruction paragraph (no `pick`):

> Monthly/weekly draw is X. Dealing range A → B. Weekly profile Y or none. Template Z. IPDA 20/40/60. LRLR low/high. Contrary …. OSOK flag …. Swing ticket present/absent. M8 London still whatever M8 said.

---

## Bind vs invent

**Bind**

- `InstitutionalContext.sponsorship.weekly` / `.monthly`  
- `origin_pd_array`, PD matrix  
- M8 `htf_entry_overlap`  
- `session_ticket`  
- Paper / dual live locks  

**Invent only as M7 layer**

- dealing range object  
- ICT weekly profile + template  
- LRLR  
- swing_ticket  

---

## What we will not build

- `osok-agent` repo  
- `OSOK` as `evaluate_candidates` module  
- LRLR writing M8 London  
- `max_day = Wednesday`  
- 12-value enum copied from blogs  
- Auto size because OSOK  
- Swing ticket that counts as the session ticket  

---

## Next move

**Slice 0 only:** glossary from lessons 2–3.  
Then Slice 1 contracts. No DTR until 8.
