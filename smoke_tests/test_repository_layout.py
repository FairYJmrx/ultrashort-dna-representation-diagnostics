"""Validate the release repository's maintained-code layout.

Run from the repository root:

    python smoke_tests/test_repository_layout.py
"""

from __future__ import annotations

from pathlib import Path
import importlib
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

REQUIRED_DIRECTORIES = (
    "methods",
    "data_pipeline/download",
    "data_pipeline/preprocess",
    "data_pipeline/simulate",
    "experiments/main",
    "experiments/audits",
    "analysis/figures",
    "analysis/tables",
    "analysis/audits",
    "scripts",
)

REPRESENTATIVE_MODULES = (
    "methods.ck4p_msp",
    "data_pipeline.preprocess.make_close_relative_reads",
    "experiments.main.run_stage3_compact_baselines",
    "experiments.audits.run_high_k_compressed_baselines",
    "analysis.figures.generate_nature_main_figures",
    "analysis.tables.generate_nature_main_tables",
)


def main() -> None:
    for relative in REQUIRED_DIRECTORIES:
        assert (ROOT / relative).is_dir(), f"Missing required directory: {relative}"

    non_wrappers: list[str] = []
    for script in (ROOT / "scripts").glob("*.py"):
        if script.name == "__init__.py":
            continue
        prefix = script.read_text(encoding="utf-8")[:240]
        if "Backward-compatible wrapper" not in prefix and "Legacy release-packaging entrypoint" not in prefix:
            non_wrappers.append(script.name)
    assert not non_wrappers, f"scripts/ contains active implementations: {non_wrappers}"

    for module_name in REPRESENTATIVE_MODULES:
        importlib.import_module(module_name)
        print(f"ok: {module_name}")

    contract_results = ROOT / "results" / "stage3" / "contract_v2"
    assert contract_results.is_dir(), "Missing contract_v2 result namespace."
    print("ok: repository layout and source-of-truth rules")


if __name__ == "__main__":
    main()
