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
to the local TeX installation, run from the repository root:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File paper_latex\scripts\build_latex.ps1
```

The script resolves the LaTeX directory independently of the caller's current
working directory, compiles the main manuscript, Supplementary Data and cover
letter, and refreshes the three checked-in review PDFs.

Build caches and SyncTeX files are intentionally excluded from the release.
The checked-in PDFs are review renderings; the `.tex`, `.bib`, table and figure
files remain the editable submission sources.

Routine editing must be performed in the checked-in LaTeX sources above;
historical Markdown-to-Word migration helpers are intentionally excluded from
this release.
