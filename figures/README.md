# Figures Directory

This folder contains the authoritative submission-grade figure exports.

| Subfolder | Contents |
|---|---|
| `contract_v2/` | PDF, PNG and SVG exports used by the final manuscript and supplementary information. |

`analysis/figures/sync_manuscript_figures.py` maps these exports into the stable
filenames under `paper_latex/figures/`. The LaTeX tree tracks only the PDF
copies required for compilation; PNG and SVG exports remain here for visual
inspection and editing.
