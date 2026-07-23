# Method Contract

This document defines the stable method contract for the release repository.
It is intended to make the repository reproducible as a methods paper rather
than as a loose collection of experiment scripts.

## Scope

The repository implements representation diagnostics for ultra-short DNA reads.
It does not implement a clinical diagnostic classifier and does not replace
Kraken, Centrifuge, alignment or curated database evidence.

The supported claim is narrower: compact biochemical and position-aware
summaries can be audited as auxiliary representation-level channels under
controlled short-read perturbation settings.

## Inputs

Experiment scripts expect tabular read inputs with at least:

| Field | Meaning |
|---|---|
| `sequence` or equivalent sequence column | DNA read sequence. |
| `label` / taxonomic label columns when present | Used only by labelled readout probes. |
| condition or perturbation column | Used for clean-versus-perturbed pairing and local-change labels. |
| length column when present | Used to stratify 69, 75, 100, 125 and 150 bp conditions. |

CAMI II marine anonymous reads are used only for paired stability because
read-level taxonomic labels were not reconstructed for that lightweight probe.

## Representation Families

| Name | Definition | Role |
|---|---|---|
| CK4 | Reverse-complement canonical contiguous 4-mer identity block. | Compact identity backbone. |
| CK5 | Reverse-complement canonical contiguous 5-mer identity block. | Identity baseline. |
| P | Global biochemical-property summary over each read, including base-property means/standard deviations plus read-level N fraction, length and entropy summaries. | Global property stability channel. |
| MSP | Multi-scale positional pooling of per-base property channels over relative-position bins. | Coarse positional property channel. |
| CK4+P | Concatenated CK4 and P under block normalization. | Tests global property contribution. |
| CK4+MSP | Concatenated CK4 and MSP under block normalization. | Tests positional property contribution. |
| CK4P-MSP | Concatenated CK4, P and MSP under block normalization. | Main compact mixed representation. |
| Full-position matrices | Per-position identity or property matrices. | Diagnostic positional upper bound. |
| CSP | Canonical spaced-property control. | Spaced-seed boundary comparator. |
| High-k compressed controls | k=15 signals compressed by MinHash, hashing trick or sparse random projection. | Compactness-constrained high-specificity audit. |

## Default Mixed Representation

The public method API is `methods/ck4p_msp.py`; its explicit experiment name is
`ck4p_msp`. Historical `ckmer*_property_*` strings are retained only for
archived compatibility analyses. They are not aliases for CK4P-MSP and must
not be relabelled as the manuscript main method.

Each block is internally L2-normalized before weighted concatenation. The
default weights are:

| Weight | Block | Default |
|---|---|---|
| `alpha` | CK4 identity block | 1.0 |
| `beta` | P global property block | 1.0 |
| `gamma` | MSP positional property block | 1.0 |

The reported mixed-space L2 metric is standardized diagnostic drift. It is not
a natural biophysical distance between commensurate physical units.

## MSP Default Bins

The default MSP binset is `2+3+4+6`. It is a coarse-to-fine relative-position
summary. The finest scale remains above single-position resolution in the
69-150 bp regime and is audited separately by the MSP bin/gamma sensitivity
analysis. The default manuscript API uses mean-only MSP pooling. Per-bin
standard deviations remain available as an optional audit variant.

## Metrics

| Metric family | Metrics |
|---|---|
| Stability | paired cosine, L2 drift, nearest-clean retrieval. |
| Shallow readout | macro-F1, accuracy. |
| Local-change sensitivity | selective-sensitivity ratio, delta-readout. |
| Reviewer-response audits | same-dimension PCA/SVD, high-k compressed baselines, block-weight sensitivity, empirical MI, kNN MI, P/MSP redundancy, runtime. |

## Claim Boundaries

MI and kNN/KSG analyses are estimator-dependent empirical audits. They should
not be described as universal information-theoretic proofs.

P and MSP are related but non-equivalent property layers. They should not be
described as orthogonal or independent physical axes.

Pipeline-facing triage, false-hit reduction and classifier-output auditing are
future work unless explicitly evaluated.
