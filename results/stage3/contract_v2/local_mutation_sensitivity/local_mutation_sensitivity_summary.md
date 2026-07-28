# Local Mutation Sensitivity Summary

This experiment compares equal-count random substitutions with local property-shift substitutions. A useful selective-sensitivity representation should keep random-noise distance low while making structured local mutation distance higher.

## Distance-based selective sensitivity

| representation   |   noise_l2 |   local_l2 |   local_minus_noise_l2 |   selective_sensitivity_ratio |   n_features |
|:-----------------|-----------:|-----------:|-----------------------:|------------------------------:|-------------:|
| ck4p_msp         |   0.205317 |   0.153979 |             -0.0513373 |                      0.752281 |          222 |
| ck4_msp          |   0.251414 |   0.188494 |             -0.0629205 |                      0.75206  |          211 |
| ck4_p            |   0.251122 |   0.187903 |             -0.0632189 |                      0.750621 |          147 |
| ck4              |   0.355074 |   0.265599 |             -0.0894754 |                      0.750383 |          136 |

## Delta-readout: random noise versus local property shift

| representation   | classifier       |   macro_f1 |   accuracy |   n_features |
|:-----------------|:-----------------|-----------:|-----------:|-------------:|
| ck4p_msp         | logistic         |   0.97863  |   0.978667 |          222 |
| ck4_msp          | logistic         |   0.977974 |   0.978    |          211 |
| ck4_p            | logistic         |   0.904311 |   0.9045   |          147 |
| ck4              | logistic         |   0.8923   |   0.8925   |          136 |
| ck4_msp          | nearest_centroid |   0.888365 |   0.889    |          211 |
| ck4p_msp         | nearest_centroid |   0.888365 |   0.889    |          222 |
| ck4              | nearest_centroid |   0.879694 |   0.880333 |          136 |
| ck4_p            | nearest_centroid |   0.87969  |   0.880333 |          147 |

## Interpretation

- `selective_sensitivity_ratio > 1` means the representation moved farther for local property-shift mutations than for equal-count random substitutions.
- High macro-F1 in the delta-readout means a shallow model can distinguish local biochemical/positional change from random noise using representation deltas.
- These metrics complement perturbation stability: they test selective sensitivity rather than invariance.
