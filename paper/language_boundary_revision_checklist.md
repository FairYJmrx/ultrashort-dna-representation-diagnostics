# Language Boundary Revision Checklist

This checklist records manuscript-level language constraints derived from pre-submission reviewer-style audits. The broader and newer contract is `MANUSCRIPT_GLOBAL_CONSTRAINTS.md`; when the two documents differ, that global contract and the current LaTeX evidence tables take precedence.

## Locked Claim Boundaries

1. CK4P-MSP is a representation-diagnostics framework, not a clinical diagnostic tool, an end-to-end classifier, a Kraken/Centrifuge replacement, or a production mNGS pipeline.
2. Mixed-space L2 must be described as standardized diagnostic drift after block construction and normalization, not as a natural biophysical distance.
3. MI, conditional MI and kNN/KSG analyses must be described as estimator-dependent empirical audits, not as universal information-theoretic proofs or theoretical lower bounds.
4. P and MSP must be described as related but non-equivalent property layers. Do not call them orthogonal axes or independent physical dimensions.
5. CAMI_TOY_low is a lightweight labelled external readout probe. CAMI II marine is an anonymous-read external stability probe without reconstructed read-level taxonomic labels.
6. The 69 and 75 bp settings should be justified as representative lower-read-length conditions within a published 50-75 bp post-QC mNGS regime. Do not imply that 69-75 bp reads are intrinsically unclassifiable. The intended claim is that identity evidence has a reduced margin relative to longer reads, making representation-level auditing useful.
7. DNA foundation models and Transformer embeddings should be discussed as powerful predictive representations and future comparators, not as methods proven unsuitable by this study. If their probes can be stronger, acknowledge that predictive strength and decomposable auditability are different goals.
8. CK4P-MSP's main value is not predictive supremacy. It is a low-dimensional, training-free and block-decomposable coordinate system for auditing identity, biochemical and coarse positional information retention under controlled perturbation.
9. Shallow readout macro-F1 is a readability probe, not the central proof of representation value. Stability, blockwise drift, MI/kNN-MI audits, P/MSP contribution and counterfactual controls carry the representation-level evidence.
10. Dimension-matched high-k baselines should be framed as compactness-constrained diagnostic audits, not as evidence against production-scale high-k matching pipelines.
11. Pipeline-facing triage, false-hit reduction and classifier-output auditing remain future work unless directly evaluated.
12. Data Availability, Code Availability, Ethics, author, funding and conflict-of-interest placeholders must be replaced before submission.

## Manuscript-wide Consistency Contract (locked 2026-07-30)

1. Evidence strength must remain stable across Abstract, Results, Discussion and Conclusion. A descriptive contrast cannot become a significant, independent or generalizable effect in a later section.
2. The six CAMI target tasks must always be described as `source-grouped fixed-head tasks drawn from a shared source pool`. Do not use `source-disjoint`, `independent target cohorts` or equivalent language.
3. Use `canonical local k-mer composition` for CK4/CK5. Reserve `exact matching` and `identity evidence` for database-linked matching, alignment or explicitly longer token systems.
4. Use `standardized diagnostic drift` for mixed-space L2 and `grouped local-change readout` for the template-grouped local probe. Do not introduce synonyms that imply a physical metric, clinical diagnosis or independent biological replication.
5. Use `descriptive cross-target contrast` for CAMI method differences. Target-bootstrap intervals and signed-rank summaries describe consistency across dependent task definitions, not population-level inference.
6. Keep P and MSP `related but non-equivalent`: P is associated primarily with global biochemical stability; MSP adds coarse positionalized property summaries and most of the grouped local-change readability increment. Neither block is called statistically independent or universally necessary.
7. Prefer direct positive scope statements over repeated disclaimers. State what the audit measures, the dataset and perturbation regime, and the boundary of inference once; do not repeat `not a classifier` in every section.
8. Maintain British spelling where prose has been standardized (`analysed`, `behaviour`, `neighbouring`, `licence`) unless a quoted software or official title requires otherwise.

## Figure and Layout Contract (locked 2026-07-30)

1. Every main figure must answer one named question in the immediately adjacent Results text. A panel without a role in the argument is moved to Supplementary Data or removed.
2. Main figures show only methods needed to establish the stated contrast. They are not exhaustive result inventories.
3. Captions must define panels, data layer, analysis unit, sample or cell count, direction of improvement, uncertainty interval and claim boundary where applicable.
4. Figures must be exported with tight content bounds. Large internal white margins, legends detached from the plotted evidence and aspect ratios that compress labels are prohibited.
5. Legends may sit outside axes when they would obscure points or lines, but the added margin must remain proportionate to the plot body.
6. Figure height must match information density. A two-panel figure must not occupy a full page merely because it is exported on a large canvas.
7. LaTeX floats should remain within one page of their first substantive citation where possible. Avoid figure-only pages, stranded headings and avoidable half-empty pages.
8. Full-width figures are reserved for genuinely multi-panel or wide comparisons. Compact two-panel figures may use one column when labels remain legible.
9. Any float or page break introduced to repair placement must be checked in the compiled PDF, not judged from source order alone.
10. The final PDF must be visually inspected after every figure, caption or float change for overlap, clipping, font size, internal whitespace and page-level whitespace.

## Required Text Revisions

### Abstract

- Replace broad "can improve stability" language with observed-result language such as "showed lower perturbation drift".
- Keep the final implication bounded to compact, decomposable representation-level robustness auditing.
- Avoid implying that CK4P-MSP is expected to outperform learned sequence embeddings in predictive probes.
- Avoid implying that 69-75 bp reads are unclassifiable. Use "lower-read-length regime" or "compressed identity margin" language.

### Introduction

- Soften exact-matching limitation language from "is amplified" to "can be amplified" unless directly supported by a cited quantitative source.
- Replace "can remain strong" with "can remain competitive".
- Recast DNA foundation model language from "poorly suited" to "not naturally aligned with the present front-end diagnostic audit".
- Keep "not direct 69/75 bp comparators" as a scope statement, not as a performance judgement.
- Explicitly state that learned embeddings may be stronger for prediction, whereas this study asks a different question: how identity, biochemical and positional evidence degrade in a decomposable representation.
- Reframe 69-75 bp as lower-bound length conditions where identity margin is reduced relative to 150 bp, not as an automatic classification-failure setting.

### Methods

- Define KSG at first use as Kraskov-Stogbauer-Grassberger.
- Keep Ross/KSG wording transparent and avoid implying an exact KSG theorem if the implementation is a nearest-neighbor robustness audit.
- Replace defensive scope language such as "The manuscript should not be read as..." with positive scope language.
- Add an explicit rationale for the 2+3+4+6 MSP binset: coarse-to-fine relative-position summaries whose finest scale keeps bins above single-position resolution in the 69-150 bp regime.
- Keep high-k compressed baselines framed as compactness-constrained audits.

### Results

- Rename "Mixed-feature information gain" to "Empirical mixed-feature information audit" or equivalent.
- Replace "carried perturbation information" with "showed estimator-dependent perturbation-associated signal".
- Replace "catastrophic collapse" wording with "immediate loss of reliability" or similarly neutral wording.
- Keep CAMI_TOY_low as lightweight external readout and CAMI II marine as anonymous-read stability.
- Add a CAMI II marine composition caveat: marine metagenomes may differ from clinical/pathogen-rich contexts, so this probe tests external sequence-source stability, not clinical generalization.
- Reduce repeated "not a standalone classifier" language in Results; keep the boundary mainly in Study design and Limitations.
- Treat macro-F1 as a shallow readability probe. Do not use it as the main evidence that CK4P-MSP is "better" than learned embeddings or production classifiers.
- When high-k or hash baselines are discussed, claim compact perturbation-stability and auditability advantages only under the stated feature-budget constraint.

### Discussion, Limitations and Conclusion

- Split overly long evidence-chain paragraphs where needed.
- Replace internal audit phrasing such as "compliant with the manuscript's current claim" with manuscript-ready prose.
- Replace "improved perturbation stability" with "reduced perturbation drift" where consistency with standardized diagnostic drift is more important.
- Keep practical implications bounded to representation-level robustness auditing.
- Add or preserve one clear sentence: CK4P-MSP is not expected to beat large learned embeddings in predictive probes; its intended role is decomposable, low-dimensional perturbation auditing.
- Keep "auxiliary" only when describing pipeline use. For the method's own contribution, prefer "compact, block-decomposable representation" or "representation-level audit coordinate system".

### Back Matter

- Keep Data Availability and Code Availability factual and repository-specific; the public DOI remains a submission action until minted.
- Replace "authors should confirm" internal notes before submission.
- Verify Yang book metadata before final reference export.
- Insert the funding statement after author confirmation; do not invent a funding source or retain a visible placeholder in the submission PDF.

## Terms To Avoid Or Use Carefully

- Avoid: proof, prove, theorem, universal guarantee, strict information gain, natural physical distance, orthogonal axes, independent physical axes, clinical validation, production classifier, replacement, deployment model.
- Avoid or qualify: better representation, stronger representation, predictive superiority, unclassifiable ultra-short reads, recovers positional information, restores position, high-density paradigm.
- Use instead: empirical audit, estimator-dependent signal, standardized diagnostic drift, related but non-equivalent layers, compact block-decomposable representation, representation-level robustness auditing, compactness-constrained baseline audit, compressed identity margin, coarse positional property summary.
