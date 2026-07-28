# Pre-submission Experiment and Manuscript Checklist

This file is the active completion checklist for the NAR Genomics and Bioinformatics submission draft. It supplements `submission_hardening_execution_plan.md` and records both scientific completion and submission readiness. Manuscript prose remains in English; this checklist remains operational and may mix English identifiers with concise Chinese explanations.

## Locked scientific argument

Under a fixed compact feature budget, CK4P-MSP organizes reverse-complement canonical local k-mer composition (K), global biochemical summaries (P), and multi-scale positional property pooling (MSP/M) as block-decomposable audit channels. The evidence must establish their empirical conditional contributions to perturbation stability and local-change readability. It must not describe the blocks as statistically independent, mutually orthogonal physical axes, or a universally optimal metric.

## Locked terminology and claim boundary

- Use `canonical local k-mer composition` or `local-token composition evidence` for CK4/CK5.
- Reserve `exact matching evidence` for alignment-, long-k-mer-, minimizer-, or database-backed matching systems.
- Use `standardized diagnostic drift` for mixed-space L2.
- Use `grouped delta-readout` for the local-change versus matched-noise probe.
- Describe P and MSP as `related but non-equivalent` and `empirically complementary`.
- Describe CK4P-MSP as a `compact, block-decomposable representation-level audit coordinate system`.
- Do not claim P/MSP orthogonality, independence, super-additivity, biophysical distance, universal information gain, clinical validation, production classification, or pipeline improvement.
- MI/KSG results are estimator-dependent empirical separability audits, not theoretical proofs.

## A. Required experiment completion

### A1. Seven-group K/P/MSP ablation

- [x] Evaluate all seven non-empty block combinations under the same block-normalized assembly rule:
  - K (136 dimensions)
  - P (11 dimensions)
  - MSP/M (75 dimensions)
  - K+P (147 dimensions)
  - K+MSP (211 dimensions)
  - P+MSP (86 dimensions)
  - K+P+MSP / CK4P-MSP (222 dimensions)
- [x] Use the existing controlled WGS perturbation grid for paired cosine, standardized diagnostic drift and nearest-clean retrieval.
- [x] Use the existing local-mutation triplets for grouped delta-readout.
- [x] Keep all derivatives of one `sample_id`/template in the same fold through `StratifiedGroupKFold`.
- [x] Record dimensions, number of paired cells, number of triplets, random seed and elapsed time.

### A2. Prespecified conditional-contribution contrasts

- [x] K conditional contribution: compare K+P+MSP with P+MSP.
- [x] P conditional contribution: compare K+P+MSP with K+MSP.
- [x] MSP conditional contribution: compare K+P+MSP with K+P.
- [x] Report matched-cell effect differences, 95% bootstrap confidence intervals, paired Wilcoxon tests and Benjamini-Hochberg-adjusted q values.
- [x] State the paired unit and number of tested contrasts.
- [x] Interpret a block as conditionally informative only for the metric supported by its matched contrast; do not require every block to improve every metric.

### A3. Result-triggered audit, not automatic expansion

- [x] Inspect the P+MSP result before opening a new experiment.
- [x] Residualized P/MSP audit not triggered: the prespecified conditional contrasts distinguish P's stability role from MSP's local-readout role under the tested grid.
- [x] Do not add Transformer, Kraken2/triage, ARG/SNP, clinical sensitivity/specificity or a universal metric theorem to the current submission scope.

## B. Required manuscript evidence update

### B1. Methods

- [x] Define the seven ablation representations and the fixed normalization rule with display equations.
- [x] State default weights `alpha = beta = gamma = 1` and the ranges used in the existing weight audit.
- [x] Define the audit protocol as a reusable sequence: clean/perturbed pairs -> block construction -> paired drift and retrieval -> grouped delta-readout -> conditional-contribution contrasts -> bounded failure flags.
- [x] Cite the primary methods/resources for ART, CAMI/CAMI II, KSG/kNN MI, Wilcoxon and Benjamini-Hochberg where first used.
- [x] Clarify that MinHash is evaluated through native signature agreement/Jaccard estimation, not mixed-vector L2 or linear readout.
- [x] Clarify CAMI_TOY preprocessing: candidate label field, retained hierarchy, minimum class/sample eligibility, background/unclassified handling and subset-selection rule.
- [x] Resolve the `30 labels` ambiguity: 30 candidate labels in a source subset do not imply a valid 30-class CK4P-MSP probe after eligibility filtering.

### B2. Results

- [x] Replace the four-group ablation paragraph/table/figure with the seven-group result.
- [x] Lead with complementary conditional roles, not with a generic statement that concatenation is better.
- [x] Report whether K remains necessary relative to P+MSP for local composition/readout evidence.
- [x] Report whether P changes global perturbation stability after conditioning on K+MSP.
- [x] Report whether MSP changes local-change readability after conditioning on K+P.
- [x] Report negative or metric-specific results explicitly; the full representation need not be best on every single axis.
- [x] Keep shallow macro-F1 explicitly as a grouped representation-level probe, not classifier performance.

### B3. Discussion and conclusion

- [x] Interpret P as a global biochemical stability summary and MSP as a coarse positionalization of related property signals.
- [x] State that P and MSP can be correlated while still contributing different conditional empirical effects.
- [x] Avoid `necessary` unless the exact metric-specific contrast supports that word; prefer `contributed`, `retained`, or `was required for the observed ... under the tested grid`.
- [x] Present CK4P-MSP as a balanced compact trade-off, not a super-additive synergy theorem or universal winner.
- [x] Keep downstream triage, false-hit reduction, deep learned embeddings and clinical mapping as bounded future work.

## C. Low-cost completeness and consistency work

### C1. Terminology and cross-section consistency

- [x] Replace CK4 `exact identity` wording throughout Abstract, Introduction, Methods, Results, Discussion, tables and captions.
- [x] Remove unsupported `orthogonal`, `independent`, `proof`, `theorem`, `superior representation` and `information gain` wording.
- [x] Reduce repeated defensive disclaimers: define scope once in the Introduction and once in Limitations, while Results report observations directly.
- [x] Verify all Abstract and Introduction claims against a named result/table/figure.

### C2. Statistics and reporting

- [x] For every primary comparison, report effect size, confidence interval, test, adjusted q value, paired unit and sample/cell count.
- [x] Keep MI precision commensurate with estimator uncertainty and report estimator settings and sensitivity range.
- [x] Confirm that no row-wise split remains where paired derivatives share a source template.
- [x] Distinguish confirmatory prespecified contrasts from descriptive exploratory audits.

### C3. Figures, tables and captions

- [x] Ensure the main ablation figure visibly includes CK4P-MSP and the seven groups or a scientifically justified focused subset plus a complete table.
- [x] Use one visual message per panel; move long labels into legends/captions.
- [x] Make every caption self-contained: panel purpose, data layer, read lengths, perturbations, n, metric direction, intervals/error bars and claim boundary.
- [x] Check axes for misleading truncation, odd aspect ratios, label overlap and unreadable font size.
- [x] Integrate supplementary figure citations into prose rather than using standalone caption-like sentences.
- [x] Keep main and supplementary numbering synchronized across Markdown, LaTeX, Word and generated assets.

### C4. References and abbreviations

- [x] Expand all abbreviations at first use, including CK4P-MSP, MSP, CSP, MI, KSG, kNN, ART, CAMI, PCA, SVD, CCA and EIIP.
- [ ] Verify final metadata and publication status for all references, especially recent sequence foundation models and software/dataset citations.
- [x] Add the formal reference supporting the public 50-75 bp mNGS read-length context.
- [x] Ensure every bibliography entry is cited and every citation key resolves in LaTeX.

### C5. Back matter and submission metadata

- [x] Retain authors: Ruixiang Mei (first author; ORCID 0009-0003-2128-0726) and Jianhua Huang (corresponding author), both affiliated with The Chinese University of Hong Kong, Shenzhen.
- [x] Retain `The authors declare no competing interests.`
- [ ] Finalize funding only after the authors decide between no specific funding and a verified grant; do not infer a grant.
- [ ] Finalize ethics wording or obtain an institutional determination for any retained restricted aggregate read-length provenance.
- [ ] Replace private-review repository wording with a public release URL, immutable tag/commit, license and archival DOI at submission.
- [ ] Remove all `must be finalized`, `will be finalized`, `TBD` and author-facing notes from the submitted manuscript.

## D. Build and submission QA

- [x] Rebuild Markdown-derived DOCX after final text/figure changes.
- [x] Rebuild the OUP/NARGAB LaTeX PDF and confirm no undefined citations, broken equations or unresolved references.
- [x] Render and visually inspect every PDF page for large avoidable whitespace, float drift, figure-only pages, clipped legends and text/figure mismatch.
- [x] Confirm that every figure and table is cited in numerical order and appears within one page of its first substantive discussion where feasible.
- [ ] Confirm submission article type (recommended current route: Standard Paper unless the software-use case is expanded).
- [x] Run a final three-perspective review: technical rigor, originality/value, and editorial/submission readiness.

## E. Acceptance gates

The manuscript is ready for submission only when:

1. The seven-group ablation and its three conditional contrasts are complete and reproducible.
2. No primary numerical claim depends on a legacy method alias or a non-grouped split.
3. The paper consistently presents conditional empirical contributions rather than independence or universal superiority.
4. CAMI, MinHash, MI and mixed L2 are described within their tested roles.
5. References, captions, abbreviations and back matter contain no unresolved submission placeholders except information that must be supplied by the authors before the final upload.
6. Both DOCX and LaTeX/PDF builds pass textual and visual QA.

## Current status after the seven-group completion pass

- **Scientific evidence:** complete for the locked representation-diagnostic claim. The seven-group result and grouped conditional contrasts distinguish P's global-stability contribution, MSP's local-change-readout contribution, and K's composition-linked retrieval contribution. A residualized P/MSP expansion is not triggered by the current result.
- **Text and assets:** complete for the current scope. The Markdown, LaTeX main PDF, supplementary PDF and DOCX have been rebuilt; the DOCX main text contains main figures/tables only, while supplementary figures remain in the dedicated supplementary PDF.
- **External author actions before upload:** final reference metadata/publication-status review, funding statement, ethics/data-governance wording, public repository URL plus immutable release/DOI, and final selection of article type. These are submission metadata gates, not outstanding experiments.
- **No further mandatory experiment is identified.** Optional scope-expansion studies (larger labelled CAMI II, learned embedding baselines, or a pipeline-facing triage study) can increase breadth, but are not required for the bounded claim supported here.
