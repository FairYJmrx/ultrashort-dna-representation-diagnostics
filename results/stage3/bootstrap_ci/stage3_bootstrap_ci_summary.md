# Stage-3 Bootstrap CI Summary

Confidence intervals are analysis-cell bootstrap intervals. Stability cells are length-by-perturbation or length-by-quality strata; CAMI cells are task/length/condition/classifier readout rows. These intervals quantify robustness across the controlled analysis grid and should not be read as clinical sample-level uncertainty.

## Compact baseline stability

| representation_label   |   n_cells | paired cosine (95% CI)   | L2 drift (95% CI)    | top-1 retrieval (95% CI)   |   median_features |
|:-----------------------|----------:|:-------------------------|:---------------------|:---------------------------|------------------:|
| canonical 5-mer        |        36 | 0.951 [0.941, 0.961]     | 0.278 [0.243, 0.315] | 1.000 [1.000, 1.000]       |             512   |
| canonical 7-mer        |        36 | 0.915 [0.900, 0.931]     | 0.367 [0.325, 0.413] | 1.000 [1.000, 1.000]       |            7856   |
| canonical spaced count |        36 | 0.967 [0.959, 0.974]     | 0.224 [0.196, 0.256] | 1.000 [1.000, 1.000]       |             136   |
| CSP                    |        36 | 0.996 [0.995, 0.997]     | 0.079 [0.068, 0.090] | 1.000 [1.000, 1.000]       |             147   |
| canonical 5-mer + CSP  |        36 | 0.973 [0.968, 0.979]     | 0.205 [0.180, 0.230] | 1.000 [1.000, 1.000]       |             659   |
| MinHash k=5, s=128     |        36 | 0.951 [0.942, 0.960]     | 0.266 [0.234, 0.300] | 1.000 [0.999, 1.000]       |             128   |
| MinHash k=7, s=128     |        36 | 0.925 [0.911, 0.937]     | 0.338 [0.300, 0.381] | 0.999 [0.998, 1.000]       |             128   |
| EIIP positional signal |        36 | 0.988 [0.985, 0.991]     | 0.129 [0.105, 0.151] | 0.943 [0.901, 0.980]       |             112.5 |
| EIIP summary           |        36 | 0.979 [0.969, 0.988]     | 0.139 [0.093, 0.185] | 0.148 [0.082, 0.221]       |               8   |

## ART Illumina stability

| representation_label   |   n_cells | paired cosine (95% CI)   | L2 drift (95% CI)    | top-1 retrieval (95% CI)   |   median_features |
|:-----------------------|----------:|:-------------------------|:---------------------|:---------------------------|------------------:|
| canonical 5-mer        |         5 | 0.903 [0.836, 0.969]     | 0.340 [0.138, 0.542] | 1.000 [0.998, 1.000]       |               512 |
| canonical 7-mer        |         5 | 0.841 [0.733, 0.949]     | 0.439 [0.183, 0.695] | 1.000 [0.998, 1.000]       |              7906 |
| canonical spaced count |         5 | 0.943 [0.904, 0.981]     | 0.259 [0.104, 0.414] | 1.000 [0.998, 1.000]       |               136 |
| CSP                    |         5 | 0.994 [0.990, 0.998]     | 0.086 [0.035, 0.137] | 1.000 [1.000, 1.000]       |               147 |
| canonical 5-mer + CSP  |         5 | 0.949 [0.913, 0.984]     | 0.248 [0.101, 0.395] | 1.000 [1.000, 1.000]       |               659 |
| MinHash k=5, s=128     |         5 | 0.915 [0.857, 0.972]     | 0.319 [0.131, 0.513] | 0.972 [0.935, 0.996]       |               128 |
| EIIP positional signal |         5 | 0.998 [0.997, 0.999]     | 0.036 [0.014, 0.058] | 1.000 [0.998, 1.000]       |               100 |
| EIIP summary           |         5 | 0.999 [0.998, 1.000]     | 0.008 [0.004, 0.013] | 0.432 [0.154, 0.711]       |                 8 |

## ART quality-stratified CSP stability

| quality_bin   | representation_label   |   n_cells | paired cosine (95% CI)   | L2 drift (95% CI)    | top-1 retrieval (95% CI)   |
|:--------------|:-----------------------|----------:|:-------------------------|:---------------------|:---------------------------|
| high          | CSP                    |         5 | 0.995 [0.992, 0.999]     | 0.072 [0.025, 0.118] | 1.000 [1.000, 1.000]       |
| low           | CSP                    |         5 | 0.992 [0.987, 0.997]     | 0.099 [0.041, 0.158] | 1.000 [1.000, 1.000]       |
| mid           | CSP                    |         5 | 0.994 [0.990, 0.998]     | 0.085 [0.035, 0.136] | 1.000 [1.000, 1.000]       |

## CAMI_TOY_low macro-F1

| task              | representation_label   |   n_cells | macro-F1 (95% CI)    | accuracy (95% CI)    |   mean_features |
|:------------------|:-----------------------|----------:|:---------------------|:---------------------|----------------:|
| label_probe       | canonical 5-mer + CSP  |        27 | 0.245 [0.229, 0.263] | 0.255 [0.238, 0.272] |        659      |
| label_probe       | canonical 5-mer        |        27 | 0.237 [0.219, 0.255] | 0.248 [0.231, 0.266] |        512      |
| label_probe       | canonical 7-mer        |        27 | 0.181 [0.159, 0.202] | 0.195 [0.174, 0.217] |       8186.33   |
| label_probe       | canonical spaced count |        27 | 0.143 [0.134, 0.152] | 0.155 [0.145, 0.165] |        136      |
| label_probe       | CSP                    |        27 | 0.142 [0.130, 0.152] | 0.154 [0.142, 0.165] |        147      |
| label_probe       | MinHash k=5, s=128     |        27 | 0.123 [0.113, 0.132] | 0.133 [0.123, 0.143] |        128      |
| label_probe       | EIIP summary           |        27 | 0.070 [0.061, 0.079] | 0.102 [0.093, 0.111] |          8      |
| label_probe       | EIIP positional signal |        27 | 0.043 [0.038, 0.047] | 0.047 [0.042, 0.051] |         81.3333 |
| target_background | canonical spaced count |        27 | 0.749 [0.727, 0.769] | 0.752 [0.731, 0.772] |        136      |
| target_background | canonical 5-mer + CSP  |        27 | 0.734 [0.703, 0.764] | 0.745 [0.715, 0.771] |        658.778  |
| target_background | canonical 5-mer        |        27 | 0.716 [0.677, 0.755] | 0.732 [0.699, 0.763] |        511.778  |
| target_background | CSP                    |        27 | 0.700 [0.661, 0.737] | 0.708 [0.674, 0.739] |        147      |
| target_background | canonical 7-mer        |        27 | 0.697 [0.675, 0.717] | 0.703 [0.682, 0.723] |       5535      |
| target_background | EIIP summary           |        27 | 0.669 [0.626, 0.714] | 0.673 [0.631, 0.715] |          8      |
| target_background | MinHash k=5, s=128     |        27 | 0.616 [0.571, 0.658] | 0.633 [0.593, 0.668] |        128      |
| target_background | EIIP positional signal |        27 | 0.488 [0.467, 0.511] | 0.511 [0.488, 0.532] |         81.3333 |
