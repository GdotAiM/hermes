"""H016b one-sided exit-minute flag + conservative re-resolution (binding fill-fragility leg; CASSANDRA early-reads
ruling 2026-10-04 s.2 + follow-up, ORION concurrence). Every definition below is DATA's reference implementation registered
VERBATIM, version v2 (source: /home/box/hermes-x/investigations/POST-WAVE1-LEADS/h016_review/one_sided/one_sided_exit.py,
sha256 691a102f208e2e4c1f44748c27288d130843eb46b557ae329f862243e2d501dd; definitions: CONSERVATIVE_EXIT_VERSION, P95_SESSIONS, _p95, _session_start, _two_sided_spreads, p95_floor, conservative, one_sided_count).
Source text of each definition is checked equal by research/forward/tests/test_h016b.py. Only this docstring and the
imports are added. Co-report / fragility leg only: the binding outcome stays the pinned ftn.research.outcomes.simulate_both."""
import datetime as dt

TARGET_R = 2.0   # = ftn.research.outcomes.TARGET_R at prereg-H016b (asserted by the tests)
REGISTERED_SOURCE_SHA256 = "691a102f208e2e4c1f44748c27288d130843eb46b557ae329f862243e2d501dd"
REGISTERED_NAMES = ('CONSERVATIVE_EXIT_VERSION', 'P95_SESSIONS', '_p95', '_session_start', '_two_sided_spreads', 'p95_floor', 'conservative', 'one_sided_count')


CONSERVATIVE_EXIT_VERSION = "v2 (2026-10-04, CASSANDRA follow-up): stop_proxy spread = max(last two-sided spread, p95 floor)"

P95_SESSIONS = 20

def _p95(xs):
    """Nearest-rank 95th percentile: sorted(xs)[ceil(0.95*n) - 1]."""
    xs = sorted(xs); n = len(xs)
    return xs[max(0, -(-95 * n // 100) - 1)] if n else None

def _session_start(d):
    """CFD session for NY date d = [d-1 18:00, d 17:00) NY (ftn.research.bars.session_bounds)."""
    return dt.datetime.combine(d - dt.timedelta(days=1), dt.time(18, 0))

def _two_sided_spreads(bid, ask, start, end):
    bm = {bid.t[i]: bid.c[i] for i in bid.window(start, end)}
    return [ask.c[j] - bm[ask.t[j]] for j in ask.window(start, end) if ask.t[j] in bm]

def p95_floor(bid, ask, t, sessions=P95_SESSIONS):
    """Proxy-spread floor at minute t. Prior sessions = the last `sessions` NY dates before t's date that are trading days
    (weekday with >= 300 BID bars in 09:30-15:59, ftn.research.bars.trading_days rule) and have two-sided minutes; spreads =
    ASK close - BID close over every two-sided minute of those sessions [d-1 18:00, d 17:00). If fewer than `sessions`
    prior sessions exist in the loaded history: p95 of the two-sided minutes of the current session so far
    [session start, t). Returns (value, source) with source 'p95_20d' or 'p95_session' (value None if no data)."""
    d = t.date(); days = []; k = d - dt.timedelta(days=1); lo = bid.t[0].date() if bid.t else d
    while len(days) < sessions and k >= lo:
        if k.weekday() < 5 and len(bid.window(dt.datetime.combine(k, dt.time(9, 30)), dt.datetime.combine(k, dt.time(16, 0)))) >= 300:
            days.append(k)
        k -= dt.timedelta(days=1)
    if len(days) >= sessions:
        xs = []
        for k in days: xs += _two_sided_spreads(bid, ask, _session_start(k), dt.datetime.combine(k, dt.time(17, 0)))
        return _p95(xs), "p95_20d"
    return _p95(_two_sided_spreads(bid, ask, _session_start(d), t)), "p95_session"

def conservative(bid, ask, et, entry, stop, side, slip, target_r=TARGET_R, events=None):
    """Conservative re-resolution (CASSANDRA ruling 2026-10-04 s.2 + follow-up), version CONSERVATIVE_EXIT_VERSION.
    Same entry/levels/slippage/time exit as simulate_both. Walk the UNION of BID and ASK minute timestamps in [entry_time, 16:00):
      both sides present  -> exactly simulate_both's checks (stop first, then target); record last spread = ask.c - bid.c.
      only the stop side present (long: BID; short: ASK) -> stop check on that bar (fill as pinned); NO target check.
      only the other side present -> proxy the stop side with the other side shifted by
          sp_proxy = max(sp_last, p95_floor) where sp_last = ask.c - bid.c at the latest two-sided minute < t (initialised
          from the t-1m bars) and p95_floor = p95 two-sided spread over the prior 20 sessions (fallback: session so far).
          Long BID proxy = ASK - sp_proxy, short ASK proxy = BID + sp_proxy. Stop hit if proxy low <= stop (long) /
          proxy high >= stop (short) (range brackets or gaps through the stop); fill = min(stop, proxy open) - slip_stop /
          max(stop, proxy open) + slip_stop. NO target check. Each proxy minute appends to `events`:
          {t, sp_last, p95, p95_source, sp_used, source ('last' | 'p95_20d' | 'p95_session'), hit}.
      neither side present -> nothing (a gap through the stop is caught on the next bar's open, as pinned).
    Time exit unchanged: last two-sided minute close before 16:00 on the exit side (as pinned)."""
    sl = dict(slip)
    risk = (entry - stop) if side == "buy" else (stop - entry)
    tgt = entry + target_r * risk if side == "buy" else entry - target_r * risk
    ib, ia = bid.idx(et) - 1, ask.idx(et) - 1
    fill_in = ask.c[ia] + sl["market"] if side == "buy" else bid.c[ib] - sl["market"]
    end = dt.datetime.combine(et.date(), dt.time(16, 0))
    bmap = {bid.t[i]: i for i in bid.window(et, end)}; amap = {ask.t[j]: j for j in ask.window(et, end)}
    sp = ask.c[ia] - bid.c[ib]
    ev = events if events is not None else []
    how, xp, xt, last, n1 = "time", None, None, None, 0
    def proxy_spread(t):
        f, src = p95_floor(bid, ask, t)
        used, s_used = (sp, "last") if f is None or sp >= f else (f, src)
        return used, dict(t=t.isoformat(), sp_last=sp, p95=f, p95_source=src, sp_used=used, source=s_used)
    for t in sorted(set(bmap) | set(amap)):
        i, j = bmap.get(t), amap.get(t)
        if i is not None and j is not None:
            if side == "buy":
                if bid.l[i] <= stop: xp, how = min(stop, bid.o[i]) - sl["stop"], "stop"
                elif bid.h[i] > tgt: xp, how = tgt - sl["limit"], "target"
            else:
                if ask.h[j] >= stop: xp, how = max(stop, ask.o[j]) + sl["stop"], "stop"
                elif ask.l[j] < tgt: xp, how = tgt + sl["limit"], "target"
            if xp is None:
                last = (i, j); sp = ask.c[j] - bid.c[i]
        else:
            n1 += 1
            if side == "buy":
                if i is not None:   # BID only: real stop side
                    if bid.l[i] <= stop: xp, how = min(stop, bid.o[i]) - sl["stop"], "stop_one_sided"
                else:               # ASK only: BID proxy
                    u, e = proxy_spread(t); hit = ask.l[j] - u <= stop; e["hit"] = hit; ev.append(e)
                    if hit: xp, how = min(stop, ask.o[j] - u) - sl["stop"], "stop_proxy"
            else:
                if j is not None:   # ASK only: real stop side
                    if ask.h[j] >= stop: xp, how = max(stop, ask.o[j]) + sl["stop"], "stop_one_sided"
                else:               # BID only: ASK proxy
                    u, e = proxy_spread(t); hit = bid.h[i] + u >= stop; e["hit"] = hit; ev.append(e)
                    if hit: xp, how = max(stop, bid.o[i] + u) + sl["stop"], "stop_proxy"
        if xp is not None:
            xt = t; break
    if xp is None:
        if last is None: return {"R": None, "exit": "no_bars", "n1": n1, "proxy_events": ev}
        i, j = last; xp = (bid.c[i] - sl["market"]) if side == "buy" else (ask.c[j] + sl["market"]); xt = bid.t[i]
    pnl = (xp - fill_in) if side == "buy" else (fill_in - xp)
    return {"R": pnl / risk, "exit": how, "exit_time": xt.isoformat(), "n1": n1, "proxy_events": ev}

def one_sided_count(bid, ask, et, xt_iso):
    xt = dt.datetime.fromisoformat(xt_iso)
    b = {bid.t[i] for i in bid.window(et, xt + dt.timedelta(minutes=1))}; a = {ask.t[j] for j in ask.window(et, xt + dt.timedelta(minutes=1))}
    return len(b ^ a), len(b - a), len(a - b)
