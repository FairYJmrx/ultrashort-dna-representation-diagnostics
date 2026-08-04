# Final Release Provenance Map

This document maps the submission argument to maintained code, frozen outputs
and manuscript assets. The canonical manuscript is `paper_latex/`; historical
Word and Markdown drafts are excluded from this public snapshot.

## Source-of-Truth Chain

1. Representation definitions live in `methods/`.
2. Data acquisition, preprocessing and simulation live in `data_pipeline/`.
3. Primary experiments and bounded audits live in `experiments/`.
4. Frozen machine-readable outputs live in `results/`.
5. Figure and table builders live in `analysis/`.
6. Submission text, tables, figures and PDFs live in `paper_latex/`.

Any numerical manuscript change must update its source result, regenerate the
affected asset, rebuild the main and supplementary PDFs, and rerun the release
smoke/preflight checks.

## Claim-to-Artifact Map

| Evidence block | Maintained entrypoint | Frozen output | Manuscript asset |
|---|---|---|---|
| CK4P-MSP definition | `methods/ck4p_msp.py` | method-contract smoke outputs | Methods equations; Figure 1 |
| Compact stability/readout | `experiments/main/run_stage3_compact_baselines.py` | `results/stage3/contract_v2/compact_baselines/` | Figure 3; Tables 3--4 |
| Seven K/P/MSP combinations | `experiments/audits/run_p_msp_contribution_audit.py` | `results/stage3/contract_v2/p_msp_contribution/` | Figure 2; Supplementary Table S2 |
| Same-dimension and high-k controls | `run_dimension_reduction_baselines.py`, `run_high_k_compressed_baselines.py` | corresponding `contract_v2/` directories | Figure 3; Supplementary Figure S1 |
| Counterfactual, weight and MI/KSG audits | maintained scripts under `experiments/audits/` | `mixed_metric_audit/`, `p_channel_counterfactual_audit/`, `knn_mi_robustness/` | Supplementary Figures S1--S7 |
| P/MSP relation and runtime | `run_property_redundancy_and_runtime_audit.py`, `run_historical_descriptor_audit.py` | `property_redundancy_runtime/`, `historical_descriptor_audit/` | Supplementary Figures S8--S9 and S12 |
| Short-read continuity | `run_short_read_length_continuity_audit.py` | `short_read_length_continuity/` | Supplementary Figure S13 |
| ART simulator probe | `data_pipeline/simulate/run_stage3_art_generate_and_evaluate.py` | `art_current_contract/` | Figure 4A; Supplementary Figure S3 |
| CAMI_TOY_low fixed-head probes | `run_cami_multitarget_fixed_head_transfer.py` | `cami_multitarget_fixed_head/`, `cami_multitarget_c_sensitivity/` | Figure 4B--C; Supplementary Figure S14 |
| CAMI II anonymous-read stability | `data_pipeline/simulate/run_cami2_marine_lightweight_probe.py` | `cami2_marine_stability/` | Supplementary Figure S10 |
| Full-position upper bound | `experiments/main/run_position_property_controlled_tasks.py` | `fullmatrix_property_contribution_controlled/` | Figure 5 |
| Local-change boundary | `run_local_mutation_sensitivity.py`, `run_local_mutation_fraction_sweep.py` | corresponding `contract_v2/` directories | Figure 6; Supplementary Figure S11 |
| CK4P-MSP-PKM Pareto extension | `methods/experimental_positional_kmer.py` and positional-kmer audits | `candidate_positional_kmer_*`, `external_motif_position_probe/` | Supplementary Figure S15 |

Detailed interpretation boundaries are maintained in
`docs/contract_v2_evidence_map.md`; exact manuscript-to-command mappings are in
`docs/manuscript_script_mapping.md`.

## Release Verification

- `python -m pytest smoke_tests -q`
- `python tools/sanitize_release_paths.py`
- `python tools/release_preflight.py`
- `python tools/reproduce_release.py --mode quick`
- `python tools/generate_release_manifest.py`

The release commit, GitHub Actions result, tag and Zenodo version DOI are
recorded in the GitHub Release notes. Manuscript availability statements cite
the stable Zenodo concept DOI `10.5281/zenodo.21792340`.
