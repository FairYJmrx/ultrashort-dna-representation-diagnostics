# Revision Action Items Before Submission

This checklist tracks the remaining manuscript-hardening tasks after the reviewer-style critiques of the CK4P-MSP manuscript. It is written for the active paper-folder version only; do not apply these items to `final_manuscript.md`.

Latest execution plan: see `submission_hardening_execution_plan.md`. That file supersedes older open-ended wording on CAMI II, Kraken2/triage, foundation-model benchmarks and application claims.

## Priority 1: Must Fix Before Any Submission

### 1. Mixed-space metric definition and L2 interpretation

- Confirm that the implementation matches the manuscript definition: each identity, biochemical and MSP block is internally L2-normalized before weighted assembly.
- Add or retain the explicit derivation that, if all blocks are unit-normalized, the final concatenated norm is a fixed scalar, `sqrt(alpha^2 + beta^2 + gamma^2)`, not a read-specific denominator.
- State that the global L2 value is a standardized diagnostic drift, not a natural biophysical distance across commensurate units.
- Report or cite block-wise drift decomposition alongside global mixed-space metrics, especially for local mutation sensitivity.
- Make clear that block-weight audits and P/MSP counterfactual controls address dilution by low-variance auxiliary channels.

### 13. Exact mixed-distance condition

- Add the exact block-normalized distance identity to the Methods or Results interpretation: with unit-normalized blocks, the mixed squared drift is a weighted average of block-wise squared drifts, scaled by `1/(alpha^2 + beta^2 + gamma^2)`.
- State the exact condition for a mixed drift to be lower than the identity-only drift: `beta^2(d_P^2 - d_K^2) + gamma^2(d_M^2 - d_K^2) < 0`, with the analogous condition for other block sets.
- Treat `d_P < d_K` and `d_M < d_K` as a sufficient but not necessary condition. Do not overstate this as a universal theorem.
- Pair this derivation with block-weight audit results so the reader can see that the conclusion is not tied to a single hand-picked weighting.

### 2. Display equations and DOCX formula rendering

- Ensure all core equations in `03_method_experiments.md` are display equations, not code-like inline text.
- Ensure the DOCX builder converts equation blocks into readable Word equations or equation-like display paragraphs without `$$` delimiters, broken LaTeX source or garbled symbols.
- Rebuild `paper_manuscript.docx` after formula fixes and run render QA if LibreOffice rendering is available.

### 3. Restricted clinical length provenance and data-governance boundary

- Keep 69 and 75 bp described as length conditions only; avoid reintroducing the hospital name into the main narrative.
- If any restricted provenance statement is retained, confine it to the Data Availability / Ethics area and keep it to one short sentence.
- State explicitly that no patient-level reads, clinical phenotypes or identifiable clinical data were used as experimental input.
- State that the restricted clinical sequencing reads are not part of the study dataset and cannot be publicly shared.
- Keep the wording aligned across Data Availability and Limitations.
- Do not expand the provenance into a separate narrative thread; keep it as a single design note.

### 4. Remove meta-commentary and defensive prose

- Remove working-section language such as "this working section", "reviewer-facing", "not a post hoc reviewer appendix" and other process commentary from the submission manuscript.
- Replace defensive phrasing with objective capability and boundary statements.
- Keep the tone restrained and NAR-style: precise, reproducible and bounded.

## Priority 2: Strongly Recommended Evidence Hardening

### 5. MI and conditional-MI robustness

- Do not present discretized MI values as universal information-theoretic proof.
- Keep the current equal-frequency MI analysis as an empirical proxy only if the estimator, bin numbers, conditioning variables and permutation baseline are stated clearly.
- If MI remains in the Results, add a k-nearest-neighbor/KSG-style MI robustness audit on low-dimensional perturbation summaries such as `d_K`, `d_P`, `d_M`, `d_K+P` and `d_K+P+M`; otherwise remove MI-based information-gain claims from the Results.
- Report repeated subsampling or bootstrap intervals for MI estimates if the kNN audit is added.
- Reduce pseudo-precision in the prose; emphasize qualitative consistency and permutation/subsampling support rather than exact bit values.

### 6. Baseline audit visibility

- Ensure Supplementary Figure S1 is explicitly cited where same-dimension PCA/SVD, hash/sketch and mixed-metric controls are discussed.
- If hash/sketch baselines are already present in the generated audit, treat the reviewer concern as a presentation issue, not a missing-experiment issue.
- If longer-k or minimizer-style compressed baselines are absent, add a small supplementary audit rather than relying only on a scope statement.
- Add a dimension-matched high-specificity k-mer compression baseline: for example, k=15 hashed/MinHash-style features or random-projection k-mer features compressed to approximately the CK4P-MSP feature budget.
- Compare this compressed high-k baseline against CK4P-MSP under the same perturbation grid using paired cosine, L2 drift, retrieval and delta-readout.
- Do not move every baseline into the main figures; keep the main visual line focused and use S1 as the baseline-audit figure.

### 7. MSP bin and gamma sensitivity

- Keep Supplementary Figure S6 as the primary response to short-bin noise and static-weighting concerns.
- State that 69/75 bp did not show catastrophic high-bin collapse under the tested settings.
- State that finer MSP binning improved delta-readout while only slightly changing paired stability.
- Do not claim that static MSP is optimal; describe it as a usable coarse positional summary.
- Put length- or variance-aware MSP weighting in future work rather than introducing it as a new main method.

### 14. P/MSP contribution, redundancy and runtime

- Keep P and MSP framed as related layers from the same biochemical property family, not as independent orthogonal physical axes.
- State the design roles explicitly: P is the global biochemical stability summary, whereas MSP positionalizes the same property family to return coarse layout information to the compact k-mer frequency backbone.
- Cite the direct CK4 / CK4+P / CK4+MSP / CK4P-MSP audit when discussing the division of labor. In the current audit, both CK4+P and CK4+MSP reduced paired L2 drift relative to CK4, while CK4+MSP carried most of the local delta-readout gain.
- Cite the redundancy audit when addressing collinearity. P and MSP share a strong global component, but MSP has higher rank and incomplete row-wise alignment with P; write this as related but not interchangeable.
- Cite the runtime audit as an engineering boundary. CK4P-MSP is still sub-millisecond per read in the local implementation but is slower than CK4 and simple hashed/MinHash high-k summaries, so do not claim a feature-extraction speed advantage.

### 15. P/MSP relation audit and length-regime support

- Reserve one supplementary figure slot for a two-panel P/MSP relation audit combining CCA and a correlation heatmap. Place it after the redundancy discussion and keep it out of the main figure line.
- Use CCA to summarize shared latent structure between P and MSP, and use the correlation heatmap to show pairwise association and redundancy. Keep any scatter-matrix version optional and secondary, not the lead panel.
- Keep the interpretation bounded: this audit should support "related but not interchangeable" language only; do not rewrite it as a proof of orthogonality or independence.
- The implemented source script is `info/scripts/generate_supp_fig_s9_p_msp_relation_audit.py`; the asset should be saved as `paper/figures/supp_fig_s9_p_msp_relation_audit.*`.
- Add a brief Methods sentence noting that 69-75 bp sits inside the commonly reported 50-75 bp post-QC mNGS read-length regime. Use Yang's *Practice and Progress of mNGS Report Interpretation* (p. 99) as background support for the general range, while keeping the restricted clinical provenance separate and minimal.
- In Methods, state the CAMI label hierarchy, the handling of background or unclassified reads, and the rationale for the chosen labeled subset before the next DOCX rebuild.
- Keep any restricted-provenance wording out of the main narrative; do not let it become the narrative center.
- Do not open a new deep-learning benchmark branch to answer this reviewer.
- Keep the CCA/heatmap figure in supplementary material unless the main narrative changes.

### 8. Error-aware perturbation positioning

- Keep ART and quality-stratified ART as simulator-derived consistency checks.
- Do not claim that ART models every clinical sequencing error process.
- Keep uniform substitutions and local mutation sweeps framed as controlled perturbation grids.
- Ensure the Results and Discussion clearly separate controlled WGS perturbations, ART simulator checks, CAMI external probes and clinical validation.

## Priority 3: Scope and Presentation Tightening

### 9. Foundation-model positioning

- Discuss DNABERT, DNABERT-2, Nucleotide Transformer, HyenaDNA, Evo and GENA-LM as representation-context literature, not as models used in this study.
- Avoid implying that the manuscript benchmarked or rejected foundation models.
- If no foundation-model embedding audit is added, explain that the present study focuses on decomposable identity, biochemical and positional channels under short-read perturbation diagnostics.
- A lightweight embedding audit may strengthen the manuscript, but it should not be allowed to shift the paper into a foundation-model benchmark.

### 10. Application and clinical-utility boundaries

- Do not claim that CK4P-MSP replaces Kraken2, alignment, curated databases, ARG/SNP detection or clinical classification.
- Describe possible uses as robustness auditing and representation-level confidence auditing, not direct downstream probability calibration.
- If the manuscript retains the word triage as an application claim, add a pipeline-facing triage audit that measures downstream false hits or false-positive rate changes. If this audit is not added, remove triage language and use representation-level robustness auditing only.
- A triage audit should test whether a CK4P-MSP-derived threshold reduces erroneous downstream assignments, not merely whether it detects heavily perturbed reads.
- Keep ARG/SNP and exact allele detection as boundary cases where exact identity evidence remains essential.
- Avoid adding a full Kraken2-prefilter or clinical pipeline experiment unless the manuscript scope is deliberately expanded.

### 11. Figure and table completeness

- Confirm that each main figure and supplementary figure has a self-contained caption.
- Check all abbreviations, especially CSP, MSP and MI, and ensure that each is defined at first use in both the Abstract and main text.
- Confirm that all figure/table callouts appear in the correct order in the final DOCX.
- Check figure readability for overlapping labels, crowded axes and insufficient legends.
- Keep Table 2 focused on data scale, diagnostic question, metrics and claim boundary; avoid turning it into prose.

### 12. Data, code, references and submission metadata

- Replace local-path-only Code Availability with a submission-ready repository statement before final submission.
- Replace temporary Data Availability placeholders with repository DOI/accession information where available.
- Complete author names, affiliations, funding, acknowledgements, author contributions and conflict-of-interest statements.
- Convert temporary citation keys into NAR/OUP-compliant numbered references.
- Verify all high-risk reference metadata, especially newer works and preprints.

## Mandatory Evidence Decisions

The revision should no longer use open-ended feasibility language for the two core methodological controls.

- High-k compressed k-mer baseline: completed. The dimension-matched k=15 compressed audit should be cited when the manuscript compares CK4P-MSP with high-specificity k-mer summaries under an approximately 222-feature budget.
- MI robustness: completed. MI language may remain only as bounded empirical support, with the kNN/KSG-style audit treated as a robustness check and the older equal-frequency MI values treated as estimator-dependent descriptive proxies.
- Triage: removed from the current application claims. If future versions reintroduce triage, the audit must include downstream false-hit/FPR or incorrect-assignment endpoints, not only perturbation-damage detection.

## Proposed Minimal Triage Audit

If the manuscript keeps an application-facing triage claim, the audit should remain lightweight and representation-level. The goal is not to prove clinical deployment, but to test whether the compact representation can flag reads whose feature evidence is degraded.

- Dataset: use existing clean/perturbed paired reads from the WGS perturbation grid and ART quality-stratified reads. Construct positive/readable examples from clean or low-perturbation reads and low-information examples from heavy perturbation, high-N fractions, severe local mutation, or low-quality ART strata.
- Triage score: compute a representation-level reliability score using nearest-clean similarity, distance to clean-template centroid, or a composite of paired cosine/L2 drift and retrieval margin.
- Baselines: compare CK4P-MSP against CK4, CK5, existing MinHash controls and the new high-k compressed baseline if added.
- Metrics: report downstream false-hit/FPR or incorrect-assignment changes where downstream classifier outputs are available; otherwise do not retain triage as an application claim. AUROC/AUPRC for low-information-read detection may be reported only as a secondary representation-level diagnostic.
- Pipeline-facing endpoint: if Kraken2 or another downstream classifier is used, report FPR, false-hit, incorrect-assignment, unclassified-rate and macro-F1 changes after triage. Do not make clinical claims unless the pipeline experiment is complete and reproducible.
- Manuscript wording: if this audit is not run, remove or downgrade triage claims and use representation-level robustness auditing instead.

## Current Experiment Decision

- No new large-scale experiment is required unless the manuscript scope changes.
- The kNN/KSG-style MI robustness audit has been run and supports a positive empirical increment for joint P/MSP distance summaries beyond CK4 distance. It should not be written as a universal information-theoretic proof.
- The dimension-matched high-k compressed k-mer baseline has been run and supports the stability advantage of CK4P-MSP over k=15 hashed, MinHash and random-projection summaries at approximately the same feature budget. Its shallow-readout advantage is modest and should not be overstated.
- The direct P/MSP contribution audit has been run and supports the division-of-labor framing: global P and MSP both stabilize perturbation drift, while MSP provides most of the local positional delta-readout gain. The redundancy audit has also been run and should be used to avoid any claim that P and MSP are fully orthogonal.
- The runtime audit has been run and should be used as a limitation: CK4P-MSP pays a measurable extraction cost relative to CK4 and simple high-k sketch/hash summaries.
- A pipeline-facing triage audit is not included in the current manuscript. Therefore application-facing triage, downstream FPR reduction and probability calibration claims should be removed from the current text.
- Dynamic MSP weighting, full clinical pipeline integration, foundation-model benchmarking and ARG/SNP validation are future-work or scope-expansion items, not mandatory repairs for the current representation-diagnostics manuscript.

## Completed Evidence Hardening

- kNN/KSG-style MI robustness audit: `info/scripts/run_knn_mi_robustness_audit.py`; output directory `info/results/stage3/reviewer_response/knn_mi_robustness`. Across 12 local-mutation cells, the audit estimated higher MI for the joint `dK_dP_dM` summaries than for `dK` alone, with an average incremental estimate of approximately 0.138 bits beyond `dK` and permutation support. Use this as empirical robustness evidence, not as a formal theorem.
- Dimension-matched high-k compressed baseline audit: `info/scripts/run_high_k_compressed_baselines.py`; output directory `info/results/stage3/reviewer_response/high_k_compressed_baselines`. CK4P-MSP retained higher paired cosine and lower L2 drift than k=15 hashed, MinHash and random-projection baselines compressed to approximately 222 features. Shallow readout was comparable in magnitude, so the manuscript should frame this result as a perturbation-stability advantage under a matched compactness budget.
- P/MSP contribution audit: `info/scripts/run_p_msp_contribution_audit.py`; output directory `info/results/stage3/reviewer_response/p_msp_contribution`. CK4+P and CK4+MSP reduced mean paired L2 drift relative to CK4, CK4P-MSP reduced it further, and CK4+MSP nearly matched CK4P-MSP in local delta-readout.
- P/MSP redundancy and runtime audit: `info/scripts/run_property_redundancy_and_runtime_audit.py`; output directory `info/results/stage3/reviewer_response/property_redundancy_runtime`. P and MSP share strong canonical association but remain incompletely aligned at the row level; CK4P-MSP extraction is slower than CK4 and simple high-k sketch/hash summaries.
- Current application boundary: no pipeline-facing triage experiment is included. The manuscript should state that downstream triage, false-hit reduction and classifier calibration require separate database-centered validation.


