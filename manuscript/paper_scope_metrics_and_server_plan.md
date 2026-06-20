# Paper Scope, Metric Logic, and Server-Scale Experiment Plan

Date: 2026-06-20

## 1. Correct Paper Purpose

The purpose of this paper is **not** to prove that a proposed feature gives the highest species-classification accuracy.

The correct purpose is:

> To compare DNA read representation schemes under ultra-short mNGS-like constraints and identify the information each representation preserves, loses, or makes easier for downstream models to use.

Therefore, the manuscript should be framed as a **representation diagnostics paper**, not as a complete clinical species-identification paper.

The central scientific questions are:

1. What does each representation preserve: composition, strand symmetry, local order, position, biochemical property, motif-pair context, or perturbation signal?
2. Which representation is stable under reverse complement, N masking, substitution, trim and paired-end information gain?
3. How does read length change information visibility and downstream separability?
4. Which representations are suitable for linear models, nearest-centroid models, CNN-like local models, or attention-like context models?
5. Where do new methods have advantage regions, and where do conventional canonical k-mers remain stronger?

## 2. How Accuracy Should Be Used

Accuracy and macro-F1 are useful, but only as **downstream probes**.

They should not be treated as clinical performance, and they should not dominate the paper. In the current lightweight setup, accuracy reflects whether a simple classifier can exploit the representation on a controlled task. It does not prove that the representation will perform best in a full mNGS pipeline.

Recommended wording:

- Use: "classification probe", "linear separability", "nearest-centroid separability", "task-specific readout".
- Avoid: "clinical accuracy", "species-identification performance", "the method is better for mNGS diagnosis".

## 3. Metric Hierarchy

### Primary representation metrics

These are closest to the paper's actual aim:

- feature dimension;
- observed vocabulary size;
- sparsity / nonzero density;
- k-mer information capacity under read length;
- reverse-complement paired cosine;
- clean-versus-perturbed cosine;
- perturbation L2 delta;
- motif/context visibility;
- read-length information curves;
- property-summary contribution by ablation;
- component delta after adding canonicalization, spaced seed, property summary, phase or RoPE.

### Secondary diagnostic metrics

These support interpretation but should not drive the entire paper:

- AUROC for QC-like perturbation detection;
- OOD centroid score;
- paired retrieval top-1 / MRR;
- close-relative target-vs-background separability;
- within-genus species separability.

### Tertiary downstream-probe metrics

These are useful but must be clearly labeled as lightweight:

- accuracy;
- macro-F1;
- simple holdout performance;
- nearest-centroid/logistic-regression results.

## 4. Does the Current Accuracy Use Conflict With the Original Idea?

Partly yes, if the paper is written as an accuracy leaderboard.

No, if accuracy is used as one diagnostic probe among several.

The original project idea was to study **information representation**, not to train a high-performance model. The current experiments are aligned with that idea only when:

- accuracy is interpreted as "can a simple classifier read out the encoded information?";
- non-classification metrics are emphasized first;
- low accuracy in close-relative classification is treated as evidence of task difficulty and information limits, not as method failure;
- high accuracy on artificial tasks is treated as controlled evidence, not clinical performance.

## 5. Current Claim Boundary for New Methods

### `cspaced_property_l2`

Supported:

- compact hybrid representation;
- reverse-complement friendly because it uses canonical spaced tokens;
- perturbation-stable under N masking and substitution;
- useful auxiliary diagnostic channel for QC-like representation behavior.

Not supported:

- full replacement of canonical k-mer;
- universal species-classification superiority;
- clinical contamination detection;
- antimicrobial-resistance detection.

### `cspaced_count_l2`

Supported:

- strong strand consistency;
- compact spaced-token baseline;
- useful in some close-relative target/background probes.

Not supported:

- guaranteed superiority over canonical contiguous k-mer in all taxonomy tasks.

### `spaced_kmer_phase`

Supported:

- useful in some position-sensitive or target/background probes.

Current ablation warning:

- explicit phase did not show independent gain over the no-phase spaced-property variant in the current motif-position ablation. This must be reported honestly.

### `RoPE-property`

Supported:

- attention-compatible representation design;
- good conceptual fit for relative-position modeling;
- useful in some close-relative and controlled position tasks.

Not yet supported:

- full Transformer superiority.

## 6. Are the Close-Relative Data Universal?

No.

The current close-relative benchmark is valuable but not universal. It uses 21 selected genomes from six clinically relevant genera. It is a lightweight representation stress test, not a representative sample of all microbes or all mNGS cases.

What it can support:

- "We tested whether conclusions survive a harder close-relative WGS-slice stress test."
- "The ranking changes under close-relative pressure, so controlled toy results alone are insufficient."
- "Canonical k-mer remains a strong close-relative backbone."

What it cannot support:

- "This is generally best for all pathogens."
- "This represents the whole microbial taxonomy."
- "This predicts clinical mNGS performance."

## 7. Why the Close-Relative Test Still Helps

Even though it is not universal, it is useful because:

- it is more realistic than purely artificial sequences;
- it contains clinically motivated hard negatives;
- it tests whether representations collapse among related taxa;
- it exposes the limit of lightweight models and short reads;
- it prevents overclaiming from toy data.

In the final paper, it should be called a **close-relative WGS slice stress test**.

## 8. Experiments That Should Be Marked for Server-Scale Follow-Up

Some experiments are important but not ideal for the current local computer. These should be marked as future/server-scale work, or run later when the user provides results.

### S1. Large close-relative panel

Goal:

- expand beyond 21 genomes to dozens or hundreds of genomes per key genus.

Recommended genera:

- Klebsiella pneumoniae species complex;
- Enterobacter cloacae complex;
- Acinetobacter baumannii/calcoaceticus complex;
- Burkholderia cepacia complex;
- Candida species and strain-level near neighbors;
- Escherichia/Shigella/Enterobacterales hard negatives.

Output needed:

- repeated-seed close-relative classification;
- taxonomic confusion matrices;
- genus/species/strain-level separability curves.

### S2. Realistic FASTQ simulation

Goal:

- simulate Illumina-like quality profiles, adapters, terminal quality decay, host background and abundance mixtures.

Output needed:

- clean/noisy representation stability;
- QC-like perturbation AUROC;
- host/background false-positive stress.

### S3. Tiny CNN / Tiny Transformer / Attention models

Goal:

- test whether raw-base, property, RoPE-property and spaced-property encodings are actually useful in trainable sequence models.

Minimum models:

- shallow 1D CNN;
- embedding CNN for k-mer tokens;
- tiny Transformer with sinusoidal PE, learned PE and RoPE-property;
- possibly contrastive read encoder.

Output needed:

- same architecture, different representation inputs;
- small data and larger data regimes;
- attention/context diagnostic task;
- close-relative WGS stress task.

### S4. Kraken2 / mature classifier audit

Goal:

- compare representation diagnostics with a mature database-based classifier.

This should not be framed as beating Kraken2. It should be used to understand clean/noisy/OOD gaps and where learned representations may be auxiliary.

### S5. AMR-oriented representation task

Goal:

- test whether representations can preserve point mutation, gene-fragment, or allele-level signals relevant to resistance.

Output needed:

- controlled SNP/indel AMR marker tasks;
- gene-family similarity stress;
- read-length and mutation-position sensitivity.

## 9. Manuscript Writing Rule

The final manuscript must keep this order:

1. representation problem;
2. method definitions;
3. intrinsic information metrics;
4. perturbation and strand diagnostics;
5. read-length and attention-context diagnostics;
6. close-relative stress tests;
7. lightweight downstream probes;
8. claim boundary and server-scale future work.

Accuracy should appear after information diagnostics, not before them.

## 10. Short Answer for the Paper's Core Message

The paper should say:

> Ultra-short DNA read representation is task-dependent. Canonical k-mers remain essential for strand-aware short-read classification, while canonical spaced-property features provide compact auxiliary information for perturbation stability and QC-like diagnostics. Read length and paired-end context change not only the number of observed bases but also which motif co-occurrences are visible to sequence models. Therefore, the right question is not which representation has the highest accuracy everywhere, but which biological and mathematical information each representation makes available to each downstream model class.
