# Figure and Table Inventory

## Main figures

- Figure 1: Representation-diagnostic framework and read-length regime. Source script: `info/scripts/generate_nature_main_figures.py`. Asset: `paper/figures/nature_fig1_framework.*`.
- Figure 2: Compact stability of identity, spaced, and property-aware representations. Source script: `info/scripts/generate_nature_main_figures.py` plus bootstrap tables. Asset: `paper/figures/nature_fig2_compact_stability.*`.
- Figure 3: CK4P-MSP compact trade-off between stability, readout, and feature dimension. Source script: `info/scripts/generate_nature_main_figures.py`. Asset: `paper/figures/nature_fig3_ck4p_msp_tradeoff.*`.
- Figure 4: External ART and CAMI probes, separating ART paired-cosine stability, CAMI coarse target/background readout and CAMI fine label-probe limits. Source script: `info/scripts/generate_nature_main_figures.py`. Asset: `paper/figures/nature_fig4_external_probes.*`.
- Figure 5: Full-position diagnostic upper-bound analysis. Source script: `info/scripts/generate_nature_main_figures.py`. Asset: `paper/figures/nature_fig5_full_position_upper_bound.*`.
- Figure 6: Local mutation sensitivity and delta-readout analysis. Source script: `info/scripts/generate_nature_main_figures.py`. Asset: `paper/figures/nature_fig6_local_mutation_sensitivity.*`.

## Supplementary figures generated for the paper folder

- Supplementary Figure S1: Baseline and mixed-metric audit, including same-dimensional PCA/SVD, hash/sketch or signal baselines, and block-weight sensitivity. Source script: `info/scripts/generate_paper_supplementary_figures.py`. Asset: `paper/figures/supp_fig_s1_baseline_audit.*`.
- Supplementary Figure S2: Empirical MI/conditional-MI proxy audit for mutation labels. Source script: `info/scripts/generate_paper_supplementary_figures.py`. Asset: `paper/figures/supp_fig_s2_mi_audit.*`.
- Supplementary Figure S3: Error-aware, quality-stratified ART perturbation audit. Source script: `info/scripts/generate_paper_supplementary_figures.py`. Asset: `paper/figures/supp_fig_s3_error_aware_art.*`.
- Supplementary Figure S4: Local-mutation fraction sweep. Source script: `info/scripts/generate_paper_supplementary_figures.py`. Asset: `paper/figures/supp_fig_s4_mutation_fraction_sweep.*`.
- Supplementary Figure S5: P-channel counterfactual and short-bin reliability audit, including CK4 plus permuted/Gaussian P/MSP controls, conditional block information and MSP bin-size reliability. Source script: `info/scripts/run_p_channel_counterfactual_audit.py`. Asset: `paper/figures/supp_fig_s5_p_channel_counterfactual_audit.*`.
- Supplementary Figure S6: MSP binset and gamma-sensitivity audit, testing whether finer multi-scale bins or the default gamma produce short-read collapse. Source script: `info/scripts/run_msp_bin_gamma_sensitivity_audit.py`. Asset: `paper/figures/supp_fig_s6_msp_bin_gamma_sensitivity.*`.
- Supplementary Figure S7: Methodological hardening audit, combining kNN MI robustness and dimension-matched high-k compressed k-mer baselines. Source scripts: `info/scripts/run_knn_mi_robustness_audit.py`, `info/scripts/run_high_k_compressed_baselines.py`, and `info/scripts/generate_supp_fig_s7_method_hardening_audit.py`. Asset: `paper/figures/supp_fig_s7_method_hardening_audit.*`.
- Supplementary Figure S8: P/MSP contribution, redundancy and runtime audit, separating global biochemical summaries from positionalized property pooling while reporting P/MSP association and extraction cost. Source scripts: `info/scripts/run_p_msp_contribution_audit.py`, `info/scripts/run_property_redundancy_and_runtime_audit.py`, and `info/scripts/generate_supp_fig_s8_redundancy_runtime_audit.py`. Asset: `paper/figures/supp_fig_s8_redundancy_runtime_audit.*`.
- Supplementary Figure S9: P/MSP relation audit, combining CCA and a grouped correlation heatmap to summarize shared latent structure and redundancy. Source script: `info/scripts/generate_supp_fig_s9_p_msp_relation_audit.py`. Asset: `paper/figures/supp_fig_s9_p_msp_relation_audit.*`.
- Supplementary Figure S10: CAMI II marine subset probe, testing whether CK4P-MSP perturbation-stability trends extend beyond CAMI_TOY_low in an external anonymous-read metagenomic short-read source without reconstructed read-level taxonomic labels in this lightweight analysis. Source scripts: `info/scripts/run_cami2_marine_lightweight_probe.py` and `info/scripts/generate_supp_fig_s10_cami2_marine_probe.py`. Asset: `paper/figures/supp_fig_s10_cami2_marine_probe.*`.

## Tables

- Table 1: Representation families. Source script: `info/scripts/generate_nature_main_tables.py`. Asset: `paper/tables/nature_table1_representation_families.*`.
- Table 2: Data layers, scale and perturbation design. Source files: `info/paper/dataset_scale_inventory.md` and paper-level table update. Asset: `paper/tables/nature_table2_data_layers.*`.
- Table 3: Compact main-method metrics. Source script: `info/scripts/generate_nature_main_tables.py`. Asset: `paper/tables/nature_table3_compact_main_method.*`.
- Table 4: Local mutation sensitivity metrics. Source script: `info/scripts/generate_nature_main_tables.py`. Asset: `paper/tables/nature_table4_local_mutation_sensitivity.*`.
- Table 5: Boundary and mechanism summary. Source script: `info/scripts/generate_nature_main_tables.py`. Asset: `paper/tables/nature_table5_boundary_summary.*`.
- Supplementary Table S10 source data: CAMI II marine subset stability source table for Supplementary Figure S10. Source script: `info/scripts/generate_supp_fig_s10_cami2_marine_probe.py`. Asset: `paper/tables/supp_table_s10_cami2_marine_probe_source.csv`.
