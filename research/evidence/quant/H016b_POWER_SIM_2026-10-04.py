"""H016b power / kill / futility simulation on the BURNED fixed-REV exploratory trades (variance only, never evidence).
H016b (CASSANDRA F9): same method and inputs as H016_POWER_SIM_2026-10-04.py, restricted to FILTER-ELIGIBLE burned trades
(4 of 258 excluded: sessions failing the 171/180 BID+ASK killzone filter, incl. the 2026-03-23 US100 stale-entry phantom fill).
Original: adapted from H015b_POWER_SIM_2026-10-04.py: same method, new inputs (ftn/demo-fixes 9bed235, correct-side bid/ask
fills + DATA slippage floors, flat book). Clustered paths: whole (date, killzone) clusters resampled with replacement,
R re-centred to mu; normal-approx cluster SE for the bounds; foil criterion approximated as the burned pooled foil
median + 1.645*SD/sqrt(N). Futility evaluated once at trade 200 (upper 97.5% cluster bound < +0.10).
Run from the repo root: python research/evidence/quant/H016b_POWER_SIM_2026-10-04.py N {stats|kill|power K}"""
import csv, statistics as st, math, random, json, sys
from collections import defaultdict
SRC = "research/evidence/quant/FTN_M9_TRADES_{}_base_2026-10-04_h016_fixed_rev_burned.csv"
# filter-eligible = killzone >= 171/180 on BID and ASK, a BID and an ASK bar at exactly entry-1m, >= 1 BID and ASK bar in
# [15:45, 16:00) NY (checked on the burned canonical Dukascopy BID/ASK export; 2026-03-23 also lacks the entry minute)
EXCLUDE = {("US100", "2026-03-23", "ny_am"), ("US100", "2026-05-29", "london"), ("US500", "2026-04-10", "ny_am"),
           ("US500", "2026-05-29", "london")}
T = []
for s in ("US100", "US500"):
    for r in csv.DictReader(open(SRC.format(s))):
        if (s, r["date"], r["session"]) in EXCLUDE:
            continue
        T.append(dict(inst=s, key=(r["date"], r["session"]), R=float(r["R"]), risk=float(r["risk_pts"])))
cl = defaultdict(list)
for t in T:
    cl[t["key"]].append(t)
C = list(cl.values()); m = st.mean(t["R"] for t in T)
p25 = {s: sorted(t["risk"] for t in T if t["inst"] == s)[len([t for t in T if t["inst"] == s]) // 4] for s in ("US100", "US500")}
SD = st.pstdev([t["R"] for t in T])
# burned correct-side foil medians (FTN_M9_SCORE_2026-10-04_h016_fixed_rev_burned.json), trade-weighted pooled
FOIL_MED = (146 * -0.05145032406650431 + 112 * -0.09435072801475754) / 258
N = int(sys.argv[1]) if len(sys.argv) > 1 else 800


def path(mu, rng):
    out = []; n = 0
    while n < N:
        c = rng.choice(C); out.extend((t["inst"], t["R"] - m + mu, t["risk"]) for t in c); n += len(c)
        out.append(None)
    return out


def split(p):
    cls = []; cur = []
    for x in p:
        if x is None:
            cls.append(cur); cur = []
        else:
            cur.append(x)
    return cls


def cl_se(cls):
    cls = [c for c in cls if c]
    n = sum(len(c) for c in cls); mu = sum(x[1] for c in cls for x in c) / n; k = len(cls); mb = n / k
    res = [sum(x[1] for x in c) - mu * len(c) for c in cls]
    return mu, math.sqrt(st.pvariance(res) / k) / mb


def fut_fail(first200):
    mu_, se = cl_se(first200)
    return mu_ + 1.96 * se < 0.10


def sim(mu, K, n=3000, seed=20261004, futility=True):
    rng = random.Random(seed); kills = fut = passed = 0; crit = [0] * 6
    for _ in range(n):
        cls = split(path(mu, rng))
        tr = []; cnt = 0
        for c in cls:
            if cnt >= N: break
            c = c[:N - cnt]; tr.append(c); cnt += len(c)
        cum = 0; killed = False; futl = False; seen = 0; done = []
        for c in tr:
            cc = []
            for x in c:
                cum += x[1]; seen += 1; cc.append(x)
                if cum <= K: killed = True; break
                if futility and seen == 200:
                    if fut_fail(done + [cc]): futl = True; break
            done.append(cc)
            if killed or futl: break
        if killed: kills += 1; continue
        if futl: fut += 1; continue
        allx = [x for c in done for x in c][:N]; mu_, se = cl_se(done); n_ = len(allx)
        rs = sorted((x[1] for x in allx), reverse=True); k = max(1, n_ // 100)
        c1 = mu_ >= 0.10; c2 = mu_ - 1.645 * se > 0; c3 = mu_ > FOIL_MED + 1.645 * SD / math.sqrt(n_)
        c4 = all(st.mean(x[1] for x in allx if x[0] == s) > 0 for s in ("US100", "US500"))
        c5 = st.mean(rs[k:]) > 0; c6 = st.mean([x[1] for x in allx if x[2] >= p25[x[0]]]) > 0
        cs = [c1, c2, c3, c4, c5, c6]
        for i, v in enumerate(cs): crit[i] += v
        passed += all(cs)
    return dict(mu=mu, K=K, N=N, p_kill=round(kills / n, 4), p_futility=round(fut / n, 4), p_pass=round(passed / n, 4),
                crit=[round(x / n, 3) for x in crit])


if __name__ == "__main__":
    mode = sys.argv[2] if len(sys.argv) > 2 else "kill"
    if mode == "kill":
        for K in (-30, -35, -40, -45, -50, -55, -60):
            print(json.dumps(sim(0.15, K, n=2000, futility=False)), flush=True)
    elif mode == "power":
        K = float(sys.argv[3])
        for mu in (0.15, 0.10, 0.0, -0.10):
            print(json.dumps(sim(mu, K, n=3000)), flush=True)
    if mode == "stats":
        both = [c for c in C if len(c) == 2]
        a = [next(t["R"] for t in c if t["inst"] == "US100") for c in both]; b = [next(t["R"] for t in c if t["inst"] == "US500") for c in both]
        ma, mb_ = st.mean(a), st.mean(b)
        rho = sum((x - ma) * (y - mb_) for x, y in zip(a, b)) / math.sqrt(sum((x - ma) ** 2 for x in a) * sum((y - mb_) ** 2 for y in b))
        vres = st.pvariance([sum(t["R"] for t in c) - m * len(c) for c in C]); mbar = len(T) / len(C)
        deff = vres / mbar / SD ** 2
        print(json.dumps(dict(trades=len(T), clusters=len(C), clusters_both=len(both), mean_cluster_size=round(mbar, 3), rho_R=round(rho, 3),
                              mean_R_burned=round(m, 4), sd_R=round(SD, 3), cluster_resid_var=round(vres, 3), deff=round(deff, 3),
                              foil_median_pooled=round(FOIL_MED, 4),
                              N_trades={d: math.ceil(((1.6449 + 0.8416) ** 2 * vres / d ** 2 / mbar ** 2) * mbar) for d in (0.10, 0.15, 0.20)})))
