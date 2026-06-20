# Stage-2 Task Plan

## Manuscript Claim

The revised paper will test a bounded representation claim: canonical k-mer
features provide high-resolution identity evidence, whereas canonical
spaced-property (CSP) features provide compact perturbation-stable auxiliary
evidence for 69/75 bp mNGS-like reads. A hybrid representation may be a more
realistic route for noisy short-read species and ARG-style pipelines than either
component alone.

## Experiments

1. Advantage-zone grid: compare canonical k-mer, canonical spaced count, CSP
   and canonical k-mer + CSP across 69, 75, 100, 110, 125, 150 and PE150 proxy
   lengths under clean, substitution, N, trim, substitution+N, indel and local
   mismatch perturbations.
2. Hospital-like 69/75 bp focus: evaluate 75 bp raw and 69 bp post-QC WGS-slice
   reads, with 150 bp as a limited reference-like comparator.
3. CSP component ablation: separate spaced seed, reverse-complement
   canonicalization and DNA-property summaries, then rank individual property
   channels.
4. Short-read readout probes: nearest-centroid, logistic regression and MLP
   readouts for target/background, within-genus species and clean-vs-perturbed
   retrieval tasks.
5. Attention breakpoint diagnostic: reuse and extend the existing motif-context
   script for dense 110-160 bp length scans and multiple motif positions.
6. Lightweight model compatibility: use MLP for global-vector features and
   small sequence-model probes for one-hot/property/RoPE-style channels when
   the local environment supports the required library.
7. ARG/SNP boundary task: synthetic marker-level ARG family, allele and
   resistance-SNP probes to test where CSP is helpful and where exact identity
   is required.
8. k and spaced-pattern sensitivity: test k=4-9 and several spaced patterns at
   69, 75 and 150 bp.

## Manuscript Rewrite

- Replace defensive "lightweight" framing with "controlled
  information-preservation diagnostics".
- Define CSP mathematically and biologically.
- Move unsupported clinical, ARG and Transformer claims into Discussion/Future
  Work.
- Rewrite Results as claim-evidence-boundary sections.
- Keep canonical k-mer as a strong baseline rather than an opponent.
