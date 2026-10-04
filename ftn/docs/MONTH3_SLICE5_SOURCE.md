# Month 3 Slice 5 — full source copy

Display only. No new decision logic.

Repo paths under `ftn-agent/`.

---

## What Slice 5 is

```
DayContext.month3
        ↓
briefing  ## Month 3 (ICT next setup)
handoff   market_state.month3
desk      M3 TF / M3 next chips
```

Reads S3 `next_setup`. Does not recompute the gate.

---

## 1. Briefing helper

```python
def _month3_lines(c: DayContext) -> list:
    m3 = getattr(c, "month3", None)
    lines = ["## Month 3 (ICT next setup)", ""]
    if not m3:
        lines += ["- not attached", ""]
        return lines
    ns = m3.next_setup
    lines += [
        f"- **Timeframe:** {m3.selected_timeframe}",
        f"- **IOF:** {m3.institutional_order_flow}",
        f"- **Sponsorship:** {m3.institutional_sponsorship}",
        f"- **Structure:** {m3.institutional_structure}",
        f"- **Macro→micro:** {m3.macro_to_micro}",
        f"- **Trap note:** {m3.trap_pattern}",
        f"- **Anticipated setup:** {m3.anticipated_setup}",
        f"- **Next setup:** {ns.flag} ({ns.reason}) — not a session ticket",
        "",
        "Month 3 describes institutional context and anticipation. It does not select an M9 candidate.",
        "",
    ]
    return lines
```

---

## 2. Handoff — src/ftn/os/handoff.py

```python
"month3": asdict(c.month3) if c.month3 else None,
```

---

## 3. Desk HTML

```html
<li><span class="read-label">M3 TF</span><span class="read-body" id="msM3Tf">—</span></li>
            <li><span class="read-label">M3 next</span><span class="read-body" id="msM3Next">—</span></li>
```

## 4. Desk JS

```javascript
var m3 = s.month3 || {};
  if ((el3 = document.getElementById("msM3Tf"))) el3.textContent = m3.selected_timeframe || "—";
  if ((el3 = document.getElementById("msM3Next"))) el3.textContent = m3.next_setup ? String(m3.next_setup.flag) : "—";
```

Missing `OS_STATE.month3` → em dash.

---

## 5. Test — test_month3_slice5_brief

```python
def test_month3_slice5_brief():
    from ftn.os.briefing import brief_from_fixture
    _, _, md, *_ = brief_from_fixture(ROOT / "fixtures/m3_evidence_eurusd.json")
    assert "## Month 3 (ICT next setup)" in md
    assert "Anticipated setup" in md
    assert "not a session ticket" in md
    assert "does not select an M9 candidate" in md
```

M9 gold unchanged.

---

## 6. What Slice 5 does not do

- No CASES_M3 freeze (Slice 6)
- No persist / paper_setup_m3
- No evaluate_candidates row
- No pair_institutional overwrite

---

## Status at S5

S1 parse → S2 context → S3 next_setup → S4 DTR → S5 display.
