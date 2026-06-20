# Stage-2 Completion Report

## What was completed

1. V1 manuscript/results/code snapshot was archived under the project archive directory before stage-2 changes.
2. Stage-2 experiments were run with fixed seeds where sampling or model fitting was used.
3. Publication assets were generated from result CSV files, including manuscript tables and figures.
4. A revised V2 manuscript was generated in Markdown, DOCX, TeX and PDF formats.
5. The V2 PDF was rendered to PNG pages and visually checked through a contact sheet.
6. A reviewer-style self-audit was written to identify remaining evidence gaps and unsupported claims.
7. A deterministic PyTorch CPU neural compatibility probe was added after audit identified that CNN/tiny Transformer evidence was still only future work.

## Core experimental outputs

- Representation grid: `results/stage2/representation_grid`
- CSP component ablation: `results/stage2/csp_ablation`
- 69/75 bp hospital-like focus tables: `results/stage2/publication_assets/tables`
- Attention breakpoint diagnostic: `results/stage2/attention_breakpoint`
- ARG/SNP boundary probes: `results/stage2/arg_snp_boundary`
- k and spaced-pattern sensitivity: `results/stage2/parameter_sensitivity`
- Deterministic neural compatibility probes: `results/stage2/neural_compatibility`
- Publication-ready generated assets: `results/stage2/publication_assets`

## Main evidence summary

- CSP was the top clean-perturbed stability representation in 42/42 WGS-slice length-by-perturbation settings.
- CSP had the clearest advantage in 69/75 bp perturbation settings, especially N masking, local mismatch and combined perturbation.
- The CSP property block improved stability over canonical spaced seed counts; hydrogen-bond and entropy summaries were the strongest singleton additions.
- Readout probes did not show universal classification superiority for CSP. Canonical k-mer remained a strong high-resolution identity baseline.
- Neural compatibility probes trained 252 fixed-seed MLP/CNN/tiny Transformer combinations. They showed task-dependent model fit rather than universal neural superiority; CSP was most defensible as a compact tabular auxiliary input.
- Attention-context breakpoints depended on motif position, so the 125-150 bp transition should be discussed as a visibility problem rather than one fixed read-length threshold.
- ARG/SNP probes support CSP as auxiliary perturbation-stability evidence, not as a standalone ARG allele or resistance SNP caller.

## Manuscript outputs

- Markdown: `manuscript/stage2_manuscript_v2.md`
- DOCX: `manuscript/stage2_manuscript_v2.docx`
- TeX: `manuscript/stage2_manuscript_v2.tex`
- PDF: `manuscript/stage2_manuscript_v2.pdf`
- Rendered PDF pages/contact sheet: `manuscript/rendered_stage2_pdf`
- Reviewer self-audit: `manuscript/stage2_reviewer_self_audit.md`

## Rendering note

LibreOffice remains broken on this machine with a `bootstrap.ini` startup error, so DOCX visual rendering could not be validated through LibreOffice. The PDF generated from the same manuscript source was compiled with XeLaTeX and visually checked through rendered PNG pages. The DOCX was generated structurally with `python-docx` and should be treated as an editable manuscript draft rather than the visually verified layout artifact.

## Claims supported now

- CSP is compact, strand-friendly and perturbation-stable for controlled ultra-short read diagnostics.
- Canonical k-mer remains a strong identity evidence baseline for close-relative and exact sequence tasks.
- Hybrid or layered evidence is a better practical framing than replacing canonical k-mer with CSP.
- Read-length effects for attention-like models should be diagnosed by motif/context visibility, not by base count alone.
- Small local neural probes can test whether a representation is readable by a model family, but they do not establish clinical neural-model superiority.

## Claims that remain future work

- Clinical species identification accuracy.
- CSP-alone species identification.
- ARG allele calling or resistance SNP calling.
- Transformer/CNN superiority at realistic clinical scale.
- Kraken2/Centrifuge/Kaiju performance comparisons on matched noisy FASTQ.
- Real FASTQ quality-profile simulation with host/background mixtures.
- CARD/ResFinder/AMRFinderPlus grounded ARG benchmark.

## Suggested next phase

1. Build a server-scale WGS panel with genome-held-out splits and more strains per genus.
2. Run same-FASTQ Kraken2/Centrifuge/Kaiju sanity comparisons.
3. Build a real ARG marker benchmark from curated databases.
4. Add one schematic figure showing the layered evidence model.
5. Convert wide tables into supplementary tables for target-journal submission.
