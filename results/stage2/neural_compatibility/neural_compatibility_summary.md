# Stage-2 Neural Compatibility Probe

This deterministic probe tests whether compact tabular features, one-hot channels and DNA property channels can be read by small local neural models. It is not a clinical classifier benchmark.

## Aggregate by task and model

| task                              | model                     | family           | input_name          |   mean_macro_f1 |   mean_accuracy |   mean_epochs |   mean_features |   n_runs |
|:----------------------------------|:--------------------------|:-----------------|:--------------------|----------------:|----------------:|--------------:|----------------:|---------:|
| global_species                    | mlp_ckmer5                | tabular_mlp      | ckmer5_count_l2     |           0.116 |           0.133 |        12.083 |         512.000 |       12 |
| global_species                    | mlp_hybrid                | tabular_mlp      | hybrid_ckmer5_csp   |           0.115 |           0.129 |        10.500 |         659.000 |       12 |
| global_species                    | mlp_csp                   | tabular_mlp      | cspaced_property_l2 |           0.099 |           0.117 |        20.417 |         147.000 |       12 |
| global_species                    | cnn_property              | cnn1d            | property            |           0.078 |           0.118 |        24.000 |         492.500 |       12 |
| global_species                    | tiny_transformer_onehot   | tiny_transformer | onehot              |           0.074 |           0.129 |        24.000 |         492.500 |       12 |
| global_species                    | tiny_transformer_property | tiny_transformer | property            |           0.065 |           0.128 |        24.000 |         492.500 |       12 |
| global_species                    | cnn_onehot                | cnn1d            | onehot              |           0.065 |           0.103 |        24.000 |         492.500 |       12 |
| target_background                 | cnn_onehot                | cnn1d            | onehot              |           0.569 |           0.583 |        20.750 |         492.500 |       12 |
| target_background                 | mlp_csp                   | tabular_mlp      | cspaced_property_l2 |           0.563 |           0.568 |         9.250 |         147.000 |       12 |
| target_background                 | mlp_hybrid                | tabular_mlp      | hybrid_ckmer5_csp   |           0.559 |           0.563 |         6.500 |         659.000 |       12 |
| target_background                 | tiny_transformer_property | tiny_transformer | property            |           0.553 |           0.556 |        22.917 |         492.500 |       12 |
| target_background                 | mlp_ckmer5                | tabular_mlp      | ckmer5_count_l2     |           0.547 |           0.560 |         6.250 |         512.000 |       12 |
| target_background                 | tiny_transformer_onehot   | tiny_transformer | onehot              |           0.535 |           0.537 |        13.833 |         492.500 |       12 |
| target_background                 | cnn_property              | cnn1d            | property            |           0.535 |           0.558 |        17.667 |         492.500 |       12 |
| within_genus_species:Enterobacter | mlp_hybrid                | tabular_mlp      | hybrid_ckmer5_csp   |           0.202 |           0.220 |         7.667 |         657.000 |       12 |
| within_genus_species:Enterobacter | mlp_csp                   | tabular_mlp      | cspaced_property_l2 |           0.187 |           0.220 |        11.333 |         147.000 |       12 |
| within_genus_species:Enterobacter | mlp_ckmer5                | tabular_mlp      | ckmer5_count_l2     |           0.167 |           0.190 |         8.917 |         510.000 |       12 |
| within_genus_species:Enterobacter | cnn_onehot                | cnn1d            | onehot              |           0.133 |           0.209 |        15.000 |         492.500 |       12 |
| within_genus_species:Enterobacter | tiny_transformer_onehot   | tiny_transformer | onehot              |           0.123 |           0.206 |        12.083 |         492.500 |       12 |
| within_genus_species:Enterobacter | tiny_transformer_property | tiny_transformer | property            |           0.105 |           0.187 |        14.750 |         492.500 |       12 |
| within_genus_species:Enterobacter | cnn_property              | cnn1d            | property            |           0.100 |           0.189 |        12.083 |         492.500 |       12 |

## Mean degradation versus clean

| task                              | condition                | model                     | family           | input_name          |   mean_macro_f1_drop |   mean_accuracy_drop |
|:----------------------------------|:-------------------------|:--------------------------|:-----------------|:--------------------|---------------------:|---------------------:|
| global_species                    | N_3pct                   | mlp_csp                   | tabular_mlp      | cspaced_property_l2 |               -0.023 |               -0.018 |
| global_species                    | N_3pct                   | tiny_transformer_onehot   | tiny_transformer | onehot              |               -0.018 |               -0.015 |
| global_species                    | N_3pct                   | mlp_ckmer5                | tabular_mlp      | ckmer5_count_l2     |               -0.010 |               -0.010 |
| global_species                    | N_3pct                   | cnn_onehot                | cnn1d            | onehot              |                0.000 |                0.009 |
| global_species                    | N_3pct                   | mlp_hybrid                | tabular_mlp      | hybrid_ckmer5_csp   |                0.003 |                0.006 |
| global_species                    | N_3pct                   | tiny_transformer_property | tiny_transformer | property            |                0.008 |                0.006 |
| global_species                    | N_3pct                   | cnn_property              | cnn1d            | property            |                0.017 |                0.003 |
| global_species                    | substitution_1pct_N_3pct | mlp_csp                   | tabular_mlp      | cspaced_property_l2 |               -0.017 |               -0.016 |
| global_species                    | substitution_1pct_N_3pct | mlp_hybrid                | tabular_mlp      | hybrid_ckmer5_csp   |               -0.013 |               -0.016 |
| global_species                    | substitution_1pct_N_3pct | mlp_ckmer5                | tabular_mlp      | ckmer5_count_l2     |                0.004 |               -0.000 |
| global_species                    | substitution_1pct_N_3pct | tiny_transformer_onehot   | tiny_transformer | onehot              |                0.006 |               -0.002 |
| global_species                    | substitution_1pct_N_3pct | cnn_property              | cnn1d            | property            |                0.008 |                0.006 |
| global_species                    | substitution_1pct_N_3pct | tiny_transformer_property | tiny_transformer | property            |                0.011 |                0.001 |
| global_species                    | substitution_1pct_N_3pct | cnn_onehot                | cnn1d            | onehot              |                0.019 |                0.025 |
| target_background                 | N_3pct                   | cnn_onehot                | cnn1d            | onehot              |               -0.078 |               -0.042 |
| target_background                 | N_3pct                   | tiny_transformer_property | tiny_transformer | property            |               -0.061 |               -0.068 |
| target_background                 | N_3pct                   | cnn_property              | cnn1d            | property            |               -0.049 |               -0.021 |
| target_background                 | N_3pct                   | mlp_ckmer5                | tabular_mlp      | ckmer5_count_l2     |               -0.023 |               -0.010 |
| target_background                 | N_3pct                   | tiny_transformer_onehot   | tiny_transformer | onehot              |               -0.019 |               -0.016 |
| target_background                 | N_3pct                   | mlp_csp                   | tabular_mlp      | cspaced_property_l2 |               -0.011 |               -0.013 |
| target_background                 | N_3pct                   | mlp_hybrid                | tabular_mlp      | hybrid_ckmer5_csp   |                0.035 |                0.031 |
| target_background                 | substitution_1pct_N_3pct | cnn_onehot                | cnn1d            | onehot              |               -0.059 |               -0.021 |
| target_background                 | substitution_1pct_N_3pct | tiny_transformer_property | tiny_transformer | property            |               -0.053 |               -0.055 |
| target_background                 | substitution_1pct_N_3pct | mlp_csp                   | tabular_mlp      | cspaced_property_l2 |               -0.050 |               -0.049 |
| target_background                 | substitution_1pct_N_3pct | cnn_property              | cnn1d            | property            |               -0.043 |               -0.029 |
| target_background                 | substitution_1pct_N_3pct | tiny_transformer_onehot   | tiny_transformer | onehot              |               -0.028 |               -0.026 |
| target_background                 | substitution_1pct_N_3pct | mlp_hybrid                | tabular_mlp      | hybrid_ckmer5_csp   |                0.002 |                0.005 |
| target_background                 | substitution_1pct_N_3pct | mlp_ckmer5                | tabular_mlp      | ckmer5_count_l2     |                0.055 |                0.057 |
| within_genus_species:Enterobacter | N_3pct                   | tiny_transformer_onehot   | tiny_transformer | onehot              |               -0.033 |                0.005 |
| within_genus_species:Enterobacter | N_3pct                   | cnn_onehot                | cnn1d            | onehot              |               -0.033 |               -0.028 |
| within_genus_species:Enterobacter | N_3pct                   | cnn_property              | cnn1d            | property            |               -0.019 |               -0.014 |
| within_genus_species:Enterobacter | N_3pct                   | tiny_transformer_property | tiny_transformer | property            |                0.004 |                0.005 |
| within_genus_species:Enterobacter | N_3pct                   | mlp_csp                   | tabular_mlp      | cspaced_property_l2 |                0.031 |                0.014 |
| within_genus_species:Enterobacter | N_3pct                   | mlp_ckmer5                | tabular_mlp      | ckmer5_count_l2     |                0.046 |                0.057 |
| within_genus_species:Enterobacter | N_3pct                   | mlp_hybrid                | tabular_mlp      | hybrid_ckmer5_csp   |                0.067 |                0.066 |
| within_genus_species:Enterobacter | substitution_1pct_N_3pct | cnn_property              | cnn1d            | property            |               -0.006 |                0.014 |
| within_genus_species:Enterobacter | substitution_1pct_N_3pct | mlp_ckmer5                | tabular_mlp      | ckmer5_count_l2     |                0.004 |               -0.005 |
| within_genus_species:Enterobacter | substitution_1pct_N_3pct | tiny_transformer_property | tiny_transformer | property            |                0.012 |                0.014 |
| within_genus_species:Enterobacter | substitution_1pct_N_3pct | cnn_onehot                | cnn1d            | onehot              |                0.014 |                0.009 |
| within_genus_species:Enterobacter | substitution_1pct_N_3pct | tiny_transformer_onehot   | tiny_transformer | onehot              |                0.039 |                0.014 |
| within_genus_species:Enterobacter | substitution_1pct_N_3pct | mlp_csp                   | tabular_mlp      | cspaced_property_l2 |                0.064 |                0.033 |
| within_genus_species:Enterobacter | substitution_1pct_N_3pct | mlp_hybrid                | tabular_mlp      | hybrid_ckmer5_csp   |                0.095 |                0.080 |
