| Task                      | Model                     | Model family     | Input               |   Mean macro-F1 |   Mean accuracy |   Mean features |   Runs |
|:--------------------------|:--------------------------|:-----------------|:--------------------|----------------:|----------------:|----------------:|-------:|
| global species            | mlp ckmer5                | tabular mlp      | ckmer5 count l2     |           0.116 |           0.133 |         512.000 |     12 |
| global species            | mlp hybrid                | tabular mlp      | hybrid ckmer5 csp   |           0.115 |           0.129 |         659.000 |     12 |
| global species            | mlp csp                   | tabular mlp      | cspaced property l2 |           0.099 |           0.117 |         147.000 |     12 |
| global species            | cnn property              | cnn1d            | property            |           0.078 |           0.118 |         492.500 |     12 |
| global species            | tiny transformer onehot   | tiny transformer | onehot              |           0.074 |           0.129 |         492.500 |     12 |
| global species            | tiny transformer property | tiny transformer | property            |           0.065 |           0.128 |         492.500 |     12 |
| global species            | cnn onehot                | cnn1d            | onehot              |           0.065 |           0.103 |         492.500 |     12 |
| target background         | cnn onehot                | cnn1d            | onehot              |           0.569 |           0.583 |         492.500 |     12 |
| target background         | mlp csp                   | tabular mlp      | cspaced property l2 |           0.563 |           0.568 |         147.000 |     12 |
| target background         | mlp hybrid                | tabular mlp      | hybrid ckmer5 csp   |           0.559 |           0.563 |         659.000 |     12 |
| target background         | tiny transformer property | tiny transformer | property            |           0.553 |           0.556 |         492.500 |     12 |
| target background         | mlp ckmer5                | tabular mlp      | ckmer5 count l2     |           0.547 |           0.560 |         512.000 |     12 |
| target background         | tiny transformer onehot   | tiny transformer | onehot              |           0.535 |           0.537 |         492.500 |     12 |
| target background         | cnn property              | cnn1d            | property            |           0.535 |           0.558 |         492.500 |     12 |
| within-genus Enterobacter | mlp hybrid                | tabular mlp      | hybrid ckmer5 csp   |           0.202 |           0.220 |         657.000 |     12 |
| within-genus Enterobacter | mlp csp                   | tabular mlp      | cspaced property l2 |           0.187 |           0.220 |         147.000 |     12 |
| within-genus Enterobacter | mlp ckmer5                | tabular mlp      | ckmer5 count l2     |           0.167 |           0.190 |         510.000 |     12 |
| within-genus Enterobacter | cnn onehot                | cnn1d            | onehot              |           0.133 |           0.209 |         492.500 |     12 |
| within-genus Enterobacter | tiny transformer onehot   | tiny transformer | onehot              |           0.123 |           0.206 |         492.500 |     12 |
| within-genus Enterobacter | tiny transformer property | tiny transformer | property            |           0.105 |           0.187 |         492.500 |     12 |
| within-genus Enterobacter | cnn property              | cnn1d            | property            |           0.100 |           0.189 |         492.500 |     12 |
