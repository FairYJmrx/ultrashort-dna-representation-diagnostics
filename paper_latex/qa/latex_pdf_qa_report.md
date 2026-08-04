# LaTeX and PDF QA Report

Date: 2026-08-04

## Build status

- Main manuscript: 19 pages, compiled from `main.tex` with the OUP authoring template.
- Supplementary Data: 14 pages, compiled from `supplementary.tex` with Figures S1-S14 and the current supplementary tables.
- Cover letter: 1 page, compiled from `cover_letter.tex`.
- Main and supplementary compilation completed with exit code 0. No undefined citations, undefined references, missing figures or `Float too large` errors were reported.
- The repeated 261.76535 pt output-routine warning is emitted by the OUP crop/output layer. Rendered pages were inspected and showed no content-level clipping or horizontal overflow.
- MiKTeX emits an environment-level notice that updates have not been checked; this does not affect the generated PDF and is not a manuscript error.

## Scientific and narrative consistency

- CK4P-MSP is presented as a fixed, training-free and block-decomposable stability-readability trade-off, not as a universal minimum-drift representation or a production classifier.
- PseKNC, PseEIIP, PCA/SVD, high-k compressed vectors, MinHash/Jaccard controls and full-position probes remain visible as boundaries rather than being hidden when they win a particular axis.
- The main figures preserve the intended division of labor: K supports composition-linked retrieval, P mainly reduces global perturbation drift, and MSP improves grouped local-change readability.
- The current public-release source contains the AI-assisted-tools disclosure, sole-author metadata and no Huang Jianhua author entry.
- Data and code statements point to the versioned GitHub repository; the Zenodo DOI remains the only release-stage placeholder until the public archive is minted.

## Visual QA

- All six main figures and Supplementary Figures S1-S14 render without clipping, blank panels, legend-data occlusion or overlapping axis labels.
- Figure 2, Figure 4 and Figure 6 show CK4P-MSP explicitly and preserve the method's fixed colour across panels.
- Main-text figures remain adjacent to their evidence sections; no full figure-only page was introduced.
- The final bibliography page contains normal tail whitespace because the reference list ends before the page bottom; this is not a float or content-placement defect.
- Supplementary table pages contain intentional tail whitespace where complete tables are kept together at readable size.

## Reproducibility

- A fresh Python 3.13 environment installed `requirements-lock.txt` and passed the five-test smoke suite and release preflight.
- The maintained full contract-v2 path completed compact baselines, grouped local mutation, all seven K/P/MSP combinations, high-k compression, kNN-MI robustness and short-read continuity audits with return code 0.
- A second clean run produced bytewise-identical kNN-MI and seven-block/binset outputs. Stale frozen summaries were refreshed where the current implementation added valid-observation fields or updated estimator values.
- The observed full-path wall time was approximately 39.5 minutes on the verification host. This is a host-specific reproduction time, not a method benchmark.

## Remaining release action

The only unresolved release action is to publish the frozen GitHub Release, enable its Zenodo archive, obtain the DOI, and replace the DOI placeholder in the manuscript, `CITATION.cff`, cover letter and release notes. The final public package must then receive a clean commit and tag.
