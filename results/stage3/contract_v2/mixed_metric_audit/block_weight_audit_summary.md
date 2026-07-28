# Mixed-metric block-weight audit

This audit keeps the k-mer, global property, and multi-scale property blocks separately normalized and varies their weights under the fixed weighted-block denominator. The point is to test whether the observed stability and selective-sensitivity trends survive reasonable block reweighting instead of relying on one selected concatenation scale.

## Stability across block weights

| weight_name       | weight_label                        |   n_cells |   paired_cosine |   l2_drift |   retrieval_top1 |
|:------------------|:------------------------------------|----------:|----------------:|-----------:|-----------------:|
| property_only     | property_only (k=0, P=1, MSP=1)     |        24 |           0.999 |      0.027 |            0.960 |
| property_dominant | property_dominant (k=1, P=2, MSP=2) |        24 |           0.996 |      0.078 |            1.000 |
| ck4p_msp          | ck4p_msp (k=1, P=1, MSP=1)          |        24 |           0.989 |      0.128 |            1.000 |
| ck4_plus_p        | ck4_plus_p (k=1, P=1, MSP=0)        |        24 |           0.984 |      0.156 |            1.000 |
| identity_dominant | identity_dominant (k=2, P=1, MSP=1) |        24 |           0.979 |      0.179 |            1.000 |
| identity_only     | identity_only (k=1, P=0, MSP=0)     |        24 |           0.969 |      0.218 |            1.000 |

## Local mutation sensitivity across block weights

| weight_name       | weight_label                        |   n_cells |   noise_l2 |   local_l2 |   local_minus_noise_l2 |   selective_sensitivity_ratio |
|:------------------|:------------------------------------|----------:|-----------:|-----------:|-----------------------:|------------------------------:|
| property_only     | property_only (k=0, P=1, MSP=1)     |        12 |      0.013 |      0.016 |                  0.002 |                         1.172 |
| property_dominant | property_dominant (k=1, P=2, MSP=2) |        12 |      0.119 |      0.090 |                 -0.029 |                         0.751 |
| ck4p_msp          | ck4p_msp (k=1, P=1, MSP=1)          |        12 |      0.205 |      0.154 |                 -0.051 |                         0.745 |
| identity_dominant | identity_dominant (k=2, P=1, MSP=1) |        12 |      0.290 |      0.217 |                 -0.073 |                         0.744 |
| ck4_plus_p        | ck4_plus_p (k=1, P=1, MSP=0)        |        12 |      0.251 |      0.188 |                 -0.063 |                         0.743 |
| identity_only     | identity_only (k=1, P=0, MSP=0)     |        12 |      0.355 |      0.266 |                 -0.089 |                         0.743 |

## Delta-readout across block weights

| weight_name       | weight_label                        | classifier   |   n_cells |   macro_f1 |   accuracy |   n_features |
|:------------------|:------------------------------------|:-------------|----------:|-----------:|-----------:|-------------:|
| ck4p_msp          | ck4p_msp (k=1, P=1, MSP=1)          | logistic     |        12 |      0.979 |      0.979 |      222.000 |
| identity_dominant | identity_dominant (k=2, P=1, MSP=1) | logistic     |        12 |      0.979 |      0.979 |      222.000 |
| property_dominant | property_dominant (k=1, P=2, MSP=2) | logistic     |        12 |      0.979 |      0.979 |      222.000 |
| property_only     | property_only (k=0, P=1, MSP=1)     | logistic     |        12 |      0.970 |      0.970 |      222.000 |
| ck4_plus_p        | ck4_plus_p (k=1, P=1, MSP=0)        | logistic     |        12 |      0.904 |      0.904 |      222.000 |
| identity_only     | identity_only (k=1, P=0, MSP=0)     | logistic     |        12 |      0.892 |      0.892 |      222.000 |
