# Stage-3 CAMI Low-complexity Probe Summary

This analysis treats CAMI as an external lightweight readout probe, not as an end-to-end clinical classifier benchmark.

## Best readout by task, condition and length

| task              | condition   |   length | representation                     |   mean_macro_f1 |   mean_accuracy |   mean_features |
|:------------------|:------------|---------:|:-----------------------------------|----------------:|----------------:|----------------:|
| target_background | N_3pct      |       69 | ckmer5_count_l2                    |           0.589 |           0.611 |         507.000 |
| target_background | N_3pct      |      100 | ckmer5_count_l2                    |           0.917 |           0.917 |         512.000 |
| target_background | clean       |       69 | ckmer5_count_l2                    |           0.566 |           0.583 |         508.000 |
| target_background | clean       |      100 | ckmer4_property_multiscale_mean_l2 |           0.972 |           0.972 |         222.000 |