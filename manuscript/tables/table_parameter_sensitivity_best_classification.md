| probe                |   length | method           | parameter       |   mean_macro_f1 |   sd_macro_f1 |   mean_accuracy |   mean_features |   genera |
|:---------------------|---------:|:-----------------|:----------------|----------------:|--------------:|----------------:|----------------:|---------:|
| target_background    |       75 | canonical spaced | pattern=0-1-3-6 |           0.547 |         0.158 |           0.633 |         136.000 |        5 |
| target_background    |      150 | canonical k-mer  | k=7             |           0.534 |         0.129 |           0.692 |        4111.000 |        5 |
| target_background    |      300 | k-mer            | k=5             |           0.539 |         0.097 |           0.658 |        1007.600 |        5 |
| within_genus_species |       75 | k-mer            | k=6             |           0.330 |         0.237 |           0.361 |        2109.500 |        6 |
| within_genus_species |      150 | canonical k-mer  | k=6             |           0.351 |         0.156 |           0.382 |        1779.833 |        6 |
| within_genus_species |      300 | canonical spaced | pattern=0-1-3-6 |           0.370 |         0.124 |           0.396 |         136.000 |        6 |