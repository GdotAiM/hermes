# Month-9 Day-Trade OS — Engineering Blueprint v2.1

**Status:** signed design **v2.1 freeze** (2026-09-16) — no modules implemented yet  
**Review note (2026-10-04):** the status line above is stale. M9 is implemented as `src/ftn/os/{contracts,dtr,sentiment,institutional,profile,candidates,session_ticket,...}.py` + `src/ftn/models/{rev,conso,bb,pip20,ftn}.py`; see `docs/SLICES.md`. §9 names `pd_matrix.py` / `arbiter.py`, which do not exist: the PD matrix is `contracts.PdMatrix` and the arbiter lives in `os/candidates.py`.  
**Existing code:** FTN engine + desk only  
**Style:** mint-agent — paper default, tickets ≠ orders  
**Source:** ICT Mentorship Core Content Month 09 (8 lessons)

v1 = five children + router.  
v2 = one OS + market state + candidates.  
v2.1 = five final review edits; stop redesigning; next step is a fixture test.

---

## 0. What Month 9 actually teaches

Not eight independent strategies. A day-trading **operating process**:

> Understand today's institutional context → sentiment and market state → liquidity and PD arrays → likely delivery → select an intradate model → use projections as objectives → keep the contrary scenario.

| # | Lesson | Role in the OS |
|---|--------|----------------|
| 1 | The Sentiment Effect | **First-class state** (was hidden in DTR/BB/PIP20) |
| 2 | Filling the Numbers | FTN objectives / annotation |
| 3 | 20 Pips Per Day | PIP20 execution model |
| 4 | Trading in Consolidations | CONSO execution model |
| 5 | Trading Market Reversals | REV execution model |
| 6-7 | Bread & Butter buy/sell | BB execution model |
| 8 | ICT Day Trade Routine | **Kernel / context builder** (DTR) |

---

## 0.1 Rule attribution

| `origin` | Meaning |
|----------|---------|
| `ict_source` | Stated in a Month-9 lesson |
| `hermes_interpretation` | Faithful compression of ICT into a field |
| `hermes_governance` | Our risk / research control — not ICT |
| `hermes_empirical` | Later finding from the research log |

Examples: contrary scenario = ict_source. One ticket per session = hermes_governance. Fade-to-EQ = ict_source. MSS as REV execution trigger = hermes_interpretation. Profile enum = hermes_interpretation. Williams %R(10) 15m as sentiment input = ict_source. Arbiter order = hermes_governance (default_preemption_policy).

---

## 1. Architecture

DTR is the kernel. Sentiment + InstitutionalContext + Profile produce Market State. REV / CONSO / BB / PIP20 are instantiable models. FTN is objectives. Arbiter selects one ticket and keeps losers in the research log.

```
DTR context
  -> SENTIMENT + INSTITUTIONAL CONTEXT + PROFILE
  -> MARKET STATE
  -> REV / CONSO / BB / PIP20
  -> FTN objectives
  -> CANDIDATE ARBITER
  -> selected ticket + suppressed log
```

---

## 2. Hard laws

ICT-aligned: context before model; contrary scenario; pivots are targets; fade-to-EQ; NY continues London unless HTF PD array; HTF PD = draw, LTF PD = timing; 20-pip is opportunity class not a promise; sentiment inputs include Asia, open, PD reaction, Williams %R(10) 15m.

Hermes governance: paper default; tickets != orders; one entry ticket per session per pair (session_ticket); no cap raise without human; no secrets; arbiter keeps suppressed candidates; children read Market State only.

---

## 3. Data contracts

### 3.1 DayContext

date, timezone=America/New_York, calendar[], watchlist[], focus_pair,
dxy { institutional, from premium|discount, relationship supportive|neutral|contradictory|unavailable, arrays[] },
pair { institutional },
origin_pd_array, opposing_target_arrays[],
opens {gmt0, ny_midnight},
ranges {cbdr, asian, flout, previous_day, swings_3d},
adr5, pd_matrix, sentiment,
profile: expansion|consolidation|reversal_watch|continuation|unclear,
scenarios {primary, contrary},
session_ticket.

DXY contradictory is context, not automatic idle.

### 3.2 Sentiment (Lesson 1)

direction, expected_delivery,
indicator { name: williams_r, period: 10, timeframe: m15, value, state },
reference_open gmt0|ny_midnight,
asian_range {high, low},
liquidity_probe { preferred_side, observed_side },
judas_side, reaction.pd_array_reaction,
basis: [williams_r, pair_iof, dxy, asian_range, opening_price, pd_array].

Williams %R is one input, not the engine.
Bullish expectation: liquidity often sought below open and/or Asian low, then higher. Bearish: above open and/or Asian high, then lower.
That is expected probe behavior, not a required sequence. preferred_side may differ from observed_side.

### 3.3 InstitutionalContext

sponsorship: monthly, weekly, daily, h4
daytrade_iof: daily, h4, m60
state + confidence derived from daytrade_iof ONLY.
Monthly/weekly never vote on daytrade state.
Daily primary; 4H witness; 60m noted, cannot flip daily.
Speak "Daily and 4H bullish; 60m conflicts" — never "2/3 vote".

### 3.4 PD matrix

htf: monthly, weekly, daily, h4
ltf: m60, m15, m5
confluences with stdev|adr|open|named_extreme
Lookback 20 daily days, 40 if spent.
origin_pd_array = leaving. opposing_target_arrays = draw.

---

## 4. DTR kernel

Builds Market State. No entry tickets.

1 calendar med/high
2 keep London/NY KZ news
3 DXY InstitutionalContext + PD + premium/discount + relationship
4 focus pair = news else watchlist else idle success
5 pair InstitutionalContext
6 origin + target arrays (null origin is a flag)
7 0 GMT open
8 NY midnight CBDR/Asian/Flout + midnight open
9 pd_matrix + LTF-STDEV confluence
10 Sentiment
11 Profile
12 primary + contrary scenarios
13 candidate pass — keep losers
14 journal briefing

Null origin_pd_array: flag PIP20/BB/FTN-entry blocked. REV self-gates. CONSO may fade. FTN annotate allowed.

---

## 5. Profile (hermes_interpretation)

Not an ICT enum. Combined from 20 Pips / CONSO / REV / BB distinctions.

expansion -> FTN/BB/PIP20
consolidation -> CONSO
reversal_watch -> REV
continuation -> BB/PIP20
unclear -> no execution; FTN may annotate

---

## 6. Models

FTN: four families; annotation-only after session_ticket; never wins entry on a number alone.

PIP20: +20 objective, 20-pip stop, raid + directional context; Asia NY-stops and NY expansion windows; raid_buffer 5 pips.

CONSO: fade_edge -> EQ only; expansion_inside -> opposite side; breakout_use -> next PD/FTN. REV inside box with HTF PD+MSS preempts CONSO.

REV eligibility (ict_source): named extreme raid + (HTF PD | NY/LC exception) + context.
REV execution (hermes_interpretation): LTF MSS.
Eight extremes. NY continues London by default.

BB: sponsorship + daytrade IOF + htf_pd + ltf_pd + liquidity_event + judas_event + engine offset|reacc + side + session + protraction_stage (ny_midnight | cme_0820 | london_close_1000 | gmt_0000 | none) + ADR-15 + 15-30 pips + <=2h + 5m.

---

## 7. Candidate arbiter

Pass A eligibility. Pass B default_preemption_policy:

  arbiter_policy: REV_preempts_CONSO_when_HTF_turn_confirmed
  REV execution-ready > CONSO > PIP20 > BB

Not a claim that REV is a better strategy.
States: selected | suppressed | invalidated | ineligible | annotate.
Always persist the full candidate_set.

---

## 8. Tickets

daily_briefing, market_state, candidate_set = not mint
reversal_candidate, range_candidate, scalp_candidate, bb_buy, bb_sell = mint if selected
ftn_annotation, no_trade = not mint

---

## 9. Layout

src/ftn/os/{dtr,sentiment,institutional,profile,pd_matrix,arbiter}.py
src/ftn/models/{ftn,pip20,conso,rev,bb}.py
CLI: python3 -m ftn brief | run

Desk default = Market State rail (sentiment, W%R, probe, institutional split, profile, DXY relationship, origin->targets, candidates, FTN overlays).

---

## 13. Build order

1. DayContext + InstitutionalContext + Sentiment + Profile + PD matrix (fixtures)
2. DTR briefing writer (no tickets)
3. Candidate logger
4. REV
5. BB
6. CONSO
7. PIP20
8. Existing FTN as annotation
9. Arbiter + session_ticket
10. Desk Market State rail

First test after slice 3: can Hermes reconstruct Month-9 reasoning from a fixture without being told which model should win?

No live broker path.


---

## 3.5 Market State immutability (`hermes_governance`)

Once the candidate pass begins, Market State is a **frozen snapshot**.

DTR builds Market State → snapshot → REV / CONSO / BB / PIP20 evaluate the SAME snapshot → Candidate Set → Arbiter.

No model may mutate profile, sentiment, InstitutionalContext, PD matrix, or origin/target arrays during evaluation. If a model needs a derived view, it returns it on its candidate record, not by writing back to DayContext.
