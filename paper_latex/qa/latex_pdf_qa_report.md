# LaTeX and PDF QA Report

Date: 2026-07-30

## Build status

- Main manuscript: 19 pages, compiled from `main.tex` with the OUP authoring template.
- Supplementary Data: 13 pages, compiled from `supplementary.tex` with Figures S1-S13 and Tables S1-S7.
- No undefined citations, undefined references, missing floats or `Float too large` warnings.
- The repeated 261.76535 pt output-routine warning is produced by the OUP crop/output layer and is not a content overflow. No content-level overfull box was visible in the rendered pages.
- MiKTeX reports that updates have not yet been checked. This environment notice does not alter the generated PDF but should be cleared before the submission build.

## Scientific consistency

- CK4P-MSP is not described as the universal minimum-drift representation.
- Property-only blocks, fitted PCA/SVD controls and PseKNC retain their lower-drift results where applicable.
- The CK4P-MSP contribution is stated as a fixed, training-free and block-decomposable stability-readability trade-off.
- Supplementary Figure S12 reports mean drift, grouped local-change readability, feature dimension and common-protocol implementation time.
- The optimized CK4P-MSP reference implementation has a median runtime of 2.71 s for an actual 10,000-read 75-bp batch, versus 2.15 s for CK4, under the declared workstation protocol. A separate actual 100,000-read pass required 28.72 s and 21.73 s, respectively; neither value is extrapolated from a 1,000-read batch.
- Historical descriptor conclusions are bounded: PseKNC is lower-dimensional and more stable; CK4P-MSP has stronger grouped local-change readability and explicit K/P/MSP attribution.
- The shared-template lower-range audit evaluates every integer length from 50 to 75 bp. Broader 100, 125 and 150 bp conditions remain anchors rather than a dense 50-150 bp scan.
- Current-contract ART results cover 50, 60, 69, 75, 100, 125 and 150 bp. Because the selected simulator profile has non-monotonic error loads across cycle settings, manuscript claims use within-length and within-quality-stratum comparisons only.
- Selective-sensitivity ratios are defined only when nuisance drift exceeds `1e-8`. Two of 3,000 PseEIIP observations were therefore marked undefined instead of producing an unstable near-zero-denominator ratio; the valid-observation mean is 0.784 and the valid fraction is 99.93%.
- Bootstrap intervals and Wilcoxon tests use prespecified matched analysis cells that reuse source template panels. The manuscript, main captions and supplementary tables now state that these summaries describe grid consistency rather than independent biological-cohort generalization.

## Visual QA

- All six main figures and Supplementary Figures S1-S13 render without clipping, blank panels, label overlap or legend-data occlusion.
- S12 uses a logarithmic runtime axis and labels all four audit dimensions directly.
- Main-text figures remain near their corresponding evidence sections; no full figure-only backlog appears after Figure 4.
- Supplementary captions state the analysis unit, interval or error-bar definition when present, and the preferred metric direction. Where no uncertainty interval is shown, the supplementary overview states this explicitly.
- Supplementary Figure S4 was regenerated with a taller source aspect for more legible effect-size trends. Supplementary Figure S8 was similarly given greater vertical plotting space without changing data or axis scales.
- Double-column float-page glue is top-aligned in the Supplementary Data. Tables S4 and S5 now form one compact top-aligned block instead of being separated by a large mid-page gap.
- Supplementary Figure S13 and Table S5 share page 12; Supplementary Tables S6 and S7 share the final page. The 13-page layout is retained because reducing it further would require smaller text or unsafe float forcing.
- The supplementary table pages contain intentional page-tail whitespace where complete tables cannot be split safely. No table is stretched or compressed below a readable size.

## Reproducibility checks

- The historical-descriptor audit script passes Python byte-code compilation after the runtime-metadata update.
- All five repository smoke scripts pass when run directly: contract artifacts, historical descriptors, imports, method contract and repository layout.
- The Supplementary Figure S7 compatibility entrypoint now delegates to the contract-v2 plotting implementation and successfully regenerates the manuscript-facing asset.
- The runtime CSV and both run-metadata JSON files now describe the same actual 10,000- and 100,000-read protocol; no stale 1,000-read extrapolation metadata remains in the canonical result directory.

## Narrative consistency repairs

- The quality-stratified ART analysis now uses the public contract-v2 CK4P-MSP implementation and is interpreted as within-simulator consistency rather than a causal read-length law.
- The Table 2 LaTeX and CSV sources now carry the same CAMI_TOY sample size, 30-label boundary and current-contract wording.
- Figure 4 defines the preferred direction for both drift and macro-F1 panels.

## Submission metadata still pending

- Replace the provisional institutional Ethics and Data Governance sentence with the institution-approved final wording.
- Confirm the Funding statement and grant numbers, or state explicitly that the work received no specific funding.
- Confirm whether an Acknowledgements section is needed.
- Activate reviewer access to the private repository at submission and mint the archival DOI when the release is made public.

## Verdict

The scientific text, figures, tables and compiled layout pass internal author-review QA for this revision. The manuscript is not yet submission-ready only because the listed author-side metadata and repository-access actions remain pending.
