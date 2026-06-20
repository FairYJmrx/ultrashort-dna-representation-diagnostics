# Ultra-short DNA Read Representation Diagnostics

This repository contains a lightweight, reproducible subproject for comparing DNA-read representation schemes under mNGS-like short-read constraints.

The scientific goal is **not** to prove that one representation universally wins species classification. The goal is to diagnose what each representation preserves, stabilizes, compresses, or loses when reads are 69-150 bp long.

## Current Manuscript Position

The safest paper claim is:

> Canonical spaced-property encoding (`cspaced_property_l2` in code) is a compact, strand-friendly, perturbation-stable auxiliary representation. Canonical k-mer remains a strong close-relative classification baseline.

Accuracy and macro-F1 are treated as downstream probes, not clinical mNGS performance estimates.

## Main Representation Families

- `kmer*_count_l2`: contiguous k-mer count vectors.
- `ckmer*_count_l2`: reverse-complement canonical k-mer count vectors.
- `cspaced_count_l2`: canonical spaced-seed count vectors.
- `cspaced_property_l2`: canonical spaced-seed counts plus compact DNA property summaries.
- `property_channels`: per-position biochemical/numeric channels.
- `spaced_kmer_phase`: spaced-token property representation with explicit phase terms.
- `rope_property`: DNA property channels with RoPE-like positional rotation.

## Key Evidence

- Perturbation stability: adding property summaries to canonical spaced counts improves N-masking and substitution robustness.
- Strand consistency: canonicalization is the decisive component, not property summaries alone.
- Read length and context: 69/75/100/125/150/PE150 comparisons show that short reads can remove entire motif-pair relations.
- Close-relative stress test: canonical k-mer and canonical spaced variants remain strong baselines; new methods are complementary.
- Parameter sensitivity: k and spaced-seed pattern choices affect classification probes, so claims should not depend on a single k value.

## Important Outputs

- Final manuscript source: `manuscript/final_manuscript.md`
- Final Word draft: `manuscript/final_manuscript.docx`
- Evidence synthesis: `manuscript/publication_evidence_synthesis.md`
- Positioning policy: `manuscript/revision_positioning_and_evidence_policy.md`
- Server-scale follow-up plan: `manuscript/paper_scope_metrics_and_server_plan.md`
- Formal references: `references/references.bib`
- Publication figures: `results/figures/fig_publication_*.png`

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
.\.venv\Scripts\python.exe scripts\run_prior_ablation.py --input data\real_slices\close_relative_reads.csv --output-dir results\runs\prior_ablation_wgs_lengths
.\.venv\Scripts\python.exe scripts\run_attention_context_diagnostic.py
.\.venv\Scripts\python.exe scripts\run_parameter_sensitivity.py --k-values 4,5,6,7 --patterns 0-1-2-3,0-2-4-6,0-1-3-6 --max-paired-reads 120 --max-samples-per-group 80 --classification-lengths 75,150,300
.\.venv\Scripts\python.exe scripts\generate_publication_evidence.py
```

The final Word manuscript is generated with the bundled Codex document runtime:

```powershell
python scripts\build_final_manuscript.py
```

## Data Policy

This repository should include lightweight generated reads, manifests, scripts, figures, and result summaries. It should not include local virtual environments or bulky downloaded reference FASTA files. Reference genomes can be regenerated from accession manifests.

The current local close-relative panel contains 21 genomes from six clinically relevant genera. It is a lightweight stress test, not a universal clinical mNGS benchmark.

## Server-scale Follow-up

The local results are sufficient for a representation-diagnostics draft, but stronger claims require:

- larger close-relative panels with many strains per genus;
- realistic FASTQ simulation with quality decay, adapters, host/background mixtures, and abundance variation;
- tiny CNN and tiny Transformer comparisons under matched representation inputs;
- Kraken2/Centrifuge/Kaiju clean-noisy-OOD audits;
- AMR-gene tasks before resistance-detection claims.
