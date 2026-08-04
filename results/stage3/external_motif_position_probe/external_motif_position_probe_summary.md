# External motif-position probe summary

This is a grouped external readability probe using public Dorsal binding-site and CRM sequences.
The label is the relative position of a known site within a 50/75/100/150 bp window.
It is not a TFBS discovery, affinity, species classification or clinical validation task.

Source: https://doi.org/10.5061/dryad.8b203
Samples: 1125 windows; CRM groups: 32; lengths: [50, 75, 100, 150]

## Class counts

|   length |   left |   middle |   right |
|---------:|-------:|---------:|--------:|
|       50 |     96 |       96 |      96 |
|       75 |     93 |       93 |      93 |
|      100 |     93 |       93 |      93 |
|      150 |     93 |       93 |      93 |

## Grouped-CV results

|   length | representation   | classifier        |   mean_accuracy |   sd_accuracy |   mean_macro_f1 |   sd_macro_f1 |   n_features |   n_folds |
|---------:|:-----------------|:------------------|----------------:|--------------:|----------------:|--------------:|-------------:|----------:|
|       50 | ck4              | contract_logistic |           0.647 |         0.139 |           0.629 |         0.148 |          136 |         5 |
|       50 | ck4              | nearest_centroid  |           0.585 |         0.123 |           0.576 |         0.132 |          136 |         5 |
|       50 | ck4p_msp         | contract_logistic |           0.632 |         0.108 |           0.608 |         0.106 |          222 |         5 |
|       50 | ck4p_msp         | nearest_centroid  |           0.588 |         0.125 |           0.581 |         0.134 |          222 |         5 |
|       50 | ckmer5_count_l2  | contract_logistic |           0.681 |         0.086 |           0.677 |         0.082 |          397 |         5 |
|       50 | ckmer5_count_l2  | nearest_centroid  |           0.657 |         0.121 |           0.650 |         0.124 |          397 |         5 |
|       50 | msp              | contract_logistic |           0.568 |         0.072 |           0.567 |         0.071 |           75 |         5 |
|       50 | msp              | nearest_centroid  |           0.576 |         0.096 |           0.576 |         0.095 |           75 |         5 |
|       50 | p                | contract_logistic |           0.378 |         0.040 |           0.301 |         0.031 |           11 |         5 |
|       50 | p                | nearest_centroid  |           0.381 |         0.055 |           0.345 |         0.055 |           11 |         5 |
|       50 | p_msp            | contract_logistic |           0.579 |         0.089 |           0.577 |         0.088 |           86 |         5 |
|       50 | p_msp            | nearest_centroid  |           0.583 |         0.092 |           0.582 |         0.091 |           86 |         5 |
|       75 | ck4              | contract_logistic |           0.622 |         0.087 |           0.612 |         0.085 |          136 |         5 |
|       75 | ck4              | nearest_centroid  |           0.570 |         0.103 |           0.564 |         0.107 |          136 |         5 |
|       75 | ck4p_msp         | contract_logistic |           0.614 |         0.093 |           0.593 |         0.088 |          222 |         5 |
|       75 | ck4p_msp         | nearest_centroid  |           0.568 |         0.090 |           0.563 |         0.092 |          222 |         5 |
|       75 | ckmer5_count_l2  | contract_logistic |           0.683 |         0.089 |           0.673 |         0.094 |          461 |         5 |
|       75 | ckmer5_count_l2  | nearest_centroid  |           0.624 |         0.088 |           0.618 |         0.092 |          461 |         5 |
|       75 | msp              | contract_logistic |           0.561 |         0.100 |           0.549 |         0.108 |           75 |         5 |
|       75 | msp              | nearest_centroid  |           0.578 |         0.125 |           0.574 |         0.125 |           75 |         5 |
|       75 | p                | contract_logistic |           0.384 |         0.080 |           0.338 |         0.097 |           11 |         5 |
|       75 | p                | nearest_centroid  |           0.385 |         0.079 |           0.349 |         0.102 |           11 |         5 |
|       75 | p_msp            | contract_logistic |           0.548 |         0.074 |           0.534 |         0.081 |           86 |         5 |
|       75 | p_msp            | nearest_centroid  |           0.561 |         0.060 |           0.554 |         0.065 |           86 |         5 |
|      100 | ck4              | contract_logistic |           0.708 |         0.077 |           0.702 |         0.071 |          136 |         5 |
|      100 | ck4              | nearest_centroid  |           0.651 |         0.064 |           0.650 |         0.066 |          136 |         5 |
|      100 | ck4p_msp         | contract_logistic |           0.683 |         0.081 |           0.671 |         0.076 |          222 |         5 |
|      100 | ck4p_msp         | nearest_centroid  |           0.655 |         0.061 |           0.653 |         0.061 |          222 |         5 |
|      100 | ckmer5_count_l2  | contract_logistic |           0.690 |         0.068 |           0.677 |         0.064 |          482 |         5 |
|      100 | ckmer5_count_l2  | nearest_centroid  |           0.662 |         0.064 |           0.657 |         0.064 |          482 |         5 |
|      100 | msp              | contract_logistic |           0.511 |         0.066 |           0.507 |         0.070 |           75 |         5 |
|      100 | msp              | nearest_centroid  |           0.504 |         0.058 |           0.503 |         0.060 |           75 |         5 |
|      100 | p                | contract_logistic |           0.359 |         0.050 |           0.298 |         0.043 |           11 |         5 |
|      100 | p                | nearest_centroid  |           0.330 |         0.027 |           0.296 |         0.033 |           11 |         5 |
|      100 | p_msp            | contract_logistic |           0.472 |         0.060 |           0.460 |         0.065 |           86 |         5 |
|      100 | p_msp            | nearest_centroid  |           0.486 |         0.047 |           0.481 |         0.052 |           86 |         5 |
|      150 | ck4              | contract_logistic |           0.698 |         0.060 |           0.688 |         0.062 |          136 |         5 |
|      150 | ck4              | nearest_centroid  |           0.608 |         0.070 |           0.607 |         0.069 |          136 |         5 |
|      150 | ck4p_msp         | contract_logistic |           0.674 |         0.056 |           0.657 |         0.055 |          222 |         5 |
|      150 | ck4p_msp         | nearest_centroid  |           0.615 |         0.068 |           0.615 |         0.067 |          222 |         5 |
|      150 | ckmer5_count_l2  | contract_logistic |           0.730 |         0.060 |           0.718 |         0.064 |          504 |         5 |
|      150 | ckmer5_count_l2  | nearest_centroid  |           0.649 |         0.062 |           0.648 |         0.060 |          504 |         5 |
|      150 | msp              | contract_logistic |           0.463 |         0.079 |           0.455 |         0.082 |           75 |         5 |
|      150 | msp              | nearest_centroid  |           0.460 |         0.072 |           0.455 |         0.074 |           75 |         5 |
|      150 | p                | contract_logistic |           0.439 |         0.062 |           0.358 |         0.049 |           11 |         5 |
|      150 | p                | nearest_centroid  |           0.441 |         0.046 |           0.406 |         0.043 |           11 |         5 |
|      150 | p_msp            | contract_logistic |           0.454 |         0.076 |           0.440 |         0.081 |           86 |         5 |
|      150 | p_msp            | nearest_centroid  |           0.440 |         0.089 |           0.433 |         0.088 |           86 |         5 |

## Within-source label-permutation null

|   length | representation   | classifier        |   mean_accuracy |   sd_accuracy |   mean_macro_f1 |   sd_macro_f1 |   n_features |   n_folds |
|---------:|:-----------------|:------------------|----------------:|--------------:|----------------:|--------------:|-------------:|----------:|
|       50 | ck4              | contract_logistic |           0.330 |         0.040 |           0.322 |         0.041 |          136 |         5 |
|       50 | ck4              | nearest_centroid  |           0.319 |         0.053 |           0.304 |         0.054 |          136 |         5 |
|       50 | ck4p_msp         | contract_logistic |           0.335 |         0.053 |           0.324 |         0.054 |          222 |         5 |
|       50 | ck4p_msp         | nearest_centroid  |           0.313 |         0.054 |           0.300 |         0.054 |          222 |         5 |
|       50 | ckmer5_count_l2  | contract_logistic |           0.317 |         0.042 |           0.305 |         0.047 |          397 |         5 |
|       50 | ckmer5_count_l2  | nearest_centroid  |           0.317 |         0.050 |           0.302 |         0.049 |          397 |         5 |
|       50 | msp              | contract_logistic |           0.344 |         0.061 |           0.338 |         0.065 |           75 |         5 |
|       50 | msp              | nearest_centroid  |           0.346 |         0.058 |           0.342 |         0.060 |           75 |         5 |
|       50 | p                | contract_logistic |           0.339 |         0.040 |           0.301 |         0.040 |           11 |         5 |
|       50 | p                | nearest_centroid  |           0.336 |         0.037 |           0.304 |         0.039 |           11 |         5 |
|       50 | p_msp            | contract_logistic |           0.346 |         0.060 |           0.338 |         0.064 |           86 |         5 |
|       50 | p_msp            | nearest_centroid  |           0.349 |         0.061 |           0.343 |         0.063 |           86 |         5 |
|       75 | ck4              | contract_logistic |           0.333 |         0.042 |           0.318 |         0.043 |          136 |         5 |
|       75 | ck4              | nearest_centroid  |           0.345 |         0.046 |           0.331 |         0.049 |          136 |         5 |
|       75 | ck4p_msp         | contract_logistic |           0.342 |         0.047 |           0.328 |         0.046 |          222 |         5 |
|       75 | ck4p_msp         | nearest_centroid  |           0.348 |         0.045 |           0.334 |         0.047 |          222 |         5 |
|       75 | ckmer5_count_l2  | contract_logistic |           0.332 |         0.055 |           0.321 |         0.057 |          461 |         5 |
|       75 | ckmer5_count_l2  | nearest_centroid  |           0.340 |         0.063 |           0.327 |         0.063 |          461 |         5 |
|       75 | msp              | contract_logistic |           0.349 |         0.052 |           0.339 |         0.055 |           75 |         5 |
|       75 | msp              | nearest_centroid  |           0.350 |         0.057 |           0.341 |         0.058 |           75 |         5 |
|       75 | p                | contract_logistic |           0.343 |         0.040 |           0.314 |         0.055 |           11 |         5 |
|       75 | p                | nearest_centroid  |           0.341 |         0.039 |           0.313 |         0.053 |           11 |         5 |
|       75 | p_msp            | contract_logistic |           0.343 |         0.047 |           0.333 |         0.049 |           86 |         5 |
|       75 | p_msp            | nearest_centroid  |           0.340 |         0.048 |           0.331 |         0.050 |           86 |         5 |
|      100 | ck4              | contract_logistic |           0.362 |         0.056 |           0.345 |         0.057 |          136 |         5 |
|      100 | ck4              | nearest_centroid  |           0.357 |         0.051 |           0.346 |         0.056 |          136 |         5 |
|      100 | ck4p_msp         | contract_logistic |           0.349 |         0.057 |           0.334 |         0.058 |          222 |         5 |
|      100 | ck4p_msp         | nearest_centroid  |           0.355 |         0.053 |           0.345 |         0.058 |          222 |         5 |
|      100 | ckmer5_count_l2  | contract_logistic |           0.349 |         0.053 |           0.338 |         0.053 |          482 |         5 |
|      100 | ckmer5_count_l2  | nearest_centroid  |           0.349 |         0.048 |           0.337 |         0.051 |          482 |         5 |
|      100 | msp              | contract_logistic |           0.329 |         0.064 |           0.323 |         0.063 |           75 |         5 |
|      100 | msp              | nearest_centroid  |           0.330 |         0.069 |           0.325 |         0.069 |           75 |         5 |
|      100 | p                | contract_logistic |           0.330 |         0.043 |           0.296 |         0.051 |           11 |         5 |
|      100 | p                | nearest_centroid  |           0.330 |         0.036 |           0.299 |         0.043 |           11 |         5 |
|      100 | p_msp            | contract_logistic |           0.336 |         0.064 |           0.329 |         0.065 |           86 |         5 |
|      100 | p_msp            | nearest_centroid  |           0.339 |         0.065 |           0.334 |         0.066 |           86 |         5 |
|      150 | ck4              | contract_logistic |           0.357 |         0.070 |           0.346 |         0.075 |          136 |         5 |
|      150 | ck4              | nearest_centroid  |           0.358 |         0.043 |           0.348 |         0.049 |          136 |         5 |
|      150 | ck4p_msp         | contract_logistic |           0.369 |         0.067 |           0.359 |         0.072 |          222 |         5 |
|      150 | ck4p_msp         | nearest_centroid  |           0.357 |         0.041 |           0.347 |         0.046 |          222 |         5 |
|      150 | ckmer5_count_l2  | contract_logistic |           0.357 |         0.055 |           0.350 |         0.055 |          504 |         5 |
|      150 | ckmer5_count_l2  | nearest_centroid  |           0.357 |         0.068 |           0.346 |         0.071 |          504 |         5 |
|      150 | msp              | contract_logistic |           0.351 |         0.058 |           0.340 |         0.058 |           75 |         5 |
|      150 | msp              | nearest_centroid  |           0.353 |         0.060 |           0.343 |         0.060 |           75 |         5 |
|      150 | p                | contract_logistic |           0.350 |         0.035 |           0.322 |         0.044 |           11 |         5 |
|      150 | p                | nearest_centroid  |           0.353 |         0.042 |           0.333 |         0.044 |           11 |         5 |
|      150 | p_msp            | contract_logistic |           0.353 |         0.058 |           0.344 |         0.060 |           86 |         5 |
|      150 | p_msp            | nearest_centroid  |           0.354 |         0.057 |           0.346 |         0.059 |           86 |         5 |

Chance macro-F1 is 1/3 for the three-class position label.
A result above chance indicates external position-label readability under this probe; it does not establish general natural position semantics.
