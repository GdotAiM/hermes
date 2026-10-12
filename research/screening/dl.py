"""S1 data: Dukascopy public datafeed 1m BID+ASK day files for NEW instruments only (protocol section 1).

Pattern of scripts/dl_dukascopy.py and research/forward/H016b/duka.py (decode/normalise re-implemented here; the
frozen harness is not imported). Hard guards: instrument allowlist (never US100/US500), UTC days
2023-01-01 .. 2026-09-25 only, output under $SCREENING_DATA (default /workspace/screening-data), never
/workspace/marketdata.

  python -m research.screening.dl download [threads]   # raw .bi5 (idempotent; 404 -> empty marker)
  python -m research.screening.dl build                 # -> <SYM>_1m_{bid,ask}.csv.gz (NY wall clock with offset)
"""
from __future__ import annotations

import datetime as dt
import gzip
import json
import lzma
import os
import pathlib
import struct
import sys
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from zoneinfo import ZoneInfo

INSTRUMENTS = {"GER40": "DEUIDXEUR", "US30": "USA30IDXUSD", "XAUUSD": "XAUUSD"}
FORBIDDEN = {"USATECHIDXUSD", "USA500IDXUSD", "US100", "US500"}
START, END = dt.date(2023, 1, 1), dt.date(2026, 9, 25)
SIDES = ("BID", "ASK")
URL = "https://datafeed.dukascopy.com/datafeed/{sym}/{y:04d}/{m0:02d}/{d:02d}/{side}_candles_min_1.bi5"
REC = struct.Struct(">5if")
UTC, NY = dt.timezone.utc, ZoneInfo("America/New_York")


def root() -> pathlib.Path:
    r = pathlib.Path(os.environ.get("SCREENING_DATA", "/workspace/screening-data")).resolve()
    if str(r).startswith("/workspace/marketdata"):
        raise SystemExit("refusing: /workspace/marketdata is off limits")
    return r


def guard(sym: str, day: dt.date) -> None:
    if sym in FORBIDDEN or sym not in INSTRUMENTS.values():
        raise ValueError(f"instrument {sym} not allowed in S1")
    if not (START <= day <= END):
        raise ValueError(f"{day} outside the S1 window {START}..{END}")


def days():
    d = START
    while d <= END:
        if d.weekday() != 5:
            yield d
        d += dt.timedelta(days=1)


def raw_path(sym, side, day):
    return root() / "raw" / sym / side / f"{day:%Y%m%d}.bi5"


def get(job):
    sym, side, day = job
    guard(sym, day)
    p = raw_path(sym, side, day)
    if p.exists():
        return "skip"
    p.parent.mkdir(parents=True, exist_ok=True)
    u = URL.format(sym=sym, y=day.year, m0=day.month - 1, d=day.day, side=side)
    for k in range(6):
        try:
            with urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"}), timeout=60) as r:
                data = r.read()
            tmp = p.with_suffix(".part"); tmp.write_bytes(data); tmp.rename(p)
            return "ok"
        except urllib.error.HTTPError as e:
            if e.code == 404:
                p.write_bytes(b""); return "404"
        except Exception:
            pass
        time.sleep(min(60, 2 ** k * 2))
    return "fail"


def download(threads=8):
    jobs = [(s, side, d) for d in sorted(days(), reverse=True) for s in INSTRUMENTS.values() for side in SIDES]
    t0, st = time.time(), {}
    with ThreadPoolExecutor(threads) as ex:
        for i, r in enumerate(ex.map(get, jobs), 1):
            st[r] = st.get(r, 0) + 1
            if i % 200 == 0 or i == len(jobs):
                el = time.time() - t0
                print(json.dumps({"done": i, "of": len(jobs), **st, "elapsed_s": round(el),
                                  "eta_s": round(el / i * (len(jobs) - i))}), flush=True)
    return st


def decode(raw: bytes, day: dt.date):
    if not raw:
        return []
    b = lzma.decompress(raw)
    t0 = dt.datetime(day.year, day.month, day.day, tzinfo=UTC)
    out = []
    for sec, o, c, lo, hi, v in REC.iter_unpack(b):
        if v == 0 and hi == lo:          # filler bar (same rule as the H016b harness normalise)
            continue
        out.append((t0 + dt.timedelta(seconds=sec), o, hi, lo, c, v))
    return out


def px(i: int) -> str:
    return f"{i // 1000}.{i % 1000:03d}"


def build():
    rep = {}
    for name, sym in INSTRUMENTS.items():
        for side in SIDES:
            out = root() / f"{name}_1m_{side.lower()}.csv.gz"
            n = missing = empty = 0
            with gzip.open(out, "wt", newline="") as fh:
                fh.write("Datetime,Open,High,Low,Close,Volume\n")
                for d in days():
                    guard(sym, d)
                    p = raw_path(sym, side, d)
                    if not p.exists():
                        missing += 1; continue
                    recs = decode(p.read_bytes(), d)
                    if not recs:
                        empty += d.weekday() < 5; continue
                    for t, o, h, l, c, v in recs:
                        fh.write(f"{t.astimezone(NY).isoformat(sep=' ')},{px(o)},{px(h)},{px(l)},{px(c)},{v!r}\n"); n += 1
            rep[f"{name}_{side}"] = {"rows": n, "missing_day_files": missing, "empty_weekday_files": empty, "path": str(out)}
    (root() / "build_report.json").write_text(json.dumps(rep, indent=1))
    return rep


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "download":
        print(download(int(sys.argv[2]) if len(sys.argv) > 2 else 8))
    elif cmd == "build":
        print(json.dumps(build(), indent=1))
