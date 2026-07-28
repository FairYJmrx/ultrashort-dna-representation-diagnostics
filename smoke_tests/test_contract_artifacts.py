"""Regenerate one canonical table and one figure from included contract data."""

from __future__ import annotations

from pathlib import Path
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from analysis.figures.generate_contract_v2_figures import figure_3, style  # noqa: E402
from analysis.tables.generate_contract_v2_tables import compact_table  # noqa: E402


def main() -> None:
    with tempfile.TemporaryDirectory(prefix="ck4p_msp_artifact_smoke_") as tmp:
        output = Path(tmp)
        compact_table(output)
        style()
        figure_3(output)

        table = output / "table3_contract_v2.tex"
        figure = output / "figure_3_contract_v2_stability.pdf"
        assert table.is_file() and table.stat().st_size > 100, "Canonical table was not generated."
        assert figure.is_file() and figure.stat().st_size > 1_000, "Canonical figure was not generated."
        assert "CK4P-MSP" in table.read_text(encoding="utf-8"), "Main method missing from table output."

    print("ok: canonical contract table and figure regenerate from included results")


if __name__ == "__main__":
    main()
