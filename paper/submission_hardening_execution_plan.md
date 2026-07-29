# Submission Hardening Execution Plan

This file is the current executable plan for the active paper-folder manuscript. It supersedes older open-ended wording that treated CAMI II, Kraken2/triage, foundation-model benchmarking or end-to-end clinical validation as mandatory repairs. The manuscript remains a representation-diagnostics paper.

## Current Decision

- Keep the central positioning as a methods-oriented representation-diagnostics study for controlled short-read mNGS-motivated settings.
- Do not reframe the paper as an end-to-end classifier, clinical diagnostic tool, Kraken2 replacement, ARG/SNP detector or production triage pipeline.
- Treat CAMI_TOY_low as a lightweight external metagenomic probe, not as production-scale external validation.
- Treat the completed lightweight CAMI II subset probe as an anonymous-read stability probe. It reduces reviewer concern about CAMI_TOY_low complexity without changing the manuscript into a full benchmark paper.
- Do not start a new deep-learning embedding benchmark, Kraken2 pipeline experiment or clinical pipeline branch unless the study scope is deliberately expanded.

## A. Verdict On The Latest External Action Plan

The latest external plan is directionally sound, but it still needs several guardrails before execution.

- Accept:
  - Define `representation diagnostics` explicitly.
  - Reduce application-facing claims.
  - Keep CAMI wording bounded.
  - Interpret mixed-space L2 as `standardized diagnostic drift`.
  - Keep MI as estimator-dependent empirical support.
  - Harden Data and Code Availability before submission.
- Modify:
  - Replace `orthogonal dimensions` with `auditable identity, biochemical and positional channels`.
  - Avoid `first`, `unprecedented` and other novelty overclaims unless separately verified.
  - Report the completed CAMI II result only as an anonymous-read stability probe.
  - Do not ban shallow macro-F1. It may be reported only as a representation-level readout, not as classifier or clinical-task performance.
  - Do not force a target/background binary CAMI design unless the labels support it. Prefer genus- or species-level top-label readout when gold labels support taxonomic labels.
  - Do not write only `Zenodo upon acceptance`. A submission version needs a public repository statement, fixed commit or release tag, license, and preferably a DOI-archived release.

## B. Immediate Text Pass

Files to inspect and edit:

- `paper/01_abstract.md`
- `paper/02_intro_related_work.md`
- `paper/03_method_experiments.md`
- `paper/04_limitations_future_conclusion.md`
- `paper/05_references.md`

### B1. Define Representation Diagnostics

Add or retain a compact definition in the Abstract, Introduction and Study design.

Preferred wording:

> Here, representation diagnostics denotes a prespecified set of representation-level audit readouts, including paired stability, block-wise drift, nearest-clean retrieval and shallow readout, rather than a clinical diagnostic rule, an automated threshold or an operational pipeline decision.

Avoid:

- clinical diagnostic rule
- automated threshold
- operating-point decision
- deployment model
- pipeline triage unless a real downstream endpoint is added
- probability calibration unless it is explicitly representation-level auditing

### B2. Reduce Application-Facing Claims

Search terms:

- `triage`
- `false-hit reduction`
- `classifier-output auditing`
- `confidence calibration`
- `clinical validation`
- `pipeline improvement`
- `replacement`
- `standalone`

Allowed wording:

> Compact biochemical and position-aware summaries may serve as auxiliary audit variables for future pipeline integration, rather than standalone deployment models or direct classifier replacements.

Future-work wording:

> Evaluating whether these audit variables improve downstream false-hit reduction in production pipelines requires separate operating-point analyses and database-centered validation.

### B3. Bound CAMI Language

Search terms:

- `validation`
- `validate`
- `external validation`

Rule:

- If the sentence refers to CAMI_TOY_low, use `probe`, `readout probe`, `external probe` or `lightweight external metagenomic probe`.
- Keep `validation` only for future work or general discussion of work not completed in this manuscript.

Preferred limitation wording:

> CAMI_TOY_low serves as a lightweight external metagenomic probe for representation readability. It should not be read as production-scale external validation across complex microbial communities.

### B4. Bound L2 And MI Interpretation

L2 wording:

> Mixed-space L2 is interpreted strictly as standardized diagnostic drift after block construction and normalization, not as a natural biophysical distance across commensurate physical units. This interpretation is stress-tested by same-dimension PCA/SVD controls, high-k compressed baselines, block-weight audits, counterfactual property controls and the P/MSP relation audit.

MI wording:

> MI and conditional-MI analyses are estimator-dependent empirical audits. They support the presence of perturbation-relevant information under the tested perturbation grid, but they are not a universal information-theoretic proof of representation superiority.

Do not write:

- `prove`
- `theorem`
- `information-theoretic superiority`
- `orthogonal information`
- `mathematically superior`

### B5. Clarify P/MSP Division Of Labor

Required wording constraints:

- P is a global biochemical stability summary.
- MSP positionalizes the same biochemical property family and returns coarse layout information to the compact k-mer backbone.
- P and MSP are related but not interchangeable.
- P and MSP are not described as orthogonal, independent or separate physical axes.

Evidence to cite:

- Direct CK4 / CK4+P / CK4+MSP / CK4P-MSP contribution audit.
- P/MSP redundancy and runtime audit.
- P/MSP relation audit with CCA and correlation heatmap.

## C. Narrative Strengthening Without New Experimental Fronts

The manuscript should defend novelty as a framework contribution, not as an invention of new biochemical descriptors.

Preferred wording:

> The core contribution of this study is not the invention of novel biochemical features, but the formulation of a diagnostic framework that decomposes ultra-short-read representations into auditable identity, biochemical and positional channels under controlled perturbation.

Constraints:

- Do not use `orthogonal dimensions`.
- Do not use `first` or `unprecedented`.
- Do not imply that foundation models were benchmarked, rejected or used.
- Keep foundation models in related-work context unless a separate embedding audit is actually run.

## D. Completed Lightweight CAMI II Probe

Status: completed as a lightweight CAMI II marine anonymous-read perturbation-stability probe without reconstructed read-level taxonomic labels in this analysis. This reduces the risk that reviewers dismiss CAMI_TOY_low as the only external metagenomic evidence, but it must not be written as CAMI II taxonomic validation.

Completed source:

- Dataset: CAMI II marine short-read sample 0.
- Parsed subset: 4,000 anonymous 150 bp reads from the `anonymous_reads.fq.gz` member inside `marmgCAMI2_sample_0_reads.tar.gz`.
- Expanded probe rows: 48,000 rows across 69, 75 and 100 bp; clean, N_3pct, substitution_1pct and substitution_1pct_N_3pct conditions.
- Result directory: `results/stage3/cami2_marine_lightweight_probe_core`.
- Source script: `scripts/run_cami2_marine_lightweight_probe.py`.
- Figure script: `scripts/generate_supp_fig_s10_cami2_marine_probe.py`.
- Figure asset: `paper/figures/supp_fig_s10_cami2_marine_probe.*`.
- Source table: `paper/tables/supp_table_s10_cami2_marine_probe_source.csv`.
- Boundary: FASTQ headers are anonymous (`S0R...`) and do not provide direct read-level taxonomy. The large OTU-specific BAM truth bundles were not downloaded for this lightweight repair. Therefore the completed probe reports paired stability, L2 drift, paired cosine and retrieval, not taxonomic macro-F1.

### D1. Scope

- Use the completed 4,000-read CAMI II marine subset as Supplementary Figure S10.
- Add one short Results paragraph only.
- Do not expand to OTU-specific BAM mapping unless the paper is deliberately expanded into a CAMI II taxonomic readout study.

### D2. Metrics

Allowed:

- paired stability
- L2 drift
- paired cosine
- nearest-clean retrieval if pair structure exists
- shallow representation readout only if read-level labels are later obtained
- macro-F1 only if explicitly labeled as representation-level linear-probe readout and backed by read-level labels

Not allowed:

- describing macro-F1 as classifier performance
- describing the probe as clinical validation
- describing the current CAMI II probe as taxonomic validation
- claiming downstream false-hit reduction
- claiming Kraken2/Centrifuge integration

### D3. Pre-Result Placeholder

Use completed-result wording, with the boundary intact:

> To test whether the compact-stability trend was restricted to CAMI_TOY_low, we added a lightweight CAMI II marine subset probe using anonymous short reads from sample 0. In this external anonymous-read perturbation-stability probe, CK4P-MSP had the lowest mean L2 drift across all tested length and perturbation cells while preserving high paired cosine. Because read-level taxonomic labels were not reconstructed for this lightweight analysis, this result is reported as an external stability probe rather than as CAMI II taxonomic validation.

## E. Methods And Results Details To Verify

### E1. MSP Binning

Add or retain:

> The 2+3+4+6 multi-scale binning was selected as a prespecified compact grid covering local to semi-global read segments, rather than being tuned post hoc to maximize benchmark performance.

Evidence:

- Supplementary Figure S6 should remain the sensitivity support.

### E2. CSP Interpretation

Define CSP at first use as canonical spaced-property.

Preferred wording:

> The suboptimal performance of the canonical spaced-property control indicates that sparse, matching-oriented seed priors do not necessarily transfer to dense read-level representations. In dense feature spaces, contiguous local composition remains a major driver of perturbation stability, whereas spaced seeds trade contiguous information for matching sensitivity.

Constraint:

- Do not write CSP as a failed method. It is a boundary comparator.

### E3. CAMI Preprocessing

Methods must state:

- label hierarchy used for CAMI labels
- how labeled subsets were selected
- how unclassified or background reads were handled
- whether top labels were filtered by read count
- whether genus-level or species-level labels were used
- how CAMI_TOY_low differs from controlled WGS perturbation and ART simulator checks

### E4. Dataset Scale

Table 2 or adjacent Methods text must report:

- read/template counts
- read-length conditions
- number of labels, genera or species where applicable
- perturbation conditions
- metrics used
- claim boundary for each data layer

## F. Figure, Table And DOCX QA

### F1. Figure And Table Captions

Each caption should define:

- abbreviations used in the panel or table
- metric type
- feature dimensions when relevant
- whether the metric is stability, readout, perturbation or runtime
- what the error bars or intervals represent

### F2. Axis And Label Checks

- Check all y-axis ranges for visual exaggeration.
- If axes are truncated, make this visually clear and do not overstate small absolute differences.
- Check all exported main and supplementary figures for label overlap.
- Avoid crowded in-panel annotations. Move complex labels into legends or captions.

### F3. Formula Checks

- Core formulas should be display equations in the manuscript source.
- The DOCX and PDF render should not contain raw `$$`, broken LaTeX or garbled mathematical symbols.
- State default `alpha = beta = gamma = 1` near the formula.
- State explored block-weight ranges where block-weight audit is introduced.

### F4. Supplementary Figure References

Replace standalone fragments such as:

> Supplementary Figure S2. Empirical MI and conditional-MI audit.

with integrated text:

> The empirical MI and conditional-MI audit (Supplementary Figure S2) showed ...

### F5. Abbreviation Checks

Check first-use expansion for:

- CK4P-MSP
- MSP
- CSP
- MI
- ART
- CAMI
- PCA
- SVD
- CCA
- KSG
- kNN
- any foundation-model abbreviation retained in related work

### F6. DOCX Rebuild

After any source or figure change:

- rebuild `paper/paper_manuscript.docx`
- render to PDF or page PNGs
- inspect title page, equations, figures, captions, page breaks and figure/table order

## G. Submission Hard Gates

NAR Genomics and Bioinformatics requires a Data Availability statement. The journal also supports data/software citation principles, and when data or software underlying the article are available online, the manuscript should include a full citation in the reference list.

Before submission, update `paper/05_references.md` and the DOCX with:

- public GitHub URL
- fixed commit hash or release tag
- license
- processed data/output table availability
- DOI-archived release if available
- software/data citation in the References if required by the final format

Current pushed release commit:

> `4a23b0acbc6a644ded93a90794b15aee4de9ee2e`

Submission metadata still to fill:

- authors
- affiliations
- corresponding author
- author contributions
- funding
- acknowledgements
- ethics/data governance
- conflict of interest

References:

- Convert temporary citation keys and plain-text references into the NARGAB/OUP-required final citation style before submission.
- Re-check metadata for recent works, preprints, software, datasets and books.

## H. Execution Order

1. Run the immediate text pass across `01`-`05`.
2. Verify Methods details: MSP, CSP, CAMI preprocessing, dataset scale.
3. Keep the completed lightweight CAMI II probe bounded to anonymous-read stability.
4. Ensure Supplementary Figure S10, Supplementary Table S10 and one short Results paragraph remain synchronized.
5. Rebuild DOCX and run visual QA.
6. Update public repository, data/code statements and references before submission.
