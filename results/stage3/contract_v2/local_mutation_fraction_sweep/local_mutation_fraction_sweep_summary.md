# Local mutation fraction sweep

This reviewer-response sweep keeps the existing local-mode coverage (center, left, right, jittered) and varies mutation fraction. It is a focused supplement to the full local mutation sensitivity run, not a replacement for the complete representation matrix.

## Distance summary

|   mutation_fraction | representation   |   n_cells |   noise_l2 |   local_l2 |   local_minus_noise_l2 |   n_features |   selective_sensitivity_ratio |   selective_sensitivity_ratio_denominator_tolerance |
|--------------------:|:-----------------|----------:|-----------:|-----------:|-----------------------:|-------------:|------------------------------:|----------------------------------------------------:|
|               0.010 | ck4              |        12 |      0.238 |      0.228 |                 -0.010 |      136.000 |                         0.959 |                                               0.000 |
|               0.010 | ck4_msp          |        12 |      0.168 |      0.162 |                 -0.007 |      211.000 |                         0.959 |                                               0.000 |
|               0.010 | ck4_p            |        12 |      0.168 |      0.161 |                 -0.007 |      147.000 |                         0.959 |                                               0.000 |
|               0.010 | ck4p_msp         |        12 |      0.138 |      0.132 |                 -0.006 |      222.000 |                         0.960 |                                               0.000 |
|               0.030 | ck4              |        12 |      0.355 |      0.266 |                 -0.089 |      136.000 |                         0.750 |                                               0.000 |
|               0.030 | ck4_msp          |        12 |      0.251 |      0.189 |                 -0.062 |      211.000 |                         0.752 |                                               0.000 |
|               0.030 | ck4_p            |        12 |      0.251 |      0.188 |                 -0.063 |      147.000 |                         0.751 |                                               0.000 |
|               0.030 | ck4p_msp         |        12 |      0.205 |      0.154 |                 -0.051 |      222.000 |                         0.752 |                                               0.000 |
|               0.050 | ck4              |        12 |      0.455 |      0.305 |                 -0.150 |      136.000 |                         0.671 |                                               0.000 |
|               0.050 | ck4_msp          |        12 |      0.322 |      0.217 |                 -0.105 |      211.000 |                         0.673 |                                               0.000 |
|               0.050 | ck4_p            |        12 |      0.322 |      0.216 |                 -0.106 |      147.000 |                         0.671 |                                               0.000 |
|               0.050 | ck4p_msp         |        12 |      0.263 |      0.177 |                 -0.086 |      222.000 |                         0.673 |                                               0.000 |

## Delta-readout summary

|   mutation_fraction | representation   | classifier       |   n_cells |   macro_f1 |   accuracy |   n_features |
|--------------------:|:-----------------|:-----------------|----------:|-----------:|-----------:|-------------:|
|               0.010 | ck4p_msp         | logistic         |        12 |      0.948 |      0.948 |      222.000 |
|               0.010 | ck4_msp          | logistic         |        12 |      0.943 |      0.944 |      211.000 |
|               0.010 | ck4_p            | logistic         |        12 |      0.730 |      0.731 |      147.000 |
|               0.010 | ck4p_msp         | nearest_centroid |        12 |      0.624 |      0.626 |      222.000 |
|               0.010 | ck4_msp          | nearest_centroid |        12 |      0.624 |      0.626 |      211.000 |
|               0.010 | ck4              | logistic         |        12 |      0.608 |      0.610 |      136.000 |
|               0.010 | ck4_p            | nearest_centroid |        12 |      0.597 |      0.599 |      147.000 |
|               0.010 | ck4              | nearest_centroid |        12 |      0.596 |      0.598 |      136.000 |
|               0.030 | ck4p_msp         | logistic         |        12 |      0.973 |      0.973 |      222.000 |
|               0.030 | ck4_msp          | logistic         |        12 |      0.972 |      0.972 |      211.000 |
|               0.030 | ck4_p            | logistic         |        12 |      0.884 |      0.884 |      147.000 |
|               0.030 | ck4              | logistic         |        12 |      0.879 |      0.880 |      136.000 |
|               0.030 | ck4_msp          | nearest_centroid |        12 |      0.871 |      0.872 |      211.000 |
|               0.030 | ck4p_msp         | nearest_centroid |        12 |      0.871 |      0.872 |      222.000 |
|               0.030 | ck4_p            | nearest_centroid |        12 |      0.861 |      0.862 |      147.000 |
|               0.030 | ck4              | nearest_centroid |        12 |      0.861 |      0.862 |      136.000 |
|               0.050 | ck4p_msp         | logistic         |        12 |      0.991 |      0.991 |      222.000 |
|               0.050 | ck4_msp          | logistic         |        12 |      0.989 |      0.989 |      211.000 |
|               0.050 | ck4              | logistic         |        12 |      0.961 |      0.961 |      136.000 |
|               0.050 | ck4_p            | logistic         |        12 |      0.959 |      0.959 |      147.000 |
|               0.050 | ck4_msp          | nearest_centroid |        12 |      0.956 |      0.956 |      211.000 |
|               0.050 | ck4p_msp         | nearest_centroid |        12 |      0.955 |      0.956 |      222.000 |
|               0.050 | ck4_p            | nearest_centroid |        12 |      0.952 |      0.952 |      147.000 |
|               0.050 | ck4              | nearest_centroid |        12 |      0.951 |      0.952 |      136.000 |
