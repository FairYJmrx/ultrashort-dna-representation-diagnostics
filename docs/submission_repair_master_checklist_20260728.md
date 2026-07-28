# Submission repair master checklist

Date: 2026-07-28

Canonical manuscript: `paper_latex/main.tex`

Canonical method repository: `release_code/`

Target: NAR Genomics and Bioinformatics, Standard Paper

Status (2026-07-29): scientific-contract, code, figure, table and LaTeX repairs are complete. Only the explicitly author-supplied submission metadata in Priority 10 and the book ISBN check in Priority 7 remain open.

## Locked scientific contract

The manuscript evaluates a compact, block-decomposable representation for controlled short-read perturbation diagnostics. CK4P-MSP contains reverse-complement canonical 4-mer composition evidence (`K`), a global biochemical property summary (`P`), and multi-scale positional property pooling (`MSP`). The supported contribution is an empirical trade-off among perturbation stability, local-change readability, composition-linked retrieval and compactness. The representation is not a physical distance law, a production classifier, an exact read-identity representation, or a clinical diagnostic pipeline.

Canonical terminology:

- `K`: reverse-complement canonical local-token composition evidence.
- `P`: global biochemical property summary.
- `MSP`: multi-scale positional property pooling.
- `CK4P-MSP`: block-normalized weighted concatenation of K, P and MSP.
- `standardized representation drift`: Euclidean displacement under the declared block-normalized contract.
- `grouped delta-readout`: a mechanism-accessibility probe with all derivatives of one template retained in one fold.
- `empirical MI audit`: an estimator-dependent separability analysis, not a universal information-theoretic proof.

## Priority 1: result-contract integrity

- [x] Remove the historical `ckmer4_property_l2` implementation from contract-v2 compact/high-k result assembly.
- [x] Recompute CK4, CK4+P and CK4P-MSP compact metrics through `methods/ck4p_msp.py` only.
- [x] Rebuild Figure 3 and Table 3 from the same contract-v2 result namespace used by the seven-group audit.
- [x] Verify that every manuscript number has one method implementation, one result file and one plotting/table source.
- [x] Update `docs/contract_v2_evidence_map.md` so historical outputs are never labelled contract-v2.

Acceptance: CK4+P has one value per dataset/aggregation definition; any different value is explicitly attributed to a different dataset rather than an implementation alias.

## Priority 2: MI inference repair

- [x] Replace zero-clipped MI increments with signed paired differences.
- [x] Add a label-permutation null distribution for the increment itself.
- [x] Add paired bootstrap confidence intervals across the 12 prespecified length-by-local-mode cells.
- [x] Report estimator and resampling parameters, sample unit and random seed.
- [x] Use `empirical separability increment` rather than `information gain` unless the estimator-specific qualification is adjacent.
- [x] Point the main text to the current KSG-style supplementary figure; retain binned MI only as a descriptive sensitivity screen.

Acceptance: the increment row contains an estimate, confidence interval and permutation P value without clipping.

## Priority 3: mechanism-aligned local-change audit

- [x] Add a 2 x 2 factorial audit separating spatial localization from substitution chemistry: contiguous/random, contiguous/property-directed, dispersed/random and dispersed/property-directed.
- [x] Keep grouped splits by template ID.
- [x] Report drift and grouped delta-readout for K, P, MSP, K+P, K+MSP, P+MSP and CK4P-MSP.
- [x] Describe the original task as a mechanism-aligned synthetic positive control rather than general anomaly detection.

Acceptance: the manuscript can distinguish evidence for positional localization from evidence for property-directed substitution changes.

## Priority 4: representation-definition and scaling transparency

- [x] Add a complete table for all 11 P coordinates and all MSP property/bin families.
- [x] Define bin edges, short-bin behavior, entropy, scaled length and ambiguous-base handling.
- [x] Explain that row-wise block normalization does not make biochemical coordinates physically commensurate.
- [x] Add a light per-property scaling audit or per-property ablation; otherwise explicitly label the channel as encoding-value-weighted.
- [x] Keep P and MSP as related but non-equivalent layers; do not claim orthogonality, statistical independence or universal necessity.

Acceptance: every feature coordinate and implicit scale choice can be reconstructed from the manuscript or Supplementary Methods.

## Priority 5: external and statistical evidence

- [x] Run CAMI II through the public contract-v2 API; retain ART only as an explicitly historical contextual probe because its archived feature families are not aliases for CK4P-MSP.
- [x] Separate current-contract external evidence from historical contextual probes in figures and captions.
- [x] State that CAMI II marine tests composition-shifted anonymous-read stability, not labelled taxonomic accuracy.
- [x] Define the retrieval candidate pool, chance level and saturation limitation.
- [x] State that Wilcoxon/bootstrap units are matched analysis cells, not independent cohorts.
- [x] Replace `reproducible across cells` with `consistent across the tested cells` unless independent replication supports the stronger term.
- [x] Add effect estimates, confidence intervals, adjusted P values and the number of tested contrasts.

Acceptance: no result is presented as external validation of contract-v2 unless it was generated by that contract.

## Priority 6: manuscript consistency and claim boundaries

- [x] Replace `exact identity` for CK4 with `canonical local-token composition evidence` or an equivalent bounded term.
- [x] Define the studied regime as `short and ultra-short reads (69-150 bp)` unless a narrower operational definition is supplied.
- [x] Preserve one concise scope statement in the Introduction and one limitation statement in Discussion; remove repetitive defensive disclaimers elsewhere.
- [x] Present Figure 6 as a boundary result: compact MSP improves readout of perturbation structure but does not maximize raw local-change distance.
- [x] Keep Transformer, Kraken, ARG/SNP and pipeline-facing triage as future comparisons/applications, not demonstrated outcomes.
- [x] Reconcile every table, caption, abstract number, Results number and Discussion statement with canonical CSV outputs.

## Priority 7: self-contained Methods and references

- [x] Document genome accessions/species, read sampling, lengths, perturbation rates and random seeds.
- [x] Document ART settings, CAMI subset construction, label level and background-read handling.
- [x] Document logistic-regression/nearest-centroid settings, grouped CV, retrieval pool and all dimensionality-reduction settings.
- [x] Document hardware, software versions, runtime measurement protocol and peak-memory method.
- [x] Add direct citations for ART, CAMI, KSG/Ross, Wilcoxon and Benjamini-Hochberg at first methodological use.
- [x] Update KmerAperture to its final 2024 PLOS Genetics publication.
- [x] Add direct citations for named Kssd and HULK/histosketch methods or remove their names.
- [ ] Verify the mNGS book's English title, publisher, ISBN and cited page.

## Priority 8: repository reproducibility

- [x] Fix package imports for all public wrapper scripts.
- [x] Remove hard-coded `D:\\AI-NGS\\info` paths and derive roots from the repository or command-line arguments.
- [x] Fix figure scripts that resolve inputs under nonexistent `analysis/results` paths.
- [x] Use directly executable smoke-test scripts as the supported runner; no pytest dependency is required.
- [x] Add an end-to-end smoke test that regenerates at least one canonical table and one figure from included result data.
- [x] Repair mojibake in `methods/ck4p_msp.py` comments.
- [x] Make README commands executable from a clean checkout and document expected outputs.

## Priority 9: figures, tables and LaTeX QA

- [x] Make all main and supplementary captions self-contained: panels, datasets, lengths, perturbations, n, uncertainty and directionality.
- [x] Clarify whether plotted points are cell means or means across cells.
- [x] Add uncertainty to central aggregate plots where it remains legible.
- [x] Check every figure source against its canonical result CSV.
- [x] Compile main and supplementary PDFs without unresolved references, missing glyphs or content overflow. The OUP class emits a page-header `overfull hbox` artifact, but rendered content remains inside the page bounds.
- [x] Visually inspect all pages for overlaps, cropped labels, undersized legends, stranded headings and avoidable blank pages.

## Priority 10: author-supplied submission metadata

- [ ] Finalize the institutional ethics determination for use of aggregate restricted clinical length provenance, or remove that provenance and rely on public literature.
- [ ] Finalize funding attribution with the corresponding author.
- [ ] Finalize acknowledgements and author contributions.
- [ ] Make the code/data repository reviewer-accessible at submission and public according to journal policy; add release tag, license and archival DOI.
- [ ] Replace every `will be finalized`, `TBD` and repository placeholder before submission.
- [x] Add the first author's ORCID to the OUP author line and author-contribution statement.

These author-supplied items may remain visibly marked while scientific and formatting repairs proceed, but the manuscript is not submission-ready until they are resolved.
