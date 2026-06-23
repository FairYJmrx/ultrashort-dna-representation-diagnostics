# Ultra-short DNA Read Representation Diagnostics, Clean Release

This branch is a clean release snapshot for the final manuscript. It contains the scripts, lightweight input data, summary results, figures, manuscript tables, final manuscript files and audit reports used by the submitted stage-3 manuscript.

## Scientific Scope

The project is a representation-diagnostics study, not a clinical diagnostic validation. The final claim is deliberately bounded: canonical k-mer, alignment and database evidence remain necessary for exact identity and functional calls, while compact biochemical and position-aware property summaries supply perturbation-stable auxiliary evidence. Full position matrices are retained only as lightweight upper-bound diagnostics, and CSP is retained as a spaced-seed boundary control.

## What Is Included

- Core source code under `src/`.
- Final experiment and manuscript scripts under `scripts/`.
- Lightweight toy data, WGS-slice manifests/reads and the CAMI_TOY_low labelled subset under `data/`.
- Final summary result CSV/JSON/Markdown files under `results/`.
- Final manuscript files, selected final tables and selected final figures under `manuscript/`.
- The one-stop provenance map under `docs/final_release_provenance_map.md` and audit reports under `results/audits/`.

## What Is Excluded

Historical `results/runs` outputs, smoke runs, old parameter-sensitivity result tables, render intermediates, local virtual environments, download fragments, full CAMI archives, ART FASTQ/SAM outputs and large paired-read intermediates are excluded. The final manuscript uses `results/stage3/spaced_pattern_sanity` for seed-layout claims. Older parameter grids are documented only in audit reports.

## Main Reproduction Path

```powershell
.\.venv\Scripts\python.exe scripts\run_stage2_representation_grid.py
.\.venv\Scripts\python.exe scripts\run_stage2_csp_ablation.py
.\.venv\Scripts\python.exe scripts\run_stage2_attention_breakpoint.py
.\.venv\Scripts\python.exe scripts\run_stage2_arg_snp_boundary.py
.\.venv\Scripts\python.exe scripts\run_stage3_compact_baselines.py
.\.venv\Scripts\python.exe scripts\run_stage3_art_generate_and_evaluate.py
.\.venv\Scripts\python.exe scripts\summarize_stage3_art_quality.py
.\.venv\Scripts\python.exe scripts\run_stage3_cami_probe.py
.\.venv\Scripts\python.exe scripts\run_position_property_controlled_tasks.py --output-dir results/stage3/fullmatrix_property_contribution_controlled --representations ckmer4_property_multiscale_mean_l2,one_hot,property_channels,base_property,rope_onehot,rope_property,ckmer5_count_l2,kmer_property --lengths 69,100 --conditions clean,N_3pct
.\.venv\Scripts\python.exe scripts\run_stage3_art_validation.py --reads-csv results/stage3/art_illumina/art_paired_reads.csv --output-dir results/stage3/art_fullmatrix_property_contribution --lengths 69,100 --representations ckmer5_count_l2,ckmer4_property_multiscale_mean_l2,one_hot,property_channels,base_property,rope_onehot,rope_property,kmer_property --max-retrieval-pairs 100
.\.venv\Scripts\python.exe scripts\run_stage3_cami_probe.py --reads-csv data/stage3/cami/cami_toy_low_subset_smoke.csv --output-dir results/stage3/cami_fullmatrix_property_contribution --lengths 69,100 --conditions clean,N_3pct --representations ckmer5_count_l2,ckmer4_property_multiscale_mean_l2,one_hot,property_channels,base_property,rope_onehot,rope_property,kmer_property --target-label tax_552396 --max-per-class 30
.\.venv\Scripts\python.exe scripts\run_spaced_pattern_sanity.py --skip-readout --max-paired-reads 240 --max-clean-per-length 480
.\.venv\Scripts\python.exe scripts\generate_stage3_bootstrap_ci.py
.\.venv\Scripts\python.exe scripts\generate_fullmatrix_property_contribution_ci.py
.\.venv\Scripts\python.exe scripts\generate_stage3_manuscript_assets_v2.py
.\.venv\Scripts\python.exe scripts\audit_result_inventory.py
.\.venv\Scripts\python.exe scripts\audit_final_provenance.py
.\.venv\Scripts\python.exe scripts\finalize_stage3_manuscript_v5.py
```

The final files are `manuscript/final_manuscript.md` and `manuscript/final_manuscript.docx`.
