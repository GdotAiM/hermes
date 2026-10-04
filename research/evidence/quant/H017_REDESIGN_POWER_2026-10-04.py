"""H017 redesign options: expected N and power. Burned trades, file-count/calendar metadata and public index levels only
(same inputs and method as H017_HOLDOUT_POWER_SIM_2026-10-04.py); no certified-untouched bar is opened.
Confirmatory window for every option: [2019-02-04, 2022-12-23] (US500 sub-window B stays exploratory).
Criteria per option: P1 cluster LB > 0 on the option's primary pool, P2 every primary instrument mean > 0, P3 ex-top-1% > 0,
P4 ex-small-stop > 0, P5 foil approx (as the draft), joint = all; 'rep' = joint AND pooled mean >= +0.10 (replication bar).
Gross R (option O4) = net R + (|fill_in - signal entry| + exit slip + measured spread for shorts) / risk_pts - an approximation of
the BID-chart fill-free outcome (not the pinned simulate_both). Run from the repo root."""
import importlib.util, json, math, random, statistics as st, datetime as dt, sys, csv
sys.argv = ["x"]
sp = importlib.util.spec_from_file_location("p", "research/evidence/quant/H017_HOLDOUT_POWER_SIM_2026-10-04.py"); P = importlib.util.module_from_spec(sp); sp.loader.exec_module(P)
P.RANGE["US500"] = (dt.date(2019, 1, 1), dt.date(2022, 12, 23))
SLIP = {"US100": dict(stop=0.5, market=0.5, limit=0.25), "US500": dict(stop=0.25, market=0.25, limit=0.10)}
# gross R per burned trade (approximation, see docstring)
G = {}
for s in P.INST:
    for r in csv.DictReader(open(P.SRC.format(s))):
        if (s, r["date"], r["session"]) in P.EXCLUDE: continue
        risk = float(r["risk_pts"]); short = r["direction"] == "bearish"
        ex = SLIP[s]["limit"] if r["exit"] == "target" else SLIP[s]["stop"] if r["exit"] == "stop" else SLIP[s]["market"]
        cost = abs(float(r["fill_in"]) - float(r["entry"])) + ex + (float(r["spread_measured"] or 0) if short else 0.0)
        G[(s, r["date"], r["session"])] = float(r["R"]) + cost / risk
for t in P.T:
    t["G"] = G[(t["inst"],) + t["key"]]
GROSS_MEAN = {s: st.mean(t["G"] for t in P.T if t["inst"] == s) for s in P.INST}
NET_MEAN = {s: st.mean(t["R"] for t in P.T if t["inst"] == s) for s in P.INST}

def sim(insts, mus, field="R", min_risk=None, n=2000, seed=20261004, vol=1.0):
    MR = dict(P.MIN_RISK, **(min_risk or {}))
    YD = P.year_days(); rng = random.Random(seed); plan = []
    for y in sorted(YD["US100"]["by_year"]):
        plan += [y] * (2 * min(YD["US100"]["by_year"][y], YD["US500"]["by_year"].get(y, 0)))
    keep = lambda t, y: t["risk"] * P.scale(t["inst"], y, vol) >= MR[t["inst"]]
    shift = {}
    for s in insts:
        w = [(t[field], sum(1 for y in plan if keep(t, y))) for t in P.T if t["inst"] == s]
        shift[s] = mus[s] - sum(r * k for r, k in w) / sum(k for _, k in w)
    c = dict(lb=0, each=0, top1=0, small=0, foil=0, joint=0, rep=0); Ns = []
    for _ in range(n):
        cls = []
        for y in plan:
            sl = rng.choice(P.SLOTS)
            cc = [(s, sl[s][field] + shift[s], sl[s]["risk"]) for s in insts if s in sl and keep(sl[s], y)]
            if cc: cls.append(cc)
        xs = [x for cc in cls for x in cc]; nn = len(xs); Ns.append(nn)
        m = sum(x[1] for x in xs) / nn; k = len(cls); mb = nn / k
        se = math.sqrt(st.pvariance([sum(x[1] for x in cc) - m * len(cc) for cc in cls]) / k) / mb
        lb = m - 1.645 * se > 0
        each = all(st.mean(x[1] for x in xs if x[0] == s) > 0 for s in insts)
        rs = sorted((x[1] for x in xs), reverse=True); top1 = st.mean(rs[max(1, nn // 100):]) > 0
        p25 = {s: sorted(x[2] for x in xs if x[0] == s)[len([x for x in xs if x[0] == s]) // 4] for s in insts}
        small = st.mean([x[1] for x in xs if x[2] >= p25[x[0]]]) > 0
        foil = m > P.FOIL_MED + 1.645 * P.SD / math.sqrt(nn)
        j = lb and each and top1 and small and foil
        for kk, v in (("lb", lb), ("each", each), ("top1", top1), ("small", small), ("foil", foil), ("joint", j), ("rep", j and m >= 0.10)): c[kk] += v
    return dict(N_median=int(st.median(Ns)), N_p01=sorted(Ns)[n // 100], p_N_below_400=sum(x < 400 for x in Ns) / n,
                p_N_below_150=sum(x < 150 for x in Ns) / n, **{k: round(v / n, 3) for k, v in c.items()})

ERA = {"US100": -0.10, "US500": 0.23}            # CASSANDRA Q8 pre-data expectation (net, pinned rule)
US100_ERA_MIN_RISK = round(4 * (3.53 + 2 * 0.5), 2)   # O2: min_risk = 4 x (DATA pre-switch off-RTH p90 3.53 + 2 x slip) = 18.12 pt
if __name__ == "__main__":
    print(json.dumps(dict(burned_net_means=NET_MEAN, burned_gross_means_approx=GROSS_MEAN, O2_US100_min_risk=US100_ERA_MIN_RISK)), flush=True)
    both, u5 = ("US100", "US500"), ("US500",)
    sc = lambda insts, burned, era: {"equal_+0.15": {s: 0.15 for s in insts}, "equal_+0.10": {s: 0.10 for s in insts},
                                     "burned_per_instrument": {s: burned[s] for s in insts}, "era_cost_adjusted": {s: era[s] for s in insts}}
    opts = {
      "O0_baseline_pooled_net": (both, "R", None, sc(both, NET_MEAN, ERA)),
      "O1_US500_only_net": (u5, "R", None, sc(u5, NET_MEAN, ERA)),
      "O2_newID_US100_era_min_stop_pooled_net": (both, "R", {"US100": US100_ERA_MIN_RISK}, sc(both, NET_MEAN, dict(ERA, US100=NET_MEAN["US100"]))),
      "O4_gross_primary_pooled": (both, "G", None, sc(both, GROSS_MEAN, GROSS_MEAN)),
    }
    for name, (insts, field, mr, scen) in opts.items():
        for lab, mus in scen.items():
            print(json.dumps(dict(option=name, scenario=lab, mus=mus, **sim(insts, mus, field, mr))), flush=True)
