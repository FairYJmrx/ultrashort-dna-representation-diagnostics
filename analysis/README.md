# Analysis Entrypoints

This folder groups scripts that transform experiment outputs into tables,
figures, audit summaries and manuscript artifacts.

| Subfolder | Purpose |
|---|---|
| `figures/` | Figure-generation entrypoints. |
| `tables/` | Table and confidence-interval generation entrypoints. |
| `audits/` | Provenance and result-inventory checks. |
| `manuscript/` | Manuscript assembly and historical document generation scripts. |

The canonical figure entrypoint is
`figures/generate_contract_v2_figures.py`, supplemented only by the dedicated
S9 and S10 builders. `generate_paper_supplementary_figures.py` and the Word
builders are retained for historical provenance and are not sources for the
current numerical claims or LaTeX submission.
