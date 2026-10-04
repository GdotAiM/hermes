"""Pluggable 1m loaders + lookahead-safe resampling.

Every loader returns a DataFrame indexed by the 1m bar OPEN time (tz-aware America/New_York)
with float columns open, high, low, close, volume. A 1m bar labelled t is only known at t+1min.
"""
from __future__ import annotations

import os
from typing import Callable, Dict, Iterable, List, Optional

import numpy as np
import pandas as pd

NY = "America/New_York"
COLS = ["open", "high", "low", "close", "volume"]


def _normalise(df: pd.DataFrame, naive_tz: str = NY) -> pd.DataFrame:
    df = df.copy()
    df.columns = [str(c).strip().lower() for c in df.columns]
    if "volume" not in df.columns:
        df["volume"] = np.nan
    idx = pd.DatetimeIndex(df.index)
    if idx.tz is None:
        idx = idx.tz_localize(naive_tz)
    df.index = idx.tz_convert(NY)
    df.index.name = "timestamp"
    df = df[COLS].astype(float)
    df = df[~df.index.duplicated(keep="last")].sort_index()
    df = df.dropna(subset=["open", "high", "low", "close"])
    return df


def load_csv(path: str, naive_tz: str = NY) -> pd.DataFrame:
    """Generic CSV: columns timestamp, open, high, low, close, volume (case-insensitive;
    'Datetime' also accepted). Offsets in the timestamps are honoured; naive times are
    interpreted in `naive_tz`."""
    raw = pd.read_csv(path)
    tcol = next(c for c in raw.columns if c.lower() in ("timestamp", "datetime", "date", "time"))
    ts = pd.to_datetime(raw[tcol], utc=True) if raw[tcol].astype(str).str.contains(r"[+-]\d\d:\d\d$|Z$").any() \
        else pd.to_datetime(raw[tcol])
    raw = raw.drop(columns=[tcol])
    raw.index = pd.DatetimeIndex(ts)
    return _normalise(raw, naive_tz)


def load_parquet(path: str, naive_tz: str = NY) -> pd.DataFrame:
    """Parquet with a DatetimeIndex (or timestamp column) and OHLC[V] columns (CFD history)."""
    raw = pd.read_parquet(path)
    if not isinstance(raw.index, pd.DatetimeIndex):
        tcol = next(c for c in raw.columns if c.lower() in ("timestamp", "datetime", "date", "time"))
        raw = raw.set_index(pd.to_datetime(raw[tcol], utc=True)).drop(columns=[tcol])
    return _normalise(raw, naive_tz)


def load_yfinance(ticker: str, cache_path: Optional[str] = None) -> pd.DataFrame:
    """Max 1m history Yahoo allows (~7 days)."""
    import yfinance as yf
    df = yf.Ticker(ticker).history(period="7d", interval="1m", prepost=True, auto_adjust=False)
    if df is None or df.empty:
        raise RuntimeError(f"yfinance returned no 1m data for {ticker}")
    df = _normalise(df[["Open", "High", "Low", "Close", "Volume"]])
    if cache_path:
        df.to_csv(cache_path)
    return df


def merge_sources(frames: Iterable[pd.DataFrame]) -> pd.DataFrame:
    """Concatenate, later frames win on duplicate timestamps."""
    df = pd.concat(list(frames))
    return df[~df.index.duplicated(keep="last")].sort_index()


def back_adjust_roll(df: pd.DataFrame, roll_bar: str) -> pd.DataFrame:
    """Panama back-adjust a non-adjusted continuous contract at `roll_bar` (NY time of the 1m
    bar in which Yahoo switched contracts). All earlier bars are shifted by
    delta = close(roll_bar) - close(previous bar); the roll bar's open is set to the adjusted
    previous close (its old-contract low is discarded)."""
    ts = pd.Timestamp(roll_bar, tz=NY)
    if ts not in df.index:
        return df
    df = df.copy()
    i = df.index.get_loc(ts)
    if i == 0:
        return df
    delta = df["close"].iloc[i] - df["close"].iloc[i - 1]
    df.iloc[:i, :4] = df.iloc[:i, :4] + delta
    o = df["close"].iloc[i - 1]
    c = df["close"].iloc[i]
    df.iloc[i, 0] = o
    df.iloc[i, 1] = max(df["high"].iloc[i], o, c)
    df.iloc[i, 2] = min(o, c)
    df.attrs["roll_adjust"] = {"bar": str(ts), "delta": float(delta)}
    return df


def detect_jumps(df: pd.DataFrame, mult: float = 25.0) -> pd.DataFrame:
    """Diagnostics: 1m bars whose |close-to-close| move exceeds mult x median 1m range."""
    rng = (df["high"] - df["low"]).median()
    d = df["close"].diff().abs()
    return df.loc[d > mult * rng].assign(jump=d[d > mult * rng])


# ---------------------------------------------------------------------------------------
# Lookahead-safe resampling
# ---------------------------------------------------------------------------------------
def resample(m1: pd.DataFrame, rule: str) -> pd.DataFrame:
    """Resample 1m -> `rule`, bars labelled by OPEN time (left/left). Adds:
    - `end`   : the bar's close time (= start + rule); the bar is usable only at/after `end`.
    - `n`     : number of 1m bars inside.
    The last bar is dropped if it is still forming (its end is after the last 1m bar's close)."""
    agg = m1.resample(rule, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum", })
    n = m1["close"].resample(rule, label="left", closed="left").count()
    agg["n"] = n
    agg = agg[agg["n"] > 0].copy()
    off = pd.tseries.frequencies.to_offset(rule)
    agg["end"] = agg.index + off
    last_close_time = m1.index[-1] + pd.Timedelta(minutes=1)
    agg = agg[agg["end"] <= last_close_time]
    return agg


def closed_bars_asof(htf: pd.DataFrame, now: pd.Timestamp) -> pd.DataFrame:
    """Higher-timeframe bars that are fully closed at wall-clock time `now`."""
    return htf[htf["end"] <= now]


# ---------------------------------------------------------------------------------------
# Named datasets
# ---------------------------------------------------------------------------------------
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(HERE, "data")

FUTURES_ROLLS = {"NQ": ["2026-09-14 11:30"], "ES": ["2026-09-14 11:30"]}  # Yahoo Sep->Dec switch


def load_futures(root: str, refresh_yf: bool = False, roll_adjust: bool = True) -> pd.DataFrame:
    """NQ/ES: 10-25 Sep 2026 CSV merged with the latest yfinance 1m pull (cached)."""
    parts = []
    base = os.path.join(DATA, f"{root}_1m_0910_0925.csv")
    if os.path.exists(base):
        parts.append(load_csv(base))
    cache = sorted(f for f in os.listdir(DATA) if f.startswith(f"{root}_1m_yf_pull_"))
    if refresh_yf or not cache:
        from datetime import date
        parts.append(load_yfinance(f"{root}=F", os.path.join(DATA, f"{root}_1m_yf_pull_{date.today():%Y%m%d}.csv")))
    else:
        parts.append(load_csv(os.path.join(DATA, cache[-1])))
    df = merge_sources(parts)
    if roll_adjust:
        for r in FUTURES_ROLLS.get(root, []):
            df = back_adjust_roll(df, r)
    return df


def load_cfd(name: str) -> pd.DataFrame:
    """US100 / US500 CFD mid-price history (no volume)."""
    return load_parquet(os.path.join(DATA, f"{name}_1m.parquet"))


LOADERS: Dict[str, Callable[..., pd.DataFrame]] = {
    "futures": load_futures,
    "cfd": load_cfd,
    "csv": load_csv,
    "yfinance": load_yfinance,
}
