# Stage-3 CAMI Low-complexity Probe Summary

This analysis treats CAMI as an external lightweight readout probe, not as an end-to-end clinical classifier benchmark.

## Best readout by task, condition and length

| task              | condition         |   length | representation                     |   mean_macro_f1 |   mean_accuracy |   mean_features |
|:------------------|:------------------|---------:|:-----------------------------------|----------------:|----------------:|----------------:|
| label_probe       | N_3pct            |       69 | ckmer4_property_l2                 |           0.231 |           0.246 |         147.000 |
| label_probe       | N_3pct            |       75 | ckmer4_property_l2                 |           0.253 |           0.268 |         147.000 |
| label_probe       | N_3pct            |      100 | ckmer5_property_multiscale_l2      |           0.270 |           0.275 |         673.000 |
| label_probe       | clean             |       69 | ckmer4_count_l2                    |           0.234 |           0.251 |         136.000 |
| label_probe       | clean             |       75 | ckmer4_property_moment_l2          |           0.263 |           0.276 |         187.000 |
| label_probe       | clean             |      100 | ckmer5_property_multiscale_l2      |           0.302 |           0.309 |         673.000 |
| label_probe       | substitution_1pct |       69 | ckmer4_property_l2                 |           0.235 |           0.248 |         147.000 |
| label_probe       | substitution_1pct |       75 | ckmer4_property_moment_l2          |           0.254 |           0.268 |         187.000 |
| label_probe       | substitution_1pct |      100 | ckmer5_property_multiscale_l2      |           0.289 |           0.297 |         673.000 |
| target_background | N_3pct            |       69 | ckmer4_property_multiscale_mean_l2 |           0.792 |           0.792 |         222.000 |
| target_background | N_3pct            |       75 | ckmer5_property_multiscale_l2      |           0.795 |           0.799 |         672.000 |
| target_background | N_3pct            |      100 | ckmer4_property_multiscale_l2      |           0.692 |           0.694 |         297.000 |
| target_background | clean             |       69 | ckmer5_property_multiscale_l2      |           0.826 |           0.826 |         672.000 |
| target_background | clean             |       75 | ckmer5_property_multiscale_l2      |           0.809 |           0.812 |         672.000 |
| target_background | clean             |      100 | ckmer4_property_multiscale_l2      |           0.760 |           0.764 |         297.000 |
| target_background | substitution_1pct |       69 | ckmer4_property_multiscale_l2      |           0.812 |           0.812 |         297.000 |
| target_background | substitution_1pct |       75 | ckmer4_property_multiscale_mean_l2 |           0.795 |           0.799 |         222.000 |
| target_background | substitution_1pct |      100 | ckmer4_property_multiscale_l2      |           0.760 |           0.764 |         297.000 |