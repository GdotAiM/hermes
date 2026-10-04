# Month 8 implementation blueprint

ICT Day Trading Model as a **layer on the existing OS**, not a second agent.

Source of truth for decisions: signed essence + Slice 1–3 freeze.  
This document says how we implement what is already locked, and how the remaining slices attach. It does not reopen architecture.

---

## 1. What Month 8 is

One process:

```
WEEKLY / DAILY DRAW
        ↓
ICT TRUE DAY          (NY clock, day_anchor 00:00)
        ↓
CBDR + ASIAN          (measurements)
        ↓
LONDON GATE           (allow / avoid + provenance)
        ↓
ICT LONDON PROFILE    (post-00:00 path + IOF)
        ↓
DAILY EXTREME PROJECTION   (not built yet)
        ↓
DAY-TRADE OPPORTUNITY      (flag only; not a ticket)
        ↓
OPTIONAL HTF OVERLAP       (annotate only; not built yet)
```

It is **not** eight strategies and **not** four new children next to REV / CONSO / PIP20 / BB.

```
                 MONTH 8
       ICT DAY-TRADE CONTEXT
                 │
          DayContext.month8
                 │
                 ▼
              MONTH 9
     sentiment / profile / candidates
     session_ticket / FTN / mint draft
```

Hermes `profile` (expansion | consolidation | reversal_watch | continuation | unclear) and `ict_london_profile` stay **two fields**.

---

## 2. Frozen laws (do not reopen)

| Decision | Freeze |
|----------|--------|
| ~2 setups / day | ICT **guidance** on `Month8State.ict_guidance`. Not a cap. |
| Session ticket | Hermes: 1 selected entry / session / pair. Independent. |
| CBDR &lt; 40 | `ideal`, classic London condition, `ict_source` |
| CBDR 40–&lt;50 | `expanded`, non-classic. Gate refuse-classic is **`hermes_interpretation`** |
| CBDR ≥ 50 | `wide`, London avoid, `ict_source` |
| NY-only days | `ict_london_profile=none` + gate avoid. **No** `ny_only_profile` |
| HTF overlap | Annotation / seed only. Never size. |
| Paper | Unchanged. Tickets ≠ orders. |

Locked sentence:

> CBDR &lt;40 is the classic condition; CBDR ≥50 is the explicit wide-CBDR avoidance condition (`ict_source`). The 40–&lt;50 band is expanded/non-classic and its treatment must be attributed as Hermes interpretation unless the lecture explicitly establishes it as a hard avoidance rule.

---

## 3. Contracts (Slice 1 — shipped)

File: `src/ftn/os/m8_contracts.py`

| Type | Role |
|------|------|
| `IctTrueDay` | NY `clock`, `day_anchor=00:00`, session windows. ICT day ≠ MT4 midnight. |
| `CbdrState` | height / body / wick + `classification` + `daytrade_classic` |
| `LondonGate` | `allowed`, `reason`, `origin` |
| `DailyExtremeProjection` | `draw` high\|low\|none, SD levels, source range |
| `HtfOverlap` | present, array, tf, `relationship=seed_only` |
| `Month8State` | the layer hung on `DayContext.month8` |

`load_day_context` calls `parse_month8(raw)`. No `month8` / `ict_day` block → `month8 is None`. **M9 fixtures unchanged.**

`classify_cbdr(height)` is the only helper allowed in the contracts file.

### Two fixture kinds (do not conflate)

| File | Kind | Purpose |
|------|------|---------|
| `fixtures/m8_reconstruction_eurusd.json` | **known-state** | Schema. May contain gate / profile / opportunity / projection as *provided* state. Not evidence-only. |
| `fixtures/m8_evidence_eurusd.json` | **evidence** | Measurements only. No gate, profile, opportunity, projection. |
| `fixtures/m8_path_eurusd.json` | **path evidence** | Evidence + `path_after_anchor`. Still no profile name. |

No fixture may contain `pick` or `expected_winner`. Gold `*.expected.json` is harness-only. The engine must not open gold.

---

## 4. Slice 2 — environment (shipped)

File: `src/ftn/os/m8_detect.py`

**Inputs:** CBDR sizes, Asian height, ADR remaining, high-impact calendar.  
**Outputs:** `cbdr.classification`, `london_session_gate`.  
**Must not output:** `ict_london_profile`.

Gate order:

1. high-impact news → avoid, `ict_source`  
2. wide (≥50) → avoid, `ict_source`  
3. Asian &gt; 40 pips → avoid, `ict_source` (`poor_consolidation`)  
4. ADR remaining ≤ 0 → avoid, `ict_source`  
5. expanded (40–&lt;50) → avoid, **`hermes_interpretation`**  
6. ideal (&lt;40) → allow, `ict_source`

Test that must not regress:

`derive_month8_measures(path_fixture).ict_london_profile == "none"`

---

## 5. Slice 3 — London profile (shipped, frozen)

File: `src/ftn/os/m8_profile.py`

**Inputs:** Slice 2 state + daytrade IOF + `evidence.path_after_anchor`.  
**Outputs:** `ict_london_profile`, and `daytrade_opportunity` only when profile ≠ none **and** gate allowed.

Path observations (not a profile name):

```
anchor: 00:00
clock: America/New_York
first_move: up | down | none
higher_high_vs_asian_or_cbdr
lower_low_vs_asian_or_cbdr
move_started_by_0200
window
```

Classifier:

| Gate | IOF | first_move | HH/LL + by 02:00 | Result |
|------|-----|------------|------------------|--------|
| closed | * | * | * | `none` |
| open | * | missing / none | * | `none` |
| open | bearish | up | yes | `normal_protraction_sell` |
| open | bearish | up | no | `delayed_protraction_sell` |
| open | bullish | down | yes | `normal_protraction_buy` |
| open | bullish | down | no | `delayed_protraction_buy` |
| open | mismatch | | | `none` |

**Guard that must not regress:**

```
evidence fixture + forced bearish IOF + no path
  → derive_month8_profile() → none
```

`daytrade_opportunity` is a **layer flag**, not a session ticket and not an arbiter winner.

### Open research (do not change classifier in Slice 3)

`bearish + up + not classic early rally` currently maps to **delayed**, not **none**. That may be stronger than the lecture. Revisit only in Slice 4 against lecture/path examples.

---

## 6. Remaining slices (ordered)

Do not start these until the previous slice is signed.

### Slice 4 — delayed vs none (research)

Question: is “up / down after 00:00 but not classic early range-take” delayed protraction or insufficient evidence?

Deliverable: 2–3 path fixtures (late rally, no HH, first_move only) + a written call.  
Change `classify_london_profile` only if the lecture supports it. Tag the rule `ict_source` or `hermes_interpretation`.

### Slice 5 — daily extreme projection

From CBDR height (prefer bodies) emit SD 1/2/3 **in the IOF direction**:

- bearish IOF → `draw=high` (sell day projects the high)  
- bullish IOF → `draw=low`

`selected_level` is context, not an entry. Same job FTN later names as numbers; M8 parent is CBDR.

Do not invent a fifth model.

### Slice 6 — HTF overlap annotate

If `origin_pd_array` / daily matrix overlaps the day-trade idea, set `htf_entry_overlap.present=true`, `relationship=seed_only`.  
Never change size language. Never raise caps.

### Slice 7 — DTR wiring

In `build_context`, if measurements exist:

```
ctx = replace(ctx, month8=derive_month8_profile(raw))
```

If no M8 block and no CBDR/Asian ranges, leave `month8=None`.  
**M9 gold candidate states must still pass.** Month 8 may idle London; it must not flip REV/CONSO/PIP20/BB by itself.

### Slice 8 — briefing + desk

Briefing section `## Month 8 (ICT day)`:

- true day windows  
- CBDR class + pips + origin of gate  
- `ict_london_profile`  
- projection (once Slice 5 exists)  
- HTF seed flag  

Desk: extra chips on the Market State rail. Not a second desk. Not a strategy picker.

### Slice 9 — reconstruction suite

One test file or CASES rows:

| Fixture | Expect |
|---------|--------|
| known-state | schema / parse |
| evidence | class + gate, profile none |
| path | normal_protraction_sell |
| no-path + bearish IOF | profile none |
| wide CBDR | avoid, ict_source |
| expanded CBDR | avoid, hermes_interpretation |

Engine never reads `*.expected.json`.

---

## 7. What we will not build

- `m8-agent` repo or a second orchestrator  
- `ny_only_profile`  
- M8 children competing in `evaluate_candidates`  
- Auto size from HTF overlap  
- Hard law `max_trades=2`  
- Collapsing Hermes `profile` into London profile  
- Treating Slice 1 known-state fixture as proof that detectors work  

---

## 8. File map (now)

```
src/ftn/os/m8_contracts.py     Slice 1
src/ftn/os/m8_detect.py        Slice 2
src/ftn/os/m8_profile.py       Slice 3
src/ftn/os/contracts.py        DayContext.month8 optional
fixtures/m8_reconstruction_eurusd.json          known-state
fixtures/m8_evidence_eurusd.json                evidence
fixtures/m8_path_eurusd.json                    path evidence
fixtures/m8_*.expected.json                     harness only
docs/MONTH8_ESSENCE.md
docs/MONTH8_CONTRACTS.md
docs/MONTH8_40_50.md
docs/MONTH8_SLICE3_FREEZE.md
docs/MONTH8_BLUEPRINT.md                        this file
```

---

## 9. How a day should read when this is fully wired

> Weekly/daily IOF is bearish. ICT day is NY-anchored at 00:00. CBDR is 26 pips bodies → ideal (`ict_source`). Asian is 19. London allowed. After 00:00 price rallied and took the range high by 02:00 → `normal_protraction_sell`. Projected daily high at 1× CBDR. Day-trade opportunity flag true. HTF seed on Daily FVG (annotate). Hermes profile remains whatever M9 derived. Session ticket still one per session if an M9 model selects.

If Slice 3 cannot say that paragraph from evidence + path, the month is not implemented yet. Slices 1–3 already make the **profile sentence** reconstructable. Projection and HTF are the rest of the paragraph.

---

## 10. Next move

Slice 3 is frozen. Next signed step is **Slice 4 (delayed vs none)** or skip to **Slice 5 (projection)** if you want to leave delayed as Hermes-for-now.

Do not wire DTR until 4 or 5 is signed, so M9 golds stay a clean regression gate.
