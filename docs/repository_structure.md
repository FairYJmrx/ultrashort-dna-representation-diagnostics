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
| `experiments/` | Organized entrypoints for main experiments and reviewer-response audits. |
| `analysis/` | Organized entrypoints for figures, tables, audits and manuscript generation. |
| `data/` | Lightweight release data and public benchmark subsets. |
| `results/` | Generated result tables, summaries and audit outputs. |
| `figures/` | Central copy of final main and supplementary figure bitmaps. |
| `paper/` | Current split paper draft, paper figures, paper tables and manuscript build products. |
| `manuscript/` | Historical stage-2/stage-3 manuscript artifacts retained for provenance. |
| `docs/` | Method contract, provenance maps and release notes. |
| `configs/` | Experiment matrices and current release defaults. |
| `references/` | Working bibliography. |
| `smoke_tests/` | Lightweight import and structure checks. |

## Script Compatibility

The root `scripts/` package is retained for import compatibility. Organized
entrypoint wrappers under `data_pipeline/`, `experiments/` and `analysis/` call
the corresponding `scripts.*` modules.

This means historical commands continue to work, while new users can start from
the organized entrypoints.

