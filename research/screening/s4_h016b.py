"""S4 (interface only, protocol v1): read H016b live paper results LATER, read-only, sealed outputs only.

Nothing is read in batch 1. ``H016bSealedReader(None).status()`` is SEALED without touching any path. Once the
registered H016b harness writes DATA_CERTIFIED.json and CASSANDRA_CLEARED.json carrying the harness digest, a
caller may pass the harness *sealed output* directory; only then is ``results()`` allowed to open the sealed log.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

HARNESS_SHA256 = "8a752e769e045b063df9a7b5ef9942f71aa4399bae53bfd9c6637a668c7819a5"
SEALED, CLEARED = "SEALED", "CLEARED"
CLEARANCE_FILES = ("DATA_CERTIFIED.json", "CASSANDRA_CLEARED.json")


class Sealed(RuntimeError):
    pass


@dataclass(frozen=True)
class H016bSealedReader:
    sealed_dir: Path | None = None

    def status(self) -> tuple[str, str]:
        if self.sealed_dir is None:
            return SEALED, "no_sealed_dir_configured"
        d = Path(self.sealed_dir)
        if "/forward/H016b" in str(d.resolve()) and str(d.resolve()).startswith("/home/box/hermes-x"):
            return SEALED, "refusing_live_harness_dir_in_v1"
        for f in CLEARANCE_FILES:
            p = d / f
            if not p.is_file():
                return SEALED, f"missing_{f}"
            try:
                if json.loads(p.read_text()).get("harness_sha256") != HARNESS_SHA256:
                    return SEALED, f"digest_mismatch_{f}"
            except (ValueError, AttributeError):
                return SEALED, f"unreadable_{f}"
        return CLEARED, "cleared"

    def results(self) -> list[dict]:
        st, why = self.status()
        if st != CLEARED:
            raise Sealed(why)
        p = Path(self.sealed_dir) / "log.csv"
        import csv
        with p.open() as fh:   # read-only
            return [dict(r) for r in csv.DictReader(fh)]
