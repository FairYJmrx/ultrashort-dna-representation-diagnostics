# LaTeX and PDF QA Report

Date: 2026-08-12

## Current-status note (2026-08-14)

This QA report records the current compiled LaTeX artifacts but retains historical release
references for provenance. The canonical manuscript now uses the four-author metadata; the
existing `v1.2.0` DOI remains an immutable historical single-author snapshot. A new release and
version DOI are still pending and are tracked in the NARGAB submission checklist maintained alongside the manuscript.

## Build status

- Main manuscript: 20 pages, compiled from `main.tex` with the OUP authoring template.
- Supplementary Data: 15 pages, compiled from `supplementary.tex` with Figures S1-S15 and Supplementary Tables S1-S11.
- Cover letter: 1 page, compiled from `cover_letter.tex`.
- Main and supplementary compilation completed with exit code 0. No undefined citations, undefined references, missing figures or `Float too large` errors were reported.
- The repeated 261.76535 pt output-routine warning is emitted by the OUP crop/output layer. Rendered pages were inspected and showed no content-level clipping or horizontal overflow.
- MiKTeX emits an environment-level notice that updates have not been checked; this does not affect the generated PDF and is not a manuscript error.

## Scientific and narrative consistency

- CK4P-MSP is presented as a fixed, training-free and block-decomposable stability-readability trade-off, not as a universal minimum-drift representation or a production classifier.
- PseKNC, PseEIIP, PCA/SVD, high-k compressed vectors, MinHash/Jaccard controls and full-position probes remain visible as boundaries rather than being hidden when they win a particular axis.
- The main figures preserve the intended division of labor: K supports composition-linked retrieval, P mainly reduces global perturbation drift, and MSP improves grouped local-change readability.
- The archived `v1.2.0` source contains the author metadata current at the time of that release and no Huang Jianhua author entry. The current canonical source contains the confirmed four-author metadata; the historical tag is not modified.
- CK4P-MSP remains the sole main method. CK4P-MSP-PKM is consistently identified as a fixed-weight, 297-dimensional supplementary Pareto extension rather than a replacement or universally improved model.
- Data and code statements currently retain the historical `v1.2.0`/concept DOI pointers pending the new four-author release; they must be backfilled once the new version DOI is minted.

## Visual QA

- All six main figures and Supplementary Figures S1-S15 render without clipping, blank panels, legend-data occlusion or overlapping axis labels.
- Figure 2, Figure 4 and Figure 6 show CK4P-MSP explicitly and preserve the method's fixed colour across panels.
- Supplementary Figure S8 now contains only the P/MSP contribution and relation audit; the retired duplicate runtime panel is no longer generated or distributed.
- Supplementary Figure S12 presents the historical-descriptor boundary and the unified long-duration runtime panel. Supplementary Table S11 gives the complete route-level timing profile.
- Supplementary Figure S15 presents the CK4P-MSP-PKM benefit-cost profile in one bounded four-panel audit: structured readout gains are shown together with drift, dimension, runtime and reverse-complement sensitivity costs.
- Main-text figures remain adjacent to their evidence sections; no full figure-only page was introduced.
- The final bibliography page contains normal tail whitespace because the reference list ends before the page bottom; this is not a float or content-placement defect.
- Supplementary table pages contain intentional tail whitespace where complete tables are kept together at readable size.

## Reproducibility

- The current runtime-update worktree passes the ten-test smoke suite, Python bytecode compilation and repository preflight. The method-contract test additionally fixes the manuscript-facing CK4P-MSP-PKM key and rejects the retired selected-point alias.
- The maintained full contract-v2 path completed compact baselines, grouped local mutation, all seven K/P/MSP combinations, high-k compression, kNN-MI robustness and short-read continuity audits with return code 0.
- A second clean run produced bytewise-identical kNN-MI and seven-block/binset outputs. Stale frozen summaries were refreshed where the current implementation added valid-observation fields or updated estimator values.
- The observed full-path wall time was approximately 39.5 minutes on the verification host. This is a host-specific reproduction time, not a method benchmark.

## Release status

The prior GitHub Release `v1.2.0` and Zenodo version DOI `10.5281/zenodo.21882250` remain immutable. This runtime update is prepared for a new release version after the release smoke and metadata checks pass; it must not move or overwrite the `v1.2.0` tag.
