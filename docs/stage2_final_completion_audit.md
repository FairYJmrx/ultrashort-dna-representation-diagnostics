# Stage-2 Final Completion Audit

Date: 2026-06-20

Objective audited: back up V1, complete the stage-2 representation advantage grid, 69/75 hospital-like scenario, CSP ablation, readout probes, attention breakpoint analysis, lightweight neural models, ARG/SNP boundary tasks, k/pattern sensitivity, and rewrite the manuscript accordingly.

## Requirement-by-requirement status

| Requirement | Evidence | Status |
|---|---|---|
| V1 backup before new stage | `archive/V1_20260620_160424/V1_MANIFEST.md` plus local V1 archive directory | Completed |
| Advantage-region representation grid | `results/stage2/representation_grid/stability_grid.csv`, `results/stage2/representation_grid/readout_grid.csv` | Completed |
| 69/75 bp hospital-like short-read focus | `results/stage2/publication_assets/tables/stage2_table_hospital_69_75_focus.md`, `results/stage2/publication_assets/figures/stage2_fig_hospital_69_75_l2.png` | Completed |
| CSP internal ablation | `results/stage2/csp_ablation/csp_ablation_metrics.csv`, `results/stage2/publication_assets/tables/stage2_table_csp_component_singletons.md` | Completed |
| Lightweight readout probes | `results/stage2/representation_grid/readout_grid.csv`, `results/stage2/publication_assets/tables/stage2_table_readout_aggregate.md` | Completed |
| Attention breakpoint analysis | `results/stage2/attention_breakpoint/attention_breakpoint_results.csv`, `results/stage2/attention_breakpoint/attention_breakpoint_change_points.csv` | Completed |
| Lightweight neural model compatibility | `results/stage2/neural_compatibility/neural_compatibility_results.csv`, `results/stage2/neural_compatibility/neural_training_history.csv`, `results/stage2/publication_assets/tables/stage2_table_neural_compatibility_aggregate.md` | Completed |
| ARG/SNP boundary tasks | `results/stage2/arg_snp_boundary/arg_snp_stability.csv`, `results/stage2/arg_snp_boundary/arg_snp_readout.csv` | Completed as synthetic boundary probes |
| k and spaced-pattern sensitivity | `results/stage2/parameter_sensitivity/parameter_stability_metrics.csv`, `results/stage2/parameter_sensitivity/parameter_classification_probes.csv` | Completed |
| Publication assets | `results/stage2/publication_assets/stage2_evidence_summary.md`, `results/stage2/publication_assets/figures`, `results/stage2/publication_assets/tables` | Completed |
| Manuscript rewrite | `manuscript/stage2_manuscript_v2.md`, `manuscript/stage2_manuscript_v2.docx`, `manuscript/stage2_manuscript_v2.tex`, `manuscript/stage2_manuscript_v2.pdf` | Completed |
| Reviewer-style self-audit | `manuscript/stage2_reviewer_self_audit.md` | Completed |
| Deterministic random seeds | Stage-2 scripts expose fixed `--seed`; neural script sets Python, NumPy and PyTorch seeds, deterministic algorithms and single-thread execution | Completed |
| GitHub archival | Remote `origin` is `https://github.com/FairYJmrx/ultrashort-dna-representation-diagnostics.git`, visibility checked as private | Completed |

## Main supported claims

- CSP is a compact, strand-friendly and perturbation-stable auxiliary representation for controlled ultra-short read diagnostics.
- Canonical k-mer remains a strong identity-evidence baseline for close-relative, allele-like and SNP-like tasks.
- Hybrid or layered evidence is the most defensible practical framing.
- Short-read context loss should be diagnosed through explicit motif/context visibility, not read length alone.
- Small deterministic neural probes show model compatibility is task-dependent; they do not prove clinical-scale CNN or Transformer superiority.

## Claims still not supported as main-paper conclusions

- Clinical species-identification accuracy.
- CSP-alone species identification.
- ARG allele calling or resistance SNP calling.
- Clinical-scale Transformer/CNN superiority.
- Kraken2/Centrifuge/Kaiju pipeline superiority or inferiority.
- Real FASTQ quality-profile behavior with host/background mixtures.
- CARD/ResFinder/AMRFinderPlus grounded ARG benchmark performance.

## Rendering and document QA

- PDF was compiled with XeLaTeX.
- PDF pages were rendered with Poppler for visual QA.
- LibreOffice remains broken locally with a `bootstrap.ini` startup error, so DOCX visual QA through LibreOffice could not be completed. The DOCX is an editable draft generated from the same manuscript source; the PDF is the visually checked artifact.

