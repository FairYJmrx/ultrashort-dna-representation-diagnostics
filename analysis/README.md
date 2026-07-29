# Analysis Entrypoints

This folder groups scripts that transform experiment outputs into tables,
figures, audit summaries and manuscript artifacts.

| Subfolder | Purpose |
|---|---|
| `figures/` | Figure-generation entrypoints. |
| `tables/` | Table and confidence-interval generation entrypoints. |
| `audits/` | Provenance and result-inventory checks. |
| `manuscript/` | Manuscript assembly and historical document generation scripts. |

The canonical figure entrypoints are `figures/generate_contract_v2_figures.py`
and `figures/generate_short_read_continuity_figures.py`, followed by
`figures/sync_manuscript_figures.py`; dedicated S9, S10 and S12 builders remain
part of the current figure path. `generate_paper_supplementary_figures.py` and the Word
builders are retained for historical provenance and are not sources for the
current numerical claims or LaTeX submission.
