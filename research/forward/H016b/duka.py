"""H016b Dukascopy datafeed client (the ONLY feed for H016b, context bars included). HYPOTHETICAL paper research: no orders.

Copied byte-for-byte in logic from the DATA-certified H015b v2 client (tag harness-H015b-v2 -> 5ea3e89,
research/forward/H015/duka.py; DATA_CERT_H015B_HARNESS_V2 C1-C13 incl. B1 finality); only this docstring differs.
For H016b BID **and** ASK day files are both BINDING (prereg data_source.feed): the harness requires both sides FINAL and
complete for a session's UTC days d-1 and d, and BID FINAL for the context; no fallback, never a synthetic ASK.

Source (DATA C1): https://datafeed.dukascopy.com/datafeed/{USATECHIDXUSD|USA500IDXUSD}/{YYYY}/{MM-1:02d}/{DD:02d}/{BID|ASK}_candles_min_1.bi5
(month is 0-indexed). One file per instrument, side and UTC day: LZMA-compressed 24-byte big-endian records `>5if` =
(seconds from 00:00 UTC, open, close, low, high as price*1000 integers, float volume). Bars are labelled by their OPEN time.

Normalisation (DATA C2/C4/C6): drop exactly the vendor filler bars `(volume == 0) & (high == low)`, never synthesise,
interpolate or forward-fill a bar; convert UTC -> America/New_York with zoneinfo; write `Datetime,Open,High,Low,Close,Volume`
with the NY offset so `ftn.research.bars.load_series` reads it unchanged.

Storage: <DATA_ROOT>/H016b/raw/<inst>/<SIDE>/<YYYY-MM-DD>.bi5 (+ .csv, + .json meta with both sha256).
Finality (DATA cert B1): a day file is FINAL only when it was pulled at or after 01:00 UTC on the following UTC day AND it
is COMPLETE by content (`complete()` below). A 404 / empty / cut-off file stays non-final and is re-pulled on every run
(reason "incomplete") for up to RETRY_DAYS weekdays after its date; after that it is frozen FINAL with
`frozen_incomplete: true` (disclosed, never silently used as complete). FINAL files are never overwritten or re-downloaded.
A non-final copy that is replaced keeps its old bytes under raw/.../superseded/ (nothing is deleted)."""
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
FINALITY_RULE = "v2_completeness"
RETRY_DAYS = 5                                        # weekdays after the file's date before an incomplete file is frozen
WEEKDAY_LAST_BAR = dt.time(16, 14)                    # NY halt: a Mon-Fri UTC file must reach 16:14 NY on that date
SUNDAY_LAST_UTC = dt.time(23, 50)                     # a Sunday UTC file (CFD reopen 18:00 NY) must reach 23:50 UTC
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


def complete(recs: list[tuple], day: dt.date) -> tuple[bool, str]:
    """Content completeness of one UTC day file (filler bars excluded).
    Mon-Fri: the last real bar is at or after 16:14 NY on that same NY date (full datetime, DATA cert B2).
    Sunday: the last real bar is at or after 23:50 UTC (the session reopens 18:00 NY). Saturday: always complete (closed)."""
    real = [r for r in recs if not (r[5] == 0 and r[2] == r[3])]
    if day.weekday() == 5:
        return True, "saturday"
    if not real:
        return False, "empty_or_404"
    last = real[-1][0]
    if day.weekday() == 6:
        ok = last.time() >= SUNDAY_LAST_UTC
        return ok, "ok" if ok else f"cut_off_last_bar_utc_{last:%H:%M}"
    want = dt.datetime.combine(day, WEEKDAY_LAST_BAR, tzinfo=NY)
    ok = last >= want
    return ok, "ok" if ok else f"cut_off_last_bar_ny_{last.astimezone(NY):%Y-%m-%d %H:%M}"


def weekdays_after(day: dt.date, upto: dt.date) -> int:
    n, d = 0, day + dt.timedelta(days=1)
    while d <= upto:
        n += d.weekday() < 5
        d += dt.timedelta(days=1)
    return n


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

    def __init__(self, root: pathlib.Path, now=None, get=None, short_ok=None):
        """short_ok(day) -> True for listed NYSE holidays / early closes, whose short CFD file is expected (no retries)."""
        self.short_ok = short_ok or (lambda day: False)
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
        """Return the day's meta, downloading unless a FINAL (v2) copy exists. Logs every pull to pulls.jsonl."""
        m = self.meta(inst, side, day)
        if m and m.get("final") and m.get("finality_rule") == FINALITY_RULE:
            return m
        now = self.now()
        if now < dt.datetime(day.year, day.month, day.day, tzinfo=UTC) + dt.timedelta(days=1):
            return dict(day=day.isoformat(), inst=inst, side=side, final=False, status="not_published_yet")
        if m:
            reason = "incomplete_repull" if m.get("finality_rule") == FINALITY_RULE else "v1_meta_recheck"
        u = url(inst, side, day)
        raw = self.get(u)                                   # FeedError propagates: day stays provisional
        present = raw is not None and len(raw) > 0
        recs = decode(raw, day) if present else []
        csvb, st = normalise(recs)
        is_complete, why = complete(recs, day)
        if not is_complete and recs and self.short_ok(day):
            is_complete, why = True, "listed_holiday_or_early_close"
        age = weekdays_after(day, (now - dt.timedelta(hours=1)).date() - dt.timedelta(days=1))
        timely = self.is_final_time(day, now)
        final = timely and (is_complete or age >= RETRY_DAYS)
        bi5, csvp, metap = self.paths(inst, side, day)
        bi5.parent.mkdir(parents=True, exist_ok=True)
        if bi5.exists() and bi5.read_bytes() != (raw or b""):
            sup = bi5.parent / "superseded"; sup.mkdir(exist_ok=True)
            tag = now.strftime("%Y%m%dT%H%M%SZ")
            for p in (bi5, csvp, metap):
                if p.exists():
                    p.rename(sup / f"{p.stem}__{tag}{p.suffix}")
        bi5.write_bytes(raw or b""); csvp.write_bytes(csvb)
        m = dict(day=day.isoformat(), inst=inst, side=side, source="dukascopy_datafeed", url=u,
                 pulled_at_utc=now.isoformat(timespec="seconds"), final=final, finality_rule=FINALITY_RULE,
                 complete=is_complete, completeness=why, frozen_incomplete=bool(final and not is_complete),
                 http_404=raw is None, bi5_bytes=len(raw or b""), bi5_sha256=sha256(raw or b""), csv_sha256=sha256(csvb), **st)
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
