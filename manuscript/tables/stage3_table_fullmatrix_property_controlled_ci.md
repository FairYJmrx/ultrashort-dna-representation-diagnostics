| task                  | representation_label       |   n_cells | macro-F1 (95% CI)    | accuracy (95% CI)    |   mean_features |
|:----------------------|:---------------------------|----------:|:---------------------|:---------------------|----------------:|
| motif_jitter_position | position k-mer property    |         4 | 0.592 [0.578, 0.610] | 0.596 [0.582, 0.614] |          1288   |
| motif_jitter_position | RoPE one-hot               |         4 | 0.541 [0.518, 0.564] | 0.544 [0.521, 0.567] |          1352   |
| motif_jitter_position | one-hot + property matrix  |         4 | 0.528 [0.487, 0.556] | 0.532 [0.493, 0.560] |           845   |
| motif_jitter_position | position one-hot           |         4 | 0.528 [0.488, 0.568] | 0.533 [0.494, 0.573] |           422.5 |
| motif_jitter_position | RoPE property              |         4 | 0.527 [0.483, 0.567] | 0.532 [0.494, 0.571] |          1352   |
| motif_jitter_position | position property channels |         4 | 0.509 [0.483, 0.535] | 0.514 [0.489, 0.537] |           422.5 |
| motif_jitter_position | CK4+P multi-scale mean     |         4 | 0.399 [0.367, 0.436] | 0.403 [0.367, 0.439] |           222   |
| motif_jitter_position | canonical 5-mer            |         4 | 0.342 [0.321, 0.368] | 0.345 [0.325, 0.370] |           512   |
| same_spectrum_order   | canonical 5-mer            |         4 | 0.992 [0.984, 1.000] | 0.992 [0.984, 1.000] |           201   |
| same_spectrum_order   | RoPE one-hot               |         4 | 0.992 [0.989, 0.994] | 0.992 [0.989, 0.994] |          1352   |
| same_spectrum_order   | RoPE property              |         4 | 0.991 [0.987, 0.994] | 0.991 [0.988, 0.994] |          1352   |
| same_spectrum_order   | position one-hot           |         4 | 0.989 [0.983, 0.994] | 0.989 [0.984, 0.994] |           422.5 |
| same_spectrum_order   | CK4+P multi-scale mean     |         4 | 0.989 [0.977, 1.000] | 0.989 [0.977, 1.000] |           193   |
| same_spectrum_order   | one-hot + property matrix  |         4 | 0.984 [0.978, 0.987] | 0.984 [0.978, 0.988] |           845   |
| same_spectrum_order   | position property channels |         4 | 0.977 [0.962, 0.986] | 0.977 [0.962, 0.986] |           422.5 |
| same_spectrum_order   | position k-mer property    |         4 | 0.969 [0.950, 0.987] | 0.969 [0.950, 0.988] |          1288   |