# Manuscript To Script Mapping

This table maps the current paper narrative to reproducible entrypoints and
primary outputs. It complements `docs/final_release_provenance_map.md`.

| Manuscript block | Primary question | Entrypoint | Main outputs |
|---|---|---|---|
| Study design and representation families | What is CK4P-MSP and what are the comparators? | `methods/ck4p_msp.py`, `methods/stage2_features.py`, `methods/representation_registry.py` | Public method API, method contract and representation definitions. |
| Data layers and perturbation design | Which read layers are used? | `data_pipeline/preprocess/*.py`, `data_pipeline/simulate/*.py` | `data/`, `results/stage3/*_metadata.json`, run manifests. |
| Compact biochemical summaries | Do compact property-aware summaries reduce perturbation drift? | `experiments/main/run_stage3_compact_baselines.py` | `results/stage3/compact_baselines/`, `results/stage3/position_property_ablation/`. |
| Same-dimension reduction controls | Is the result explained by feature count? | `experiments/audits/run_dimension_reduction_baselines.py` | `results/stage3/reviewer_response/dimension_reduction_baselines/`. |
| High-k compressed baselines | Does CK4P-MSP remain stable against compact high-k controls? | `experiments/audits/run_high_k_compressed_baselines.py` | `results/stage3/reviewer_response/high_k_compressed_baselines/`. |
| Empirical MI and kNN MI audit | Do added property distances show perturbation-associated signal? | `experiments/audits/run_mi_audit.py`, `experiments/audits/run_knn_mi_robustness_audit.py` | `results/stage3/reviewer_response/mi_audit/`, `results/stage3/reviewer_response/knn_mi_robustness/`. |
| Seven-group K/P/MSP contribution and redundancy | Which block contributes to stability, local-change readout and nearest-clean retrieval after conditioning on the other blocks? | `experiments/audits/run_p_msp_contribution_audit.py`, `experiments/audits/run_property_redundancy_and_runtime_audit.py` | `results/stage3/contract_v2/p_msp_contribution/`, `results/stage3/contract_v2/property_redundancy_runtime/`. |
| MSP short-bin and gamma sensitivity | Does MSP fail at 69-75 bp? | `experiments/audits/run_msp_bin_gamma_sensitivity_audit.py` | `results/stage3/reviewer_response/msp_bin_gamma_sensitivity/`. |
| ART simulator and error-aware strata | Does the stability trend persist under simulator-derived errors? | `data_pipeline/simulate/run_stage3_art_generate_and_evaluate.py`, `data_pipeline/simulate/summarize_stage3_art_quality.py` | `results/stage3/art_illumina/`, `results/stage3/art_quality_stratified/`. |
| CAMI_TOY_low labelled readout | Does coarse/fine external readout remain task-limited? | `experiments/main/run_stage3_cami_probe.py` | `results/stage3/cami_probe_expanded/`, `results/stage3/cami_*`. |
| CAMI II marine anonymous-read stability | Does compact stability hold on an external anonymous read source? | `data_pipeline/simulate/run_cami2_marine_lightweight_probe.py` | `results/stage3/cami2_marine_lightweight_probe*/`. |
| Full-position upper bound | What does fine positional information add? | `experiments/main/run_position_property_controlled_tasks.py` | `results/stage3/fullmatrix_property_contribution_controlled/`. |
| Local mutation sensitivity | Can nuisance stability be separated from local-change readout? | `experiments/main/run_local_mutation_sensitivity.py`, `experiments/audits/run_local_mutation_fraction_sweep.py` | `results/stage3/local_mutation_sensitivity/`, `results/stage3/reviewer_response/local_mutation_fraction_sweep/`. |
| Boundary analyses | Where does the compact representation stop? | `experiments/main/run_stage2_arg_snp_boundary.py`, `experiments/main/run_stage2_attention_breakpoint.py`, `experiments/main/run_spaced_pattern_sanity.py` | `results/stage2/*`, `results/stage3/spaced_pattern_sanity/`. |
| Figures and manuscript tables | Which assets support the paper? | `analysis/figures/*.py`, `analysis/tables/*.py` | `paper/figures/`, `paper/figures_docx/`, `paper/tables/`, `figures/`. |
| Final provenance audits | Are outputs mapped back to scripts? | `analysis/audits/audit_result_inventory.py`, `analysis/audits/audit_final_provenance.py` | `results/audits/`. |
