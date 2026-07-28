# Submission repair completion report

Date: 2026-07-29

Target: NAR Genomics and Bioinformatics, Standard Paper

Canonical manuscript: `paper_latex/main.tex`

Canonical reproducibility package: `release_code/`

## Completed scientific repairs

- Consolidated CK4, P, MSP and CK4P-MSP under the public `methods/ck4p_msp.py` contract.
- Recomputed manuscript-facing compact metrics in `results/stage3/contract_v2/` and removed historical feature aliases from current claims.
- Replaced row-random local delta-readout splitting with template-grouped validation.
- Added the seven non-empty K/P/MSP combinations and prespecified conditional contribution contrasts.
- Added a mechanism-aligned 2 x 2 audit separating spatial localization from substitution chemistry.
- Added signed KSG-style empirical-separability increments with paired bootstrap intervals and label-permutation inference.
- Added fixed-map/property-scaling, block-weight, MSP bin/gamma, sequence-permutation, Gaussian counterfactual and P/MSP relation audits.
- Added dimension-matched high-k hash/random-projection controls and a native MinHash Jaccard audit.
- Re-ran the lightweight CAMI II marine anonymous-read stability probe through the public method contract.
- Retained ART only as an explicitly historical simulator-context probe; it is not labelled as contract-v2 CK4P-MSP evidence.

## Evidence-boundary findings incorporated into the manuscript

- P and MSP are related because they use the same biochemical property family, but they are not interchangeable.
- P contributes primarily to lower global perturbation drift under the tested grid.
- MSP contributes most of the grouped local-change readout increment and adds coarse spatial organization.
- K preserves composition-linked nearest-clean retrieval; it is not described as exact read identity.
- CK4P-MSP does not exceed CK4 on raw local-to-nuisance distance amplification and is not presented as a mutation detector.
- Clean-partition-fitted CK7 PCA/SVD projections attain lower numerical drift than CK4P-MSP. The main method's differentiating properties are fixed construction, no training and block-level attribution, not universal minimum drift.
- MI values are estimator-dependent empirical separability estimates, not an information-theoretic theorem.
- CAMI_TOY_low supports coarse target/background readability and a weak 30-label boundary; CAMI II supports anonymous-read stability only.

## Manuscript and figure completion

- Main manuscript: 17 pages under the OUP authoring template.
- Supplementary manuscript: 12 pages with Figures S1-S11 and Tables S1-S7.
- Main and supplementary figure captions now state panel content, analysis unit, sample scale, uncertainty and metric direction where applicable.
- Final visual QA found no clipped labels, overlapping legends, broken equations, stranded figure sections or avoidable blank figure pages.
- Stable review PDFs are `paper_latex/paper_manuscript_latex.pdf` and `paper_latex/paper_supplementary_latex.pdf`.

## Reproducibility checks

The following checks passed from `release_code/`:

```text
python smoke_tests/test_imports.py
python smoke_tests/test_method_contract.py
python smoke_tests/test_repository_layout.py
python smoke_tests/test_contract_artifacts.py
python -m compileall -q methods data_pipeline experiments analysis scripts smoke_tests
```

The artifact smoke test regenerated one canonical manuscript table and Figure 3 from included result data.

## Open author-supplied submission items

- Confirm the institutional ethics/data-governance wording for aggregate restricted read-length provenance, or remove that provenance.
- Confirm funding attribution with the corresponding author.
- Finalize acknowledgements.
- Make the private repository reviewer-accessible at submission, then freeze a public release and mint an archival DOI.
- Verify the ISBN and final bibliographic metadata for *Practice and Progress of mNGS Report Interpretation*.

These items are deliberately left visible. The scientific and typesetting repair is complete, but the manuscript should not be labelled submission-ready until they are resolved.
