from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from ftn.config_load import repo_root
from ftn.paths import journal_dir


def write_journal(payload: dict[str, Any]) -> Path:
    t = payload["ticket"]
    tpl = (repo_root() / "src" / "ftn" / "journal" / "_TEMPLATE_DECISION.md").read_text(
        encoding="utf-8"
    )
    levels = "\n".join(
        f"- L{lv['index']} `{lv['name']}` @ {lv['price']:.5f}" for lv in t.get("four_levels", [])
    ) or "- none"
    conf = t.get("pd_confluence") or []
    confluence = (
        "\n".join(f"- {h.get('name')} × {h.get('pd_array')} ({h.get('kind')})" for h in conf)
        or "- none"
    )
    reasons = t.get("no_trade_reasons") or []
    reason_txt = "\n".join(f"- {r}" for r in reasons) or "- none (candidate)"
    setup = t.get("setup") or {}
    setup_txt = "\n".join(f"- {k}: {v}" for k, v in setup.items()) or "- missing"
    body = (
        tpl.replace("{{DATE}}", payload["scanned_at"])
        .replace("{{SYMBOL}}", str(t.get("symbol")))
        .replace("{{BIAS}}", str(t.get("bias")))
        .replace("{{KIND}}", str(t.get("kind")))
        .replace("{{FAMILY}}", str(t.get("family")))
        .replace("{{LEVELS}}", levels)
        .replace("{{CONFLUENCE}}", confluence)
        .replace("{{SETUP}}", setup_txt)
        .replace("{{REASONS}}", reason_txt)
    )
    if "authority" in t:
        st = t.get("session_ticket") or {}
        body += (
            "\n## Ticket authority\n\n"
            f"- Authority: `{t.get('authority')}` (Month-9 kernel is the sole ticket authority)\n"
            f"- Selected: `{t.get('selected_module')}`  Session ticket: `{st.get('id')}`\n"
            f"- actionable_for_mint: {t.get('actionable_for_mint')}\n"
            f"- blocked_by: {t.get('blocked_by')}\n"
            f"- Legacy fixture gate (research only): {t.get('legacy_gate_ok')}\n"
        )
        tr = payload.get("trace") or {}
        if tr:
            body += "\n## Pipeline trace (ftn.trace.v1; context layers are annotation only)\n\n"
            body += "".join(f"- gate {g}\n" for g in (tr.get("gates") or {}).get("chain") or [])
            for stage in ("bias", "context"):
                for name, lay in (tr.get(stage) or {}).items():
                    if isinstance(lay, dict):
                        body += (f"- {stage}.{name}: role={lay.get('role')} feeds_rev={lay.get('feeds_rev')} "
                                 f"available={lay.get('available', True)}\n")
            res = tr.get("result") or {}
            body += f"- result: {res.get('status')} R={res.get('R')} (see `ftn results`; H016 forward R sealed)\n"
    out = journal_dir()
    path = out / f"{payload['scanned_at']}_DECISION.md"
    n = 1
    while path.exists():
        path = out / f"{payload['scanned_at']}_{n}_DECISION.md"
        n += 1
    path.write_text(body, encoding="utf-8")
    return path
