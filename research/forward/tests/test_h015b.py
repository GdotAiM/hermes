"""H015b harness tests: bound percentile, cluster bootstrap, futility-once, kill, calendar, Dukascopy decode/normalise,
store immutability/finality, foil-with-N == ftn foil, burned-tape per-session reproduction (C11) and an end-to-end forward
`final` in a sandbox served from marketdata's NATIVE Dukascopy bi5 files (never HistData). No network, no orders."""
import csv, datetime as dt, json, lzma, pathlib, struct, sys
import pytest

FWD = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(FWD / "H015"))
import duka as D   # noqa: E402
import h015 as H   # noqa: E402

TAPE = pathlib.Path("/workspace/ict-blueprint/research/model-u-longrun/data")
MD_RAW = pathlib.Path("/workspace/marketdata/raw/dukascopy")
needs_tape = pytest.mark.skipif(not (TAPE / "US100_1m.csv.gz").exists(), reason="no burned tape")
needs_md = pytest.mark.skipif(not (MD_RAW / "USATECHIDXUSD/2026").exists(), reason="no marketdata native Dukascopy raw")


def trades_csv(inst):
    return list(csv.DictReader(open(H.REPO / f"research/evidence/quant/FTN_M9_TRADES_{inst}_base_2026-10-04_d22_stop_beyond_raid.csv")))


# ------------------------------------------------------------------ statistics
def test_binding_bound_is_5th_percentile_not_boot_ci_default():
    assert H.LB_INDEX == 500 and H.UB975_INDEX == 9749
    S = H.ftn()["stats"]
    xs = [((i * 37) % 101 - 50) / 25 for i in range(300)]
    lo975, _ = S.boot_ci(xs, alpha=0.05)          # = vals[250]: one-sided 97.5%, NOT binding
    lo95, _ = S.boot_ci(xs, alpha=0.10)           # = vals[500]: trade-level one-sided 95% co-report
    assert lo975 < lo95
    # with singleton clusters the cluster bootstrap draws exactly like boot_ci (same rng sequence)
    tr = [dict(date=f"d{i:04d}", session="london", instrument="US100", R=x)
          for i, x in enumerate(xs)]
    vals = H.cluster_boot(tr)
    assert vals[H.LB_INDEX] == pytest.approx(lo95, abs=1e-12) and vals[250] == pytest.approx(lo975, abs=1e-12)
    assert H.binding_bound(tr)["lb_one_sided_95"] == pytest.approx(lo95, abs=1e-12)


def test_cluster_keeps_both_instruments_together():
    tr = []
    for i in range(50):
        r = 1.0 if i % 2 else -1.0
        for inst in H.INSTS:
            tr.append(dict(date=f"2027-02-{i:02d}", session="ny_am", instrument=inst, R=r))
    v = H.cluster_boot(tr, n=2000)
    # every resample mean is a multiple of 1/50 (pairs move together), never an odd multiple of 1/100
    assert all(abs(x * 50 - round(x * 50)) < 1e-9 for x in v)
    assert H.binding_bound(tr)["n_clusters"] == 50


def test_futility_fires_once_on_first_200_only():
    bad = [dict(date=f"2027-03-{i:04d}", session="london", instrument="US100", R=-0.5) for i in range(200)]
    good = [dict(date=f"2027-09-{i:04d}", session="london", instrument="US100", R=3.0) for i in range(500)]
    assert H.futility(bad[:199]) is None
    f = H.futility(bad + good)
    assert f["n"] == 200 and f["fails"]
    assert H.futility(good[:200])["fails"] is False


def test_kill_at_minus_45():
    tr = [dict(date=f"2027-01-{i:03d}", session="london", instrument="US100", R=-1.0) for i in range(60)]
    k = H.kill_walk(tr)
    assert k["kill"] and k["kill_at_trade"] == 45
    assert not H.kill_walk(tr[:44])["kill"]


def test_canonical_order():
    tr = [dict(date="2027-01-05", session="ny_am", instrument="US100", R=0), dict(date="2027-01-05", session="london", instrument="US500", R=0),
          dict(date="2027-01-05", session="london", instrument="US100", R=0), dict(date="2027-01-04", session="ny_am", instrument="US500", R=0)]
    assert [(t["date"], t["session"], t["instrument"]) for t in H.canonical(tr)] == [
        ("2027-01-04", "ny_am", "US500"), ("2027-01-05", "london", "US100"), ("2027-01-05", "london", "US500"), ("2027-01-05", "ny_am", "US100")]


# ------------------------------------------------------------------ calendar
def test_calendar():
    assert H.calendar_status(dt.date(2026, 10, 5)) == "ok"
    assert H.calendar_status(dt.date(2026, 10, 10)) == "weekend"
    assert H.calendar_status(dt.date(2026, 11, 26)) == "holiday"
    assert H.calendar_status(dt.date(2026, 11, 27)) == "holiday"
    assert H.calendar_status(dt.date(2028, 7, 3)) == "holiday" and H.calendar_status(dt.date(2028, 7, 4)) == "holiday"
    assert H.calendar_status(dt.date(2028, 7, 5)) == "ok"
    assert H.calendar_status(dt.date(2029, 1, 2)) == "calendar_not_covered"
    assert H.dst_mismatch_week(dt.date(2026, 10, 27)) and not H.dst_mismatch_week(dt.date(2026, 10, 20))
    assert not H.dst_mismatch_week(dt.date(2026, 11, 3))


# ------------------------------------------------------------------ Dukascopy decode / store
def bi5(recs):
    return lzma.compress(b"".join(struct.pack(">5if", *r) for r in recs), format=lzma.FORMAT_ALONE)


def test_decode_normalise_filler_and_offsets():
    day = dt.date(2026, 11, 2)   # first day after the US DST change: EST
    raw = bi5([(0, 100000, 100500, 99000, 101000, 1.5), (60, 100500, 100500, 100500, 100500, 0.0), (120, 1, 2, 1, 2, 0.0)])
    recs = D.decode(raw, day)
    b, st = D.normalise(recs)
    lines = b.decode().splitlines()
    assert st == dict(rows_raw=3, rows_kept=2, filler_dropped=1)          # only (vol==0)&(high==low) dropped
    assert lines[1].startswith("2026-11-01 19:00:00-05:00,100.000,101.000,99.000,100.500")
    assert lines[2].startswith("2026-11-01 19:02:00-05:00,0.001,0.002,0.001,0.002")   # vol 0 but high != low: kept


def test_decode_rejects_duplicates_out_of_order_and_bad_schema():
    day = dt.date(2026, 10, 5)
    with pytest.raises(D.SchemaError):
        D.decode(bi5([(60, 1, 1, 1, 1, 1.0), (60, 1, 1, 1, 1, 1.0)]), day)
    with pytest.raises(D.SchemaError):
        D.decode(bi5([(120, 1, 1, 1, 1, 1.0), (60, 1, 1, 1, 1, 1.0)]), day)
    with pytest.raises(D.SchemaError):
        D.decode(lzma.compress(b"x" * 25, format=lzma.FORMAT_ALONE), day)
    assert D.url("US100", "BID", dt.date(2026, 10, 5)).endswith("/USATECHIDXUSD/2026/09/05/BID_candles_min_1.bi5")


def test_store_finality_by_completeness_v2(tmp_path):
    """DATA cert B1: FINAL = timely AND complete by content; cut-off files are re-pulled; old bytes kept in superseded/."""
    day = dt.date(2026, 10, 5)                                    # Monday, EDT: 16:14 NY = 20:14 UTC = sec 72840
    full = bi5([(0, 100000, 100500, 99000, 101000, 1.5), (72840, 100000, 100500, 99000, 101000, 1.5)])
    cut = bi5([(0, 100000, 100500, 99000, 101000, 1.5), (52140, 100000, 100500, 99000, 101000, 1.5)])   # 14:29 NY
    srv = {"b": None}; calls = []
    clock = [dt.datetime(2026, 10, 6, 1, 5, tzinfo=D.UTC)]
    s = D.Store(tmp_path, now=lambda: clock[0], get=lambda u: calls.append(u) or srv["b"])
    m = s.ensure("US100", "BID", day)                              # 404 at the pull
    assert m["final"] is False and m["completeness"] == "empty_or_404"
    srv["b"] = cut; clock[0] += dt.timedelta(days=1)
    m = s.ensure("US100", "BID", day)                              # cut-off file: still not final, re-pulled
    assert m["final"] is False and m["completeness"].startswith("cut_off") and len(calls) == 2
    srv["b"] = full; clock[0] += dt.timedelta(days=1)
    m = s.ensure("US100", "BID", day)
    assert m["final"] is True and m["complete"] and not m["frozen_incomplete"] and len(calls) == 3
    assert list((tmp_path / "raw/US100/BID/superseded").glob("*.bi5"))            # earlier bytes kept, nothing deleted
    s.ensure("US100", "BID", day)
    assert len(calls) == 3 and s.verify("US100", "BID", day)                      # FINAL: never re-downloaded
    s.paths("US100", "BID", day)[1].write_text("tampered")
    assert not s.verify("US100", "BID", day)
    # a file that stays cut off is frozen (disclosed) after 5 weekdays
    d2 = dt.date(2026, 10, 6); srv["b"] = cut
    clock[0] = dt.datetime(2026, 10, 7, 1, 5, tzinfo=D.UTC)
    cutd2 = bi5([(0, 100000, 100500, 99000, 101000, 1.5), (52140, 100000, 100500, 99000, 101000, 1.5)])
    s.get = lambda u: cutd2
    assert s.ensure("US100", "BID", d2)["final"] is False
    clock[0] = dt.datetime(2026, 10, 14, 1, 5, tzinfo=D.UTC)
    m = s.ensure("US100", "BID", d2)
    assert m["final"] is True and m["frozen_incomplete"] is True
    assert s.ensure("US100", "BID", dt.date(2026, 10, 15))["status"] == "not_published_yet"
    # v1 metas (no finality_rule) are re-checked
    mp = s.paths("US100", "BID", day)[2]; mm = json.loads(mp.read_text()); mm.pop("finality_rule"); mp.write_text(json.dumps(mm))
    s.get = lambda u: full
    assert s.ensure("US100", "BID", day)["finality_rule"] == D.FINALITY_RULE


def test_complete_uses_full_datetime_and_weekday_rules():
    mon = dt.date(2026, 10, 5)
    rec = lambda sec: (dt.datetime(2026, 10, 5, tzinfo=D.UTC) + dt.timedelta(seconds=sec), 1, 2, 1, 2, 1.0)
    assert D.complete([rec(72840)], mon)[0] and not D.complete([rec(72780)], mon)[0]
    assert D.complete([], dt.date(2026, 10, 10))[0]                     # Saturday: closed
    sun = dt.date(2026, 10, 4)
    r2 = lambda sec: (dt.datetime(2026, 10, 4, tzinfo=D.UTC) + dt.timedelta(seconds=sec), 1, 2, 1, 2, 1.0)
    assert D.complete([r2(86340)], sun)[0] and not D.complete([r2(79200)], sun)[0]


def test_http_404_is_gap_and_errors_raise(monkeypatch):
    import urllib.error
    monkeypatch.setattr(D.time, "sleep", lambda s: None)
    def op404(req, timeout): raise urllib.error.HTTPError(req.full_url, 404, "nf", {}, None)
    def op503(req, timeout): raise urllib.error.HTTPError(req.full_url, 503, "busy", {}, None)
    assert D.http_get("http://x", _open=op404) is None
    with pytest.raises(D.FeedError):
        D.http_get("http://x", tries=2, _open=op503)


def test_pins_verified_against_tag():
    assert H.verify_pins() == {}
    assert len(H.pins()) == 96


# ------------------------------------------------------------------ burned-tape reproduction (C11) + foil
@needs_tape
def test_repro_burned_per_session_every_7th_day():
    r = H.repro_burned(str(TAPE), every=7)
    for inst in H.INSTS:
        assert r[inst]["n_mismatch"] == 0, r[inst]["mismatches"]
        assert r[inst]["n_harness"] == r[inst]["n_csv"] > 0


@needs_tape
def test_foil_with_n_equals_ftn_foil():
    F = H.ftn()
    s = F["bars"].load_series(TAPE / "US100_1m.csv.gz", "US100")
    tr = [dict(date=t["date"], session=t["session"], risk_pts=float(t["risk_pts"])) for t in trades_csv("US100")[:12]]
    ref = F["score"].foil(F["dc"].History(s, F["bars"].trading_days(s)), tr, 0.8, n=40)
    got = H.foil_with_n(s, tr, 0.8, n=40)
    assert [g[0] for g in got] == ref and all(0 < g[1] <= 12 for g in got)


# ------------------------------------------------------------------ end-to-end forward path (sandbox, native Dukascopy bi5)
def md_get(u, drop=(), truncate=None, strip=None):
    """Serve marketdata's raw NATIVE Dukascopy bi5 files for a datafeed URL (fake network). DATA cert scenarios:
    drop = {(side, day)} -> 404; truncate = {(side, day): n_records}; strip = {(side, day): (sec_from, sec_to)}."""
    p = u.split("/datafeed/")[1].split("/")
    sym, y, m0, d, f = p[0], int(p[1]), int(p[2]), int(p[3]), p[4]
    side = f.split("_")[0]; day = dt.date(y, m0 + 1, d)
    if (side, day) in set(drop):
        return None
    q = MD_RAW / sym / str(y) / f"{y:04d}{m0 + 1:02d}{d:02d}_{side}.bi5"
    if not q.exists():
        return None
    raw = q.read_bytes()
    if truncate and (side, day) in truncate:
        x = lzma.decompress(raw)[:24 * truncate[(side, day)]]
        raw = lzma.compress(x, format=lzma.FORMAT_ALONE)
    if strip and (side, day) in strip:
        a, b = strip[(side, day)]
        x = lzma.decompress(raw)
        recs = [x[i:i + 24] for i in range(0, len(x), 24)]
        recs = [r for r in recs if not (a <= struct.unpack(">5if", r)[0] < b)]
        raw = lzma.compress(b"".join(recs), format=lzma.FORMAT_ALONE)
    return raw


def getter(**kw):
    return lambda u: md_get(u, **kw)


@needs_md
@needs_tape
def test_forward_final_on_native_dukascopy_reproduces_burned_trade(tmp_path, monkeypatch):
    # a pre-2026-05-29 trade day (reused tape == native Dukascopy there, DATA F2)
    want = [t for t in trades_csv("US100") if t["date"] == "2026-03-25"]
    assert want
    d = dt.date(2026, 3, 25)
    monkeypatch.setattr(H, "FIRST_DATE", d)
    monkeypatch.setattr(H, "pending_dates", lambda led, at: [d])
    at = dt.datetime(2026, 10, 5, 1, 30, tzinfo=D.UTC)
    reg = dict(registered=True, registration_commit="x", registration_time_utc="2026-10-04T08:00:00+00:00", harness_matches_registered=True)
    monkeypatch.setattr(H, "registration_status", lambda fetch=False: reg)
    rows = H.cmd_final(root=tmp_path, at=at, get=md_get, fetch_remote=False)
    us100 = {r["session"]: r for r in rows if r["instrument"] == "US100"}
    for t in want:
        r = us100[t["session"]]
        assert r["status"] in ("trade", "short_session")
        assert (r["entry_time"], str(r["entry"]), str(r["stop"])) == (t["entry_time"], t["entry"], t["stop"])
        assert r["counted"] is False and "session_started_before_prereg" in r["not_counted_reasons"]
    outs = {(o["date"], o["instrument"], o["session"]): o for o in H.Ledger(tmp_path).outcomes()}
    for t in want:
        assert outs[(t["date"], "US100", t["session"])]["R"] == t["R"]
    # R is sealed: not in log.csv
    assert "R" not in open(tmp_path / "log.csv").readline().split(",")
    rep = H.cmd_report(root=tmp_path)
    assert rep["R"].startswith("SEALED") and "Dukascopy" in rep["feed_disclosure"]
    v = H.cmd_verify(root=tmp_path)
    assert v["ok"] and v["rows_checked"] >= 2, v
    # every row carries hashes; the second run is a no-op (terminal rows are never re-scored)
    assert all(r["session_raw_sha256"] and r["context_manifest_sha256"] for r in rows)
    monkeypatch.undo()
    monkeypatch.setattr(H, "registration_status", lambda fetch=False: reg)
    led = H.Ledger(tmp_path)
    lat = led.latest()
    assert all(lat[(d.isoformat(), i, s)]["status"] in H.TERMINAL for i in H.INSTS for s in H.SESSIONS)


def test_provisional_then_feed_gap(tmp_path, monkeypatch):
    d = dt.date(2026, 10, 5)
    reg = dict(registered=True, registration_commit="x", registration_time_utc="2026-10-04T08:00:00+00:00", harness_matches_registered=True)
    def get(u):
        raise D.FeedError("503")
    st = D.Store(tmp_path, now=lambda: dt.datetime(2026, 10, 6, 2, tzinfo=D.UTC), get=get)
    rows = H.session_rows_for(st, "US100", d, reg, True, "r1", dt.datetime(2026, 10, 6, 2, tzinfo=D.UTC))
    assert {r[0]["status"] for r in rows} == {"provisional"} and all(o is None for _, o in rows)
    rows = H.session_rows_for(st, "US100", d, reg, True, "r2", dt.datetime(2026, 10, 14, 2, tzinfo=D.UTC))
    assert {r[0]["status"] for r in rows} == {"feed_gap"}


def test_pending_dates_respect_01utc(tmp_path):
    led = H.Ledger(tmp_path)
    assert H.pending_dates(led, dt.datetime(2026, 10, 6, 0, 59, tzinfo=D.UTC)) == []
    assert H.pending_dates(led, dt.datetime(2026, 10, 6, 1, 0, tzinfo=D.UTC)) == [dt.date(2026, 10, 5)]


@needs_md
@needs_tape
def test_report_after_clearance_runs_all_co_reports(tmp_path, monkeypatch):
    d = dt.date(2026, 3, 25)
    monkeypatch.setattr(H, "pending_dates", lambda led, at: [d])
    reg = dict(registered=True, registration_commit="x", registration_time_utc="2026-10-04T08:00:00+00:00", harness_matches_registered=True)
    monkeypatch.setattr(H, "registration_status", lambda fetch=False: reg)
    H.cmd_final(root=tmp_path, at=dt.datetime(2026, 10, 5, 1, 30, tzinfo=D.UTC), get=md_get, fetch_remote=False)
    # pretend the burned rows were countable, only to exercise the report path (sandbox)
    rows = list(csv.DictReader(open(tmp_path / "log.csv")))
    for r in rows:
        if r["status"] == "trade":
            r["counted"] = "True"
    with open(tmp_path / "log.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=H.LOG_COLS); w.writeheader(); w.writerows(rows)
    for fn in ("DATA_CERTIFIED.json", "CASSANDRA_CLEARED.json"):
        (tmp_path / fn).write_text(json.dumps({"harness_sha256": H.harness_digest()}))
    rep = H.cmd_report(root=tmp_path, foil_n=20)
    n = rep["n_counted"]
    assert n >= 2 and rep["pooled"]["n"] == n
    assert rep["verdict"].startswith("OPEN (N=") and "no verdict" in rep["verdict"]
    assert rep["foil"]["n_per_replicate"]["max"] <= n
    assert rep["ask_resim"]["n"] == n and rep["data_monitor_monthly"]
    assert all("crossed_bars" in v for v in rep["data_monitor_monthly"].values())
    assert rep["gap_flag_co_report"]["flagged_n"] >= 0 and "short_session_dropped_trades" in rep
    assert rep["kill"]["min_cum"] is not None
    assert "lb_one_sided_95" in rep["pooled"]["binding_cluster_bound"]


def test_feed_suspension_after_more_than_10_gap_days(tmp_path):
    lat = {}
    days = H.expected_trading_days(dt.date(2026, 10, 5), dt.date(2026, 11, 6))
    for i, d in enumerate(days):
        st = "feed_gap" if 2 <= i <= 12 else "no_trade"
        for inst in H.INSTS:
            for s in H.SESSIONS:
                lat[(d.isoformat(), inst, s)] = dict(status=st)
    sp = H.suspension(lat, tmp_path)
    assert sp["suspended"] and sp["since"] == days[2].isoformat()
    lat2 = {k: (dict(status="no_trade") if k[0] == days[12].isoformat() else v) for k, v in lat.items()}
    assert not H.suspension(lat2, tmp_path)["suspended"]     # exactly 10 gap days: not suspended
    (tmp_path / "FEED_RESUMED.json").write_text(json.dumps({"resume_from": days[15].isoformat()}))
    assert not H.suspension(lat, tmp_path)["suspended"]



# ------------------------------------------------------------------ DATA cert scenarios (B1-B5), native Dukascopy bi5
REG = dict(registered=True, registration_commit="x", registration_time_utc="2026-10-04T07:37:41+00:00", harness_matches_registered=True)


def run_rows(root, d, at, get, inst="US100"):
    st = D.Store(root, now=lambda: at, get=get, short_ok=lambda day: H.calendar_status(day) == "holiday")
    return {r["session"]: (r, o) for r, o in H.session_rows_for(st, inst, d, REG, True, "t", at)}


def utc(y, m, d, h=2, mi=0):
    return dt.datetime(y, m, d, h, mi, tzinfo=D.UTC)


@needs_md
def test_S1_memorial_day_in_context_is_not_context_gap(tmp_path):
    rows = run_rows(tmp_path, dt.date(2026, 6, 1), utc(2026, 6, 2), getter())
    assert {r["status"] for r, _ in rows.values()} <= {"trade", "no_trade"}
    assert all(r["context_missing_days"] is None for r, _ in rows.values())


@needs_md
def test_B4_labor_day_context_for_first_sessions(tmp_path):
    assert dt.date(2026, 9, 7) not in H.expected_trading_days(dt.date(2026, 9, 1), dt.date(2026, 9, 30))
    assert H.calendar_status(dt.date(2026, 9, 7)) == "holiday"
    rows = run_rows(tmp_path, dt.date(2026, 9, 15), utc(2026, 9, 16), getter())   # context contains Labor Day 2026-09-07
    assert {r["status"] for r, _ in rows.values()} <= {"trade", "no_trade"}
    assert all(r["context_missing_days"] is None for r, _ in rows.values())


@needs_md
def test_S2_session_file_404_then_recovers(tmp_path):
    d = dt.date(2026, 8, 20)
    clean = run_rows(tmp_path / "clean", d, utc(2026, 8, 21), getter())
    rows = run_rows(tmp_path / "s2", d, utc(2026, 8, 21, 1, 5), getter(drop={("BID", d)}))
    assert {r["status"] for r, _ in rows.values()} == {"provisional"}                  # B2: was not_trading_day in v1
    assert all(o is None for _, o in rows.values())
    rows = run_rows(tmp_path / "s2", d, utc(2026, 8, 22), getter())                    # B1: re-pulled, now complete
    for s in H.SESSIONS:
        assert rows[s][0]["status"] == clean[s][0]["status"] in ("trade", "no_trade")
        assert rows[s][0]["entry_time"] == clean[s][0]["entry_time"]
        assert (rows[s][1] or {}).get("R") == (clean[s][1] or {}).get("R")
    nxt = run_rows(tmp_path / "s2", dt.date(2026, 8, 21), utc(2026, 8, 22, 3), getter())   # B3: next session not poisoned
    assert {r["status"] for r, _ in nxt.values()} <= {"trade", "no_trade"}


@needs_md
def test_S3_truncated_then_full_and_persistent_truncation_feed_gap(tmp_path):
    d = dt.date(2026, 8, 20)
    clean = run_rows(tmp_path / "clean", d, utc(2026, 8, 21), getter())
    tr = getter(truncate={("BID", d): 1110})
    assert {r["status"] for r, _ in run_rows(tmp_path / "s3", d, utc(2026, 8, 21, 1, 5), tr).values()} == {"provisional"}
    rows = run_rows(tmp_path / "s3", d, utc(2026, 8, 24), getter())
    assert {s: rows[s][0]["status"] for s in H.SESSIONS} == {s: clean[s][0]["status"] for s in H.SESSIONS}
    # persistent cut-off: provisional while retrying, feed_gap once the 5-trading-day window is over
    assert {r["status"] for r, _ in run_rows(tmp_path / "s3b", d, utc(2026, 8, 24), tr).values()} == {"provisional"}
    rows = run_rows(tmp_path / "s3b", d, utc(2026, 8, 31), tr)
    assert {r["status"] for r, _ in rows.values()} == {"feed_gap"}


@needs_md
def test_B3_frozen_bad_context_day_is_skipped_with_disclosure(tmp_path):
    bad = dt.date(2026, 8, 20)
    tr = getter(truncate={("BID", bad): 900})            # cut at ~11:00 NY: < 300 RTH bars, so not a trading day
    run_rows(tmp_path, bad, utc(2026, 8, 31), tr)                       # frozen incomplete after the retry window
    rows = run_rows(tmp_path, dt.date(2026, 9, 1), utc(2026, 9, 2), tr)
    for r, _ in rows.values():
        assert r["status"] in ("trade", "no_trade")
        assert "2026-08-20" in (r["context_frozen_incomplete"] or "") and "2026-08-20" in (r["context_missing_days"] or "")


@needs_md
@needs_tape
def test_B5_gap_trades_stay_counted_rows_with_flag(tmp_path):
    """DATA ruling: 2026-03-12 US100 (61-min gap) london target + ny_am target were dropped by v1; v2 keeps them, flagged."""
    want = {t["session"]: t for t in trades_csv("US100") if t["date"] == "2026-03-12"}
    assert set(want) == {"london", "ny_am"}
    rows = run_rows(tmp_path, dt.date(2026, 3, 12), utc(2026, 10, 5), getter())
    for s, t in want.items():
        r, o = rows[s]
        assert r["status"] == "trade" and r["exit_bar_1545_ok"] is True
        assert o["R"] == t["R"] and o["exit"] == t["exit"]
    # the 61-min gap DATA found is in the burned (HistData-merged) tape, not in native Dukascopy: flag it on the tape
    F = H.ftn(); tape = F["bars"].load_series(TAPE / "US100_1m.csv.gz", "US100")
    d = dt.date(2026, 3, 12)
    assert H.exit_bars_ok(tape, d)                                        # binding rule: kept (v1 dropped both)
    assert all(H.gap_flag(tape, dt.datetime.fromisoformat(t["entry_time"])) for t in want.values())
    assert not any(rows[s][0]["gap_flag"] for s in want)                   # native file has no gap


@needs_md
def test_B5_exit_bar_rule_applies_to_every_session(tmp_path):
    d = dt.date(2026, 8, 20)                             # EDT: 15:45-16:00 NY = 19:45-20:00 UTC
    rows = run_rows(tmp_path, d, utc(2026, 8, 21), getter(strip={("BID", d): (71100, 72000)}))
    assert {r["status"] for r, _ in rows.values()} == {"short_session"}
    assert all("no_bar_1545_1600" in r["not_counted_reasons"] and r["exit_bar_1545_ok"] is False for r, _ in rows.values())


def test_futility_set_frozen_once_and_reshuffle_reported(tmp_path):
    tr = [dict(date=f"2027-03-{i:04d}", session="london", instrument="US100", R=-0.5) for i in range(1, 251)]
    f = H.futility_frozen(tr, tmp_path)
    keys = json.loads((tmp_path / "FUTILITY_SET.json").read_text())["keys"]
    assert len(keys) == 200 and f["fails"] and f["reshuffle"] == []
    early = [dict(date="2027-01-01", session="london", instrument="US100", R=5.0)]   # a later backfill of an earlier date
    f2 = H.futility_frozen(early + tr, tmp_path)
    assert json.loads((tmp_path / "FUTILITY_SET.json").read_text())["keys"] == keys          # never overwritten
    assert f2["fails"] == f["fails"] and f2["ub_one_sided_975"] == f["ub_one_sided_975"]
    assert "2027-01-01|US100|london" in f2["reshuffle"]


def test_kill_walk_min_cum():
    tr = [dict(date=f"2027-01-{i:03d}", session="london", instrument="US100", R=r) for i, r in enumerate([-1, -2, 1], 1)]
    assert H.kill_walk(tr)["min_cum"] == -3
