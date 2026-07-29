"""Backward-compatible wrapper for the CAMI fixed-head coordinate audit."""

import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from experiments.audits.run_cami_fixed_head_coordinate_audit import *  # noqa: E402,F401,F403


if __name__ == "__main__":
    main()
