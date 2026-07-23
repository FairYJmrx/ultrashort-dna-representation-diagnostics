# Local Mutation Sensitivity Summary

This experiment compares equal-count random substitutions with local property-shift substitutions. A useful selective-sensitivity representation should keep random-noise distance low while making structured local mutation distance higher.

## Distance-based selective sensitivity

| representation      |   noise_l2 |   local_l2 |   local_minus_noise_l2 |   selective_sensitivity_ratio |   n_features |
|:--------------------|-----------:|-----------:|-----------------------:|------------------------------:|-------------:|
| property_channels   |  0.0863179 |   0.106509 |             0.0201912  |                      1.25469  |      531.667 |
| kmer_property       |  0.167487  |   0.184504 |             0.0170172  |                      1.12545  |     1637.33  |
| base_property       |  0.188251  |   0.206961 |             0.0187093  |                      1.10144  |     1063.33  |
| one_hot             |  0.238887  |   0.238887 |             0          |                      1        |      531.667 |
| cspaced_property_l2 |  0.115692  |   0.10933  |            -0.00636159 |                      0.946862 |      147     |
| ckmer4_property_l2  |  0.115199  |   0.086462 |            -0.0287368  |                      0.75234  |      147     |
| ck4p_msp            |  0.205317  |   0.153979 |            -0.0513373  |                      0.752281 |      222     |
| ckmer4_count_l2     |  0.355074  |   0.265599 |            -0.0894754  |                      0.750383 |      136     |

## Delta-readout: random noise versus local property shift

| representation      | classifier       |   macro_f1 |   accuracy |   n_features |
|:--------------------|:-----------------|-----------:|-----------:|-------------:|
| property_channels   | logistic         |   0.98361  |   0.983667 |      531.667 |
| ck4p_msp            | logistic         |   0.97863  |   0.978667 |      222     |
| base_property       | logistic         |   0.975009 |   0.975167 |     1063.33  |
| kmer_property       | logistic         |   0.973134 |   0.973167 |     1637.33  |
| property_channels   | nearest_centroid |   0.965609 |   0.965667 |      531.667 |
| one_hot             | logistic         |   0.958137 |   0.958667 |      531.667 |
| base_property       | nearest_centroid |   0.955931 |   0.956    |     1063.33  |
| one_hot             | nearest_centroid |   0.937136 |   0.937333 |      531.667 |
| ckmer4_property_l2  | logistic         |   0.898463 |   0.898667 |      147     |
| ckmer4_count_l2     | logistic         |   0.8923   |   0.8925   |      136     |
| ck4p_msp            | nearest_centroid |   0.888365 |   0.889    |      222     |
| kmer_property       | nearest_centroid |   0.885652 |   0.8865   |     1637.33  |
| ckmer4_count_l2     | nearest_centroid |   0.879694 |   0.880333 |      136     |
| ckmer4_property_l2  | nearest_centroid |   0.87732  |   0.878    |      147     |
| cspaced_property_l2 | logistic         |   0.69707  |   0.697667 |      147     |
| cspaced_property_l2 | nearest_centroid |   0.658485 |   0.659333 |      147     |

## Interpretation

- `selective_sensitivity_ratio > 1` means the representation moved farther for local property-shift mutations than for equal-count random substitutions.
- High macro-F1 in the delta-readout means a shallow model can distinguish local biochemical/positional change from random noise using representation deltas.
- These metrics complement perturbation stability: they test selective sensitivity rather than invariance.
