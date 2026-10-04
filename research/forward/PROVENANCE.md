# Provenance of the frozen copies (copied 2026-10-04 SAST by ORION; originals left untouched)

The originals live in folders that are **not under version control**. They were copied byte-for-byte and verified against the
prereg sha256 pins. The harness refuses to run if a pin does not match. Paths below are relative to `research/forward/`.

| Copy | Original | sha256 | Pinned by |
|---|---|---|---|
| `H013/frozen/research/model-u-longrun/scripts/v1/u_engine.py` | `/workspace/ict-blueprint/research/model-u-longrun/scripts/v1/u_engine.py` | `5e98e99e…13fe4e` | H013 prereg `rule_object_sha256` |
| `H013/frozen/research/model-u-longrun/scripts/v1/run_u_lib.py` | `…/scripts/v1/run_u_lib.py` | `8d00223c…cdddad2` | H013 prereg |
| `H013/frozen/research/model-u-longrun/scripts/longrun.py` | `…/scripts/longrun.py` | `bf88f0ad…ef743fc4` | H013 prereg. Provenance only, not imported: it needs the v2 engine. The harness reproduces its v1 path; see `tests/test_h013_repro.py`. |
| `H013/frozen/research/model-u-longrun/data/costs.json` | `…/data/costs.json` | `a1df6f5b…6dd07062d` | H013 prereg |
| `H014/frozen/configs/v5_A_overnight_5mFVG_ce_c12_none.yaml` | `/workspace/mmxm/configs/v5_A_overnight_5mFVG_ce_c12_none.yaml` | `3414c77c…51b67968` | H014 prereg |
| `H014/frozen/mmxm/engine.py`, `data.py`, `config.py`, `baseline.py` | `/workspace/mmxm/mmxm/…` | see prereg | H014 prereg |
| `H014/frozen/mmxm/indicators.py`, `__init__.py` | `/workspace/mmxm/mmxm/…` | `0cd95b11…6ecf` / `6899cc98…7913` | H014 prereg `rule_object_dependencies_sha256` (added 2026-10-04: imported by the engine, previously unpinned) |
| `common/tv_feed.py` | `/workspace/ict-blueprint/forward-test/tv_feed.py` (unchanged since 2026-09-28 15:16 SAST) | `2773d472…c8336` | harness manifest |

The `/workspace/ict-blueprint/forward-test` and `/workspace/mmxm/forward` files were edited in place on 2026-10-04 (08:07–08:10 SAST) by another worker; see `research/forward_harness/` on branch `forward/h013-h014-scripts`, commit 32d131d. Nothing here comes from those edited files except `tv_feed.py`, which they did not change. The pinned rule files were unchanged at copy time.
