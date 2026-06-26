"""Organized entrypoint for `scripts.build_stage3_manuscript_v4`.

The implementation remains in `scripts/build_stage3_manuscript_v4.py` for import compatibility.
Run this file from the repository root or any working directory.
"""

from __future__ import annotations

import runpy
from pathlib import Path
import sys


def _find_repo_root(start: Path) -> Path:
    for candidate in [start, *start.parents]:
        if (candidate / 'scripts').is_dir() and (candidate / 'methods').is_dir():
            return candidate
    raise RuntimeError('Could not locate repository root containing scripts/ and methods/.')


ROOT = _find_repo_root(Path(__file__).resolve())
sys.path.insert(0, str(ROOT))


if __name__ == "__main__":
    runpy.run_module("scripts.build_stage3_manuscript_v4", run_name="__main__")
