# Full-Matrix Property Contribution Bootstrap CI Summary

Confidence intervals are analysis-cell bootstrap intervals. They quantify stability of the lightweight screen across length, condition and classifier cells, not clinical population uncertainty.

## Controlled position/order readout

| task                  | representation_label       |   n_cells | macro-F1 (95% CI)    | accuracy (95% CI)    |   mean_features |
|:----------------------|:---------------------------|----------:|:---------------------|:---------------------|----------------:|
| motif_jitter_position | position k-mer property    |         4 | 0.592 [0.578, 0.610] | 0.596 [0.582, 0.614] |          1288   |
| motif_jitter_position | RoPE one-hot               |         4 | 0.541 [0.518, 0.564] | 0.544 [0.521, 0.567] |          1352   |
| motif_jitter_position | one-hot + property matrix  |         4 | 0.528 [0.487, 0.556] | 0.532 [0.493, 0.560] |           845   |
| motif_jitter_position | position one-hot           |         4 | 0.528 [0.488, 0.568] | 0.533 [0.494, 0.573] |           422.5 |
| motif_jitter_position | RoPE property              |         4 | 0.527 [0.483, 0.567] | 0.532 [0.494, 0.571] |          1352   |
| motif_jitter_position | position property channels |         4 | 0.509 [0.483, 0.535] | 0.514 [0.489, 0.537] |           422.5 |
| motif_jitter_position | CK4P-MSP                   |         4 | 0.399 [0.367, 0.436] | 0.403 [0.367, 0.439] |           222   |
| motif_jitter_position | canonical 5-mer            |         4 | 0.342 [0.321, 0.368] | 0.345 [0.325, 0.370] |           512   |
| same_spectrum_order   | canonical 5-mer            |         4 | 0.992 [0.984, 1.000] | 0.992 [0.984, 1.000] |           201   |
| same_spectrum_order   | RoPE one-hot               |         4 | 0.992 [0.989, 0.994] | 0.992 [0.989, 0.994] |          1352   |
| same_spectrum_order   | RoPE property              |         4 | 0.991 [0.987, 0.994] | 0.991 [0.988, 0.994] |          1352   |
| same_spectrum_order   | position one-hot           |         4 | 0.989 [0.983, 0.994] | 0.989 [0.984, 0.994] |           422.5 |
| same_spectrum_order   | CK4P-MSP                   |         4 | 0.989 [0.977, 1.000] | 0.989 [0.977, 1.000] |           193   |
| same_spectrum_order   | one-hot + property matrix  |         4 | 0.984 [0.978, 0.987] | 0.984 [0.978, 0.988] |           845   |
| same_spectrum_order   | position property channels |         4 | 0.977 [0.962, 0.986] | 0.977 [0.962, 0.986] |           422.5 |
| same_spectrum_order   | position k-mer property    |         4 | 0.969 [0.950, 0.987] | 0.969 [0.950, 0.988] |          1288   |

## Controlled paired deltas

| task                  | contrast                        |   n_paired_cells | delta macro_f1 (95% CI)   | delta accuracy (95% CI)   | interpretation                                                                  |
|:----------------------|:--------------------------------|-----------------:|:--------------------------|:--------------------------|:--------------------------------------------------------------------------------|
| motif_jitter_position | property_channels - one_hot     |                4 | -0.019 [-0.058, 0.023]    | -0.020 [-0.058, 0.021]    | per-position biochemical property channels versus per-position base identity    |
| motif_jitter_position | base_property - one_hot         |                4 | 0.000 [-0.021, 0.029]     | -0.001 [-0.021, 0.026]    | adding property channels to one-hot positional identity                         |
| motif_jitter_position | rope_property - rope_onehot     |                4 | -0.014 [-0.031, 0.003]    | -0.011 [-0.027, 0.004]    | property semantics under the same RoPE-like positional transform                |
| motif_jitter_position | kmer_property - ckmer5_count_l2 |                4 | 0.250 [0.241, 0.259]      | 0.251 [0.242, 0.260]      | position-resolved k-mer property sequence versus compact canonical k-mer counts |
| same_spectrum_order   | property_channels - one_hot     |                4 | -0.013 [-0.022, -0.003]   | -0.013 [-0.022, -0.003]   | per-position biochemical property channels versus per-position base identity    |
| same_spectrum_order   | base_property - one_hot         |                4 | -0.005 [-0.006, -0.002]   | -0.005 [-0.006, -0.002]   | adding property channels to one-hot positional identity                         |
| same_spectrum_order   | rope_property - rope_onehot     |                4 | -0.002 [-0.005, 0.000]    | -0.002 [-0.005, 0.000]    | property semantics under the same RoPE-like positional transform                |
| same_spectrum_order   | kmer_property - ckmer5_count_l2 |                4 | -0.023 [-0.041, -0.006]   | -0.023 [-0.041, -0.006]   | position-resolved k-mer property sequence versus compact canonical k-mer counts |

## ART stability

| representation_label       |   n_cells | paired cosine (95% CI)   | L2 drift (95% CI)    | top-1 retrieval (95% CI)   |   mean_features |
|:---------------------------|----------:|:-------------------------|:---------------------|:---------------------------|----------------:|
| position property channels |         2 | 0.993 [0.991, 0.995]     | 0.109 [0.087, 0.130] | 1.000 [1.000, 1.000]       |           422.5 |
| CK4P-MSP                   |         2 | 0.991 [0.989, 0.993]     | 0.126 [0.109, 0.143] | 1.000 [1.000, 1.000]       |           222   |
| position k-mer property    |         2 | 0.974 [0.966, 0.981]     | 0.214 [0.173, 0.254] | 1.000 [1.000, 1.000]       |          1288   |
| one-hot + property matrix  |         2 | 0.968 [0.958, 0.978]     | 0.238 [0.192, 0.284] | 1.000 [1.000, 1.000]       |           845   |
| RoPE property              |         2 | 0.961 [0.949, 0.973]     | 0.261 [0.211, 0.312] | 1.000 [1.000, 1.000]       |          1352   |
| RoPE one-hot               |         2 | 0.950 [0.935, 0.965]     | 0.296 [0.238, 0.354] | 1.000 [1.000, 1.000]       |          1352   |
| position one-hot           |         2 | 0.949 [0.934, 0.965]     | 0.298 [0.239, 0.358] | 1.000 [1.000, 1.000]       |           422.5 |
| canonical 5-mer            |         2 | 0.834 [0.794, 0.874]     | 0.540 [0.454, 0.626] | 1.000 [1.000, 1.000]       |           512   |

## ART paired deltas

| contrast                        |   n_paired_cells | delta paired_cosine_mean (95% CI)   | delta l2_delta_mean (95% CI)   | delta retrieval_top1 (95% CI)   | interpretation                                                                  |
|:--------------------------------|-----------------:|:------------------------------------|:-------------------------------|:--------------------------------|:--------------------------------------------------------------------------------|
| property_channels - one_hot     |                2 | 0.044 [0.030, 0.058]                | -0.190 [-0.228, -0.152]        | 0.000 [0.000, 0.000]            | per-position biochemical property channels versus per-position base identity    |
| base_property - one_hot         |                2 | 0.018 [0.012, 0.025]                | -0.061 [-0.074, -0.047]        | 0.000 [0.000, 0.000]            | adding property channels to one-hot positional identity                         |
| rope_property - rope_onehot     |                2 | 0.011 [0.007, 0.015]                | -0.035 [-0.043, -0.027]        | 0.000 [0.000, 0.000]            | property semantics under the same RoPE-like positional transform                |
| kmer_property - ckmer5_count_l2 |                2 | 0.139 [0.107, 0.172]                | -0.327 [-0.372, -0.281]        | 0.000 [0.000, 0.000]            | position-resolved k-mer property sequence versus compact canonical k-mer counts |

## CAMI target/background readout

| representation_label       |   n_cells | macro-F1 (95% CI)    | accuracy (95% CI)    |   mean_features |
|:---------------------------|----------:|:---------------------|:---------------------|----------------:|
| canonical 5-mer            |         8 | 0.747 [0.625, 0.865] | 0.757 [0.639, 0.875] |          509.75 |
| CK4P-MSP                   |         8 | 0.731 [0.589, 0.871] | 0.743 [0.611, 0.875] |          222    |
| position k-mer property    |         8 | 0.663 [0.522, 0.804] | 0.667 [0.528, 0.806] |         1288    |
| position property channels |         8 | 0.616 [0.517, 0.714] | 0.618 [0.521, 0.709] |          422.5  |
| RoPE one-hot               |         8 | 0.595 [0.473, 0.715] | 0.597 [0.472, 0.722] |         1352    |
| one-hot + property matrix  |         8 | 0.576 [0.451, 0.701] | 0.576 [0.451, 0.702] |          845    |
| position one-hot           |         8 | 0.568 [0.436, 0.694] | 0.569 [0.444, 0.701] |          422.5  |
| RoPE property              |         8 | 0.565 [0.408, 0.721] | 0.569 [0.424, 0.722] |         1352    |

## CAMI paired deltas

| contrast                        |   n_paired_cells | delta macro_f1 (95% CI)   | delta accuracy (95% CI)   | interpretation                                                                  |
|:--------------------------------|-----------------:|:--------------------------|:--------------------------|:--------------------------------------------------------------------------------|
| property_channels - one_hot     |                8 | 0.048 [0.006, 0.085]      | 0.049 [0.007, 0.090]      | per-position biochemical property channels versus per-position base identity    |
| base_property - one_hot         |                8 | 0.008 [-0.031, 0.049]     | 0.007 [-0.028, 0.049]     | adding property channels to one-hot positional identity                         |
| rope_property - rope_onehot     |                8 | -0.030 [-0.079, 0.014]    | -0.028 [-0.076, 0.014]    | property semantics under the same RoPE-like positional transform                |
| kmer_property - ckmer5_count_l2 |                8 | -0.085 [-0.134, -0.031]   | -0.090 [-0.146, -0.035]   | position-resolved k-mer property sequence versus compact canonical k-mer counts |

## Interpretation boundary

- Full-matrix position encodings are retained as high-resolution position-readable diagnostics, not as the main method.
- A positive property-channel stability delta supports a biochemical-property contribution under perturbation.
- CAMI target/background readout remains a small external probe; it should not be described as clinical classification performance.