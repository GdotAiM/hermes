"""H013 live-alert watcher (audit trail for the prereg 'live_alerted_only' rule). HYPOTHETICAL paper research: no orders.
Polls TradingView CAPITALCOM:US100 / US500 (no fallback) once a minute (at :05 s) from start until 11:31 NY, runs the frozen
v1 invocation (FILL_THRU=1, hash-verified engine) on the bars available so far, and APPENDS one FILL event per new first-fill
to h013_alerts.jsonl with the SAST alert time and a raw snapshot (raw/forward/live/<inst>_<date>_<HHMMSS>.csv + sha256).
tv_final.py marks a trade live_alerted only if its FILL event precedes the trade's 50-50 exit time.
Single instance per box (flock). Start it before 09:00 NY (14:55 SAST until 30 Oct 2026; 15:55 SAST from 2 Nov 2026):
  ./run_h013_h014_session.sh watch   (= nohup setsid .venv/bin/python h013_live_watch.py >> h013_live_watch_<date>.log 2>&1 &)
Usage: h013_live_watch.py [--once] [--until HH:MM]"""
import sys, time, fcntl, json, pandas as pd
import h013_harness as H

def poll(E1, V1, d, seen):
    out = []
    for nm in ("US100", "US500"):
        ts = H.now_sast().strftime("%Y-%m-%d %H:%M:%S")
        try: df, meta = H.fetch(nm, n=1500)
        except H.FeedError as e:
            H.append_alert(dict(event="FEED_GAP", date=d, instrument=nm, alert_sast=ts, error=str(e))); out.append(f"{nm} FEED_GAP {e}"); continue
        df = df[df.index < H.at(d, "12:00")]
        if not len(df) or df.index[-1] < H.at(d, "09:00"): out.append(f"{nm} waiting (last bar {df.index[-1] if len(df) else None})"); continue
        res, t = H.evaluate(E1, V1, df, d, nm)
        if t is None: out.append(f"{nm} no fill yet (last bar {df.index[-1]:%H:%M} NY)"); continue
        k = H.trade_key(d, nm, res["direction"], res["entry"], res["entry_time_ny"])
        if k in seen: out.append(f"{nm} filled {k} (alerted)"); continue
        rel, h = H.save_raw(df, f"{nm}_{d}_{H.now_sast():%H%M%S}", sub="live")
        trunc = "time exit" in str(res["out_5050"]) and df.index[-1] < H.at(d, "11:29")
        ev = dict(event="FILL", key=k, date=d, instrument=nm, stream=H.STREAM[nm], alert_sast=ts, last_bar_ny=str(df.index[-1]),
                  direction=res["direction"], setup=res["setup"], entry=res["entry"], stop=res["stop"], T1=res["T1"], T2=res["T2"],
                  fill_time_ny=res["entry_time_ny"], exit_already_in_data=not trunc, outcome_so_far=res["out_5050"],
                  raw_file=rel, raw_sha256=h, feed=meta["feed"], fetch_time_sast=meta["fetch_time_sast"], harness_sha256_digest=H.harness_digest())
        H.append_alert(ev); seen.add(k); out.append(f"{nm} NEW FILL ALERT {json.dumps(ev, default=str)}")
    return out

def main(argv):
    lock = open(H.FT / ".h013_live_watch.lock", "w")
    try: fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError: print("h013_live_watch: already running"); return
    E1, V1 = H.load_engine()
    until = argv[argv.index("--until") + 1] if "--until" in argv else "11:31"
    d = pd.Timestamp.now(tz=H.TZ).strftime("%Y-%m-%d")
    if H.calendar_status(d) in ("weekend", "holiday_full_closure"): print(f"h013_live_watch: {d} is {H.calendar_status(d)}; nothing to watch"); return
    seen = {a["key"] for a in H.read_alerts() if a.get("event") == "FILL" and a.get("date") == d}
    print(f"[{H.now_sast():%H:%M:%S} SAST] H013 watcher start {d} until {until} NY; harness {H.harness_digest()[:12]}; cal {H.calendar_status(d)}", flush=True)
    while True:
        try: lines = poll(E1, V1, d, seen)
        except Exception as e: lines = [f"POLL ERROR (will retry next minute): {type(e).__name__}: {str(e)[:200]}"]
        for line in lines: print(f"[{H.now_sast():%H:%M:%S} SAST] {line}", flush=True)
        if "--once" in argv or pd.Timestamp.now(tz=H.TZ) >= H.at(d, until): break
        now = pd.Timestamp.now(tz=H.TZ); nxt = now.floor("min") + pd.Timedelta(seconds=65)
        time.sleep(max(1.0, (nxt - now).total_seconds()))
    print(f"[{H.now_sast():%H:%M:%S} SAST] H013 watcher done", flush=True)

if __name__ == "__main__": main(sys.argv[1:])
