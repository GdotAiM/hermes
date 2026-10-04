# Month 7 Slice 9 — full source copy

Display only. No candidate, no session ticket, no size.

## 1. Briefing — `_month7_lines` in src/ftn/os/briefing.py

Inserted before `_month8_lines`. Call site: `lines += _month7_lines(c)` then `_month8_lines`.

```python
def _month7_lines(c: DayContext) -> list:
    m7 = getattr(c, "month7", None)
    lines = ["## Month 7 (ICT week)", ""]
    if not m7:
        lines += ["- not attached", ""]
        return lines
    dr = m7.dealing_range
    wp = m7.ict_weekly_profile
    tm = m7.manipulation_template
    sw = m7.swing_ticket
    lines += [
        f"- **Dealing range:** {dr.from_array_id} ({dr.from_tf}) → {dr.to_array_id} ({dr.to_tf}) {dr.direction}",
        f"- **IPDA:** {m7.ipda_window.days}",
        f"- **ICT weekly profile:** `{wp.name}` ({wp.state})",
        f"- **Manipulation template:** `{tm.name}`",
        f"- **LRLR:** {m7.lrlr.state}",
        f"- **Intraweek contrary:** {m7.intraweek_contrary.state}",
        f"- **OSOK opportunity:** {m7.osok_opportunity.flag} ({m7.osok_opportunity.reason}) — not a session ticket",
        f"- **Swing ticket:** {sw.id if sw else 'none'}",
        "",
        "Month 7 describes the week. It does not select an M9 candidate.",
        "",
    ]
    return lines
```

DTR uses persist=False, so briefing swing id is `none` unless a file already exists from Slice 7 tests.

## 2. Handoff — src/ftn/os/handoff.py

```python
"month7": asdict(c.month7) if c.month7 else None,
```

## 3. Desk HTML

```html
<li><span class="read-label">M7 week</span><span class="read-body" id="msM7Profile">—</span></li>
<li><span class="read-label">M7 LRLR</span><span class="read-body" id="msM7Lrlr">—</span></li>
<li><span class="read-label">M7 OSOK</span><span class="read-body" id="msM7Osok">—</span></li>
```

## 4. Desk JS

```javascript
  var m7 = s.month7 || {};
  if ((el7 = document.getElementById("msM7Profile"))) el7.textContent = (m7.ict_weekly_profile && m7.ict_weekly_profile.name) || "—";
  if ((el7 = document.getElementById("msM7Lrlr"))) el7.textContent = (m7.lrlr && m7.lrlr.state) || "—";
  if ((el7 = document.getElementById("msM7Osok"))) el7.textContent = m7.osok_opportunity ? String(m7.osok_opportunity.flag) : "—";
```

Missing `OS_STATE.month7` → em dash.

## 5. Test

```python
assert "## Month 7 (ICT week)" in md
assert "classic_tuesday_low_of_week" in md
assert "not a session ticket" in md
```

M9 gold still matches.

## Next

Slice 10 — CASES_M7 reconstruction freeze. Engine must not read *.expected.json.
