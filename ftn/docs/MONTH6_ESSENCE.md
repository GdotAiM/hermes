# Month 6 essence — FROZEN

2017 ICT Core Content, Lessons 57–64. Swing / monthly horizon.

Not eight bots. One evidence-accumulation process.

---

## Canon URLs

| # | Lesson | URL |
|---|--------|-----|
| 1 | Ideal Swing Conditions For Any Market | https://www.youtube.com/watch?v=0juYnbKays0 |
| 2 | Elements To Successful Swing Trading | https://www.youtube.com/watch?v=Xs1i0aIeTME |
| 3 | Classic Swing Trading Approach | https://www.youtube.com/watch?v=g--tikwaupk |
| 4 | High Probability Swing Setups In Bull Markets | https://www.youtube.com/watch?v=osRUnIpGIJ0 |
| 5 | High Probability Swing Setups In Bear Markets | https://www.youtube.com/watch?v=soY9zX3gt2U |
| 6 | Reducing Risk & Maximizing Reward In Swing Setups | https://www.youtube.com/watch?v=JAjL7rUX2Iw |
| 7 | Keys To Selecting Markets That Will Move Explosively | https://www.youtube.com/watch?v=Hoo_wTMgdcY |
| 8 | The Million Dollar Swing Setup | https://www.youtube.com/watch?v=VL4YLTRerHY |

Lesson 3 ID is two ASCII hyphens: `g--tikwaupk`.

---

## Process (frozen)

```
Market suitability
        ↓
HTF directional sponsorship / draw
        ↓
Swing conditions + supporting evidence
  (HTF trend, IOF, rates, COT, PD arrays,
   seasonal tendency, intermarket — confirming,
   not all universally required)
        ↓
Bull / Bear sequential setup family
        ↓
Classic swing approach
  (PD-array spectrum + HTF alignment + LTF refinement)
        ↓
Risk / reward frame
        ↓
Explosive-market selection filter
        ↓
Million-Dollar Swing Setup
  (named HTF swing template — gated composite)
        ↓
swing_opportunity  true | false
```

Million-Dollar Setup is a **gated composite of evidence**, not another PD-array name.

---

## Layer map

```
M6  swing / monthly     DayContext.month6     annotation only
M7  weekly / OSOK       DayContext.month7     paper_swing
M8  ICT day             DayContext.month8     London / projection
M9  session             candidates            session_ticket
```

```
M6 swing_opportunity
        ≠
M7 OSOK
        ≠
M9 session candidate
        ≠
M9 session_ticket
        ≠
order
```

M6 does not write `session_ticket`. M6 does not write `paper_swing`. M6 does not enter `evaluate_candidates`.

---

## Frozen governance

| Decision | Choice |
|----------|--------|
| Ticket | Opportunity / annotation only. No `paper_swing_m6`. |
| Million Dollar | Named setup / template. Not a child that can beat REV/BB. |
| Bull / bear | One field: `swing_family = bull \| bear \| none` |
| Market selection | Suitability filter: `suitable \| unsuitable \| unclear`. No rank, no second router. |
| Risk | Guidance: stop_reference, target_reference, reward_frame. No lots. No broker. |

---

## What the software must reconstruct (later)

> Market suitability is X. HTF draw is Y. Supporting evidence present/absent. Swing family is bull/bear/none. Classic approach notes …. Risk frame: invalidation A, opposing objective B. Explosive-market filter: suitable/unsuitable. Million-dollar composite: assembled / incomplete. Swing opportunity true/false.

No `pick` key. No session ticket from this layer.

---

## Explicitly not frozen yet (Slice 0 / blueprint)

- Exact names of the three bullish sequential patterns and their bearish mirrors (extract from lessons 4–5 before the enum).
- Which Lesson-2 evidence items are required vs confirming.
- Exact Million-Dollar gate list (seasonal, major-market, intermarket, PD/IPDA, setup, management) — list from lesson 8, then freeze.

Those are glossary work. They do not reopen this essence.

---

## Next permitted

Blueprint + Slice 0 glossary from lessons 4, 5, and 8.  
No `m6_contracts.py` until that glossary is signed.
