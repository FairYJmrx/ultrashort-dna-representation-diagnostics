| Probe                |   Length | Method                      | Parameter       |   Mean macro-F1 |   SD macro-F1 |   Mean features |
|:---------------------|---------:|:----------------------------|:----------------|----------------:|--------------:|----------------:|
| target_background    |       69 | canonical spaced            | pattern=0-2-5-7 |           0.555 |         0.085 |         136.000 |
| target_background    |       75 | k-mer                       | k=5             |           0.543 |         0.110 |         983.800 |
| target_background    |      150 | canonical k-mer             | k=6             |           0.582 |         0.075 |        1957.200 |
| within_genus_species |       69 | canonical spaced + property | pattern=0-3-5-8 |           0.351 |         0.124 |         147.000 |
| within_genus_species |       75 | k-mer                       | k=5             |           0.373 |         0.135 |         979.500 |
| within_genus_species |      150 | canonical k-mer             | k=6             |           0.398 |         0.181 |        1971.333 |
