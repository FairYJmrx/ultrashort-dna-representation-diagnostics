# Same-dimension dimensionality-reduction baselines

High-dimensional canonical k-mer features were projected to the same dimensional ranges as the compact property-aware representations. Reducers were fitted on the clean/train portion within each analysis cell, then applied to paired perturbed reads or readout test examples.

## Stability summary

| representation   | representation_label   |   n_cells |   paired_cosine |   l2_drift |   retrieval_top1 |   median_features |
|:-----------------|:-----------------------|----------:|----------------:|-----------:|-----------------:|------------------:|
| ck7_svd147       | CK7 SVD-147            |        24 |           0.994 |      0.093 |            1.000 |           147.000 |
| ck7_pca147       | CK7 PCA-147            |        24 |           0.994 |      0.095 |            1.000 |           147.000 |
| ck7_svd222       | CK7 SVD-222            |        24 |           0.993 |      0.097 |            1.000 |           222.000 |
| ck7_pca222       | CK7 PCA-222            |        24 |           0.993 |      0.098 |            1.000 |           222.000 |
| ck4p_msp         | CK4P-MSP               |        24 |           0.989 |      0.128 |            1.000 |           222.000 |
| ck4_p            | CK4+P                  |        24 |           0.984 |      0.156 |            1.000 |           147.000 |
| ck5_svd147       | CK5 SVD-147            |        24 |           0.972 |      0.206 |            1.000 |           147.000 |
| ck4              | CK4                    |        24 |           0.969 |      0.218 |            1.000 |           136.000 |
| ck5_pca147       | CK5 PCA-147            |        24 |           0.967 |      0.227 |            1.000 |           147.000 |
| ck5_svd222       | CK5 SVD-222            |        24 |           0.965 |      0.234 |            1.000 |           222.000 |
| ck5_pca222       | CK5 PCA-222            |        24 |           0.958 |      0.255 |            1.000 |           222.000 |
| ckmer5_count_l2  | CK5                    |        24 |           0.946 |      0.292 |            1.000 |           512.000 |

## Readout summary

| representation   | representation_label   | classifier       |   n_cells |   macro_f1 |   accuracy |   median_features |
|:-----------------|:-----------------------|:-----------------|----------:|-----------:|-----------:|------------------:|
| ck7_pca147       | CK7 PCA-147            | logistic         |       132 |      0.416 |      0.429 |            49.500 |
| ck7_pca222       | CK7 PCA-222            | logistic         |       132 |      0.416 |      0.429 |            49.500 |
| ck5_pca147       | CK5 PCA-147            | nearest_centroid |       132 |      0.410 |      0.423 |            49.500 |
| ck5_pca222       | CK5 PCA-222            | nearest_centroid |       132 |      0.410 |      0.423 |            49.500 |
| ck7_svd147       | CK7 SVD-147            | nearest_centroid |       132 |      0.406 |      0.419 |            49.500 |
| ck7_svd222       | CK7 SVD-222            | nearest_centroid |       132 |      0.406 |      0.419 |            49.500 |
| ck5_svd147       | CK5 SVD-147            | nearest_centroid |       132 |      0.406 |      0.423 |            49.500 |
| ck5_svd222       | CK5 SVD-222            | nearest_centroid |       132 |      0.406 |      0.423 |            49.500 |
| ck5_pca147       | CK5 PCA-147            | logistic         |       132 |      0.403 |      0.419 |            49.500 |
| ck5_pca222       | CK5 PCA-222            | logistic         |       132 |      0.403 |      0.419 |            49.500 |
| ck7_svd147       | CK7 SVD-147            | logistic         |       132 |      0.403 |      0.429 |            49.500 |
| ck7_svd222       | CK7 SVD-222            | logistic         |       132 |      0.403 |      0.429 |            49.500 |
| ckmer5_count_l2  | CK5                    | nearest_centroid |       132 |      0.402 |      0.423 |           507.000 |
| ck4_p            | CK4+P                  | logistic         |       132 |      0.402 |      0.420 |           147.000 |
| ck7_pca147       | CK7 PCA-147            | nearest_centroid |       132 |      0.402 |      0.414 |            49.500 |
| ck7_pca222       | CK7 PCA-222            | nearest_centroid |       132 |      0.402 |      0.414 |            49.500 |
| ck4p_msp         | CK4P-MSP               | logistic         |       132 |      0.401 |      0.423 |           222.000 |
| ck4p_msp         | CK4P-MSP               | nearest_centroid |       132 |      0.401 |      0.418 |           222.000 |
| ck4_p            | CK4+P                  | nearest_centroid |       132 |      0.399 |      0.416 |           147.000 |
| ck4              | CK4                    | nearest_centroid |       132 |      0.397 |      0.414 |           136.000 |
| ck5_svd147       | CK5 SVD-147            | logistic         |       132 |      0.390 |      0.417 |            49.500 |
| ck5_svd222       | CK5 SVD-222            | logistic         |       132 |      0.390 |      0.417 |            49.500 |
| ck4              | CK4                    | logistic         |       132 |      0.389 |      0.407 |           136.000 |
| ckmer5_count_l2  | CK5                    | logistic         |       132 |      0.388 |      0.415 |           507.000 |
