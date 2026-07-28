# Stage-2 Representation Grid Summary

This run compares exact canonical k-mer evidence, canonical spaced counts, CSP and hybrid features under short-read perturbations.

## Best perturbation stability by condition and length

| condition                |   length | representation      |   paired_cosine_mean |   l2_delta_mean |   retrieval_top1 |   n_features |   density |
|:-------------------------|---------:|:--------------------|---------------------:|----------------:|-----------------:|-------------:|----------:|
| N_3pct                   |       69 | cspaced_property_l2 |                0.994 |           0.107 |            1.000 |          147 |     0.384 |
| N_3pct                   |       75 | cspaced_property_l2 |                0.995 |           0.101 |            1.000 |          147 |     0.403 |
| N_3pct                   |      100 | cspaced_property_l2 |                0.995 |           0.103 |            1.000 |          147 |     0.483 |
| N_3pct                   |      125 | cspaced_property_l2 |                0.995 |           0.104 |            1.000 |          147 |     0.548 |
| N_3pct                   |      150 | cspaced_property_l2 |                0.996 |           0.087 |            1.000 |          147 |     0.608 |
| N_3pct                   |      300 | cspaced_property_l2 |                0.997 |           0.077 |            1.000 |          147 |     0.802 |
| local_mismatch_6bp       |       69 | eiip_summary_l2     |                1.000 |           0.015 |            0.022 |            8 |     1.000 |
| local_mismatch_6bp       |       75 | eiip_summary_l2     |                1.000 |           0.014 |            0.037 |            8 |     1.000 |
| local_mismatch_6bp       |      100 | eiip_summary_l2     |                1.000 |           0.016 |            0.052 |            8 |     1.000 |
| local_mismatch_6bp       |      125 | eiip_summary_l2     |                1.000 |           0.017 |            0.040 |            8 |     1.000 |
| local_mismatch_6bp       |      150 | eiip_summary_l2     |                1.000 |           0.015 |            0.045 |            8 |     1.000 |
| local_mismatch_6bp       |      300 | eiip_summary_l2     |                1.000 |           0.004 |            0.068 |            8 |     1.000 |
| short_indel              |       69 | eiip_summary_l2     |                0.999 |           0.023 |            0.557 |            8 |     1.000 |
| short_indel              |       75 | eiip_summary_l2     |                0.998 |           0.028 |            0.522 |            8 |     1.000 |
| short_indel              |      100 | cspaced_property_l2 |                0.997 |           0.056 |            1.000 |          147 |     0.496 |
| short_indel              |      125 | cspaced_property_l2 |                0.998 |           0.055 |            1.000 |          147 |     0.565 |
| short_indel              |      150 | cspaced_property_l2 |                0.998 |           0.056 |            1.000 |          147 |     0.621 |
| short_indel              |      300 | eiip_summary_l2     |                0.999 |           0.019 |            0.090 |            8 |     1.000 |
| substitution_1pct        |       69 | eiip_summary_l2     |                1.000 |           0.003 |            0.665 |            8 |     1.000 |
| substitution_1pct        |       75 | eiip_summary_l2     |                1.000 |           0.003 |            0.623 |            8 |     1.000 |
| substitution_1pct        |      100 | eiip_summary_l2     |                1.000 |           0.005 |            0.520 |            8 |     1.000 |
| substitution_1pct        |      125 | eiip_summary_l2     |                1.000 |           0.005 |            0.448 |            8 |     1.000 |
| substitution_1pct        |      150 | eiip_summary_l2     |                1.000 |           0.006 |            0.398 |            8 |     1.000 |
| substitution_1pct        |      300 | eiip_summary_l2     |                1.000 |           0.003 |            0.203 |            8 |     1.000 |
| substitution_1pct_N_3pct |       69 | cspaced_property_l2 |                0.991 |           0.130 |            1.000 |          147 |     0.384 |
| substitution_1pct_N_3pct |       75 | cspaced_property_l2 |                0.992 |           0.122 |            1.000 |          147 |     0.403 |
| substitution_1pct_N_3pct |      100 | cspaced_property_l2 |                0.993 |           0.119 |            1.000 |          147 |     0.483 |
| substitution_1pct_N_3pct |      125 | cspaced_property_l2 |                0.993 |           0.120 |            1.000 |          147 |     0.549 |
| substitution_1pct_N_3pct |      150 | cspaced_property_l2 |                0.994 |           0.104 |            1.000 |          147 |     0.609 |
| substitution_1pct_N_3pct |      300 | cspaced_property_l2 |                0.996 |           0.088 |            1.000 |          147 |     0.803 |
| trim_5bp                 |       69 | cspaced_property_l2 |                0.997 |           0.075 |            1.000 |          147 |     0.384 |
| trim_5bp                 |       75 | cspaced_property_l2 |                0.998 |           0.070 |            1.000 |          147 |     0.404 |
| trim_5bp                 |      100 | cspaced_property_l2 |                0.998 |           0.056 |            1.000 |          147 |     0.488 |
| trim_5bp                 |      125 | cspaced_property_l2 |                0.999 |           0.046 |            1.000 |          147 |     0.558 |
| trim_5bp                 |      150 | cspaced_property_l2 |                0.999 |           0.040 |            1.000 |          147 |     0.616 |
| trim_5bp                 |      300 | cspaced_property_l2 |                1.000 |           0.021 |            1.000 |          147 |     0.811 |

## Hybrid overview

| condition                |   length |   paired_cosine_mean |   l2_delta_mean |   retrieval_top1 |
|:-------------------------|---------:|---------------------:|----------------:|-----------------:|
| N_3pct                   |       69 |                0.957 |           0.289 |            1.000 |
| N_3pct                   |       75 |                0.961 |           0.274 |            1.000 |
| N_3pct                   |      100 |                0.957 |           0.289 |            1.000 |
| N_3pct                   |      125 |                0.956 |           0.293 |            1.000 |
| N_3pct                   |      150 |                0.965 |           0.261 |            1.000 |
| N_3pct                   |      300 |                0.965 |           0.258 |            1.000 |
| local_mismatch_6bp       |       69 |                0.918 |           0.402 |            1.000 |
| local_mismatch_6bp       |       75 |                0.927 |           0.379 |            1.000 |
| local_mismatch_6bp       |      100 |                0.947 |           0.322 |            1.000 |
| local_mismatch_6bp       |      125 |                0.959 |           0.283 |            1.000 |
| local_mismatch_6bp       |      150 |                0.967 |           0.253 |            1.000 |
| local_mismatch_6bp       |      300 |                0.986 |           0.164 |            1.000 |
| short_indel              |       69 |                0.976 |           0.145 |            1.000 |
| short_indel              |       75 |                0.977 |           0.145 |            1.000 |
| short_indel              |      100 |                0.979 |           0.156 |            1.000 |
| short_indel              |      125 |                0.979 |           0.163 |            1.000 |
| short_indel              |      150 |                0.979 |           0.171 |            1.000 |
| short_indel              |      300 |                0.982 |           0.175 |            1.000 |
| substitution_1pct        |       69 |                0.971 |           0.165 |            1.000 |
| substitution_1pct        |       75 |                0.971 |           0.167 |            1.000 |
| substitution_1pct        |      100 |                0.973 |           0.179 |            1.000 |
| substitution_1pct        |      125 |                0.974 |           0.185 |            1.000 |
| substitution_1pct        |      150 |                0.975 |           0.189 |            1.000 |
| substitution_1pct        |      300 |                0.978 |           0.191 |            1.000 |
| substitution_1pct_N_3pct |       69 |                0.928 |           0.366 |            1.000 |
| substitution_1pct_N_3pct |       75 |                0.934 |           0.351 |            1.000 |
| substitution_1pct_N_3pct |      100 |                0.935 |           0.351 |            1.000 |
| substitution_1pct_N_3pct |      125 |                0.931 |           0.363 |            1.000 |
| substitution_1pct_N_3pct |      150 |                0.941 |           0.334 |            1.000 |
| substitution_1pct_N_3pct |      300 |                0.943 |           0.327 |            1.000 |
| trim_5bp                 |       69 |                0.981 |           0.197 |            1.000 |
| trim_5bp                 |       75 |                0.983 |           0.186 |            1.000 |
| trim_5bp                 |      100 |                0.988 |           0.157 |            1.000 |
| trim_5bp                 |      125 |                0.991 |           0.136 |            1.000 |
| trim_5bp                 |      150 |                0.993 |           0.121 |            1.000 |
| trim_5bp                 |      300 |                0.997 |           0.078 |            1.000 |

## Best readout probes

| task                 | condition                |   length | representation      | classifier       |   mean_macro_f1 |   mean_accuracy |
|:---------------------|:-------------------------|---------:|:--------------------|:-----------------|----------------:|----------------:|
| target_background    | N_3pct                   |       69 | ck4                 | logistic         |           0.586 |           0.604 |
| target_background    | N_3pct                   |       75 | cspaced_property_l2 | nearest_centroid |           0.581 |           0.605 |
| target_background    | N_3pct                   |      100 | cspaced_property_l2 | nearest_centroid |           0.544 |           0.603 |
| target_background    | N_3pct                   |      150 | eiip_l2             | nearest_centroid |           0.549 |           0.580 |
| target_background    | clean                    |       69 | hybrid_ckmer5_csp   | nearest_centroid |           0.542 |           0.558 |
| target_background    | clean                    |       75 | eiip_l2             | logistic         |           0.583 |           0.637 |
| target_background    | clean                    |      100 | cspaced_count_l2    | logistic         |           0.555 |           0.616 |
| target_background    | clean                    |      150 | ck4p_msp            | logistic         |           0.538 |           0.617 |
| target_background    | substitution_1pct        |       69 | minhash_k5_s128     | logistic         |           0.585 |           0.624 |
| target_background    | substitution_1pct        |       75 | eiip_l2             | logistic         |           0.582 |           0.635 |
| target_background    | substitution_1pct        |      100 | cspaced_property_l2 | logistic         |           0.578 |           0.641 |
| target_background    | substitution_1pct        |      150 | eiip_l2             | logistic         |           0.544 |           0.618 |
| target_background    | substitution_1pct_N_3pct |       69 | minhash_k5_s128     | nearest_centroid |           0.546 |           0.586 |
| target_background    | substitution_1pct_N_3pct |       75 | eiip_l2             | logistic         |           0.596 |           0.643 |
| target_background    | substitution_1pct_N_3pct |      100 | cspaced_property_l2 | nearest_centroid |           0.557 |           0.603 |
| target_background    | substitution_1pct_N_3pct |      150 | eiip_l2             | logistic         |           0.570 |           0.627 |
| target_background    | trim_5bp                 |       69 | cspaced_property_l2 | logistic         |           0.544 |           0.566 |
| target_background    | trim_5bp                 |       75 | eiip_l2             | nearest_centroid |           0.577 |           0.615 |
| target_background    | trim_5bp                 |      100 | cspaced_property_l2 | logistic         |           0.561 |           0.642 |
| target_background    | trim_5bp                 |      150 | eiip_l2             | logistic         |           0.551 |           0.622 |
| within_genus_species | N_3pct                   |       69 | cspaced_property_l2 | logistic         |           0.393 |           0.403 |
| within_genus_species | N_3pct                   |       75 | minhash_k5_s128     | logistic         |           0.365 |           0.383 |
| within_genus_species | N_3pct                   |      100 | ckmer5_count_l2     | logistic         |           0.358 |           0.386 |
| within_genus_species | N_3pct                   |      150 | ck4p_msp            | nearest_centroid |           0.372 |           0.384 |
| within_genus_species | clean                    |       69 | ckmer5_count_l2     | nearest_centroid |           0.368 |           0.391 |
| within_genus_species | clean                    |       75 | eiip_l2             | logistic         |           0.392 |           0.402 |
| within_genus_species | clean                    |      100 | ck4                 | nearest_centroid |           0.360 |           0.369 |
| within_genus_species | clean                    |      150 | ck4                 | logistic         |           0.403 |           0.414 |
| within_genus_species | substitution_1pct        |       69 | hybrid_ckmer5_csp   | nearest_centroid |           0.375 |           0.404 |
| within_genus_species | substitution_1pct        |       75 | eiip_l2             | logistic         |           0.366 |           0.381 |
| within_genus_species | substitution_1pct        |      100 | hybrid_ckmer5_csp   | logistic         |           0.358 |           0.387 |
| within_genus_species | substitution_1pct        |      150 | ck4                 | nearest_centroid |           0.389 |           0.400 |
| within_genus_species | substitution_1pct_N_3pct |       69 | cspaced_property_l2 | logistic         |           0.335 |           0.356 |
| within_genus_species | substitution_1pct_N_3pct |       75 | eiip_l2             | logistic         |           0.362 |           0.372 |
| within_genus_species | substitution_1pct_N_3pct |      100 | eiip_summary_l2     | logistic         |           0.362 |           0.395 |
| within_genus_species | substitution_1pct_N_3pct |      150 | ck4_p               | logistic         |           0.387 |           0.401 |
| within_genus_species | trim_5bp                 |       69 | hybrid_ckmer5_csp   | nearest_centroid |           0.387 |           0.408 |
| within_genus_species | trim_5bp                 |       75 | eiip_l2             | logistic         |           0.342 |           0.353 |
| within_genus_species | trim_5bp                 |      100 | cspaced_count_l2    | logistic         |           0.377 |           0.389 |
| within_genus_species | trim_5bp                 |      150 | ck4                 | nearest_centroid |           0.397 |           0.409 |
