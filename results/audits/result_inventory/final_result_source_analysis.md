# Final Result Source Analysis

This audit is a project-level result inventory. It separates final evidence, historical exploratory output, superseded parameter grids, smoke runs and generated audit outputs before the final manuscript is regenerated.

## Main conclusion

The 0-2-5-7 and 0-3-5-8 patterns were not fabricated. They came from the real stage-2 parameter-sensitivity grid, which scanned five four-position layouts. The later results/runs parameter grid scanned only three four-position layouts, so mixing those two grids in the manuscript would create a provenance problem. The final manuscript should therefore use the focused stage-3 spaced-pattern sanity run for seed-layout statements and mark both older parameter tables as deprecated for final claims.

Stage 1 corresponds to results/runs. Those outputs are historical exploration and early diagnostics, not the final evidence base. Stage 2 contains the main controlled mechanism grid, except its old parameter-sensitivity directory. Stage 3 contains external validation, bootstrap CIs and the final seed-layout sanity check.

## Stage/category counts

| stage_category                          | evidence_status              | clean_release_policy                |   directories |   csv_files |   csv_bytes |
|:----------------------------------------|:-----------------------------|:------------------------------------|--------------:|------------:|------------:|
| audit_container                         | container_directory          | container_only                      |             1 |           0 |           0 |
| audit_outputs                           | audit_evidence               | include                             |             2 |           8 |      146100 |
| results_container                       | container_directory          | container_only                      |             1 |           0 |           0 |
| stage2_container                        | container_directory          | container_only                      |             1 |           0 |           0 |
| stage2_main_mechanism_grid              | final_evidence_source        | include_selected                    |             4 |           8 |      914390 |
| stage2_publication_assets               | derived_final_tables_figures | include_selected_tables_figures     |             2 |           8 |       17026 |
| stage3_container                        | container_directory          | container_only                      |             1 |           2 |        4191 |
| stage3_external_validation              | final_evidence_source        | include                             |             1 |           4 |       15395 |
| stage3_external_validation              | final_evidence_source        | include_selected                    |             1 |           1 |       26551 |
| stage3_external_validation              | final_evidence_source        | include_summary_exclude_fastq_reads |             1 |           2 |       26357 |
| stage3_external_validation              | final_evidence_source        | include_summary_exclude_reads       |             2 |           3 |      514932 |
| stage3_fullmatrix_property_contribution | final_evidence_source        | include                             |             2 |           7 |       47665 |
| stage3_fullmatrix_property_contribution | final_evidence_source        | include_selected                    |             1 |           1 |        2793 |
| stage3_fullmatrix_property_contribution | final_evidence_source        | include_summary_exclude_reads       |             1 |           1 |       10299 |
| stage3_metadata                         | metadata                     | include_selected                    |            18 |          92 |    95693171 |
| stage3_position_property_revision       | final_evidence_source        | include_selected                    |             1 |           1 |        7582 |
| stage3_position_property_revision       | final_evidence_source        | include_summary_exclude_reads       |             2 |           4 |     2962727 |
| stage3_publication_assets               | derived_final_figures        | include_selected                    |             1 |           0 |           0 |
| stage3_spaced_pattern_sanity            | final_evidence_source        | include                             |             1 |           3 |       33127 |

## Parameter-grid comparison

| grid                                  | folder                               | run_json                                                            | patterns_from_stability_csv                                                                                     | lengths_from_stability_csv   | k_values_from_stability_csv   | conditions_from_stability_csv               |   n_stability_rows | readout_csv_exists   |   n_readout_rows | patterns_from_run_json                                                                                          | lengths_from_run_json   | classification_lengths_from_run_json   | k_values_from_run_json   | status_for_final_manuscript      |
|:--------------------------------------|:-------------------------------------|:--------------------------------------------------------------------|:----------------------------------------------------------------------------------------------------------------|:-----------------------------|:------------------------------|:--------------------------------------------|-------------------:|:---------------------|-----------------:|:----------------------------------------------------------------------------------------------------------------|:------------------------|:---------------------------------------|:-------------------------|:---------------------------------|
| stage2_parameter_sensitivity_old_grid | results/stage2/parameter_sensitivity |                                                                     |                                                                                                                 |                              |                               |                                             |                  0 | False                |                0 |                                                                                                                 |                         |                                        |                          | deprecated_for_final_seed_claims |
| runs_parameter_sensitivity_later_grid | results/runs/parameter_sensitivity   |                                                                     |                                                                                                                 |                              |                               |                                             |                  0 | False                |                0 |                                                                                                                 |                         |                                        |                          | deprecated_for_final_seed_claims |
| stage3_spaced_pattern_sanity_final    | results/stage3/spaced_pattern_sanity | results/stage3/spaced_pattern_sanity/spaced_pattern_sanity_run.json | 0-1-2,0-1-2-3,0-1-2-3-4,0-1-3-6,0-1-3-6-9,0-1-4-7,0-2-4,0-2-4-6,0-2-4-6-8,0-2-5-7,0-2-5-8,0-3-5-8,0-3-6,0-3-6-9 | 69,75                        |                               | N_3pct,local_mismatch_6bp,substitution_1pct |                168 | False                |                0 | 0-1-2,0-2-4,0-3-6,0-1-2-3,0-1-3-6,0-2-4-6,0-1-4-7,0-2-5-7,0-2-5-8,0-3-5-8,0-3-6-9,0-1-2-3-4,0-1-3-6-9,0-2-4-6-8 | 69,75                   |                                        |                          | final_seed_layout_sanity         |

## Final evidence directories selected for clean release

| dir                                                        | stage_category                          | evidence_status              | clean_release_policy                |   csv_files |   json_files |   md_files |   total_csv_bytes |
|:-----------------------------------------------------------|:----------------------------------------|:-----------------------------|:------------------------------------|------------:|-------------:|-----------:|------------------:|
| results/audits/final_provenance                            | audit_outputs                           | audit_evidence               | include                             |           4 |            0 |          1 |             18107 |
| results/audits/result_inventory                            | audit_outputs                           | audit_evidence               | include                             |           4 |            0 |          1 |            127993 |
| results/stage2/arg_snp_boundary                            | stage2_main_mechanism_grid              | final_evidence_source        | include_selected                    |           2 |            1 |          1 |            120036 |
| results/stage2/attention_breakpoint                        | stage2_main_mechanism_grid              | final_evidence_source        | include_selected                    |           2 |            1 |          1 |             58402 |
| results/stage2/csp_ablation                                | stage2_main_mechanism_grid              | final_evidence_source        | include_selected                    |           2 |            1 |          1 |            248676 |
| results/stage2/publication_assets                          | stage2_publication_assets               | derived_final_tables_figures | include_selected_tables_figures     |           0 |            0 |          0 |                 0 |
| results/stage2/representation_grid                         | stage2_main_mechanism_grid              | final_evidence_source        | include_selected                    |           2 |            1 |          1 |            487276 |
| results/stage3/art_ck4p_position_ablation                  | stage3_position_property_revision       | final_evidence_source        | include_selected                    |           1 |            1 |          1 |              7582 |
| results/stage3/art_fullmatrix_property_contribution        | stage3_fullmatrix_property_contribution | final_evidence_source        | include_selected                    |           1 |            1 |          1 |              2793 |
| results/stage3/art_illumina                                | stage3_external_validation              | final_evidence_source        | include_summary_exclude_fastq_reads |           2 |            1 |          1 |             26357 |
| results/stage3/art_quality_stratified                      | stage3_external_validation              | final_evidence_source        | include_selected                    |           1 |            1 |          1 |             26551 |
| results/stage3/bootstrap_ci                                | stage3_external_validation              | final_evidence_source        | include                             |           4 |            0 |          1 |             15395 |
| results/stage3/cami_ck4p_position_ablation_fast            | stage3_position_property_revision       | final_evidence_source        | include_summary_exclude_reads       |           1 |            1 |          1 |             52376 |
| results/stage3/cami_fullmatrix_property_contribution       | stage3_fullmatrix_property_contribution | final_evidence_source        | include_summary_exclude_reads       |           1 |            1 |          1 |             10299 |
| results/stage3/cami_probe_expanded                         | stage3_external_validation              | final_evidence_source        | include_summary_exclude_reads       |           1 |            1 |          1 |             48560 |
| results/stage3/compact_baselines                           | stage3_external_validation              | final_evidence_source        | include_summary_exclude_reads       |           2 |            1 |          2 |            466372 |
| results/stage3/fullmatrix_property_contribution_ci         | stage3_fullmatrix_property_contribution | final_evidence_source        | include                             |           6 |            0 |          1 |             13693 |
| results/stage3/fullmatrix_property_contribution_controlled | stage3_fullmatrix_property_contribution | final_evidence_source        | include                             |           1 |            1 |          0 |             33972 |
| results/stage3/position_property_ablation                  | stage3_position_property_revision       | final_evidence_source        | include_summary_exclude_reads       |           3 |            1 |          1 |           2910351 |
| results/stage3/spaced_pattern_sanity                       | stage3_spaced_pattern_sanity            | final_evidence_source        | include                             |           3 |            1 |          1 |             33127 |

## Deprecated result tables still present in the working project

No deprecated parameter tables were found in the working manuscript table directory.

## Audit interpretation rules

- Final manuscript tables must match their source CSVs through the manuscript table formatting path, not through ad hoc visual copying.
- The clean release should include final scripts, source summary CSVs, generated final tables, figures, manuscript builders and audit reports.
- The clean release should exclude bulk historical results/runs, smoke outputs, old parameter-sensitivity tables, full FASTQ/SAM files and large reproducible read intermediates.
- All known final manuscript pattern tokens are checked separately by audit_final_provenance.py.

## Inventory files generated

- `result_directory_inventory.csv`: directory-level counts, stage categories and clean-release policy.
- `run_json_configuration_inventory.csv`: JSON/run-configuration fields extracted from result files.
- `csv_schema_inventory.csv`: CSV row counts, columns and stage categories.
- `parameter_grid_comparison.csv`: side-by-side comparison of old stage-2, later results/runs and final stage-3 seed-layout grids.
