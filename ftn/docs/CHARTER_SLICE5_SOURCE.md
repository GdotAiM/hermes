# Charter Slice 5 — briefing + handoff + desk

Display only. After Month 12.

```python
def _charter_lines(c: DayContext) -> list:
    ch = getattr(c, "charter", None)
    lines = ["## Charter (ICT PAM)", ""]
    if not ch:
        lines += ["- not attached", ""]
        return lines
    cr = ch.charter_recognition
    pams = [e.pam_id for e in (ch.recognized_pams or ()) if e.pam_id != "none"] or ["none"]
    lines += [
        f"- **Identified PAM:** {ch.identified_pam}",
        f"- **Recognized:** {', '.join(pams)}",
        f"- **Model 13 bridge:** {ch.model13_bridge}",
        f"- **Charter recognition:** {cr.flag} ({cr.reason}) — not a session ticket",
        "",
        "Charter describes named model recognition. It does not select an M9 candidate or create a paper ticket.",
        "",
    ]
    for e in ch.recognized_pams or ():
        if e.pam_id == "none":
            continue
        lines += [
            f"- **{e.pam_id}** ({e.horizon}): primary={e.primary_lecture_note}, "
            f"amplified={e.amplified_note}, trade_plan={e.trade_plan_note}, "
            f"algo={e.algorithmic_theory_note}",
        ]
    if ch.recognized_pams:
        lines.append("")
    return lines


```

Handoff charter. Desk chips Charter / PAM.
