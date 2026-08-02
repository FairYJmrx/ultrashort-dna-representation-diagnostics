# Manuscript Global Constraints

Status: locked for the current NAR Genomics and Bioinformatics submission track.

Contract version: 2026-07-30. Journal-facing requirements must be rechecked against the official author guidelines immediately before submission because file, accessibility and data-sharing requirements may change.

This document is the highest-level writing, evidence, figure, table, layout and release contract for the manuscript. When an older checklist, reviewer note or Markdown draft conflicts with this file, this file and the current LaTeX evidence tables take precedence.

## 0. How To Use This Contract

1. This is an execution contract, not a list of stylistic preferences. Every substantive edit must pass the relevant evidence, terminology, figure, layout and submission clauses below.
2. Resolve conflicts in this order: current verified result tables and scripts; current method contract; this document; current LaTeX prose; older planning notes and reviewer simulations.
3. A reviewer suggestion is not evidence. It may trigger an audit, but wording or experiments change only after the suggestion is checked against the study objective, existing data and comparison contract.
4. Do not repair a structural weakness with stronger prose. If the evidence cannot support a claim, narrow or remove the claim and record the missing experiment separately.
5. Do not hide a valid negative result merely because it weakens a single-metric ranking. Retain it when it defines the method's operating boundary or prevents a misleading superiority narrative.
6. Before editing, identify the affected claim, evidence level, analysis unit, section and figure/table. After editing, search the entire source tree for older formulations.
7. The manuscript must guide the reader through five questions in order: relevance, novelty, trust, reuse and meaning with boundaries.

## 1. Canonical Sources And Change Control

1. The canonical manuscript source is `info/paper_latex/`.
2. The canonical compiled outputs are `paper_manuscript_latex.pdf` and `paper_supplementary_latex.pdf` generated from the current LaTeX source.
3. Files under `info/paper/` are planning and continuity records. They must not silently override newer LaTeX wording or result values.
4. Experiment values must come from the current contract-v2 result namespace or a named later contract. Values must not be copied from legacy figures by visual estimation.
5. A wording change that alters the claim, analysis unit, population, condition, method definition or uncertainty interpretation requires a cross-section search before compilation.
6. A figure change requires simultaneous review of its Results paragraph, caption, alt text, table cross-reference and Supplementary reference.
7. Generated PDFs are updated only after successful compilation and visual QA.
8. The release branch is synchronized only after the canonical local source passes content and layout checks.

## 2. Core Scientific Position

1. CK4P-MSP is a compact, training-free and block-decomposable short-read representation for representation-level perturbation auditing.
2. Its contribution is the explicit separation and conditional audit of canonical local k-mer composition (K), global biochemical summaries (P) and multi-scale positionalized property summaries (MSP).
3. The contribution is not first use of k-mer/property fusion, a new biological law, a clinical diagnostic system, a production classifier or a replacement for alignment and database matching.
4. The principal value is attributable trade-off analysis across stability, local-change readability, composition-linked retrieval, compactness and implementation cost.
5. CK4P-MSP is not required to minimize drift or maximize predictive accuracy. PseKNC and fitted PCA/SVD define lower-drift boundaries; full-position encodings define higher positional-readout boundaries.
6. Database-linked exact matching and alignment remain the appropriate identity-evidence backbone for fine taxonomic, allele-level, ARG/SNP and curated biological interpretation tasks.
7. Learned DNA embeddings may offer stronger predictive features. Their predictive strength and CK4P-MSP's block-level auditability are distinct evaluation objectives.

## 3. Evidence Hierarchy And Permitted Verbs

### Level A: Direct prespecified evidence

Use for prespecified matched-grid or grouped analyses with declared units and methods.

Permitted verbs: `showed`, `reduced`, `increased`, `retained`, `was associated with`, `was higher/lower under the tested grid`.

Required qualifiers: dataset or grid, metric, analysis unit and direction.

### Level B: Robustness or sensitivity evidence

Use for weight scans, scaling variants, mutation-fraction sweeps, estimator sensitivity, counterfactual channels and dependent target-task summaries.

Permitted verbs: `supported`, `was consistent with`, `remained stable across`, `provided descriptive evidence`, `delimited`.

Do not use: `validated`, `confirmed universally`, `proved`, `established generalization`.

### Level C: Boundary or negative evidence

Use for PseKNC lower drift, PCA/SVD lower drift, full-position upper bounds, distance-ratio non-advantage, N-mask scaling failure and ARG/SNP limits.

Required function: define what the method does not optimize and prevent a one-metric superiority narrative.

### Level D: Future hypothesis

Use for pipeline triage, false-hit reduction, candidate-aware secondary models, adaptive MSP weighting and learned-embedding comparisons.

Required wording: `future work should test`, `could be evaluated`, `remains to be determined`.

Never report Level D as demonstrated utility.

## 4. Statistical Language Contract

1. Always name the analysis unit: read, source template/group, matched length-by-perturbation cell, length-by-local-mode cell or target-task definition.
2. Template-grouped cross-validation must state that all derivatives of one template remain in one fold.
3. Matched-cell bootstrap intervals quantify variation across the controlled analysis grid, not uncertainty across independent biological cohorts.
4. CAMI cross-target summaries use six dependent target definitions from one source pool. Their bootstrap intervals and signed-rank calculations are descriptive sensitivity summaries, not independent-community inference.
5. A `P` or `q` value must be accompanied by the tested contrast, unit, sidedness where relevant and multiple-testing procedure.
6. `Significant` is used only for a prespecified statistical test whose assumptions and analysis unit are defensible. Prefer exact effect size and interval in Results.
7. MI values are estimator-dependent empirical separability estimates. Do not call them information-theoretic lower bounds or universal information gain.
8. KSG-style estimates must retain the estimator, `k`, subsampling/permutation design and finite-sample boundary in Methods or caption.
9. Undefined ratios caused by near-zero nuisance denominators remain undefined/unstable; they are not converted into large finite advantages.
10. Three-decimal values are reported only when supported by the source table and useful for comparison. Avoid pseudo-precision in interpretive prose.

## 5. Terminology Ledger

Use these exact terms consistently:

- `canonical local k-mer composition` for CK4/CK5 evidence.
- `global biochemical property block` or `global biochemical summaries` for P.
- `multi-scale property pooling` and `coarse positionalized property summary` for MSP.
- `standardized diagnostic drift` for block-normalized mixed-space L2.
- `grouped local-change readout` for the template-grouped local-versus-nuisance probe.
- `composition-linked nearest-clean retrieval` for the retrieval audit.
- `source-grouped fixed-head tasks drawn from a shared source pool` for CAMI_TOY_low.
- `anonymous-read stability probe` for the lightweight CAMI II marine analysis.
- `descriptive cross-target contrast` for dependent CAMI target summaries.
- `related but non-equivalent` for the P/MSP relationship.

Restricted terms:

- `identity`: reserve for database-linked exact/near-exact matching, alignment or explicitly identified sequence evidence. CK4 alone is not exact read identity.
- `diagnostic`: use as `representation diagnostics` or `diagnostic drift`; do not imply patient diagnosis.
- `robustness`: pair with the tested perturbation and metric; prefer `lower drift` when reporting a numerical result.
- `stability`: specify geometric stability, simulator stability or preprocessing stability.
- `readability`: identify the probe and label contrast; it is not predictive utility by itself.

Prohibited without new evidence:

- `orthogonal biological axes`, `independent physical dimensions`, `universal necessity`.
- `mathematically superior`, `proved`, `theorem`, `causal biochemical mechanism`.
- `clinical validation`, `clinical sensitivity/specificity`, `false-positive reduction`.
- `state of the art`, `best`, `outperforms all`, `production-ready`.
- `restores position`, `recovers full positional information`.

## 6. Representation And Metric Definitions

1. K, P and MSP dimensions, coordinate definitions, normalization order and default weights must agree across equations, text, tables, code documentation and figure labels.
2. Each block is normalized internally before fixed-weight concatenation; the denominator depends only on declared weights, not read-specific concatenated energy.
3. Mixed L2 is an algebraic standardized drift under the declared representation contract. It does not make heterogeneous coordinates physically commensurate.
4. P and MSP are correlated because they use related property maps. CCA/correlation evidence supports non-equivalence, not independence.
5. The 2+3+4+6 binset is a prespecified coarse-to-fine summary and is not described as biologically optimal.
6. Static weights are declared defaults. Sensitivity scans test fragility and do not retrospectively optimize the main result.
7. MinHash is evaluated in native Jaccard/signature-agreement geometry and is not presented as an L2-vector baseline.
8. Hashed and random-projection high-k controls are compactness-constrained vector baselines, not substitutes for production high-k matching systems.

## 7. Read-Length And Data-Provenance Contract

1. The dense shared-template sweep covers every integer length from 50 to 75 bp.
2. The 100, 125 and 150 bp conditions are broader anchors. Do not call the design a continuous 50--150 bp sweep.
3. ART includes 50, 60, 69, 75, 100, 125 and 150 bp and supports within-length ordering, not a monotonic causal length law.
4. The 69 and 75 bp points reflect aggregate local pre/post-QC length provenance and fall within a published 50--75 bp mNGS regime.
5. No patient-level sequence, identifier, label or clinical outcome is an experimental input.
6. CAMI_TOY_low provides coarse labelled fixed-head readout. It is not fine taxonomic validation.
7. CAMI II marine provides external anonymous-read stability only in the current lightweight analysis.
8. Marine composition differs from pathogen-rich or low-biomass mNGS contexts; report this as a composition-shifted public-source probe, not clinical generalization.

## 8. Section-specific Writing Contract

### Title

- Name the object and methodological action. Avoid clinical or universal-performance language.

### Abstract

- Maximum 250 words.
- Include problem, representation, principal ablation, core quantitative result, external boundary and bounded implication.
- Do not include unqualified significance language, unsupported utility or methods not reported in the paper.
- Any CAMI difference must be marked descriptive and source-grouped.

### Introduction

- Move from biological context to exact matching, compact/vectorized methods, biochemical/hybrid descriptors, learned representations and the unresolved audit problem.
- Cite prior composition-property and position-aware feature engineering so originality is not framed as first fusion.
- End with a positive methodological contribution, explicit audit axes and study boundary.
- Do not use related work as a sequence of model summaries without connecting each family to the paper's question.

### Materials and Methods

- Define the method before evaluation.
- Provide equations as display equations with vector/scalar notation distinguished.
- Report data scale, labels, taxonomic rank, preprocessing, grouping, seeds, software versions and hardware for runtime.
- Separate prespecified analyses from sensitivity analyses.
- Avoid result interpretation beyond rationale and analysis contract.

### Results

- Each subsection begins with the question or contrast, then reports numbers, then gives one bounded interpretation.
- Lead with effect size and direction, not adjectives.
- Include negative and boundary results where they define the operating profile.
- Do not repeat general scope disclaimers after every result.
- Do not introduce methods or datasets absent from Methods.

### Discussion

- Synthesize division of labour among K, P and MSP and position CK4P-MSP against historical, compressed high-k, fitted-reduction and full-position boundaries.
- Explain why lower drift is not the sole objective and why grouped local-change readability matters.
- Distinguish demonstrated implications, limitations and future hypotheses.
- Avoid repeating Results numerically unless the number is essential to the interpretation.

### Limitations And Future Work

- Limitations must identify the affected inference, not merely apologize.
- Future work may include pipeline integration, adaptive weighting, richer errors and learned embeddings, but must not imply completed benefit.

### Conclusion

- Restate the tested contribution and trade-off in one compact paragraph.
- Do not introduce new metrics, datasets, applications or superiority claims.

## 9. Figure Content Contract

1. Every main figure must support one sentence-level conclusion stated before plotting.
2. A panel remains in the main paper only if removing it would weaken the core argument.
3. Main figures prioritize mechanism, conditional contribution and operating boundaries over exhaustive method lists.
4. Methods displayed in a panel must be commensurable under the plotted metric. Non-commensurable methods require a separate panel or supplementary audit.
5. Negative results are retained when they define a boundary; they must not visually dominate the central contribution without explanatory context.
6. Axis labels use the same metric names as Methods. Directionality must be stated in the caption.
7. Point, bar, line and error-bar meanings must be defined. Captions identify the analysis unit and whether intervals are descriptive grid variation or cohort inference.
8. Legends must not cover data, titles, annotations or error bars.
9. Text inside figures must remain legible at final printed width; avoid shrinking a large canvas to solve layout.
10. Export figures with tight bounding boxes and proportionate margins. Large unused internal whitespace is prohibited.
11. Do not use truncated axes to exaggerate small differences without an explicit reason and visual cue.
12. Main-figure colour assignments remain consistent for CK4, CK4+P, CK4+MSP, CK4P-MSP and external baselines across figures.
13. Alt text states the visual conclusion and the main boundary; it does not repeat the caption verbatim.
14. Quantitative main figures use the canonical method palette: CK4 `#5B677A`, CK4+P `#2F6BDE`, CK4+MSP `#009E73`, CK4P-MSP `#B83A62` and CK5 `#7456A4`. Conceptual channel colours in Figure 1 are semantic and must not be reused as conflicting quantitative method marks.
15. Repeated observations, aggregate summaries and pair links use distinct visual grammar. In target-task panels, neutral circles denote task-level observations, method-coloured diamonds denote cross-target means and pale lines preserve pairing; all three symbols must be defined in a shared legend.

## 10. Current Main-Figure Roles

1. Figure 1: define K/P/MSP workflow, audit axes and read-length regime.
2. Figure 2: show seven-group conditional division of labour across drift, grouped local-change readout and retrieval.
3. Figure 3: compare compact stability and dimension against composition and dimension-matched high-k vector controls.
4. Figure 4: separate ART simulator stability from CAMI shifted fixed-head readout and relative retention.
5. Figure 5: define full-position positional-readout upper bounds and dimensional cost.
6. Figure 6: show MSP-associated grouped local-change readability while retaining raw distance ratio as a non-advantage boundary.

## 11. Table Contract

1. Tables report exact values that would be difficult to recover from figures.
2. Main tables contain only values needed for the core narrative; complete grids and metadata belong in Supplementary Data or machine-readable files.
3. Column headers include metric, direction or unit where ambiguity is possible.
4. Captions define averaging, minima, sample/cell counts and dependence structure.
5. Decimal precision is consistent within each metric.
6. Tables must not repeat a figure without adding exact values, metadata or statistical detail.
7. Taxon identifiers must include scientific name and rank in a supplementary metadata table.

## 12. LaTeX And Page-layout Contract

1. Compile with the current OUP authoring template and only packages required by the source.
2. Core equations use display math; raw code-style equations are prohibited.
3. Figures should appear within one page of first substantive discussion where float mechanics allow.
4. Avoid figure-only pages unless a figure genuinely requires a full page for legibility.
5. Prevent stranded section headings, captions detached from figures and tables split into unreadable fragments.
6. Use full-width floats only for genuinely wide or multi-panel content. Compact content should use a column-width float.
7. Do not enlarge figure canvases to fill pages. Page occupancy follows information density.
8. Reduce avoidable page whitespace by separating oversized float groups, adjusting float width/height and allowing compact tables to backfill pages.
9. End-of-document whitespace is acceptable when no subsequent content can validly backfill it; internal half-empty pages require justification.
10. After compilation, inspect every page for overlap, clipping, unreadable labels, orphan headings, float backlog and disproportionate blank space.
11. Compiler warnings are triaged: undefined references/citations, oversized floats and content overflows are blockers; harmless template font substitutions are recorded but do not by themselves block submission.

## 13. Language Style Contract

1. Use concise, declarative scientific prose. Prefer subject--verb--result order.
2. Keep one primary claim per sentence and one logical function per paragraph.
3. Use transitions to express causal or contrastive logic, not decorative phrasing.
4. Avoid promotional adjectives, rhetorical questions, reviewer-facing language and internal process narration.
5. Avoid repeated negative constructions. State the tested role positively, then state the boundary once.
6. Maintain one spelling convention. The current manuscript uses British forms where variants differ (`analysed`, `behaviour`, `labelled`, `licence`). Technical `-ize` forms may remain when standard in the field, but variants must not alternate casually.
7. Abbreviations are expanded at first occurrence in the Abstract and independently at first occurrence in the main text when required.
8. K, P, MSP, CSP, MI, KSG, ART, CAMI, EIIP, PCA and SVD must retain one expansion and one capitalization.
9. Use en-dash-like LaTeX ranges (`--`) for numeric ranges and hyphens for compound modifiers.
10. Avoid anthropomorphic or adversarial wording such as `defends`, `proves critics wrong`, `harder to dismiss` or `reviewer-proof`.

## 14. References And Attribution Contract

1. Cite original method papers for tools, estimators, benchmarks and representation families.
2. Cite current final publication metadata where available; preprints are labelled accurately.
3. Methods citations must appear where ART, CAMI, KSG/Ross, Wilcoxon, Benjamini--Hochberg and NCBI Taxonomy are defined.
4. Literature statements must distinguish use of biochemical encodings from evidence that a specific numerical property is causal.
5. Reference entries require authors, title, venue, year, volume/pages or article number and DOI where available.
6. The Yang mNGS book citation must preserve the English title, Chinese-language status, publisher and cited page.

## 15. Back Matter And Submission Contract

1. Author names, affiliations, correspondence and ORCID must match the submission system.
2. Do not invent funding, ethics approval, acknowledgement or contributor roles.
3. A final funding statement is mandatory after author confirmation, even if it states that no specific funding was received.
4. Conflict of interest currently states no competing interests and changes only with author confirmation.
5. Data and Code Availability must identify the exact repository, access status, licence and archival DOI/public release plan.
6. Restricted local records are described only as aggregate length provenance; their sequence data are outside the study package.
7. Supplementary figure/table counts must match the compiled file.
8. Visible `TBD`, `must be finalized`, local-only paths and inaccessible reviewer instructions are submission blockers.

## 16. Claim Propagation And Cross-section Consistency

1. Maintain a single claim hierarchy across the title, Abstract, Introduction, Results, Discussion and Conclusion. No later section may silently strengthen an earlier claim beyond its evidence level.
2. The Abstract reports the narrowest defensible version of each principal conclusion. It must not convert a descriptive comparison into independent validation or a probe result into application utility.
3. The Introduction may state the research gap and intended contribution, but must not pre-announce a result as established fact.
4. Results state observed effects under named conditions. Discussion may interpret those effects but must preserve the same population, perturbation, representation and analysis-unit boundaries.
5. The Conclusion may be broader in significance than a single Results sentence only when it explicitly retains the tested short-read and perturbation scope.
6. Any change to one of the following triggers a full-text search and cross-section update: `identity`, `diagnostic`, `robustness`, `stability`, `information`, `generalization`, `external`, `independent`, `optimal`, `efficient`, `short read`, or any named baseline.
7. Quantitative values appearing in more than one section must be sourced from one machine-readable result and formatted consistently. Manually duplicated numbers require a post-edit equality check.
8. A claim that appears in the Abstract or Conclusion must have a direct Results paragraph and a main-text figure/table or an explicitly named supplementary result.
9. A limitation that materially changes interpretation must appear at first interpretation in Results or Discussion, not only in a late limitations paragraph.

## 17. Dataset And Experiment-role Separation

1. Assign one primary inferential role to each data layer before writing: method development, controlled perturbation, simulator consistency, labelled external readout, anonymous external stability, boundary analysis or sensitivity analysis.
2. Do not pool data layers with different labels, generators or dependence structures into one inferential population unless the pooling rule was prespecified and justified.
3. WGS-derived controlled pairs support perturbation-mechanism analysis, not direct clinical or environmental prevalence claims.
4. ART supports simulator-derived error consistency. It does not independently validate real sequencing physics or clinical performance.
5. CAMI_TOY_low supports coarse, source-grouped labelled readout under the constructed fixed-head tasks. It does not support strain-complete, community-level or independent-cohort generalization.
6. CAMI II marine supports anonymous external stability under a composition-shifted public source. Without labels, it cannot support accuracy, taxonomic recall or biological utility claims.
7. Local aggregate read-length provenance motivates tested lengths only. It is neither a dataset layer nor validation evidence.
8. Training, tuning, threshold selection and final reporting sets must be named. If no tuning occurred, state that parameters were prespecified rather than implying validation-set optimization.
9. Random seeds, source-template grouping and repeated derivatives must be described so that no derivative of one source can leak across training and test folds.
10. If a data layer is removed from a figure, verify that no surviving caption, Results sentence or Supplementary cross-reference still assigns evidence to it.

## 18. Baseline Fairness And Comparison Contract

1. Every baseline must have a declared role: historical descriptor, matched-dimension compact baseline, fitted reduction, high-k compressed vector, sketch/matching method, learned representation, positional upper bound or counterfactual control.
2. Compare methods only on metrics that are native or defensibly standardized for all methods in that panel. State when a metric is an audit convenience rather than a method's conventional operating metric.
3. Match feature dimension, training access, fitting data, preprocessing, distance function and downstream probe where the scientific question requires resource-bounded comparison.
4. When exact matching, sketches or database classifiers are discussed but not directly benchmarked, state the task mismatch. Do not present their absence as evidence of CK4P-MSP superiority.
5. PCA/SVD are fitted-reduction controls and must disclose the fitting split. They are not training-free baselines.
6. Hashed/random-projection k=15 vectors test compact high-specificity composition under a severe dimension budget. They do not represent the full performance of production high-k indexing.
7. PseKNC/PseEIIP are historical property-aware descriptors. If either has lower drift, report that boundary plainly rather than selecting only readout metrics that favour CK4P-MSP.
8. Full-position encodings are diagnostic upper bounds with higher dimensional cost, not ordinary peers expected to lose to the compact method.
9. A learned embedding comparison, if added later, must disclose model version, pretraining source, pooling, truncation, projection fitting, hardware and whether the encoder was frozen. It must not be compared as if training cost were zero.
10. Runtime comparisons must use the same hardware, process count, input representation, I/O policy, warm-up policy and read batch. Extrapolated values must be labelled as extrapolated.
11. Never infer superiority from a single metric when methods were designed for different objectives. Report the relevant trade-off profile.

## 19. Ablation, Redundancy And Attribution Contract

1. The minimum internal comparison set for the main method is K, K+P, K+MSP and K+P+MSP. P-only and MSP-only may remain supplementary when they answer block behaviour rather than deployment configuration.
2. Attribute P primarily to global property stability only when K+P differs from K under the prespecified drift audit and the result survives the declared sensitivity checks.
3. Attribute MSP to coarse positionalized local-change readability only when K+MSP or K+P+MSP improves the grouped probe relative to the appropriate non-positional counterpart.
4. Do not call P and MSP statistically independent, orthogonal or universally necessary. Their permitted interpretation is `related but non-equivalent`.
5. Correlation/CCA audits quantify shared and residual structure. They do not prove mechanistic independence or causal information channels.
6. The necessity of both P and MSP is task-conditional: the joint method is justified by a multi-objective profile, not by requiring each block to win every metric.
7. Permuted and Gaussian property controls test whether gains arise from sequence-linked structure rather than added dimensions. They do not establish biological causality.
8. Block-weight and bin-count scans are sensitivity audits. Do not retrospectively select the best setting and report it as the prespecified main method.
9. If an ablation result contradicts the proposed division of labour, pause prose revision and reassess the claim before changing figures.

## 20. Negative, OOD And Boundary-result Contract

1. Distinguish three outcomes: lower geometric drift, retained task-relevant signal and downstream transfer. One does not imply the others.
2. N-mask results must state whether the probe was contract-space unscaled or train-z-scored. A scaling-induced transfer failure is not evidence that the raw representation lost all information.
3. If both unscaled and scaled probes degrade, report a genuine out-of-distribution limitation of the affected block.
4. Near-zero denominator ratios are marked `undefined` or `unstable`; they must not be plotted as extreme finite wins.
5. A method that loses on minimum drift may still be useful if it retains local-change readability, retrieval or interpretability under a compact budget. This trade-off must be shown, not asserted.
6. A method that wins a shallow probe but has unstable drift must not be described as robust without a separate perturbation analysis.
7. Fine-label, ARG/SNP, clinical and pipeline effects remain outside demonstrated scope unless directly measured with suitable labels and analysis units.
8. Boundary findings should be positioned beside the corresponding positive result so the reader can evaluate the operating profile without searching the Limitations section.

## 21. Reproducibility, Runtime And Artifact Contract

1. Each main and supplementary quantitative output must map to one script entry point, one configuration, one result table and one plotting script.
2. The repository must contain a manuscript-to-script/result/figure mapping and a minimal reproduction path for every main figure and table.
3. Method defaults in the paper, standalone script, reusable module and repository documentation must match exactly.
4. Record Python and dependency versions, random seeds, hardware, thread/process counts and operating-system-relevant settings for runtime and stochastic analyses.
5. Runtime must be measured directly at the reported batch size whenever feasible. Otherwise report the observed batch and label any larger value as a linear equivalent extrapolation.
6. Separate algorithmic compute time from download, database construction, file decompression and figure generation.
7. Public-source inputs require stable identifiers, checksums or retrieval metadata where feasible. Locally generated intermediates require deterministic generation instructions.
8. Machine-readable result tables are authoritative. Figures are views of those tables and must not contain hand-edited numerical positions.
9. Before release, run a clean-environment smoke test from documented entry points and verify that output schemas match the manuscript mapping.
10. The review repository may remain private before submission only if reviewers can receive reliable access. The archival DOI/public release must be completed at the declared submission or acceptance stage required by the journal.

## 22. Figure Production And Visual QA Contract

1. Before plotting, write a one-sentence figure claim, panel question, required comparisons, direction of benefit and known boundary. A plot without this contract is not generated.
2. Choose single-column or full-width placement from information density. A two-panel figure is not automatically full width, and a wide figure is not automatically a useful figure.
3. Regenerate figures at the intended final aspect ratio. Do not use LaTeX scaling to compensate for an excessively wide or short source canvas.
4. Crop exports to content with a tight bounding box. Unused plotting area, empty legend zones and decorative margins must be removed at source.
5. No panel should reserve substantial blank space for absent data or a removed legend. Rebalance subplot widths after any method or panel is removed.
6. Shared legends belong outside data regions when internal placement obscures points, lines, annotations or titles. Panel-specific legends are used only when the encodings differ.
7. Axis limits must be chosen from the inferential question. Zero baselines are used where absolute magnitude matters; truncated ranges require visible justification and must not exaggerate negligible effects.
8. Method order, colour, marker and line style remain stable across figures. Colour must not be the only carrier of meaning.
9. At final displayed width, labels, ticks, panel letters and annotations must remain legible and must not collide. Enlarging the PDF viewport is not a substitute for print-scale inspection.
10. Multi-panel labels are placed consistently and do not compete with titles. Avoid repeating panel letters inside both the source figure and LaTeX subcaptions.
11. Captions describe panel content, data layer, length/perturbation, analysis unit, sample or cell count, interval/error-bar meaning, metric direction and abbreviation expansions. Captions do not contain extended Discussion.
12. Main-article alt text is concise, states the pattern and boundary, and is stored directly with the corresponding figure legend for submission.
13. Every figure passes three reviews: numerical source check, scientific role check and rendered-page visual check.
14. Review the actual composite output, not individual panels only. Composite assembly can introduce clipped labels, inconsistent fonts and disproportionate whitespace.
15. Supplementary figures follow the same visual standard as main figures. `Supplementary` is not a waiver for unreadable or weakly motivated plots.
16. High-resolution editable/vector source files are retained. Raster output is used only when the content genuinely requires it.

## 23. Current NARGAB Submission-compliance Snapshot

Checked against the official NAR Genomics and Bioinformatics author guidance on 2026-07-30. Recheck before submission.

1. The intended route is a Standard Paper containing a novel method, not a claim to a production clinical classifier.
2. NARGAB uses single-anonymized review. Author names and affiliations remain in the submitted manuscript; a blinded manuscript is not currently required.
3. Initial submission may use one complete PDF with main text, references, tables and figures embedded. Supplementary Data are uploaded separately.
4. The LaTeX source uses the OUP `Modern Large` template. The PDF is required initially; native source files may be requested at revision.
5. Pages are numbered. Do not add line numbering or footnotes to the initial manuscript.
6. Main figures and legends are embedded near their first substantive discussion for reviewer readability. High-resolution composite figure files are retained for upload.
7. Alt text is required for every main-article image and must be included under the corresponding legend in the submission manuscript.
8. Supplementary items must all be cited in the main text. The preferred Supplementary PDF size is below 5 MB where feasible without harming legibility.
9. Novel bioinformatics components must be open source and follow FAIR-oriented usability expectations. Data/code statements cannot rely only on `available on request`.
10. The submitting author must provide an ORCID. All author identities, contributions and order must be confirmed before submission.
11. Any AI-assisted language, code, analysis or image use must be disclosed in the cover letter and in the manuscript location required by the current journal policy. The authors must verify all affected content.
12. Related manuscripts, reused third-party content, permissions and unresolved intellectual-property matters must be settled before submission.
13. Submission readiness requires actual reviewer-accessible repository information. A placeholder Git link or inaccessible local path does not satisfy reproducibility review.
14. Official sources of truth: `https://academic.oup.com/nargab/pages/author-guidelines` and `https://academic.oup.com/nargab/pages/scope_and_criteria`.

## 24. Final Acceptance Gates

The manuscript may be labelled submission-ready only when all gates pass:

- [ ] All quantitative claims trace to a current result table.
- [ ] Every Abstract/Conclusion claim has a direct Results and figure/table anchor.
- [ ] Abstract is at most 250 words.
- [ ] No cross-section contradiction in method role, dataset scale, read length, analysis unit or claim strength.
- [ ] Every dataset is used only for its declared inferential role.
- [ ] Every baseline has a declared role and a fair metric/preprocessing contract.
- [ ] K, K+P, K+MSP and K+P+MSP support the stated task-conditional attribution.
- [ ] Negative/OOD findings are reported where they delimit the positive claim.
- [ ] No undefined LaTeX citations or references.
- [ ] All figures pass content-role, legibility, tight-bounds and no-overlap checks.
- [ ] Main figures include alt text and self-contained captions with analysis units and interval meanings.
- [ ] No avoidable internal half-empty pages, stranded headings or float backlog.
- [ ] Main and supplementary captions are self-contained.
- [ ] Runtime values are direct measurements or explicitly labelled extrapolations under a documented hardware/software contract.
- [ ] Main outputs map to reproducible scripts, configurations, results and plotting entry points.
- [ ] Funding and institution-specific ethics wording are author-confirmed.
- [ ] Repository access works for reviewers; public DOI plan is stated.
- [ ] AI-assistance disclosure is author-reviewed and placed according to current journal policy.
- [ ] Canonical source, generated PDFs and release branch are synchronized.
