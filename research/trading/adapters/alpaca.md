# Alpaca Adapter Contract (MINT)

**Status:** Documented REST + CLI; **no MCP** yet. Paper default. Live locked.

Official docs: https://docs.alpaca.markets/  
Python SDK: `alpaca-py` (`pip install alpaca-py` — optional)

---

## Environment variables

| Var | Purpose |
|-----|---------|
| `ALPACA_API_KEY` | API key id |
| `ALPACA_SECRET_KEY` | Secret key |
| `ALPACA_BASE_URL` | Override base URL (prefer paper) |
| `MINT_LIVE` | Must be `1` **and** config `live_enabled: true` for live |

**Never commit values.** Use a local `.env` (gitignored).

---

## Base URLs

| Mode | Base URL |
|------|----------|
| **Paper** (default) | `https://paper-api.alpaca.markets` |
| **Live** (locked) | `https://api.alpaca.markets` |

MINT refuses live URL unless dual unlock. Stub also refuses if `live_enabled` is false and URL looks live.

---

## REST endpoints (v2, illustrative)

Auth: HTTP headers

```
APCA-API-KEY-ID: <ALPACA_API_KEY>
APCA-API-SECRET-KEY: <ALPACA_SECRET_KEY>
```

| Action | Method | Path |
|--------|--------|------|
| Account | GET | `/v2/account` |
| Positions | GET | `/v2/positions` |
| Place order | POST | `/v2/orders` |
| Get order | GET | `/v2/orders/{order_id}` |
| Cancel order | DELETE | `/v2/orders/{order_id}` |
| List orders | GET | `/v2/orders` |

### Example order body (paper)

```json
{
  "symbol": "SPY",
  "qty": "1",
  "side": "buy",
  "type": "market",
  "time_in_force": "day",
  "client_order_id": "mint-paper-example-001"
}
```

---

## curl examples (**placeholder keys only**)

```bash
# Paper account — replace placeholders; do not paste real keys into git/chat logs if avoidable
export ALPACA_API_KEY="YOUR_PAPER_KEY_ID"
export ALPACA_SECRET_KEY="YOUR_PAPER_SECRET"
export ALPACA_BASE_URL="https://paper-api.alpaca.markets"

curl -s -X GET "$ALPACA_BASE_URL/v2/account" \
  -H "APCA-API-KEY-ID: $ALPACA_API_KEY" \
  -H "APCA-API-SECRET-KEY: $ALPACA_SECRET_KEY"
```

```bash
# Dry-run mindset: prefer the Python stub before any POST
curl -s -X POST "$ALPACA_BASE_URL/v2/orders" \
  -H "APCA-API-KEY-ID: $ALPACA_API_KEY" \
  -H "APCA-API-SECRET-KEY: $ALPACA_SECRET_KEY" \
  -H "Content-Type: application/json" \
  -d '{"symbol":"SPY","qty":"1","side":"buy","type":"market","time_in_force":"day"}'
```

Agents in HERMES-X: **do not** run these against real endpoints unless a human is conducting a paper smoke test.

---

## alpaca-py sketch (optional)

```python
# Illustrative only — not imported by default in MINT stub
# from alpaca.trading.client import TradingClient
# from alpaca.trading.requests import MarketOrderRequest
# from alpaca.trading.enums import OrderSide, TimeInForce
#
# client = TradingClient(api_key, secret_key, paper=True)
# account = client.get_account()
# order = client.submit_order(
#     MarketOrderRequest(
#         symbol="SPY",
#         qty=1,
#         side=OrderSide.BUY,
#         time_in_force=TimeInForce.DAY,
#     )
# )
```

Prefer [`alpaca_paper_stub.py`](alpaca_paper_stub.py) for MINT dry-run / guard logic.

---

## CLI notes

| Tool | Notes |
|------|-------|
| `trading/adapters/alpaca_paper_stub.py` | MINT stub: env load, account (paper), place_order dry-run |
| `alpaca-py` | Official SDK if human installs locally |
| `curl` | Fine for smoke tests with paper keys |

### Stub usage

```bash
python trading/adapters/alpaca_paper_stub.py account
python trading/adapters/alpaca_paper_stub.py place_order \
  --symbol SPY --qty 1 --side buy --type market
# Intentional paper submit (still refuses live when locked):
python trading/adapters/alpaca_paper_stub.py place_order \
  --symbol SPY --qty 1 --side buy --type market --submit
```

---

## Live unlock checklist (human only)

1. Set `trading/config.yaml` `live_enabled: true` (separate reviewed change).
2. Export `MINT_LIVE=1`.
3. Point `ALPACA_BASE_URL` to live URL **only** with live keys.
4. Confirm RISK + human written authorization in git.
5. LEDGER row: live unlocked (date, who).

Until then: **paper only**.
