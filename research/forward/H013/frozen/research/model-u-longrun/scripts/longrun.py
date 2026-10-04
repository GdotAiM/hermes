"""Run Model U v1 base, v2 base, v2 09:25 start, v2 no-fib-filter on Dukascopy US100/US500 CFD 1m (BID), identical rules.
Costs: per-side adverse cost in price units (COST[inst]) applied on entry and on every exit (engine SLIP is in ticks of 0.25)."""
import sys, pathlib, json, numpy as np, pandas as pd
HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE / "v1")); sys.path.insert(0, str(HERE / "v2"))
import u_engine as E1, run_u_lib as V1
import u2_engine as E2, run_u2 as V2

HOLIDAYS = {"2025-09-01", "2025-11-27", "2025-12-25", "2026-01-01", "2026-01-19", "2026-02-16", "2026-04-03", "2026-05-25",
            "2026-06-19", "2026-07-03", "2026-09-07"}   # NYSE full closures (CFD may trade thinly; excluded)
IS_DAYS = {d.strftime("%Y-%m-%d") for d in pd.bdate_range("2026-09-14", "2026-09-25")}
COST = json.load(open("data/costs.json"))     # {"US100": per-side cost in points, "US500": ...}
MODELS = {"v1 base": None, "v2 base": {}, "v2 start 09:25": dict(start="09:25"), "v2 no fib filter": dict(fib=False)}

def load(nm):
    df = pd.read_parquet(f"data/{nm}_1m.parquet")
    return df[["Open", "High", "Low", "Close"]].astype(float)

def trading_days(df):
    days, dq = [], []
    for d in pd.bdate_range("2025-09-02", "2026-09-25"):
        d = d.strftime("%Y-%m-%d")
        n_07_12 = len(df.loc[f"{d} 07:00":f"{d} 11:59"]); n_02_12 = len(df.loc[f"{d} 02:00":f"{d} 11:59"])
        ok = d not in HOLIDAYS and n_07_12 >= 285
        dq.append(dict(date=d, bars_0700_1159=n_07_12, bars_0200_1159=n_02_12, missing_0200_1159=600 - n_02_12,
                       holiday=d in HOLIDAYS, used=ok))
        if ok: days.append(d)
    return days, pd.DataFrame(dq)

def run(nm):
    df = load(nm); days, dq = trading_days(df)
    E1.SLIP = COST[nm] / E1.TICK; E2.SLIP = COST[nm] / E2.TICK
    rows = []
    for d in days:
        c1 = c2 = None
        for model, v in MODELS.items():
            if model == "v1 base":
                c1 = c1 or V1.ctx_for(df, d, nm); c, g = c1, c1["g"]
                t = V1.best_trade(c, "11:00", False, False, True)
            else:
                c2 = c2 or V2.ctx_for(df, d); c, g = c2, c2["g"]
                found, _ = V2.all_fills(c, V2.params(c, v)); t = V2.pack(found[0]) if found else None
            base = dict(model=model, inst=nm, date=d, sample="IS" if d in IS_DAYS else "OOS", range_low=c["L"], range_high=c["H"])
            if t is None: rows.append({**base, "status": "no trade"}); continue
            r = t["res"]; ft = g.index[r["fill_i"]]; risk = abs(t["entry"] - t["stop"])
            rows.append({**base, "status": "trade", "direction": t["side"], "type": t["cand"]["kind"], "trigger": t["cand"]["why"],
                         "entry_rule": t["cand"].get("fibtag", "FVG CE"), "entry_time_ny": ft.strftime("%H:%M"),
                         "entry": t["entry"], "stop": t["stop"], "t1": t["t1"], "t2": t["t2"], "risk_pts": risk,
                         "t1_R_planned": abs(t["t1"] - t["entry"]) / risk, "t2_R_planned": abs(t["t2"] - t["entry"]) / risk,
                         "R_T1": r["R_t1"], "out_T1": r["out_t1"], "R_T2": r["R_t2"], "out_T2": r["out_t2"],
                         "R_5050": r["R_part"], "out_5050": r["out_part"], "exit_time_5050": g.index[r["exit_part_i"]].strftime("%H:%M"),
                         "cost_per_side_pts": COST[nm]})
    return pd.DataFrame(rows), dq.assign(inst=nm)

if __name__ == "__main__":
    mult = float(sys.argv[1]) if len(sys.argv) > 1 else 1.0          # cost stress multiplier
    thru = int(sys.argv[2]) if len(sys.argv) > 2 else 0               # fill-through ticks robustness
    E1.FILL_THRU = E2.FILL_THRU = thru
    COST.update({k: v * mult for k, v in COST.items()})
    allr, alldq = [], []
    for nm in ("US100", "US500"):
        r, dq = run(nm); allr.append(r); alldq.append(dq); print(nm, "days used", dq.used.sum(), "trades", (r.status == "trade").sum())
    res = pd.concat(allr)
    if mult == 1.0 and thru == 0:
        res.to_csv("trades.csv", index=False); pd.concat(alldq).to_csv("data/data_quality_days.csv", index=False)
    else:
        res.to_csv(f"data/trades_cost{mult:g}x_thru{thru}.csv", index=False)
