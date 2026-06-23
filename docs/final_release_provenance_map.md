# Final Release Provenance Map

Purpose: one-stop map from revised manuscript claims to scripts, result files, tables, figures and audit reports. This map reflects the post-CSP revision in which the main story is compact biochemical and position-aware representation diagnostics. It deliberately does not add a third neural baseline family.

Working-tree source commit at the time of this map: 2b2bffc00dd7ca5ebe16b16e9ac95f0483fc095e. The clean release snapshot is maintained on the local and remote `release` branch; verify the current tip with `git rev-parse release` or `git rev-parse origin/release`.

## Quick Entry Points

- Final manuscript: manuscript/final_manuscript.md and manuscript/final_manuscript.docx.
- Main planning ledger: POSITION_PROPERTY_REVISION_TASKS.md.
- Release file manifest: RELEASE_MANIFEST.md in the clean release copy.
- Result inventory audit: results/audits/result_inventory/final_result_source_analysis.md.
- Final provenance audit: results/audits/final_provenance/final_provenance_audit.md.
- Machine-readable result/script map: results/audits/final_provenance/final_result_script_map.csv.

## Important Provenance Decisions

- CSP and S0246 are no longer the central method. They are retained as spaced-seed mechanism and sensitivity controls.
- The old deterministic neural-compatibility outputs are historical diagnostics, not final evidence, and are excluded from the revised clean-release evidence set.
- Full-matrix position encodings are lightweight upper-bound diagnostics for position readability and P-versus-non-P semantics, not the primary method.
- Accuracy and macro-F1 are shallow readout probes. They are not clinical classifier endpoints.

## Final Manuscript Build Chain

1. scripts/run_stage3_compact_baselines.py and the revised position-property runs generate compact representation stability/readout summaries.
2. scripts/run_stage3_art_validation.py evaluates compact and full-matrix representations on normalized ART paired reads where available.
3. scripts/run_stage3_cami_probe.py evaluates lightweight CAMI target/background and label readout probes.
4. scripts/run_position_property_controlled_tasks.py generates controlled order/position screens for compact and full-matrix diagnostics.
5. scripts/generate_stage3_bootstrap_ci.py generates legacy stage-3 analysis-cell CI summaries.
6. scripts/generate_fullmatrix_property_contribution_ci.py generates CI tables for P-versus-non-P full-matrix ablations.
7. scripts/generate_stage3_manuscript_assets_v2.py regenerates Figure 1 assets.
8. scripts/audit_result_inventory.py and scripts/audit_final_provenance.py regenerate provenance audits.
9. scripts/finalize_stage3_manuscript_v5.py builds stage3_manuscript_v5.* and copies them to final_manuscript.*.

## Result-to-Script Map

| Evidence block | Status | Generator scripts | Primary outputs | Manuscript use | Clean release policy |
|---|---|---|---|---|---|
| Stage-2 WGS-slice mechanism grid | final boundary evidence | scripts/run_stage2_representation_grid.py | results/stage2/representation_grid/stability_grid.csv; results/stage2/representation_grid/readout_grid.csv; results/stage2/representation_grid/stage2_representation_grid_run.json | historical WGS mechanism context and boundary checks | include selected summaries; exclude generated read intermediates |
| Stage-2 CSP component ablation | final boundary evidence | scripts/run_stage2_csp_ablation.py | results/stage2/csp_ablation/csp_ablation_metrics.csv; results/stage2/csp_ablation/csp_ablation_deltas.csv; results/stage2/csp_ablation/csp_ablation_run.json | CSP mechanism boundary, not primary method | include selected summaries |
| Stage-2 attention/context diagnostic | final boundary evidence | scripts/run_stage2_attention_breakpoint.py | results/stage2/attention_breakpoint/attention_breakpoint_results.csv; results/stage2/attention_breakpoint/attention_breakpoint_change_points.csv; results/stage2/attention_breakpoint/attention_breakpoint_run.json | read-length/context visibility limitation | include selected summaries; exclude generated reads |
| Stage-2 ARG/SNP boundary probes | final boundary evidence | scripts/run_stage2_arg_snp_boundary.py | results/stage2/arg_snp_boundary/arg_snp_stability.csv; results/stage2/arg_snp_boundary/arg_snp_readout.csv; results/stage2/arg_snp_boundary/arg_snp_boundary_run.json | limitation that stability is not allele/SNP equivalence | include selected summaries; exclude generated reads |
| Stage-2 deterministic neural compatibility | historical diagnostic only | scripts/run_stage2_neural_compatibility.py | results/stage2/neural_compatibility/* | not used in revised final manuscript | exclude from clean final evidence bundle unless archived separately |
| Compact CK4/CK5 + property ablation | final main evidence | scripts/run_stage3_compact_baselines.py | results/stage3/position_property_ablation/compact_baseline_stability.csv; results/stage3/position_property_ablation/compact_baseline_readout.csv; results/stage3/position_property_ablation/stage3_compact_baselines_run.json | main CK4+P and multi-scale property stability/readout results | include summaries and run JSON; exclude generated reads |
| Compact ART validation | final main evidence | scripts/run_stage3_art_validation.py | results/stage3/art_ck4p_position_ablation/art_stability_metrics.csv; results/stage3/art_ck4p_position_ablation/art_validation_summary.md; results/stage3/art_ck4p_position_ablation/stage3_art_validation_run.json | ART stability for compact position-aware property variants | include stability summaries/manifests |
| Compact CAMI readout | final main evidence | scripts/run_stage3_cami_probe.py | results/stage3/cami_ck4p_position_ablation_fast/cami_probe_readout.csv; results/stage3/cami_ck4p_position_ablation_fast/cami_probe_summary.md; results/stage3/cami_ck4p_position_ablation_fast/stage3_cami_probe_run.json | CAMI target/background and label-probe compact readout | include readout summary; exclude generated CAMI read intermediates |
| Full-matrix property contribution, controlled | final upper-bound diagnostic | scripts/run_position_property_controlled_tasks.py | results/stage3/fullmatrix_property_contribution_controlled/position_property_controlled_results.csv; results/stage3/fullmatrix_property_contribution_controlled/position_property_controlled_run.json | tests whether P improves full-matrix position/order readout | include lightweight outputs |
| Full-matrix property contribution, ART | final upper-bound diagnostic | scripts/run_stage3_art_validation.py | results/stage3/art_fullmatrix_property_contribution/art_stability_metrics.csv; results/stage3/art_fullmatrix_property_contribution/art_validation_summary.md; results/stage3/art_fullmatrix_property_contribution/stage3_art_validation_run.json | P-versus-non-P ART stability deltas | include stability summary |
| Full-matrix property contribution, CAMI | final upper-bound diagnostic | scripts/run_stage3_cami_probe.py | results/stage3/cami_fullmatrix_property_contribution/cami_probe_readout.csv; results/stage3/cami_fullmatrix_property_contribution/cami_probe_summary.md; results/stage3/cami_fullmatrix_property_contribution/stage3_cami_probe_run.json | P-versus-non-P CAMI target/background deltas | include readout summary; exclude generated reads |
| Full-matrix property contribution CI | final uncertainty evidence | scripts/generate_fullmatrix_property_contribution_ci.py | results/stage3/fullmatrix_property_contribution_ci/*.csv; results/stage3/fullmatrix_property_contribution_ci/fullmatrix_property_contribution_ci_summary.md | CI statements in Abstract and Results | include all CI outputs and manuscript tables |
| Stage-3 legacy/bootstrap CI | final uncertainty evidence | scripts/generate_stage3_bootstrap_ci.py | results/stage3/bootstrap_ci/*.csv; results/stage3/bootstrap_ci/stage3_bootstrap_ci_summary.md | uncertainty summaries for retained stage-3 analyses | include all CI summaries |
| Focused spaced-pattern sanity | final CSP boundary evidence | scripts/run_spaced_pattern_sanity.py | results/stage3/spaced_pattern_sanity/spaced_pattern_sanity_stability.csv; results/stage3/spaced_pattern_sanity/spaced_pattern_sanity_cardinality_summary.csv; results/stage3/spaced_pattern_sanity/spaced_pattern_sanity_best_four_position.csv | shows S0246 is not a universal optimized seed | include all focused sanity outputs |
| Manuscript Figure 1 | final figure | scripts/generate_stage3_manuscript_assets_v2.py | manuscript/figures/stage3_fig_layered_evidence_architecture.png; .svg; .pdf; .tiff | layered evidence architecture | include PNG/SVG/PDF; TIFF optional |
| Project-level audits | audit evidence | scripts/audit_result_inventory.py; scripts/audit_final_provenance.py; scripts/prepare_release_repository.py | results/audits/result_inventory/*; results/audits/final_provenance/*; docs/final_release_provenance_map.md | release integrity and claim provenance | include audit reports and maps |

## Deprecated or Excluded Result Families

| Path family | Reason | Where documented |
|---|---|---|
| results/runs/* | Stage-1 exploratory and historical diagnostics, not final evidence. | results/audits/result_inventory/final_result_source_analysis.md |
| results/stage2/parameter_sensitivity/* | Real old parameter grid, superseded for final seed-layout claims. | results/audits/result_inventory/parameter_grid_comparison.csv |
| results/runs/parameter_sensitivity/* | Real later grid with different coverage, not the source of final seed claims. | results/audits/result_inventory/parameter_grid_comparison.csv |
| results/stage2/neural_compatibility/* | Historical deterministic diagnostic; revised manuscript does not add neural baseline experiments. | results/audits/result_inventory/final_result_source_analysis.md |
| ART FASTQ/SAM, CAMI .part caches, *_reads.csv intermediates | Bulky reproducible intermediates, excluded from clean release. | RELEASE_MANIFEST.md; scripts/prepare_release_repository.py |

## How Codex Should Use This Map

1. Start with the row matching the manuscript claim.
2. Read primary outputs before reading scripts.
3. Use CI summaries for uncertainty wording.
4. Use final_result_script_map.csv for machine-readable provenance.
5. Do not promote historical neural compatibility, old parameter grids, or full-matrix screens into primary method claims.
