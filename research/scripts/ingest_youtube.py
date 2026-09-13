#!/usr/bin/env python3
"""
HERMES-X evidence intake — YouTube ingestion.

Pulls metadata + captions into investigations/<INV>/evidence/<video_id>/
in the pack layout already used by INV-001/002 (META.md, META.json,
auto_captions*.vtt, collapsed.txt, yt-dlp meta). Does NOT interpret,
score, or promote — ATLAS/CASSANDRA triage stays separate.

Also writes an intake ticket (MINT dispatch-ticket pattern):
  evidence/intake_tickets/intake_<video_id>_<stamp>.json

DEPENDENCIES:
    pip install yt-dlp   # or use PATH yt-dlp

USAGE:
    python3 scripts/ingest_youtube.py <youtube_url> --hermes-x . --investigation INV-002-methodology-seed
    python3 scripts/ingest_youtube.py L81eMQhmXmc --hermes-x . --investigation INV-002-methodology-seed
    python3 scripts/ingest_youtube.py <url> --hermes-x . --investigation INV-001-2026-lectures --download-video
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path


YOUTUBE_ID_RE = re.compile(
    r"(?:youtu\.be/|youtube\.com/(?:watch\?v=|shorts/|embed/|live/))([A-Za-z0-9_-]{11})"
)


def extract_video_id(url: str) -> str:
    m = YOUTUBE_ID_RE.search(url)
    if m:
        return m.group(1)
    if re.fullmatch(r"[A-Za-z0-9_-]{11}", url):
        return url
    raise SystemExit(f"Could not extract a video ID from: {url}")


def find_ytdlp() -> str:
    for cand in ("yt-dlp", str(Path.home() / ".local/bin/yt-dlp"), "/workspace/hermes-venv/bin/yt-dlp"):
        p = shutil.which(cand) if not cand.startswith("/") and "/" not in cand else (cand if Path(cand).is_file() else None)
        if p:
            return p
        if Path(cand).is_file():
            return cand
    raise SystemExit("yt-dlp not found. Install: pip install yt-dlp")


def format_duration(seconds: int | float | None) -> str:
    if not seconds:
        return "unknown"
    s = int(seconds)
    h, rem = divmod(s, 3600)
    m, sec = divmod(rem, 60)
    if h:
        return f"{h}:{m:02d}:{sec:02d}"
    return f"{m}:{sec:02d}"


def upload_date_iso(yyyymmdd: str) -> str:
    if not yyyymmdd or len(yyyymmdd) != 8:
        return yyyymmdd or ""
    return f"{yyyymmdd[0:4]}-{yyyymmdd[4:6]}-{yyyymmdd[6:8]}"


@dataclass
class IntakeTicket:
    kind: str  # new_evidence
    video_id: str
    source_url: str
    title: str
    channel: str
    upload_date: str
    duration_s: int
    pack_dir: str
    meta_md: str
    investigation: str
    ingested_at: str
    needs_triage_by: str  # ATLAS
    status: str  # RAW


def already_ingested(pack_dir: Path) -> bool:
    return (pack_dir / "META.md").is_file()


def fetch_meta(ytdlp: str, url: str) -> dict:
    cmd = [ytdlp, "--skip-download", "--dump-json", "--no-warnings", url]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        raise SystemExit(f"yt-dlp metadata failed:\n{r.stderr[-2000:]}")
    return json.loads(r.stdout)


def fetch_captions(ytdlp: str, url: str, pack_dir: Path, video_id: str) -> Path:
    """Download VTT into pack_dir. Prefer manual subs, else auto."""
    pack_dir.mkdir(parents=True, exist_ok=True)
    outtmpl = str(pack_dir / f"{video_id}.%(ext)s")
    # Try manual then auto
    for flags in (
        ["--write-sub", "--sub-langs", "en.*,en", "--skip-download"],
        ["--write-auto-sub", "--sub-langs", "en.*,en", "--skip-download"],
    ):
        cmd = [ytdlp, *flags, "--sub-format", "vtt", "-o", outtmpl, url]
        r = subprocess.run(cmd, capture_output=True, text=True)
        vtts = list(pack_dir.glob(f"{video_id}*.vtt"))
        if r.returncode == 0 and vtts:
            # Normalize name
            src = vtts[0]
            # Prefer auto_captions.en.vtt naming used in lab
            dest = pack_dir / "auto_captions.en.vtt"
            if "auto" in flags[0] or "auto" in src.name:
                dest = pack_dir / "auto_captions.en.vtt"
            else:
                dest = pack_dir / "manual_captions.en.vtt"
            if src.resolve() != dest.resolve():
                shutil.move(str(src), str(dest))
            # clean extras
            for extra in pack_dir.glob(f"{video_id}*.vtt"):
                if extra.resolve() != dest.resolve():
                    extra.unlink(missing_ok=True)
            return dest
    raise SystemExit(
        f"No captions (manual or auto) for {video_id}. Cannot ingest without transcript."
    )


def parse_vtt(path: Path) -> list[dict]:
    text = path.read_text(encoding="utf-8", errors="replace")
    blocks = re.split(r"\n\n+", text)
    segments: list[dict] = []
    ts_re = re.compile(r"(\d{2}:\d{2}:\d{2}\.\d{3}) --> (\d{2}:\d{2}:\d{2}\.\d{3})")
    last_text = None
    for block in blocks:
        m = ts_re.search(block)
        if not m:
            continue
        start, end = m.groups()
        lines = [
            ln.strip()
            for ln in block.splitlines()
            if ln.strip() and "-->" not in ln and not ln.strip().isdigit() and not ln.startswith("WEBVTT")
        ]
        caption = re.sub(r"<[^>]+>", "", " ".join(lines)).strip()
        if caption and caption != last_text:
            segments.append({"start": start, "end": end, "text": caption})
            last_text = caption
    return segments


def write_collapsed(pack_dir: Path, segments: list[dict]) -> Path:
    lines = [f"[{s['start']}] {s['text']}" for s in segments]
    out = pack_dir / "collapsed.txt"
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return out


def write_meta_md(
    pack_dir: Path,
    video_id: str,
    url: str,
    meta: dict,
    caption_kind: str,
    investigation: str,
) -> Path:
    title = meta.get("title", "untitled")
    channel = meta.get("uploader") or meta.get("channel") or "unknown"
    upload = upload_date_iso(meta.get("upload_date") or "")
    duration = format_duration(meta.get("duration"))
    out = pack_dir / "META.md"
    body = f"""# META — {video_id}

**Title:** {title}
**Channel:** {channel}
**Duration:** {duration}
**Upload:** {upload}
**URL:** {url}
**INV role:** {investigation} — RAW intake (not triaged)
**Caption kind:** {caption_kind}
**Status:** RAW — ATLAS must triage; ASR/captions ≠ Observed without QA
**Ingested:** {datetime.now(timezone.utc).strftime("%Y-%m-%d")} via `scripts/ingest_youtube.py`
"""
    out.write_text(body, encoding="utf-8")
    return out


def write_meta_json(pack_dir: Path, video_id: str, url: str, meta: dict, caption_kind: str) -> Path:
    slim = {
        "video_id": video_id,
        "url": url,
        "title": meta.get("title"),
        "channel": meta.get("uploader") or meta.get("channel"),
        "channel_id": meta.get("channel_id"),
        "upload_date": meta.get("upload_date"),
        "duration": meta.get("duration"),
        "caption_kind": caption_kind,
        "status": "RAW",
        "ingested_at": datetime.now(timezone.utc).isoformat(),
    }
    out = pack_dir / "META.json"
    out.write_text(json.dumps(slim, indent=2) + "\n", encoding="utf-8")
    # Full dump for forensics (gitignored often via size — keep small pointer)
    full = pack_dir / "yt-dlp_meta.json"
    # strip huge fields
    dump = {k: meta[k] for k in meta if k not in ("formats", "thumbnails", "automatic_captions", "subtitles")}
    full.write_text(json.dumps(dump, indent=2)[:500_000] + "\n", encoding="utf-8")
    return out


def write_intake_ticket(
    tickets_dir: Path,
    video_id: str,
    url: str,
    meta: dict,
    pack_dir: Path,
    investigation: str,
) -> Path:
    tickets_dir.mkdir(parents=True, exist_ok=True)
    ticket = IntakeTicket(
        kind="new_evidence",
        video_id=video_id,
        source_url=url,
        title=meta.get("title", "untitled"),
        channel=meta.get("uploader") or meta.get("channel") or "unknown",
        upload_date=upload_date_iso(meta.get("upload_date") or ""),
        duration_s=int(meta.get("duration") or 0),
        pack_dir=str(pack_dir),
        meta_md=str(pack_dir / "META.md"),
        investigation=investigation,
        ingested_at=datetime.now(timezone.utc).isoformat(),
        needs_triage_by="ATLAS",
        status="RAW",
    )
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out = tickets_dir / f"intake_{video_id}_{stamp}.json"
    out.write_text(json.dumps(asdict(ticket), indent=2) + "\n", encoding="utf-8")
    latest = tickets_dir / "latest.json"
    latest.write_text(json.dumps(asdict(ticket), indent=2) + "\n", encoding="utf-8")
    return out


def maybe_download_video(ytdlp: str, url: str, pack_dir: Path) -> Path | None:
    out = pack_dir / "lecture.mp4"
    cmd = [
        ytdlp,
        "-f",
        "bv*[ext=mp4]+ba[ext=m4a]/b[ext=mp4]/b",
        "--merge-output-format",
        "mp4",
        "-o",
        str(out),
        url,
    ]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print(f"WARN: video download failed:\n{r.stderr[-1500:]}", file=sys.stderr)
        return None
    return out if out.is_file() else None


def main() -> int:
    ap = argparse.ArgumentParser(description="Ingest YouTube into HERMES-X INV evidence packs")
    ap.add_argument("url", help="YouTube URL or bare 11-char video ID")
    ap.add_argument("--hermes-x", type=Path, required=True)
    ap.add_argument(
        "--investigation",
        required=True,
        help="INV folder name under investigations/ (e.g. INV-002-methodology-seed)",
    )
    ap.add_argument("--download-video", action="store_true", help="Also fetch lecture.mp4 (large; gitignored)")
    ap.add_argument("--force", action="store_true", help="Re-ingest even if META.md exists")
    args = ap.parse_args()

    hx = args.hermes_x.resolve()
    inv_dir = hx / "investigations" / args.investigation
    if not inv_dir.is_dir():
        raise SystemExit(f"Investigation not found: {inv_dir}")

    video_id = extract_video_id(args.url)
    url = args.url if args.url.startswith("http") else f"https://www.youtube.com/watch?v={video_id}"
    pack_dir = inv_dir / "evidence" / video_id
    tickets_dir = hx / "evidence" / "intake_tickets"

    if already_ingested(pack_dir) and not args.force:
        print(f"Already ingested: {pack_dir / 'META.md'}")
        print("Nothing to do (idempotent). Pass --force to re-ingest.")
        return 0

    ytdlp = find_ytdlp()
    print(f"Fetching metadata for {video_id} ...")
    meta = fetch_meta(ytdlp, url)
    pack_dir.mkdir(parents=True, exist_ok=True)

    print("Fetching captions ...")
    vtt = fetch_captions(ytdlp, url, pack_dir, video_id)
    caption_kind = "manual English" if vtt.name.startswith("manual") else "ASR (automatic English)"
    segments = parse_vtt(vtt)
    if not segments:
        raise SystemExit(f"Parsed 0 caption segments from {vtt}")

    write_collapsed(pack_dir, segments)
    write_meta_md(pack_dir, video_id, url, meta, caption_kind, args.investigation)
    write_meta_json(pack_dir, video_id, url, meta, caption_kind)

    # content hash for integrity
    full_text = " ".join(s["text"] for s in segments)
    (pack_dir / "CONTENT_HASH.txt").write_text(
        hashlib.sha256(full_text.encode()).hexdigest() + "\n", encoding="utf-8"
    )

    if args.download_video:
        print("Downloading lecture.mp4 (optional) ...")
        maybe_download_video(ytdlp, url, pack_dir)

    ticket = write_intake_ticket(tickets_dir, video_id, url, meta, pack_dir, args.investigation)

    print(f"Wrote pack              -> {pack_dir}")
    print(f"  META.md / META.json / {vtt.name} / collapsed.txt")
    print(f"Wrote intake ticket     -> {ticket}")
    print()
    print("Status: RAW. Nothing triaged, scored, or promoted.")
    print("Next: ATLAS reviews META.md + collapsed.txt for CLAIM_CARDs.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
