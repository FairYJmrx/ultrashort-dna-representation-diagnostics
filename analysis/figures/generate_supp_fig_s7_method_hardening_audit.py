"""Regenerate the current Supplementary Figure S7 from contract-v2 results.

The plotting implementation is centralized in ``generate_contract_v2_figures``.
This compatibility entrypoint writes the shared source asset and then updates
the manuscript-facing filenames used by the LaTeX project.
"""

from __future__ import annotations

import shutil
from pathlib import Path

from generate_contract_v2_figures import supplementary_s7


ROOT = Path(__file__).resolve().parents[2]
SOURCE_DIR = ROOT / "figures" / "contract_v2"
MANUSCRIPT_DIR = ROOT / "paper_latex" / "figures" / "supplementary"
SOURCE_STEM = "supplementary_figure_s7_high_k_audit"
MANUSCRIPT_STEM = "supp_fig_s7_method_hardening_audit"


def main() -> None:
    supplementary_s7(SOURCE_DIR)
    MANUSCRIPT_DIR.mkdir(parents=True, exist_ok=True)
    for suffix in ("pdf", "png", "svg"):
        shutil.copy2(
            SOURCE_DIR / f"{SOURCE_STEM}.{suffix}",
            MANUSCRIPT_DIR / f"{MANUSCRIPT_STEM}.{suffix}",
        )
    print(f"Updated Supplementary Figure S7 in {MANUSCRIPT_DIR}")


if __name__ == "__main__":
    main()
