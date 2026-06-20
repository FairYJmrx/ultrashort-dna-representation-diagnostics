# Stage-2 Publication Evidence Summary
This file is generated from stage-2 experiment CSV files. It separates hard evidence from claims that should remain in Discussion or Future Work.
## Hard Claims Supported by Local Experiments
- CSP was the top clean-perturbed stability representation in 42/42 length-by-perturbation settings in the WGS-slice grid.
- In 69/75 bp hospital-like settings, CSP consistently reduced L2 drift under N masking, substitution, local mismatch and combined perturbation relative to canonical k-mer and canonical spaced seed baselines.
- Lightweight readout probes did not show a universal classification win for CSP. Near-species identity remains task- and parameter-dependent, and canonical k-mer is a strong high-resolution baseline.
- CSP component ablation supports that the property block adds stability over canonical spaced seed counts; the full block is more defensible than any single biochemical summary alone.
- Attention-context diagnostics show that the 125-150 bp transition is not a single magic read length: the breakpoint shifts with motif position and paired-context visibility.
- Deterministic neural compatibility probes (252 trained combinations) showed task-dependent model fit: no small CNN or tiny Transformer universally dominated, and CSP was most defensible as a compact tabular auxiliary input.
- ARG/SNP boundary probes show a sharp distinction between stability and identity. CSP preserves perturbed feature proximity, but exact k-mer evidence dominates synthetic ARG-family/allele readouts, and SNP decisions cannot be assigned to CSP alone.

## Claims to Downgrade to Discussion/Future Work
- Transformer superiority, embedding-layer behavior at clinical scale and clinical mNGS accuracy are not proven by these local experiments.
- CSP-alone species identification, ARG allele calling, resistance SNP interpretation, plasmid linkage and gene-context inference are not supported as stand-alone claims.
- Kraken2/Centrifuge/Kaiju pipeline comparisons, genome-held-out panels, real FASTQ quality profiles and CARD/ResFinder/AMRFinderPlus marker tasks remain server-stage or future work.

## Generated Tables
- `results\stage2\publication_assets\tables\stage2_table_arg_snp_best_readout.md`
- `results\stage2\publication_assets\tables\stage2_table_arg_snp_best_stability.md`
- `results\stage2\publication_assets\tables\stage2_table_arg_snp_readout_aggregate.md`
- `results\stage2\publication_assets\tables\stage2_table_attention_best_readout.md`
- `results\stage2\publication_assets\tables\stage2_table_attention_change_points.md`
- `results\stage2\publication_assets\tables\stage2_table_best_readout.md`
- `results\stage2\publication_assets\tables\stage2_table_best_stability.md`
- `results\stage2\publication_assets\tables\stage2_table_csp_component_singletons.md`
- `results\stage2\publication_assets\tables\stage2_table_csp_full_ablation.md`
- `results\stage2\publication_assets\tables\stage2_table_hospital_69_75_focus.md`
- `results\stage2\publication_assets\tables\stage2_table_neural_compatibility_aggregate.md`
- `results\stage2\publication_assets\tables\stage2_table_neural_compatibility_drop.md`
- `results\stage2\publication_assets\tables\stage2_table_parameter_readout_best.md`
- `results\stage2\publication_assets\tables\stage2_table_parameter_stability_best.md`
- `results\stage2\publication_assets\tables\stage2_table_readout_aggregate.md`
- `results\stage2\publication_assets\tables\stage2_table_stability_gain_summary.md`

## Generated Figures
- `results\stage2\publication_assets\figures\stage2_fig_arg_snp_readout.png`
- `results\stage2\publication_assets\figures\stage2_fig_attention_breakpoints.png`
- `results\stage2\publication_assets\figures\stage2_fig_attention_f1_breakpoints.png`
- `results\stage2\publication_assets\figures\stage2_fig_csp_singleton_ablation.png`
- `results\stage2\publication_assets\figures\stage2_fig_hospital_69_75_l2.png`
- `results\stage2\publication_assets\figures\stage2_fig_neural_compatibility.png`
- `results\stage2\publication_assets\figures\stage2_fig_readout_aggregate.png`
- `results\stage2\publication_assets\figures\stage2_fig_stability_grid.png`
