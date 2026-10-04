# Month 2 Slice 5 — briefing + handoff + desk

Display only.

```python
def _month2_lines(c: DayContext) -> list:
    m2 = getattr(c, "month2", None)
    lines = ["## Month 2 (ICT risk frame)", ""]
    if not m2:
        lines += ["- not attached", ""]
        return lines
    fr = m2.low_risk_frame
    lines += [
        f"- **Small-account posture:** {m2.small_account_posture}",
        f"- **Identified low-risk:** {m2.identified_low_risk_frame}",
        f"- **Identified high-reward:** {m2.identified_high_reward_context}",
        f"- **Guidance:** {m2.monthly_return_guidance}",
        f"- **Psychology:** {m2.psychology_note}",
        f"- **Loss mitigation:** {m2.loss_mitigation_note}",
        f"- **Trap note:** {m2.trap_pattern}",
        f"- **Low-risk frame:** {fr.flag} ({fr.reason}) — not a session ticket",
        "",
        "Month 2 describes risk framing. It does not select an M9 candidate or size a position.",
        "",
    ]
    return lines


```

Handoff month2. Desk chip M2 frame.
