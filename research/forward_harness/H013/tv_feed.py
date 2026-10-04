"""Fetch 1m bars from TradingView's public websocket (anonymous 'unauthorized_user_token', tvDatafeed-style). Returns NY-tz OHLC."""
import json, random, string, re, time, pandas as pd
from websocket import create_connection
def _msg(f, p): s = json.dumps({"m": f, "p": p}, separators=(",", ":")); return f"~m~{len(s)}~m~{s}"
def _sid(pre): return pre + "".join(random.choices(string.ascii_lowercase, k=12))
def fetch_tv(symbol, n=500, interval="1", timeout=25):
    ws = create_connection("wss://data.tradingview.com/socket.io/websocket", header={"Origin": "https://www.tradingview.com"},
                           timeout=timeout)
    cs = _sid("cs_")
    for m in (_msg("set_auth_token", ["unauthorized_user_token"]), _msg("chart_create_session", [cs, ""]),
              _msg("resolve_symbol", [cs, "sds_sym_1", "=" + json.dumps({"symbol": symbol, "adjustment": "splits"})]),
              _msg("create_series", [cs, "sds_1", "s1", "sds_sym_1", interval, n, ""])):
        ws.send(m)
    raw, t0, err = "", time.time(), None
    while time.time() - t0 < timeout:
        r = ws.recv()
        for hb in re.findall(r"~m~\d+~m~(~h~\d+)", r): ws.send(f"~m~{len(hb)}~m~{hb}")
        raw += r
        if "symbol_error" in r or "series_error" in r: err = r[:300]; break
        if "series_completed" in r: break
    ws.close()
    if err: raise RuntimeError(f"{symbol}: {err}")
    m = re.search(r'"s":\[(.+?)\}\]', raw)
    if not m: raise RuntimeError(f"{symbol}: no bars")
    vals = [json.loads(y)["v"] for y in re.findall(r'\{"i":\d+,"v":\[[^\]]+\]\}', raw)]
    df = pd.DataFrame([v[:5] for v in vals], columns=["t", "Open", "High", "Low", "Close"])
    df.index = pd.DatetimeIndex(pd.to_datetime(df.pop("t"), unit="s", utc=True)).tz_convert("America/New_York")
    df = df[~df.index.duplicated(keep="last")].sort_index().astype(float)
    return df
if __name__ == "__main__":
    import sys; d = fetch_tv(sys.argv[1] if len(sys.argv) > 1 else "CAPITALCOM:US100"); print(len(d)); print(d.tail(3))
