# Stage-3 CAMI Low-complexity Probe Summary

This analysis treats CAMI as an external lightweight readout probe, not as an end-to-end clinical classifier benchmark.

## Best readout by task, condition and length

| task              | condition         |   length | representation    |   mean_macro_f1 |   mean_accuracy |   mean_features |
|:------------------|:------------------|---------:|:------------------|----------------:|----------------:|----------------:|
| label_probe       | N_3pct            |       69 | hybrid_ckmer5_csp |           0.204 |           0.214 |         659.000 |
| label_probe       | N_3pct            |       75 | hybrid_ckmer5_csp |           0.242 |           0.256 |         659.000 |
| label_probe       | N_3pct            |      100 | hybrid_ckmer5_csp |           0.276 |           0.282 |         659.000 |
| label_probe       | clean             |       69 | hybrid_ckmer5_csp |           0.213 |           0.225 |         659.000 |
| label_probe       | clean             |       75 | hybrid_ckmer5_csp |           0.247 |           0.263 |         659.000 |
| label_probe       | clean             |      100 | hybrid_ckmer5_csp |           0.300 |           0.304 |         659.000 |
| label_probe       | substitution_1pct |       69 | ckmer5_count_l2   |           0.205 |           0.215 |         512.000 |
| label_probe       | substitution_1pct |       75 | hybrid_ckmer5_csp |           0.233 |           0.248 |         659.000 |
| label_probe       | substitution_1pct |      100 | hybrid_ckmer5_csp |           0.293 |           0.297 |         659.000 |
| target_background | N_3pct            |       69 | cspaced_count_l2  |           0.812 |           0.812 |         136.000 |
| target_background | N_3pct            |       75 | hybrid_ckmer5_csp |           0.752 |           0.757 |         658.000 |
| target_background | N_3pct            |      100 | cspaced_count_l2  |           0.714 |           0.715 |         136.000 |
| target_background | clean             |       69 | cspaced_count_l2  |           0.819 |           0.819 |         136.000 |
| target_background | clean             |       75 | hybrid_ckmer5_csp |           0.773 |           0.778 |         658.000 |
| target_background | clean             |      100 | cspaced_count_l2  |           0.727 |           0.729 |         136.000 |
| target_background | substitution_1pct |       69 | cspaced_count_l2  |           0.784 |           0.785 |         136.000 |
| target_background | substitution_1pct |       75 | ckmer5_count_l2   |           0.771 |           0.778 |         512.000 |
| target_background | substitution_1pct |      100 | cspaced_count_l2  |           0.727 |           0.729 |         136.000 |