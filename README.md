# Ultra-short DNA Read Representation Diagnostics

This repository is the reproducible release for the manuscript on
representation diagnostics for ultra-short metagenomic reads. It is organized
as a methods repository: method definitions are centralized, data preparation
and experiments have separate entrypoints, and manuscript claims are mapped to
scripts and outputs.

## 1. Repository Map

| Path | Purpose |
|---|---|
| `methods/` | Canonical implementation of sequence utilities, CK4/CK5, P, MSP, CK4P-MSP, CSP, full-position encodings and evaluation helpers. |
| `src/` | Compatibility wrappers for older scripts that import `src.*`. New code should import `methods.*`. |
| `data_pipeline/` | Maintained public download, preprocessing and simulation implementations. |
| `experiments/` | Maintained main experiments and method-hardening audits. |
| `analysis/` | Maintained figures, tables, provenance audits and manuscript assembly. |
| `scripts/` | Backwards-compatible command wrappers; not a second implementation tree. |
| `legacy/` | Isolated historical packaging utilities; excluded from the scientific reproduction path. |
| `data/` | Lightweight release data and public benchmark subsets. |
| `results/` | Generated result tables, summaries, run manifests and audit outputs. |
| `figures/` | Central copy of final main and supplementary figure bitmaps. |
| `paper/` | Current split paper draft, paper figures, tables and manuscript build artifacts. |
| `manuscript/` | Historical final/stage manuscript artifacts retained for provenance. |
| `docs/` | Method contract, repository structure, provenance maps and manuscript-script mapping. |
| `configs/` | Experiment matrices and release-default method settings. |
| `references/` | Working bibliography. |
| `smoke_tests/` | Lightweight import and repository checks. |

See `docs/repository_structure.md` and `docs/code_layout.md` for the longer
map and source-of-truth rules.

The manuscript-facing API for the main method is
`methods/ck4p_msp.py`. It exposes CK4, P, MSP, CK4P-MSP assembly and paired
drift helpers directly; older experiment scripts remain available through the
broader `methods/stage2_features.py` feature-construction layer.

## 2. Environment Setup

The release was developed on Windows with Python 3. Recommended setup:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Run a quick import smoke test:

```powershell
.\.venv\Scripts\python.exe smoke_tests\test_imports.py
.\.venv\Scripts\python.exe smoke_tests\test_method_contract.py
.\.venv\Scripts\python.exe smoke_tests\test_repository_layout.py
```

The second check verifies that the public method API and explicit `ck4p_msp`
experiment entrypoint produce the same 222-dimensional default representation.
When a manually distributed `ck4p_msp_standalone.py` is placed at the repository
root, it is checked against the same contract as an optional extra.

ART-based reruns require a local ART executable. The release keeps ART outputs
and summaries, but does not include full FASTQ/SAM intermediates.

## 3. Method Contract

The main method is CK4P-MSP:

- CK4: reverse-complement canonical 4-mer composition block.
- P: global biochemical-property summary.
- MSP: multi-scale positional property pooling over relative-position bins.
- CK4P-MSP: block-normalized CK4, P and MSP with default weights
  `alpha=beta=gamma=1`.

The mixed L2 metric is standardized diagnostic drift, not a natural
biophysical distance. MI/KSG analyses are estimator-dependent empirical audits,
not universal information-theoretic proofs.

See `docs/method_contract.md` and `configs/release_defaults.yaml` for the
formal method contract and default settings.

## 4. Reproduction Path

The old `scripts/` commands remain valid for historical reproduction. New
manuscript-facing experiments use the explicit `ck4p_msp` representation name;
historical `ckmer*_property_*` strings are retained for compatibility and are
not aliases for the block-normalized main method.

### Contract-v2 manuscript evidence

The current manuscript evidence is the `results/stage3/contract_v2/` namespace.
Run the commands below after preparing the lightweight WGS slices. They use the
public `methods.ck4p_msp` implementation and grouped template-level validation
where local perturbation variants share a source template.

```powershell
.\.venv\Scripts\python.exe experiments\main\run_stage3_compact_baselines.py --output-dir results\stage3\contract_v2\compact_baselines
.\.venv\Scripts\python.exe experiments\main\run_local_mutation_sensitivity.py --output-dir results\stage3\contract_v2\local_mutation_sensitivity
.\.venv\Scripts\python.exe experiments\audits\run_p_msp_contribution_audit.py --output-dir results\stage3\contract_v2\p_msp_contribution
.\.venv\Scripts\python.exe experiments\audits\run_high_k_compressed_baselines.py --output-dir results\stage3\contract_v2\high_k_compressed_baselines
.\.venv\Scripts\python.exe experiments\audits\run_knn_mi_robustness_audit.py --output-dir results\stage3\contract_v2\knn_mi_robustness
.\.venv\Scripts\python.exe experiments\audits\run_msp_bin_gamma_sensitivity_audit.py --output-dir results\stage3\contract_v2\msp_bin_gamma_sensitivity
.\.venv\Scripts\python.exe experiments\audits\run_property_redundancy_and_runtime_audit.py --output-dir results\stage3\contract_v2\property_redundancy_runtime
```

The K/P/MSP contribution audit evaluates all seven non-empty block combinations
and reports prespecified conditional contrasts for K given P+MSP, P given
CK4+MSP, and MSP given CK4+P. Grouped delta-readout keeps all derivatives of a
source template in the same fold.

See `docs/contract_v2_evidence_map.md` for the claim, result-table and script
mapping. Historical ART, CAMI and full-position probes remain available for
their bounded external and upper-bound roles, but their legacy feature labels
must not be used to make claims about the public CK4P-MSP contract.

### Data and simulation

```powershell
.\.venv\Scripts\python.exe data_pipeline\preprocess\make_close_relative_reads.py
.\.venv\Scripts\python.exe data_pipeline\preprocess\make_hardened_reads.py
.\.venv\Scripts\python.exe data_pipeline\simulate\run_stage3_art_generate_and_evaluate.py
.\.venv\Scripts\python.exe data_pipeline\simulate\summarize_stage3_art_quality.py
.\.venv\Scripts\python.exe data_pipeline\simulate\run_cami2_marine_lightweight_probe.py
```

### Main experiments

```powershell
.\.venv\Scripts\python.exe experiments\main\run_stage2_representation_grid.py
.\.venv\Scripts\python.exe experiments\main\run_stage2_csp_ablation.py
.\.venv\Scripts\python.exe experiments\main\run_stage2_attention_breakpoint.py
.\.venv\Scripts\python.exe experiments\main\run_stage2_arg_snp_boundary.py
.\.venv\Scripts\python.exe experiments\main\run_stage3_compact_baselines.py
.\.venv\Scripts\python.exe experiments\main\run_stage3_cami_probe.py
.\.venv\Scripts\python.exe experiments\main\run_position_property_controlled_tasks.py
.\.venv\Scripts\python.exe experiments\main\run_local_mutation_sensitivity.py
.\.venv\Scripts\python.exe experiments\main\run_spaced_pattern_sanity.py
```

### Method-hardening audits

```powershell
.\.venv\Scripts\python.exe experiments\audits\run_dimension_reduction_baselines.py
.\.venv\Scripts\python.exe experiments\audits\run_high_k_compressed_baselines.py
.\.venv\Scripts\python.exe experiments\audits\run_mi_audit.py
.\.venv\Scripts\python.exe experiments\audits\run_knn_mi_robustness_audit.py
.\.venv\Scripts\python.exe experiments\audits\run_mixed_metric_audit.py
.\.venv\Scripts\python.exe experiments\audits\run_p_msp_contribution_audit.py
.\.venv\Scripts\python.exe experiments\audits\run_property_redundancy_and_runtime_audit.py
.\.venv\Scripts\python.exe experiments\audits\run_msp_bin_gamma_sensitivity_audit.py
.\.venv\Scripts\python.exe experiments\audits\run_p_channel_counterfactual_audit.py
.\.venv\Scripts\python.exe experiments\audits\run_local_mutation_fraction_sweep.py
```

### Figures, tables and audits

```powershell
.\.venv\Scripts\python.exe analysis\tables\generate_stage3_bootstrap_ci.py
.\.venv\Scripts\python.exe analysis\tables\generate_fullmatrix_property_contribution_ci.py
.\.venv\Scripts\python.exe analysis\figures\generate_nature_main_figures.py
.\.venv\Scripts\python.exe analysis\figures\generate_paper_supplementary_figures.py
.\.venv\Scripts\python.exe analysis\audits\audit_result_inventory.py
.\.venv\Scripts\python.exe analysis\audits\audit_final_provenance.py
```

The complete manuscript-to-script mapping is in
`docs/manuscript_script_mapping.md`.

## 5. Included And Excluded Files

Included:

- Core method code and organized entrypoints.
- Lightweight release data and selected public benchmark subsets.
- Summary results, figure source summaries, final figures and manuscript tables.
- Provenance maps and audit reports.

Excluded:

- Historical smoke outputs, local environments and render intermediates.
- Full CAMI archives, ART FASTQ/SAM intermediates and large paired-read
  fragments.
- Restricted clinical sequencing reads. Only representative length conditions
  are used in this release.

See `RELEASE_MANIFEST.md` for the detailed file inventory.
