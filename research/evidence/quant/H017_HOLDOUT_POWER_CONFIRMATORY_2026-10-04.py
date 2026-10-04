"""H017 confirmatory-pool power (ORION Q2 advisory: US100 + US500 sub-window A, both 2019-02-04 -> 2022-12-23) and P(pooled N < 400) (Q5 floor), same method and burned inputs as H017_HOLDOUT_POWER_SIM_2026-10-04.py; also the Q10 conditional late window (Dukascopy BID only from 2020-07-07). Burned data and public index levels only; no holdout bar is read. Run from the repo root."""
import importlib.util, json, datetime as dt, sys, statistics as st
sys.argv = ["x"]
sp = importlib.util.spec_from_file_location("p", "research/evidence/quant/H017_HOLDOUT_POWER_SIM_2026-10-04.py"); P = importlib.util.module_from_spec(sp); sp.loader.exec_module(P)
def run(label, lo, vol, mus=(0.10, 0.15)):
    P.RANGE["US100"] = (lo, dt.date(2022, 12, 23)); P.RANGE["US500"] = (lo, dt.date(2022, 12, 23))
    e = P.expected_n(vol)
    # N distribution under the same resampling (mu irrelevant for N)
    out = dict(label=label, start=lo.isoformat(), vol=vol, expected_N=dict(US100=e["US100"]["expected"], US500=e["US500"]["expected"], pooled=e["pooled"]))
    for mu in mus:
        r = P.simulate(mu, vol, n=2000)
        out[f"mu_{mu:+.2f}"] = dict(N_median=r["N_median"], N_range=[r["N_min"], r["N_max"]], **r["p"])
    print(json.dumps(out), flush=True)
# N<400 probability needs the N draws: re-implement count only
def p_floor(lo, vol, n=4000, seed=20261004):
    import random
    P.RANGE["US100"] = (lo, dt.date(2022, 12, 23)); P.RANGE["US500"] = (lo, dt.date(2022, 12, 23))
    YD = P.year_days(); rng = random.Random(seed); plan = []
    for y in sorted(YD["US100"]["by_year"]):
        plan += [y] * (2 * min(YD["US100"]["by_year"][y], YD["US500"]["by_year"].get(y, 0)))
    keep = lambda t, y: vol is None or t["risk"] * P.scale(t["inst"], y, vol) >= P.MIN_RISK[t["inst"]]
    Ns = []
    for _ in range(n):
        c = 0
        for y in plan:
            sl = rng.choice(P.SLOTS); c += sum(1 for s in P.INST if s in sl and keep(sl[s], y))
        Ns.append(c)
    Ns.sort()
    return dict(start=lo.isoformat(), vol=vol, N_p01=Ns[n // 100], N_median=Ns[n // 2], p_N_below_400=sum(x < 400 for x in Ns) / n)
if __name__ == "__main__":
    full, late = dt.date(2019, 1, 1), dt.date(2020, 7, 7)
    run("confirmatory pool (US100 + US500 A), central", full, 1.0)
    run("confirmatory pool, naive (no min-stop scaling)", full, None)
    run("confirmatory pool, vol 0.8 (lower point volatility)", full, 0.8)
    run("conditional window if Dukascopy BID stays from 2020-07-07 only (Q1/Q10)", late, 1.0)
    run("conditional late window, vol 0.8", late, 0.8)
    for lo in (full, late):
        for vol in (1.0, 0.8, 0.6, None):
            print(json.dumps(dict(floor=p_floor(lo, vol))), flush=True)
