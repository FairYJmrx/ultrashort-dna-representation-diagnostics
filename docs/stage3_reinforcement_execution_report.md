# Stage 3 reinforcement experiments and manuscript revision report

Generated: 2026-06-22

## 1. Stage objective

This stage was designed to strengthen the manuscript as a controlled representation-diagnostics study rather than an end-to-end clinical mNGS classifier. The target claim is deliberately bounded:

- canonical k-mer provides high-resolution identity evidence;
- canonical spaced-property encoding (CSP, implemented as `cspaced_property_l2`) provides compact, strand-friendly, perturbation-stable and interpretable auxiliary evidence;
- hybrid or layered evidence is the more realistic route for short-read mNGS/ARG workflows.

The additional experiments were not added as defensive decorations. They close three reviewer-level gaps: whether CSP only wins because it is low-dimensional, whether hand-coded perturbations are too idealized, and whether the representation signals are still readable in an external metagenomic benchmark context.

## 2. Data-design rationale added to the manuscript

The manuscript now explains why controlled simulation is scientifically appropriate for this question:

1. The paper tests representation-level information preservation, not clinical sensitivity/specificity.
2. Real clinical mNGS often has sample-level truth but lacks read-level origin, exact sequencing-error source, mutation status and controlled read length.
3. WGS-derived reads provide controlled species origin, read length, perturbation and clean-perturbed pairing.
4. ART Illumina provides a field-standard sequencing-error profile to test whether the stability result is not an artifact of uniform substitutions/N/trim.
5. CAMI_TOY_low provides external read-level gold mapping for a lightweight benchmark probe.
6. Full clinical pipelines with host/background mixtures, abundance structure and database incompleteness remain future work.

## 3. Completed reinforcement experiments

### Experiment A: MinHash + EIIP compact baselines

Purpose: test whether CSP's stability can be explained away by generic compactness or generic biochemical numeric encoding.

Inputs:
- WGS-derived close-relative read grid.
- Read lengths: 69, 75, 100, 110, 125, 150 and PE150 proxy (300 bp).
- Perturbations: substitution, N masking, trim, substitution+N, short indel and local mismatch.

Representations:
- canonical 5-mer and 7-mer;
- canonical spaced count;
- CSP;
- canonical k-mer + CSP hybrid;
- MinHash k=5/k=7 sketch, sketch size 128;
- EIIP positional signal and EIIP summary.

Outputs:
- `results/stage3/compact_baselines/compact_baseline_stability.csv`
- `results/stage3/compact_baselines/compact_baseline_readout.csv`
- `results/stage3/compact_baselines/compact_baseline_interpretation.md`

Main result:
- CSP: mean paired cosine 0.996, mean L2 drift 0.079, nearest-clean retrieval 1.000, median 147 features.
- MinHash k=5 preserved retrieval but drifted more: mean cosine 0.951, L2 0.266.
- EIIP summary looked extremely stable by low-dimensional cosine but retrieval was poor: mean retrieval 0.148.

Interpretation:
CSP is not just a small vector and not just a biochemical scalar encoding. The useful property is the combination of canonical spaced identity evidence plus interpretable property summaries. Low drift alone is not sufficient if paired identity retrieval collapses.

### Experiment B: ART Illumina error-profile validation

Purpose: test whether CSP-like stability remains under a standard sequencing-error simulator rather than only under hand-coded perturbations.

Inputs:
- Existing 21-genome close-relative WGS manifest.
- ART Illumina executable under `tools/art/extracted_bp/Win64/art_illumina.exe`.
- Read lengths: 69, 75, 100, 125, 150 bp.
- Fold coverage: 0.005.

Outputs:
- `results/stage3/art_illumina/art_paired_reads.csv`
- `results/stage3/art_illumina/art_stability_metrics.csv`
- `results/stage3/art_illumina/art_completed_summary.md`
- `results/stage3/art_quality_stratified/art_quality_stratified_stability.csv`
- `results/stage3/art_quality_stratified/art_quality_stratified_summary.md`

Main result:
- ART generated 75,592 paired rows, corresponding to 37,796 clean/error pairs.
- CSP retained top-1 retrieval 1.000 across the ART grid, with mean paired cosine 0.994 and mean L2 drift 0.086.
- EIIP summary had very low drift but weak retrieval, reinforcing that numerical stability without identity recoverability is insufficient.
- ART quality-stratified analysis showed CSP top-1 retrieval 1.000 in both low- and high-quality strata, with mean paired cosine from 0.992 to 0.995.

Interpretation:
ART strengthens the perturbation-stability claim under platform-like error profiles. It does not make CSP a stand-alone taxonomic classifier. The result supports CSP as a stability/quality auxiliary evidence block.

### Experiment C: CAMI_TOY_low external benchmark probe

Purpose: test whether representation signals are readable in an external metagenomic benchmark context with read-level gold mapping.

Inputs:
- CAMI_TOY_low 30-genome GigaDB archive via remote tar range extraction, not full local download.
- FASTQ prefix: 32 MiB.
- Gold read mapping prefix: 256 MiB.
- Labelled subset: 24,000 reads across 30 taxon labels.
- Native CAMI reads are 2x100 bp; therefore external probe lengths are limited to 69, 75 and 100 bp.

Readout models:
- nearest centroid;
- logistic regression;
- scikit-learn MLP;
- fixed random seeds.

Outputs:
- `data/stage3/cami/cami_toy_low_subset_reads_expanded.csv`
- `results/stage3/cami_probe_expanded/cami_probe_reads.csv`
- `results/stage3/cami_probe_expanded/cami_probe_readout.csv`
- `results/stage3/cami_probe_expanded/cami_probe_summary.md`

Main result:
- Multi-taxon label probe remained difficult, as expected for weak readouts over short anonymous metagenomic reads.
- Hybrid canonical 5-mer + CSP won 8 of 9 label-probe condition-length settings.
- In binary target/background probes, canonical spaced count won 6 of 9 settings and hybrid won 2 of 9 settings.
- At 69 bp under 1% substitution, canonical spaced count reached mean macro-F1 0.784.

Interpretation:
CAMI does not prove clinical classification accuracy. It supports the readout value of layered or compact spaced evidence in an external benchmark. The result also prevents overclaiming: CSP alone is not always the best readout representation.

## 4. Manuscript revisions completed

Updated file:
- `manuscript/stage3_manuscript_v3.md`
- `manuscript/stage3_manuscript_v3.docx`

Main revisions:
1. Added the rationale for controlled simulated reads in Introduction/Methods logic.
2. Replaced planned stage-3 placeholders with completed MinHash/EIIP, ART and CAMI results.
3. Added ART quality-stratified interpretation.
4. Updated CAMI text to use the expanded 24,000-read subset and MLP-compatible readout.
5. Tightened claims so CSP is framed as a compact perturbation-stable auxiliary block, not a universal replacement for canonical k-mer.
6. Expanded Limitations and Future Work around clinical mNGS boundaries, CAMI 2x100 limitation, host/background mixtures, abundance structure, database incompleteness and future end-to-end pipelines.

## 5. Current evidence boundary

Supported strongly:
- CSP is compact and perturbation-stable in WGS-derived controlled reads.
- CSP remains stable under ART Illumina-like sequencing errors.
- Low-dimensional EIIP stability alone is insufficient because retrieval can collapse.
- MinHash preserves identity-like retrieval but drifts more than CSP under the perturbation grid.
- CAMI external probes support hybrid/spaced evidence readability but do not support a CSP-alone classifier claim.

Supported with caution:
- Hybrid or layered representation is the most realistic design route.
- CSP is useful for QC/audit, perturbation-stability and auxiliary confidence signals.

Not claimed:
- clinical sensitivity or specificity;
- species-level production classifier superiority;
- ARG allele calling;
- resistance SNP calling;
- plasmid linkage or genomic context inference;
- replacement of Kraken2/Centrifuge/Kaiju/alignment/database evidence.

## 6. Remaining work before submission

Local manuscript tasks:
1. Render and visually QA the final DOCX if LibreOffice or an alternative converter can be repaired.
2. Run a reviewer-style audit against the final v3 text.
3. Check citation formatting and exact reference list completeness.
4. Add exact public repository commit hash once the GitHub repository is finalized or archived.

Server/future extension tasks:
1. Larger genome-held-out WGS panel.
2. Full CAMI or additional CAMI profiles if storage and time allow.
3. Independent pipeline sanity checks using Kraken2/Centrifuge/Kaiju on the same FASTQ inputs.
4. Real ARG database tasks using CARD, ResFinder, AMRFinderPlus or MEGARes/AMR++.
5. Clinical sample-level validation when orthogonal labels and ethical/data permissions are available.
