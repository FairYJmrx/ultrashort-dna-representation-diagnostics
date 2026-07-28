# Property scaling audit

The declared row-normalized encoding is compared with train-fitted coordinate z-scoring. The latter is a sensitivity analysis and does not redefine CK4P-MSP.

## Scaling sensitivity

| representation        |   n_cells |   paired_cosine |   l2_drift |   retrieval_top1 |
|:----------------------|----------:|----------------:|-----------:|-----------------:|
| P_unit_range          |        24 |          0.9996 |     0.0231 |           0.4963 |
| P_declared            |        24 |          0.9994 |     0.0247 |           0.3632 |
| MSP_declared          |        24 |          0.9995 |     0.0265 |           0.9688 |
| MSP_unit_range        |        24 |          0.9978 |     0.0558 |           0.9850 |
| CK4P-MSP_declared     |        24 |          0.9894 |     0.1283 |           1.0000 |
| CK4P-MSP_unit_range   |        24 |          0.9889 |     0.1318 |           1.0000 |
| CK4+P_unit_range      |        24 |          0.9845 |     0.1551 |           1.0000 |
| CK4+P_declared        |        24 |          0.9844 |     0.1557 |           1.0000 |
| MSP_train_zscore      |        24 |          0.9219 |     0.3294 |           0.9513 |
| CK4P-MSP_train_zscore |        24 |          0.8866 |     0.3899 |           0.9870 |
| CK4+P_train_zscore    |        24 |          0.8690 |     0.4040 |           0.8395 |
| P_train_zscore        |        24 |          0.7686 |     0.4955 |           0.3883 |

## P-group leave-one-out audit

| omitted_p_group   |   n_cells |   paired_cosine |   l2_drift |   retrieval_top1 |
|:------------------|----------:|----------------:|-----------:|-----------------:|
| hydrogen          |        24 |          0.9845 |     0.1552 |           1.0000 |
| entropy           |        24 |          0.9844 |     0.1557 |           1.0000 |
| n_fraction        |        24 |          0.9844 |     0.1557 |           1.0000 |
| eiip              |        24 |          0.9844 |     0.1557 |           1.0000 |
| none              |        24 |          0.9844 |     0.1557 |           1.0000 |
| scaled_length     |        24 |          0.9843 |     0.1558 |           1.0000 |
| purine            |        24 |          0.9843 |     0.1558 |           1.0000 |
| gc                |        24 |          0.9843 |     0.1558 |           1.0000 |
