# Month 11 Slice 5 — briefing + handoff + desk

Display only. Briefing after Month 10.

```python
def _month11_lines(c: DayContext) -> list:
    m11 = getattr(c, "month11", None)
    lines = ["## Month 11 (ICT mega-trade)", ""]
    if not m11:
        lines += ["- not attached", ""]
        return lines
    mt = m11.mega_trade
    lines += [
        f"- **Family:** {m11.mega_trade_family}",
        f"- **Identified mega-trade:** {m11.identified_mega_trade}",
        f"- **Quarterly overlap:** {m11.quarterly_shift_overlap}",
        f"- **Seasonal overlap:** {m11.seasonal_overlap}",
        f"- **Relative strength:** {m11.relative_strength_note}",
        f"- **Mega-trade:** {mt.flag} ({mt.reason}) — not a session ticket",
        "",
        "Month 11 describes a mega-trade horizon. It does not select an M9 candidate or write M5 quarterly_shift.",
        "",
    ]
    return lines


```

Handoff month11. Desk chips M11 mega / M11 family.
