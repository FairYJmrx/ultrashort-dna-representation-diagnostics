"""Backward-compatible wrapper for the CAMI multi-target fixed-head audit."""

import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from experiments.audits.run_cami_multitarget_fixed_head_transfer import main  # noqa: E402


if __name__ == "__main__":
    main()
