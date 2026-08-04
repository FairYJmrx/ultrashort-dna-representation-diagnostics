# Code Layout and Source-of-Truth Rules

This document defines where maintained code lives in the release. It prevents
the manuscript method, experiment commands and figure generators from drifting
into separate implementations.

## Maintained Modules

| Directory | Contains | Must not contain |
|---|---|---|
| `methods/` | Canonical representation implementations and reusable feature helpers. | Experiment-specific data loading, plotting or manuscript text. |
| `data_pipeline/download/` | Public download and remote archive inspection. | Representation comparisons. |
| `data_pipeline/preprocess/` | Read construction, local FASTA slicing and preprocessing. | Statistical result summaries. |
| `data_pipeline/simulate/` | ART and external-source simulation probes. | Final figure assembly. |
| `experiments/main/` | Main experimental protocols and bounded comparison studies. | Manuscript rendering. |
| `experiments/audits/` | Sensitivity, counterfactual, redundancy, MI and baseline audits. | Alternative method definitions. |
| `analysis/tables/` | Summary table and confidence-interval generation. | Data simulation. |
| `analysis/figures/` | Main and supplementary figure generation. | Primary experiment execution. |
| `analysis/audits/` | Provenance and result-inventory validation. | Scientific result mutation. |

## Compatibility Policy

`scripts/` contains thin backwards-compatible imports only. New commands,
documentation and manuscript-to-script mappings must point to one of the
maintained directories above. Historical Word builders and superseded release
packaging are intentionally excluded from this public snapshot.

## Method Rule

The manuscript main representation is selected by the explicit name
`ck4p_msp` and constructed by `methods.ck4p_msp`. Historical
`ckmer*_property_*` feature names remain available for archival analyses but
must not be relabelled as CK4P-MSP.

## Result Rule

Each rerun writes its own directory and JSON manifest under `results/`. New
contract-correct reruns are placed under `results/stage3/contract_v2/` until
their figures and manuscript tables have been regenerated and reviewed. Old
results are retained for provenance but must not be combined numerically with
the contract-v2 evidence.
