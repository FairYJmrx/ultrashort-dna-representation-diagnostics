| Perturbation       |   Length | Family                      | Parameter       |   Mean paired cosine |   Mean L2 drift |   Observed vocabulary/features |
|:-------------------|---------:|:----------------------------|:----------------|---------------------:|----------------:|-------------------------------:|
| 3% N mask          |       69 | canonical spaced + property | pattern=0-1-2-3 |                0.994 |           0.106 |                            147 |
| 3% N mask          |       75 | canonical spaced + property | pattern=0-1-2-3 |                0.995 |           0.098 |                            147 |
| 3% N mask          |      150 | canonical spaced + property | pattern=0-1-2-3 |                0.996 |           0.086 |                            147 |
| reverse_complement |       69 | canonical k-mer             | k=6             |                1.000 |           0.000 |                           2052 |
| reverse_complement |       75 | canonical k-mer             | k=8             |                1.000 |           0.000 |                          11656 |
| reverse_complement |      150 | canonical k-mer             | k=8             |                1.000 |           0.000 |                          18791 |
| 1% substitution    |       69 | canonical spaced + property | pattern=0-1-2-3 |                0.997 |           0.049 |                            147 |
| 1% substitution    |       75 | canonical spaced + property | pattern=0-1-2-3 |                0.998 |           0.044 |                            147 |
| 1% substitution    |      150 | canonical spaced + property | pattern=0-1-2-3 |                0.998 |           0.051 |                            147 |
