# Month 12 Slice 5 — briefing + handoff + desk

Display only. Briefing after Month 11.

```python
def _month12_lines(c: DayContext) -> list:
    m12 = getattr(c, "month12", None)
    lines = ["## Month 12 (ICT top-down)", ""]
    if not m12:
        lines += ["- not attached", ""]
        return lines
    td = m12.top_down
    lines += [
        f"- **Long-term:** {m12.long_term_note}",
        f"- **Intermediate-term:** {m12.intermediate_term_note}",
        f"- **Short-term:** {m12.short_term_note}",
        f"- **Intraday:** {m12.intraday_note}",
        f"- **Identified top-down:** {m12.identified_top_down}",
        f"- **Top-down:** {td.flag} ({td.reason}) — not a session ticket",
        "",
        "Month 12 describes a top-down reading. It does not select an M9 candidate or write M5–M11 fields.",
        "",
    ]
    return lines


```

Handoff month12. Desk chips M12 top / M12 id.
