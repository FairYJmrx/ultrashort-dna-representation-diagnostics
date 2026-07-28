# kNN/KSG-style MI robustness audit

This audit estimates MI between low-dimensional continuous perturbation-distance summaries and the local-vs-noise perturbation label using a k-nearest-neighbor mixed continuous/discrete estimator. It is a robustness check for the earlier discretized MI proxy, not an absolute information-theoretic proof over the full representation space.

## Summary

| feature_set              |   n_cells |   mean_knn_mi_bits |   median_knn_mi_bits |   mean_perm_p |   mean_subsample_ci_low |   mean_subsample_ci_high |
|:-------------------------|----------:|-------------------:|---------------------:|--------------:|------------------------:|-------------------------:|
| dK_dP_dM                 |        12 |             0.8892 |               0.9272 |        0.0099 |                  0.8676 |                   0.9083 |
| dK_dM                    |        12 |             0.8625 |               0.8995 |        0.0099 |                  0.8404 |                   0.8861 |
| dK_dP                    |        12 |             0.8326 |               0.8993 |        0.0099 |                  0.8078 |                   0.8613 |
| dK                       |        12 |             0.7516 |               0.8252 |        0.0099 |                  0.7261 |                   0.7905 |
| dP_dM                    |        12 |             0.7187 |               0.7116 |        0.0099 |                  0.6758 |                   0.7438 |
| dM                       |        12 |             0.4628 |               0.4513 |        0.0099 |                  0.4255 |                   0.5067 |
| dP                       |        12 |             0.4234 |               0.4303 |        0.0099 |                  0.3885 |                   0.4642 |
| increment_dP_dM_given_dK |        12 |             0.1376 |               0.0919 |      nan      |                nan      |                 nan      |
