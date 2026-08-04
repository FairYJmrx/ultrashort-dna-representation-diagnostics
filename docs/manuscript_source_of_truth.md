# Manuscript Source of Truth

The canonical submission manuscript is the LaTeX project in `paper_latex/`.
Its numerical claims must be traceable to `results/stage3/contract_v2/` through
`docs/contract_v2_evidence_map.md`.

Historical Markdown and Word drafts are intentionally excluded from the public
snapshot. They are not current wording, numerical or figure sources and must
not be used to regenerate submission claims.

Submission-facing files are:

- `paper_latex/main.tex` and `paper_latex/sections/` for the main manuscript;
- `paper_latex/supplementary.tex` for Supplementary Data;
- `paper_latex/references.bib` for bibliography metadata;
- `paper_latex/figures/` and `paper_latex/tables/` for included assets;
- `paper_latex/paper_manuscript_latex.pdf` and
  `paper_latex/paper_supplementary_latex.pdf` for review rendering.

Local LaTeX build directories and rendered QA pages are excluded from the
release. Any change to a manuscript result requires updating the canonical
result CSV, regenerating the affected table or figure, recompiling both PDFs,
and rerunning `smoke_tests/test_contract_artifacts.py`.
