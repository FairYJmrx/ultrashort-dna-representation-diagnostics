| Task                      | Condition              | Model                     | Model family     | Input               |   Mean macro-F1 drop vs clean |   Mean accuracy drop vs clean |
|:--------------------------|:-----------------------|:--------------------------|:-----------------|:--------------------|------------------------------:|------------------------------:|
| global species            | 3% N mask              | mlp csp                   | tabular mlp      | cspaced property l2 |                        -0.023 |                        -0.018 |
| global species            | 3% N mask              | tiny transformer onehot   | tiny transformer | onehot              |                        -0.018 |                        -0.015 |
| global species            | 3% N mask              | mlp ckmer5                | tabular mlp      | ckmer5 count l2     |                        -0.010 |                        -0.010 |
| global species            | 3% N mask              | cnn onehot                | cnn1d            | onehot              |                         0.000 |                         0.009 |
| global species            | 3% N mask              | mlp hybrid                | tabular mlp      | hybrid ckmer5 csp   |                         0.003 |                         0.006 |
| global species            | 3% N mask              | tiny transformer property | tiny transformer | property            |                         0.008 |                         0.006 |
| global species            | 3% N mask              | cnn property              | cnn1d            | property            |                         0.017 |                         0.003 |
| global species            | 1% substitution + 3% N | mlp csp                   | tabular mlp      | cspaced property l2 |                        -0.017 |                        -0.016 |
| global species            | 1% substitution + 3% N | mlp hybrid                | tabular mlp      | hybrid ckmer5 csp   |                        -0.013 |                        -0.016 |
| global species            | 1% substitution + 3% N | mlp ckmer5                | tabular mlp      | ckmer5 count l2     |                         0.004 |                        -0.000 |
| global species            | 1% substitution + 3% N | tiny transformer onehot   | tiny transformer | onehot              |                         0.006 |                        -0.002 |
| global species            | 1% substitution + 3% N | cnn property              | cnn1d            | property            |                         0.008 |                         0.006 |
| global species            | 1% substitution + 3% N | tiny transformer property | tiny transformer | property            |                         0.011 |                         0.001 |
| global species            | 1% substitution + 3% N | cnn onehot                | cnn1d            | onehot              |                         0.019 |                         0.025 |
| target background         | 3% N mask              | cnn onehot                | cnn1d            | onehot              |                        -0.078 |                        -0.042 |
| target background         | 3% N mask              | tiny transformer property | tiny transformer | property            |                        -0.061 |                        -0.068 |
| target background         | 3% N mask              | cnn property              | cnn1d            | property            |                        -0.049 |                        -0.021 |
| target background         | 3% N mask              | mlp ckmer5                | tabular mlp      | ckmer5 count l2     |                        -0.023 |                        -0.010 |
| target background         | 3% N mask              | tiny transformer onehot   | tiny transformer | onehot              |                        -0.019 |                        -0.016 |
| target background         | 3% N mask              | mlp csp                   | tabular mlp      | cspaced property l2 |                        -0.011 |                        -0.013 |
| target background         | 3% N mask              | mlp hybrid                | tabular mlp      | hybrid ckmer5 csp   |                         0.035 |                         0.031 |
| target background         | 1% substitution + 3% N | cnn onehot                | cnn1d            | onehot              |                        -0.059 |                        -0.021 |
| target background         | 1% substitution + 3% N | tiny transformer property | tiny transformer | property            |                        -0.053 |                        -0.055 |
| target background         | 1% substitution + 3% N | mlp csp                   | tabular mlp      | cspaced property l2 |                        -0.050 |                        -0.049 |
| target background         | 1% substitution + 3% N | cnn property              | cnn1d            | property            |                        -0.043 |                        -0.029 |
| target background         | 1% substitution + 3% N | tiny transformer onehot   | tiny transformer | onehot              |                        -0.028 |                        -0.026 |
| target background         | 1% substitution + 3% N | mlp hybrid                | tabular mlp      | hybrid ckmer5 csp   |                         0.002 |                         0.005 |
| target background         | 1% substitution + 3% N | mlp ckmer5                | tabular mlp      | ckmer5 count l2     |                         0.055 |                         0.057 |
| within-genus Enterobacter | 3% N mask              | tiny transformer onehot   | tiny transformer | onehot              |                        -0.033 |                         0.005 |
| within-genus Enterobacter | 3% N mask              | cnn onehot                | cnn1d            | onehot              |                        -0.033 |                        -0.028 |
| within-genus Enterobacter | 3% N mask              | cnn property              | cnn1d            | property            |                        -0.019 |                        -0.014 |
| within-genus Enterobacter | 3% N mask              | tiny transformer property | tiny transformer | property            |                         0.004 |                         0.005 |
| within-genus Enterobacter | 3% N mask              | mlp csp                   | tabular mlp      | cspaced property l2 |                         0.031 |                         0.014 |
| within-genus Enterobacter | 3% N mask              | mlp ckmer5                | tabular mlp      | ckmer5 count l2     |                         0.046 |                         0.057 |
| within-genus Enterobacter | 3% N mask              | mlp hybrid                | tabular mlp      | hybrid ckmer5 csp   |                         0.067 |                         0.066 |
| within-genus Enterobacter | 1% substitution + 3% N | cnn property              | cnn1d            | property            |                        -0.006 |                         0.014 |
| within-genus Enterobacter | 1% substitution + 3% N | mlp ckmer5                | tabular mlp      | ckmer5 count l2     |                         0.004 |                        -0.005 |
| within-genus Enterobacter | 1% substitution + 3% N | tiny transformer property | tiny transformer | property            |                         0.012 |                         0.014 |
| within-genus Enterobacter | 1% substitution + 3% N | cnn onehot                | cnn1d            | onehot              |                         0.014 |                         0.009 |
| within-genus Enterobacter | 1% substitution + 3% N | tiny transformer onehot   | tiny transformer | onehot              |                         0.039 |                         0.014 |
| within-genus Enterobacter | 1% substitution + 3% N | mlp csp                   | tabular mlp      | cspaced property l2 |                         0.064 |                         0.033 |
| within-genus Enterobacter | 1% substitution + 3% N | mlp hybrid                | tabular mlp      | hybrid ckmer5 csp   |                         0.095 |                         0.080 |
