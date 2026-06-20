# Stage-2 Representation Grid Summary

This run compares exact canonical k-mer evidence, canonical spaced counts, CSP and hybrid features under short-read perturbations.

## Best perturbation stability by condition and length

| condition                |   length | representation      |   paired_cosine_mean |   l2_delta_mean |   retrieval_top1 |   n_features |   density |
|:-------------------------|---------:|:--------------------|---------------------:|----------------:|-----------------:|-------------:|----------:|
| N_3pct                   |       69 | cspaced_property_l2 |                0.994 |           0.107 |            1.000 |          147 |     0.382 |
| N_3pct                   |       75 | cspaced_property_l2 |                0.995 |           0.101 |            1.000 |          147 |     0.402 |
| N_3pct                   |      100 | cspaced_property_l2 |                0.995 |           0.103 |            1.000 |          147 |     0.482 |
| N_3pct                   |      110 | cspaced_property_l2 |                0.995 |           0.095 |            1.000 |          147 |     0.512 |
| N_3pct                   |      125 | cspaced_property_l2 |                0.995 |           0.102 |            1.000 |          147 |     0.548 |
| N_3pct                   |      150 | cspaced_property_l2 |                0.996 |           0.087 |            1.000 |          147 |     0.606 |
| N_3pct                   |      300 | cspaced_property_l2 |                0.997 |           0.077 |            1.000 |          147 |     0.801 |
| local_mismatch_6bp       |       69 | cspaced_property_l2 |                0.988 |           0.157 |            0.999 |          147 |     0.394 |
| local_mismatch_6bp       |       75 | cspaced_property_l2 |                0.989 |           0.146 |            1.000 |          147 |     0.414 |
| local_mismatch_6bp       |      100 | cspaced_property_l2 |                0.993 |           0.118 |            1.000 |          147 |     0.498 |
| local_mismatch_6bp       |      110 | cspaced_property_l2 |                0.994 |           0.109 |            1.000 |          147 |     0.527 |
| local_mismatch_6bp       |      125 | cspaced_property_l2 |                0.995 |           0.099 |            1.000 |          147 |     0.566 |
| local_mismatch_6bp       |      150 | cspaced_property_l2 |                0.996 |           0.084 |            1.000 |          147 |     0.622 |
| local_mismatch_6bp       |      300 | cspaced_property_l2 |                0.999 |           0.043 |            1.000 |          147 |     0.814 |
| short_indel              |       69 | cspaced_property_l2 |                0.996 |           0.058 |            1.000 |          147 |     0.393 |
| short_indel              |       75 | cspaced_property_l2 |                0.997 |           0.056 |            1.000 |          147 |     0.412 |
| short_indel              |      100 | cspaced_property_l2 |                0.997 |           0.055 |            1.000 |          147 |     0.496 |
| short_indel              |      110 | cspaced_property_l2 |                0.997 |           0.058 |            1.000 |          147 |     0.524 |
| short_indel              |      125 | cspaced_property_l2 |                0.998 |           0.058 |            1.000 |          147 |     0.563 |
| short_indel              |      150 | cspaced_property_l2 |                0.998 |           0.056 |            1.000 |          147 |     0.620 |
| short_indel              |      300 | cspaced_property_l2 |                0.999 |           0.045 |            1.000 |          147 |     0.812 |
| substitution_1pct        |       69 | cspaced_property_l2 |                0.998 |           0.047 |            1.000 |          147 |     0.393 |
| substitution_1pct        |       75 | cspaced_property_l2 |                0.997 |           0.052 |            1.000 |          147 |     0.412 |
| substitution_1pct        |      100 | cspaced_property_l2 |                0.998 |           0.053 |            1.000 |          147 |     0.495 |
| substitution_1pct        |      110 | cspaced_property_l2 |                0.998 |           0.052 |            1.000 |          147 |     0.525 |
| substitution_1pct        |      125 | cspaced_property_l2 |                0.998 |           0.051 |            1.000 |          147 |     0.564 |
| substitution_1pct        |      150 | cspaced_property_l2 |                0.998 |           0.050 |            1.000 |          147 |     0.620 |
| substitution_1pct        |      300 | cspaced_property_l2 |                0.999 |           0.040 |            1.000 |          147 |     0.813 |
| substitution_1pct_N_3pct |       69 | cspaced_property_l2 |                0.991 |           0.128 |            1.000 |          147 |     0.382 |
| substitution_1pct_N_3pct |       75 | cspaced_property_l2 |                0.993 |           0.119 |            1.000 |          147 |     0.402 |
| substitution_1pct_N_3pct |      100 | cspaced_property_l2 |                0.993 |           0.120 |            1.000 |          147 |     0.482 |
| substitution_1pct_N_3pct |      110 | cspaced_property_l2 |                0.993 |           0.113 |            1.000 |          147 |     0.512 |
| substitution_1pct_N_3pct |      125 | cspaced_property_l2 |                0.993 |           0.119 |            1.000 |          147 |     0.547 |
| substitution_1pct_N_3pct |      150 | cspaced_property_l2 |                0.995 |           0.104 |            1.000 |          147 |     0.607 |
| substitution_1pct_N_3pct |      300 | cspaced_property_l2 |                0.996 |           0.088 |            1.000 |          147 |     0.801 |
| trim_5bp                 |       69 | cspaced_property_l2 |                0.997 |           0.075 |            1.000 |          147 |     0.383 |
| trim_5bp                 |       75 | cspaced_property_l2 |                0.998 |           0.069 |            1.000 |          147 |     0.403 |
| trim_5bp                 |      100 | cspaced_property_l2 |                0.998 |           0.056 |            1.000 |          147 |     0.487 |
| trim_5bp                 |      110 | cspaced_property_l2 |                0.999 |           0.051 |            1.000 |          147 |     0.517 |
| trim_5bp                 |      125 | cspaced_property_l2 |                0.999 |           0.046 |            1.000 |          147 |     0.557 |
| trim_5bp                 |      150 | cspaced_property_l2 |                0.999 |           0.040 |            1.000 |          147 |     0.614 |
| trim_5bp                 |      300 | cspaced_property_l2 |                1.000 |           0.021 |            1.000 |          147 |     0.810 |

## Hybrid overview

| condition                |   length |   paired_cosine_mean |   l2_delta_mean |   retrieval_top1 |
|:-------------------------|---------:|---------------------:|----------------:|-----------------:|
| N_3pct                   |       69 |                0.957 |           0.289 |            1.000 |
| N_3pct                   |       75 |                0.961 |           0.275 |            1.000 |
| N_3pct                   |      100 |                0.958 |           0.287 |            1.000 |
| N_3pct                   |      110 |                0.962 |           0.271 |            1.000 |
| N_3pct                   |      125 |                0.956 |           0.293 |            1.000 |
| N_3pct                   |      150 |                0.965 |           0.262 |            1.000 |
| N_3pct                   |      300 |                0.965 |           0.258 |            1.000 |
| local_mismatch_6bp       |       69 |                0.919 |           0.399 |            0.999 |
| local_mismatch_6bp       |       75 |                0.927 |           0.379 |            1.000 |
| local_mismatch_6bp       |      100 |                0.947 |           0.322 |            1.000 |
| local_mismatch_6bp       |      110 |                0.953 |           0.304 |            1.000 |
| local_mismatch_6bp       |      125 |                0.959 |           0.284 |            1.000 |
| local_mismatch_6bp       |      150 |                0.967 |           0.253 |            1.000 |
| local_mismatch_6bp       |      300 |                0.986 |           0.164 |            1.000 |
| short_indel              |       69 |                0.976 |           0.150 |            1.000 |
| short_indel              |       75 |                0.977 |           0.148 |            1.000 |
| short_indel              |      100 |                0.979 |           0.154 |            1.000 |
| short_indel              |      110 |                0.978 |           0.164 |            1.000 |
| short_indel              |      125 |                0.978 |           0.169 |            1.000 |
| short_indel              |      150 |                0.979 |           0.170 |            1.000 |
| short_indel              |      300 |                0.981 |           0.175 |            1.000 |
| substitution_1pct        |       69 |                0.974 |           0.150 |            1.000 |
| substitution_1pct        |       75 |                0.971 |           0.172 |            1.000 |
| substitution_1pct        |      100 |                0.972 |           0.183 |            1.000 |
| substitution_1pct        |      110 |                0.973 |           0.186 |            1.000 |
| substitution_1pct        |      125 |                0.974 |           0.185 |            1.000 |
| substitution_1pct        |      150 |                0.975 |           0.189 |            1.000 |
| substitution_1pct        |      300 |                0.978 |           0.192 |            1.000 |
| substitution_1pct_N_3pct |       69 |                0.931 |           0.357 |            1.000 |
| substitution_1pct_N_3pct |       75 |                0.936 |           0.343 |            1.000 |
| substitution_1pct_N_3pct |      100 |                0.934 |           0.354 |            1.000 |
| substitution_1pct_N_3pct |      110 |                0.937 |           0.344 |            1.000 |
| substitution_1pct_N_3pct |      125 |                0.932 |           0.360 |            1.000 |
| substitution_1pct_N_3pct |      150 |                0.942 |           0.332 |            1.000 |
| substitution_1pct_N_3pct |      300 |                0.944 |           0.324 |            1.000 |
| trim_5bp                 |       69 |                0.981 |           0.195 |            1.000 |
| trim_5bp                 |       75 |                0.983 |           0.185 |            1.000 |
| trim_5bp                 |      100 |                0.988 |           0.156 |            1.000 |
| trim_5bp                 |      110 |                0.989 |           0.147 |            1.000 |
| trim_5bp                 |      125 |                0.991 |           0.136 |            1.000 |
| trim_5bp                 |      150 |                0.993 |           0.121 |            1.000 |
| trim_5bp                 |      300 |                0.997 |           0.078 |            1.000 |

## Best readout probes

| task                 | condition                |   length | representation      | classifier       |   mean_macro_f1 |   mean_accuracy |
|:---------------------|:-------------------------|---------:|:--------------------|:-----------------|----------------:|----------------:|
| target_background    | N_3pct                   |       69 | hybrid_ckmer5_csp   | mlp              |           0.488 |           0.510 |
| target_background    | N_3pct                   |       75 | cspaced_property_l2 | logistic         |           0.552 |           0.589 |
| target_background    | N_3pct                   |      100 | hybrid_ckmer5_csp   | nearest_centroid |           0.614 |           0.655 |
| target_background    | N_3pct                   |      150 | hybrid_ckmer5_csp   | nearest_centroid |           0.564 |           0.617 |
| target_background    | clean                    |       69 | cspaced_property_l2 | mlp              |           0.523 |           0.570 |
| target_background    | clean                    |       75 | hybrid_ckmer5_csp   | logistic         |           0.537 |           0.599 |
| target_background    | clean                    |      100 | ckmer5_count_l2     | nearest_centroid |           0.587 |           0.634 |
| target_background    | clean                    |      150 | cspaced_property_l2 | nearest_centroid |           0.568 |           0.594 |
| target_background    | substitution_1pct        |       69 | cspaced_count_l2    | nearest_centroid |           0.528 |           0.549 |
| target_background    | substitution_1pct        |       75 | cspaced_property_l2 | logistic         |           0.539 |           0.569 |
| target_background    | substitution_1pct        |      100 | ckmer5_count_l2     | nearest_centroid |           0.594 |           0.631 |
| target_background    | substitution_1pct        |      150 | cspaced_property_l2 | nearest_centroid |           0.615 |           0.638 |
| target_background    | substitution_1pct_N_3pct |       69 | cspaced_property_l2 | mlp              |           0.555 |           0.587 |
| target_background    | substitution_1pct_N_3pct |       75 | cspaced_property_l2 | nearest_centroid |           0.530 |           0.553 |
| target_background    | substitution_1pct_N_3pct |      100 | hybrid_ckmer5_csp   | nearest_centroid |           0.541 |           0.595 |
| target_background    | substitution_1pct_N_3pct |      150 | cspaced_count_l2    | nearest_centroid |           0.602 |           0.634 |
| target_background    | trim_5bp                 |       69 | cspaced_property_l2 | mlp              |           0.531 |           0.573 |
| target_background    | trim_5bp                 |       75 | cspaced_count_l2    | nearest_centroid |           0.565 |           0.594 |
| target_background    | trim_5bp                 |      100 | ckmer5_count_l2     | nearest_centroid |           0.590 |           0.633 |
| target_background    | trim_5bp                 |      150 | cspaced_property_l2 | nearest_centroid |           0.571 |           0.593 |
| within_genus_species | N_3pct                   |       69 | hybrid_ckmer5_csp   | nearest_centroid |           0.302 |           0.308 |
| within_genus_species | N_3pct                   |       75 | hybrid_ckmer5_csp   | nearest_centroid |           0.354 |           0.358 |
| within_genus_species | N_3pct                   |      100 | ckmer7_count_l2     | nearest_centroid |           0.334 |           0.352 |
| within_genus_species | N_3pct                   |      150 | cspaced_count_l2    | logistic         |           0.381 |           0.382 |
| within_genus_species | clean                    |       69 | hybrid_ckmer5_csp   | nearest_centroid |           0.327 |           0.337 |
| within_genus_species | clean                    |       75 | hybrid_ckmer5_csp   | nearest_centroid |           0.372 |           0.374 |
| within_genus_species | clean                    |      100 | ckmer5_count_l2     | nearest_centroid |           0.349 |           0.359 |
| within_genus_species | clean                    |      150 | cspaced_property_l2 | logistic         |           0.390 |           0.396 |
| within_genus_species | substitution_1pct        |       69 | hybrid_ckmer5_csp   | mlp              |           0.325 |           0.343 |
| within_genus_species | substitution_1pct        |       75 | hybrid_ckmer5_csp   | logistic         |           0.383 |           0.393 |
| within_genus_species | substitution_1pct        |      100 | ckmer7_count_l2     | nearest_centroid |           0.339 |           0.366 |
| within_genus_species | substitution_1pct        |      150 | cspaced_property_l2 | nearest_centroid |           0.390 |           0.394 |
| within_genus_species | substitution_1pct_N_3pct |       69 | cspaced_property_l2 | mlp              |           0.325 |           0.352 |
| within_genus_species | substitution_1pct_N_3pct |       75 | ckmer7_count_l2     | nearest_centroid |           0.348 |           0.373 |
| within_genus_species | substitution_1pct_N_3pct |      100 | hybrid_ckmer5_csp   | nearest_centroid |           0.346 |           0.355 |
| within_genus_species | substitution_1pct_N_3pct |      150 | cspaced_property_l2 | logistic         |           0.380 |           0.389 |
| within_genus_species | trim_5bp                 |       69 | ckmer5_count_l2     | nearest_centroid |           0.338 |           0.347 |
| within_genus_species | trim_5bp                 |       75 | ckmer7_count_l2     | logistic         |           0.370 |           0.387 |
| within_genus_species | trim_5bp                 |      100 | ckmer5_count_l2     | nearest_centroid |           0.345 |           0.352 |
| within_genus_species | trim_5bp                 |      150 | cspaced_count_l2    | logistic         |           0.392 |           0.396 |
