# NAR Genomics and Bioinformatics Submission Checklist

This is the active pre-submission checklist for the CK4P-MSP manuscript. It
records manuscript status, author decisions, figure semantics, reproducibility
requirements and NARGAB/OUP submission packaging. It is not manuscript prose.

Status labels:

- `[x] Done`: verified in the current local manuscript or release workspace.
- `[ ] Author confirmation`: requires a decision or information from the authors.
- `[ ] Must do`: required before submission or before calling the manuscript
  submission-ready.
- `[ ] Optional`: useful enhancement, but not required for the current scope.

## 1. Journal And Manuscript Route

- [x] Target journal: NAR Genomics and Bioinformatics.
- [x] Current manuscript type: Standard Paper, not the more demanding Methods
  Paper route. The manuscript presents a representation-diagnostics study with
  controlled perturbation and external probes; it does not claim a production
  classifier or clinical pipeline.
- [x] Scientific source of truth: `D:\AI-NGS\info\paper_latex`.
- [x] Submission format: OUP authoring-template LaTeX compiled to PDF. The DOCX
  is a synchronized convenience artifact, not the source of truth.
- [x] Current main PDF: `paper_latex/paper_manuscript_latex.pdf`, 18 pages,
  compiled successfully from a clean QA build on 2026-08-04 after the
  read-length de-specialization pass and final reference-layout adjustment.
- [x] Current supplementary PDF: `paper_latex/paper_supplementary_latex.pdf`,
  14 pages, compiled successfully on 2026-08-04 with revised Figures S6 and
  S13.
- [x] Current supplementary source contains Figures S1-S14 and Tables S1-S9.
- [ ] Before submission, compile both main and supplementary files from a clean
  build directory and freeze the exact source commit used for the PDFs.
- [ ] Use the final NARGAB/OUP portal requirements at submission; do not infer
  a blind-review manuscript requirement. The submission manuscript will be
  author visible and include the sole author, affiliation, corresponding-author
  details and ORCID. The current LaTeX PDFs are synchronized with the
  sole-author decision; the convenience DOCX remains a separate pending
  artifact.

Official references:

- [Author Guidelines](https://academic.oup.com/nargab/pages/author-guidelines)
- [Scope and Criteria](https://academic.oup.com/nargab/pages/scope_and_criteria)

## 2. Author And Institutional Metadata

### Confirmed authorship decision

- [x] Sole author: Ruixiang Mei.
- [x] Sole-author ORCID: https://orcid.org/0009-0003-2128-0726.
- [x] Jianhua Huang will not be listed as an author, corresponding author or
  CRediT contributor in the current submission.
- [x] No patent or commercialization claim is currently planned.
- [x] The author reports no competing interests. The final manuscript wording
  should use the singular form: `The author declares no competing interests.`
- [x] Funding decision: this is an independently conducted study and received
  no specific grant from a public, commercial or not-for-profit funding body.
  Do not associate the manuscript with Jianhua Huang's grants.
- [x] Acknowledgements decision: no individual acknowledgement is currently
  required. Do not acknowledge Jianhua Huang merely because he was previously
  considered for authorship. Add a person only for a specific non-author
  contribution and after obtaining permission.
- [x] Ethics scope decision: the final study record will contain only public
  reference/benchmark data and computationally simulated data, with no human
  participants, patient-level data or identifiable private information.

### Manuscript synchronization required

- [x] Remove Jianhua Huang from the author list, corresponding-author block,
  author contributions and submission metadata in `paper_latex/main.tex`,
  `paper_latex/supplementary.tex` and `paper_latex/sections/back_matter.tex`.
  The synchronized DOCX artifact will be refreshed after the source freeze.
- [x] Designate Ruixiang Mei as the sole and corresponding author throughout
  the main manuscript, supplementary file and submission metadata.
- [ ] Confirm the corresponding-author email. Prefer an institutional address
  if it will remain accessible during review; the currently known candidate is
  `121090416@link.cuhk.edu.cn`.
- [ ] Link Ruixiang Mei's ORCID to the corresponding-author submission account.
- [x] Replace the current Author Contributions paragraph with a sole-author
  CRediT statement covering the roles actually performed: conceptualization,
  methodology, software, formal analysis, investigation, data curation,
  visualization, writing - original draft and writing - review and editing.
- [x] Change plural author references in the COI and other back-matter
  statements to singular where grammatically required.
- [x] Insert the final Funding statement: `This research received no specific
  grant from any funding agency in the public, commercial or not-for-profit
  sectors.`
- [x] Remove the individual Acknowledgements placeholder/section. This does not
  remove the separate mandatory disclosure of AI-assisted drafting, code review
  or figure QA where required by journal policy.
- [x] Removed the unpublished local/hospital aggregate read-length provenance
  from Methods, Discussion, Data Availability and Ethics/Data Governance. Base
  the 50-75-bp design rationale on the cited public literature and the public/
  simulated experimental inputs only.
- [x] Replaced the provisional ethics wording with a factual no-human-participant
  statement: only public reference/benchmark data and simulated data were used;
  no patient-level or identifiable private data were analysed, and institutional
  ethics approval was therefore not required.
- [x] Recompiled the main and supplementary PDFs from the clean QA build and
  verified PDF metadata, title pages, correspondence details and sole-author
  identity in the current LaTeX PDFs.
- [ ] Refresh the convenience DOCX and verify that its title page and author
  metadata contain only the final sole author; the current DOCX predates the
  latest LaTeX pass and is not the source of truth.

### Author or institutional confirmation required

- [x] Current intended affiliation: School of Data Science, The Chinese
  University of Hong Kong, Shenzhen, Shenzhen 518172, Guangdong, China.
- [ ] Confirm the exact official affiliation wording and postal code with the
  institution.

## 3. AI-Use Disclosure

- [ ] Decide the accurate disclosure scope for generative-AI assistance used in
  drafting, editing, code review, figure QA and manuscript organization.
- [ ] Add an author-approved disclosure in the cover letter and in the
  manuscript's appropriate Methods or Acknowledgements location, following the
  current NARGAB/OUP policy. The disclosure must not imply that AI generated,
  validated or took responsibility for scientific conclusions.
- [ ] Ensure the disclosure is consistent with the actual contribution and
  does not claim that no AI tool was used.

## 4. Data, Code And Reproducibility

### Current state

- [x] Release repository exists:
  https://github.com/FairYJmrx/ultrashort-dna-representation-diagnostics
- [x] Release branch exists and contains the current reproduction manifest.
- [x] `README.md` and `RELEASE_MANIFEST.md` map the reproduction path, scripts,
  inputs, outputs and manuscript assets.
- [x] The manuscript now uses only public reference/benchmark and simulated
  inputs as its evidence base. Unpublished local aggregate read-length
  provenance has been removed from Methods, Discussion and back matter.
- [ ] The repository is still private and no archival DOI has been minted.

### Must complete before submission

- [ ] Decide whether the repository becomes public at submission. A private
  review repository is an interim authoring state, not the safest final state
  for NARGAB's strict software/data-access expectations.
- [ ] If remaining private, confirm that the journal portal accepts the chosen
  reviewer-access mechanism and provide working read-only access instructions.
- [ ] Freeze a version tag/commit and archive the same release in Zenodo or
  another suitable repository to obtain a DOI. The DOI and public URL must be
  inserted into Data Availability and Code Availability when available.
- [ ] Run the release on a clean environment using only documented commands;
  record software versions, operating system, CPU/RAM context and completion
  status.
- [ ] Remove all local absolute paths, temporary directories, stale build
  products and machine-specific assumptions from the public/reviewer package.
- [ ] Verify that public source data, derived tables, figure inputs, scripts,
  licenses and third-party data-use terms are all distributable.
- [ ] Verify that every manuscript figure/table can be regenerated from the
  release manifest and that generated asset hashes match the frozen release.
- [ ] Complete the journal's online data-standardization and reproducibility
  checklist, if presented by the submission system.

## 5. Scientific Scope And Text Consistency

- [x] The paper is framed as a training-free, low-dimensional,
  block-decomposable representation-diagnostics framework.
- [x] The manuscript does not claim universal minimum drift, universal
  predictive superiority, clinical validation, ARG/SNP resolution or a Kraken/
  alignment replacement.
- [x] CK4 is described as canonical local-token composition evidence, not exact
  whole-read identity.
- [x] P and MSP are described as related but non-equivalent auditable channels,
  not statistically independent or orthogonal physical axes.
- [x] P is associated mainly with global stability and chemistry-related
  information; MSP is associated mainly with coarse local-change readability.
- [x] The seven-group ablation and the 2 x 2 mechanism audit explain that both
  blocks contribute, but neither block is necessary for every metric.
- [x] PseKNC, NCP+ANF and PseEIIP are treated as historical descriptor controls;
  their lower drift or different dimension is not hidden.
- [x] CAMI_TOY_low is described as six coarse source-grouped target/background
  probes, not fine taxonomic validation.
- [x] CAMI II marine is described as an anonymous-read stability probe without
  reconstructed read-level labels.
- [x] The dense length sweep is correctly limited to 50-75 bp, with 100, 125
  and 150 bp as broader anchors rather than a continuous 50-150 bp scan.
- [x] The 69-bp condition has been de-specialized across Methods, Results,
  Discussion, back matter, captions, writing constraints and release-facing
  legacy prose. It remains only as an ordinary member of existing experimental
  grids and is not described as a clinical threshold or unpublished provenance.
- [x] Supplementary Figure S13 no longer marks 69 bp with a vertical reference
  line. The continuity figure now treats all integer lengths from 50 to 75 bp
  uniformly.
- [x] Supplementary Figure S6 weight sensitivity was rerun at 75 and 100 bp.
  The fixed-weight conclusion was retained without relying on a 69/75-bp pair.
- [x] Search the final manuscript for stale, stronger wording such as exact
  identity, orthogonal channels, universal information gain, clinical
  diagnostic performance or standalone classification. The final scan also
  standardized the last `local-mutation/random-noise` phrase to
  `local-to-nuisance`.
- [x] Verify that every numerical claim in Abstract, Results, Discussion,
  captions and tables agrees with the final source tables and scripts. The
  audit is recorded in `release_code/docs/manuscript_table_provenance_audit.md`.
- [x] Confirm that matched-cell bootstrap intervals and Wilcoxon tests are
  described as consistency across the controlled grid, not independent
  biological-cohort inference.
- [x] Mark any unstable or undefined ratio caused by a near-zero denominator as
  undefined/unstable in source outputs and tables; do not expose it as a valid
  effect size. Current ratio-producing audits use a `1e-8` nuisance-drift
  tolerance and retain valid counts/fractions.

## 6. References And Abbreviations

- [x] Verify BibTeX structure and available publication metadata for cited
  keys, including DOI resolution, journal, volume, pages and author spelling.
  The separately listed Yang-edited book remains the only manual metadata
  exception.
- [ ] Complete the formal citation for the Yang-edited book, including the
  publisher's official English title, editor spelling and the page-99
  50-75-bp statement.
- [x] Verify formal citations for ART, CAMI, KSG, Benjamini-Hochberg,
  PseKNC, PseEIIP, NCP+ANF, MinHash and the major matching baselines.
- [x] Check the final reference list for incomplete preprint/arXiv metadata and
  replace entries with final proceedings or journal versions where available.
  DNABERT-2 and HyenaDNA now use their official ICLR and NeurIPS records;
  genuinely preprint-only records remain labelled as such.
- [x] Main text currently uses numbered OUP/NAR-style citations and no undefined
  citation keys were reported in the latest main compilation.
- [x] Run one final abbreviation audit. At first use, define CK4P-MSP, CK4,
  CSP, MSP, MI, KSG, ART, CAMI, EIIP, PCA, SVD, NCP and ANF as applicable.
- [x] Confirm that Supplementary Figure/Table citations use one consistent
  format, for example `(Supplementary Figure S8)` and `(Supplementary Table S4)`.

## 7. Figure And Table Semantic Audit

The earlier Figure 4 problem showed that visual QA must test meaning, not only
overlap. Every figure must pass all items below.

### Semantic audit status - completed 2026-08-02

- [x] Completed a panel-by-panel semantic audit of main Figures 1-6 and
  Supplementary Figures S1-S14 against their captions and alt text.
- [x] Replaced the ambiguous `identity` heading in Figure 1 with `sequence
  evidence` and explicitly separated CK4/CK5 composition from matching,
  alignment and database context.
- [x] Recast Figure 1 so that K, P and MSP are shown as three evidence blocks
  contributing to a CK4P-MSP audit profile, rather than visually assigning the
  complete method to the MSP branch alone.
- [x] Replaced the S5C display label `identity_CK4` with the more accurate
  `composition_CK4`.
- [x] Added an explicit contract-space versus train-z-score legend to
  Supplementary Figure S14B and defined the green/red mapping in its caption.
- [x] Verified that Figure 4 defines neutral target-task circles,
  method-coloured cross-target diamonds and faint target-pairing lines.
- [x] Expanded main Table 1, Table 2 and Table 5 captions so that baseline roles,
  non-independent derivative counts and boundary-only analyses are explicit.
- [x] No new experiment is required to resolve the semantic issues found in
  this audit.
- [x] Cross-figure palette, grayscale accessibility, final-size typography and
  page-level placement audits are complete.

### Global figure contract

- [x] Main figures 2-6 use the canonical CK4P-MSP method colour `#B83A62`.
- [x] Applied the same method-colour contract to supplementary figures whenever
  colour denotes method identity. S5, S8 and S12 were regenerated; S10 uses
  perturbation colours rather than method colours.
- [x] Kept semantic colours separate from method colours when colour denotes
  channel, preprocessing condition, perturbation or quality stratum.
- [x] For every plot, explain every marker shape, line, hatch, fill, error bar,
  reference line and connector in the legend or caption. In particular, do not
  leave circles, diamonds or faint pairing lines unexplained.
- [x] Checked colour and grayscale contact sheets. Method comparisons retain
  direct labels, marker shapes, line styles or panel structure and do not rely
  on hue alone.
- [x] Make axis names, units, directionality and baseline meaning explicit.
- [x] State the analysis unit, sample/template count, uncertainty definition and
  whether observations are paired or share source templates.
- [x] Ensure captions are self-contained: panel roles, data layer, length,
  perturbation, metric direction, n and uncertainty must be recoverable without
  searching the main text.
- [x] Checked final-size typography at the intended 84 mm single-column or 178 mm
  double-column width. Keep final labels at least 5 pt and enlarge dense axes
  rather than shrinking the whole figure.
- [x] Checked aspect ratio, crop, margins and unused white space. No decorative
  title or oversized legend consumes the data area in the final rendered PDFs.
- [x] Checked that each figure answers a specific manuscript question and does
  not present a scientifically redundant comparison as a main result.
- [x] Retained editable PDF/SVG source and stable figure names for all regenerated
  main and supplementary assets.

### Current figure-specific actions

- [x] Main Figure 4: the neutral target-task circles, method-coloured diamonds
  and faint target-pairing lines are now defined in the caption.
- [x] Rechecked Figure 4 at final double-column size; diamonds, neutral task
  circles, pairing lines and method labels do not collide.
- [x] Review Figure 2 for semantic focus and confirm that its visual argument
  is the P/MSP mechanism rather than an undifferentiated method ranking.
- [x] Review Figure 3 for an explicit CK4P-MSP mark in all quantitative panels
  that distinguishes dimension-matched controls from historical descriptors.
- [x] Review Figure 5 semantics and ensure its upper-bound role is clear
  without implying that full-position encodings are deployable alternatives.
- [x] Review Figure 6 wording so that CK4P-MSP's lower local-change
  sensitivity than the position-explicit upper bounds is visible but not
  confused with failure of the compact representation's audit objective.
- [x] Regenerated S5, S8 and S12 with the canonical CK4P-MSP colour. Audited S10
  and retained its non-method perturbation colours intentionally.
- [x] Audited S14 because its colours encode preprocessing/contract conditions;
  the legend and caption state this explicitly and do not imply method identity.
- [x] Normalized the inconsistent in-figure title treatment in S8 and shortened
  the dense S10 title without removing its dataset metadata.
- [x] Rechecked S9 heatmap labels and S12 runtime/dimension labels at final size;
  both remain legible in the rendered supplementary PDF.
- [x] Rechecked S10 title, metadata header and legend placement after final
  rendering; no overlap or clipping remains.
- [x] Verified that every supplementary figure S1-S14 is cited in the main text
  or in the cited supplementary overview; no orphaned figure remains.

## 8. Table And Numeric QA

- [x] Checked every compiled table for readable font size, line breaks, units,
  decimals, significance notation and column alignment.
- [x] Checked that table captions define abbreviations, analysis units, interval
  meanings and whether values are cell means or independent observations.
- [x] Confirmed Supplementary Table numbering S1-S9 in the compiled output,
  including the source file retained under its historical filename.
- [x] Traced every current numeric table to its source CSV/run artifact and
  documented generator. Main Tables 3-4 and Supplementary Tables S1-S9 now
  regenerate exactly from `generate_contract_v2_tables.py`; static Tables 1,
  2 and 5 are mapped to method definitions, manifests and boundary results.
- [x] Ran a final numeric cross-check of effect sizes, confidence
  intervals, adjusted q values and undefined/unstable ratios between tables,
  prose and source results. This pass also replaced a stale 2,000-pair CAMI II
  preview in Supplementary Table S1 with the current 4,000-pair values.

## 9. LaTeX, PDF And Layout QA

- [x] Latest main compilation completed without LaTeX errors or undefined
  citations.
- [x] Main PDF has no observed equation glyph failures, figure clipping or
  obvious main-text figure overlap in the latest visual pass.
- [x] Supplementary source compiled successfully into a 14-page PDF during the
  current QA pass.
- [x] Replaced the stale canonical supplementary PDF with the final clean build
  after the figure, caption and palette checks passed.
- [x] Inspected all 18 main pages and 14 supplementary pages at 100% and as
  contact sheets.
- [x] Checked for stranded headings, large unexplained blank regions, figure pages
  with captions detached from data, table overflow and accidental blank pages.
- [x] Confirmed that figure movement remains within one page of the interpreting
  text and that no page contains only a detached caption or undersized figure.
- [x] Checked all display equations for standard LaTeX rendering, vector symbols,
  fixed block-weight normalization and consistent notation.
- [x] Checked overfull/underfull warnings against rendered pages. The recurring
  full-width-float warning is produced by the OUP output routine; no visible
  overflow, clipping or margin intrusion was found.
- [x] Verified page headers, page numbers, section hierarchy, references and
  supplementary numbering in the final PDFs.
- [x] Removed the forced page break before Ethics and Data Governance that had
  created a nearly empty left column; the final main manuscript is an
  18-page document with the reference section compressed only after the body
  layout was visually verified.
- [ ] Portal-specific initial-submission assembly remains deliberately excluded
  from this four-point audit.

### Scientific wording status - completed 2026-08-02

- [x] Replaced `mutual-information robustness checks` with estimator-sensitivity
  checks for empirical separability in the Introduction and Methods.
- [x] Kept MI/KSG values explicitly estimator-dependent and avoided theorem,
  proof or universal-information language.
- [x] Replaced residual composition/identity conflation in the vectorized k-mer
  review and Discussion; database-linked exact matching remains a separate role.
- [x] Kept P and MSP as related but non-interchangeable layers, without claiming
  orthogonality, statistical independence or universal necessity.
- [x] Kept the read-length scope consistent: a dense shared-template audit at
  50--75 bp plus discrete 100, 125 and 150 bp anchors, not a continuous law.
- [x] Kept ART, CAMI_TOY_low and CAMI II claims separated into simulator
  consistency, coarse fixed-head label retention and anonymous-read stability.
- [x] Changed the local-mutation heading from generic `robustness` to numerical
  stability and changed Figure 3's title to a bounded stability trade-off.
- [x] Replaced `public implementation` with `reference implementation` while the
  release repository remains private.
- [x] No unresolved Abstract--Introduction--Methods--Results--Discussion claim
  contradiction was found in this pass.

## 10. Final Submission Package

- [x] Current main PDF copied from the clean QA build; final freeze still
  requires the release commit/tag.
- [x] Current supplementary PDF copied from the clean QA build; final freeze
  still requires the release commit/tag.
- [x] Separate high-resolution/editable figure files with stable names are
  present in the LaTeX source tree.
- [x] LaTeX source, bibliography and compilation instructions for revision or
  editorial production.
- [ ] Cover letter with Standard Paper positioning, concise novelty statement,
  scope boundary and AI-use disclosure.
- [ ] Actual public or reviewer-access repository URL, release tag and DOI plan.
- [ ] Final Data Availability, Code Availability, Ethics, Funding,
  Acknowledgements, sole-author Contributions and singular COI text.
- [ ] Ruixiang Mei ORCID and corresponding-author account linkage.
- [ ] Final check that no local paths, internal review notes, temporary comments
  or unresolved placeholders are included in the submitted package.

## 11. Decisions Explicitly Deferred

- [ ] Public repository release and DOI: author decision before submission.
- [ ] Ruixiang Mei corresponding-author email: author confirmation.
- [ ] Exact official affiliation wording and postal code: author/institution
  confirmation.
- [ ] Final AI-use disclosure wording and placement: author confirmation.
- [x] Final supplementary palette and semantic figure fixes completed; no new
  scientific experiment was required.
- [ ] Rebuild the convenience DOCX after the LaTeX source freeze; its current
  2026-07-30 timestamp is older than the final 2026-08-04 PDFs.
