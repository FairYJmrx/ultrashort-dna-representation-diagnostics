# CAMI_TOY multi-target frozen-head audit

The primary analysis uses the declared contract space and C=1. Six targets were prespecified by source-read abundance and capped at 1,200 target groups each. Target-level intervals resample six target tasks and therefore describe task-to-task consistency rather than population-level biological generalization.

## Primary cross-target summary

| representation   | representation_label   |   n_features |   mean_baseline_macro_f1 |   mean_shifted_macro_f1 |   min_target_shifted_macro_f1 |   mean_retention |   min_target_retention |
|:-----------------|:-----------------------|-------------:|-------------------------:|------------------------:|------------------------------:|-----------------:|-----------------------:|
| ck5              | CK5                    |          512 |                   0.8167 |                  0.7948 |                        0.6979 |           0.9723 |                 0.9529 |
| ck4_p            | CK4+P                  |          147 |                   0.8177 |                  0.7945 |                        0.6982 |           0.9703 |                 0.9357 |
| ck4              | CK4                    |          136 |                   0.8229 |                  0.7935 |                        0.6930 |           0.9627 |                 0.9251 |
| ck4p_msp         | CK4P-MSP               |          222 |                   0.8159 |                  0.7934 |                        0.6992 |           0.9714 |                 0.9399 |
| ck4_msp          | CK4+MSP                |          211 |                   0.8179 |                  0.7933 |                        0.6975 |           0.9686 |                 0.9332 |
| pseknc_k3_l3     | PseKNC                 |           67 |                   0.8033 |                  0.7833 |                        0.6841 |           0.9739 |                 0.9559 |
| pseeiip          | PseEIIP                |           64 |                   0.8080 |                  0.7814 |                        0.6780 |           0.9655 |                 0.9311 |

## CK4P-MSP paired cross-target contrasts

| comparator   |   n_targets |   mean_absolute_f1_difference |   absolute_target_bootstrap_ci_low |   absolute_target_bootstrap_ci_high |   absolute_target_wilcoxon_p |   n_targets_absolute_favour_ck4p_msp |   mean_relative_drop_difference |   relative_target_bootstrap_ci_low |   relative_target_bootstrap_ci_high |   relative_target_wilcoxon_p |   n_targets_relative_favour_ck4p_msp |   absolute_target_wilcoxon_q |   relative_target_wilcoxon_q |
|:-------------|------------:|------------------------------:|-----------------------------------:|------------------------------------:|-----------------------------:|-------------------------------------:|--------------------------------:|-----------------------------------:|------------------------------------:|-----------------------------:|-------------------------------------:|-----------------------------:|-----------------------------:|
| ck4          |           6 |                       -0.0001 |                            -0.0044 |                              0.0044 |                       1.0000 |                                    3 |                          0.0069 |                             0.0010 |                              0.0128 |                       0.1562 |                                    4 |                       1.0000 |                       0.5250 |
| ck4_msp      |           6 |                        0.0001 |                            -0.0018 |                              0.0022 |                       0.8438 |                                    3 |                          0.0021 |                            -0.0006 |                              0.0048 |                       0.3125 |                                    4 |                       1.0000 |                       0.5357 |
| ck4_p        |           6 |                       -0.0010 |                            -0.0021 |                              0.0002 |                       0.2188 |                                    2 |                          0.0008 |                            -0.0018 |                              0.0029 |                       0.5625 |                                    4 |                       0.5250 |                       0.7500 |
| ck5          |           6 |                       -0.0013 |                            -0.0038 |                              0.0003 |                       0.3125 |                                    2 |                         -0.0005 |                            -0.0059 |                              0.0050 |                       1.0000 |                                    3 |                       0.5357 |                       1.0000 |
| pseeiip      |           6 |                        0.0120 |                             0.0054 |                              0.0180 |                       0.0312 |                                    6 |                          0.0042 |                             0.0009 |                              0.0084 |                       0.2188 |                                    4 |                       0.1875 |                       0.5250 |
| pseknc_k3_l3 |           6 |                        0.0102 |                             0.0054 |                              0.0147 |                       0.0312 |                                    6 |                         -0.0024 |                            -0.0073 |                              0.0026 |                       0.4375 |                                    2 |                       0.1875 |                       0.6562 |

## Contract-space regularization sensitivity

| representation   | representation_label   |   c_value |   mean_shifted_macro_f1 |   mean_retention |   min_macro_f1 |
|:-----------------|:-----------------------|----------:|------------------------:|-----------------:|---------------:|
| ck4              | CK4                    |    0.1000 |                  0.7845 |           0.9778 |         0.6719 |
| ck4              | CK4                    |    1.0000 |                  0.7935 |           0.9627 |         0.6513 |
| ck4              | CK4                    |   10.0000 |                  0.7770 |           0.9374 |         0.5945 |
| ck4_msp          | CK4+MSP                |    0.1000 |                  0.7771 |           0.9797 |         0.6615 |
| ck4_msp          | CK4+MSP                |    1.0000 |                  0.7933 |           0.9686 |         0.6675 |
| ck4_msp          | CK4+MSP                |   10.0000 |                  0.7824 |           0.9437 |         0.6098 |
| ck4_p            | CK4+P                  |    0.1000 |                  0.7777 |           0.9802 |         0.6638 |
| ck4_p            | CK4+P                  |    1.0000 |                  0.7945 |           0.9703 |         0.6704 |
| ck4_p            | CK4+P                  |   10.0000 |                  0.7887 |           0.9515 |         0.6297 |
| ck4p_msp         | CK4P-MSP               |    0.1000 |                  0.7732 |           0.9811 |         0.6582 |
| ck4p_msp         | CK4P-MSP               |    1.0000 |                  0.7934 |           0.9714 |         0.6695 |
| ck4p_msp         | CK4P-MSP               |   10.0000 |                  0.7903 |           0.9538 |         0.6401 |
| ck5              | CK5                    |    0.1000 |                  0.7856 |           0.9791 |         0.6720 |
| ck5              | CK5                    |    1.0000 |                  0.7948 |           0.9723 |         0.6771 |
| ck5              | CK5                    |   10.0000 |                  0.7750 |           0.9527 |         0.6396 |
| pseeiip          | PseEIIP                |    0.1000 |                  0.7683 |           0.9780 |         0.6474 |
| pseeiip          | PseEIIP                |    1.0000 |                  0.7814 |           0.9655 |         0.6386 |
| pseeiip          | PseEIIP                |   10.0000 |                  0.7769 |           0.9522 |         0.6215 |
| pseknc_k3_l3     | PseKNC                 |    0.1000 |                  0.7625 |           0.9791 |         0.6414 |
| pseknc_k3_l3     | PseKNC                 |    1.0000 |                  0.7833 |           0.9739 |         0.6681 |
| pseknc_k3_l3     | PseKNC                 |   10.0000 |                  0.7852 |           0.9622 |         0.6557 |