# Month 6 blueprint

Essence frozen. This is the implementation contract **after** Slice 0 glossary is signed.

M6 is optional `DayContext.month6`. It does not persist tickets. It does not enter M9 arbitration.

---

## Invariants (from essence)

- `swing_opportunity` = annotation only  
- no `paper_swing_m6`  
- Million-Dollar = gated composite, not a candidate  
- `swing_family` = bull | bear | none  
- market_selection = suitable | unsuitable | unclear  
- risk = references only  
- M7/M8/M9 golds must stay green  

```
raw weekly/monthly evidence
        ↓
S2  suitability + HTF draw
        ↓
S3  supporting evidence (required vs confirming)
        ↓
S4  swing_family + sequential pattern
        ↓
S5  classic approach notes + risk frame
        ↓
S6  Million-Dollar composite gate
        ↓
S7  swing_opportunity flag
        ↓
S8  DTR attach persist=False / no ticket
        ↓
S9  briefing + desk
        ↓
S10 reconstruction freeze
```

Slice 0 is glossary only. No `m6_contracts.py` until S0 is signed.

---

## Proposed slices (after S0)

| Slice | Deliverable | Must not |
|-------|-------------|----------|
| 0 | Glossary (this file’s sibling) | Code |
| 1 | `m6_contracts.py` + optional DayContext.month6 + known-state fixture | Detectors |
| 2 | Suitability + HTF draw from labeled sponsorship | Name a family |
| 3 | Supporting-evidence flags (required vs confirming) | Mint Million-Dollar |
| 4 | swing_family + sequential pattern from labeled M/W/D alignment | Opportunity flag |
| 5 | Risk frame (stop/target references) | Sizing |
| 6 | Million-Dollar composite: all required gates or incomplete | Ticket |
| 7 | swing_opportunity from S2–S6 | Persist |
| 8 | DTR attach when monthly/swing evidence exists | Break golds / persist |
| 9 | Briefing `## Month 6` + desk chips | Buttons |
| 10 | CASES_M6 + no `.expected.json` in engine | New fields |

---

## Bind vs invent

**Bind:** `InstitutionalContext.sponsorship` monthly/weekly, PD matrix, origin arrays, M7 dealing range (read-only).

**Invent only on month6:** suitability, swing_family, sequential pattern, evidence flags, MD composite, risk references, swing_opportunity.
