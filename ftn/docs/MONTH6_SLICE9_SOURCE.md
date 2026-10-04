# Month 6 Slice 9 — full source copy

Display only. No candidate, no ticket, no size.

## 1. Briefing — `_month6_lines` in src/ftn/os/briefing.py

Inserted before `_month7_lines`. Call site: `lines += _month6_lines(c)` then 7 then 8.

```python
def _month6_lines(c: DayContext) -> list:
    m6 = getattr(c, "month6", None)
    lines = ["## Month 6 (ICT swing)", ""]
    if not m6:
        lines += ["- not attached", ""]
        return lines
    rf = m6.risk_frame
    md = m6.million_dollar_swing
    so = m6.swing_opportunity
    lines += [
        f"- **Market selection:** {m6.market_selection.state}",
        f"- **HTF draw:** {m6.htf_draw}",
        f"- **Swing family:** `{m6.swing_family}`",
        f"- **Sequential pattern:** `{m6.sequential_pattern.name}` ({m6.sequential_pattern.state})",
        f"- **Risk:** stop={rf.stop_reference} target={rf.target_reference} frame={rf.reward_frame}",
        f"- **Million-Dollar:** {md.state} missing={list(md.missing)}",
        f"- **Swing opportunity:** {so.flag} ({so.reason}) — not a session ticket",
        "",
        "Month 6 describes the swing. It does not select an M9 candidate.",
        "",
    ]
    return lines
```

## 2. Handoff — src/ftn/os/handoff.py

```python
"month6": asdict(c.month6) if c.month6 else None,
```

## 3. Desk HTML

```html
<li><span class="read-label">M6 family</span><span class="read-body" id="msM6Family">—</span></li>
<li><span class="read-label">M6 MD</span><span class="read-body" id="msM6Md">—</span></li>
<li><span class="read-label">M6 opp</span><span class="read-body" id="msM6Opp">—</span></li>
```

## 4. Desk JS

```javascript
  var m6 = s.month6 || {};
  if ((el6 = document.getElementById("msM6Family"))) el6.textContent = m6.swing_family || "—";
  if ((el6 = document.getElementById("msM6Md"))) el6.textContent = (m6.million_dollar_swing && m6.million_dollar_swing.state) || "—";
  if ((el6 = document.getElementById("msM6Opp"))) el6.textContent = m6.swing_opportunity ? String(m6.swing_opportunity.flag) : "—";
```

Missing `OS_STATE.month6` → em dash.

## 5. Test

```python
assert "## Month 6 (ICT swing)" in md
assert "mw_bullish_daily_correcting" in md
assert "not a session ticket" in md
```

M9 gold still matches.

## Next

Slice 10 — CASES_M6 reconstruction freeze. Engine must not read *.expected.json.
