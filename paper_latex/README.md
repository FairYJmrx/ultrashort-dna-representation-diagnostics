# LaTeX Manuscript Package

This directory contains the OUP/NAR-style LaTeX source package for the manuscript and supplementary file.

## Key Files

- `main.tex`: main manuscript source.
- `supplementary.tex`: supplementary source.
- `references.bib`: BibTeX reference file.
- `sections/`: manuscript sections generated from the curated paper Markdown files.
- `tables/`: LaTeX tables generated from manuscript CSV tables.
- `figures/`: main and supplementary figure PDFs.
- `scripts/build_latex_sources.py`: regenerates LaTeX source files from the paper workspace.
- `scripts/build_latex.cmd`: local Windows build wrapper for MiKTeX/latexmk.
- `qa/latex_toolchain_report.md`: local toolchain and visual QA report.
- `build/main.pdf`: compiled main manuscript preview.
- `build_supp/supplementary.pdf`: compiled supplementary preview.

## Rebuild

From this directory on Windows:

```powershell
.\scripts\build_latex.cmd
.\scripts\build_latex.cmd -MainTex supplementary.tex -OutputDirectory build_supp
```

The checked-in `main.tex` and `supplementary.tex` are already generated and can be compiled directly with the bundled figures, tables and BibTeX file. The source generator `scripts/build_latex_sources.py` is retained for provenance, but it expects the full manuscript preparation workspace at `D:\AI-NGS\info\paper` and is not required for normal archival compilation.

For archival submission packages, the core files are `main.tex`, `supplementary.tex`, `references.bib`, `figures/` and `tables/`.
