# Continuity Ledger

Use this file to keep the split drafts coherent.

## Locked positioning

- Paper type: methods-oriented representation diagnostics paper.
- Core claim: the paper diagnoses what information remains available in ultra-short read representations under controlled perturbation, rather than introducing an end-to-end clinical classifier.
- Main method: CK4P-MSP.
- Role of full-position matrices: diagnostic upper bound, not deployment recommendation.
- Role of CSP: mechanistic or boundary comparator, not novelty center and not a "failed method".

## Locked scope

- Preferred scenario phrase: `controlled short-read (69-150 bp) mNGS-motivated settings`.
- Do not use `clinical-like` in the revised core draft.
- Do not claim clinical validation.
- Do not claim replacement of exact matching, alignment, or curated database methods.
- Do not claim CK4P-MSP is a universal readout winner.

## Locked terminology

- `canonical local k-mer composition backbone`
- `biochemical side channel`
- `multi-scale property pooling`
- `diagnostic upper bound`
- `delta-readout`
- `controlled perturbation`
- `paired cosine`
- `L2 drift`

## Word-choice constraints

- Prefer `controlled short-read (69-150 bp) mNGS settings` or `controlled short-read mNGS-motivated settings`.
- Prefer `consistent evidence` or `a consistent body of evidence`, not `decisive evidence`.
- Prefer `could serve`, `may support`, `is consistent with`, or `suggests` when the claim is bounded.
- Prefer `fine-grained positional information` over `fine positional information`.
- Prefer `scenario-specific` or `condition-specific` over vague `regime-specific` unless the regime is explicitly named.
- Use `canonical local k-mer composition` for CK4/CK5. Reserve `exact matching evidence` for database- or alignment-based systems.
- Prefer `auxiliary channel`, `auxiliary descriptor`, or `auxiliary summary`, not `replacement`.

## Avoid list

- `clinical-like`
- `decisive evidence`
- `standalone winner`
- `replace`
- `solve everything`
- `black box` as a casual accusation
- `first` / `unprecedented` unless separately verified

## Sentence-level style

- Keep paragraph topic sentences short and assertive.
- Prefer two medium-length sentences over one very long sentence when introducing a new claim.
- Use semicolons sparingly and only to join tightly linked technical clauses.
- Use em dashes only when the interruption is genuinely clarifying; otherwise prefer commas or a new sentence.
- When a sentence contrasts two representation families, name the axis of contrast explicitly: identity, stability, position, dimension, or diagnostic readability.

## Evidence priorities

- Stability claims should center on paired cosine and L2 drift.
- Local mutation claims should center on grouped delta-readout. Selective-sensitivity ratios are a boundary metric and must not be presented as a CK4P-MSP advantage.
- Retrieval can appear as a supporting identity-preservation metric, but not as the lead inferential result.
- The central ablation is CK4 versus CK4+P versus CK4+MSP versus CK4P-MSP: P and MSP reduce drift, MSP carries most local-change readout, and the combined representation is the compact trade-off.
- Do not describe CK4P-MSP as globally most stable: CK4+P is more stable on the current global perturbation grid.
- MinHash is a native collision/Jaccard control, not an L2-vector or shallow-readout baseline.

## Figure policy

- Each main figure should answer one question.
- Complex labels belong in legends, tables, or captions, not next to plotted points.
- The old spaced-seed main-text figure is removed.
- A freed main-figure slot should serve reviewer-response evidence, not legacy support plots.

## Paragraph jobs

- Abstract: context -> gap -> approach -> strongest result -> bounded implication.
- Introduction: problem -> prior routes -> gap -> present study.
- Methods: study design -> data layers -> representation families -> metrics/statistics -> reproducibility.
- Results: one question per subsection.
- Discussion: contribution -> interpretation -> limits -> bounded use case.

## Cross-section reminders

- If a limitation is introduced in Abstract or Introduction, it must reappear in Discussion.
- If a method role is defined in Introduction, keep the same role wording in Methods and Results.
- If a result is softened in Discussion, make sure the Abstract does not overstate it.

## NAR/OUP Manuscript Constraints

Source to re-check before submission: Nucleic Acids Research / Oxford Academic Author Guidelines (`https://academic.oup.com/nar/pages/General_Instructions`). Treat these as hard manuscript assembly constraints for `paper_manuscript.docx`.

- Manuscript order should follow NAR convention: Title page, Abstract, Introduction, Materials and Methods, Results, Discussion/Conclusion, Data Availability, Funding, Acknowledgements/Author Contributions when required, Conflict of Interest, References, Tables and Figure legends/embedded figures as allowed by submission stage.
- The main DOCX should be single-column and single-spaced, with clean heading hierarchy and no line numbering or text footnotes unless the journal workflow specifically requests them.
- Materials and Methods should precede Results. Our `03_method_experiments.md` may remain a working combined file, but `paper_manuscript.docx` must split its content into `Materials and Methods` and `Results` sections.
- Figures and tables must be numbered consecutively in the order cited. Each main figure should answer one manuscript question; supplementary figures should carry baseline audits, MI/error-aware support, and sensitivity checks that are important but not the central narrative.
- Data Availability is mandatory. It must explicitly separate: newly generated processed outputs and scripts; reused public resources such as ART/CAMI where applicable; and the restricted clinical sequencing provenance, which motivated the 69/75 bp length conditions but was not used as experimental input and cannot be publicly shared.
- Citation formatting for final submission should be converted from temporary Pandoc-style keys such as `[@kraken]` to the journal-required reference style. Do not leave citation keys in the final submission copy.
- Use restrained NAR-style claims: methods/results language should remain precise, reproducible, and bounded; avoid marketing phrasing and clinical-validation language.
- DOCX assembly QA must check three gates before delivery: formatting/template consistency, figure/table readability without label overlap, and writing consistency across Abstract, Introduction, Methods/Results, Discussion, and Data Availability.

## Open Reviewer-Risk TODOs: P-channel Validity

These items must stay visible before the next manuscript/DOCX rebuild.

- Reframe global L2 as `standardized diagnostic drift`, not as a natural biophysical distance in a heterogeneous feature space.
- Add a block-weighted distance definition: `d_w^2 = alpha^2 ||delta K||_2^2 + beta^2 ||delta P||_2^2 + gamma^2 ||delta MSP||_2^2`.
- Add a `CK4 + random/permuted property block` control to test whether the observed stability gain can be reproduced by low-variance dilution alone.
- Add block-wise drift reporting for identity, biochemical and MSP blocks instead of relying only on global L2.
- Add a 69/75 bp pooled-feature reliability audit: bootstrap variance or confidence intervals for P/MSP pooled features by read length and bin scale.
- Treat MI/conditional MI as estimator-dependent empirical support under the tested perturbation grid, not as a universal information-theoretic proof.
- In Results, make the claim conditional: KSG-style distance summaries show empirical local-versus-noise separability beyond CK4 under the tested grid. Do not rely on legacy permutation/Gaussian-block controls until they are regenerated under the public contract.
- In Discussion, explicitly acknowledge that heterogeneous concatenation is an engineering diagnostic representation, not a claim of equal physical units across k-mer and biochemical summaries.

## Open Reviewer-Risk TODOs: Dataset Scale and Simulation Rationale

- Add an explicit dataset-scale paragraph or table in Methods. It must report rows/read templates, length grid, genera/species or label counts, perturbation conditions and whether the layer is controlled WGS, ART simulator, CAMI external probe or local-mutation triplet analysis.
- Explain why the study uses controlled simulation/perturbation layers: the paper diagnoses representation behavior under known perturbation mechanisms, so controlled pairs are necessary to separate nuisance stability, identity retention, positional readability and local mutation sensitivity.
- Explain the boundary of lightweight CAMI use: CAMI_TOY_low is an external readability probe and not a claim of production-scale clinical benchmarking.
- Keep the 69/75 bp restricted clinical provenance separate from dataset scale: restricted clinical reads were not used as experimental input; only the length conditions motivated the design.
- Table 2 should either be expanded with scale columns or accompanied by a dedicated dataset-scale table before manuscript submission.

## Open Reviewer-Risk TODOs: P/MSP relation audit and provenance support

- Reserve one supplementary figure for a two-panel P/MSP relation audit combining CCA and a correlation heatmap.
- Use CCA as the shared-latent-structure summary and the heatmap as the pairwise redundancy view. Treat a scatter-matrix layout as optional and secondary.
- Keep the interpretation bounded to "related but not interchangeable"; do not recast the audit as a proof of orthogonality, independence or new physical axes.
- Use Yang's *Practice and Progress of mNGS Report Interpretation* (p. 99) only as background support for the common 50-75 bp post-QC mNGS regime.
- Keep the restricted clinical provenance separate and minimal; if it remains in the manuscript, it should stay as one short length-provenance sentence, not a narrative center.
- Do not repeat the hospital name in multiple manuscript sections once the minimal provenance sentence is set.
- Add explicit CAMI label-hierarchy and background-read handling text in Methods before the next DOCX rebuild.
- Do not reopen the deep-learning benchmark branch unless the manuscript scope is deliberately expanded.

## Open Reviewer-Risk TODOs: Mathematical/Physical Rigor Pass

Status: added after the latest reviewer-style critique. Do not run additional experiments until the user explicitly says to continue.

1. Formula presentation and NAR style
   - Replace the current code-like inline formula `x = [alpha K, beta P, gamma M] / ||...||2` with a display-equation block.
   - Use vector notation for sequence-level block mappings, e.g. `\phi_K(s_i)`, `\phi_P(s_i)`, `\phi_M(s_i)`.
   - Avoid Word-hostile raw LaTeX in the final DOCX unless the builder converts it safely; if not, use equation text blocks with standard mathematical symbols carefully checked in PDF export.

2. Normalization crosstalk / metric definition
   - Clarify that the paper's intended diagnostic metric is assembled from separately normalized blocks with fixed prespecified weights, not an unqualified raw concatenation followed by a read-specific global normalization. Concatenation keeps block coordinates disjoint, but this must not be described as statistical independence or physical orthogonality.
   - Define block-normalized vectors first, then define weighted block distance, preferably: `d_w^2(i,j) = alpha^2 ||Khat_i-Khat_j||_2^2 + beta^2 ||Phat_i-Phat_j||_2^2 + gamma^2 ||Mhat_i-Mhat_j||_2^2`.
   - State explicitly that this is a standardized diagnostic drift, not a natural physical distance equating k-mer counts and biochemical units.
   - Align this formula with actual experiments and with block-wise drift, block-weight audit, and P/MSP counterfactual controls.

3. MSP short-bin noise / gamma sensitivity
   - Do not introduce dynamic weighting as a new main method unless the project is ready to reframe and rerun the manuscript.
   - Dynamic weighting would shift the story toward a weight-optimization algorithm and require additional validation.
   - Instead, run a lightweight MSP bin/gamma sensitivity audit only after explicit user instruction.
   - Candidate script already written but not executed: `info/scripts/run_msp_bin_gamma_sensitivity_audit.py`.
   - Audit design: binsets `2`, `2+3`, `2+3+4`, `2+3+4+6`; gamma `0,0.25,0.5,1,2`; stability mainly at 69/75 bp; delta-readout at 69/100/150 bp.
   - This audit can show whether static MSP is catastrophically sensitive to fine binning or gamma, but it cannot prove dynamic weighting is unnecessary or optimal.
   - If audit is stable, write MSP as a coarse positional summary with a short-read reliability audit. If unstable, downgrade MSP claims and state that length-/variance-aware weighting is future work.

4. MI proxy transparency and pseudo-precision
   - Explain the MI proxy algorithm in Methods: equal-frequency discretization, number of bins, conditional grouping, and permutation baseline.
   - Do not present `0.153 bits` or `0.222 bits` as absolute physical information values; use approximate phrasing and say estimator-dependent descriptive proxy.
   - If time allows, add a light bin-count sensitivity check (e.g. 6/8/10 bins). If not, at least disclose discretization dependence as a limitation.
   - Keep the conclusion bounded: MI/conditional MI supports non-redundant perturbation readability under the tested estimator; it is not a theorem that CK4P-MSP is universally information-superior.

