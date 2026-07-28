# Repository Structure

This release is organized around four reproducibility questions:

1. Where are the method definitions?
2. How are data downloaded, simulated or preprocessed?
3. Which scripts reproduce each experiment block?
4. Which outputs support each manuscript claim?

## Top-Level Map

| Path | Purpose |
|---|---|
| `methods/` | Canonical method implementation package. |
| `src/` | Backward-compatible import wrappers for historical scripts. |
| `data_pipeline/` | Organized entrypoints for data download, preprocessing and simulation. |
| `experiments/` | Maintained implementations for main experiments and reviewer-response audits. |
| `analysis/` | Maintained implementations for figures, tables, audits and manuscript generation. |
| `data/` | Lightweight release data and public benchmark subsets. |
| `results/` | Generated result tables, summaries and audit outputs. |
| `figures/` | Central copy of final main and supplementary figure bitmaps. |
| `paper_latex/` | Canonical submission manuscript source, figures, tables and supplementary file. |
| `paper/` | Historical pre-LaTeX writing notes retained for provenance; not a numerical or wording source of truth. |
| `manuscript/` | Historical stage-2/stage-3 manuscript artifacts retained for provenance. |
| `docs/` | Method contract, provenance maps and release notes. |
| `configs/` | Experiment matrices and current release defaults. |
| `references/` | Working bibliography. |
| `scripts/` | Backwards-compatible wrappers for historical commands. |
| `legacy/` | Superseded release-packaging utilities, isolated from the active path. |
| `smoke_tests/` | Lightweight import, method-contract and structure checks. |

## Script Compatibility

The root `scripts/` package is retained only for import compatibility. The
maintained implementations live directly under `data_pipeline/`,
`experiments/` and `analysis/`; legacy wrappers import those modules rather
than carrying a second implementation. The manuscript-facing method itself is
defined only in `methods/ck4p_msp.py` and selected with the explicit
representation name `ck4p_msp`; historical feature-name strings are not method
aliases. See `docs/code_layout.md` for detailed rules.

The canonical manuscript contract is documented in
`docs/manuscript_source_of_truth.md`. In particular, historical Word and
Markdown artifacts are not eligible sources for current numerical claims.

This means historical commands continue to work, while new users can start from
the organized entrypoints.
