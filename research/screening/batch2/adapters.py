"""Batch 2 adapters: run the FROZEN Model U v1 and MMXM v1..v5 rule objects (vendored byte-identical copies, sha256-pinned
in ADDENDUM_BATCH2.md) on a BID series. Only the per-instrument parameters declared in the addendum are set."""
from __future__ import annotations

import hashlib
import sys
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
VENDOR = HERE / "vendor"
CONFIGS = HERE / "configs"
NY = "America/New_York"

PINS = {
    "vendor/model_u/u_engine.py": "5e98e99e47133905c6662afcdea9d9df4ef74e7afefa49f17e7798925613fe4e",
    "vendor/model_u/run_u_lib.py": "8d00223c1f326bd386c1f924f05dc92fd38a3674639b57cd96df12194cdddad2",
    "vendor/mmxm/__init__.py": "6899cc98e28059141b39ac009c61e496d2bd19da256a5ae6d3480337f7643913",
    "vendor/mmxm/baseline.py": "8298952b8dcd2903e1783bb70a97ed257c255d2b613609c5c0373f72778516ed",
    "vendor/mmxm/config.py": "4614c85b38c52f60018bd1b174368b4be221c47d645960a0cb89e6de16988f65",
    "vendor/mmxm/data.py": "fa2ebee1e25c87507f9faf26fed99f7c7a9edf7a234dcfda198ad163bd255fcd",
    "vendor/mmxm/engine.py": "86e7180980517e20b03a9bf4668dea28329fa203151fe56fa872e02a51f6c67f",
    "vendor/mmxm/htf.py": "a6eb7d5ac75e7ea1fa3213e031e61c564e57c59d49e48bcd5df4b35d2ea47397",
    "vendor/mmxm/htf_v4.py": "0bbfb6f2abe69ced47503c0e574488c6f22cf65f8f11c4ce11adfebf3c8cba23",
    "vendor/mmxm/indicators.py": "0cd95b1134e25f502d9e1699062cf01176c3b03df0f805787f6488d76e3b2ecf",
    "configs/v1_default.yaml": "7e886516566a99eefde24ead96e9f40c7fb74207c09299cd11de86ee8d9dda9b",
    "configs/v2_overnight_LHon_from0930.yaml": "90691aaab076711906d783cc53f3d650752f58b8d63b1ea3d94568619ce1b64d",
    "configs/v3_asia_LHoff_daily_draw.yaml": "9aea2b0158802f81656b99817abb60aeac6c98cbb6b0def70937aad9afaa6e9b",
    "configs/v4_overnight_LHon_midnight_open.yaml": "c466ec8ff668f209c3cb7809ae30ab351c6e6ba7bd5a2d87ad59cc21c58ca579",
    "configs/v5_A_overnight_5mFVG_ce_c12_none.yaml": "3414c77c4693a2ad0557a3f77513118ad292821e6d18f6713b901c7451b67968",
}
MMXM_CONFIGS = {"D2": "v1_default", "D3": "v2_overnight_LHon_from0930", "D4": "v3_asia_LHoff_daily_draw",
                "D5": "v4_overnight_LHon_midnight_open", "D6": "v5_A_overnight_5mFVG_ce_c12_none"}

# NYSE full closures 2023-01 .. 2026-09 (addendum §B3); Model U also excludes 2025-12-24 (H013 DATA fix 7)
NYSE_CLOSED = {"2023-01-02", "2023-01-16", "2023-02-20", "2023-04-07", "2023-05-29", "2023-06-19", "2023-07-04", "2023-09-04",
               "2023-11-23", "2023-12-25", "2024-01-01", "2024-01-15", "2024-02-19", "2024-03-29", "2024-05-27", "2024-06-19",
               "2024-07-04", "2024-09-02", "2024-11-28", "2024-12-25", "2025-01-01", "2025-01-09", "2025-01-20", "2025-02-17",
               "2025-04-18", "2025-05-26", "2025-06-19", "2025-07-04", "2025-09-01", "2025-11-27", "2025-12-25", "2026-01-01",
               "2026-01-19", "2026-02-16", "2026-04-03", "2026-05-25", "2026-06-19", "2026-07-03", "2026-09-07"}
MODEL_U_EXTRA = {"2025-12-24"}


def verify_pins() -> dict:
    bad = {}
    for rel, want in PINS.items():
        got = hashlib.sha256((HERE / rel).read_bytes()).hexdigest()
        if got != want:
            bad[rel] = got
    return bad


def to_df(s, cap: bool) -> pd.DataFrame:
    """ftn Series (naive NY wall clock) -> tz-aware NY DataFrame; the repeated fall-back hour (01:00-02:00) is dropped."""
    idx = pd.DatetimeIndex(s.t).tz_localize(NY, ambiguous="NaT", nonexistent="NaT")
    cols = ("Open", "High", "Low", "Close") if cap else ("open", "high", "low", "close")
    df = pd.DataFrame({cols[0]: s.o, cols[1]: s.h, cols[2]: s.l, cols[3]: s.c}, index=idx, dtype=float)
    df = df[df.index.notna()]
    df = df[~df.index.duplicated(keep="last")].sort_index()
    if not cap:
        df["volume"] = np.nan
        df.index.name = "timestamp"
    return df


# ------------------------------------------------------------------ Model U v1 (H013 invocation)
_MU = None


def _model_u():
    global _MU
    if _MU is None:
        assert not verify_pins(), verify_pins()
        sys.path.insert(0, str(VENDOR / "model_u"))
        import u_engine as E1, run_u_lib as V1
        assert Path(E1.__file__).resolve().parent == (VENDOR / "model_u").resolve()
        _MU = (E1, V1)
    return _MU


def run_model_u(sym: str, s, params: dict, start: str, end: str) -> list[dict]:
    """H013: best_trade(ctx, '11:00', False, False, True), FILL_THRU 1, R_5050; day universe = business days with >= 285
    1m bars in 07:00-11:59 NY, NYSE full closures + 2025-12-24 excluded. params: tick, cost_per_side."""
    E1, V1 = _model_u()
    for m in (E1, V1):          # run_u_lib star-imports u_engine, so it holds its own TICK copy (used in ctx_for tol)
        m.FILL_THRU = 1
        m.TICK = params["tick"]
        m.SLIP = params["cost_per_side"] / params["tick"]
    df = to_df(s, cap=True)
    out = []
    for d in pd.bdate_range(start, end):
        ds = d.strftime("%Y-%m-%d")
        if ds in NYSE_CLOSED or ds in MODEL_U_EXTRA:
            continue
        if len(df.loc[f"{ds} 07:00":f"{ds} 11:59"]) < 285:
            continue
        c = V1.ctx_for(df, ds, sym)
        t = V1.best_trade(c, "11:00", False, False, True)
        if t is None:
            continue
        risk = abs(t["entry"] - t["stop"])
        out.append({"symbol": sym, "date": ds, "session": "ny_am", "R": float(t["res"]["R_part"]), "risk_pts": float(risk),
                    "weekday": date.fromisoformat(ds).weekday(), "direction": t["side"]})
    return out


# ------------------------------------------------------------------ MMXM (H014 engine, run_backtest over the full series)
_MM = None


def _mmxm():
    global _MM
    if _MM is None:
        assert not verify_pins(), verify_pins()
        sys.path.insert(0, str(VENDOR))
        from mmxm import engine, config
        assert Path(engine.__file__).resolve().parent == (VENDOR / "mmxm").resolve()
        _MM = (engine, config)
    return _MM


def run_mmxm(cfg_name: str, sym: str, s, params: dict) -> list[dict]:
    """Frozen config; for the instrument's root only tick_size, min_swing_dist_points and cost_points_round_trip are set
    (addendum §B2). Excludes NYSE full closures (as the MMXM studies' holiday co-report)."""
    engine, config = _mmxm()
    cfg = config.Config.from_yaml(str(CONFIGS / f"{cfg_name}.yaml"))
    root = params["root"]
    cfg = cfg.override(tick_size={**cfg.tick_size, root: params["tick"]},
                       min_swing_dist_points={**cfg.min_swing_dist_points, root: params["min_swing"]},
                       cost_points_round_trip={root: params["cost_rt"]})
    tr, _, _ = engine.run_backtest(to_df(s, cap=False), cfg, root, sym)
    out = []
    for _, r in tr.iterrows():
        ds = str(r["date_ny"])
        if ds in NYSE_CLOSED:
            continue
        out.append({"symbol": sym, "date": ds, "session": "ny_am", "R": float(r["r_multiple"]), "risk_pts": float(r["risk_pts"]),
                    "weekday": date.fromisoformat(ds).weekday(), "direction": r["direction"]})
    return out
