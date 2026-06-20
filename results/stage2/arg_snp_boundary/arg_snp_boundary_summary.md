# Stage-2 ARG/SNP Boundary Task

This synthetic boundary task tests whether CSP can act alone in ARG-family, ARG-allele and resistance-SNP style probes.

## Best perturbation stability

| task           | condition                |   length | representation      |   paired_cosine_mean |   l2_delta_mean |   retrieval_top1 |   n_features |
|:---------------|:-------------------------|---------:|:--------------------|---------------------:|----------------:|-----------------:|-------------:|
| arg_allele     | N_3pct                   |       69 | cspaced_property_l2 |                0.994 |           0.105 |            0.125 |           78 |
| arg_allele     | N_3pct                   |       75 | cspaced_property_l2 |                0.995 |           0.100 |            0.114 |           81 |
| arg_allele     | N_3pct                   |      100 | cspaced_property_l2 |                0.994 |           0.107 |            0.125 |           94 |
| arg_allele     | N_3pct                   |      150 | cspaced_property_l2 |                0.996 |           0.094 |            0.106 |          110 |
| arg_allele     | local_mismatch_6bp       |       69 | cspaced_property_l2 |                0.990 |           0.139 |            0.119 |           78 |
| arg_allele     | local_mismatch_6bp       |       75 | cspaced_property_l2 |                0.991 |           0.131 |            0.119 |           81 |
| arg_allele     | local_mismatch_6bp       |      100 | cspaced_property_l2 |                0.994 |           0.112 |            0.108 |           94 |
| arg_allele     | local_mismatch_6bp       |      150 | cspaced_property_l2 |                0.996 |           0.089 |            0.108 |          110 |
| arg_allele     | substitution_1pct        |       69 | cspaced_property_l2 |                0.998 |           0.042 |            0.139 |           78 |
| arg_allele     | substitution_1pct        |       75 | cspaced_property_l2 |                0.998 |           0.044 |            0.133 |           81 |
| arg_allele     | substitution_1pct        |      100 | cspaced_property_l2 |                0.998 |           0.050 |            0.125 |           94 |
| arg_allele     | substitution_1pct        |      150 | cspaced_property_l2 |                0.998 |           0.055 |            0.122 |          110 |
| arg_allele     | substitution_1pct_N_3pct |       69 | cspaced_property_l2 |                0.992 |           0.121 |            0.117 |           78 |
| arg_allele     | substitution_1pct_N_3pct |       75 | cspaced_property_l2 |                0.993 |           0.114 |            0.117 |           81 |
| arg_allele     | substitution_1pct_N_3pct |      100 | cspaced_property_l2 |                0.992 |           0.121 |            0.114 |           94 |
| arg_allele     | substitution_1pct_N_3pct |      150 | cspaced_property_l2 |                0.994 |           0.110 |            0.117 |          110 |
| arg_allele     | trim_5bp                 |       69 | cspaced_property_l2 |                0.997 |           0.073 |            0.094 |           78 |
| arg_allele     | trim_5bp                 |       75 | cspaced_property_l2 |                0.998 |           0.069 |            0.083 |           81 |
| arg_allele     | trim_5bp                 |      100 | cspaced_property_l2 |                0.998 |           0.059 |            0.031 |           94 |
| arg_allele     | trim_5bp                 |      150 | cspaced_property_l2 |                0.999 |           0.044 |            0.031 |          110 |
| arg_family     | N_3pct                   |       69 | cspaced_property_l2 |                0.994 |           0.105 |            0.108 |          101 |
| arg_family     | N_3pct                   |       75 | cspaced_property_l2 |                0.995 |           0.099 |            0.122 |          107 |
| arg_family     | N_3pct                   |      100 | cspaced_property_l2 |                0.995 |           0.100 |            0.117 |          122 |
| arg_family     | N_3pct                   |      150 | cspaced_property_l2 |                0.996 |           0.086 |            0.128 |          137 |
| arg_family     | local_mismatch_6bp       |       69 | cspaced_property_l2 |                0.989 |           0.145 |            0.094 |          101 |
| arg_family     | local_mismatch_6bp       |       75 | cspaced_property_l2 |                0.990 |           0.137 |            0.106 |          107 |
| arg_family     | local_mismatch_6bp       |      100 | cspaced_property_l2 |                0.994 |           0.110 |            0.094 |          122 |
| arg_family     | local_mismatch_6bp       |      150 | cspaced_property_l2 |                0.997 |           0.083 |            0.108 |          137 |
| arg_family     | substitution_1pct        |       69 | cspaced_property_l2 |                0.998 |           0.048 |            0.131 |          101 |
| arg_family     | substitution_1pct        |       75 | cspaced_property_l2 |                0.998 |           0.047 |            0.142 |          107 |
| arg_family     | substitution_1pct        |      100 | cspaced_property_l2 |                0.998 |           0.049 |            0.125 |          122 |
| arg_family     | substitution_1pct        |      150 | cspaced_property_l2 |                0.998 |           0.049 |            0.128 |          137 |
| arg_family     | substitution_1pct_N_3pct |       69 | cspaced_property_l2 |                0.992 |           0.122 |            0.125 |          101 |
| arg_family     | substitution_1pct_N_3pct |       75 | cspaced_property_l2 |                0.993 |           0.117 |            0.106 |          107 |
| arg_family     | substitution_1pct_N_3pct |      100 | cspaced_property_l2 |                0.993 |           0.119 |            0.108 |          122 |
| arg_family     | substitution_1pct_N_3pct |      150 | cspaced_property_l2 |                0.995 |           0.103 |            0.108 |          137 |
| arg_family     | trim_5bp                 |       69 | cspaced_property_l2 |                0.997 |           0.074 |            0.031 |          101 |
| arg_family     | trim_5bp                 |       75 | cspaced_property_l2 |                0.998 |           0.070 |            0.028 |          107 |
| arg_family     | trim_5bp                 |      100 | cspaced_property_l2 |                0.999 |           0.054 |            0.056 |          122 |
| arg_family     | trim_5bp                 |      150 | cspaced_property_l2 |                0.999 |           0.040 |            0.033 |          137 |
| resistance_snp | N_3pct                   |       69 | cspaced_property_l2 |                0.995 |           0.099 |            0.042 |           56 |
| resistance_snp | N_3pct                   |       75 | cspaced_property_l2 |                0.996 |           0.092 |            0.028 |           57 |
| resistance_snp | local_mismatch_6bp       |       69 | cspaced_property_l2 |                0.993 |           0.121 |            0.025 |           56 |
| resistance_snp | local_mismatch_6bp       |       75 | cspaced_property_l2 |                0.994 |           0.111 |            0.031 |           57 |
| resistance_snp | substitution_1pct        |       69 | cspaced_property_l2 |                0.999 |           0.037 |            0.039 |           56 |
| resistance_snp | substitution_1pct        |       75 | cspaced_property_l2 |                0.999 |           0.035 |            0.036 |           57 |
| resistance_snp | substitution_1pct_N_3pct |       69 | cspaced_property_l2 |                0.994 |           0.112 |            0.033 |           56 |
| resistance_snp | substitution_1pct_N_3pct |       75 | cspaced_property_l2 |                0.994 |           0.104 |            0.033 |           57 |
| resistance_snp | trim_5bp                 |       69 | cspaced_property_l2 |                0.998 |           0.065 |            0.019 |           56 |
| resistance_snp | trim_5bp                 |       75 | cspaced_property_l2 |                0.998 |           0.059 |            0.008 |           57 |

## Best readout performance

| task           | condition                |   length | representation   | classifier       |   macro_f1 |   accuracy |
|:---------------|:-------------------------|---------:|:-----------------|:-----------------|-----------:|-----------:|
| arg_allele     | N_3pct                   |       69 | ckmer5_count_l2  | nearest_centroid |      1.000 |      1.000 |
| arg_allele     | N_3pct                   |       75 | ckmer5_count_l2  | nearest_centroid |      1.000 |      1.000 |
| arg_allele     | N_3pct                   |      100 | ckmer5_count_l2  | nearest_centroid |      1.000 |      1.000 |
| arg_allele     | N_3pct                   |      150 | ckmer5_count_l2  | nearest_centroid |      1.000 |      1.000 |
| arg_allele     | clean                    |       69 | ckmer5_count_l2  | nearest_centroid |      1.000 |      1.000 |
| arg_allele     | clean                    |       75 | ckmer5_count_l2  | nearest_centroid |      1.000 |      1.000 |
| arg_allele     | clean                    |      100 | ckmer5_count_l2  | nearest_centroid |      1.000 |      1.000 |
| arg_allele     | clean                    |      150 | ckmer5_count_l2  | nearest_centroid |      1.000 |      1.000 |
| arg_allele     | local_mismatch_6bp       |       69 | ckmer5_count_l2  | nearest_centroid |      1.000 |      1.000 |
| arg_allele     | local_mismatch_6bp       |       75 | ckmer5_count_l2  | nearest_centroid |      1.000 |      1.000 |
| arg_allele     | local_mismatch_6bp       |      100 | ckmer5_count_l2  | nearest_centroid |      1.000 |      1.000 |
| arg_allele     | local_mismatch_6bp       |      150 | ckmer5_count_l2  | nearest_centroid |      1.000 |      1.000 |
| arg_allele     | substitution_1pct        |       69 | ckmer5_count_l2  | nearest_centroid |      1.000 |      1.000 |
| arg_allele     | substitution_1pct        |       75 | ckmer5_count_l2  | nearest_centroid |      1.000 |      1.000 |
| arg_allele     | substitution_1pct        |      100 | ckmer5_count_l2  | nearest_centroid |      1.000 |      1.000 |
| arg_allele     | substitution_1pct        |      150 | ckmer5_count_l2  | nearest_centroid |      0.991 |      0.991 |
| arg_allele     | substitution_1pct_N_3pct |       69 | ckmer5_count_l2  | nearest_centroid |      1.000 |      1.000 |
| arg_allele     | substitution_1pct_N_3pct |       75 | ckmer5_count_l2  | nearest_centroid |      1.000 |      1.000 |
| arg_allele     | substitution_1pct_N_3pct |      100 | ckmer5_count_l2  | nearest_centroid |      1.000 |      1.000 |
| arg_allele     | substitution_1pct_N_3pct |      150 | ckmer5_count_l2  | nearest_centroid |      1.000 |      1.000 |
| arg_allele     | trim_5bp                 |       69 | ckmer5_count_l2  | nearest_centroid |      1.000 |      1.000 |
| arg_allele     | trim_5bp                 |       75 | ckmer5_count_l2  | nearest_centroid |      1.000 |      1.000 |
| arg_allele     | trim_5bp                 |      100 | ckmer5_count_l2  | nearest_centroid |      1.000 |      1.000 |
| arg_allele     | trim_5bp                 |      150 | ckmer5_count_l2  | nearest_centroid |      1.000 |      1.000 |
| arg_family     | N_3pct                   |       69 | ckmer5_count_l2  | nearest_centroid |      1.000 |      1.000 |
| arg_family     | N_3pct                   |       75 | ckmer5_count_l2  | nearest_centroid |      1.000 |      1.000 |
| arg_family     | N_3pct                   |      100 | ckmer5_count_l2  | nearest_centroid |      1.000 |      1.000 |
| arg_family     | N_3pct                   |      150 | ckmer5_count_l2  | nearest_centroid |      1.000 |      1.000 |
| arg_family     | clean                    |       69 | ckmer5_count_l2  | nearest_centroid |      1.000 |      1.000 |
| arg_family     | clean                    |       75 | ckmer5_count_l2  | nearest_centroid |      1.000 |      1.000 |
| arg_family     | clean                    |      100 | ckmer5_count_l2  | nearest_centroid |      1.000 |      1.000 |
| arg_family     | clean                    |      150 | ckmer5_count_l2  | nearest_centroid |      1.000 |      1.000 |
| arg_family     | local_mismatch_6bp       |       69 | ckmer5_count_l2  | nearest_centroid |      1.000 |      1.000 |
| arg_family     | local_mismatch_6bp       |       75 | ckmer5_count_l2  | nearest_centroid |      1.000 |      1.000 |
| arg_family     | local_mismatch_6bp       |      100 | ckmer5_count_l2  | nearest_centroid |      1.000 |      1.000 |
| arg_family     | local_mismatch_6bp       |      150 | ckmer5_count_l2  | nearest_centroid |      1.000 |      1.000 |
| arg_family     | substitution_1pct        |       69 | ckmer5_count_l2  | nearest_centroid |      1.000 |      1.000 |
| arg_family     | substitution_1pct        |       75 | ckmer5_count_l2  | nearest_centroid |      1.000 |      1.000 |
| arg_family     | substitution_1pct        |      100 | ckmer5_count_l2  | nearest_centroid |      1.000 |      1.000 |
| arg_family     | substitution_1pct        |      150 | ckmer5_count_l2  | nearest_centroid |      1.000 |      1.000 |
| arg_family     | substitution_1pct_N_3pct |       69 | ckmer5_count_l2  | nearest_centroid |      1.000 |      1.000 |
| arg_family     | substitution_1pct_N_3pct |       75 | ckmer5_count_l2  | nearest_centroid |      1.000 |      1.000 |
| arg_family     | substitution_1pct_N_3pct |      100 | ckmer5_count_l2  | nearest_centroid |      1.000 |      1.000 |
| arg_family     | substitution_1pct_N_3pct |      150 | ckmer5_count_l2  | nearest_centroid |      1.000 |      1.000 |
| arg_family     | trim_5bp                 |       69 | ckmer5_count_l2  | nearest_centroid |      1.000 |      1.000 |
| arg_family     | trim_5bp                 |       75 | ckmer5_count_l2  | nearest_centroid |      1.000 |      1.000 |
| arg_family     | trim_5bp                 |      100 | ckmer5_count_l2  | nearest_centroid |      1.000 |      1.000 |
| arg_family     | trim_5bp                 |      150 | ckmer5_count_l2  | nearest_centroid |      1.000 |      1.000 |
| resistance_snp | N_3pct                   |       69 | cspaced_count_l2 | nearest_centroid |      0.979 |      0.981 |
| resistance_snp | N_3pct                   |       75 | cspaced_count_l2 | logistic         |      0.990 |      0.991 |
| resistance_snp | clean                    |       69 | ckmer5_count_l2  | nearest_centroid |      1.000 |      1.000 |
| resistance_snp | clean                    |       75 | ckmer5_count_l2  | nearest_centroid |      1.000 |      1.000 |
| resistance_snp | local_mismatch_6bp       |       69 | ckmer5_count_l2  | nearest_centroid |      0.968 |      0.972 |
| resistance_snp | local_mismatch_6bp       |       75 | ckmer5_count_l2  | nearest_centroid |      0.948 |      0.954 |
| resistance_snp | substitution_1pct        |       69 | cspaced_count_l2 | nearest_centroid |      0.990 |      0.991 |
| resistance_snp | substitution_1pct        |       75 | ckmer5_count_l2  | logistic         |      1.000 |      1.000 |
| resistance_snp | substitution_1pct_N_3pct |       69 | ckmer5_count_l2  | nearest_centroid |      0.979 |      0.981 |
| resistance_snp | substitution_1pct_N_3pct |       75 | cspaced_count_l2 | nearest_centroid |      0.947 |      0.954 |
| resistance_snp | trim_5bp                 |       69 | ckmer5_count_l2  | nearest_centroid |      1.000 |      1.000 |
| resistance_snp | trim_5bp                 |       75 | ckmer5_count_l2  | nearest_centroid |      1.000 |      1.000 |

## Resistance-SNP task by representation

| condition                |   length | representation      |   mean_macro_f1 |
|:-------------------------|---------:|:--------------------|----------------:|
| N_3pct                   |       69 | ckmer5_count_l2     |           0.963 |
| N_3pct                   |       69 | ckmer7_count_l2     |           0.963 |
| N_3pct                   |       69 | cspaced_count_l2    |           0.973 |
| N_3pct                   |       69 | cspaced_property_l2 |           0.973 |
| N_3pct                   |       69 | hybrid_ckmer5_csp   |           0.968 |
| N_3pct                   |       69 | hybrid_ckmer7_csp   |           0.963 |
| N_3pct                   |       75 | ckmer5_count_l2     |           0.968 |
| N_3pct                   |       75 | ckmer7_count_l2     |           0.962 |
| N_3pct                   |       75 | cspaced_count_l2    |           0.984 |
| N_3pct                   |       75 | cspaced_property_l2 |           0.990 |
| N_3pct                   |       75 | hybrid_ckmer5_csp   |           0.979 |
| N_3pct                   |       75 | hybrid_ckmer7_csp   |           0.962 |
| clean                    |       69 | ckmer5_count_l2     |           1.000 |
| clean                    |       69 | ckmer7_count_l2     |           1.000 |
| clean                    |       69 | cspaced_count_l2    |           1.000 |
| clean                    |       69 | cspaced_property_l2 |           1.000 |
| clean                    |       69 | hybrid_ckmer5_csp   |           1.000 |
| clean                    |       69 | hybrid_ckmer7_csp   |           1.000 |
| clean                    |       75 | ckmer5_count_l2     |           1.000 |
| clean                    |       75 | ckmer7_count_l2     |           1.000 |
| clean                    |       75 | cspaced_count_l2    |           1.000 |
| clean                    |       75 | cspaced_property_l2 |           1.000 |
| clean                    |       75 | hybrid_ckmer5_csp   |           1.000 |
| clean                    |       75 | hybrid_ckmer7_csp   |           1.000 |
| local_mismatch_6bp       |       69 | ckmer5_count_l2     |           0.957 |
| local_mismatch_6bp       |       69 | ckmer7_count_l2     |           0.946 |
| local_mismatch_6bp       |       69 | cspaced_count_l2    |           0.947 |
| local_mismatch_6bp       |       69 | cspaced_property_l2 |           0.947 |
| local_mismatch_6bp       |       69 | hybrid_ckmer5_csp   |           0.963 |
| local_mismatch_6bp       |       69 | hybrid_ckmer7_csp   |           0.951 |
| local_mismatch_6bp       |       75 | ckmer5_count_l2     |           0.931 |
| local_mismatch_6bp       |       75 | ckmer7_count_l2     |           0.917 |
| local_mismatch_6bp       |       75 | cspaced_count_l2    |           0.910 |
| local_mismatch_6bp       |       75 | cspaced_property_l2 |           0.904 |
| local_mismatch_6bp       |       75 | hybrid_ckmer5_csp   |           0.936 |
| local_mismatch_6bp       |       75 | hybrid_ckmer7_csp   |           0.929 |
| substitution_1pct        |       69 | ckmer5_count_l2     |           0.973 |
| substitution_1pct        |       69 | ckmer7_count_l2     |           0.974 |
| substitution_1pct        |       69 | cspaced_count_l2    |           0.984 |
| substitution_1pct        |       69 | cspaced_property_l2 |           0.990 |
| substitution_1pct        |       69 | hybrid_ckmer5_csp   |           0.984 |
| substitution_1pct        |       69 | hybrid_ckmer7_csp   |           0.979 |
| substitution_1pct        |       75 | ckmer5_count_l2     |           0.995 |
| substitution_1pct        |       75 | ckmer7_count_l2     |           0.995 |
| substitution_1pct        |       75 | cspaced_count_l2    |           1.000 |
| substitution_1pct        |       75 | cspaced_property_l2 |           1.000 |
| substitution_1pct        |       75 | hybrid_ckmer5_csp   |           0.995 |
| substitution_1pct        |       75 | hybrid_ckmer7_csp   |           0.995 |
| substitution_1pct_N_3pct |       69 | ckmer5_count_l2     |           0.968 |
| substitution_1pct_N_3pct |       69 | ckmer7_count_l2     |           0.963 |
| substitution_1pct_N_3pct |       69 | cspaced_count_l2    |           0.958 |
| substitution_1pct_N_3pct |       69 | cspaced_property_l2 |           0.963 |
| substitution_1pct_N_3pct |       69 | hybrid_ckmer5_csp   |           0.979 |
| substitution_1pct_N_3pct |       69 | hybrid_ckmer7_csp   |           0.968 |
| substitution_1pct_N_3pct |       75 | ckmer5_count_l2     |           0.940 |
| substitution_1pct_N_3pct |       75 | ckmer7_count_l2     |           0.929 |
| substitution_1pct_N_3pct |       75 | cspaced_count_l2    |           0.947 |
| substitution_1pct_N_3pct |       75 | cspaced_property_l2 |           0.941 |
| substitution_1pct_N_3pct |       75 | hybrid_ckmer5_csp   |           0.946 |
| substitution_1pct_N_3pct |       75 | hybrid_ckmer7_csp   |           0.929 |
| trim_5bp                 |       69 | ckmer5_count_l2     |           1.000 |
| trim_5bp                 |       69 | ckmer7_count_l2     |           1.000 |
| trim_5bp                 |       69 | cspaced_count_l2    |           1.000 |
| trim_5bp                 |       69 | cspaced_property_l2 |           1.000 |
| trim_5bp                 |       69 | hybrid_ckmer5_csp   |           1.000 |
| trim_5bp                 |       69 | hybrid_ckmer7_csp   |           1.000 |
| trim_5bp                 |       75 | ckmer5_count_l2     |           1.000 |
| trim_5bp                 |       75 | ckmer7_count_l2     |           1.000 |
| trim_5bp                 |       75 | cspaced_count_l2    |           1.000 |
| trim_5bp                 |       75 | cspaced_property_l2 |           1.000 |
| trim_5bp                 |       75 | hybrid_ckmer5_csp   |           1.000 |
| trim_5bp                 |       75 | hybrid_ckmer7_csp   |           1.000 |
