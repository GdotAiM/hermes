# Month 1 Slice 5 — briefing + handoff + desk

Display only.

```python
def _month1_lines(c: DayContext) -> list:
    m1 = getattr(c, "month1", None)
    lines = ["## Month 1 (ICT foundation)", ""]
    if not m1:
        lines += ["- not attached", ""]
        return lines
    se = m1.setup_elements
    lines += [
        f"- **Identified setup elements:** {m1.identified_setup_elements}",
        f"- **Dealing-range side:** {m1.dealing_range_side}",
        f"- **Conditioning:** {m1.conditioning_note}",
        f"- **Focus:** {m1.focus_note}",
        f"- **Fair valuation:** {m1.fair_valuation_note}",
        f"- **Liquidity run:** {m1.liquidity_run_note}",
        f"- **Impulse:** {m1.impulse_note}",
        f"- **Protraction:** {m1.protraction_note}",
        f"- **Setup elements:** {se.flag} ({se.reason}) — not a session ticket",
        "",
        "Month 1 describes foundation context. It does not select an M9 candidate or overwrite Hermes profile.",
        "",
    ]
    return lines


```

Handoff month1. Desk chips M1 setup / M1 side.
