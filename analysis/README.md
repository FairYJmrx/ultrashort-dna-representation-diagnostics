# Analysis Entrypoints

This folder groups scripts that transform experiment outputs into tables,
figures, audit summaries and manuscript artifacts.

| Subfolder | Purpose |
|---|---|
| `figures/` | Figure-generation entrypoints. |
| `tables/` | Table and confidence-interval generation entrypoints. |
| `audits/` | Provenance and result-inventory checks. |

The canonical figure entrypoints are `figures/generate_contract_v2_figures.py`
and `figures/generate_short_read_continuity_figures.py`, followed by
`figures/sync_manuscript_figures.py`; dedicated S9, S10 and S12 builders remain
part of the current figure path. `generate_paper_supplementary_figures.py` is
retained only for regenerating legacy comparison panels and is not the source
of current contract-v2 numerical claims.

Quantitative main-figure method colours and markers are defined centrally in
`figures/figure_style.py`. Current figure builders must import that contract
rather than defining a second method palette.
