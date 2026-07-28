# Canonical LaTeX manuscript

This directory is the submission source of truth for the main manuscript and
Supplementary Data.

## Files

- `main.tex`: main manuscript root.
- `supplementary.tex`: Supplementary Data root.
- `sections/`: main-text sections.
- `tables/`: main and supplementary LaTeX tables.
- `figures/`: PDF figure assets used by the two roots.
- `references.bib`: manuscript bibliography.
- `paper_manuscript_latex.pdf`: verified main-manuscript rendering.
- `paper_supplementary_latex.pdf`: verified supplementary rendering.

## Compile

The sources use the Oxford University Press authoring class distributed with
the NAR Genomics and Bioinformatics LaTeX template. With that class available
to the local TeX installation, run from this directory:

```powershell
latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex
latexmk -pdf -interaction=nonstopmode -halt-on-error supplementary.tex
```

Build caches and SyncTeX files are intentionally excluded from the release.
The checked-in PDFs are review renderings; the `.tex`, `.bib`, table and figure
files remain the editable submission sources.

`scripts/build_latex_sources.py` is retained only to document the original
Markdown-to-LaTeX migration. It is not the manuscript build command and exits
without changing files unless `--overwrite` is supplied explicitly. Routine
editing must be performed in the checked-in LaTeX sources above.
