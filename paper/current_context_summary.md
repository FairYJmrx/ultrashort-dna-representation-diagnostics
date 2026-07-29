# Current Context Summary

This file compresses the active manuscript context after adding the CAMI II marine lightweight probe. It applies to the manuscript sources under `paper/`.

## Locked manuscript identity

- Manuscript type: methods-oriented representation-diagnostics paper.
- Active draft folder: `paper/`.
- Do not edit or rely on `final_manuscript.md`.
- Core method: CK4P-MSP, implemented as the compact 222-dimensional `ckmer4_property_multiscale_mean_l2` representation.
- Core framing: representation-level audit of identity, biochemical and positional channels under controlled short-read perturbation.
- Not a clinical diagnostic tool, end-to-end classifier, Kraken2 replacement, ARG/SNP detector, or production triage pipeline.

## Claim boundaries

- Use `representation diagnostics` to mean prespecified representation-level audit readouts: paired stability, block-wise drift, nearest-clean retrieval, shallow readout and local delta-readout.
- Mixed-space L2 is `standardized diagnostic drift`, not a natural biophysical distance across commensurate units.
- MI/conditional MI results are estimator-dependent empirical audits, not universal information-theoretic proof.
- P and MSP are related but not interchangeable. P is a global biochemical stability summary. MSP positionalizes the same property family to return coarse layout information to the compact k-mer backbone.
- Avoid `orthogonal`, `first`, `unprecedented`, `prove`, `theorem`, `clinical validation`, `pipeline improvement`, `false-hit reduction`, `triage` and direct `confidence calibration` claims unless a corresponding experiment is actually added.

## Completed CAMI II marine lightweight probe

- Dataset: CAMI II marine short-read sample 0.
- Source URL: `https://frl.publisso.de/data/frl:6425521/marine/short_read/marmgCAMI2_sample_0_reads.tar.gz`.
- Setup URL: `https://frl.publisso.de/data/frl:6425521/marine/short_read/marmgCAMI2_setup.tar.gz`.
- Parsed subset: 4,000 anonymous 150 bp reads from `anonymous_reads.fq.gz`.
- Expanded rows: 48,000 across 69, 75 and 100 bp; clean, N_3pct, substitution_1pct and substitution_1pct_N_3pct conditions.
- Result directory: `results/stage3/cami2_marine_lightweight_probe_core/`.
- Source script: `scripts/run_cami2_marine_lightweight_probe.py`.
- Figure script: `scripts/generate_supp_fig_s10_cami2_marine_probe.py`.
- Figure asset: `paper/figures/supp_fig_s10_cami2_marine_probe.*`.
- Source table: `paper/tables/supp_table_s10_cami2_marine_probe_source.csv`.
- Result: CK4P-MSP had the lowest mean L2 drift in all 9 tested length by perturbation cells and maintained high paired cosine.
- Boundary: FASTQ headers are anonymous (`S0R...`) and do not provide read-level taxonomy. Large OTU-specific BAM truth bundles were not downloaded. Therefore this probe is an external perturbation-stability probe, not CAMI II taxonomic validation and not a macro-F1 readout benchmark.

## Manuscript integration rule

- Add CAMI II marine to Methods as an external anonymous-read perturbation-stability probe without reconstructed read-level taxonomic labels in this lightweight analysis.
- Add one short Results paragraph after the existing external ART/CAMI probe section.
- Cite Supplementary Figure S10 and Supplementary Table S10 source data.
- Update limitations to distinguish CAMI_TOY_low labelled readout from CAMI II marine anonymous-read paired stability.
- Do not move CAMI II into main figures unless the manuscript scope changes.
