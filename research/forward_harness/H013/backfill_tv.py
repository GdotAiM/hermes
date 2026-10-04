"""H013 BACKFILL logger: re-logs a past NY session from a deeper TradingView CAPITALCOM fetch (8000 1m bars, about 5 sessions),
truncated to the session's 16:59 NY. Same frozen engine and filters as tv_final.py (via h013_harness.finalize_session).
Raw bars consumed are saved to raw/forward/<inst>_<date>.csv (or a timestamped sibling if a different file already exists) with
their sha256 in the row. Rows are run_kind=BACKFILL, note BACKFILLED, and NEVER count (prereg counting_rules.live_alerted_only).
CAPITALCOM only: no PEPPERSTONE/OANDA/Yahoo fallback; a failed fetch is logged as a feed gap.
Usage: backfill_tv.py YYYY-MM-DD [--dry]   HYPOTHETICAL paper research."""
import sys, pandas as pd
import h013_harness as H

def main(argv):
    d = argv[0]; dry = "--dry" in argv; frames, metas = {}, {}
    for nm in ("US100", "US500"):
        try:
            frames[nm], metas[nm] = H.fetch(nm, n=8000, d=d)
            if frames[nm].index[0] > H.at(d, "00:00") - pd.Timedelta(hours=6): raise H.FeedError(f"history too short, starts {frames[nm].index[0]}")
        except H.FeedError as e:
            frames.pop(nm, None); metas[nm] = dict(feed=f"TradingView {H.FEED[nm]}", error=str(e), fetch_time_sast=H.now_sast().strftime("%Y-%m-%d %H:%M:%S"))
    reg = H.registration_status(fetch_remote=not dry)
    note = f"BACKFILLED {H.now_sast():%Y-%m-%d %H:%M} SAST, not live-alerted"
    rows = H.finalize_session(d, "BACKFILL", frames, metas, reg, note=note, dry=dry)
    print(pd.DataFrame(rows).reindex(columns=["date", "instrument", "status", "direction", "entry_time_ny", "entry", "R_5050", "bars_0700_1159",
                                               "raw_file", "raw_sha256", "counted", "not_counted_reasons"]).T.to_string())
    return rows

if __name__ == "__main__": main(sys.argv[1:])
