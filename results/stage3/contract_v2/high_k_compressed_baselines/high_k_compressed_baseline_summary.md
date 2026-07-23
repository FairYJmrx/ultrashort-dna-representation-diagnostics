# High-k compressed k-mer baseline audit

This audit compares CK4P-MSP with dimension-matched high-specificity k-mer vector controls. Hashing trick counts and sparse random projection are evaluated in vector geometry. MinHash is reported separately through its native signature-collision estimate of k-mer-set Jaccard similarity.

## Stability summary

| representation     | representation_label          |   n_cells |   paired_cosine |   l2_drift |   retrieval_top1 |   median_features |
|:-------------------|:------------------------------|----------:|----------------:|-----------:|-----------------:|------------------:|
| ckmer4_property_l2 | CK4+P                         |        24 |           0.996 |      0.078 |            1.000 |           147.000 |
| ck4p_msp           | CK4P-MSP                      |        24 |           0.989 |      0.129 |            1.000 |           222.000 |
| ckmer4_count_l2    | CK4                           |        24 |           0.969 |      0.220 |            1.000 |           136.000 |
| ckmer5_count_l2    | CK5                           |        24 |           0.945 |      0.295 |            1.000 |           512.000 |
| rp_ck15_d222       | CK15 random projection, d=222 |        24 |           0.868 |      0.447 |            1.000 |           222.000 |
| hash_k15_d222      | Hashed k=15, d=222            |        24 |           0.821 |      0.524 |            0.999 |           222.000 |

## Readout summary

| representation     | representation_label          | classifier       |   n_cells |   macro_f1 |   accuracy |   median_features |
|:-------------------|:------------------------------|:-----------------|----------:|-----------:|-----------:|------------------:|
| ckmer5_count_l2    | CK5                           | nearest_centroid |       132 |      0.407 |      0.424 |           507.000 |
| ckmer5_count_l2    | CK5                           | logistic         |       132 |      0.396 |      0.421 |           507.000 |
| ckmer4_property_l2 | CK4+P                         | nearest_centroid |       132 |      0.396 |      0.410 |           147.000 |
| ck4p_msp           | CK4P-MSP                      | nearest_centroid |       132 |      0.394 |      0.408 |           222.000 |
| ckmer4_count_l2    | CK4                           | nearest_centroid |       132 |      0.392 |      0.406 |           136.000 |
| hash_k15_d222      | Hashed k=15, d=222            | logistic         |       132 |      0.379 |      0.403 |           222.000 |
| hash_k15_d222      | Hashed k=15, d=222            | nearest_centroid |       132 |      0.378 |      0.403 |           222.000 |
| ck4p_msp           | CK4P-MSP                      | logistic         |       132 |      0.376 |      0.394 |           222.000 |
| ckmer4_count_l2    | CK4                           | logistic         |       132 |      0.363 |      0.382 |           136.000 |
| ckmer4_property_l2 | CK4+P                         | logistic         |       132 |      0.360 |      0.379 |           147.000 |
| rp_ck15_d222       | CK15 random projection, d=222 | nearest_centroid |       132 |      0.268 |      0.449 |           222.000 |
| rp_ck15_d222       | CK15 random projection, d=222 | logistic         |       132 |      0.265 |      0.446 |           222.000 |

## Native MinHash Jaccard audit

| representation   | representation_label   |   n_cells |   estimated_jaccard |   exact_jaccard |   mean_absolute_error |
|:-----------------|:-----------------------|----------:|--------------------:|----------------:|----------------------:|
| minhash_k15_s222 | MinHash k=15, s=222    |        24 |               0.711 |           0.711 |                 0.020 |
