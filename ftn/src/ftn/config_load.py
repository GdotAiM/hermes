"""config.yaml loader — stdlib only (PyYAML is not a dependency).

Parses the small YAML subset config.yaml actually uses (nested block mappings
by indentation, inline flow mappings ``{ k: v }``, block lists of scalars,
``#`` comments) and then validates it against an explicit schema. Anything
outside that subset, unknown keys, wrong types or out-of-range values raise
``ConfigError`` with the file and line instead of being silently ignored.

``load_config()`` returns the historical flat dict (``mode``, ``live_enabled``,
``min_atr_pips`` …) plus ``raw`` (the nested document) so callers don't change.
"""

from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any


class ConfigError(ValueError):
    """Invalid or unsupported config.yaml content."""


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def dispatch_out() -> Path:
    """FTN output dir (handoffs, session tickets). Delegates to ``ftn.paths.out_dir``
    (main's lazy resolution; ``FTN_OUT_DIR`` overrides)."""
    from ftn.paths import out_dir
    return out_dir()


# ---------------------------------------------------------------- parsing

_KEY = re.compile(r"^([A-Za-z_][A-Za-z0-9_]*)\s*:(?:\s+(.*))?$")


def _strip_comment(line: str) -> str:
    out, quote = [], None
    for ch in line:
        if quote:
            if ch == quote:
                quote = None
        elif ch in "\"'":
            quote = ch
        elif ch == "#":
            break
        out.append(ch)
    return "".join(out).rstrip()


def _scalar(text: str, where: str) -> Any:
    t = text.strip()
    if t == "":
        return None
    if (t[0] == t[-1]) and t[0] in "\"'" and len(t) >= 2:
        return t[1:-1]
    low = t.lower()
    if low in ("true", "yes"):
        return True
    if low in ("false", "no"):
        return False
    if low in ("null", "~"):
        return None
    if re.fullmatch(r"[-+]?\d+", t):
        return int(t)
    if re.fullmatch(r"[-+]?(\d+\.\d*|\.\d+|\d+)([eE][-+]?\d+)?", t):
        return float(t)
    if t[0] in "[{&*!|>%@`":
        raise ConfigError(f"{where}: unsupported YAML syntax {t!r}")
    return t


def _split_top(inner: str) -> list[str]:
    parts, buf, quote = [], [], None
    for ch in inner:
        if quote:
            if ch == quote:
                quote = None
        elif ch in "\"'":
            quote = ch
        elif ch == ",":
            parts.append("".join(buf))
            buf = []
            continue
        buf.append(ch)
    parts.append("".join(buf))
    return parts


def _flow_map(text: str, where: str) -> dict:
    inner = text.strip()[1:-1].strip()
    out: dict = {}
    if not inner:
        return out
    for part in _split_top(inner):
        if ":" not in part:
            raise ConfigError(f"{where}: bad inline mapping entry {part.strip()!r}")
        k, v = part.split(":", 1)
        k = k.strip()
        if k in out:
            raise ConfigError(f"{where}: duplicate key {k!r}")
        out[k] = _scalar(v, where)
    return out


def parse_yaml_subset(text: str, source: str = "config.yaml") -> dict:
    root: dict = {}
    # stack of (indent, container, key_in_parent_for_lists)
    stack: list[tuple[int, Any]] = [(-1, root)]
    pending: tuple[int, dict, str] | None = None  # key awaiting nested block
    for n, raw_line in enumerate(text.splitlines(), 1):
        where = f"{source}:{n}"
        if "\t" in raw_line[: len(raw_line) - len(raw_line.lstrip())]:
            raise ConfigError(f"{where}: tabs are not allowed for indentation")
        line = _strip_comment(raw_line)
        if not line.strip():
            continue
        indent = len(line) - len(line.lstrip(" "))
        body = line.strip()
        if pending is not None:
            p_indent, p_parent, p_key = pending
            pending = None
            if indent > p_indent:
                container: Any = [] if body.startswith("- ") or body == "-" else {}
                p_parent[p_key] = container
                stack.append((indent, container))
        while stack and indent < stack[-1][0]:
            stack.pop()
        if not stack or indent != stack[-1][0] and stack[-1][0] != -1:
            raise ConfigError(f"{where}: inconsistent indentation")
        cur_indent, cur = stack[-1]
        if cur_indent == -1 and indent != 0:
            raise ConfigError(f"{where}: unexpected indentation at top level")
        if body.startswith("- ") or body == "-":
            if not isinstance(cur, list):
                raise ConfigError(f"{where}: list item where a mapping key was expected")
            item = body[1:].strip()
            if item.startswith("{"):
                if not item.endswith("}"):
                    raise ConfigError(f"{where}: unterminated inline mapping")
                cur.append(_flow_map(item, where))
                continue
            if not item or _KEY.match(item):
                raise ConfigError(f"{where}: only scalar or inline-mapping list items are supported")
            cur.append(_scalar(item, where))
            continue
        if isinstance(cur, list):
            raise ConfigError(f"{where}: mapping key inside a list")
        m = _KEY.match(body)
        if not m:
            raise ConfigError(f"{where}: cannot parse {body!r}")
        key, val = m.group(1), (m.group(2) or "").strip()
        if key in cur:
            raise ConfigError(f"{where}: duplicate key {key!r}")
        if val == "":
            cur[key] = None
            pending = (indent, cur, key)
        elif val == "[]":
            cur[key] = []
        elif val.startswith("{"):
            if not val.endswith("}"):
                raise ConfigError(f"{where}: unterminated inline mapping")
            cur[key] = _flow_map(val, where)
        else:
            cur[key] = _scalar(val, where)
    return root


# ------------------------------------------------------------- validation

_TIME = re.compile(r"^([01]\d|2[0-3]):[0-5]\d$")

SCHEMA: dict[str, Any] = {
    "layer": {"id": str, "title": str, "mint_sibling": str},
    "mode": ("enum", {"paper", "live"}),
    "live_enabled": bool,
    "live_data_enabled": bool,
    "symbol_default": str,
    "timezone": str,
    "equity": {"starting_usd": ("num", 0, None), "currency": str},
    "risk_caps": {
        "max_trade_risk_pct": ("num", 0, 100),
        "max_daily_loss_pct": ("num", 0, 100),
        "max_portfolio_dd_pct": ("num", 0, 100),
        "scale_out_after_levels": ("int", 1, 20),
        "runner_pct": ("num", 0, 1),
        "raise_requires": ("enum", {"human"}),
    },
    "volatility": {"min_atr_pips": ("num", 0, None), "compress_blocks_trade": bool},
    "sessions": ("sessions",),
    "killzones": ("list", str),
    "measurement_families": ("list", str),
    "confluence": {"require_pd_overlap": bool, "overlap_tolerance_pips": ("num", 0, None)},
    "model13_bridge_enabled": bool,
    "mint_allowlist": ("list", ("allow_entry",)),
    "journal": {"template": str},
    "banned": ("list", str),
}
FAMILIES = {"pivots", "cbdr", "asian", "flout"}
ENTRY_MODULES = {"REV", "CONSO", "BB", "PIP20"}
_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def _check_allow_entry(e: Any, path: str) -> None:
    """MINT ALLOWLIST.md: Path A (board SURVIVES) or Path B (human paper pilot)."""
    if not isinstance(e, dict):
        raise ConfigError(f"{path}: expected {{ id: ..., kind: ... }}")
    allowed = {"id", "kind", "board_ref", "stamp", "expires", "kill", "notes"}
    extra = set(e) - allowed
    if extra:
        raise ConfigError(f"{path}: unknown keys {sorted(extra)} (allowed: {sorted(allowed)})")
    if e.get("id") not in ENTRY_MODULES:
        raise ConfigError(f"{path}.id: {e.get('id')!r} not an M9 entry model {sorted(ENTRY_MODULES)}")
    kind = e.get("kind")
    if kind == "survives":
        if not isinstance(e.get("board_ref"), str) or not e["board_ref"]:
            raise ConfigError(f"{path}: kind survives requires board_ref (ORION board lock path)")
    elif kind == "paper_pilot":
        for req in ("stamp", "expires", "kill"):
            if not isinstance(e.get(req), str) or not e[req]:
                raise ConfigError(f"{path}: kind paper_pilot requires {req}")
        if not _DATE.match(e["expires"]):
            raise ConfigError(f"{path}.expires: expected \"YYYY-MM-DD\", got {e['expires']!r}")
    else:
        raise ConfigError(f"{path}.kind: {kind!r} not in ['paper_pilot', 'survives']")


def _check(value: Any, spec: Any, path: str) -> None:
    if value is None:
        raise ConfigError(f"{path}: value is empty")
    if isinstance(spec, dict):
        if not isinstance(value, dict):
            raise ConfigError(f"{path}: expected a mapping")
        for k, v in value.items():
            if k not in spec:
                raise ConfigError(f"{path}.{k}: unknown key (allowed: {', '.join(sorted(spec))})")
            _check(v, spec[k], f"{path}.{k}")
        return
    if spec is bool:
        if not isinstance(value, bool):
            raise ConfigError(f"{path}: expected true/false, got {value!r}")
        return
    if spec is str:
        if not isinstance(value, str):
            raise ConfigError(f"{path}: expected a string, got {value!r}")
        return
    kind = spec[0]
    if kind == "enum":
        if value not in spec[1]:
            raise ConfigError(f"{path}: {value!r} not in {sorted(spec[1])}")
    elif kind in ("num", "int"):
        ok = isinstance(value, int) if kind == "int" else isinstance(value, (int, float))
        if isinstance(value, bool) or not ok:
            raise ConfigError(f"{path}: expected a {'whole ' if kind == 'int' else ''}number, got {value!r}")
        lo, hi = spec[1], spec[2]
        if lo is not None and value < lo:
            raise ConfigError(f"{path}: {value} is below minimum {lo}")
        if hi is not None and value > hi:
            raise ConfigError(f"{path}: {value} is above maximum {hi}")
    elif kind == "list":
        if not isinstance(value, list):
            raise ConfigError(f"{path}: expected a list")
        for i, item in enumerate(value):
            _check(item, spec[1], f"{path}[{i}]")
    elif kind == "allow_entry":
        _check_allow_entry(value, path)
    elif kind == "sessions":
        if not isinstance(value, dict):
            raise ConfigError(f"{path}: expected a mapping of session windows")
        for name, win in value.items():
            if not isinstance(win, dict) or set(win) != {"start", "end"}:
                raise ConfigError(f"{path}.{name}: expected {{ start: \"HH:MM\", end: \"HH:MM\" }}")
            for edge in ("start", "end"):
                if not isinstance(win[edge], str) or not _TIME.match(win[edge]):
                    raise ConfigError(f"{path}.{name}.{edge}: expected quoted \"HH:MM\", got {win[edge]!r}")


def validate_config(doc: dict, source: str = "config.yaml") -> None:
    _check(doc, SCHEMA, source)
    for req in ("mode", "live_enabled"):
        if req not in doc:
            raise ConfigError(f"{source}: missing required key {req!r}")
    sessions = doc.get("sessions") or {}
    for kz in doc.get("killzones") or []:
        if sessions and kz not in sessions:
            raise ConfigError(f"{source}.killzones: {kz!r} is not defined under sessions")
    for fam in doc.get("measurement_families") or []:
        if fam not in FAMILIES:
            raise ConfigError(f"{source}.measurement_families: unknown family {fam!r}")
    ids = [e["id"] for e in doc.get("mint_allowlist") or []]
    if len(ids) != len(set(ids)):
        raise ConfigError(f"{source}.mint_allowlist: duplicate model id")
    if doc.get("mode") == "live" and not doc.get("live_enabled"):
        raise ConfigError(f"{source}: mode: live requires live_enabled: true (and FTN_LIVE=1)")


def load_config(path: str | Path | None = None) -> dict[str, Any]:
    if path is None:
        env = os.environ.get("FTN_CONFIG", "").strip()
        path = Path(env) if env else repo_root() / "config.yaml"
    path = Path(path)
    cfg: dict[str, Any] = {"mode": "paper", "live_enabled": False, "path": str(path)}
    doc: dict = {}
    if path.is_file():
        doc = parse_yaml_subset(path.read_text(encoding="utf-8"), path.name)
        validate_config(doc, path.name)
    rc = doc.get("risk_caps") or {}
    vol = doc.get("volatility") or {}
    conf = doc.get("confluence") or {}
    for key in ("mode", "symbol_default", "timezone", "live_enabled", "live_data_enabled",
                "model13_bridge_enabled", "killzones", "sessions"):
        if key in doc:
            cfg[key] = doc[key]
    for key in ("max_trade_risk_pct", "max_daily_loss_pct", "max_portfolio_dd_pct",
                "scale_out_after_levels", "runner_pct"):
        if key in rc:
            cfg[key] = rc[key]
    cfg["mint_allowlist"] = list(doc.get("mint_allowlist") or [])
    cfg["equity_usd"] = float((doc.get("equity") or {}).get("starting_usd", 100000))
    if "min_atr_pips" in vol:
        cfg["min_atr_pips"] = float(vol["min_atr_pips"])
    if "compress_blocks_trade" in vol:
        cfg["compress_blocks_trade"] = vol["compress_blocks_trade"]
    if "require_pd_overlap" in conf:
        cfg["require_pd_overlap"] = conf["require_pd_overlap"]
    if "overlap_tolerance_pips" in conf:
        cfg["overlap_tolerance_pips"] = float(conf["overlap_tolerance_pips"])
    cfg.setdefault("min_atr_pips", 20)
    cfg.setdefault("overlap_tolerance_pips", 8)
    cfg.setdefault("scale_out_after_levels", 4)
    cfg.setdefault("runner_pct", 0.25)
    cfg.setdefault("require_pd_overlap", True)
    cfg.setdefault("compress_blocks_trade", True)
    cfg.setdefault("killzones", ["london", "ny_am"])
    cfg.setdefault("model13_bridge_enabled", False)
    cfg["raw"] = doc
    return cfg
