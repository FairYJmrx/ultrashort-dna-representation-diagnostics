# Methods Package

`methods/` is the canonical implementation package for representation
construction and evaluation helpers.

The old `src/` namespace is retained only as a compatibility layer for
historical scripts. New code should import from `methods.*`.

## Module Map

| Module | Role |
|---|---|
| `sequence_utils.py` | DNA sequence helpers, reverse complement, k-mer tokenization and perturbation utilities. |
| `base_encodings.py` | Global biochemical scalar encodings, including hydrogen-bond class, GC, purine and EIIP-related signals. |
| `sklearn_features.py` | Canonical k-mer count matrices, TF-IDF-style transformations and compressed k-mer controls. |
| `position_encodings.py` | Full-position and position-aware encodings used as upper-bound diagnostics. |
| `spaced_features.py` | Spaced-seed and canonical spaced-property controls. |
| `representation_registry.py` | Registry for named representation families used by experiment scripts. |
| `stage2_features.py` | Shared feature-construction layer for CK4, CK5, P, MSP, CK4+P, CK4+MSP, CK4P-MSP and boundary controls. |
| `evaluation.py`, `ml_eval.py` | Lightweight evaluation and shallow readout helpers. |
| `toy_data.py` | Controlled toy and perturbation data helpers. |
| `token_audit.py` | Token-level audit utilities. |

