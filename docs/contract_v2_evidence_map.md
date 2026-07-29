# Contract-v2 Evidence Map

This map records the evidence eligible for manuscript claims about the public
`ck4p_msp` implementation. It prevents historical feature aliases and current
results from being combined in a single claim.

| Claim role | Script | Result directory | Interpretation boundary |
|---|---|---|---|
| Compact stability | `experiments/main/run_stage3_compact_baselines.py` and `experiments/audits/run_high_k_compressed_baselines.py` | `results/stage3/contract_v2/compact_baselines/` and `results/stage3/contract_v2/high_k_compressed_baselines/` | CK4P-MSP is more stable than CK4/CK5 and the tested 222-dimensional high-k vector controls; shallow readout does not lead every baseline. |
| Seven-group K/P/MSP ablation | `experiments/audits/run_p_msp_contribution_audit.py` | `results/stage3/contract_v2/p_msp_contribution/` | All non-empty block combinations and three prespecified conditional contrasts are reported; metric-specific contributions are not an orthogonality or universal-necessity proof. |
| Local-change readout | `experiments/main/run_local_mutation_sensitivity.py` | `results/stage3/contract_v2/local_mutation_sensitivity/` | Grouped template-level cross-validation tests local-change versus matched-noise readability. |
| High-k compactness control | `experiments/audits/run_high_k_compressed_baselines.py` | `results/stage3/contract_v2/high_k_compressed_baselines/` | Hashing-trick and random-projection vectors are L2 controls; MinHash is reported only through native collision/Jaccard agreement. |
| Fitted linear-reduction boundary | `experiments/audits/run_dimension_reduction_baselines.py` | `results/stage3/contract_v2/dimension_reduction_baselines/` | Clean-partition-fitted CK7 PCA/SVD can achieve lower drift than CK4P-MSP. This is a data-dependent boundary, not evidence that CK4P-MSP minimizes drift. |
| Fixed-weight and sequence-link controls | `experiments/audits/run_mixed_metric_audit.py` and `experiments/audits/run_p_channel_counterfactual_audit.py` | `results/stage3/contract_v2/mixed_metric_audit/` and `results/stage3/contract_v2/p_channel_counterfactual_audit/` | Grouped readout is stable across non-zero K/P/MSP weights, and sequence-linked P/MSP outperforms permuted or Gaussian added blocks. These are empirical controls rather than an optimal-weight theorem. |
| Empirical signal-separability audit | `experiments/audits/run_knn_mi_robustness_audit.py` | `results/stage3/contract_v2/knn_mi_robustness/` | KSG-style estimates are estimator-dependent empirical summaries, not a theorem. |
| Factorial local-change mechanism audit | `experiments/audits/run_local_change_factorial_audit.py` | `results/stage3/contract_v2/local_change_factorial/` | Separates spatial localization from substitution chemistry with grouped template-level splits. |
| Property-coordinate scaling audit | `experiments/audits/run_property_scaling_audit.py` | `results/stage3/contract_v2/property_scaling/` | Tests fixed map rescaling and a deliberately aggressive train-fit z-score boundary; it is not a scale-invariance proof. |
| MSP sensitivity | `experiments/audits/run_msp_bin_gamma_sensitivity_audit.py` | `results/stage3/contract_v2/msp_bin_gamma_sensitivity/` | Tests whether the pre-set bins and weight are brittle; it does not select an optimal weight. |
| Local-change fraction boundary | `experiments/audits/run_local_mutation_fraction_sweep.py` | `results/stage3/contract_v2/local_mutation_fraction_sweep/` | Grouped delta-readout is reported across 1%, 3% and 5% synthetic local changes; it is not functional-variant validation. |
| P/MSP relation | `experiments/audits/run_property_redundancy_and_runtime_audit.py` | `results/stage3/contract_v2/property_redundancy_runtime/` | CCA/rank summaries show relation rather than independence. The earlier runtime output is retained for provenance but is superseded by the common-protocol historical audit for manuscript timing claims. |
| Historical handcrafted-descriptor boundary and common runtime | `experiments/audits/run_historical_descriptor_audit.py` | `results/stage3/contract_v2/historical_descriptor_audit/` | PseKNC has lower drift and dimension, whereas CK4P-MSP has stronger grouped local-change readability. Runtime uses warm-up, randomized within-repeat order, pre-timing garbage collection and one numerical-library thread; it remains implementation- and hardware-specific. |
| CAMI_TOY contract-v2 readout | `experiments/main/run_stage3_cami_probe.py` | `results/stage3/contract_v2/cami_toy_readout/` | Supports bounded external readout on one low-complexity source; it is not production-scale taxonomic validation. |
| CAMI II marine contract-v2 stability | `data_pipeline/simulate/run_cami2_marine_lightweight_probe.py` | `results/stage3/contract_v2/cami2_marine_stability/` | Supports paired stability under composition shift; anonymous reads provide no taxonomic endpoint. |

## Ineligible legacy interpretations

- Historical `ckmer4_property_multiscale_mean_l2` results must not be relabelled
  as the public block-normalized CK4P-MSP method.
- MinHash signatures must not be compared by vector L2 drift or used as a
  linear readout feature without a separately justified representation.
- Non-grouped local-change splits must not be used for manuscript delta-readout
  claims.
