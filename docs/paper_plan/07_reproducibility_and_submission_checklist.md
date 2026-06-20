# 07 Reproducibility and Submission Checklist

## 1. Current Manuscript Stage

Completed:

- Stage 1 initial draft: `manuscript/stage1_initial_draft.md`
- Stage 2 reviewer audit: `manuscript/stage2_reviewer_audit.md`
- Stage 3 final manuscript: `manuscript/stage3_final_manuscript.md`
- Chinese internal summary: `manuscript/stage3_中文项目总结.md`

Current positioning:

> Lightweight representation diagnostics and canonical spaced-property feature design for ultra-short DNA reads.

Not positioned as:

> Clinically validated mNGS species identification or AMR detection.

## 2. Key Reproducibility Commands

Run from:

```powershell
cd D:\AI-NGS\信息学
$env:OPENBLAS_NUM_THREADS='1'
$env:OMP_NUM_THREADS='1'
$env:MKL_NUM_THREADS='1'
```

Generate hardened synthetic tasks:

```powershell
.\.venv\Scripts\python.exe scripts\make_hardened_reads.py --output data\toy_reads\toy_hardened_tasks.csv --lengths 69,75,100 --conditions clean,substitution_1pct,N_3pct,N_cluster_5pct,reverse_complement --reads-per-class 80 --seed 31
```

Generate local WGS slices:

```powershell
.\.venv\Scripts\python.exe scripts\make_genome_slice_reads.py --output data\real_slices\local_wgs_slices.csv --lengths 69,75,100,150 --conditions clean,substitution_1pct,N_3pct,reverse_complement --reads-per-genome 120 --max-bases 500000 --seed 41
```

Run spaced-hybrid downstream diagnostics:

```powershell
.\.venv\Scripts\python.exe scripts\run_lightweight_downstream_tasks.py --input data\toy_reads\toy_downstream_stress.csv --output-dir results\runs\spaced_hybrid_smoke75 --representations spaced_count_l2,cspaced_count_l2,cspaced_property_l2,ckmer5_count_l2,ckmer7_tfidf_l2,spaced_kmer_phase --lengths 75 --paired-conditions substitution_5pct,N_cluster_5pct,indel_stress --tasks paired_retrieval,rc_consistency,contamination_detection,ood_rejection --known-labels GC_rich,AT_rich
```

Run hardened classification:

```powershell
.\.venv\Scripts\python.exe scripts\run_representation_classification.py --input data\toy_reads\toy_hardened_tasks.csv --output-dir results\runs\hardened_task_classification75_trainonly --representations kmer5_count_l2,ckmer5_count_l2,kmer7_tfidf_l2,ckmer7_tfidf_l2,one_hot,property_channels,spaced_kmer_phase,codon_frame_channels,rope_property,cspaced_count_l2,cspaced_property_l2 --lengths 75 --conditions clean,N_3pct,N_cluster_5pct --tasks same_spectrum_order,motif_jitter_position --classifiers nearest_centroid,knn_3,logistic_regression,mlp_small --seed 17
```

Run local WGS-slice classification:

```powershell
.\.venv\Scripts\python.exe scripts\run_representation_classification.py --input data\real_slices\local_wgs_slices.csv --output-dir results\runs\real_wgs_slice_classification75_trainonly --representations kmer5_count_l2,ckmer5_count_l2,kmer7_tfidf_l2,ckmer7_tfidf_l2,one_hot,property_channels,spaced_kmer_phase,codon_frame_channels,rope_property,cspaced_count_l2,cspaced_property_l2 --lengths 75 --conditions clean,substitution_1pct,N_3pct --tasks real_genome_slice --classifiers nearest_centroid,knn_3,logistic_regression,mlp_small --seed 19
```

Generate paper result synthesis:

```powershell
.\.venv\Scripts\python.exe scripts\generate_paper_results.py
```

## 3. Result Files Used by the Final Manuscript

- `results/runs/paper_level_result_synthesis.md`
- `results/runs/spaced_hybrid_smoke75/lightweight_downstream_results.csv`
- `results/runs/hardened_task_classification75_trainonly/classification_results.csv`
- `results/runs/real_wgs_slice_classification75_trainonly/classification_results.csv`
- `results/runs/real_wgs_slice_length_curve_trainonly/classification_results.csv`
- `results/runs/hardened_task_cv75_trainonly/classification_results.csv`
- `results/runs/real_wgs_slice_cv75_trainonly/classification_results.csv`
- `results/figures/fig_qc_auroc.png`
- `results/figures/fig_rc_consistency.png`
- `results/figures/fig_real_wgs_75bp.png`
- `results/figures/fig_length_curve.png`

## 4. Submission-Blocking Gaps

For a stronger Q2-or-above submission, add:

1. More real reference genomes and near-neighbor groups.
2. Host/background reads and abundance variation.
3. Kraken2/Centrifuge/traditional mapper baselines.
4. Proper tiny CNN and tiny attention baselines.
5. Multiple random seeds for all key tasks.
6. Formal references in journal style.
7. Optional: convert the manuscript into LaTeX or Word format.

## 5. Claim Boundary to Preserve

Allowed:

- "representation diagnostics"
- "lightweight benchmark"
- "QC-like perturbation detection"
- "local WGS-slice sanity benchmark"
- "canonical k-mer remains strong"

Avoid:

- "clinical mNGS validated"
- "species identification solved"
- "AMR detection improved"
- "Transformer superiority proved"
- "new representation replaces canonical k-mer"

