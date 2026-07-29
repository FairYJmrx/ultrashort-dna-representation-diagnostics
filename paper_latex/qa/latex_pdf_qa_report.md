# LaTeX and PDF QA Report

Date: 2026-07-29

## Build status

- Main manuscript: 18 pages, compiled from `main.tex` with the OUP authoring template.
- Supplementary Data: 13 pages, compiled from `supplementary.tex` with Figures S1-S12 and Tables S1-S7.
- No undefined citations, undefined references, missing floats or `Float too large` warnings.
- The repeated 261.76535 pt output-routine warning is produced by the OUP crop/output layer and is not a content overflow. No content-level overfull box was visible in the rendered pages.
- MiKTeX reports that updates have not yet been checked. This environment notice does not alter the generated PDF but should be cleared before the submission build.

## Scientific consistency

- CK4P-MSP is not described as the universal minimum-drift representation.
- Property-only blocks, fitted PCA/SVD controls and PseKNC retain their lower-drift results where applicable.
- The CK4P-MSP contribution is stated as a fixed, training-free and block-decomposable stability-readability trade-off.
- Supplementary Figure S12 reports mean drift, grouped local-change readability, feature dimension and common-protocol implementation time.
- The optimized CK4P-MSP reference implementation has a median runtime of 2.70 s per 10,000 75-bp reads, versus 2.12 s for CK4, under the declared workstation protocol.
- Historical descriptor conclusions are bounded: PseKNC is lower-dimensional and more stable; CK4P-MSP has stronger grouped local-change readability and explicit K/P/MSP attribution.

## Visual QA

- All six main figures and Supplementary Figures S1-S12 render without clipping, blank panels, label overlap or legend-data occlusion.
- S12 uses a logarithmic runtime axis and labels all four audit dimensions directly.
- Main-text figures remain near their corresponding evidence sections; no full figure-only backlog appears after Figure 4.
- Supplementary Tables S6 and S7 share the final page. The 13-page layout is retained because reducing it further would require smaller text or unsafe float forcing.
- The supplementary table pages contain intentional page-tail whitespace where complete tables cannot be split safely. No table is stretched or compressed below a readable size.

## Submission metadata still pending

- Replace the provisional institutional Ethics and Data Governance sentence with the institution-approved final wording.
- Confirm the Funding statement and grant numbers, or state explicitly that the work received no specific funding.
- Confirm whether an Acknowledgements section is needed.
- Activate reviewer access to the private repository at submission and mint the archival DOI when the release is made public.

## Verdict

The scientific text, figures, tables and compiled layout pass internal author-review QA. The manuscript is not yet submission-ready only because the listed author-side metadata and repository-access actions remain pending.
