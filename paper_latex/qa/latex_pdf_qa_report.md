# LaTeX and PDF QA Report

Date: 2026-08-11

## Build status

- Main manuscript: 19 pages, compiled from `main.tex` with the OUP authoring template.
- Supplementary Data: 15 pages, compiled from `supplementary.tex` with Figures S1-S15 and Supplementary Tables S1-S10.
- Cover letter: 1 page, compiled from `cover_letter.tex`.
- Main and supplementary compilation completed with exit code 0. No undefined citations, undefined references, missing figures or `Float too large` errors were reported.
- The repeated 261.76535 pt output-routine warning is emitted by the OUP crop/output layer. Rendered pages were inspected and showed no content-level clipping or horizontal overflow.
- MiKTeX emits an environment-level notice that updates have not been checked; this does not affect the generated PDF and is not a manuscript error.

## Scientific and narrative consistency

- CK4P-MSP is presented as a fixed, training-free and block-decomposable stability-readability trade-off, not as a universal minimum-drift representation or a production classifier.
- PseKNC, PseEIIP, PCA/SVD, high-k compressed vectors, MinHash/Jaccard controls and full-position probes remain visible as boundaries rather than being hidden when they win a particular axis.
- The main figures preserve the intended division of labor: K supports composition-linked retrieval, P mainly reduces global perturbation drift, and MSP improves grouped local-change readability.
- The archived `v1.2.0` source contains the author metadata current at the time of release and no Huang Jianhua author entry. Final journal author metadata remains subject to a later, explicitly versioned update after the proposed student coauthors and their roles are confirmed.
- CK4P-MSP remains the sole main method. CK4P-MSP-PKM is consistently identified as a fixed-weight, 297-dimensional supplementary Pareto extension rather than a replacement or universally improved model.
- Data and code statements point to GitHub Release `v1.2.0`, Zenodo version DOI `10.5281/zenodo.21882250` and the stable Zenodo concept DOI `10.5281/zenodo.21792340`.

## Visual QA

- All six main figures and Supplementary Figures S1-S15 render without clipping, blank panels, legend-data occlusion or overlapping axis labels.
- Figure 2, Figure 4 and Figure 6 show CK4P-MSP explicitly and preserve the method's fixed colour across panels.
- Supplementary Figure S15 presents the CK4P-MSP-PKM benefit-cost profile in one bounded four-panel audit: structured readout gains are shown together with drift, dimension, runtime and reverse-complement sensitivity costs.
- Main-text figures remain adjacent to their evidence sections; no full figure-only page was introduced.
- The final bibliography page contains normal tail whitespace because the reference list ends before the page bottom; this is not a float or content-placement defect.
- Supplementary table pages contain intentional tail whitespace where complete tables are kept together at readable size.

## Reproducibility

- The release snapshot passes the ten-test smoke suite, Python bytecode compilation and repository preflight. The method-contract test additionally fixes the manuscript-facing CK4P-MSP-PKM key and rejects the retired selected-point alias.
- The maintained full contract-v2 path completed compact baselines, grouped local mutation, all seven K/P/MSP combinations, high-k compression, kNN-MI robustness and short-read continuity audits with return code 0.
- A second clean run produced bytewise-identical kNN-MI and seven-block/binset outputs. Stale frozen summaries were refreshed where the current implementation added valid-observation fields or updated estimator values.
- The observed full-path wall time was approximately 39.5 minutes on the verification host. This is a host-specific reproduction time, not a method benchmark.

## Release status

GitHub Release `v1.2.0` is published from commit `4d9c9d5ac2a0f0d8a7dbe3493097088b37660e09`, and its release-smoke workflow completed successfully. Zenodo archived the immutable release files under version DOI `10.5281/zenodo.21882250`; the concept DOI `10.5281/zenodo.21792340` continues to resolve to the release history. Any later author-metadata revision must use a new release version rather than moving or overwriting the `v1.2.0` tag.
