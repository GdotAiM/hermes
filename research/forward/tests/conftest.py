import os, pathlib, sys
FWD = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(FWD)); sys.path.insert(0, str(FWD / "H013")); sys.path.insert(0, str(FWD / "H014"))
DUKA_MU = pathlib.Path(os.environ.get("HERMES_FWD_DUKA_MU", "/workspace/ict-blueprint/research/model-u-longrun"))
MMXM_OUT = pathlib.Path(os.environ.get("HERMES_FWD_MMXM", "/workspace/mmxm"))
