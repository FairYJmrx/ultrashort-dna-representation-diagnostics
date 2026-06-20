# Ultra-short DNA Read Representation Diagnostics

This repository contains the `信息学` subproject for controlled DNA-read representation diagnostics under mNGS-like short-read constraints.

The scientific goal is **not** to prove that one representation universally wins species classification. The goal is to diagnose what each representation preserves, stabilizes, compresses or loses when reads are 69-150 bp long, with a PE150 proxy included as a paired-end-style reference point.

## Current Manuscript Position

The current paper claim is:

> Canonical k-mers provide high-resolution identity evidence, whereas canonical spaced-property encoding (`cspaced_property_l2`, abbreviated CSP) provides compact, strand-friendly and perturbation-stable auxiliary evidence for ultra-short mNGS-like reads. Hybrid or layered evidence is the practical route.

Accuracy and macro-F1 are treated as readout probes, not clinical mNGS performance estimates.

## Main Representation Families

- `kmer*_count_l2`: contiguous k-mer count vectors.
- `ckmer*_count_l2`: reverse-complement canonical k-mer count vectors.
- `cspaced_count_l2`: canonical spaced-seed count vectors.
- `cspaced_property_l2`: canonical spaced-seed counts plus compact DNA property summaries.
- `property_channels`: per-position biochemical/numeric channels.
- `spaced_kmer_phase`: spaced-token property representation with explicit phase terms.
- `rope_property`: DNA property channels with RoPE-like positional rotation.

## Key Evidence

- Perturbation stability: CSP was the top clean-perturbed stability representation in 42/42 WGS-slice length-by-perturbation settings.
- Hospital-like short reads: the clearest CSP advantage occurs around 69/75 bp under N masking, local mismatch and combined perturbation.
- CSP ablation: the full property block improves stability over canonical spaced seed counts; hydrogen-bond and entropy summaries are the strongest singleton additions.
- Readout probes: CSP does not universally win classification; canonical k-mer remains a strong high-resolution identity baseline.
- Neural compatibility: deterministic local MLP/CNN/tiny Transformer probes show task-dependent model fit, not universal neural superiority.
- Read length and context: the 125-150 bp transition is position-dependent because short reads can remove entire motif-pair relations.
- Parameter sensitivity: k and spaced-seed pattern choices affect classification probes, so claims should not depend on a single k value.
- ARG/SNP boundary: CSP can preserve perturbed feature proximity, but allele/SNP decisions still require exact sequence, alignment or curated database evidence.

## Important Outputs

- Stage-2 manuscript source: `manuscript/stage2_manuscript_v2.md`
- Stage-2 Word draft: `manuscript/stage2_manuscript_v2.docx`
- Stage-2 PDF: `manuscript/stage2_manuscript_v2.pdf`
- Evidence synthesis: `results/stage2/publication_assets/stage2_evidence_summary.md`
- Reviewer self-audit: `manuscript/stage2_reviewer_self_audit.md`
- Completion report: `docs/stage2_completion_report.md`
- Formal references: `references/references.bib`
- Publication figures: `results/stage2/publication_assets/figures/stage2_fig_*.png`
- Publication tables: `results/stage2/publication_assets/tables/stage2_table_*.md`

## Reproducibility

Create an environment:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Core rerun order:

```powershell
.\.venv\Scripts\python.exe scripts\prepare_close_relative_genomes.py
.\.venv\Scripts\python.exe scripts\make_close_relative_reads.py
.\.venv\Scripts\python.exe scripts\run_stage2_representation_grid.py
.\.venv\Scripts\python.exe scripts\run_stage2_csp_ablation.py
.\.venv\Scripts\python.exe scripts\run_stage2_attention_breakpoint.py
.\.venv\Scripts\python.exe scripts\run_stage2_arg_snp_boundary.py
.\.venv\Scripts\python.exe scripts\run_parameter_sensitivity.py --input results\stage2\representation_grid\stage2_derived_reads.csv --output-dir results\stage2\parameter_sensitivity
.\.venv\Scripts\python.exe scripts\run_stage2_neural_compatibility.py --resume
.\.venv\Scripts\python.exe scripts\generate_stage2_publication_assets.py
.\.venv\Scripts\python.exe scripts\build_stage2_manuscript.py
.\.venv\Scripts\python.exe scripts\build_stage2_pdf_manuscript.py
```

## Data Policy

This repository should include lightweight generated reads, manifests, scripts, figures, and result summaries. It should not include local virtual environments or bulky downloaded reference FASTA files. Reference genomes can be regenerated from accession manifests.

The current local close-relative panel contains 21 genomes from six clinically relevant genera. It is a lightweight stress test, not a universal clinical mNGS benchmark.

Large stage-2 derived-read CSV files are intentionally ignored by Git and kept local. Summary tables, figures, scripts and manuscript files are tracked.

## Rendering Note

LibreOffice is currently broken on this machine with a `bootstrap.ini` startup error, so DOCX visual rendering could not be completed. The manuscript PDF is compiled with XeLaTeX and checked through rendered PNG pages; treat the PDF as the visually verified artifact and the DOCX as an editable draft.

## Server-scale Follow-up

The local results are sufficient for a representation-diagnostics draft, but stronger claims require:

- larger close-relative panels with many strains per genus;
- realistic FASTQ simulation with quality decay, adapters, host/background mixtures, and abundance variation;
- Kraken2/Centrifuge/Kaiju clean-noisy-OOD audits;
- AMR-gene tasks before resistance-detection claims.
