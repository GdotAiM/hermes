# Month 10 Slice 5 — briefing + handoff + desk

Display only. Briefing after Month 8.

```python
def _month10_lines(c: DayContext) -> list:
    m10 = getattr(c, "month10", None)
    lines = ["## Month 10 (ICT multi-asset)", ""]
    if not m10:
        lines += ["- not attached", ""]
        return lines
    mac = m10.multi_asset_context
    lines += [
        f"- **Identified multi-asset:** {m10.identified_multi_asset}",
        f"- **COT:** {m10.cot_reading}",
        f"- **Relative strength:** {m10.relative_strength}",
        f"- **Open interest:** {m10.open_interest}",
        f"- **Commodity seasonal:** {m10.commodity_seasonal_note}",
        f"- **Carrying charge:** {m10.carrying_charge_note}",
        f"- **Asset class:** {m10.asset_class}",
        f"- **Asset session:** {m10.asset_session_note}",
        f"- **Confluence:** {m10.multi_asset_confluence_note}",
        f"- **Options:** {m10.options_note}",
        f"- **Watchlist:** {m10.watchlist_note}",
        f"- **Multi-asset context:** {mac.flag} ({mac.reason}) — not a session ticket",
        "",
        "Month 10 describes multi-asset context. It does not select an M9 candidate or write M5/M6 fields.",
        "",
    ]
    return lines


```

Handoff month10. Desk chips M10 ctx / M10 asset.
