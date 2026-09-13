# MINT Broker Adapters

Adapters translate MINT paper tickets into broker-specific API calls. **No Alpaca MCP exists yet** — use documented REST/CLI contracts and the Python paper stub.

---

## Interface (contract)

Every adapter SHOULD expose (conceptually):

| Method | Purpose | Notes |
|--------|---------|-------|
| `get_account()` | Equity, buying power, cash | Paper account only by default |
| `get_positions()` | Open positions | Sync with `risk/BOOK.md` |
| `place_order(...)` | Submit or dry-run order | Default **dry-run** unless explicit submit + paper mode |
| `cancel_order(id)` | Cancel | Optional in stub |
| `get_orders(...)` | List orders | Optional |

### Shared guards (all adapters)

1. Load credentials from **env only** — never from git.
2. If `live_enabled` is false **or** `MINT_LIVE` ≠ `1` → refuse live base URLs.
3. If config `mode: paper` → only paper base URL.
4. Require caller to pass `board_ref` / strategy id for audit (journal layer may enforce).
5. Print clear errors; exit non-zero on refuse.

### Order fields (minimum)

```
symbol, side (buy|sell), qty | notional,
type (market|limit|stop|stop_limit),
time_in_force,
limit_price?, stop_price?,
client_order_id?,
dry_run: bool
```

---

## Implemented

| Adapter | Docs | Stub |
|---------|------|------|
| Alpaca | [`alpaca.md`](alpaca.md) | [`alpaca_paper_stub.py`](alpaca_paper_stub.py) |

---

## Adding an adapter

1. Write `trading/adapters/<broker>.md` (endpoints, env, CLI).
2. Add a minimal stub that refuses live when locked.
3. Point `trading/config.yaml` `brokers.<name>`.
4. Never enable live in the same PR without human unlock docs.
5. LEDGER row.

---

## Dependencies

Optional:

```bash
pip install alpaca-py
```

See `trading/requirements.txt` (alpaca-py noted as optional). Agents must **not** force-install or call real APIs unless a human is running a deliberate paper smoke test.
