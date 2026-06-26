# Dataset Scale Inventory

This file records dataset scale details that should be surfaced in Methods/Table 2 before submission. Counts are from local result files, not from the manuscript prose.

| Data layer | Total rows | Unique clean/read templates | Lengths | Genera | Species/labels | Notes |
|---|---:|---:|---|---:|---:|---|
| WGS compact baseline reads | 25,200 | 3,600 | 69, 75, 100, 125, 150, 300 | 6 | 21 | 7 conditions; main compact/stability baseline dataset |
| Position-property ablation reads | 36,000 | 3,600 | 69, 75, 100, 125, 150, 300 | 6 | 21 | 10 conditions; main CK4/CK4+P/CK4P-MSP ablation dataset |
| ART Illumina paired reads | 75,592 | 37,796 | 69, 75, 100, 125, 150 | 6 | 21 | 2 conditions; clean plus ART paired rows |
| CAMI_TOY_low probe reads | 104,166 | 7,460 | 69, 75, 100 | 30 | 30 | 3 conditions; initial labelled CAMI subset |
| CAMI_TOY_low expanded probe reads | 216,000 | 16,342 | 69, 75, 100 | 30 | 30 | 3 conditions; expanded labelled CAMI subset used by later probes |
| CAMI C4P fast probe reads | 216,000 | 16,342 | 69, 75, 100 | 30 | 30 | 3 conditions; same expanded CAMI subset for c4p ablation |
| CAMI II marine subset probe | 48,000 | 4,000 | 69, 75, 100 | NA | not reconstructed | 4 conditions; external CAMI II marine sample_0 anonymous-read perturbation-stability probe, not taxonomic validation |
| Local mutation sensitivity summary | 144 summary rows | 250 triplets per cell | 69, 100, 150 | NA | NA | 12 representations; 4 local modes |

## Immediate manuscript implication

- The current manuscript mentions lightweight CAMI and controlled short-read settings, but it does not yet consistently report read counts, label counts, genera/species counts or length grids in the Methods text.
- Table 2 should be expanded or paired with a dataset-scale table so reviewers can assess whether each data layer is a toy check, controlled grid, simulator validation or external probe.
- The 69/75 bp clinical provenance statement is present, but it should remain separate from dataset scale because restricted clinical reads were not used as experimental input.
- The CAMI II marine subset should be described as an external anonymous-read perturbation-stability probe without reconstructed read-level taxonomic labels in this lightweight analysis. Its anonymous FASTQ headers do not provide direct taxonomic labels, and the large OTU-specific BAM truth bundles were not downloaded for this lightweight repair.
