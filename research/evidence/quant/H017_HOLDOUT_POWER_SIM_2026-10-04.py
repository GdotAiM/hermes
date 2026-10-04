"""H017 (holdout) expected-N and power simulation. DRAFT input to the H017 prereg; never evidence.

Inputs (and ONLY these):
  * BURNED fixed-REV trades (H016b's filter-eligible 254 of 258; research/evidence/quant/FTN_M9_TRADES_{US100,US500}_base_
    2026-10-04_h016_fixed_rev_burned.csv) and the burned session count (544 = 272 trading days x 2 killzones,
    FTN_M9_SCORE_2026-10-04_h016_fixed_rev_burned.json).
  * The NYSE exchange calendar (/workspace/marketdata/data/calendar/exchange_calendar.parquet; dates and status only).
  * Approximate PUBLIC annual-average index levels (general knowledge; NOT computed from any library file) used only to
    scale the fixed-point min-stop gate (see LEVELS).
No bar file inside DATA's certified-untouched ranges is opened, loaded, decoded or hashed by this script.

Method:
  * Session slots: every NYSE full trading day ('open', not 'early_close') in the counted window x 2 killzones. The first
    22 trading days of each instrument's certified range are kernel context only (rule.context_history, >= 22 sessions).
  * Each slot draws one of the 544 burned session slots uniformly (empty slots included) and inherits its 0/1 trade per
    instrument; a trade is KEPT in year y iff risk_pts * s_y >= min_risk, s_y = LEVEL[y] / burned median entry (x vol
    factor). This models only the fixed-point min-stop gate (US100 10.2 pt, US500 4.88 pt) at lower index levels.
  * R re-centred per instrument to mu over the expected kept composition. Bounds: normal-approximation session-cluster SE,
    one-sided z = 1.645 (the binding call is the cluster percentile bootstrap v[500]; the approximation is for power only).
  * Criteria per replicate: LB > 0 (pooled cluster), mean > 0 on US100 and US500, ex-top-1% > 0, ex-small-stop (< own
    sample p25 per instrument) > 0, foil (burned pooled foil median + 1.645 SD / sqrt(n)), and mean >= +0.10 (option).
    Fill-fragility and the conservative-exit leg cannot be simulated from burned data (0/258 one-sided; see the prereg).
Run from the repo root: python research/evidence/quant/H017_HOLDOUT_POWER_SIM_2026-10-04.py"""
import csv, json, math, random, statistics as st, datetime as dt, sys
import pandas as pd

SRC = "research/evidence/quant/FTN_M9_TRADES_{}_base_2026-10-04_h016_fixed_rev_burned.csv"
EXCLUDE = {("US100", "2026-03-23", "ny_am"), ("US100", "2026-05-29", "london"), ("US500", "2026-04-10", "ny_am"),
           ("US500", "2026-05-29", "london")}
BURNED_SLOTS = 544
MIN_RISK = {"US100": 10.2, "US500": 4.88}
CAL = "/workspace/marketdata/data/calendar/exchange_calendar.parquet"
# certified untouched ranges (DATA_RULINGS_MARKETDATA_2026-10-04.md s.4; marketdata/data/untouched_certified.json), NY dates
RANGE = {"US100": (dt.date(2019, 1, 1), dt.date(2022, 12, 23)), "US500": (dt.date(2019, 1, 1), dt.date(2025, 5, 30))}
CONTEXT_DAYS = 22
# approximate public annual-average index levels (NDX for US100, SPX for US500); 2022 NDX to 23 Dec, 2025 SPX Jan-May
LEVELS = {"US100": {2019: 7950, 2020: 10250, 2021: 14500, 2022: 12400},
          "US500": {2019: 2915, 2020: 3218, 2021: 4273, 2022: 4099, 2023: 4284, 2024: 5428, 2025: 5800}}
FOIL_MED = (146 * -0.05145032406650431 + 112 * -0.09435072801475754) / 258
INST = ("US100", "US500")

T = []
for s in INST:
    for r in csv.DictReader(open(SRC.format(s))):
        if (s, r["date"], r["session"]) in EXCLUDE:
            continue
        T.append(dict(inst=s, key=(r["date"], r["session"]), R=float(r["R"]), risk=float(r["risk_pts"]), entry=float(r["entry"])))
slots = {}
for t in T:
    slots.setdefault(t["key"], {})[t["inst"]] = t
SLOTS = list(slots.values()) + [{}] * (BURNED_SLOTS - len(slots))
SD = st.pstdev([t["R"] for t in T])
BURN_LEVEL = {s: st.median(t["entry"] for t in T if t["inst"] == s) for s in INST}

cal = pd.read_parquet(CAL)
nyse = cal[(cal.exchange == "NYSE")]
OPEN = sorted(pd.to_datetime(nyse[nyse.status == "open"].date).dt.date)
ALL_SESS = sorted(pd.to_datetime(nyse[nyse.status != "holiday"].date).dt.date)


def counted_days(s):
    lo, hi = RANGE[s]
    sess = [d for d in ALL_SESS if lo <= d <= hi]
    first = sess[CONTEXT_DAYS]                      # 22 sessions of context first
    return [d for d in OPEN if first <= d <= hi], first


def year_days():
    out = {}
    for s in INST:
        days, first = counted_days(s)
        yd = {}
        for d in days:
            yd[d.year] = yd.get(d.year, 0) + 1
        out[s] = dict(first_counted=first.isoformat(), last=RANGE[s][1].isoformat(), full_trading_days=len(days), by_year=yd)
    return out


def scale(s, y, vol):
    return LEVELS[s][y] / BURN_LEVEL[s] * vol


def expected_n(vol=None):
    YD = year_days(); res = {}
    for s in INST:
        tr = [t for t in T if t["inst"] == s]; rate_naive = len(tr) / BURNED_SLOTS
        tot = 0.0; by = {}
        for y, nd in YD[s]["by_year"].items():
            keep = 1.0 if vol is None else sum(t["risk"] * scale(s, y, vol) >= MIN_RISK[s] for t in tr) / len(tr)
            e = 2 * nd * rate_naive * keep; by[y] = round(e, 1); tot += e
        res[s] = dict(per_session_rate_burned=round(rate_naive, 4), expected=round(tot), by_year=by)
    res["pooled"] = round(res["US100"]["expected"] + res["US500"]["expected"])
    return res


def simulate(mu, vol, n=2000, seed=20261004):
    YD = year_days(); rng = random.Random(seed)
    plan = []                                    # (year, instruments active)
    for y in sorted(set(YD["US100"]["by_year"]) | set(YD["US500"]["by_year"])):
        n100 = YD["US100"]["by_year"].get(y, 0); n500 = YD["US500"]["by_year"].get(y, 0)
        both = min(n100, n500)
        plan += [(y, INST)] * (2 * both) + [(y, ("US500",))] * (2 * (n500 - both)) + [(y, ("US100",))] * (2 * (n100 - both))
    keep = lambda t, y: vol is None or t["risk"] * scale(t["inst"], y, vol) >= MIN_RISK[t["inst"]]
    shift = {}
    for s in INST:                               # re-centre to mu over the expected kept composition
        w = [(t["R"], sum(1 for (y, act) in plan if s in act and keep(t, y))) for t in T if t["inst"] == s]
        shift[s] = mu - sum(r * k for r, k in w) / sum(k for _, k in w)
    crit = dict(lb=0, both=0, top1=0, small=0, foil=0, mean010=0, joint_user=0, joint_h016b_style=0)
    Ns = []
    for _ in range(n):
        cls = []
        for y, act in plan:
            sl = rng.choice(SLOTS)
            c = [(s, sl[s]["R"] + shift[s], sl[s]["risk"]) for s in act if s in sl and keep(sl[s], y)]
            if c:
                cls.append(c)
        xs = [x for c in cls for x in c]; nn = len(xs); Ns.append(nn)
        m = sum(x[1] for x in xs) / nn; k = len(cls); mb = nn / k
        se = math.sqrt(st.pvariance([sum(x[1] for x in c) - m * len(c) for c in cls]) / k) / mb
        lb = m - 1.645 * se > 0
        both = all(st.mean(x[1] for x in xs if x[0] == s) > 0 for s in INST)
        rs = sorted((x[1] for x in xs), reverse=True); top1 = st.mean(rs[max(1, nn // 100):]) > 0
        p25 = {s: sorted(x[2] for x in xs if x[0] == s)[len([x for x in xs if x[0] == s]) // 4] for s in INST}
        small = st.mean([x[1] for x in xs if x[2] >= p25[x[0]]]) > 0
        foil = m > FOIL_MED + 1.645 * SD / math.sqrt(nn); m010 = m >= 0.10
        for kname, v in (("lb", lb), ("both", both), ("top1", top1), ("small", small), ("foil", foil), ("mean010", m010)):
            crit[kname] += v
        crit["joint_user"] += lb and both and top1 and small and foil
        crit["joint_h016b_style"] += lb and both and top1 and small and foil and m010
    return dict(mu=mu, vol=vol, reps=n, N_median=int(st.median(Ns)), N_min=min(Ns), N_max=max(Ns),
                p={k: round(v / n, 3) for k, v in crit.items()})


if __name__ == "__main__":
    out = dict(burned=dict(trades=len(T), sessions=BURNED_SLOTS, burned_median_entry=BURN_LEVEL, sd_R=round(SD, 3),
                           per_instrument=dict((s, len([t for t in T if t["inst"] == s])) for s in INST)),
               counted_windows=year_days(),
               expected_N=dict(naive_no_scaling=expected_n(None), level_scaled_vol1=expected_n(1.0),
                               level_scaled_vol1_25=expected_n(1.25), level_scaled_vol1_5=expected_n(1.5)))
    print(json.dumps(out, indent=1), flush=True)
    for vol in (1.0, None, 1.5):
        for mu in (0.0, 0.10, 0.15, 0.20):
            print(json.dumps(simulate(mu, vol)), flush=True)
