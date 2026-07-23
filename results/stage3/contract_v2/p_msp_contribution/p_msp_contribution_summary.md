# P/MSP contribution audit

Purpose: separate the global biochemical property block (P) from the multi-scale positional property block (MSP) under the same internally normalized block-concatenation rule used in the manuscript.

Interpretation boundary: this audit does not assume that P and MSP are orthogonal. It asks whether adding P, MSP, or both changes perturbation stability and local-delta readability in distinct ways.

## Run metadata

|   elapsed_seconds | reads                                                                          | triplets                                                                          | lengths            | conditions                                                                                                   |   max_pairs |   max_triplets |   cv_folds |     seed |
|------------------:|:-------------------------------------------------------------------------------|:----------------------------------------------------------------------------------|:-------------------|:-------------------------------------------------------------------------------------------------------------|------------:|---------------:|-----------:|---------:|
|            44.006 | results\stage3\contract_v2\compact_baselines\stage3_compact_baseline_reads.csv | results\stage3\contract_v2\local_mutation_sensitivity\local_mutation_triplets.csv | [69, 75, 100, 150] | ['substitution_1pct', 'N_3pct', 'trim_5bp', 'substitution_1pct_N_3pct', 'local_mismatch_6bp', 'short_indel'] |         500 |            400 |          5 | 20260625 |

## Stability summary

| representation   | representation_label   |   n_cells |   n_features |   paired_cosine_mean |   l2_delta_mean |   retrieval_top1_mean |
|:-----------------|:-----------------------|----------:|-------------:|---------------------:|----------------:|----------------------:|
| ck4_p_msp        | CK4P-MSP               |        24 |     222.0000 |               0.9894 |          0.1286 |                0.9999 |
| ck4_msp          | CK4+MSP                |        24 |     211.0000 |               0.9844 |          0.1557 |                0.9999 |
| ck4_p            | CK4+P                  |        24 |     147.0000 |               0.9844 |          0.1560 |                0.9999 |
| ck4              | CK4                    |        24 |     136.0000 |               0.9694 |          0.2182 |                0.9998 |

## Stability by length

|   length | representation   | representation_label   |   n_cells |   paired_cosine_mean |   l2_delta_mean |   retrieval_top1_mean |
|---------:|:-----------------|:-----------------------|----------:|---------------------:|----------------:|----------------------:|
|       69 | ck4_p_msp        | CK4P-MSP               |         6 |               0.9862 |          0.1459 |                1.0000 |
|       69 | ck4_p            | CK4+P                  |         6 |               0.9797 |          0.1769 |                1.0000 |
|       69 | ck4_msp          | CK4+MSP                |         6 |               0.9797 |          0.1770 |                1.0000 |
|       69 | ck4              | CK4                    |         6 |               0.9600 |          0.2477 |                0.9997 |
|       75 | ck4_p_msp        | CK4P-MSP               |         6 |               0.9877 |          0.1379 |                1.0000 |
|       75 | ck4_p            | CK4+P                  |         6 |               0.9819 |          0.1673 |                1.0000 |
|       75 | ck4_msp          | CK4+MSP                |         6 |               0.9819 |          0.1674 |                1.0000 |
|       75 | ck4              | CK4                    |         6 |               0.9643 |          0.2343 |                1.0000 |
|      100 | ck4_p_msp        | CK4P-MSP               |         6 |               0.9903 |          0.1254 |                0.9997 |
|      100 | ck4_msp          | CK4+MSP                |         6 |               0.9858 |          0.1517 |                0.9997 |
|      100 | ck4_p            | CK4+P                  |         6 |               0.9857 |          0.1523 |                0.9997 |
|      100 | ck4              | CK4                    |         6 |               0.9720 |          0.2126 |                0.9997 |
|      150 | ck4_p_msp        | CK4P-MSP               |         6 |               0.9934 |          0.1050 |                1.0000 |
|      150 | ck4_msp          | CK4+MSP                |         6 |               0.9904 |          0.1268 |                1.0000 |
|      150 | ck4_p            | CK4+P                  |         6 |               0.9902 |          0.1276 |                1.0000 |
|      150 | ck4              | CK4                    |         6 |               0.9810 |          0.1780 |                1.0000 |

## Local mutation distance summary

| representation   | representation_label   |   n_cells |   n_features |   noise_l2_mean |   local_l2_mean |   local_minus_noise_l2_mean |   selective_sensitivity_ratio_mean |
|:-----------------|:-----------------------|----------:|-------------:|----------------:|----------------:|----------------------------:|-----------------------------------:|
| ck4_p_msp        | CK4P-MSP               |      3000 |     222.0000 |          0.2053 |          0.1540 |                     -0.0513 |                             0.7523 |
| ck4_msp          | CK4+MSP                |      3000 |     211.0000 |          0.2514 |          0.1885 |                     -0.0629 |                             0.7521 |
| ck4_p            | CK4+P                  |      3000 |     147.0000 |          0.2511 |          0.1879 |                     -0.0632 |                             0.7506 |
| ck4              | CK4                    |      3000 |     136.0000 |          0.3551 |          0.2656 |                     -0.0895 |                             0.7504 |

## Delta-readout summary

| representation   | representation_label   | classifier   |   n_cells |   n_features |   macro_f1_mean |   macro_f1_std_mean |   accuracy_mean |
|:-----------------|:-----------------------|:-------------|----------:|-------------:|----------------:|--------------------:|----------------:|
| ck4_p_msp        | CK4P-MSP               | logistic     |        12 |     222.0000 |          0.9786 |              0.0090 |          0.9787 |
| ck4_msp          | CK4+MSP                | logistic     |        12 |     211.0000 |          0.9780 |              0.0102 |          0.9780 |
| ck4_p            | CK4+P                  | logistic     |        12 |     147.0000 |          0.9043 |              0.0230 |          0.9045 |
| ck4              | CK4                    | logistic     |        12 |     136.0000 |          0.8923 |              0.0264 |          0.8925 |

## Delta-readout by length

|   length | representation   | representation_label   |   n_cells |   macro_f1_mean |   macro_f1_std_mean |   accuracy_mean |
|---------:|:-----------------|:-----------------------|----------:|----------------:|--------------------:|----------------:|
|       69 | ck4_msp          | CK4+MSP                |         4 |          0.9599 |              0.0158 |          0.9600 |
|       69 | ck4_p_msp        | CK4P-MSP               |         4 |          0.9594 |              0.0143 |          0.9595 |
|       69 | ck4_p            | CK4+P                  |         4 |          0.7845 |              0.0375 |          0.7850 |
|       69 | ck4              | CK4                    |         4 |          0.7605 |              0.0426 |          0.7610 |
|      100 | ck4_p_msp        | CK4P-MSP               |         4 |          0.9820 |              0.0063 |          0.9820 |
|      100 | ck4_msp          | CK4+MSP                |         4 |          0.9810 |              0.0074 |          0.9810 |
|      100 | ck4_p            | CK4+P                  |         4 |          0.9479 |              0.0187 |          0.9480 |
|      100 | ck4              | CK4                    |         4 |          0.9379 |              0.0213 |          0.9380 |
|      150 | ck4_p_msp        | CK4P-MSP               |         4 |          0.9945 |              0.0064 |          0.9945 |
|      150 | ck4_msp          | CK4+MSP                |         4 |          0.9930 |              0.0074 |          0.9930 |
|      150 | ck4_p            | CK4+P                  |         4 |          0.9805 |              0.0129 |          0.9805 |
|      150 | ck4              | CK4                    |         4 |          0.9785 |              0.0152 |          0.9785 |
