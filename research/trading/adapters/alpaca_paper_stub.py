#!/usr/bin/env python3
"""
MINT Alpaca paper client stub.

- Loads ALPACA_API_KEY, ALPACA_SECRET_KEY, ALPACA_BASE_URL from env
- Defaults to paper base URL
- get account (paper) — network call only if keys present and not dry-guarded
- place_order: dry-run unless --submit AND mode is paper
- Refuses live unless MINT_LIVE=1 AND config live_enabled true
- Does not commit or print secret values

This stub is intentionally minimal. It will NOT call live APIs when locked.
For agent automation, prefer dry-run (default) and do not pass --submit
unless a human is running a deliberate paper smoke test.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Optional

PAPER_BASE = "https://paper-api.alpaca.markets"
LIVE_BASE = "https://api.alpaca.markets"
LIVE_MARKERS = ("api.alpaca.markets",)  # paper-api is separate


def _repo_config_path() -> Path:
    # trading/adapters/thisfile → trading/config.yaml
    return Path(__file__).resolve().parent.parent / "config.yaml"


def _simple_yaml_bool(text: str, key: str, default: bool = False) -> bool:
    """Minimal key: value parser for live_enabled — no PyYAML required."""
    for line in text.splitlines():
        stripped = line.split("#", 1)[0].strip()
        if not stripped or ":" not in stripped:
            continue
        k, v = stripped.split(":", 1)
        if k.strip() == key:
            val = v.strip().strip("\"'").lower()
            if val in ("true", "yes", "1"):
                return True
            if val in ("false", "no", "0"):
                return False
    return default
def _simple_yaml_str(text: str, key: str, default: str = "") -> str:
    for line in text.splitlines():
        stripped = line.split("#", 1)[0].strip()
        if not stripped or ":" not in stripped:
            continue
        k, v = stripped.split(":", 1)
        if k.strip() == key:
            return v.strip().strip("\"'")
    return default


def load_mint_config() -> dict[str, Any]:
    path = _repo_config_path()
    cfg: dict[str, Any] = {
        "mode": "paper",
        "live_enabled": False,
        "path": str(path),
    }
    if not path.is_file():
        print(f"WARN: config not found at {path}; assuming paper / live_enabled false", file=sys.stderr)
        return cfg
    text = path.read_text(encoding="utf-8")
    mode = _simple_yaml_str(text, "mode", "paper")
    live_enabled = _simple_yaml_bool(text, "live_enabled", False)
    if isinstance(live_enabled, bool):
        cfg["live_enabled"] = live_enabled
    else:
        cfg["live_enabled"] = False
    cfg["mode"] = mode if isinstance(mode, str) else "paper"
    return cfg


def load_env() -> dict[str, Optional[str]]:
    return {
        "api_key": os.environ.get("ALPACA_API_KEY"),
        "secret_key": os.environ.get("ALPACA_SECRET_KEY"),
        "base_url": os.environ.get("ALPACA_BASE_URL", PAPER_BASE).rstrip("/"),
        "mint_live": os.environ.get("MINT_LIVE", "0"),
    }


def is_live_url(url: str) -> bool:
    u = url.lower().rstrip("/")
    if "paper-api.alpaca.markets" in u:
        return False
    return any(m in u for m in LIVE_MARKERS)


def assert_url_allowed(env: dict[str, Optional[str]], cfg: dict[str, Any]) -> None:
    base = env["base_url"] or PAPER_BASE
    live_url = is_live_url(base)
    dual_unlock = (env.get("mint_live") == "1") and bool(cfg.get("live_enabled"))

    if live_url and not dual_unlock:
        print(
            "ERROR: Live Alpaca URL refused.\n"
            f"  ALPACA_BASE_URL={base}\n"
            f"  config live_enabled={cfg.get('live_enabled')} (from {cfg.get('path')})\n"
            f"  MINT_LIVE={env.get('mint_live')!r}\n"
            "  Live requires MINT_LIVE=1 AND config live_enabled: true.\n"
            f"  Use paper URL: {PAPER_BASE}",
            file=sys.stderr,
        )
        sys.exit(2)

    if cfg.get("mode") != "paper" and not dual_unlock:
        print(
            f"ERROR: config mode={cfg.get('mode')!r} but live is not dual-unlocked. "
            "Set mode: paper or unlock live explicitly.",
            file=sys.stderr,
        )
        sys.exit(2)

    if dual_unlock and live_url:
        print(
            "ERROR: Live unlock detected but this stub refuses live trading by policy.\n"
            "  MINT package must not place live orders from the stub.\n"
            "  Use a human-reviewed live client outside agent automation.",
            file=sys.stderr,
        )
        sys.exit(2)


def _headers(env: dict[str, Optional[str]]) -> dict[str, str]:
    if not env["api_key"] or not env["secret_key"]:
        print(
            "ERROR: Missing ALPACA_API_KEY and/or ALPACA_SECRET_KEY in environment.\n"
            "  Export paper keys locally; never commit them.",
            file=sys.stderr,
        )
        sys.exit(2)
    return {
        "APCA-API-KEY-ID": env["api_key"],
        "APCA-API-SECRET-KEY": env["secret_key"],
        "Content-Type": "application/json",
    }


def http_json(
    method: str,
    url: str,
    env: dict[str, Optional[str]],
    body: Optional[dict[str, Any]] = None,
) -> Any:
    data = None if body is None else json.dumps(body).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=_headers(env), method=method)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            raw = resp.read().decode("utf-8")
            return json.loads(raw) if raw else {}
    except urllib.error.HTTPError as e:
        err_body = e.read().decode("utf-8", errors="replace")
        print(f"ERROR: HTTP {e.code} from Alpaca: {err_body}", file=sys.stderr)
        sys.exit(1)
    except urllib.error.URLError as e:
        print(f"ERROR: Network failure contacting Alpaca: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_account(env: dict[str, Optional[str]], cfg: dict[str, Any], dry_meta: bool) -> None:
    assert_url_allowed(env, cfg)
    base = env["base_url"] or PAPER_BASE
    if dry_meta or not env["api_key"] or not env["secret_key"]:
        print(
            json.dumps(
                {
                    "dry_run": True,
                    "action": "get_account",
                    "base_url": base,
                    "mode": cfg.get("mode"),
                    "live_enabled": cfg.get("live_enabled"),
                    "note": "No network call — missing keys or --dry-meta. "
                    "Export paper keys to fetch real paper account.",
                },
                indent=2,
            )
        )
        return
    account = http_json("GET", f"{base}/v2/account", env)
    # Avoid dumping anything that looks like a secret; account JSON is fine
    safe = {
        k: account.get(k)
        for k in (
            "id",
            "account_number",
            "status",
            "currency",
            "cash",
            "equity",
            "buying_power",
            "pattern_day_trader",
            "trading_blocked",
            "account_blocked",
        )
        if k in account
    }
    safe["base_url"] = base
    safe["mode"] = cfg.get("mode")
    print(json.dumps(safe, indent=2))


def cmd_place_order(
    env: dict[str, Optional[str]],
    cfg: dict[str, Any],
    args: argparse.Namespace,
) -> None:
    assert_url_allowed(env, cfg)
    base = env["base_url"] or PAPER_BASE

    order: dict[str, Any] = {
        "symbol": args.symbol.upper(),
        "side": args.side.lower(),
        "type": args.type.lower(),
        "time_in_force": args.time_in_force.lower(),
    }
    if args.qty is not None:
        order["qty"] = str(args.qty)
    if args.notional is not None:
        order["notional"] = str(args.notional)
    if args.limit_price is not None:
        order["limit_price"] = str(args.limit_price)
    if args.stop_price is not None:
        order["stop_price"] = str(args.stop_price)
    if args.client_order_id:
        order["client_order_id"] = args.client_order_id

    if not args.qty and not args.notional:
        print("ERROR: provide --qty or --notional", file=sys.stderr)
        sys.exit(2)

    submit = bool(args.submit)
    if submit and cfg.get("mode") != "paper":
        print(
            f"ERROR: --submit refused because config mode={cfg.get('mode')!r} (need mode: paper).",
            file=sys.stderr,
        )
        sys.exit(2)

    if not submit:
        print(
            json.dumps(
                {
                    "dry_run": True,
                    "action": "place_order",
                    "base_url": base,
                    "mode": cfg.get("mode"),
                    "live_enabled": cfg.get("live_enabled"),
                    "order": order,
                    "note": "Dry-run only. Pass --submit with paper mode + keys to POST to paper API.",
                },
                indent=2,
            )
        )
        return

    # Intentional paper submit
    assert_url_allowed(env, cfg)
    if is_live_url(base):
        print("ERROR: --submit refused for live URL.", file=sys.stderr)
        sys.exit(2)
    result = http_json("POST", f"{base}/v2/orders", env, body=order)
    print(json.dumps({"dry_run": False, "order_response": result}, indent=2, default=str))


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="MINT Alpaca paper stub — dry-run by default; refuses live when locked.",
    )
    sub = p.add_subparsers(dest="command", required=True)

    acc = sub.add_parser("account", help="GET paper account (or dry-meta without keys)")
    acc.add_argument(
        "--dry-meta",
        action="store_true",
        help="Do not call network; print planned request metadata",
    )

    po = sub.add_parser("place_order", help="Place order (dry-run unless --submit and paper mode)")
    po.add_argument("--symbol", required=True)
    po.add_argument("--side", required=True, choices=["buy", "sell"])
    po.add_argument("--type", default="market", choices=["market", "limit", "stop", "stop_limit"])
    po.add_argument("--qty", type=float, default=None)
    po.add_argument("--notional", type=float, default=None)
    po.add_argument("--limit-price", type=float, default=None)
    po.add_argument("--stop-price", type=float, default=None)
    po.add_argument("--time-in-force", default="day")
    po.add_argument("--client-order-id", default=None)
    po.add_argument(
        "--submit",
        action="store_true",
        help="Actually POST to paper API (requires keys; refuses live)",
    )
    return p


def main(argv: Optional[list[str]] = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    cfg = load_mint_config()
    env = load_env()

    # Always evaluate URL policy early for clear errors
    assert_url_allowed(env, cfg)

    if args.command == "account":
        cmd_account(env, cfg, dry_meta=bool(getattr(args, "dry_meta", False)))
    elif args.command == "place_order":
        cmd_place_order(env, cfg, args)
    else:
        parser.error(f"unknown command {args.command}")


if __name__ == "__main__":
    main()
