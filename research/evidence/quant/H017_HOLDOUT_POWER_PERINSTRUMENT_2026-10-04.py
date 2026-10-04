"""Per-instrument-mean power for the H017 confirmatory pool (sub-window A), verifying CASSANDRA F2 (A2) with the draft method at 2,000 reps."""
import importlib.util, json, datetime as dt, sys
sys.argv = ["x"]
sp = importlib.util.spec_from_file_location("p", "research/evidence/quant/H017_HOLDOUT_POWER_SIM_2026-10-04.py"); P = importlib.util.module_from_spec(sp); sp.loader.exec_module(P)
P.RANGE["US500"] = (dt.date(2019, 1, 1), dt.date(2022, 12, 23))
src = open("research/evidence/quant/H017_HOLDOUT_POWER_SIM_2026-10-04.py").read()
# per-instrument targets: patch the shift so each instrument is centred to its own mu
orig = P.simulate
def sim_mu(mus, vol=1.0, n=2000):
    class M(float): pass
    def patched(mu, vol, n=n, seed=20261004):
        return orig(mu, vol, n, seed)
    # monkeypatch: replace re-centring by per-instrument targets
    import types
    code = src.split("def simulate(", 1)[1].split("\n\n\nif __name__", 1)[0]
    code = "def simulate(" + code.replace("shift[s] = mu - ", "shift[s] = MUS[s] - ")
    g = dict(vars(P)); g["MUS"] = mus; exec(code, g)
    return g["simulate"](0.0, vol, n)
for label, mus in (("equal +0.15", {"US100": 0.15, "US500": 0.15}), ("equal +0.10", {"US100": 0.10, "US500": 0.10}),
                   ("burned per-instrument means", {"US100": 0.006, "US500": 0.183}), ("era-cost adjusted (CASSANDRA Q8)", {"US100": -0.10, "US500": 0.23})):
    r = sim_mu(mus); print(json.dumps(dict(label=label, mus=mus, N_median=r["N_median"], joint_P1_P5=r["p"]["joint_user"], with_mean010=r["p"]["joint_h016b_style"], p=r["p"])), flush=True)
