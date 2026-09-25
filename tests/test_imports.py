"""Chaque module s'importe seul, en premier (le démon importe à la demande : un import circulaire y casse une lecture)."""
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
MODULES = sorted(p.stem for p in ROOT.glob("rog_flare2_*.py") if p.stem not in ("rog_flare2_replay_capture",))


@pytest.mark.parametrize("module", MODULES)
def test_module_imports_alone(module):
    r = subprocess.run([sys.executable, "-c", f"import {module}"], cwd=ROOT, capture_output=True, text=True,
                       timeout=60)
    assert r.returncode == 0, r.stderr[-800:]
