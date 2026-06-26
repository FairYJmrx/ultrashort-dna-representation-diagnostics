"""Lightweight import smoke test for the release repository.

Run from the repository root:

    python smoke_tests/test_imports.py
"""

from __future__ import annotations

import importlib
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

MODULES = [
    "methods.ck4p_msp",
    "methods.sequence_utils",
    "methods.stage2_features",
    "methods.representation_registry",
    "methods.spaced_features",
    "src.stage2_features",
    "scripts.run_stage2_representation_grid",
    "scripts.run_stage3_compact_baselines",
]


def main() -> None:
    for module in MODULES:
        importlib.import_module(module)
        print(f"ok: {module}")
    from methods.ck4p_msp import build_ck4p_msp, expected_dimensions

    sequences = ["ACGTACGTACGTACGT", "TGCATGCATGCATGCA"]
    matrix = build_ck4p_msp(sequences)
    expected = expected_dimensions()["total"]
    assert matrix.shape == (2, expected), f"Unexpected CK4P-MSP shape: {matrix.shape}"
    print(f"ok: CK4P-MSP shape {matrix.shape}")


if __name__ == "__main__":
    main()
