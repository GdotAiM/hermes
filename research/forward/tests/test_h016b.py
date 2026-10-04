"""H016b harness tests (paper research; no network, no orders). Data used: synthetic bi5 records, the BURNED canonical
Dukascopy BID/ASK export (2025-08-24 18:00 -> 2026-09-25 17:00 NY) and marketdata's native Dukascopy raw bi5 files for
burned-window days only: the fake datafeed below REFUSES any day outside 2025-08-24 .. 2026-09-25 (never forward data,
never DATA's certified-untouched ranges)."""
import csv, datetime as dt, importlib.util, json, lzma, pathlib, struct
import pytest

FWD = pathlib.Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location("h016b_harness", FWD / "H016b" / "h016b.py")
H = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(H)
D = H.duka

TAPE = pathlib.Path(H.BURNED_TAPE)
MD_RAW = pathlib.Path("/workspace/marketdata/raw/dukascopy")
BURNED = (dt.date(2025, 8, 24), dt.date(2026, 9, 25))
needs_tape = pytest.mark.skipif(not (TAPE / "US100_1m_ask.csv.gz").exists(), reason="no burned BID/ASK export")
needs_md = pytest.mark.skipif(not (MD_RAW / "USATECHIDXUSD/2026").exists(), reason="no marketdata native Dukascopy raw")


def trades_csv(inst, kind="base"):
    return list(csv.DictReader(open(H.REPO / f"research/evidence/quant/FTN_M9_TRADES_{inst}_{kind}_2026-10-04_h016_fixed_rev_burned.csv")))


# ------------------------------------------------------------------ constants / pins
def test_binding_constants_match_prereg():
    p = H.prereg()
    assert H.N_DECISION == p["binding_N"]["decision"] == 747
    assert "<= -40R" in p["binding_kill"]["rule"] and H.KILL_R == -40.0
    assert H.FUTILITY_AT == 200 and H.FUTILITY_BAR == 0.10 and "v[9749]" in p["binding_futility"]["rule"]
    assert H.LB_INDEX == 500 and H.UB975_INDEX == 9749 and H.SEED == 20261004 and H.N_BOOT == 10_000
    assert H.FIRST_DATE == dt.date(2026, 10, 5)
    assert H.HOLM_3 == pytest.approx((0.016667, 0.025, 0.05), abs=1e-6) and H.FAMILY == tuple(p["family_rule"]["active_family"])
    assert H.TAG == "prereg-H016b" and H.TAG_COMMIT.startswith("74b13d3")
    assert p["data_source"]["fallback_feeds_allowed"] is False


def test_pins_verified_against_tag():
    assert H.verify_pins() == {}
    c = H.prereg()["code"]
    assert sum(len(c[b]) for b in ("kernel_and_dtr_sha256", "risk_sha256", "scoring_sha256", "registration_inputs_sha256")) == 117
    assert len(H.pins()) == 111       # unique paths (a few files sit in two blocks)
    assert any(k.startswith("ftn/src/ftn/engine/") for k in H.pins())


def test_pin_mismatch_refuses(monkeypatch, tmp_path):
    real = H.pins()
    rel = "ftn/src/ftn/os/instruments.py"
    monkeypatch.setattr(H, "pins", lambda: {**real, rel: "0" * 64})
    assert H.verify_pins() == {rel: "sha256_differs_from_prereg_pin"}
    with pytest.raises(SystemExit, match="harness_hash_mismatch"):
        H.cmd_final(root=tmp_path, at=dt.datetime(2026, 10, 6, 1, 30, tzinfo=D.UTC), get=lambda u: None, fetch_remote=False)
    monkeypatch.undo()
    monkeypatch.setenv("FTN_EVENTS_CSV", "/tmp/x.csv")
    assert H.verify_pins().get("FTN_EVENTS_CSV") == "override_forbidden"


def test_duka_code_identical_to_certified_h015b_v2():
    import subprocess
    v2 = subprocess.run(["git", "-C", str(H.REPO), "show", "harness-H015b-v2:research/forward/H015/duka.py"],
                        capture_output=True, text=True, check=True).stdout
    mine = (FWD / "H016b" / "duka.py").read_text()
    code = lambda s: s[s.index("from __future__"):]
    assert code(mine) == code(v2)


# ------------------------------------------------------------------ statistics
def test_binding_bound_is_5th_percentile_not_boot_ci_default():
    S = H.ftn()["stats"]
    xs = [((i * 37) % 101 - 50) / 25 for i in range(300)]
    lo975, _ = S.boot_ci(xs, alpha=0.05)
    lo95, _ = S.boot_ci(xs, alpha=0.10)
    assert lo975 < lo95
    tr = [dict(date=f"d{i:04d}", session="london", instrument="US100", R=x) for i, x in enumerate(xs)]
    vals = H.cluster_boot(tr)
    assert vals[H.LB_INDEX] == pytest.approx(lo95, abs=1e-12) and vals[250] == pytest.approx(lo975, abs=1e-12)
    bb = H.binding_bound(tr)
    assert bb["lb_one_sided_95"] == pytest.approx(lo95, abs=1e-12)
    assert bb["p_one_sided"] == (sum(1 for v in vals if v <= 0) + 1) / 10_001


def test_cluster_keeps_both_instruments_together():
    tr = [dict(date=f"2027-02-{i:02d}", session="ny_am", instrument=inst, R=1.0 if i % 2 else -1.0)
          for i in range(50) for inst in H.INSTS]
    v = H.cluster_boot(tr, n=2000)
    assert all(abs(x * 50 - round(x * 50)) < 1e-9 for x in v)
    assert H.binding_bound(tr)["n_clusters"] == 50


def test_futility_fires_once_on_first_200_only(tmp_path):
    bad = [dict(date=f"2027-03-{i:04d}", session="london", instrument="US100", R=-0.5) for i in range(200)]
    good = [dict(date=f"2027-09-{i:04d}", session="london", instrument="US100", R=3.0) for i in range(500)]
    assert H.futility(bad[:199]) is None
    f = H.futility(bad + good)
    assert f["n"] == 200 and f["fails"]
    assert H.futility(good[:200])["fails"] is False


def test_futility_set_frozen_once_in_sealed_and_reshuffle_reported(tmp_path):
    tr = [dict(date=f"2027-03-{i:04d}", session="london", instrument="US100", R=-0.5) for i in range(1, 251)]
    f = H.futility_frozen(tr, tmp_path)
    p = tmp_path / "sealed" / "FUTILITY_SET.json"
    keys = json.loads(p.read_text())["keys"]
    assert len(keys) == 200 and f["fails"] and f["reshuffle"] == [] and not (tmp_path / "FUTILITY_SET.json").exists()
    early = [dict(date="2027-01-01", session="london", instrument="US100", R=5.0)]
    f2 = H.futility_frozen(early + tr, tmp_path)
    assert json.loads(p.read_text())["keys"] == keys and f2["fails"] == f["fails"]
    assert "2027-01-01|US100|london" in f2["reshuffle"]


def test_kill_at_minus_40():
    tr = [dict(date=f"2027-01-{i:03d}", session="london", instrument="US100", R=-1.0) for i in range(60)]
    k = H.kill_walk(tr)
    assert k["kill"] and k["kill_at_trade"] == 40 and k["min_cum"] == -60
    assert not H.kill_walk(tr[:39])["kill"]


def test_canonical_order():
    tr = [dict(date="2027-01-05", session="ny_am", instrument="US100", R=0), dict(date="2027-01-05", session="london", instrument="US500", R=0),
          dict(date="2027-01-05", session="london", instrument="US100", R=0), dict(date="2027-01-04", session="ny_am", instrument="US500", R=0)]
    assert [(t["date"], t["session"], t["instrument"]) for t in H.canonical(tr)] == [
        ("2027-01-04", "ny_am", "US500"), ("2027-01-05", "london", "US100"), ("2027-01-05", "london", "US500"), ("2027-01-05", "ny_am", "US100")]


# ------------------------------------------------------------------ calendar
def test_calendar():
    assert H.calendar_status(dt.date(2026, 10, 5)) == "ok"
    assert H.calendar_status(dt.date(2026, 10, 10)) == "weekend"
    assert H.calendar_status(dt.date(2026, 11, 26)) == "holiday" and H.calendar_status(dt.date(2026, 11, 27)) == "holiday"
    assert H.calendar_status(dt.date(2026, 9, 7)) == "holiday"            # B4 pre-window Labor Day
    assert H.calendar_status(dt.date(2028, 7, 3)) == "holiday" and H.calendar_status(dt.date(2028, 7, 5)) == "ok"
    assert H.calendar_status(dt.date(2029, 3, 30)) == "holiday" and H.calendar_status(dt.date(2029, 12, 24)) == "holiday"
    assert H.calendar_status(dt.date(2029, 12, 27)) == "ok"
    assert H.calendar_status(dt.date(2030, 4, 19)) == "holiday" and H.calendar_status(dt.date(2030, 11, 29)) == "holiday"
    assert H.calendar_status(dt.date(2031, 1, 2)) == "calendar_not_covered" and "calendar_not_covered" not in H.TERMINAL
    assert H.dst_mismatch_week(dt.date(2026, 10, 27)) and not H.dst_mismatch_week(dt.date(2026, 10, 20))


# ------------------------------------------------------------------ store (synthetic bi5)
def bi5(recs):
    return lzma.compress(b"".join(struct.pack(">5if", *r) for r in recs), format=lzma.FORMAT_ALONE)


def test_store_finality_by_completeness_b1(tmp_path):
    day = dt.date(2026, 10, 5)
    full = bi5([(0, 100000, 100500, 99000, 101000, 1.5), (72840, 100000, 100500, 99000, 101000, 1.5)])
    cut = bi5([(0, 100000, 100500, 99000, 101000, 1.5), (52140, 100000, 100500, 99000, 101000, 1.5)])
    srv = {"b": None}; calls = []
    clock = [dt.datetime(2026, 10, 6, 1, 5, tzinfo=D.UTC)]
    s = D.Store(tmp_path, now=lambda: clock[0], get=lambda u: calls.append(u) or srv["b"])
    assert s.ensure("US100", "ASK", day)["final"] is False
    srv["b"] = cut; clock[0] += dt.timedelta(days=1)
    assert s.ensure("US100", "ASK", day)["completeness"].startswith("cut_off")
    srv["b"] = full; clock[0] += dt.timedelta(days=1)
    m = s.ensure("US100", "ASK", day)
    assert m["final"] and len(calls) == 3 and list((tmp_path / "raw/US100/ASK/superseded").glob("*.bi5"))
    s.ensure("US100", "ASK", day)
    assert len(calls) == 3 and s.verify("US100", "ASK", day)


def test_provisional_then_feed_gap_no_data(tmp_path):
    """Burned date with a failing feed (no bytes served): provisional, then feed_gap_bid after 5 trading days."""
    d = dt.date(2026, 8, 20)
    reg = dict(registered=True, registration_commit="x", registration_time_utc="2026-10-04T10:00:00+00:00", harness_matches_registered=True)
    def get(u):
        raise D.FeedError("503")
    st = H.OwnStore(tmp_path, now=lambda: dt.datetime(2026, 8, 21, 2, tzinfo=D.UTC), get=get)
    rows = H.session_rows_for(st, "US100", d, reg, True, "r1", dt.datetime(2026, 8, 21, 2, tzinfo=D.UTC))
    assert {r[0]["status"] for r in rows} == {"provisional"} and all(o is None for _, o in rows)
    rows = H.session_rows_for(st, "US100", d, reg, True, "r2", dt.datetime(2026, 8, 29, 2, tzinfo=D.UTC))
    assert {r[0]["status"] for r in rows} == {"feed_gap_bid"}


def test_pending_dates_respect_01utc(tmp_path):
    led = H.Ledger(tmp_path)
    assert H.pending_dates(led, dt.datetime(2026, 10, 6, 0, 59, tzinfo=D.UTC)) == []
    assert H.pending_dates(led, dt.datetime(2026, 10, 6, 1, 0, tzinfo=D.UTC)) == [dt.date(2026, 10, 5)]


def test_feed_suspension_after_more_than_10_gap_days(tmp_path):
    lat = {}
    days = H.expected_trading_days(dt.date(2026, 10, 5), dt.date(2026, 11, 6))
    for i, d in enumerate(days):
        st = ("feed_gap_bid" if i % 2 else "feed_gap_ask") if 2 <= i <= 12 else "no_trade"
        for inst in H.INSTS:
            for s in H.SESSIONS:
                lat[(d.isoformat(), inst, s)] = dict(status=st)
    sp = H.suspension(lat, tmp_path)
    assert sp["suspended"] and sp["since"] == days[2].isoformat()
    (tmp_path / "FEED_RESUMED.json").write_text(json.dumps({"resume_from": days[15].isoformat()}))
    assert not H.suspension(lat, tmp_path)["suspended"]


# ------------------------------------------------------------------ burned-tape reproduction + foil + running book
@needs_tape
def test_repro_burned_per_session_every_5th_day():
    r = H.repro_burned(str(TAPE), every=5)
    for inst in H.INSTS:
        assert r[inst]["n_mismatch"] == 0, r[inst]["mismatches"]
        assert r[inst]["n_harness"] == r[inst]["n_csv"] > 0


@needs_tape
def test_foil_with_n_equals_ftn_correct_side_foil():
    F = H.ftn()
    bid = F["bars"].load_series(TAPE / "US100_1m_bid.csv.gz", "US100"); ask = F["bars"].load_series(TAPE / "US100_1m_ask.csv.gz", "US100")
    hist = F["dc"].History(bid, F["bars"].trading_days(bid), ask=ask)
    tr = [dict(date=t["date"], session=t["session"], risk_pts=float(t["risk_pts"])) for t in trades_csv("US100")[:12]]
    ref = F["score"].foil(hist, tr, 0.8, n=40, sim=F["score"].make_sim("US100", hist, "correct_side"))
    got = H.foil_with_n(bid, ask, tr, "US100", n=40)
    assert [g[0] for g in got] == ref and all(0 < g[1] <= 12 for g in got)


def _book_trades(inst):
    return [dict(date=t["date"], session=t["session"], instrument=inst, entry_time=t["entry_time"], exit_time=t["exit_time"],
                 R=float(t["R"])) for t in trades_csv(inst)]


def test_running_book_replay_equals_scorer_running_book():
    """Co-report equivalence: replaying the book over the binding (flat-book) tickets reproduces the scorer's running book."""
    for inst in H.INSTS:
        rb = H.book_replay(_book_trades(inst), pooled=False)[inst]
        want = [f"{t['date']}|{inst}|{t['session']}" for t in trades_csv(inst, "base_runningbook")]
        assert rb["taken_keys"] == want, inst
        assert rb["reset"] == "next_calendar_month" and rb["n_blocked"]["max_drawdown_cap"] > 0
    pooled = H.book_replay(_book_trades("US100") + _book_trades("US500"))["pooled"]
    assert pooled["n_taken"] + pooled["tickets_lost"] == 258


# ------------------------------------------------------------------ end-to-end forward path on BURNED native Dukascopy bi5
def md_get(u, drop=(), truncate=None, strip=None):
    """Fake datafeed serving marketdata's native Dukascopy bi5 (BID and ASK). Refuses any day outside the burned window."""
    p = u.split("/datafeed/")[1].split("/")
    sym, y, m0, d, f = p[0], int(p[1]), int(p[2]), int(p[3]), p[4]
    side = f.split("_")[0]; day = dt.date(y, m0 + 1, d)
    if not (BURNED[0] <= day <= BURNED[1]):
        raise AssertionError(f"test tried to read {day} outside the burned window {BURNED}")
    if (side, day) in set(drop):
        return None
    q = MD_RAW / sym / str(y) / f"{y:04d}{m0 + 1:02d}{d:02d}_{side}.bi5"
    if not q.exists():
        return None
    raw = q.read_bytes()
    if truncate and (side, day) in truncate:
        raw = lzma.compress(lzma.decompress(raw)[:24 * truncate[(side, day)]], format=lzma.FORMAT_ALONE)
    if strip and (side, day) in strip:
        a, b = strip[(side, day)]
        x = lzma.decompress(raw)
        recs = [x[i:i + 24] for i in range(0, len(x), 24)]
        raw = lzma.compress(b"".join(r for r in recs if not (a <= struct.unpack(">5if", r)[0] < b)), format=lzma.FORMAT_ALONE)
    return raw


def getter(**kw):
    return lambda u: md_get(u, **kw)


REG = dict(registered=True, registration_commit="x", registration_time_utc="2026-10-04T10:00:00+00:00", harness_matches_registered=True)


def run_rows(root, d, at, get, inst="US100"):
    st = H.OwnStore(root, now=lambda: at, get=get, short_ok=lambda day: H.calendar_status(day) == "holiday")
    return {r["session"]: (r, o) for r, o in H.session_rows_for(st, inst, d, REG, True, "t", at)}


def utc(y, m, d, h=2, mi=0):
    return dt.datetime(y, m, d, h, mi, tzinfo=D.UTC)


def test_fake_feed_refuses_post_burned_days():
    with pytest.raises(AssertionError):
        md_get(D.url("US100", "BID", dt.date(2026, 9, 28)))
    with pytest.raises(AssertionError):
        md_get(D.url("US500", "ASK", dt.date(2025, 5, 30)))      # DATA certified-untouched US500 range


@needs_md
def test_forward_final_on_native_dukascopy_reproduces_burned_trades(tmp_path, monkeypatch):
    d = dt.date(2026, 3, 25)
    want = {(t["date"], inst, t["session"]): t for inst in H.INSTS for t in trades_csv(inst) if t["date"] == d.isoformat()}
    assert len(want) == 4
    monkeypatch.setattr(H, "pending_dates", lambda led, at: [d])
    monkeypatch.setattr(H, "registration_status", lambda fetch=False: REG)
    rows = H.cmd_final(root=tmp_path, at=utc(2026, 9, 26, 1, 30), get=md_get, fetch_remote=False)
    by = {(r["date"], r["instrument"], r["session"]): r for r in rows}
    for k, t in want.items():
        r = by[k]
        assert r["status"] == "trade" and (r["entry_time"], str(r["entry"]), str(r["stop"])) == (t["entry_time"], t["entry"], t["stop"])
        assert r["counted"] is False and "before_first_eligible_session" in r["not_counted_reasons"]
        assert r["kz_bars_ask"] >= H.KZ_MIN and r["exit_bar_1545_ok_ask"] is True
    outs = {(o["date"], o["instrument"], o["session"]): o for o in H.Ledger(tmp_path).outcomes()}
    for k, t in want.items():
        assert outs[k]["R"] == t["R"] and outs[k]["exit"] == t["exit"] and outs[k]["R_flatcost"] and outs[k]["R_slip2x"]
    hdr = open(tmp_path / "log.csv").readline().strip().split(",")
    assert "R" not in hdr and "fill_out" not in hdr
    assert json.loads((tmp_path / "STATE.json").read_text())["n_counted"] == 0
    assert (tmp_path / "sealed" / "STATE.json").exists()
    rep = H.cmd_report(root=tmp_path)
    assert rep["R"].startswith("SEALED") and "BID+ASK" in rep["feed_disclosure"] and rep["data_monitor_monthly"]
    v = H.cmd_verify(root=tmp_path)
    assert v["ok"] and v["rows_checked"] == 4, v
    lat = H.Ledger(tmp_path).latest()
    assert all(lat[(d.isoformat(), i, s)]["status"] in H.TERMINAL for i in H.INSTS for s in H.SESSIONS)


@needs_md
def test_report_after_clearance_runs_all_co_reports(tmp_path, monkeypatch):
    d = dt.date(2026, 3, 25)
    monkeypatch.setattr(H, "pending_dates", lambda led, at: [d])
    monkeypatch.setattr(H, "registration_status", lambda fetch=False: REG)
    H.cmd_final(root=tmp_path, at=utc(2026, 9, 26, 1, 30), get=md_get, fetch_remote=False)
    rows = list(csv.DictReader(open(tmp_path / "log.csv")))
    for r in rows:                                    # sandbox only: pretend the burned rows were countable
        if r["status"] == "trade":
            r["counted"] = "True"
    with open(tmp_path / "log.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=H.LOG_COLS); w.writeheader(); w.writerows(rows)
    for fn in ("DATA_CERTIFIED.json", "CASSANDRA_CLEARED.json"):
        (tmp_path / fn).write_text(json.dumps({"harness_sha256": H.harness_digest()}))
    rep = H.cmd_report(root=tmp_path, foil_n=20)
    n = rep["n_counted"]
    assert n == 4 and rep["pooled"]["n"] == n and rep["verdict"].startswith("OPEN (N=4 < 100")
    assert rep["foil"]["n_per_replicate"]["max"] <= n
    assert set(rep["cost_ladder"]) == {"correct_side_x1_binding", "correct_side_slip_x2", "flat_cost_co_report"}
    assert rep["cost_ladder"]["correct_side_slip_x2"] <= rep["cost_ladder"]["correct_side_x1_binding"]
    assert rep["running_book_co_report"]["pooled"]["n_taken"] + rep["running_book_co_report"]["pooled"]["tickets_lost"] == n
    assert rep["family_rule"]["holm_thresholds"] == H.HOLM_3 and "not independent replication" in rep["family_rule"]["text"].replace("NOT", "not")
    assert rep["h015b_overlap"]["available"] is False
    assert "data_cond4_excl_context_disclosed_non_binding" in rep and "lb_one_sided_95" in rep["pooled"]["binding_cluster_bound"]
    ff = rep["fill_fragility"]
    assert len(ff["perturbations"]) == 21 and "conservative_one_sided_exit" in ff["perturbations"] and "verdict_flips" in ff
    assert rep["pooled"]["mean_R_conservative_one_sided_exit"] == pytest.approx(rep["pooled"]["mean_R"], abs=1e-12)
    assert rep["one_sided_exit_co_report"]["flagged_n"] == 0
    assert "stale_entry_draws_per_replicate" in rep["foil"]


@needs_md
def test_B2_ask_missing_is_provisional_then_recovers(tmp_path):
    """H016: a 404 ASK session file -> provisional (never a fallback), re-pulled when present -> same row as clean."""
    d = dt.date(2026, 8, 20)
    clean = run_rows(tmp_path / "clean", d, utc(2026, 8, 21), getter())
    rows = run_rows(tmp_path / "a", d, utc(2026, 8, 21, 1, 5), getter(drop={("ASK", d)}))
    assert {r["status"] for r, _ in rows.values()} == {"provisional"} and all(o is None for _, o in rows.values())
    rows = run_rows(tmp_path / "a", d, utc(2026, 8, 22), getter())
    for s in H.SESSIONS:
        assert rows[s][0]["status"] == clean[s][0]["status"] and rows[s][0]["entry_time"] == clean[s][0]["entry_time"]
        assert (rows[s][1] or {}).get("R") == (clean[s][1] or {}).get("R")


@needs_md
def test_B2_persistent_ask_truncation_is_feed_gap(tmp_path):
    d = dt.date(2026, 8, 20)
    tr = getter(truncate={("ASK", d): 1110})
    assert {r["status"] for r, _ in run_rows(tmp_path, d, utc(2026, 8, 24), tr).values()} == {"provisional"}
    assert {r["status"] for r, _ in run_rows(tmp_path, d, utc(2026, 8, 31), tr).values()} == {"feed_gap_ask"}


@needs_md
def test_B3_frozen_bad_context_day_is_skipped_with_disclosure(tmp_path):
    bad = dt.date(2026, 8, 20)
    tr = getter(truncate={("BID", bad): 900})
    run_rows(tmp_path, bad, utc(2026, 8, 31), tr)
    rows = run_rows(tmp_path, dt.date(2026, 9, 1), utc(2026, 9, 2), tr)
    for r, _ in rows.values():
        assert r["status"] in ("trade", "no_trade")
        assert "2026-08-20" in (r["context_frozen_incomplete"] or "") and "2026-08-20" in (r["context_missing_days"] or "")


@needs_md
def test_B4_labor_day_context(tmp_path):
    rows = run_rows(tmp_path, dt.date(2026, 9, 15), utc(2026, 9, 16), getter())
    assert {r["status"] for r, _ in rows.values()} <= {"trade", "no_trade"}
    assert all(r["context_missing_days"] is None for r, _ in rows.values())


@needs_md
def test_B5_exit_bar_rule_every_session_bid_and_ask(tmp_path):
    d = dt.date(2026, 8, 20)                             # EDT: 15:45-16:00 NY = 19:45-20:00 UTC
    for side, flag, reason in (("BID", "exit_bar_1545_ok", "no_bar_1545_1600"), ("ASK", "exit_bar_1545_ok_ask", "no_ask_bar_1545_1600")):
        rows = run_rows(tmp_path / side, d, utc(2026, 8, 21), getter(strip={(side, d): (71100, 72000)}))
        assert {r["status"] for r, _ in rows.values()} == {"short_session"}
        assert all(reason in r["not_counted_reasons"] and r[flag] is False for r, _ in rows.values())


@needs_md
def test_ask_killzone_min_bar_filter(tmp_path):
    d = dt.date(2026, 8, 20)                             # London killzone 02:00-05:00 NY = 06:00-09:00 UTC; strip 20 ASK minutes
    rows = run_rows(tmp_path, d, utc(2026, 8, 21), getter(strip={("ASK", d): (21600, 22800)}))
    r, _ = rows["london"]
    assert r["status"] == "short_session" and r["kz_bars_ask"] < H.KZ_MIN and "kz_bars_ask" in r["not_counted_reasons"]
    assert rows["ny_am"][0]["status"] in ("trade", "no_trade")


@needs_md
def test_final_lock_refuses_concurrent_run(tmp_path, monkeypatch):
    import fcntl
    tmp_path.mkdir(exist_ok=True)
    with open(tmp_path / ".final.lock", "w") as f:
        fcntl.flock(f, fcntl.LOCK_EX)
        with pytest.raises(SystemExit, match="lock"):
            H.cmd_final(root=tmp_path, at=utc(2026, 10, 6, 1, 30), get=lambda u: None, fetch_remote=False)


# ------------------------------------------------------------------ H016b additions (CASSANDRA C1-C3, DATA K1-K10, early-reads rulings)
DATA_ONE_SIDED = pathlib.Path("/home/box/hermes-x/investigations/POST-WAVE1-LEADS/h016_review/one_sided/one_sided_exit.py")
O = H.one_sided


def test_C1_first_eligible_session_after_later_of_tag_and_registration():
    reg = dict(REG, registration_time_utc="2026-10-05T10:30:00+00:00")       # registered after London 10-05 started
    assert "session_started_before_harness_registration" in H.timing_reasons(dt.date(2026, 10, 5), "london", reg)
    assert "session_started_before_harness_registration" not in H.timing_reasons(dt.date(2026, 10, 5), "ny_am", reg)  # 07:00 NY = 11:00 UTC
    reg2 = dict(REG, registration_time_utc="2026-10-04T20:00:00+00:00")
    assert H.timing_reasons(dt.date(2026, 10, 5), "london", reg2) == []
    assert "pre_registration_touched" in H.timing_reasons(dt.date(2026, 10, 1), "ny_am", reg2)
    assert "session_started_before_harness_registration" in H.timing_reasons(dt.date(2026, 10, 5), "london", dict(REG, registration_time_utc=None))
    assert H.PRE_REGISTRATION_TOUCHED == tuple(f"2026-{x}" for x in ("09-26", "09-27", "09-28", "09-29", "09-30", "10-01", "10-02", "10-03"))


def test_C2_quarantine_root_and_foreign_files_refused(tmp_path):
    with pytest.raises(SystemExit, match="quarantined"):
        H.guard_root(pathlib.Path("/home/box/hermes-x/forward/H015b"))
    with pytest.raises(SystemExit, match="quarantined"):
        H.guard_root(pathlib.Path("/workspace/marketdata/raw"))
    src = (FWD / "H016b" / "h016b.py").read_text()
    assert '"H015b"' not in src and "forward/H015b\")" not in src.replace("QUARANTINED_DIRS = (\"/home/box/hermes-x/forward/H015b\"", "")
    assert H.DATA_ROOT.name == "H016b"
    # a file written by another process (plain duka.Store, no provenance) is refused
    d = dt.date(2026, 8, 20)
    D.Store(tmp_path, now=lambda: utc(2026, 8, 22), get=lambda u: bi5([(0, 100000, 100500, 99000, 101000, 1.5)])).ensure("US100", "BID", d)
    assert H.foreign_files(tmp_path)
    with pytest.raises(H.ForeignFile):
        H.OwnStore(tmp_path, now=lambda: utc(2026, 8, 22), get=lambda u: None).ensure("US100", "BID", d)
    with pytest.raises(SystemExit, match="not downloaded by this harness"):
        H.cmd_final(root=tmp_path, at=utc(2026, 8, 22), get=lambda u: None, fetch_remote=False)
    # own downloads carry provenance; tampering is refused
    own = tmp_path / "own"
    st = H.OwnStore(own, now=lambda: utc(2026, 8, 22), get=lambda u: bi5([(0, 100000, 100500, 99000, 101000, 1.5)]))
    st.ensure("US100", "BID", d)
    assert H.foreign_files(own) == []
    st.paths("US100", "BID", d)[1].write_text("Datetime,Open,High,Low,Close,Volume\n")
    assert H.foreign_files(own)


def test_no_marketdata_load_no_default_bars_no_unpinned_modules():
    import sys
    src = (FWD / "H016b" / "h016b.py").read_text()
    assert "marketdata.load" not in src.replace("marketdata.load()", "") and "DEFAULT_BARS" not in src and "import marketdata" not in src
    H.ftn()
    assert H.unpinned_ftn_modules() == []
    assert "marketdata" not in sys.modules
    for bad in ("ftn.__main__", "ftn.adapters", "ftn.journal", "ftn.workflow"):
        assert bad not in sys.modules


def test_one_sided_functions_registered_verbatim_from_DATA():
    import ast, inspect
    if not DATA_ONE_SIDED.exists():
        pytest.skip("DATA reference not on this box")
    ref = DATA_ONE_SIDED.read_text(); t = ast.parse(ref)
    seg = {n.name: ast.get_source_segment(ref, n) for n in t.body if isinstance(n, ast.FunctionDef)}
    seg.update({n.targets[0].id: ast.get_source_segment(ref, n) for n in t.body if isinstance(n, ast.Assign) and isinstance(n.targets[0], ast.Name)})
    mine = (FWD / "H016b" / "one_sided.py").read_text(); tm = ast.parse(mine)
    segm = {getattr(n, "name", None) or n.targets[0].id: ast.get_source_segment(mine, n) for n in tm.body
            if isinstance(n, (ast.FunctionDef, ast.Assign))}
    for name in O.REGISTERED_NAMES:
        assert segm[name] == seg[name], name
    import hashlib
    print("DATA reference sha256 now", hashlib.sha256(ref.encode()).hexdigest(), "registered", O.REGISTERED_SOURCE_SHA256)
    assert O.TARGET_R == H.ftn()["out"].TARGET_R


def _S(ts, o, h, l, c):
    from ftn.research.bars import Series
    return Series("US100", ts, o, h, l, c, "synthetic")


@needs_tape
def test_burned_one_sided_zero_flagged_conservative_equals_pinned_and_trigger_sim_zero_shift():
    """DATA's burned reference: 0/258 flagged, conservative R == pinned R, pooled mean +0.1003; and the trigger-only
    simulator at zero shift is exactly the pinned simulate_both on every burned trade."""
    F = H.ftn(); allR, cons = [], []
    for inst in H.INSTS:
        bid = F["bars"].load_series(TAPE / f"{inst}_1m_bid.csv.gz", inst); ask = F["bars"].load_series(TAPE / f"{inst}_1m_ask.csv.gz", inst)
        sl = H.slip(inst)
        for t in trades_csv(inst):
            et = dt.datetime.fromisoformat(t["entry_time"]); side = "buy" if t["direction"] == "bullish" else "sell"
            p = F["out"].simulate_both(bid, ask, et, float(t["entry"]), float(t["stop"]), side, sl)
            c = O.conservative(bid, ask, et, float(t["entry"]), float(t["stop"]), side, sl)
            z = H.sim_trigger(bid, ask, et, float(t["entry"]), float(t["stop"]), side, sl)
            assert repr(p["R"]) == t["R"] and c["R"] == p["R"] and c["exit"] == p["exit"] and z["R"] == p["R"] and z["exit"] == p["exit"]
            assert O.one_sided_count(bid, ask, et, p["exit_time"])[0] == 0
            allR.append(p["R"]); cons.append(c["R"])
    assert len(allR) == 258 and round(sum(allR) / 258, 4) == 0.1003 == round(sum(cons) / 258, 4)


def test_C3_perturbation_set_and_trigger_semantics():
    names = [n for n, _ in H.PERTURBATIONS]
    assert len(names) == 21 and len(set(names)) == 21
    assert sum(n.startswith("trigger_") for n in names) == 12 and sum(n.startswith("recompute_") for n in names) == 4
    assert {"ask_+0.1", "ask_-0.1", "min_risk_+0.25", "min_risk_-0.25", "conservative_one_sided_exit"} <= set(names)
    H.ftn(); S = _S; t0 = dt.datetime(2026, 1, 5, 9, 0); M = lambda k: t0 + dt.timedelta(minutes=k)
    ts = [M(k) for k in range(6)]
    # long, entry 100, stop 90 (risk 10, target 120); minute 2 BID low = 89.95 (touch by 0.05), minute 4 BID high = 120.05
    bid = S(ts, [100]*6, [101, 101, 101, 101, 120.05, 101], [99, 99, 89.95, 99, 99, 99], [100]*6)
    ask = S(ts, [101]*6, [102, 102, 102, 102, 121.05, 102], [100, 100, 90.95, 100, 100, 100], [101]*6)
    sl = {"market": 0.5, "stop": 0.5, "limit": 0.25}
    base = H.sim_trigger(bid, ask, M(1), 100, 90, "buy", sl)
    assert base["exit"] == "stop" and base == {**base, **{k: v for k, v in H.ftn()["out"].simulate_both(bid, ask, M(1), 100, 90, "buy", sl).items() if k in base}}
    wider = H.sim_trigger(bid, ask, M(1), 100, 90, "buy", sl, d_stop=0.1)            # stop level 89.9: not touched -> target
    assert wider["exit"] == "target" and wider["risk_pts"] == 10 and wider["fill_out"] == 120 - 0.25
    farther = H.sim_trigger(bid, ask, M(1), 100, 90, "buy", sl, d_stop=0.1, d_tgt=0.1)  # target 120.1 not traded through -> time
    assert farther["exit"] == "time"
    closer_t = H.sim_trigger(bid, ask, M(1), 100, 90, "buy", sl, d_stop=0.1, d_tgt=-0.1)
    assert closer_t["exit"] == "target" and closer_t["fill_out"] == pytest.approx(119.9 - 0.25)
    t = dict(entry_time=M(1).isoformat(), entry="100", stop="90", side="buy", instrument="US100")
    rec = H.perturbed_outcome(bid, ask, t, dict(kind="recompute", delta=0.1))          # stop 89.9, risk 10.1, target 120.2
    assert rec["exit"] == "time" and rec["risk_pts"] == pytest.approx(10.1)


def test_fragility_flip_sets_fill_fragile_label():
    rep = dict(pooled=dict(mean_R=0.2, binding_cluster_bound=dict(lb_one_sided_95=0.01)), foil=dict(pct=99.0),
               per_instrument={i: dict(mean_R=0.1) for i in H.INSTS}, robustness=dict(ex_top1pct=0.1, ex_small_stop=0.1),
               fill_fragility=dict(verdict_flips=True))
    k = dict(kill=False); assert H.verdict(rep, H.N_DECISION, k, None) == "PASSES (unadjusted, fill-fragile)"
    rep["fill_fragility"]["verdict_flips"] = False
    assert H.verdict(rep, H.N_DECISION, k, None) == "PASSES (unadjusted)"


def test_kill_log_written_once(tmp_path):
    tr = [dict(date=f"2027-01-{i:03d}", session="london", instrument="US100", R=-1.0) for i in range(60)]
    k = H.kill_walk(tr)
    a = H.kill_log_once(tr, k, tmp_path, utc(2027, 3, 1))
    assert a["kill_at_trade"] == 40 and len(a["keys"]) == 40 and (tmp_path / "sealed" / "KILL_LOG.json").exists()
    b = H.kill_log_once(tr + [dict(date="2026-12-31", session="london", instrument="US100", R=-5.0)], H.kill_walk(tr), tmp_path, utc(2027, 4, 1))
    assert b == a


@needs_md
def test_feed_gap_entry_no_fall_through_2026_03_23(tmp_path):
    """DATA K6(i): the first selection is the ticket; a missing t-1m bar -> feed_gap_entry, no later 15m signal is used."""
    d = dt.date(2026, 3, 23)
    rows = run_rows(tmp_path, d, utc(2026, 3, 24), getter())
    r, o = rows["ny_am"]
    assert r["status"] in ("feed_gap_entry", "short_session") and o is None or r["status"] == "short_session"
    assert r["entry_time"] == "2026-03-23T07:15:00" and r["entry_bar_bid"] is False and r["entry_bar_ask"] is False
    assert "entry_bar_bid=False" in (r["not_counted_reasons"] or "")
    rows_b = H.score_sessions(*H.series_pair(H.OwnStore(tmp_path), "US100", d,
                                             json.loads((tmp_path / r["manifest_file"]).read_text())), d)
    nyam = [x for x in rows_b if x["session"] == "ny_am"]
    assert len(nyam) == 1 and nyam[0]["outcome"] is None and nyam[0]["entry_time"] == "2026-03-23T07:15:00"
    assert rows["london"][0]["status"] == "trade" and rows["london"][0]["calendar_identity_ok"] is True


@needs_md
def test_K4_missing_ask_context_day_is_not_context_gap(tmp_path):
    """Context needs BID only: ASK is fetched only for the session's UTC days d-1, d; a missing ASK on an earlier day is
    never requested and cannot cause context_gap."""
    d = dt.date(2026, 8, 20); asked = []
    def g(u):
        if "/ASK_" in u:
            asked.append(u)
        return md_get(u, drop={("ASK", dt.date(2026, 8, 10))})
    rows = run_rows(tmp_path, d, utc(2026, 8, 21), g)
    assert {r["status"] for r, _ in rows.values()} <= {"trade", "no_trade"}
    assert len(asked) == 2


def test_calendar_not_covered_waits_not_terminal(tmp_path):
    reg = dict(REG)
    st = H.OwnStore(tmp_path, now=lambda: utc(2031, 1, 3), get=lambda u: (_ for _ in ()).throw(AssertionError("no download")))
    rows = H.session_rows_for(st, "US100", dt.date(2031, 1, 2), reg, True, "r", utc(2031, 1, 3))
    assert {r["status"] for r, _ in rows} == {"provisional"} and all("calendar_not_covered" in r["error"] for r, _ in rows)


DATA_TESTS_SHA256 = "439b8ac3b317684c457cfca4c9f2205aa97b94978c6318c3bedacb848d0785e2"


def test_DATA_synthetic_one_sided_tests_verbatim():
    """DATA's synthetic tests T1-T5 (h016_review/one_sided/stats_and_tests.py, sha256 at registration DATA_TESTS_SHA256), copied
    verbatim (print lines dropped) and run against the registered one_sided.conservative + the pinned simulate_both."""
    H.ftn()
    from ftn.research.bars import Series
    from ftn.research.outcomes import simulate_both
    conservative = O.conservative
    # ---- unit tests of conservative() on synthetic bars (the burned tape has no one-sided minutes) ----
    def S(ts, o, h, l, c): return Series("US100", ts, o, h, l, c, "synthetic")
    t0 = dt.datetime(2026, 1, 5, 9, 0); M = lambda k: t0 + dt.timedelta(minutes=k)
    slip = {"market": 0.5, "stop": 0.5, "limit": 0.25}
    tests = []
    # T1 long, minute 3 has BID only and BID low breaches stop -> pinned skips it (later target), conservative stops
    bt = [M(k) for k in range(0, 8)]; at = [M(k) for k in range(0, 8) if k != 3]
    bo = [100]*8; bh = [101,101,101,101,130,130,130,130]; bl = [99,99,99,89,99,99,99,99]; bc = [100]*8
    ask = S(at, [x+1 for i,x in enumerate(bo) if i!=3], [x+1 for i,x in enumerate(bh) if i!=3], [x+1 for i,x in enumerate(bl) if i!=3], [x+1 for i,x in enumerate(bc) if i!=3])
    bid = S(bt, bo, bh, bl, bc)
    p = simulate_both(bid, ask, M(1), 100, 90, "buy", slip); c = conservative(bid, ask, M(1), 100, 90, "buy", slip)
    tests.append(("T1 long BID-only stop minute", p["exit"], c["exit"], p["exit"]=="target" and c["exit"]=="stop_one_sided"))
    # T2 short, minute 3 has BID only; BID high + spread(1) >= stop -> conservative stop_proxy
    bh2 = [101,101,101,110,101,101,101,101]; bl2 = [99,99,99,99,60,60,60,60]
    bid = S(bt, bo, bh2, bl2, bc)
    ask = S(at, [x+1 for i,x in enumerate(bo) if i!=3], [x+1 for i,x in enumerate(bh2) if i!=3], [x+1 for i,x in enumerate(bl2) if i!=3], [x+1 for i,x in enumerate(bc) if i!=3])
    p = simulate_both(bid, ask, M(1), 100, 110.5, "sell", slip); c = conservative(bid, ask, M(1), 100, 110.5, "sell", slip)
    tests.append(("T2 short BID-only proxy brackets stop", p["exit"], c["exit"], p["exit"]=="target" and c["exit"]=="stop_proxy"))
    # T3 long, minute 3 has ASK only with a target-level high: target NOT taken on a one-sided minute
    bt3 = [M(k) for k in range(0,8) if k != 3]; at3 = [M(k) for k in range(0,8)]
    bh3 = [101,101,101,125,101,101,101,101]
    bid = S(bt3, [100]*7, [x for i,x in enumerate(bh3) if i!=3], [99]*7, [100]*7)
    ask = S(at3, [101]*8, [x+1 for x in bh3], [100]*8, [101]*8)
    p = simulate_both(bid, ask, M(1), 100, 90, "buy", slip); c = conservative(bid, ask, M(1), 100, 90, "buy", slip)
    tests.append(("T3 long ASK-only target-level minute ignored", p["exit"], c["exit"], p["exit"]=="time" and c["exit"]=="time"))
    # T4 long, ASK-only minute; last spread narrow (1.0) but session-so-far p95 (3.0) brackets the stop -> stop_proxy via p95_session
    bt4 = [M(k) for k in range(0, 16) if k != 12]; at4 = [M(k) for k in range(0, 16)]
    spr = {k: (3.0 if k < 10 else 1.0) for k in range(16)}
    alow = {k: 96.0 for k in range(16)}; alow[12] = 92.0
    bid = S(bt4, [100]*15, [101]*15, [95]*15, [100]*15)
    ask = S(at4, [100+spr[k] for k in range(16)], [101+spr[k] for k in range(16)], [alow[k] if k == 12 else 95+spr[k] for k in range(16)], [100+spr[k] for k in range(16)])
    ev = []
    p = simulate_both(bid, ask, M(11), 100, 90, "buy", slip); c = conservative(bid, ask, M(11), 100, 90, "buy", slip, events=ev)
    ok4 = p["exit"] == "time" and c["exit"] == "stop_proxy" and ev and ev[0]["source"] == "p95_session" and ev[0]["sp_last"] == 1.0 and ev[0]["sp_used"] == 3.0
    tests.append(("T4 long ASK-only, narrow last spread, p95_session floor triggers stop", p["exit"], c["exit"], ok4)); 
    # T4b same but WITHOUT the floor the v1 rule would not stop (last spread 1.0: 92-1=91 > 90)
    tests.append(("T4b v1 rule (last spread only) would not stop", "-", str(92 - 1.0 > 90), 92 - 1.0 > 90))
    # T5 short, BID-only minute; 20 prior sessions with spread 2.5 -> p95_20d floor triggers; last spread 1.0
    D0 = dt.date(2026, 2, 2); days = []; k = D0 - dt.timedelta(days=1)
    while len(days) < 22:
        if k.weekday() < 5: days.append(k)
        k -= dt.timedelta(days=1)
    days = sorted(days)
    bt5, bo5, bh5, bl5, bc5, at5, ao5, ah5, al5, ac5 = ([] for _ in range(10))
    for d in days:
        for m in range(390):
            t = dt.datetime.combine(d, dt.time(9, 30)) + dt.timedelta(minutes=m)
            bt5.append(t); bo5.append(100); bh5.append(100.5); bl5.append(99.5); bc5.append(100)
            at5.append(t); ao5.append(102.5); ah5.append(103); al5.append(102); ac5.append(102.5)
    for m in range(0, 30):
        t = dt.datetime.combine(D0, dt.time(9, 0)) + dt.timedelta(minutes=m)
        bh = 108.0 if m == 20 else 100.5
        bt5.append(t); bo5.append(100); bh5.append(bh); bl5.append(99.5); bc5.append(100)
        if m != 20: at5.append(t); ao5.append(101); ah5.append(101.5); al5.append(100.5); ac5.append(101)
    bid = S(bt5, bo5, bh5, bl5, bc5); ask = S(at5, ao5, ah5, al5, ac5)
    ev = []; e5 = dt.datetime.combine(D0, dt.time(9, 10))
    p = simulate_both(bid, ask, e5, 100, 110, "sell", slip); c = conservative(bid, ask, e5, 100, 110, "sell", slip, events=ev)
    ok5 = p["exit"] == "time" and c["exit"] == "stop_proxy" and ev and ev[0]["source"] == "p95_20d" and ev[0]["sp_used"] == 2.5 and 108.0 + 1.0 < 110
    tests.append(("T5 short BID-only, narrow last spread, p95_20d floor triggers stop", p["exit"], c["exit"], ok5)); 
    assert all(t[3] for t in tests)
