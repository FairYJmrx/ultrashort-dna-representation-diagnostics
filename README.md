# Short DNA Read Representation Diagnostics

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.21792340.svg)](https://doi.org/10.5281/zenodo.21792340)
[![release-smoke](https://github.com/FairYJmrx/ultrashort-dna-representation-diagnostics/actions/workflows/smoke.yml/badge.svg?branch=release)](https://github.com/FairYJmrx/ultrashort-dna-representation-diagnostics/actions/workflows/smoke.yml)

This repository is the reproducible release for the manuscript on
representation diagnostics for short metagenomic reads. It is organized
as a methods repository: method definitions are centralized, data preparation
and experiments have separate entrypoints, and manuscript claims are mapped to
scripts and outputs.

The archived `v1.2.0` source and output snapshot is available at version DOI
[10.5281/zenodo.21882250](https://doi.org/10.5281/zenodo.21882250). Zenodo links
all archived versions under the stable concept DOI
[10.5281/zenodo.21792340](https://doi.org/10.5281/zenodo.21792340).

The current four-author release candidate is `v1.2.1`. Its version-specific DOI
will be added after the corresponding GitHub Release is archived by Zenodo.

## 1. Repository Map

| Path | Purpose |
|---|---|
| `methods/` | Canonical implementation of CK4P-MSP, historical handcrafted descriptors, sequence utilities, CSP/full-position controls and evaluation helpers. |
| `src/` | Compatibility wrappers for older scripts that import `src.*`. New code should import `methods.*`. |
| `data_pipeline/` | Maintained public download, preprocessing and simulation implementations. |
| `experiments/` | Maintained main experiments and method-hardening audits. |
| `analysis/` | Maintained figures, tables, provenance audits and manuscript assembly. |
| `scripts/` | Backwards-compatible command wrappers; not a second implementation tree. |
| `data/` | Lightweight release data and public benchmark subsets. |
| `results/` | Generated result tables, summaries, run manifests and audit outputs. |
| `figures/` | Central copy of final main and supplementary figure bitmaps. |
| `paper_latex/` | Canonical submission manuscript source, figures, tables and supplementary file. |
| `docs/` | Method contract, repository structure, provenance maps and manuscript-script mapping. |
| `configs/` | Experiment matrices and release-default method settings. |
| `smoke_tests/` | Lightweight import and repository checks. |
| `tools/` | One-command reproduction and release-preflight utilities. |

See `docs/repository_structure.md` and `docs/code_layout.md` for the longer
map and source-of-truth rules. Submission wording and numbers are governed by
`docs/manuscript_source_of_truth.md`.

The manuscript-facing API for the main method is
`methods/ck4p_msp.py`. It exposes CK4, P, MSP, CK4P-MSP assembly and paired
drift helpers directly; older experiment scripts remain available through the
broader `methods/stage2_features.py` feature-construction layer.

The optional supplementary extension is `CK4P-MSP-PKM`, implemented by
`build_ck4p_msp_pkm()` in `methods/experimental_positional_kmer.py`. It appends
a 75-dimensional positional k-mer moment block at the fixed weight
`delta=0.25`, producing 297 features. It is an exploratory Pareto extension,
not a replacement or alias for the stable main method.

## 2. Environment Setup

The release was developed with Python 3.13 and is tested for release with
Python 3.11 or later. Install the pinned clean-environment dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements-lock.txt
```

Run the complete smoke and preflight checks:

```powershell
.\.venv\Scripts\python.exe -m pytest smoke_tests -q
.\.venv\Scripts\python.exe tools\release_preflight.py
.\.venv\Scripts\python.exe tools\reproduce_release.py --mode quick
```

The method-contract check verifies that the public method API and explicit `ck4p_msp`
experiment entrypoint produce the same 222-dimensional default representation.
When a manually distributed `ck4p_msp_standalone.py` is placed at the repository
root, it is checked against the same contract as an optional extra.

ART-based reruns require a local ART executable. The release keeps ART outputs
and summaries, but does not include full FASTQ/SAM intermediates.
PyTorch is optional and is used only to seed optional legacy neural branches;
it is not required by CK4P-MSP or the maintained manuscript evidence path.

## 3. Method Contract

The main method is CK4P-MSP:

- CK4: reverse-complement canonical 4-mer composition block.
- P: global biochemical-property summary.
- MSP: multi-scale positional property pooling over relative-position bins.
- CK4P-MSP: block-normalized CK4, P and MSP with default weights
  `alpha=beta=gamma=1`.
- CK4P-MSP-PKM: supplementary 297-dimensional extension with a hashed
  positional k-mer moment block and fixed `delta=0.25`.

The mixed L2 metric is standardized representation drift, not a natural
biophysical distance. MI/KSG analyses are estimator-dependent empirical audits,
not universal information-theoretic proofs.

The manuscript does not claim first composition--property fusion or minimum
drift. PseKNC, NCP+ANF and PseEIIP are implemented in
`methods/historical_descriptors.py` as direct historical boundaries. Under the
reported audit, PseKNC is smaller and more stable, whereas CK4P-MSP retains
stronger grouped local-change readability and explicit K/P/MSP attribution.

See `docs/method_contract.md` and `configs/release_defaults.yaml` for the
formal method contract and default settings.

`configs/ck4p_msp_pkm_supplementary.yaml` records the extension contract and
its claim boundaries. The display name never includes the selected numeric
weight; machine-readable manuscript assets use `ck4p_msp_pkm_w025` where a
stable key is required.

## 4. Reproduction Path

For a single entrypoint, use:

```powershell
.\.venv\Scripts\python.exe tools\reproduce_release.py --mode quick
.\.venv\Scripts\python.exe tools\reproduce_release.py --mode full
```

`quick` validates imports, the public method contract, repository structure and
regeneration of one canonical table and figure. `full` runs the maintained
contract-v2 commands that do not require excluded raw archives or a separately
installed ART executable. See the command log under `results/_repro_check/`.

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
.\.venv\Scripts\python.exe experiments\audits\run_grouped_readout_audit.py --output-dir results\stage3\contract_v2\grouped_readout_audit_full
.\.venv\Scripts\python.exe experiments\audits\run_knn_mi_robustness_audit.py --output-dir results\stage3\contract_v2\knn_mi_robustness
.\.venv\Scripts\python.exe experiments\audits\run_local_change_factorial_audit.py --output-dir results\stage3\contract_v2\local_change_factorial
.\.venv\Scripts\python.exe experiments\audits\run_local_change_factorial_audit.py --output-dir results\stage3\contract_v2\local_change_p_attribution --lengths 69,100,150 --local-modes center,left,right,jittered --n-reads 250 --mutation-fraction 0.03 --cv-folds 5 --seed 20260728
.\.venv\Scripts\python.exe experiments\audits\run_property_scaling_audit.py --output-dir results\stage3\contract_v2\property_scaling
.\.venv\Scripts\python.exe experiments\audits\run_property_scaling_audit.py --input results\stage3\contract_v2\compact_baselines\stage3_compact_baseline_reads.csv --output-dir results\stage3\contract_v2\p_coordinate_attribution --lengths 69,75,100,150 --conditions substitution_1pct,N_3pct,trim_5bp,substitution_1pct_N_3pct,local_mismatch_6bp,short_indel --max-pairs 250 --seed 20260728
.\.venv\Scripts\python.exe experiments\audits\run_msp_bin_gamma_sensitivity_audit.py --output-dir results\stage3\contract_v2\msp_bin_gamma_sensitivity
.\.venv\Scripts\python.exe experiments\audits\run_property_redundancy_and_runtime_audit.py --output-dir results\stage3\contract_v2\property_redundancy_runtime
.\.venv\Scripts\python.exe experiments\audits\run_historical_descriptor_audit.py --output-dir results\stage3\contract_v2\historical_descriptor_audit --runtime-read-counts 10000,100000 --runtime-repeats 5 --runtime-large-batch-repeats 1
.\.venv\Scripts\python.exe experiments\audits\run_unified_runtime_benchmark.py --output-dir results\stage3\contract_v2\unified_runtime_benchmark --target-seconds 120 --minimum-repeats 5 --skip-scaling
.\.venv\Scripts\python.exe experiments\audits\run_unified_runtime_benchmark.py --output-dir results\stage3\contract_v2\unified_runtime_scaling_pass --scaling-only
.\.venv\Scripts\python.exe experiments\audits\run_short_read_length_continuity_audit.py --output-dir results\stage3\contract_v2\short_read_length_continuity
.\.venv\Scripts\python.exe experiments\main\run_stage3_cami_probe.py --input data\stage3\cami\cami_toy_low_subset_reads_expanded.csv --output-dir results\stage3\contract_v2\cami_toy_readout
.\.venv\Scripts\python.exe experiments\audits\run_cami_fixed_head_transfer.py --output-dir results\stage3\contract_v2\cami_fixed_head_transfer
.\.venv\Scripts\python.exe experiments\audits\run_cami_fixed_head_coordinate_audit.py --result-dir results\stage3\contract_v2\cami_fixed_head_transfer
.\.venv\Scripts\python.exe experiments\audits\run_cami_multitarget_fixed_head_transfer.py --output-dir results\stage3\contract_v2\cami_multitarget_fixed_head --c-values 1
.\.venv\Scripts\python.exe experiments\audits\run_cami_multitarget_fixed_head_transfer.py --output-dir results\stage3\contract_v2\cami_multitarget_c_sensitivity --representations ck4,ck4p_msp,ck5,pseknc_k3_l3,pseeiip --c-values 0.1,1,10
.\.venv\Scripts\python.exe experiments\audits\run_positional_kmer_weight_sweep.py --output-dir results\stage3\candidate_positional_kmer_weight_sweep
.\.venv\Scripts\python.exe experiments\audits\run_positional_kmer_strand_audit.py --output-dir results\stage3\candidate_positional_kmer_strand_audit
.\.venv\Scripts\python.exe experiments\audits\run_positional_kmer_historical_comparison.py --output-dir results\stage3\candidate_positional_kmer_historical_comparison
.\.venv\Scripts\python.exe data_pipeline\simulate\run_cami2_marine_lightweight_probe.py --output-dir results\stage3\contract_v2\cami2_marine_stability
.\.venv\Scripts\python.exe data_pipeline\simulate\run_stage3_art_generate_and_evaluate.py
.\.venv\Scripts\python.exe data_pipeline\simulate\summarize_stage3_art_quality.py
```

The manuscript runtime values come only from `run_unified_runtime_benchmark.py`.
The historical-descriptor and positional-kmer candidate timing files are retained
for provenance but are not interchangeable with the unified long-duration
contract. The primary run uses full-run medians and interquartile ranges after
at least 120 cumulative timed seconds and five calls per method. The separate
100,000-read invocation is a single scaling pass.

The K/P/MSP contribution audit evaluates all seven non-empty block combinations
and reports prespecified conditional contrasts for K given P+MSP, P given
CK4+MSP, and MSP given CK4+P. Grouped delta-readout keeps all derivatives of a
source template in the same fold.

See `docs/contract_v2_evidence_map.md` for the claim, result-table and script
mapping. Current-contract CAMI\_TOY readout, six-target fixed-head transfer,
learned-preprocessing sensitivity and CAMI II stability outputs are included in
that map. The current ART audit uses the public CK4P-MSP contract at
50, 60, 69, 75, 100, 125 and 150 bp. Full-position probes remain upper-bound
controls; legacy feature labels must not be used to make claims about the public
method. The runtime protocol is specified separately in
`docs/unified_runtime_benchmark.md`.

### E5: 35-species fixed-capacity probe

The large CAMISIM-derived 35-species input is an external server-side input.
The release repository keeps the reconstruction contract without vendoring the
multi-gigabyte FASTQ or token cache. Record input hashes and the label map with:

```powershell
.\.venv\Scripts\python.exe data_pipeline\simulate\prepare_35_species_manifest.py --fastq <FASTQ> --labels <LABELS_NPY> --label-map <LABEL_MAP_JSON> --output-dir results\e5_35species\manifest
  .\.venv\Scripts\python.exe data_pipeline\preprocess\build_35_species_splits.py --labels <LABELS_NPY> --groups <SOURCE_GROUPS_NPY> --output results\e5_35species\splits.npz
  .\.venv\Scripts\python.exe experiments\main\run_e5_multispecies_probe.py --representation CK4 <CK4_NPY> --representation CK4P-MSP <CK4P_MSP_NPY> --labels <LABELS_NPY> --splits results\e5_35species\splits.npz --output-dir results\e5_35species\readout
```

For the formal E5 run, first select the deterministic subset with a maximum
of 50,000 reads per species and 1,500,000 reads overall. Reuse its row-index
file and subset labels for every representation; do not mix the 13.3M-read
FASTQ with a label or feature cache from another generation batch.

Use `--assume-independent-reads` only when simulator documentation guarantees
independent generated reads. The versioned E5 contract is recorded in
`configs/e5_35species.yaml`; treat it and the generated manifest as the
authoritative record of read length, class count, split policy and readout
budget. E5 uses one fixed MLP readout across
representations and is reported as a closed-set representation-accessibility
probe, not as a production species classifier.

`run_grouped_readout_audit.py` is a conservative source-template split check
for the compact WGS readout helper. It does not overwrite historical compact
baseline outputs. The current WGS panel contains one reference accession per
species, so this remains a closed-set reference-panel probe rather than an
unseen-genome generalization benchmark.
CK4P-MSP contract.

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
.\.venv\Scripts\python.exe experiments\audits\run_local_change_factorial_audit.py
.\.venv\Scripts\python.exe experiments\audits\run_property_scaling_audit.py
.\.venv\Scripts\python.exe experiments\audits\run_historical_descriptor_audit.py
.\.venv\Scripts\python.exe experiments\audits\run_unified_runtime_benchmark.py --target-seconds 120 --minimum-repeats 5 --skip-scaling
.\.venv\Scripts\python.exe experiments\audits\run_short_read_length_continuity_audit.py
.\.venv\Scripts\python.exe experiments\audits\run_cami_fixed_head_transfer.py
.\.venv\Scripts\python.exe experiments\audits\run_cami_fixed_head_coordinate_audit.py
.\.venv\Scripts\python.exe experiments\audits\run_cami_multitarget_fixed_head_transfer.py
```

### Figures, tables and audits

```powershell
.\.venv\Scripts\python.exe analysis\figures\generate_contract_v2_figures.py
.\.venv\Scripts\python.exe analysis\figures\generate_supp_fig_s8_redundancy_runtime_audit.py
.\.venv\Scripts\python.exe analysis\figures\generate_supp_fig_s12_historical_descriptor_audit.py
.\.venv\Scripts\python.exe analysis\figures\generate_short_read_continuity_figures.py
.\.venv\Scripts\python.exe analysis\figures\generate_cami_fixed_head_figures.py
.\.venv\Scripts\python.exe analysis\figures\generate_supp_fig_s15_pkm_pareto_audit.py
.\.venv\Scripts\python.exe analysis\figures\sync_manuscript_figures.py
.\.venv\Scripts\python.exe analysis\tables\generate_contract_v2_tables.py
.\.venv\Scripts\python.exe analysis\audits\audit_result_inventory.py
.\.venv\Scripts\python.exe smoke_tests\test_contract_artifacts.py
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
