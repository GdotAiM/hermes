# Month 4 Slice 5 — full source copy

Display only. No new decision logic.

```python
def _month4_lines(c: DayContext) -> list:
    m4 = getattr(c, "month4", None)
    lines = ["## Month 4 (ICT arrays)", ""]
    if not m4:
        lines += ["- not attached", ""]
        return lines
    kinds = [a.kind for a in (m4.arrays or ()) if a.kind != "none"] or ["none"]
    so = m4.array_opportunity
    lines += [
        f"- **Catalog:** {', '.join(kinds)}",
        f"- **Pattern note:** {m4.pattern_note}",
        f"- **Rates:** {m4.interest_rate_effects}",
        f"- **Array opportunity:** {so.flag} ({so.reason}) — not a session ticket",
        "",
        "Month 4 describes the PD-array catalog. It does not select an M9 candidate.",
        "",
    ]
    return lines


```


Handoff: `"month4": asdict(c.month4) if c.month4 else None`

Desk:
- M4 catalog (`msM4Cat`)
- M4 opp (`msM4Opp`)

Test: briefing contains Month 4 header, fvg, liquidity_void, not-a-ticket language.
M9 gold unchanged.
