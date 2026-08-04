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


def assert_no_legacy_main_key() -> None:
    """Reject the historical main-method alias in active release files."""
    legacy_key = "ck4" + "_p_msp"
    text_extensions = {
        ".py", ".md", ".csv", ".json", ".txt", ".yaml", ".yml",
        ".tex", ".bib", ".aux", ".toc", ".out", ".log", ".tsv",
    }
    offenders: list[str] = []
    for path in ROOT.rglob("*"):
        if not path.is_file() or "archive" in path.parts or path.suffix.lower() not in text_extensions:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        relative = path.relative_to(ROOT)
        if legacy_key in text:
            offenders.append(str(relative))
    assert not offenders, f"legacy CK4P-MSP alias found in active files: {offenders}"


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
    assert_no_legacy_main_key()
    from methods.ck4p_msp import build_block_combination, build_ck4p_msp_features, expected_dimensions
    from methods.experimental_positional_kmer import (
        CK4P_MSP_PKM_KEY,
        CK4P_MSP_PKM_LABEL,
        build_weighted_augment_candidates,
    )
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

    assert CK4P_MSP_PKM_KEY == "ck4p_msp_pkm_w025"
    assert CK4P_MSP_PKM_LABEL == "CK4P-MSP-PKM"
    weighted = build_weighted_augment_candidates(sequences, [0.1, 0.25])
    assert CK4P_MSP_PKM_KEY in weighted
    assert "pkm_weight_w010" in weighted
    assert "cpkm_weight_w025" in weighted
    assert "pkm_" + "augment_w025" not in weighted

    standalone = load_standalone()
    if standalone is not None:
        external = standalone.build_ck4p_msp_features(sequences).matrix
        np.testing.assert_allclose(external, public.matrix, rtol=0.0, atol=1e-12)
        print("ok: standalone and repository CK4P-MSP implementations agree")
    else:
        print("note: optional standalone script is intentionally not part of this repository checkout")
    print(f"ok: CK4P-MSP contract shape {public.matrix.shape}")
    print("ok: all seven non-empty K/P/MSP block combinations satisfy the fixed normalization contract")


def test_method_contract_smoke() -> None:
    main()


if __name__ == "__main__":
    main()
