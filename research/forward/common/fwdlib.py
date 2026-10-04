"""Shared plumbing for the HERMES-X frozen forward tests (H013, H014). HYPOTHETICAL paper research: no orders, no broker calls.

What lives here (and nothing rule-related does): sha256 pinning, the TradingView CAPITALCOM fetch wrapper (no fallback feeds),
raw-bar persistence, the NYSE calendar check from the prereg, registration-on-main checks from git, and append-only logs.
All rule times are America/New_York wall clock. SAST is reported for humans only."""
from __future__ import annotations

import csv, gzip, hashlib, io, json, os, pathlib, subprocess, datetime as dt
import pandas as pd

TZ = "America/New_York"
SAST = "Africa/Johannesburg"
FORWARD = pathlib.Path(__file__).resolve().parents[1]          # research/forward
REPO = FORWARD.parents[1]                                       # repo root
DATA_ROOT = pathlib.Path(os.environ.get("HERMES_FWD_DATA", "/home/box/hermes-x/forward"))
FEEDS = {"US100": "CAPITALCOM:US100", "US500": "CAPITALCOM:US500"}   # the ONLY feeds a counted row may come from


class FeedError(RuntimeError):
    pass


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def sha256_file(p) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def now_sast() -> pd.Timestamp:
    return pd.Timestamp.now(tz=SAST)


def at(d, hm) -> pd.Timestamp:
    return pd.Timestamp(f"{d} {hm}").tz_localize(TZ)


def load_prereg(path_rel: str) -> dict:
    return json.loads((REPO / path_rel).read_text())


# ------------------------------------------------------------------ pinning
def verify_pins(root: pathlib.Path, pins: dict) -> dict:
    """{relpath: sha256} -> {relpath: actual} for every mismatch (empty dict = all good)."""
    bad = {}
    for rel, want in pins.items():
        p = root / rel
        got = sha256_file(p) if p.exists() else "MISSING"
        if got != want:
            bad[rel] = got
    return bad


def manifest(files) -> dict:
    """Repo-relative path -> sha256 for the harness file set."""
    return {str(pathlib.Path(f).resolve().relative_to(REPO)): sha256_file(f) for f in files}


# ------------------------------------------------------------------ calendar
def calendar_status(d: str, prereg: dict) -> str:
    """'ok' | 'weekend' | 'nyse_full_closure' | 'nyse_early_close' | 'historical_exclusion' | 'calendar_not_covered'."""
    hol = prereg["holidays_excluded"]
    if pd.Timestamp(d).weekday() >= 5:
        return "weekend"
    if d in hol["full_closures"]:
        return "nyse_full_closure"
    if d in hol["early_closes"]:
        return "nyse_early_close"
    if d in hol.get("historical_additions", []):
        return "historical_exclusion"
    last_year = max(hol["full_closures"] + hol["early_closes"])[:4]
    if d > f"{last_year}-12-31":
        return "calendar_not_covered"       # DATA must extend the list before this session can count
    return "ok"


# ------------------------------------------------------------------ feed
def fetch_capitalcom(inst: str, n: int = 8000, now: pd.Timestamp | None = None, _fetch=None) -> tuple[pd.DataFrame, dict]:
    """TradingView CAPITALCOM 1m bars, NY tz. Drops the still-forming bar. Raises FeedError (no fallback, ever)."""
    sym = FEEDS[inst]
    if _fetch is None:
        import sys
        sys.path.insert(0, str(FORWARD / "common"))
        from tv_feed import fetch_tv as _fetch
    t0 = now_sast()
    try:
        df = _fetch(sym, n=n)
    except Exception as e:  # network / symbol / protocol error -> logged gap, never substituted
        raise FeedError(f"{sym}: {str(e)[:200]}") from e
    now = now or pd.Timestamp.now(tz=TZ)
    df = df[df.index + pd.Timedelta(minutes=1) <= now][["Open", "High", "Low", "Close"]].astype(float)
    if not len(df):
        raise FeedError(f"{sym}: no completed bars")
    return df, dict(feed=f"TradingView {sym}", fetch_time_sast=t0.strftime("%Y-%m-%d %H:%M:%S"),
                    fetch_first_bar_ny=str(df.index[0]), fetch_last_bar_ny=str(df.index[-1]), fetch_rows=len(df))


# ------------------------------------------------------------------ raw bars
def bars_to_csv_bytes(df: pd.DataFrame) -> bytes:
    out = df[["Open", "High", "Low", "Close"]].copy()
    out.index = out.index.tz_convert(TZ).strftime("%Y-%m-%d %H:%M:%S%z")
    out.index.name = "time_ny"
    return out.to_csv(float_format="%.5f").encode()


def save_raw(df: pd.DataFrame, lead: str, inst: str, tag: str) -> tuple[str, str]:
    """Persist the exact bars consumed to <DATA_ROOT>/<lead>/raw/<inst>/<tag>.csv (never overwritten).
    Returns (path relative to DATA_ROOT, sha256 of the file bytes)."""
    b = bars_to_csv_bytes(df)
    d = DATA_ROOT / lead / "raw" / inst
    d.mkdir(parents=True, exist_ok=True)
    p = d / f"{tag}.csv"
    k = 1
    while p.exists() and p.read_bytes() != b:
        p = d / f"{tag}_{k}.csv"; k += 1
    if not p.exists():
        p.write_bytes(b)
    return str(p.relative_to(DATA_ROOT)), sha256_bytes(b)


def read_raw(rel: str) -> pd.DataFrame:
    df = pd.read_csv(DATA_ROOT / rel, index_col=0)
    df.index = pd.to_datetime(df.index, utc=True).tz_convert(TZ)
    return df.astype(float)


# ------------------------------------------------------------------ registration (git)
def _git(*a) -> str:
    return subprocess.run(["git", "-C", str(REPO), *a], check=True, capture_output=True, text=True).stdout


def registration_status(prereg_rel: str, current_manifest: dict, ref: str = "origin/main", fetch: bool = False) -> dict:
    """Registration = the FIRST first-parent commit on `ref` (i.e. the moment it landed on main, merge commits included) whose
    prereg carries a harness_sha256.files manifest (DATA fix 5: a git commit, not a script timestamp). Counting additionally needs
    the current harness files to equal that FIRST registered manifest (any later change = new ID, not a silent re-registration)."""
    out = dict(registered=False, registration_commit=None, registration_time_ny=None, harness_matches_registered=False, error=None)
    try:
        if fetch:
            subprocess.run(["git", "-C", str(REPO), "fetch", "-q", "origin", "main"], check=False, capture_output=True, timeout=60)
        for line in reversed(_git("log", "--first-parent", "--format=%H %cI", ref, "--", prereg_rel).splitlines()):
            sha, when = line.split()
            try:
                hs = json.loads(_git("show", f"{sha}:{prereg_rel}")).get("harness_sha256")
            except Exception:
                continue
            if isinstance(hs, dict) and hs.get("repo_root") == "GdotAiM/hermes" and hs.get("files"):
                out.update(registered=True, registration_commit=sha,
                           registration_time_ny=str(pd.Timestamp(when).tz_convert(TZ)),
                           harness_matches_registered=(hs["files"] == current_manifest))
                break
    except Exception as e:
        out["error"] = str(e)[:200]
    return out


# ------------------------------------------------------------------ logs
def append_csv(path: pathlib.Path, row: dict, columns: list[str]):
    path.parent.mkdir(parents=True, exist_ok=True)
    new = not path.exists()
    with open(path, "a", newline="") as f:
        w = csv.DictWriter(f, fieldnames=columns, extrasaction="ignore")
        if new:
            w.writeheader()
        w.writerow({k: row.get(k) for k in columns})


def append_jsonl(path: pathlib.Path, rec: dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a") as f:
        f.write(json.dumps(rec, default=str) + "\n")


def read_jsonl(path: pathlib.Path) -> list[dict]:
    if not path.exists():
        return []
    return [json.loads(l) for l in path.read_text().splitlines() if l.strip()]
