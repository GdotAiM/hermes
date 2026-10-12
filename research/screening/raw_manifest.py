"""C4: per-raw-file manifest (raw sha256 + LZMA-decompressed-content sha256) for $SCREENING_DATA/raw.
Read-only; no network. Refuses any file dated after 2026-09-25.
  python3 -m research.screening.raw_manifest > research/screening/s1_raw_manifest.csv
"""
import hashlib, lzma, sys, datetime as dt
from research.screening.dl import root, END, INSTRUMENTS, SIDES, days

def main():
    w = sys.stdout.write
    w("sym,side,day,raw_bytes,raw_sha256,decomp_bytes,decomp_sha256,records\n")
    for d in sorted(days()):
        for sym in INSTRUMENTS.values():
            for side in SIDES:
                assert d <= END
                p = root() / "raw" / sym / side / f"{d:%Y%m%d}.bi5"
                if not p.exists():
                    w(f"{sym},{side},{d:%Y-%m-%d},MISSING,,,,\n"); continue
                raw = p.read_bytes()
                dec = lzma.decompress(raw) if raw else b""
                w(f"{sym},{side},{d:%Y-%m-%d},{len(raw)},{hashlib.sha256(raw).hexdigest()},"
                  f"{len(dec)},{hashlib.sha256(dec).hexdigest()},{len(dec)//24}\n")

if __name__ == "__main__":
    main()
