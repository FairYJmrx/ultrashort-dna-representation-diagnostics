# Seven-group K/P/MSP contribution audit

Purpose: evaluate all seven non-empty combinations of the canonical local k-mer composition block (K), global biochemical property block (P), and multi-scale positional property block (MSP) under the same internally normalized block-concatenation rule used in the manuscript.

Interpretation boundary: this audit does not assume that K, P and MSP are orthogonal or statistically independent. It tests metric-specific conditional contributions under the controlled perturbation grid.

## Run metadata

|   elapsed_seconds | reads                                                                                                      | triplets                                                                                                      | lengths            | conditions                                                                                                   |   max_pairs |   max_triplets |   cv_folds |     seed |
|------------------:|:-----------------------------------------------------------------------------------------------------------|:--------------------------------------------------------------------------------------------------------------|:-------------------|:-------------------------------------------------------------------------------------------------------------|------------:|---------------:|-----------:|---------:|
|            16.157 | results/stage3/contract_v2/compact_baselines/stage3_compact_baseline_reads.csv | results/stage3/contract_v2/local_mutation_sensitivity/local_mutation_triplets.csv | [69, 75, 100, 150] | ['substitution_1pct', 'N_3pct', 'trim_5bp', 'substitution_1pct_N_3pct', 'local_mismatch_6bp', 'short_indel'] |         500 |            400 |          5 | 20260625 |

## Stability summary

| representation   | representation_label   |   n_cells |   n_features |   paired_cosine_mean |   l2_delta_mean |   retrieval_top1_mean |
|:-----------------|:-----------------------|----------:|-------------:|---------------------:|----------------:|----------------------:|
| p                | P                      |        24 |      11.0000 |               0.9994 |          0.0247 |                0.2948 |
| msp              | MSP                    |        24 |      75.0000 |               0.9995 |          0.0265 |                0.9581 |
| p_msp            | P+MSP                  |        24 |      86.0000 |               0.9994 |          0.0273 |                0.9417 |
| ck4p_msp        | CK4P-MSP               |        24 |     222.0000 |               0.9894 |          0.1286 |                0.9999 |
| ck4_msp          | CK4+MSP                |        24 |     211.0000 |               0.9844 |          0.1557 |                0.9999 |
| ck4_p            | CK4+P                  |        24 |     147.0000 |               0.9844 |          0.1560 |                0.9999 |
| ck4              | CK4                    |        24 |     136.0000 |               0.9694 |          0.2182 |                0.9998 |

## Stability by length

|   length | representation   | representation_label   |   n_cells |   paired_cosine_mean |   l2_delta_mean |   retrieval_top1_mean |
|---------:|:-----------------|:-----------------------|----------:|---------------------:|----------------:|----------------------:|
|       69 | p                | P                      |         6 |               0.9993 |          0.0263 |                0.2813 |
|       69 | p_msp            | P+MSP                  |         6 |               0.9993 |          0.0310 |                0.9210 |
|       69 | msp              | MSP                    |         6 |               0.9993 |          0.0320 |                0.9297 |
|       69 | ck4p_msp        | CK4P-MSP               |         6 |               0.9862 |          0.1459 |                1.0000 |
|       69 | ck4_p            | CK4+P                  |         6 |               0.9797 |          0.1769 |                1.0000 |
|       69 | ck4_msp          | CK4+MSP                |         6 |               0.9797 |          0.1770 |                1.0000 |
|       69 | ck4              | CK4                    |         6 |               0.9600 |          0.2477 |                0.9997 |
|       75 | p                | P                      |         6 |               0.9994 |          0.0244 |                0.2877 |
|       75 | p_msp            | P+MSP                  |         6 |               0.9994 |          0.0288 |                0.9427 |
|       75 | msp              | MSP                    |         6 |               0.9994 |          0.0297 |                0.9473 |
|       75 | ck4p_msp        | CK4P-MSP               |         6 |               0.9877 |          0.1379 |                1.0000 |
|       75 | ck4_p            | CK4+P                  |         6 |               0.9819 |          0.1673 |                1.0000 |
|       75 | ck4_msp          | CK4+MSP                |         6 |               0.9819 |          0.1674 |                1.0000 |
|       75 | ck4              | CK4                    |         6 |               0.9643 |          0.2343 |                1.0000 |
|      100 | msp              | MSP                    |         6 |               0.9996 |          0.0253 |                0.9667 |
|      100 | p                | P                      |         6 |               0.9993 |          0.0256 |                0.2930 |
|      100 | p_msp            | P+MSP                  |         6 |               0.9994 |          0.0271 |                0.9477 |
|      100 | ck4p_msp        | CK4P-MSP               |         6 |               0.9903 |          0.1254 |                0.9997 |
|      100 | ck4_msp          | CK4+MSP                |         6 |               0.9858 |          0.1517 |                0.9997 |
|      100 | ck4_p            | CK4+P                  |         6 |               0.9857 |          0.1523 |                0.9997 |
|      100 | ck4              | CK4                    |         6 |               0.9720 |          0.2126 |                0.9997 |
|      150 | msp              | MSP                    |         6 |               0.9998 |          0.0191 |                0.9887 |
|      150 | p_msp            | P+MSP                  |         6 |               0.9996 |          0.0222 |                0.9557 |
|      150 | p                | P                      |         6 |               0.9994 |          0.0224 |                0.3173 |
|      150 | ck4p_msp        | CK4P-MSP               |         6 |               0.9934 |          0.1050 |                1.0000 |
|      150 | ck4_msp          | CK4+MSP                |         6 |               0.9904 |          0.1268 |                1.0000 |
|      150 | ck4_p            | CK4+P                  |         6 |               0.9902 |          0.1276 |                1.0000 |
|      150 | ck4              | CK4                    |         6 |               0.9810 |          0.1780 |                1.0000 |

## Local mutation distance summary

| representation   | representation_label   |   n_cells |   n_features |   noise_l2_mean |   local_l2_mean |   local_minus_noise_l2_mean |   selective_sensitivity_ratio_mean |   selective_sensitivity_ratio_n_valid |   selective_sensitivity_ratio_valid_fraction |
|:-----------------|:-----------------------|----------:|-------------:|----------------:|----------------:|----------------------------:|-----------------------------------:|--------------------------------------:|---------------------------------------------:|
| msp              | MSP                    |      3000 |      75.0000 |          0.0179 |          0.0211 |                      0.0032 |                             1.3990 |                                  2988 |                                       0.9960 |
| p_msp            | P+MSP                  |      3000 |      86.0000 |          0.0135 |          0.0159 |                      0.0024 |                             1.3077 |                                  2988 |                                       0.9960 |
| p                | P                      |      3000 |      11.0000 |          0.0061 |          0.0073 |                      0.0012 |                             1.8562 |                                  2854 |                                       0.9513 |
| ck4p_msp        | CK4P-MSP               |      3000 |     222.0000 |          0.2053 |          0.1540 |                     -0.0513 |                             0.7523 |                                  3000 |                                       1.0000 |
| ck4_msp          | CK4+MSP                |      3000 |     211.0000 |          0.2514 |          0.1885 |                     -0.0629 |                             0.7521 |                                  3000 |                                       1.0000 |
| ck4_p            | CK4+P                  |      3000 |     147.0000 |          0.2511 |          0.1879 |                     -0.0632 |                             0.7506 |                                  3000 |                                       1.0000 |
| ck4              | CK4                    |      3000 |     136.0000 |          0.3551 |          0.2656 |                     -0.0895 |                             0.7504 |                                  3000 |                                       1.0000 |

## Delta-readout summary

| representation   | representation_label   | classifier   |   n_cells |   n_features |   macro_f1_mean |   macro_f1_std_mean |   accuracy_mean |
|:-----------------|:-----------------------|:-------------|----------:|-------------:|----------------:|--------------------:|----------------:|
| ck4p_msp        | CK4P-MSP               | logistic     |        12 |     222.0000 |          0.9786 |              0.0090 |          0.9787 |
| ck4_msp          | CK4+MSP                | logistic     |        12 |     211.0000 |          0.9780 |              0.0102 |          0.9780 |
| p_msp            | P+MSP                  | logistic     |        12 |      86.0000 |          0.9704 |              0.0125 |          0.9705 |
| msp              | MSP                    | logistic     |        12 |      75.0000 |          0.9652 |              0.0133 |          0.9653 |
| ck4_p            | CK4+P                  | logistic     |        12 |     147.0000 |          0.9043 |              0.0230 |          0.9045 |
| ck4              | CK4                    | logistic     |        12 |     136.0000 |          0.8923 |              0.0264 |          0.8925 |
| p                | P                      | logistic     |        12 |      11.0000 |          0.6391 |              0.0427 |          0.6407 |

## Delta-readout by length

|   length | representation   | representation_label   |   n_cells |   macro_f1_mean |   macro_f1_std_mean |   accuracy_mean |
|---------:|:-----------------|:-----------------------|----------:|----------------:|--------------------:|----------------:|
|       69 | ck4_msp          | CK4+MSP                |         4 |          0.9599 |              0.0158 |          0.9600 |
|       69 | ck4p_msp        | CK4P-MSP               |         4 |          0.9594 |              0.0143 |          0.9595 |
|       69 | p_msp            | P+MSP                  |         4 |          0.9588 |              0.0150 |          0.9590 |
|       69 | msp              | MSP                    |         4 |          0.9506 |              0.0158 |          0.9510 |
|       69 | ck4_p            | CK4+P                  |         4 |          0.7845 |              0.0375 |          0.7850 |
|       69 | ck4              | CK4                    |         4 |          0.7605 |              0.0426 |          0.7610 |
|       69 | p                | P                      |         4 |          0.6262 |              0.0522 |          0.6275 |
|      100 | ck4p_msp        | CK4P-MSP               |         4 |          0.9820 |              0.0063 |          0.9820 |
|      100 | ck4_msp          | CK4+MSP                |         4 |          0.9810 |              0.0074 |          0.9810 |
|      100 | p_msp            | P+MSP                  |         4 |          0.9750 |              0.0094 |          0.9750 |
|      100 | msp              | MSP                    |         4 |          0.9705 |              0.0125 |          0.9705 |
|      100 | ck4_p            | CK4+P                  |         4 |          0.9479 |              0.0187 |          0.9480 |
|      100 | ck4              | CK4                    |         4 |          0.9379 |              0.0213 |          0.9380 |
|      100 | p                | P                      |         4 |          0.6685 |              0.0349 |          0.6695 |
|      150 | ck4p_msp        | CK4P-MSP               |         4 |          0.9945 |              0.0064 |          0.9945 |
|      150 | ck4_msp          | CK4+MSP                |         4 |          0.9930 |              0.0074 |          0.9930 |
|      150 | ck4_p            | CK4+P                  |         4 |          0.9805 |              0.0129 |          0.9805 |
|      150 | ck4              | CK4                    |         4 |          0.9785 |              0.0152 |          0.9785 |
|      150 | p_msp            | P+MSP                  |         4 |          0.9775 |              0.0130 |          0.9775 |
|      150 | msp              | MSP                    |         4 |          0.9744 |              0.0116 |          0.9745 |
|      150 | p                | P                      |         4 |          0.6225 |              0.0409 |          0.6250 |

## Prespecified conditional-contribution contrasts

Positive improvement values favour the complete CK4P-MSP representation. Confidence intervals are paired-cell bootstrap intervals; Wilcoxon tests are two-sided and q values use Benjamini-Hochberg correction across the 12 prespecified rows.

| contrast    | full_representation   | comparator   | evidence_layer                | metric             | metric_direction   | paired_unit             |   n_pairs |   full_mean |   comparator_mean |   mean_improvement_positive_is_better |   bootstrap_95_ci_low |   bootstrap_95_ci_high |   wilcoxon_two_sided_p |   full_better_fraction |   bh_q |
|:------------|:----------------------|:-------------|:------------------------------|:-------------------|:-------------------|:------------------------|----------:|------------:|------------------:|--------------------------------------:|----------------------:|-----------------------:|-----------------------:|-----------------------:|-------:|
| K | P+MSP   | ck4p_msp             | p_msp        | global_perturbation_stability | paired_cosine_mean | higher             | length+condition        |        24 |      0.9894 |            0.9994 |                               -0.0100 |               -0.0126 |                -0.0077 |                 0.0000 |                 0.0000 | 0.0000 |
| K | P+MSP   | ck4p_msp             | p_msp        | global_perturbation_stability | l2_delta_mean      | lower              | length+condition        |        24 |      0.1286 |            0.0273 |                               -0.1013 |               -0.1178 |                -0.0865 |                 0.0000 |                 0.0000 | 0.0000 |
| K | P+MSP   | ck4p_msp             | p_msp        | global_perturbation_stability | retrieval_top1     | higher             | length+condition        |        24 |      0.9999 |            0.9418 |                                0.0582 |                0.0364 |                 0.0808 |                 0.0004 |                 0.6667 | 0.0007 |
| K | P+MSP   | ck4p_msp             | p_msp        | grouped_local_delta_readout   | macro_f1           | higher             | length+local_mode+split |        12 |      0.9786 |            0.9704 |                                0.0082 |               -0.0002 |                 0.0185 |                 0.3804 |                 0.6667 | 0.5072 |
| P | CK4+MSP | ck4p_msp             | ck4_msp      | global_perturbation_stability | paired_cosine_mean | higher             | length+condition        |        24 |      0.9894 |            0.9844 |                                0.0050 |                0.0038 |                 0.0063 |                 0.0000 |                 1.0000 | 0.0000 |
| P | CK4+MSP | ck4p_msp             | ck4_msp      | global_perturbation_stability | l2_delta_mean      | lower              | length+condition        |        24 |      0.1286 |            0.1557 |                                0.0272 |                0.0233 |                 0.0313 |                 0.0000 |                 1.0000 | 0.0000 |
| P | CK4+MSP | ck4p_msp             | ck4_msp      | global_perturbation_stability | retrieval_top1     | higher             | length+condition        |        24 |      0.9999 |            0.9999 |                                0.0000 |                0.0000 |                 0.0000 |                 1.0000 |                 0.0000 | 1.0000 |
| P | CK4+MSP | ck4p_msp             | ck4_msp      | grouped_local_delta_readout   | macro_f1           | higher             | length+local_mode+split |        12 |      0.9786 |            0.9780 |                                0.0007 |               -0.0002 |                 0.0015 |                 0.4375 |                 0.3333 | 0.5250 |
| MSP | CK4+P | ck4p_msp             | ck4_p        | global_perturbation_stability | paired_cosine_mean | higher             | length+condition        |        24 |      0.9894 |            0.9844 |                                0.0050 |                0.0038 |                 0.0064 |                 0.0000 |                 1.0000 | 0.0000 |
| MSP | CK4+P | ck4p_msp             | ck4_p        | global_perturbation_stability | l2_delta_mean      | lower              | length+condition        |        24 |      0.1286 |            0.1560 |                                0.0275 |                0.0232 |                 0.0318 |                 0.0000 |                 1.0000 | 0.0000 |
| MSP | CK4+P | ck4p_msp             | ck4_p        | global_perturbation_stability | retrieval_top1     | higher             | length+condition        |        24 |      0.9999 |            0.9999 |                                0.0000 |                0.0000 |                 0.0000 |                 1.0000 |                 0.0000 | 1.0000 |
| MSP | CK4+P | ck4p_msp             | ck4_p        | grouped_local_delta_readout   | macro_f1           | higher             | length+local_mode+split |        12 |      0.9786 |            0.9043 |                                0.0743 |                0.0347 |                 0.1171 |                 0.0005 |                 1.0000 | 0.0007 |
