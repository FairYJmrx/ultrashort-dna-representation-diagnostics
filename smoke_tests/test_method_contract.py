"""Check the public CK4P-MSP contract and standalone implementation.

Run from the repository root:

    python smoke_tests/test_method_contract.py
"""

from __future__ import annotations

import importlib.util
from pathlib import Path
import sys

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def load_standalone():
    path = ROOT / "ck4p_msp_standalone.py"
    if path.exists():
        spec = importlib.util.spec_from_file_location("ck4p_msp_standalone", path)
        if spec is None or spec.loader is None:
            raise RuntimeError(f"Could not load standalone method from {path}")
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
        return module
    return None


def main() -> None:
    from methods.ck4p_msp import build_block_combination, build_ck4p_msp_features, expected_dimensions
    from methods.stage2_features import build_feature_matrix

    sequences = ["ACGTACGTACGTACGT", "TGCATGCATGCATGCA", "ACGTNNNNACGTACGT"]
    public = build_ck4p_msp_features(sequences)
    matrix, info = build_feature_matrix(sequences, "ck4p_msp", length=16)
    expected = expected_dimensions()

    assert public.matrix.shape == (len(sequences), expected["total"])
    assert info.n_features == expected["total"]
    np.testing.assert_allclose(matrix, public.matrix, rtol=0.0, atol=1e-12)
    np.testing.assert_allclose(np.linalg.norm(public.matrix, axis=1), 1.0, rtol=0.0, atol=1e-12)

    blocks = {"K": public.ck4, "P": public.p, "M": public.msp}
    expected_combinations = {
        ("K",): 136,
        ("P",): 11,
        ("M",): 75,
        ("K", "P"): 147,
        ("K", "M"): 211,
        ("P", "M"): 86,
        ("K", "P", "M"): 222,
    }
    names = {
        ("K",): "ck4",
        ("P",): "p",
        ("M",): "msp",
        ("K", "P"): "ck4_p",
        ("K", "M"): "ck4_msp",
        ("P", "M"): "p_msp",
        ("K", "P", "M"): "ck4p_msp",
    }
    for parts, dimension in expected_combinations.items():
        combined = build_block_combination(public, names[parts])
        assert combined.shape == (len(sequences), dimension)
        np.testing.assert_allclose(np.linalg.norm(combined, axis=1), 1.0, rtol=0.0, atol=1e-12)
        via_registry, registry_info = build_feature_matrix(sequences, names[parts], length=16)
        assert registry_info.n_features == dimension
        np.testing.assert_allclose(via_registry, combined, rtol=0.0, atol=1e-12)

    standalone = load_standalone()
    if standalone is not None:
        external = standalone.build_ck4p_msp_features(sequences).matrix
        np.testing.assert_allclose(external, public.matrix, rtol=0.0, atol=1e-12)
        print("ok: standalone and repository CK4P-MSP implementations agree")
    else:
        print("note: optional standalone script is intentionally not part of this repository checkout")
    print(f"ok: CK4P-MSP contract shape {public.matrix.shape}")
    print("ok: all seven non-empty K/P/MSP block combinations satisfy the fixed normalization contract")


if __name__ == "__main__":
    main()
