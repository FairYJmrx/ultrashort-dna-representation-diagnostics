# Stage 3 Submission Metadata and Reproducibility Checklist

Generated: 2026-06-23

## Historical manuscript files

Former stage-3 Markdown and Word files are retained under `manuscript/` for
provenance only. The submission source of truth is now
`paper_latex/main.tex`; see `docs/manuscript_source_of_truth.md`.

## Current repository state

- Repository URL currently written in the manuscript: `https://github.com/FairYJmrx/ultrashort-dna-representation-diagnostics`
- Current local HEAD: `2b2bffc00dd7ca5ebe16b16e9ac95f0483fc095e`
- Important caveat: this is not yet a final submission hash, because the working tree contains many uncommitted stage-2/stage-3 files, generated outputs and archives. Before submission, freeze the repository, commit the final source/result/manuscript package, and replace the manuscript's provisional hash with the final clean commit hash or repository DOI.

## One-command-style reproduction order

Run from the repository root after installing `requirements.txt`.

```powershell
& .\.venv\Scripts\python.exe scripts\run_stage3_compact_baselines.py
& .\.venv\Scripts\python.exe scripts\run_stage3_art_generate_and_evaluate.py
& .\.venv\Scripts\python.exe scripts\summarize_stage3_art_quality.py
& .\.venv\Scripts\python.exe scripts\run_stage3_cami_probe.py --reads-csv data\stage3\cami\cami_toy_low_subset_reads_expanded.csv --output-dir results\stage3\cami_probe_expanded --lengths 69,75,100 --conditions clean,N_3pct,substitution_1pct --classifiers nearest_centroid,logistic,mlp --target-label 562
& .\.venv\Scripts\python.exe scripts\generate_stage3_bootstrap_ci.py --n-boot 2000 --seed 20260623
& .\.venv\Scripts\python.exe scripts\generate_stage3_manuscript_assets.py
& .\.venv\Scripts\python.exe scripts\build_stage3_manuscript_v4.py
& .\.venv\Scripts\python.exe scripts\polish_stage3_manuscript_v4.py
& .\.venv\Scripts\python.exe scripts\finalize_stage3_manuscript_v4.py
```

The CAMI command assumes the lightweight labelled subset already exists. If it must be regenerated, first run `scripts\inspect_stage3_cami_remote_tar.py` and `scripts\prepare_stage3_cami_toy_low_subset.py` with the documented remote-prefix extraction settings.

## Randomness and runtime policy

- Random seeds are fixed in the stage-2/stage-3 scripts.
- Neural probes use deterministic seeds and CPU execution.
- The accepted runtime policy for long experiments is up to 1 hour by default; if progress is clear at the limit, extend rather than terminate.
- Stage-3 CI generation is lightweight and used `--seed 20260623`.

## Author and submission metadata to finalize

- Author name: MEI Ruixiang.
- Affiliation: to be provided by the user/institution.
- Corresponding author: to be decided with the supervising group. If the advisor supervises, guarantees the work and will handle journal communication, listing the advisor as corresponding author is usually appropriate; otherwise use the responsible author agreed by the group.
- Email: to be provided.
- ORCID: optional but recommended if available.
- Author contributions: current placeholder is conception, implementation, analysis and drafting by MEI Ruixiang; supervisory, funding, data-resource or clinical-advisory contributions must be added accurately.
- Funding: to be provided, or state no specific funding if true.
- Competing interests: current placeholder is none declared; must be confirmed before submission.
- Ethics: current placeholder is not applicable for controlled simulated reads and public benchmark data; confirm that no restricted patient data are included.

## Claim boundary to preserve

Use this sentence as the fixed boundary statement:

> CSP provides compact perturbation-stable auxiliary evidence, whereas canonical k-mer/alignment/database evidence remains necessary for exact identity and functional calls.

Avoid claiming:

- CSP improves clinical species-identification accuracy.
- CSP improves ARG allele or resistance SNP calling.
- CAMI_TOY_low is a full CAMI challenge benchmark.
- Bootstrap CIs estimate clinical sample-level uncertainty.
- The current local HEAD is the final archived submission hash before a clean commit/archive is made.
