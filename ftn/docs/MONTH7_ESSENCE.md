# Month 7 essence note

March 2017: **ICT Short-Term Trading**.

Not eight strategies. One weekly operating process.

> Know the monthly/weekly draw and the dealing range (premium ↔ discount arrays) → name the **weekly range profile** you are watching → know how market-maker templates tend to engineer that week’s high or low (Mon–Wed) → blend IPDA lookbacks with those PD arrays → ask whether the run toward the objective is **low-resistance** → stay prepared for an intraweek reversal / overlapping model → take **one** quality short-term piece (OSOK) aimed at most of that weekly expansion. If no OSOK, drop to the day-trade stack we already have (M8/M9).

If you cannot name the weekly draw and a dealing range, you do not force an OSOK.

---

## The eight lessons as stages

| # | Lecture | Role |
|---|---------|------|
| 1 | Monthly & weekly ranges | Short-term is ICT’s preferred style. Frame the week as a **dealing range**: monthly discount → weekly premium (bullish) or the inverse. PD arrays on M / W / D / 4H. Execution chart is still 60m. OSOK is weekly bread-and-butter; no OSOK → day trade. Seasonal tendency is a bonus, not a requirement. Mon–Wed high/low broken later in the week often confirms aggressive continuation. |
| 2 | Weekly range profiles | **ICT weekly profiles** — which day tends to print the week’s extreme, given HTF bias. Lecture opens with classic **Tuesday low** (bullish: Mon hovers above HTF discount, Tue drives into it) and classic **Tuesday high** (bearish mirror), then Wednesday variants. These are **not** Hermes `profile`. Same split we used for `ict_london_profile`. |
| 3 | MM manipulation templates | How the profile is *engineered*: run an old M/W/D pool, discount the news, then deliver to the opposing weekly/daily array. This is the playbook behind OSOK, not a separate bot. |
| 4 | IPDA + PD arrays | Blend 20 / 40 / 60-day IPDA windows with the PD matrix already on Market State. Lookbacks **qualify** the dealing range; they do not vote against day-trade IOF the way we refused a crude HTF majority in M9. |
| 5–6 | LRLR parts 1–2 | Is the path toward the weekly objective **low-resistance** (arrays giving way) or high-resistance (should idle / expect overlap)? This is a **gate on the weekly idea**, not a fifth M9 child. |
| 7 | Intraweek reversals & overlapping models | When the profile you chose is wrong: midweek reversal / overlap. Contrary scenario stays first-class — same discipline as M9 `scenarios.contrary`. |
| 8 | One Shot One Kill | One setup to pay the weekly objective. High or low of the week often Mon–Wed. Capture a large piece of the dealing range (guidance, not a pip cap law). 60m is the executable chart. |

---

## One paragraph the software must reconstruct

> “Monthly/weekly draw is X. Dealing range is this discount array → this premium array. ICT weekly profile being watched is Y (or none). Manipulation template expected: run this pool on this day. IPDA window in play: 20/40/60. LRLR: low / high / unclear. Intraweek contrary: …. OSOK opportunity flag true/false. HTF seed may already exist from M8.”

No `pick: OSOK` on the fixture.

---

## What this is not

- Not eight new children next to REV / CONSO / PIP20 / BB.  
- Not a replacement for M8 London or M9 DTR.  
- Not `Hermes profile = Tuesday_low`.  
- Not “OSOK selected ⇒ ignore session_ticket.” Different **horizon**.

```
Month 7  weekly / short-term context
        ↓
Month 8  ICT day
        ↓
Month 9  session models + paper ticket
```

If OSOK is live as a swing idea, M9 may still take **zero or one** session ticket that *seeds* it (`seed_only` already exists). OSOK must not silently become a second same-session scalp.

---

## Fields to specify later (blueprint, not code)

1. `dealing_range` — from_array / to_array / direction  
2. `ict_weekly_profile` — start with lecture-2 names + `none`; do not invent a 12-value enum until we list them from lessons 2–3  
3. `ipda_window` — 20 | 40 | 60 | none  
4. `lrlr` — low | high | unclear  
5. `intraweek_contrary` — watch | confirmed | none  
6. `osok_opportunity` — flag only  
7. Ticket kind — **open**: paper swing that may span sessions vs stay annotation-only until you freeze governance  

---

## Review questions

1. OSOK across sessions: separate `swing_ticket` kind, or annotation until a later phase?  
2. Weekly profile enum: freeze the Tuesday/Wednesday families from lecture 2 first, add lesson-3 templates as `manipulation_template`?  
3. LRLR “high resistance” → idle OSOK only, or also tighten M8 London gate? (Recommendation: **OSOK only** — don’t let M7 silently close London.)  
4. “~70–76% of weekly extremes Mon–Wed” → ICT guidance, same treatment as M8 “~2 setups/day”?

---

No blueprint and no `month7` module until this essence is signed (with answers to 1–4 if you already know them).
