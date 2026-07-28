# Contract-v2 Evidence Map

This map records the evidence eligible for manuscript claims about the public
`ck4p_msp` implementation. It prevents historical feature aliases and current
results from being combined in a single claim.

| Claim role | Script | Result directory | Interpretation boundary |
|---|---|---|---|
| Compact stability | `experiments/main/run_stage3_compact_baselines.py` | `results/stage3/contract_v2/compact_baselines/` | CK4P-MSP is more stable than CK4/CK5; CK4+P is more stable globally. |
| P/MSP ablation | `experiments/audits/run_p_msp_contribution_audit.py` | `results/stage3/contract_v2/p_msp_contribution/` | P and MSP contribute distinct empirical effects; this is not an orthogonality proof. |
| Local-change readout | `experiments/main/run_local_mutation_sensitivity.py` | `results/stage3/contract_v2/local_mutation_sensitivity/` | Grouped template-level cross-validation tests local-change versus matched-noise readability. |
| High-k compactness control | `experiments/audits/run_high_k_compressed_baselines.py` | `results/stage3/contract_v2/high_k_compressed_baselines/` | Hashing-trick and random-projection vectors are L2 controls; MinHash is reported only through native collision/Jaccard agreement. |
| Empirical signal-separability audit | `experiments/audits/run_knn_mi_robustness_audit.py` | `results/stage3/contract_v2/knn_mi_robustness/` | KSG-style estimates are estimator-dependent empirical summaries, not a theorem. |
| MSP sensitivity | `experiments/audits/run_msp_bin_gamma_sensitivity_audit.py` | `results/stage3/contract_v2/msp_bin_gamma_sensitivity/` | Tests whether the pre-set bins and weight are brittle; it does not select an optimal weight. |
| P/MSP relation and runtime | `experiments/audits/run_property_redundancy_and_runtime_audit.py` | `results/stage3/contract_v2/property_redundancy_runtime/` | CCA/rank summaries show relation rather than independence; runtime is an engineering boundary. |

## Ineligible legacy interpretations

- Historical `ckmer4_property_multiscale_mean_l2` results must not be relabelled
  as the public block-normalized CK4P-MSP method.
- MinHash signatures must not be compared by vector L2 drift or used as a
  linear readout feature without a separately justified representation.
- Non-grouped local-change splits must not be used for manuscript delta-readout
  claims.
