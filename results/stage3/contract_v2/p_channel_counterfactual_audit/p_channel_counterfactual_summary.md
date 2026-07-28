# P-channel counterfactual and reliability audit

Purpose: test whether the P/MSP contribution remains sequence-linked after controlling for dimensionality and marginal scale. Permuted and Gaussian P/MSP blocks preserve extra dimensions but remove the biological sequence-to-feature mapping.

This is empirical support for the diagnostic representation, not a proof that heterogeneous Euclidean distance is a universal biophysical metric.

## Run metadata

|   elapsed_seconds |   reads_rows |   triplet_rows | lengths       | conditions                                                                       |   max_pairs |   max_triplets |     seed |
|------------------:|-------------:|---------------:|:--------------|:---------------------------------------------------------------------------------|------------:|---------------:|---------:|
|            90.433 |        25200 |           9000 | 69,75,100,150 | substitution_1pct,N_3pct,substitution_1pct_N_3pct,local_mismatch_6bp,short_indel |         250 |            250 | 20260625 |

## Stability counterfactual

| representation    | representation_label   |   n_cells |   n_pairs_mean |   paired_cosine_mean |   l2_delta_mean |   retrieval_top1_mean |   mean_pair_margin |
|:------------------|:-----------------------|----------:|---------------:|---------------------:|----------------:|----------------------:|-------------------:|
| ck4p_msp          | CK4P-MSP               |        20 |       250.0000 |               0.9883 |          0.1350 |                1.0000 |             0.1047 |
| ck4_permuted_pmsp | CK4 + permuted P/MSP   |        20 |       250.0000 |               0.9856 |          0.1604 |                1.0000 |             0.1027 |
| ck4               | CK4                    |        20 |       250.0000 |               0.9661 |          0.2293 |                1.0000 |             0.3086 |
| ck4_gaussian_pmsp | CK4 + Gaussian P/MSP   |        20 |       250.0000 |               0.7261 |          0.6294 |                0.5242 |            -0.0250 |

## Block-wise drift

| block                   |   n_cells |   paired_cosine_mean |   l2_delta_mean |   l2_delta_p95_mean |
|:------------------------|----------:|---------------------:|----------------:|--------------------:|
| multiscale_property_MSP |        20 |               0.9996 |          0.0245 |              0.0412 |
| global_property_P       |        20 |               0.9992 |          0.0276 |              0.0340 |
| identity_CK4            |        20 |               0.9661 |          0.2293 |              0.3524 |

## Local mutation distance

| representation    | representation_label   |   n_cells |   noise_l2_mean |   local_l2_mean |   local_minus_noise_l2_mean |   selective_sensitivity_ratio_mean |
|:------------------|:-----------------------|----------:|----------------:|----------------:|----------------------------:|-----------------------------------:|
| ck4_gaussian_pmsp | CK4 + Gaussian P/MSP   |      3000 |          0.9403 |          0.9336 |                     -0.0067 |                             1.0204 |
| ck4_permuted_pmsp | CK4 + permuted P/MSP   |      3000 |          0.2129 |          0.1639 |                     -0.0491 |                             0.7709 |
| ck4p_msp          | CK4P-MSP               |      3000 |          0.2053 |          0.1540 |                     -0.0513 |                             0.7523 |
| ck4               | CK4                    |      3000 |          0.3551 |          0.2656 |                     -0.0895 |                             0.7504 |

## Delta-readout

| representation    | representation_label   | classifier   |   n_cells |   macro_f1_mean |   macro_f1_std_mean |   accuracy_mean |
|:------------------|:-----------------------|:-------------|----------:|----------------:|--------------------:|----------------:|
| ck4p_msp          | CK4P-MSP               | logistic     |        12 |          0.9786 |              0.0090 |          0.9787 |
| ck4               | CK4                    | logistic     |        12 |          0.8923 |              0.0264 |          0.8925 |
| ck4_gaussian_pmsp | CK4 + Gaussian P/MSP   | logistic     |        12 |          0.8861 |              0.0195 |          0.8865 |
| ck4_permuted_pmsp | CK4 + permuted P/MSP   | logistic     |        12 |          0.8791 |              0.0237 |          0.8793 |

## Mutual information

| representation    | representation_label   |   n_cells |   mi_bits_mean |   mi_perm_p_median |   mi_perm_mean |
|:------------------|:-----------------------|----------:|---------------:|-------------------:|---------------:|
| ck4p_msp          | CK4P-MSP               |        12 |         0.7275 |             0.0050 |         0.0103 |
| ck4               | CK4                    |        12 |         0.7272 |             0.0050 |         0.0103 |
| ck4_permuted_pmsp | CK4 + permuted P/MSP   |        12 |         0.7169 |             0.0050 |         0.0100 |
| ck4_gaussian_pmsp | CK4 + Gaussian P/MSP   |        12 |         0.0116 |             0.5622 |         0.0102 |

## Conditional block information

|   ck4_distance_mi_bits |   p_distance_mi_bits |   msp_distance_mi_bits |   pmsp_joint_mi_bits |   joint_ck4_pmsp_mi_bits |   pmsp_conditional_on_ck4_mi_bits |   joint_minus_ck4_mi_bits |   pmsp_conditional_perm_p |   joint_minus_ck4_perm_p |   n_triplets |
|-----------------------:|---------------------:|-----------------------:|---------------------:|-------------------------:|----------------------------------:|--------------------------:|--------------------------:|-------------------------:|-------------:|
|                 0.7275 |               0.2562 |                 0.3242 |               0.5694 |                   0.8716 |                            0.2225 |                    0.1441 |                    0.0050 |                   0.0050 |     250.0000 |

## Pooled-feature reliability

|   length | block                   |   n_reads |   n_features |   mean_feature_sd |   median_feature_sd |   mean_bootstrap_ci_width |   median_bootstrap_ci_width |   min_bin_bp |   median_bin_bp |   worst_case_binomial_se |
|---------:|:------------------------|----------:|-------------:|------------------:|--------------------:|--------------------------:|----------------------------:|-------------:|----------------:|-------------------------:|
|       69 | global_property_P       |       600 |           11 |            0.0109 |              0.0083 |                    0.0017 |                      0.0013 |     nan      |        nan      |                 nan      |
|       69 | multiscale_property_MSP |       600 |           75 |            0.0077 |              0.0097 |                    0.0012 |                      0.0016 |     nan      |        nan      |                 nan      |
|       69 | MSP_bin_scale_2         |       600 |           10 |          nan      |            nan      |                  nan      |                    nan      |      34.0000 |         34.5000 |                   0.0857 |
|       69 | MSP_bin_scale_3         |       600 |           15 |          nan      |            nan      |                  nan      |                    nan      |      23.0000 |         23.0000 |                   0.1043 |
|       69 | MSP_bin_scale_4         |       600 |           20 |          nan      |            nan      |                  nan      |                    nan      |      17.0000 |         17.0000 |                   0.1213 |
|       69 | MSP_bin_scale_6         |       600 |           30 |          nan      |            nan      |                  nan      |                    nan      |      11.0000 |         11.5000 |                   0.1508 |
|       75 | global_property_P       |       600 |           11 |            0.0111 |              0.0087 |                    0.0016 |                      0.0013 |     nan      |        nan      |                 nan      |
|       75 | multiscale_property_MSP |       600 |           75 |            0.0076 |              0.0098 |                    0.0012 |                      0.0015 |     nan      |        nan      |                 nan      |
|       75 | MSP_bin_scale_2         |       600 |           10 |          nan      |            nan      |                  nan      |                    nan      |      37.0000 |         37.5000 |                   0.0822 |
|       75 | MSP_bin_scale_3         |       600 |           15 |          nan      |            nan      |                  nan      |                    nan      |      25.0000 |         25.0000 |                   0.1000 |
|       75 | MSP_bin_scale_4         |       600 |           20 |          nan      |            nan      |                  nan      |                    nan      |      18.0000 |         19.0000 |                   0.1179 |
|       75 | MSP_bin_scale_6         |       600 |           30 |          nan      |            nan      |                  nan      |                    nan      |      12.0000 |         12.5000 |                   0.1443 |
|      100 | global_property_P       |       600 |           11 |            0.0108 |              0.0084 |                    0.0017 |                      0.0013 |     nan      |        nan      |                 nan      |
|      100 | multiscale_property_MSP |       600 |           75 |            0.0068 |              0.0082 |                    0.0011 |                      0.0013 |     nan      |        nan      |                 nan      |
|      100 | MSP_bin_scale_2         |       600 |           10 |          nan      |            nan      |                  nan      |                    nan      |      50.0000 |         50.0000 |                   0.0707 |
|      100 | MSP_bin_scale_3         |       600 |           15 |          nan      |            nan      |                  nan      |                    nan      |      33.0000 |         33.0000 |                   0.0870 |
|      100 | MSP_bin_scale_4         |       600 |           20 |          nan      |            nan      |                  nan      |                    nan      |      25.0000 |         25.0000 |                   0.1000 |
|      100 | MSP_bin_scale_6         |       600 |           30 |          nan      |            nan      |                  nan      |                    nan      |      16.0000 |         17.0000 |                   0.1250 |
|      150 | global_property_P       |       600 |           11 |            0.0102 |              0.0080 |                    0.0015 |                      0.0012 |     nan      |        nan      |                 nan      |
|      150 | multiscale_property_MSP |       600 |           75 |            0.0060 |              0.0071 |                    0.0009 |                      0.0011 |     nan      |        nan      |                 nan      |
|      150 | MSP_bin_scale_2         |       600 |           10 |          nan      |            nan      |                  nan      |                    nan      |      75.0000 |         75.0000 |                   0.0577 |
|      150 | MSP_bin_scale_3         |       600 |           15 |          nan      |            nan      |                  nan      |                    nan      |      50.0000 |         50.0000 |                   0.0707 |
|      150 | MSP_bin_scale_4         |       600 |           20 |          nan      |            nan      |                  nan      |                    nan      |      37.0000 |         37.5000 |                   0.0822 |
|      150 | MSP_bin_scale_6         |       600 |           30 |          nan      |            nan      |                  nan      |                    nan      |      25.0000 |         25.0000 |                   0.1000 |
