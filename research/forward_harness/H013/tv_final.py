"""H013 FINAL logger (Model U v1 base, frozen forward-only test). Run once per NY session AFTER 12:00 NY
(18:05 SAST until Fri 30 Oct 2026; 19:05 SAST from Mon 2 Nov 2026), so the 07:00-11:59 min-bar window is complete.
Feed: TradingView CAPITALCOM:US100 (decision series) and CAPITALCOM:US500 (disclosure series) ONLY - no fallback feed,
gaps are logged, never substituted. Engine: frozen v1 (hash-verified), best_trade(ctx, "11:00", False, False, True),
FILL_THRU = 1 tick, costs 0.8 / 0.5 pt per side on every leg. Raw bars -> raw/forward/<inst>_<date>.csv (sha256 in the row).
Writes APPEND-ONLY h013_forward_log.csv (see h013_harness.py). Live-alert evidence comes from h013_live_watch.py.
Replaces the pre-registration tv_final.py (FILL_THRU=0, PEPPERSTONE/OANDA/Yahoo fallbacks, no holiday/min-bar filter,
no raw bars; backup in _pre_h013_backup_2026-10-04/). The legacy forward_log.csv is frozen at 2026-10-02 and never counts.
Usage: tv_final.py [YYYY-MM-DD|today] [--dry] [--raw US100=path.csv US500=path.csv]   HYPOTHETICAL paper research."""
import sys, pandas as pd
import h013_harness as H

def main(argv):
    args = [a for a in argv if not a.startswith("--") and "=" not in a]
    today = pd.Timestamp.now(tz=H.TZ).strftime("%Y-%m-%d")
    d = today if not args or args[0] == "today" else args[0]
    dry = "--dry" in argv; raw = dict(a.split("=", 1) for a in argv if "=" in a)
    run_kind = "FINAL" if d == today else "LATE_FINAL"
    if raw: run_kind = "REPLAY"; dry = True
    if not dry and run_kind == "FINAL" and pd.Timestamp.now(tz=H.TZ) < H.at(d, "12:01"):
        raise SystemExit("tv_final: run after 12:00 NY (07:00-11:59 min-bar window must be complete); use --dry for a preview")
    frames, metas = {}, {}
    for nm in ("US100", "US500"):
        try:
            if nm in raw:
                df = H.load_raw(raw[nm]); df = df[df.index <= H.at(d, "16:59")]
                frames[nm] = df; metas[nm] = dict(feed=f"TradingView {H.FEED[nm]} (replay of saved raw {raw[nm]})", fetch_time_sast=None,
                                                  fetch_first_bar_ny=str(df.index[0]), fetch_last_bar_ny=str(df.index[-1]))
            else: frames[nm], metas[nm] = H.fetch(nm, n=3000, d=d)
        except H.FeedError as e: metas[nm] = dict(feed=f"TradingView {H.FEED[nm]}", error=str(e), fetch_time_sast=H.now_sast().strftime("%Y-%m-%d %H:%M:%S"))
    reg = H.registration_status(fetch_remote=not dry)
    rows = H.finalize_session(d, run_kind, frames, metas, reg, dry=dry)
    show = ["date", "instrument", "run_kind", "status", "direction", "setup", "entry_time_ny", "entry", "stop", "risk_pts", "R_5050", "out_5050",
            "bars_0700_1159", "calendar_status", "raw_sha256", "live_alerted", "counted", "not_counted_reasons"]
    print(pd.DataFrame(rows).reindex(columns=show).T.to_string())
    return rows

if __name__ == "__main__": main(sys.argv[1:])
