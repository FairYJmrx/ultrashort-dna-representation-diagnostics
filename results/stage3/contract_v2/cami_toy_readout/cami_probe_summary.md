# Stage-3 CAMI Low-complexity Probe Summary

This analysis treats CAMI as an external lightweight readout probe, not as an end-to-end clinical classifier benchmark.

## Best readout by task, condition and length

| task              | condition         |   length | representation   |   mean_macro_f1 |   mean_accuracy |   mean_features |
|:------------------|:------------------|---------:|:-----------------|----------------:|----------------:|----------------:|
| label_probe       | N_3pct            |       69 | ck4_p            |           0.247 |           0.260 |         147.000 |
| label_probe       | N_3pct            |       75 | ck4p_msp         |           0.260 |           0.274 |         222.000 |
| label_probe       | N_3pct            |      100 | ckmer5_count_l2  |           0.287 |           0.286 |         512.000 |
| label_probe       | clean             |       69 | ck4_p            |           0.246 |           0.259 |         147.000 |
| label_probe       | clean             |       75 | ck4_p            |           0.266 |           0.280 |         147.000 |
| label_probe       | clean             |      100 | ckmer5_count_l2  |           0.316 |           0.317 |         512.000 |
| label_probe       | substitution_1pct |       69 | ck4p_msp         |           0.244 |           0.257 |         222.000 |
| label_probe       | substitution_1pct |       75 | ck4_p            |           0.261 |           0.277 |         147.000 |
| label_probe       | substitution_1pct |      100 | ckmer5_count_l2  |           0.307 |           0.306 |         512.000 |
| target_background | N_3pct            |       69 | ck4p_msp         |           0.863 |           0.865 |         222.000 |
| target_background | N_3pct            |       75 | ckmer5_count_l2  |           0.948 |           0.948 |         512.000 |
| target_background | N_3pct            |      100 | ck4_p            |           0.842 |           0.844 |         147.000 |
| target_background | clean             |       69 | ck4p_msp         |           0.874 |           0.875 |         222.000 |
| target_background | clean             |       75 | ckmer5_count_l2  |           0.937 |           0.938 |         512.000 |
| target_background | clean             |      100 | ckmer5_count_l2  |           0.852 |           0.854 |         512.000 |
| target_background | substitution_1pct |       69 | ck4p_msp         |           0.895 |           0.896 |         222.000 |
| target_background | substitution_1pct |       75 | ckmer5_count_l2  |           0.927 |           0.927 |         512.000 |
| target_background | substitution_1pct |      100 | ck4              |           0.852 |           0.854 |         136.000 |