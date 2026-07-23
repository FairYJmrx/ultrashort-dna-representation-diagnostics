# Stage-2 Representation Grid Summary

This run compares exact canonical k-mer evidence, canonical spaced counts, CSP and hybrid features under short-read perturbations.

## Best perturbation stability by condition and length

| condition                |   length | representation     |   paired_cosine_mean |   l2_delta_mean |   retrieval_top1 |   n_features |   density |
|:-------------------------|---------:|:-------------------|---------------------:|----------------:|-----------------:|-------------:|----------:|
| N_3pct                   |       69 | ckmer4_property_l2 |                0.994 |           0.105 |            1.000 |          147 |     0.386 |
| N_3pct                   |       75 | ckmer4_property_l2 |                0.995 |           0.098 |            1.000 |          147 |     0.404 |
| N_3pct                   |      100 | ckmer4_property_l2 |                0.995 |           0.101 |            1.000 |          147 |     0.477 |
| N_3pct                   |      150 | ckmer4_property_l2 |                0.996 |           0.085 |            1.000 |          147 |     0.595 |
| local_mismatch_6bp       |       69 | ckmer4_property_l2 |                0.991 |           0.132 |            1.000 |          147 |     0.400 |
| local_mismatch_6bp       |       75 | ckmer4_property_l2 |                0.992 |           0.122 |            1.000 |          147 |     0.416 |
| local_mismatch_6bp       |      100 | ckmer4_property_l2 |                0.995 |           0.098 |            1.000 |          147 |     0.493 |
| local_mismatch_6bp       |      150 | ckmer4_property_l2 |                0.998 |           0.070 |            1.000 |          147 |     0.611 |
| short_indel              |       69 | ckmer4_property_l2 |                0.998 |           0.040 |            1.000 |          147 |     0.398 |
| short_indel              |       75 | ckmer4_property_l2 |                0.998 |           0.040 |            1.000 |          147 |     0.413 |
| short_indel              |      100 | ckmer4_property_l2 |                0.999 |           0.040 |            1.000 |          147 |     0.490 |
| short_indel              |      150 | ckmer4_property_l2 |                0.999 |           0.040 |            1.000 |          147 |     0.608 |
| substitution_1pct        |       69 | ckmer4_property_l2 |                0.997 |           0.050 |            1.000 |          147 |     0.398 |
| substitution_1pct        |       75 | ckmer4_property_l2 |                0.998 |           0.049 |            1.000 |          147 |     0.414 |
| substitution_1pct        |      100 | ckmer4_property_l2 |                0.998 |           0.050 |            1.000 |          147 |     0.491 |
| substitution_1pct        |      150 | ckmer4_property_l2 |                0.998 |           0.048 |            1.000 |          147 |     0.608 |
| substitution_1pct_N_3pct |       69 | ckmer4_property_l2 |                0.992 |           0.127 |            1.000 |          147 |     0.387 |
| substitution_1pct_N_3pct |       75 | ckmer4_property_l2 |                0.993 |           0.118 |            1.000 |          147 |     0.404 |
| substitution_1pct_N_3pct |      100 | ckmer4_property_l2 |                0.993 |           0.117 |            1.000 |          147 |     0.478 |
| substitution_1pct_N_3pct |      150 | ckmer4_property_l2 |                0.995 |           0.102 |            1.000 |          147 |     0.595 |
| trim_5bp                 |       69 | ckmer4_property_l2 |                0.997 |           0.071 |            1.000 |          147 |     0.388 |
| trim_5bp                 |       75 | ckmer4_property_l2 |                0.998 |           0.066 |            1.000 |          147 |     0.405 |
| trim_5bp                 |      100 | ckmer4_property_l2 |                0.999 |           0.053 |            1.000 |          147 |     0.483 |
| trim_5bp                 |      150 | ckmer4_property_l2 |                0.999 |           0.038 |            1.000 |          147 |     0.602 |

## Best readout probes

| task                 | condition                |   length | representation      | classifier       |   mean_macro_f1 |   mean_accuracy |
|:---------------------|:-------------------------|---------:|:--------------------|:-----------------|----------------:|----------------:|
| target_background    | N_3pct                   |       69 | ckmer4_count_l2     | logistic         |           0.586 |           0.604 |
| target_background    | N_3pct                   |       75 | cspaced_property_l2 | nearest_centroid |           0.581 |           0.605 |
| target_background    | N_3pct                   |      100 | cspaced_property_l2 | nearest_centroid |           0.544 |           0.603 |
| target_background    | N_3pct                   |      150 | ck4p_msp            | logistic         |           0.527 |           0.584 |
| target_background    | clean                    |       69 | ckmer5_count_l2     | logistic         |           0.535 |           0.622 |
| target_background    | clean                    |       75 | cspaced_property_l2 | nearest_centroid |           0.553 |           0.589 |
| target_background    | clean                    |      100 | cspaced_property_l2 | logistic         |           0.545 |           0.608 |
| target_background    | clean                    |      150 | ck4p_msp            | logistic         |           0.538 |           0.617 |
| target_background    | substitution_1pct        |       69 | cspaced_property_l2 | logistic         |           0.537 |           0.577 |
| target_background    | substitution_1pct        |       75 | cspaced_property_l2 | nearest_centroid |           0.568 |           0.604 |
| target_background    | substitution_1pct        |      100 | cspaced_property_l2 | logistic         |           0.578 |           0.641 |
| target_background    | substitution_1pct        |      150 | ck4p_msp            | logistic         |           0.536 |           0.622 |
| target_background    | substitution_1pct_N_3pct |       69 | ckmer5_count_l2     | logistic         |           0.534 |           0.600 |
| target_background    | substitution_1pct_N_3pct |       75 | ck4p_msp            | logistic         |           0.531 |           0.589 |
| target_background    | substitution_1pct_N_3pct |      100 | cspaced_property_l2 | nearest_centroid |           0.557 |           0.603 |
| target_background    | substitution_1pct_N_3pct |      150 | cspaced_property_l2 | logistic         |           0.565 |           0.606 |
| target_background    | trim_5bp                 |       69 | cspaced_property_l2 | logistic         |           0.544 |           0.566 |
| target_background    | trim_5bp                 |       75 | cspaced_property_l2 | nearest_centroid |           0.544 |           0.577 |
| target_background    | trim_5bp                 |      100 | cspaced_property_l2 | logistic         |           0.561 |           0.642 |
| target_background    | trim_5bp                 |      150 | ck4p_msp            | logistic         |           0.522 |           0.613 |
| within_genus_species | N_3pct                   |       69 | cspaced_property_l2 | logistic         |           0.393 |           0.403 |
| within_genus_species | N_3pct                   |       75 | ckmer4_property_l2  | nearest_centroid |           0.317 |           0.342 |
| within_genus_species | N_3pct                   |      100 | ckmer5_count_l2     | logistic         |           0.358 |           0.386 |
| within_genus_species | N_3pct                   |      150 | ck4p_msp            | nearest_centroid |           0.372 |           0.384 |
| within_genus_species | clean                    |       69 | ckmer5_count_l2     | nearest_centroid |           0.368 |           0.391 |
| within_genus_species | clean                    |       75 | ckmer4_count_l2     | nearest_centroid |           0.337 |           0.366 |
| within_genus_species | clean                    |      100 | ckmer4_count_l2     | nearest_centroid |           0.360 |           0.369 |
| within_genus_species | clean                    |      150 | ckmer4_count_l2     | logistic         |           0.403 |           0.414 |
| within_genus_species | substitution_1pct        |       69 | ckmer4_property_l2  | logistic         |           0.370 |           0.391 |
| within_genus_species | substitution_1pct        |       75 | cspaced_property_l2 | logistic         |           0.339 |           0.353 |
| within_genus_species | substitution_1pct        |      100 | ck4p_msp            | nearest_centroid |           0.350 |           0.358 |
| within_genus_species | substitution_1pct        |      150 | ckmer4_count_l2     | nearest_centroid |           0.389 |           0.400 |
| within_genus_species | substitution_1pct_N_3pct |       69 | cspaced_property_l2 | logistic         |           0.335 |           0.356 |
| within_genus_species | substitution_1pct_N_3pct |       75 | cspaced_property_l2 | nearest_centroid |           0.338 |           0.347 |
| within_genus_species | substitution_1pct_N_3pct |      100 | ck4p_msp            | logistic         |           0.352 |           0.363 |
| within_genus_species | substitution_1pct_N_3pct |      150 | ckmer4_property_l2  | logistic         |           0.396 |           0.410 |
| within_genus_species | trim_5bp                 |       69 | ckmer5_count_l2     | nearest_centroid |           0.364 |           0.375 |
| within_genus_species | trim_5bp                 |       75 | cspaced_property_l2 | logistic         |           0.337 |           0.343 |
| within_genus_species | trim_5bp                 |      100 | cspaced_property_l2 | logistic         |           0.371 |           0.381 |
| within_genus_species | trim_5bp                 |      150 | ckmer4_count_l2     | nearest_centroid |           0.397 |           0.409 |
