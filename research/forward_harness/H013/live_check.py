"""Live Model U v1 BASE check (user-facing status/alerts). Data: TradingView public websocket, CAPITALCOM:US100 and
CAPITALCOM:US500 ONLY (H013 prereg: no PEPPERSTONE/OANDA/Yahoo fallback; a failed fetch raises and is a logged gap).
Signal logic = longrun v1 code UNCHANGED (V1.ctx_for, V1.side_ctx, E1.long_candidates, E1.simulate on range fractions),
with the frozen H013 fill rule FILL_THRU = 1 tick (limit fills only if price trades 1 tick through the CE).
Status is evaluated only up to the latest available bar. v1 takes ONE trade per day: the first candidate to fill.
Costs use the longrun per-side costs (US100 0.8, US500 0.5 pts) for the R figures; prices are CAPITALCOM CFD prices.
The auditable H013 live-alert record is h013_live_watch.py -> h013_alerts.jsonl (this script's alert_state.json is not used
for counting). 'v1_reentry' rows are legacy/log-only and are not part of H013.
Usage: live_check.py [YYYY-MM-DD]"""
import sys, json, pathlib, datetime as dt, numpy as np, pandas as pd
FT = pathlib.Path(__file__).parent; LR = FT.parent / "research/model-u-longrun"
sys.path.insert(0, str(LR / "scripts/v1"))
import u_engine as E1, run_u_lib as V1
E1.FILL_THRU = 1                                    # H013 frozen fill rule (prereg engine_settings.FILL_THRU_ticks)
COST = json.load(open(LR / "data/costs.json")); TZ = "America/New_York"
SYM = {"US100": "CAPITALCOM:US100", "US500": "CAPITALCOM:US500"}
TV = {"US100": ["CAPITALCOM:US100"], "US500": ["CAPITALCOM:US500"]}      # CAPITALCOM only (H013 prereg)
TV_BARS = 1500   # ~500 bars would start ~00:56 NY and miss the Asia window (prev bday 19:00-00:00) used by v1; 1500 covers Sunday 18:00+
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0 Safari/537.36"

def status_after_fill(gg, fill, cand):
    """Walk from the fill bar to the latest bar (long space): stopped / TP1 / TP2 / filled-open. Same conventions as simulate()."""
    Hi, Lo = gg.High.values, gg.Low.values; s, t1, t2, e = cand["stop"], cand["t1"], cand["t2"], cand["entry"]
    if Lo[fill] <= s: return "stopped (in fill bar)", fill
    st, cur = "filled (open)", s
    i_exit = gg.index.searchsorted(gg.index[0].normalize() + pd.Timedelta(hours=11, minutes=30))   # 11:30 NY time exit (as simulate)
    for i in range(fill + 1, min(len(gg), i_exit)):
        if Lo[i] <= cur: return (st + " then stopped at BE" if st.startswith("TP1") else "stopped"), i
        if Hi[i] >= t2: return "TP2 hit", i
        if Hi[i] >= t1 and not st.startswith("TP1"): st, cur = "TP1 hit (stop to BE)", e
    if len(gg) > i_exit: return st + " -> closed 11:30 time exit", i_exit - 1
    return st, len(gg) - 1

def check(nm, d, df):
    E1.SLIP = COST[nm] / E1.TICK
    c = V1.ctx_for(df, d, nm); g = c["g"]; n = len(g)
    i_end = min(c["i1100"], n); out = []
    for side in ("long", "short"):
        gg = g if side == "long" else E1.neg(g); sc = V1.side_ctx(c, side); sg = 1 if side == "long" else -1
        for cand in E1.long_candidates(gg, sc, c["i900"], c["i1100"], reanchor=False, in_range=True):
            if cand["trig_i"] >= n: continue
            px = lambda v: sg * v
            e, s, t1, t2 = px(cand["entry"]), px(cand["stop"]), px(cand["t1"]), px(cand["t2"])
            row = dict(inst=nm, direction=side, setup=cand["kind"], trigger=cand["why"], entry=e, stop=s, TP1=t1, TP2=t2,
                       risk_pts=round(abs(e - s), 2), entry_frac=round((e - c["L"]) / c["R"], 3),
                       setup_time_ny=g.index[cand["trig_i"]].strftime("%H:%M"), fvg_c2_ny=g.index[cand["c2"]].strftime("%H:%M"))
            # replicate simulate() fill/cancel loop on the available bars
            Hi, Lo = gg.High.values, gg.Low.values; fill = None; stat = "pending"; start = cand["trig_i"] + 1
            for i in range(start, min(c["i1100"], n)):
                thr = cand["entry"] - E1.FILL_THRU * E1.TICK
                if Hi[i] >= cand["t1"] and not (Lo[i] <= thr): stat = "cancelled (TP1 printed before fill)"; row["event_ny"] = g.index[i].strftime("%H:%M"); break
                if Lo[i] <= thr: fill = i; break
            if fill is not None:
                row["fill_time_ny"] = g.index[fill].strftime("%H:%M")
                stat, j = status_after_fill(gg, fill, cand); row["event_ny"] = g.index[j].strftime("%H:%M"); row["_exit_i"] = j
                cst = COST[nm]; ef = cand["entry"] + cst; rk = cand["entry"] - cand["stop"]     # long space
                row["R_open_now_after_costs"] = round((gg.Close.values[-1] - cst - ef) / rk, 3)
                res = E1.simulate(gg, cand, c["i1100"], c["i1130"])
                if res: row.update(R_T1=round(res["R_t1"], 3), R_T2=round(res["R_t2"], 3), R_5050=round(res["R_part"], 3),
                                   out_5050_sofar=res["out_part"])
            elif stat == "pending" and g.index[-1] >= V1.at(d, "10:59", TZ): stat = "expired (no fill by 11:00)"
            row["status"] = stat; row["_fill_i"] = fill if fill is not None else 10**9; row["_trig_i"] = cand["trig_i"]; row["_cand"] = cand; out.append(row)
    # plain v1: ONE trade per day = first candidate to fill. Variant 'v1_reentry': after that trade is fully closed
    # (stopped / TP2 / BE stop after TP1 / 11:30), the first candidate whose setup (c3) forms AFTER the exit bar and fills later
    # is a 2nd trade (max 2 per instrument per day). Other candidates are void.
    for r in out: r["variant"] = "v1"
    fills = [r for r in out if r["_fill_i"] < 10**9]
    if fills:
        first = min(fills, key=lambda r: r["_fill_i"])
        closed = any(x in first["status"] for x in ("stopped", "TP2 hit", "closed 11:30"))
        second = None
        if closed:
            ex = first["_exit_i"]
            later = [r for r in out if r is not first and r["_trig_i"] > ex]
            f2 = [r for r in later if r["_fill_i"] < 10**9]
            second = min(f2, key=lambda r: r["_fill_i"]) if f2 else None
            for r in later:
                r["variant"] = "v1_reentry"
                if second is not None and r is not second: r["status"] = "void (v1_reentry already filled its 2nd trade)"
        for r in out:
            if r is first or r["variant"] == "v1_reentry": continue
            if r["status"] == "pending" or r["_fill_i"] < 10**9 or r["status"].startswith("cancel"):
                r["status"] = "void (v1 already filled another order today)"
    return c, g, out

def chart(nm, d, c, g, rows):
    import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
    from matplotlib.patches import Rectangle
    x = g.loc[f"{d} 07:00":]; fig, ax = plt.subplots(figsize=(12, 6))
    for i, (t, r) in enumerate(x.iterrows()):
        col = "tab:green" if r.Close >= r.Open else "tab:red"
        ax.plot([i, i], [r.Low, r.High], color=col, lw=0.6); ax.add_patch(Rectangle((i - .35, min(r.Open, r.Close)), .7, max(abs(r.Close - r.Open), 1e-6), color=col))
    i9 = int((x.index < V1.at(d, "09:00", TZ)).sum()); ax.axvspan(-0.5, i9 - 0.5, color="tab:blue", alpha=0.06)
    for q in np.arange(0, 1.001, 0.125):
        v = c["L"] + q * c["R"]; ax.axhline(v, color="purple" if q == 0.5 else "tab:blue", lw=1.2 if q in (0, .5, 1) else .5, ls="-" if q in (0, .5, 1) else ":")
        ax.text(len(x) + .5, v, f"{q:.3f} {v:.2f}", fontsize=7, color="tab:blue", va="center")
    for r in rows:
        if r["status"].startswith("void") or r["status"].startswith("cancel"): continue
        i0 = x.index.get_loc(g.index[g.index.strftime("%H:%M") == r["setup_time_ny"]][0])
        for k, colr in (("entry", "black"), ("stop", "red"), ("TP1", "green"), ("TP2", "darkgreen")):
            ax.plot([i0, len(x) + 8], [r[k]] * 2, color=colr, lw=1.2); ax.text(i0, r[k], f"{k} {r[k]:.2f}", fontsize=7, color=colr, va="bottom")
        ax.set_title(f"{nm} ({SYM_USED.get(nm, SYM[nm])}) {d} · v1 {r['direction']} {r['setup']} · {r['status']} · risk {r['risk_pts']} pts\n"
                     f"1m, latest bar {g.index[-1]:%H:%M} NY · HYPOTHETICAL paper", fontsize=9)
    tk = [i for i, t in enumerate(x.index) if t.minute % 30 == 0]
    ax.set_xticks(tk); ax.set_xticklabels([f"{x.index[i]:%H:%M}\n{x.index[i] + pd.Timedelta(hours=6):%H:%M} SAST" for i in tk], fontsize=7)
    ax.set_xlim(-1, len(x) + 14); fig.tight_layout(); p = FT / f"live_{nm}_{d}.png"; fig.savefig(p, dpi=110); return p

def get_data(nm):
    """TradingView CAPITALCOM only (no fallback). Drops the still-forming last bar. Raises if the fetch fails."""
    from tv_feed import fetch_tv
    now = pd.Timestamp.now(tz=TZ); errs = []
    for sym in TV[nm]:
        try:
            df = fetch_tv(sym, n=TV_BARS)
            return df[df.index + pd.Timedelta(minutes=1) <= now], f"TradingView {sym}", errs
        except Exception as e: errs.append(f"{sym}: {str(e)[:120]}")
    raise RuntimeError(f"{nm}: TradingView CAPITALCOM fetch failed (no fallback by H013 prereg): {errs}")

if __name__ == "__main__":
    d = sys.argv[1] if len(sys.argv) > 1 else dt.datetime.now(dt.timezone.utc).astimezone(pd.Timestamp.now(tz=TZ).tz).strftime("%Y-%m-%d")
    SYM_USED = {}; stp = FT / "alert_state.json"; state = json.load(open(stp)) if stp.exists() else {}
    live = state.setdefault("live", {}); state.pop("live_yahoo", None); now_sast = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    for nm, sym in SYM.items():
        df, src, errs = get_data(nm); c, g, rows = check(nm, d, df); SYM_USED[nm] = src
        last = g.index[-1]; lag = (pd.Timestamp.now(tz=TZ) - (last + pd.Timedelta(minutes=1))).total_seconds() / 60
        if errs: print("   feed errors:", errs)
        print("   eighths:", {f"{q:.3f}": round(c["L"] + q * c["R"], 2) for q in np.arange(0, 1.001, 0.125)})
        print(f"== {nm} {src}: bar close lag vs wall clock {lag:.1f} min;: latest bar {last:%H:%M} NY ({last + pd.Timedelta(hours=6):%H:%M} SAST), last close {g.Close.iloc[-1]:.2f}")
        print(f"   07-09 range L {c['L']:.2f} H {c['H']:.2f} R {c['R']:.2f} M {c['M']:.2f} (pre-09 bars {int((g.index < V1.at(d, '09:00', TZ)).sum())}/120)")
        rows_clean = [{k: (float(v) if isinstance(v, (np.floating,)) else v) for k, v in r.items() if not k.startswith("_")} for r in rows]
        for r in rows_clean: print("   ", r)
        if not rows_clean: print("    no v1 setup yet")
        live[nm] = dict(source=src, checked_sast=now_sast, latest_bar_ny=f"{last:%Y-%m-%d %H:%M}", range=dict(low=c["L"], high=c["H"]), orders=rows_clean)
        for r in rows_clean:
            key = f"{d}|{nm}|{r['direction']}|{r['setup_time_ny']}|{r['entry']}"
            known = {o.get("key"): o for o in state.setdefault("orders_reported", [])}
            if key not in known: state["orders_reported"].append(dict(key=key, first_seen_sast=now_sast, source=src, **r))
            else: known[key].update(status=r["status"], last_update_sast=now_sast)
        live_rows = [r for r in rows_clean if not r["status"].startswith(("void", "cancel"))]
        if live_rows: print("   chart:", chart(nm, d, c, g, rows_clean))
    # re-read right before writing (a scheduled routine may also edit alert_state.json) and merge
    fresh = json.load(open(stp)) if stp.exists() else {}
    fresh.setdefault("live", {}).update(live); fresh.pop("live_yahoo", None)
    fk = {o.get("key"): o for o in fresh.setdefault("orders_reported", [])}
    for o in state.get("orders_reported", []):
        if o.get("key") in fk: fk[o["key"]].update({k: v for k, v in o.items() if k in ("status", "last_update_sast", "fill_time_ny", "event_ny")})
        else: fresh["orders_reported"].append(o)
    json.dump(fresh, open(stp, "w"), indent=1, default=str)
