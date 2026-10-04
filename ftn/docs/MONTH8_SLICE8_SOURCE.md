# Month 8 Slice 8 — full source copy

Expose Month 8 to the human. Display only. No new strategy, no ticket, no size.

Repo paths under `ftn-agent/`.

---

## What Slice 8 is

```
DayContext.month8
        │
        ├── briefing  ## Month 8 (ICT day)
        ├── handoff   market_state.month8
        └── desk      five Market State rail chips
```

Chips and markdown are **readouts**. They do not call `evaluate_candidates` and they do not write `session_ticket`.

---

## 1. `src/ftn/os/briefing.py` — `_month8_lines`

Inserted after the Market State list, before `## Scenarios`.

```python
def _month8_lines(c: DayContext) -> list:
    m8 = getattr(c, "month8", None)
    lines = ["## Month 8 (ICT day)", ""]
    if not m8:
        lines += ["- not attached", ""]
        return lines
    td = m8.ict_true_day
    cb = m8.cbdr
    g = m8.london_session_gate
    pr = m8.daily_extreme_projection
    ov = m8.htf_entry_overlap
    lines += [
        f"- **True day:** clock `{td.clock}` anchor `{td.day_anchor}`",
        f"- **Windows:** Asian {td.asian} · London KZ {td.london_kz} · NY AM {td.ny_am} · London Close {td.london_close} · CBDR {td.cbdr_window}",
        f"- **CBDR:** {cb.height_pips} pips · {cb.classification} · classic={cb.daytrade_classic} (`{cb.origin}`)",
        f"- **Asian height:** {m8.asian_height_pips} pips",
        f"- **London gate:** allowed={g.allowed} reason={g.reason} (`{g.origin}`)",
        f"- **ICT London profile:** `{m8.ict_london_profile}`",
        f"- **Projection:** draw={pr.draw} selected={pr.selected_level} source={pr.source_range} (`{pr.origin}`)",
        f"- **SD levels:** {list(pr.sd_levels)}",
        f"- **Day-trade opportunity flag:** {m8.daytrade_opportunity} (not a session ticket)",
        f"- **HTF overlap:** present={ov.present} {ov.array_id} {ov.timeframe} {ov.relationship}",
        "",
        "Month 8 describes the day. It does not select an M9 candidate.",
        "",
    ]
    return lines
```

Call site in `render_briefing`:

```python
        f"- **Target arrays:** {', '.join(c.opposing_target_arrays) or '—'}",
        "",
    ]
    lines += _month8_lines(c)
    lines += [
        "## Scenarios",
        ...
```

---

## 2. Path-fixture briefing excerpt (generated)

```
## Month 8 (ICT day)

- **True day:** clock `America/New_York` anchor `00:00`
- **Windows:** Asian ('20:00', '00:00') · London KZ ('01:00', '05:00') · NY AM ('07:00', '10:00') · London Close ('10:00', '12:00') · CBDR ('14:00', '20:00')
- **CBDR:** 26 pips · ideal · classic=True (`ict_source`)
- **Asian height:** 19 pips
- **London gate:** allowed=True reason=None (`ict_source`)
- **ICT London profile:** `normal_protraction_sell`
- **Projection:** draw=high selected=1.063 source=cbdr_bodies (`ict_source`)
- **SD levels:** [{'sd': 1, 'price': 1.063}, {'sd': 2, 'price': 1.0654}, {'sd': 3, 'price': 1.0678}]
- **Day-trade opportunity flag:** True (not a session ticket)
- **HTF overlap:** present=True D_FVG_bear daily seed_only

Month 8 describes the day. It does not select an M9 candidate.
```

---

## 3. Handoff — `src/ftn/os/handoff.py`

Inside `market_state`:

```python
            "scenarios": c.scenarios,
            "month8": asdict(c.month8) if c.month8 else None,
```

Hermes X can read the layer. It still must not write Market State.

---

## 4. Desk HTML — `desk/index.html` Market State list

Added rows (display only):

```html
<li><span class="read-label">M8 CBDR</span><span class="read-body" id="msM8Cbdr">—</span></li>
<li><span class="read-label">M8 London</span><span class="read-body" id="msM8London">—</span></li>
<li><span class="read-label">M8 profile</span><span class="read-body" id="msM8Profile">—</span></li>
<li><span class="read-label">M8 project</span><span class="read-body" id="msM8Proj">—</span></li>
<li><span class="read-label">M8 HTF</span><span class="read-body" id="msM8Htf">—</span></li>
```

Hermes `profile` chip (`#profileChip`) is unchanged. ICT London profile is a **separate** row.

---

## 5. Desk JS — `desk/js/app.js` inside `renderMarketState`

```javascript
  var m8 = s.month8 || {};
  var cb = m8.cbdr || {};
  var gate = m8.london_session_gate || {};
  var proj = m8.daily_extreme_projection || {};
  var ov = m8.htf_entry_overlap || {};
  var el;
  if ((el = document.getElementById("msM8Cbdr"))) el.textContent = (cb.height_pips != null ? cb.height_pips + " pips · " : "") + (cb.classification || "—");
  if ((el = document.getElementById("msM8London"))) el.textContent = gate.allowed === true ? "allowed" : (gate.allowed === false ? "avoid " + (gate.reason || "") : "—");
  if ((el = document.getElementById("msM8Profile"))) el.textContent = m8.ict_london_profile || "—";
  if ((el = document.getElementById("msM8Proj"))) el.textContent = (proj.draw || "—") + " " + (proj.selected_level != null ? proj.selected_level : "");
  if ((el = document.getElementById("msM8Htf"))) el.textContent = ov.present ? ((ov.array_id || "") + " · " + (ov.relationship || "seed_only")) : "—";
```

`OS_STATE` in `desk/js/os_state.js` may still be an older M9 snapshot without `month8`. Missing key → chips show "—". That is intended; the live brief/handoff is the source of truth.

---

## 6. Test — `test_month8_slice8_brief`

```python
def test_month8_slice8_brief():
    from ftn.os.briefing import brief_from_fixture
    _, _, md, *_ = brief_from_fixture(ROOT / "fixtures/m8_path_eurusd.json")
    assert "## Month 8 (ICT day)" in md
    assert "normal_protraction_sell" in md
    assert "seed_only" in md
    assert "not a session ticket" in md
```

M9 `test_reconstruct_matches_gold` still passes (gold does not assert briefing text).

---

## 7. What Slice 8 does not do

- No buttons that select REV / a London profile  
- No auto-refresh of `os_state.js` from DTR (optional later)  
- No reconstruction-suite table (Slice 9)

---

## 8. Next permitted

Slice 9 — freeze the M8 reconstruction matrix already covered by tests 1–8.
