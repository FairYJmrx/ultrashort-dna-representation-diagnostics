from __future__ import annotations

import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

import scripts.build_stage2_manuscript as base  # noqa: E402
import scripts.build_stage3_manuscript_v4 as v4  # noqa: E402


def polish_text(md: str) -> str:
    md = md.replace(
        "They support a narrower design principle: short-read DNA pipelines should separate exact identity evidence from compact perturbation-stable auxiliary evidence, rather than ranking representations by a single accuracy number.",
        "They support a narrower design principle: short-read DNA pipelines should separate exact identity evidence from compact perturbation-stable auxiliary evidence, rather than ranking representations by a single accuracy number. CSP provides compact perturbation-stable auxiliary evidence, whereas canonical k-mer/alignment/database evidence remains necessary for exact identity and functional calls.",
        1,
    )
    md = md.replace(
        "Instead, canonical k-mers provide high-resolution identity evidence, whereas CSP provides compact, strand-friendly and perturbation-stable auxiliary evidence. CSP provides compact perturbation-stable auxiliary evidence, whereas canonical k-mer/alignment/database evidence remains necessary for exact identity and functional calls.",
        "Instead, canonical k-mers provide high-resolution identity evidence. CSP provides compact perturbation-stable auxiliary evidence, whereas canonical k-mer/alignment/database evidence remains necessary for exact identity and functional calls.",
    )
    figure_replacements = [
        ("Figure 8. ARG/SNP boundary readout probes.", "Figure 9. ARG/SNP boundary readout probes."),
        ("Figure 7. Best readout transitions around motif visibility.", "Figure 8. Best readout transitions around motif visibility."),
        ("Figure 6. Attention-style context visibility breakpoints.", "Figure 7. Attention-style context visibility breakpoints."),
        ("Figure 5. Deterministic neural compatibility probes.", "Figure 6. Deterministic neural compatibility probes."),
        ("Figure 4. Lightweight readout probes remained task-dependent.", "Figure 5. Lightweight readout probes remained task-dependent."),
        ("Figure 3. Singleton property ablation.", "Figure 4. Singleton property ablation."),
        ("Figure 2. Hospital-like 69/75 bp perturbation drift.", "Figure 3. Hospital-like 69/75 bp perturbation drift."),
        ("Figure 1. Clean-perturbed feature stability across read length.", "Figure 2. Clean-perturbed feature stability across read length."),
    ]
    for old, new in figure_replacements:
        md = md.replace(old, new)
    return md


def main() -> None:
    md = polish_text(v4.build_stage3_v4_markdown())
    v4.MD_PATH.write_text(md, encoding="utf-8")
    base.DOCX_PATH = v4.DOCX_PATH
    base.build_docx(md)
    print(f"Polished {v4.MD_PATH}")
    print(f"Polished {v4.DOCX_PATH}")


if __name__ == "__main__":
    main()
