# Month 5 Slice 9 — full source copy

Display + DTR attach. No candidate, no ticket, no size.

Repo paths under `ftn-agent/`.

---

## What Slice 9 is

```
raw
 ↓
existing DTR (M9 + M8 + M7 + M6)
 ↓
position evidence?
    ├── month5 / ict_position
    ├── quarterly_shift
    ├── ipda_days
    ├── pair_institutional.sponsorship.monthly
    └── origin starts with M_
         ↓ yes
    derive_month5(raw_m5)   # S8 pipeline
         ↓
    replace(ctx, month5=..., month6=..., month7=..., month8=...)
         ↓
briefing / handoff / desk chips
```

`derive_month5` is the S8 pipeline. DTR does not persist a position file.

`M_` origin may also attach M6/M7. Separate fields.

---

## 1. DTR attach — src/ftn/os/dtr.py

```python
from ftn.os.m5_opportunity import derive_month5

    month5 = None
    inst_sp = ((raw.get("pair_institutional") or {}).get("sponsorship") or {})
    pos_ev = bool(
        raw.get("month5")
        or raw.get("ict_position")
        or raw.get("quarterly_shift")
        or raw.get("ipda_days")
        or inst_sp.get("monthly")
        or str(origin or raw.get("origin_pd_array") or "").startswith("M_")
    )
    if pos_ev:
        raw_m5 = dict(raw)
        raw_m5["evidence"] = ev
        if origin:
            raw_m5["origin_pd_array"] = origin
        month5 = derive_month5(raw_m5)
```

`replace(..., month5=month5)`.

---

## 2. Briefing — `_month5_lines` before Month 6

```python
def _month5_lines(c: DayContext) -> list:
    m5 = getattr(c, "month5", None)
    lines = ["## Month 5 (ICT position)", ""]
    if not m5:
        lines += ["- not attached", ""]
        return lines
    qs = m5.quarterly_shift
    ip = m5.ipda_window
    of_ = m5.open_float
    sw = m5.institutional_swing
    so = m5.position_opportunity
    lines += [
        f"- **Quarterly shift:** {qs.state} lookback={qs.lookback_months} {qs.direction}",
        f"- **IPDA:** {ip.days}",
        f"- **Open float:** buy={of_.buy_side} sell={of_.sell_side}",
        f"- **OF pools:** {list(m5.open_float_pools.pool_ids) or 'none'}",
        f"- **Institutional swing:** `{sw.kind}` entry={sw.entry_annotation}",
        f"- **Seasonal:** {m5.confirming.seasonal_tendency}",
        f"- **HTF PD:** {m5.htf_pd.dealing_range_tf} disc={m5.htf_pd.nearest_discount_id} prem={m5.htf_pd.nearest_premium_id}",
        f"- **Setup / entry:** {m5.setup_progression} / {m5.entry_technique}",
        f"- **Position opportunity:** {so.flag} ({so.reason}) — not a session ticket",
        "",
        "Month 5 describes the position. It does not select an M9 candidate.",
        "",
    ]
    return lines
```

---

## 3. Handoff — src/ftn/os/handoff.py

```python
"month5": asdict(c.month5) if c.month5 else None,
```

---

## 4. Desk HTML

```html
<li><span class="read-label">M5 QS</span><span class="read-body" id="msM5Qs">—</span></li>
<li><span class="read-label">M5 swing</span><span class="read-body" id="msM5Swing">—</span></li>
<li><span class="read-label">M5 opp</span><span class="read-body" id="msM5Opp">—</span></li>
```

## 5. Desk JS

```javascript
  var m5 = s.month5 || {};
  if ((el5 = document.getElementById("msM5Qs"))) el5.textContent = (m5.quarterly_shift && m5.quarterly_shift.state) || "—";
  if ((el5 = document.getElementById("msM5Swing"))) el5.textContent = (m5.institutional_swing && m5.institutional_swing.kind) || "—";
  if ((el5 = document.getElementById("msM5Opp"))) el5.textContent = m5.position_opportunity ? String(m5.position_opportunity.flag) : "—";
```

Missing `OS_STATE.month5` → em dash.

---

## 6. Test — test_month5_slice9_dtr_brief

```python
ctx = build_context(ROOT / "fixtures/m5_evidence_eurusd.json")
assert ctx.month5 is not None
assert ctx.month5.position_opportunity.flag is True
assert ctx.session_ticket is None
assert "## Month 5 (ICT position)" in md
assert "not a session ticket" in md
```

M9 gold still matches.

---

## 7. What Slice 9 does not do

- No CASES_M5 freeze (Slice 10)
- No persist / paper_position_m5
- No `evaluate_candidates` row
- Does not require `ctx.month5` on M9 fixtures

---

## Next permitted

Slice 10 — CASES_M5 reconstruction freeze. Engine must not read `*.expected.json`.
