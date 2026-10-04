"""H015b Dukascopy datafeed client (the ONLY feed for H015b, context bars included). HYPOTHETICAL paper research: no orders.

Source (DATA C1): https://datafeed.dukascopy.com/datafeed/{USATECHIDXUSD|USA500IDXUSD}/{YYYY}/{MM-1:02d}/{DD:02d}/{BID|ASK}_candles_min_1.bi5
(month is 0-indexed). One file per instrument, side and UTC day: LZMA-compressed 24-byte big-endian records `>5if` =
(seconds from 00:00 UTC, open, close, low, high as price*1000 integers, float volume). Bars are labelled by their OPEN time.

Normalisation (DATA C2/C4/C6, appendix A3/A6): drop exactly the vendor filler bars `(volume == 0) & (high == low)`, never
synthesise, interpolate or forward-fill a bar; convert UTC -> America/New_York with zoneinfo; write
`Datetime,Open,High,Low,Close,Volume` with the NY offset so `ftn.research.bars.load_series` reads it unchanged.

Storage (DATA C10, appendix A5): <DATA_ROOT>/H015b/raw/<inst>/<SIDE>/<YYYY-MM-DD>.bi5 (+ .csv, + .json meta with both sha256).
A day file is FINAL when it was pulled at or after 01:00 UTC on the following UTC day; FINAL files are never overwritten or
re-downloaded. A non-final copy may be replaced by a later pull (the pull log records why: completeness only)."""
from __future__ import annotations

import datetime as dt, hashlib, json, lzma, pathlib, struct, time, urllib.error, urllib.request
from zoneinfo import ZoneInfo

UTC = dt.timezone.utc
NY = ZoneInfo("America/New_York")
SYMBOL = {"US100": "USATECHIDXUSD", "US500": "USA500IDXUSD"}
SIDES = ("BID", "ASK")
URL = "https://datafeed.dukascopy.com/datafeed/{sym}/{y:04d}/{m0:02d}/{d:02d}/{side}_candles_min_1.bi5"
REC = struct.Struct(">5if")
FINAL_AFTER = dt.timedelta(days=1, hours=1)          # 01:00 UTC on the next UTC day
UA = {"User-Agent": "Mozilla/5.0"}


class FeedError(RuntimeError):
    """Network/throttle failure: the day stays provisional and is retried; never substituted by another feed."""


class SchemaError(RuntimeError):
    """The vendor file does not decode as 24-byte >5if records or prices are implausible -> feed_suspended."""


def url(inst: str, side: str, day: dt.date) -> str:
    return URL.format(sym=SYMBOL[inst], y=day.year, m0=day.month - 1, d=day.day, side=side)


def sha256(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def http_get(u: str, tries: int = 6, timeout: int = 60, _open=None) -> bytes | None:
    """bytes, or None on 404 (no file = gap, never filled). Retries 5xx / timeouts with backoff, then FeedError."""
    op = _open or urllib.request.urlopen
    last = None
    for k in range(tries):
        try:
            with op(urllib.request.Request(u, headers=UA), timeout=timeout) as r:
                return r.read()
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return None
            last = f"HTTP {e.code}"
        except Exception as e:  # timeout, reset, DNS
            last = f"{type(e).__name__}: {str(e)[:120]}"
        time.sleep(min(60, 2 ** k * 2))
    raise FeedError(f"{u}: {last}")


def decode(raw: bytes, day: dt.date) -> list[tuple]:
    """[(utc datetime, open, high, low, close, volume, (o,h,l,c ints))] for every record, filler included."""
    if not raw:
        return []
    try:
        b = lzma.decompress(raw)
    except lzma.LZMAError as e:
        raise SchemaError(f"not LZMA: {e}") from e
    if len(b) % REC.size:
        raise SchemaError(f"payload {len(b)} bytes is not a multiple of {REC.size}")
    t0 = dt.datetime(day.year, day.month, day.day, tzinfo=UTC)
    out = []
    prev = -1
    for sec, o, c, lo, hi, v in REC.iter_unpack(b):
        if sec <= prev:   # DATA ruling: duplicate / out-of-order timestamps in a raw download -> schema failure, never re-sorted
            raise SchemaError(f"duplicate or out-of-order raw timestamp sec={sec} after {prev}")
        prev = sec
        if not (0 <= sec < 86400) or sec % 60 or min(o, c, lo, hi) <= 0 or lo > min(o, c) or hi < max(o, c):
            raise SchemaError(f"bad record sec={sec} o={o} c={c} l={lo} h={hi}")
        out.append((t0 + dt.timedelta(seconds=sec), o, hi, lo, c, float(v)))
    return out


def px(i: int) -> str:
    """Exact decimal text of price*1000 integers (float(px(i)) == i / 1000)."""
    return f"{i // 1000}.{i % 1000:03d}"


def normalise(recs: list[tuple]) -> tuple[bytes, dict]:
    """Drop exactly (volume == 0) & (high == low); write NY-offset CSV. Returns (csv bytes, stats)."""
    lines = ["Datetime,Open,High,Low,Close,Volume"]
    dropped = kept = 0
    prev = None
    for t, o, h, l, c, v in recs:
        if v == 0 and h == l:
            dropped += 1
            continue
        if prev is not None and t <= prev:
            raise SchemaError(f"non-monotonic / duplicate timestamp {t}")
        prev = t
        ny = t.astimezone(NY)
        lines.append(f"{ny.isoformat(sep=' ')},{px(o)},{px(h)},{px(l)},{px(c)},{v!r}")
        kept += 1
    return ("\n".join(lines) + "\n").encode(), dict(rows_raw=len(recs), rows_kept=kept, filler_dropped=dropped)


class Store:
    """Immutable per-day raw store. meta json: url, pulled_at_utc, final, bi5_sha256, csv_sha256, rows, filler_dropped."""

    def __init__(self, root: pathlib.Path, now=None, get=None):
        self.root = pathlib.Path(root)
        self.now = now or (lambda: dt.datetime.now(UTC))
        self.get = get or http_get

    def paths(self, inst, side, day):
        d = self.root / "raw" / inst / side
        s = day.isoformat()
        return d / f"{s}.bi5", d / f"{s}.csv", d / f"{s}.json"

    def meta(self, inst, side, day) -> dict | None:
        p = self.paths(inst, side, day)[2]
        return json.loads(p.read_text()) if p.exists() else None

    def is_final_time(self, day: dt.date, at: dt.datetime) -> bool:
        return at >= dt.datetime(day.year, day.month, day.day, tzinfo=UTC) + FINAL_AFTER

    def ensure(self, inst: str, side: str, day: dt.date, reason: str = "missing") -> dict:
        """Return the day's meta, downloading only if no FINAL copy exists. Logs every pull to pulls.jsonl."""
        m = self.meta(inst, side, day)
        if m and m["final"]:
            return m
        now = self.now()
        if now < dt.datetime(day.year, day.month, day.day, tzinfo=UTC) + dt.timedelta(days=1):
            return dict(day=day.isoformat(), inst=inst, side=side, final=False, status="not_published_yet")
        u = url(inst, side, day)
        raw = self.get(u)                                   # FeedError propagates: day stays provisional
        present = raw is not None and len(raw) > 0
        recs = decode(raw, day) if present else []
        csvb, st = normalise(recs)
        final = self.is_final_time(day, now)
        bi5, csvp, metap = self.paths(inst, side, day)
        bi5.parent.mkdir(parents=True, exist_ok=True)
        if m and m.get("final"):
            raise RuntimeError("refusing to overwrite a FINAL day file")
        bi5.write_bytes(raw or b""); csvp.write_bytes(csvb)
        m = dict(day=day.isoformat(), inst=inst, side=side, source="dukascopy_datafeed", url=u,
                 pulled_at_utc=now.isoformat(timespec="seconds"), final=final, http_404=raw is None,
                 bi5_bytes=len(raw or b""), bi5_sha256=sha256(raw or b""), csv_sha256=sha256(csvb), **st)
        metap.write_text(json.dumps(m, indent=1, sort_keys=True) + "\n")
        with open(self.root / "pulls.jsonl", "a") as f:
            f.write(json.dumps(dict(m, reason=reason)) + "\n")
        return m

    def verify(self, inst, side, day) -> bool:
        """Stored bytes still hash to the recorded sha256 (immutability check)."""
        m = self.meta(inst, side, day)
        bi5, csvp, _ = self.paths(inst, side, day)
        return bool(m) and sha256(bi5.read_bytes()) == m["bi5_sha256"] and sha256(csvp.read_bytes()) == m["csv_sha256"]

    def csv_text(self, inst, side, day) -> str:
        return self.paths(inst, side, day)[1].read_text()
