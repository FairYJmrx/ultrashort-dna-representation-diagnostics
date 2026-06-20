# Revision Positioning and Evidence Policy

Date: 2026-06-20

## Non-negotiable manuscript position

This project is a DNA-read representation diagnostics study, not a species-classification leaderboard.

The manuscript must compare how different representations preserve, compress, transform, or discard sequence information under short-read mNGS-like constraints. Classification results are allowed only as downstream readout probes of representation behavior.

## Correct claim for the proposed method

The safest claim for `cspaced_property_l2` is:

> `cspaced_property_l2` is a compact, strand-friendly, perturbation-stable auxiliary representation that combines canonical spaced tokens with low-dimensional DNA property summaries. It is not intended to replace canonical k-mer representations in all settings.

Supported advantage region:

- short-read perturbation stability under N masking and substitution;
- reverse-complement friendly behavior inherited from canonical spaced tokens;
- compact auxiliary features that are easy to concatenate with conventional k-mer or model embeddings;
- diagnostic use in QC-like, robustness, and representation-comparison experiments.

Boundary that must be stated:

- canonical k-mer remains a strong close-relative classification baseline;
- no current lightweight experiment proves universal species-classification superiority;
- no current local experiment proves clinical mNGS diagnostic performance;
- the method is best framed as complementary rather than replacing canonical k-mer.

## Accuracy and macro-F1 policy

Accuracy and macro-F1 can appear in the paper only as tertiary metrics.

They answer:

> Can a simple downstream readout extract a particular signal from the representation?

They do not answer:

> Is this a clinically accurate species-identification model?

The main text should therefore use wording such as:

- classification probe;
- linear separability;
- nearest-centroid readout;
- target/background separability stress test;
- context-visibility downstream readout.

The main text should avoid wording such as:

- clinical accuracy;
- diagnostic performance;
- our method identifies species better;
- universal superiority.

## Primary evidence hierarchy

Primary evidence:

- dimensionality and compactness;
- observed vocabulary size and sparsity;
- reverse-complement paired cosine;
- clean-vs-perturbed paired cosine;
- perturbation L2 delta;
- read-length information curves;
- motif-pair and context visibility;
- component ablation deltas for canonicalization, spaced seeding, property summaries, phase, and RoPE-like position handling.

Secondary evidence:

- close-relative WGS-slice stress tests;
- QC-like perturbation AUROC;
- OOD/prototype diagnostics;
- target-vs-background separability.

Tertiary evidence:

- accuracy;
- macro-F1;
- lightweight logistic regression or nearest-centroid results.

## Representativeness of the close-relative dataset

The current close-relative dataset is not universal.

It contains 21 genomes from six clinically relevant genera and should be described as a lightweight WGS-slice stress test. It is useful because it is harder than artificial data and exposes method behavior around related taxa, but it cannot represent the full microbial taxonomy, full clinical mNGS diversity, or all sequencing conditions.

Allowed claim:

> In a lightweight close-relative stress test, canonical k-mer remained a strong baseline, while the proposed auxiliary representations showed robustness and compactness advantages in specific perturbation regimes.

Disallowed claim:

> The selected genera prove general superiority for mNGS species identification.

## Server-scale experiments to mark separately

The following experiments are important but should be marked as server-scale follow-up if not run locally:

- expanded close-relative panels with many strains per genus;
- realistic FASTQ simulation with quality decay, adapters, host background, abundance mixtures, and contamination;
- repeated-seed evaluation across larger genome panels;
- tiny CNN and tiny Transformer comparison under controlled representation inputs;
- Kraken2/Centrifuge/Kaiju clean-noisy-OOD audit as clinical-pipeline baselines;
- AMR-gene task for resistance-detection relevance.

## Writing rule for the final manuscript

Every result paragraph must answer three questions:

1. What information property is being tested?
2. Which representation has an advantage region, and why?
3. What conclusion is not justified by the current evidence?

This rule prevents the manuscript from becoming an accuracy ranking table and keeps the logic aligned with the representation-science goal.
