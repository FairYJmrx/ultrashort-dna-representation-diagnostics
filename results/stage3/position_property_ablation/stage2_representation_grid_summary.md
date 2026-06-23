# Stage-2 Representation Grid Summary

This run compares exact canonical k-mer evidence, canonical spaced counts, CSP and hybrid features under short-read perturbations.

## Best perturbation stability by condition and length

| condition                 |   length | representation                     |   paired_cosine_mean |   l2_delta_mean |   retrieval_top1 |   n_features |   density |
|:--------------------------|---------:|:-----------------------------------|---------------------:|----------------:|-----------------:|-------------:|----------:|
| N_10pct                   |       69 | ckmer4_property_multiscale_mean_l2 |                0.974 |           0.228 |            1.000 |          222 |     0.532 |
| N_10pct                   |       75 | ckmer4_property_multiscale_mean_l2 |                0.973 |           0.231 |            1.000 |          222 |     0.544 |
| N_10pct                   |      100 | ckmer4_property_multiscale_mean_l2 |                0.977 |           0.214 |            1.000 |          222 |     0.593 |
| N_10pct                   |      125 | ckmer4_property_multiscale_mean_l2 |                0.980 |           0.200 |            1.000 |          222 |     0.632 |
| N_10pct                   |      150 | ckmer4_property_multiscale_mean_l2 |                0.980 |           0.200 |            1.000 |          222 |     0.665 |
| N_10pct                   |      300 | ckmer4_property_multiscale_mean_l2 |                0.985 |           0.172 |            1.000 |          222 |     0.797 |
| N_3pct                    |       69 | ckmer4_property_multiscale_mean_l2 |                0.995 |           0.101 |            1.000 |          222 |     0.541 |
| N_3pct                    |       75 | ckmer4_property_multiscale_mean_l2 |                0.995 |           0.095 |            1.000 |          222 |     0.555 |
| N_3pct                    |      100 | ckmer4_property_multiscale_mean_l2 |                0.995 |           0.096 |            1.000 |          222 |     0.606 |
| N_3pct                    |      125 | ckmer4_property_multiscale_mean_l2 |                0.995 |           0.096 |            1.000 |          222 |     0.646 |
| N_3pct                    |      150 | ckmer4_property_multiscale_mean_l2 |                0.997 |           0.081 |            1.000 |          222 |     0.684 |
| N_3pct                    |      300 | ckmer4_property_multiscale_mean_l2 |                0.997 |           0.073 |            1.000 |          222 |     0.818 |
| local_mismatch_12bp       |       69 | ckmer4_property_multiscale_mean_l2 |                0.986 |           0.164 |            1.000 |          222 |     0.536 |
| local_mismatch_12bp       |       75 | ckmer4_property_multiscale_mean_l2 |                0.988 |           0.153 |            1.000 |          222 |     0.549 |
| local_mismatch_12bp       |      100 | ckmer4_property_multiscale_l2      |                0.992 |           0.123 |            1.000 |          297 |     0.649 |
| local_mismatch_12bp       |      125 | ckmer4_property_multiscale_l2      |                0.995 |           0.101 |            1.000 |          297 |     0.678 |
| local_mismatch_12bp       |      150 | ckmer4_property_multiscale_l2      |                0.996 |           0.086 |            1.000 |          297 |     0.705 |
| local_mismatch_12bp       |      300 | ckmer4_property_multiscale_l2      |                0.999 |           0.045 |            1.000 |          297 |     0.799 |
| local_mismatch_6bp        |       69 | ckmer4_property_multiscale_mean_l2 |                0.992 |           0.124 |            1.000 |          222 |     0.534 |
| local_mismatch_6bp        |       75 | ckmer4_property_multiscale_mean_l2 |                0.993 |           0.118 |            1.000 |          222 |     0.548 |
| local_mismatch_6bp        |      100 | ckmer4_property_multiscale_mean_l2 |                0.996 |           0.094 |            1.000 |          222 |     0.597 |
| local_mismatch_6bp        |      125 | ckmer4_property_multiscale_mean_l2 |                0.997 |           0.077 |            1.000 |          222 |     0.635 |
| local_mismatch_6bp        |      150 | ckmer4_property_multiscale_mean_l2 |                0.998 |           0.066 |            1.000 |          222 |     0.671 |
| local_mismatch_6bp        |      300 | ckmer4_property_multiscale_l2      |                0.999 |           0.035 |            1.000 |          297 |     0.798 |
| short_indel               |       69 | ckmer4_property_multiscale_mean_l2 |                0.998 |           0.039 |            1.000 |          222 |     0.532 |
| short_indel               |       75 | ckmer4_property_multiscale_mean_l2 |                0.998 |           0.039 |            1.000 |          222 |     0.546 |
| short_indel               |      100 | ckmer4_property_multiscale_mean_l2 |                0.999 |           0.039 |            1.000 |          222 |     0.595 |
| short_indel               |      125 | ckmer4_property_multiscale_mean_l2 |                0.999 |           0.039 |            1.000 |          222 |     0.633 |
| short_indel               |      150 | ckmer4_property_multiscale_l2      |                0.999 |           0.038 |            1.000 |          297 |     0.702 |
| short_indel               |      300 | ckmer4_property_multiscale_l2      |                0.999 |           0.031 |            1.000 |          297 |     0.797 |
| substitution_1pct         |       69 | ckmer4_property_multiscale_mean_l2 |                0.998 |           0.048 |            1.000 |          222 |     0.532 |
| substitution_1pct         |       75 | ckmer4_property_multiscale_mean_l2 |                0.998 |           0.051 |            1.000 |          222 |     0.546 |
| substitution_1pct         |      100 | ckmer4_property_multiscale_mean_l2 |                0.998 |           0.048 |            1.000 |          222 |     0.595 |
| substitution_1pct         |      125 | ckmer4_property_multiscale_mean_l2 |                0.999 |           0.043 |            1.000 |          222 |     0.633 |
| substitution_1pct         |      150 | ckmer4_property_multiscale_mean_l2 |                0.999 |           0.047 |            1.000 |          222 |     0.669 |
| substitution_1pct         |      300 | ckmer4_property_multiscale_l2      |                0.999 |           0.036 |            1.000 |          297 |     0.798 |
| substitution_1pct_N_3pct  |       69 | ckmer4_property_multiscale_mean_l2 |                0.993 |           0.119 |            1.000 |          222 |     0.540 |
| substitution_1pct_N_3pct  |       75 | ckmer4_property_multiscale_mean_l2 |                0.993 |           0.112 |            1.000 |          222 |     0.555 |
| substitution_1pct_N_3pct  |      100 | ckmer4_property_multiscale_mean_l2 |                0.993 |           0.113 |            1.000 |          222 |     0.606 |
| substitution_1pct_N_3pct  |      125 | ckmer4_property_multiscale_mean_l2 |                0.994 |           0.109 |            1.000 |          222 |     0.647 |
| substitution_1pct_N_3pct  |      150 | ckmer4_property_multiscale_mean_l2 |                0.995 |           0.097 |            1.000 |          222 |     0.684 |
| substitution_1pct_N_3pct  |      300 | ckmer4_property_multiscale_mean_l2 |                0.997 |           0.083 |            1.000 |          222 |     0.820 |
| substitution_5pct         |       69 | ckmer4_property_multiscale_mean_l2 |                0.989 |           0.137 |            1.000 |          222 |     0.534 |
| substitution_5pct         |       75 | ckmer4_property_multiscale_mean_l2 |                0.989 |           0.139 |            1.000 |          222 |     0.547 |
| substitution_5pct         |      100 | ckmer4_property_multiscale_mean_l2 |                0.991 |           0.129 |            0.998 |          222 |     0.598 |
| substitution_5pct         |      125 | ckmer4_property_multiscale_mean_l2 |                0.992 |           0.121 |            1.000 |          222 |     0.636 |
| substitution_5pct         |      150 | ckmer4_property_multiscale_mean_l2 |                0.993 |           0.114 |            1.000 |          222 |     0.673 |
| substitution_5pct         |      300 | ckmer4_property_multiscale_l2      |                0.996 |           0.086 |            1.000 |          297 |     0.801 |
| substitution_5pct_N_10pct |       69 | ckmer4_property_multiscale_mean_l2 |                0.964 |           0.268 |            0.980 |          222 |     0.533 |
| substitution_5pct_N_10pct |       75 | ckmer4_property_multiscale_mean_l2 |                0.963 |           0.271 |            0.988 |          222 |     0.545 |
| substitution_5pct_N_10pct |      100 | ckmer4_property_multiscale_mean_l2 |                0.968 |           0.251 |            0.988 |          222 |     0.594 |
| substitution_5pct_N_10pct |      125 | ckmer4_property_multiscale_mean_l2 |                0.972 |           0.234 |            0.998 |          222 |     0.633 |
| substitution_5pct_N_10pct |      150 | ckmer4_property_multiscale_mean_l2 |                0.973 |           0.231 |            0.995 |          222 |     0.668 |
| substitution_5pct_N_10pct |      300 | ckmer4_property_multiscale_mean_l2 |                0.981 |           0.193 |            1.000 |          222 |     0.802 |

## Hybrid overview

| condition                 |   length |   paired_cosine_mean |   l2_delta_mean |   retrieval_top1 |
|:--------------------------|---------:|---------------------:|----------------:|-----------------:|
| N_10pct                   |       69 |                0.879 |           0.489 |            1.000 |
| N_10pct                   |       75 |                0.879 |           0.490 |            1.000 |
| N_10pct                   |      100 |                0.890 |           0.468 |            1.000 |
| N_10pct                   |      125 |                0.901 |           0.442 |            1.000 |
| N_10pct                   |      150 |                0.902 |           0.440 |            1.000 |
| N_10pct                   |      300 |                0.920 |           0.399 |            1.000 |
| N_3pct                    |       69 |                0.967 |           0.256 |            1.000 |
| N_3pct                    |       75 |                0.970 |           0.245 |            1.000 |
| N_3pct                    |      100 |                0.968 |           0.250 |            1.000 |
| N_3pct                    |      125 |                0.969 |           0.248 |            1.000 |
| N_3pct                    |      150 |                0.976 |           0.220 |            1.000 |
| N_3pct                    |      300 |                0.978 |           0.207 |            1.000 |
| local_mismatch_12bp       |       69 |                0.892 |           0.463 |            1.000 |
| local_mismatch_12bp       |       75 |                0.903 |           0.439 |            1.000 |
| local_mismatch_12bp       |      100 |                0.932 |           0.366 |            1.000 |
| local_mismatch_12bp       |      125 |                0.950 |           0.314 |            1.000 |
| local_mismatch_12bp       |      150 |                0.962 |           0.276 |            1.000 |
| local_mismatch_12bp       |      300 |                0.985 |           0.171 |            1.000 |
| local_mismatch_6bp        |       69 |                0.935 |           0.360 |            1.000 |
| local_mismatch_6bp        |       75 |                0.940 |           0.344 |            1.000 |
| local_mismatch_6bp        |      100 |                0.958 |           0.288 |            1.000 |
| local_mismatch_6bp        |      125 |                0.970 |           0.245 |            1.000 |
| local_mismatch_6bp        |      150 |                0.976 |           0.217 |            1.000 |
| local_mismatch_6bp        |      300 |                0.991 |           0.135 |            1.000 |
| short_indel               |       69 |                0.984 |           0.124 |            1.000 |
| short_indel               |       75 |                0.984 |           0.127 |            1.000 |
| short_indel               |      100 |                0.985 |           0.130 |            1.000 |
| short_indel               |      125 |                0.986 |           0.138 |            1.000 |
| short_indel               |      150 |                0.987 |           0.136 |            1.000 |
| short_indel               |      300 |                0.990 |           0.134 |            1.000 |
| substitution_1pct         |       69 |                0.978 |           0.147 |            1.000 |
| substitution_1pct         |       75 |                0.977 |           0.158 |            1.000 |
| substitution_1pct         |      100 |                0.980 |           0.156 |            1.000 |
| substitution_1pct         |      125 |                0.983 |           0.146 |            1.000 |
| substitution_1pct         |      150 |                0.982 |           0.162 |            1.000 |
| substitution_1pct         |      300 |                0.987 |           0.150 |            1.000 |
| substitution_1pct_N_3pct  |       69 |                0.947 |           0.314 |            1.000 |
| substitution_1pct_N_3pct  |       75 |                0.950 |           0.306 |            1.000 |
| substitution_1pct_N_3pct  |      100 |                0.949 |           0.313 |            1.000 |
| substitution_1pct_N_3pct  |      125 |                0.952 |           0.304 |            1.000 |
| substitution_1pct_N_3pct  |      150 |                0.959 |           0.281 |            1.000 |
| substitution_1pct_N_3pct  |      300 |                0.965 |           0.261 |            1.000 |
| substitution_5pct         |       69 |                0.904 |           0.413 |            1.000 |
| substitution_5pct         |       75 |                0.901 |           0.425 |            1.000 |
| substitution_5pct         |      100 |                0.909 |           0.413 |            1.000 |
| substitution_5pct         |      125 |                0.914 |           0.405 |            1.000 |
| substitution_5pct         |      150 |                0.921 |           0.391 |            1.000 |
| substitution_5pct         |      300 |                0.938 |           0.349 |            1.000 |
| substitution_5pct_N_10pct |       69 |                0.797 |           0.630 |            0.994 |
| substitution_5pct_N_10pct |       75 |                0.794 |           0.635 |            0.995 |
| substitution_5pct_N_10pct |      100 |                0.812 |           0.607 |            1.000 |
| substitution_5pct_N_10pct |      125 |                0.831 |           0.577 |            1.000 |
| substitution_5pct_N_10pct |      150 |                0.833 |           0.575 |            1.000 |
| substitution_5pct_N_10pct |      300 |                0.865 |           0.518 |            1.000 |

## Best readout probes

| task                 | condition                |   length | representation                                       | classifier       |   mean_macro_f1 |   mean_accuracy |
|:---------------------|:-------------------------|---------:|:-----------------------------------------------------|:-----------------|----------------:|----------------:|
| target_background    | N_3pct                   |       69 | ckmer4_property_multiscale_l2                        | logistic         |           0.610 |           0.670 |
| target_background    | N_3pct                   |       75 | hybrid:ckmer5_count_l2+ckmer4_property_anchor_l2     | nearest_centroid |           0.546 |           0.614 |
| target_background    | N_3pct                   |      100 | ckmer4_property_multiscale_l2                        | logistic         |           0.543 |           0.585 |
| target_background    | N_3pct                   |      150 | ckmer5_property_anchor_l2                            | nearest_centroid |           0.515 |           0.541 |
| target_background    | clean                    |       69 | ckmer4_property_anchor_l2                            | logistic         |           0.596 |           0.656 |
| target_background    | clean                    |       75 | ckmer4_property_multiscale_mean_l2                   | logistic         |           0.548 |           0.619 |
| target_background    | clean                    |      100 | ckmer4_count_l2                                      | logistic         |           0.549 |           0.594 |
| target_background    | clean                    |      150 | ckmer4_property_moment_l2                            | logistic         |           0.521 |           0.551 |
| target_background    | substitution_1pct        |       69 | ckmer4_property_anchor_l2                            | logistic         |           0.566 |           0.631 |
| target_background    | substitution_1pct        |       75 | ckmer5_property_multiscale_l2                        | nearest_centroid |           0.574 |           0.626 |
| target_background    | substitution_1pct        |      100 | cspaced_property_l2                                  | logistic         |           0.582 |           0.618 |
| target_background    | substitution_1pct        |      150 | ckmer4_property_moment_l2                            | logistic         |           0.542 |           0.570 |
| target_background    | substitution_1pct_N_3pct |       69 | ckmer4_property_moment_l2                            | logistic         |           0.559 |           0.636 |
| target_background    | substitution_1pct_N_3pct |       75 | ckmer4_property_multiscale_l2                        | logistic         |           0.541 |           0.597 |
| target_background    | substitution_1pct_N_3pct |      100 | cspaced_property_l2                                  | logistic         |           0.576 |           0.612 |
| target_background    | substitution_1pct_N_3pct |      150 | cspaced_property_l2                                  | nearest_centroid |           0.529 |           0.555 |
| within_genus_species | N_3pct                   |       69 | hybrid:ckmer5_count_l2+ckmer4_property_moment_l2     | logistic         |           0.311 |           0.325 |
| within_genus_species | N_3pct                   |       75 | ckmer4_property_moment_l2                            | nearest_centroid |           0.352 |           0.365 |
| within_genus_species | N_3pct                   |      100 | cspaced_property_l2                                  | logistic         |           0.322 |           0.335 |
| within_genus_species | N_3pct                   |      150 | ckmer4_property_anchor_l2                            | logistic         |           0.329 |           0.343 |
| within_genus_species | clean                    |       69 | hybrid:ckmer5_count_l2+ckmer4_property_multiscale_l2 | logistic         |           0.337 |           0.348 |
| within_genus_species | clean                    |       75 | hybrid:ckmer5_count_l2+ckmer4_property_l2            | logistic         |           0.349 |           0.363 |
| within_genus_species | clean                    |      100 | cspaced_property_l2                                  | logistic         |           0.345 |           0.356 |
| within_genus_species | clean                    |      150 | hybrid:ckmer5_count_l2+ckmer4_property_multiscale_l2 | logistic         |           0.318 |           0.337 |
| within_genus_species | substitution_1pct        |       69 | ckmer5_property_multiscale_l2                        | logistic         |           0.324 |           0.345 |
| within_genus_species | substitution_1pct        |       75 | ckmer5_property_multiscale_l2                        | logistic         |           0.353 |           0.377 |
| within_genus_species | substitution_1pct        |      100 | cspaced_property_l2                                  | nearest_centroid |           0.373 |           0.383 |
| within_genus_species | substitution_1pct        |      150 | hybrid:ckmer5_count_l2+ckmer4_property_multiscale_l2 | logistic         |           0.356 |           0.369 |
| within_genus_species | substitution_1pct_N_3pct |       69 | hybrid:ckmer5_count_l2+ckmer4_property_anchor_l2     | logistic         |           0.360 |           0.378 |
| within_genus_species | substitution_1pct_N_3pct |       75 | ckmer4_property_moment_l2                            | nearest_centroid |           0.366 |           0.375 |
| within_genus_species | substitution_1pct_N_3pct |      100 | cspaced_property_l2                                  | nearest_centroid |           0.331 |           0.341 |
| within_genus_species | substitution_1pct_N_3pct |      150 | ckmer5_property_anchor_l2                            | nearest_centroid |           0.338 |           0.353 |
