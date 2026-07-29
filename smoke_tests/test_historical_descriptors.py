"""Contract checks for historical handcrafted descriptor controls."""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from methods.historical_descriptors import (  # noqa: E402
    TRINUCLEOTIDES,
    ncp_anf_matrix,
    pseeiip_matrix,
    pseknc_matrix,
)


def main() -> None:
    ncp_anf = ncp_anf_matrix(["ACGT"], length=4)
    assert ncp_anf.shape == (1, 16)
    assert np.isfinite(ncp_anf).all()

    pseeiip = pseeiip_matrix(["AAA"])
    assert pseeiip.shape == (1, 64)
    assert np.flatnonzero(pseeiip[0]).tolist() == [TRINUCLEOTIDES.index("AAA")]

    pseknc = pseknc_matrix(["AAAAAA"], k=3, lambda_value=3, weight=0.05)
    assert pseknc.shape == (1, 67)
    assert np.isclose(pseknc[0, 0], 1.0)
    assert np.count_nonzero(pseknc[0]) == 1

    for matrix in (
        ncp_anf_matrix(["ACNT"], length=5),
        pseeiip_matrix(["ACNT"]),
        pseknc_matrix(["ACNTAC"]),
    ):
        assert np.isfinite(matrix).all()
        assert matrix.shape[0] == 1

    print("Historical descriptor contract checks passed.")


if __name__ == "__main__":
    main()
