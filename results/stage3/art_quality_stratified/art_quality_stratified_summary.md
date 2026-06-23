# Stage-3 ART Quality-stratified Stability Summary

## Best stability by length and quality bin

|   length | quality_bin   | representation_label   |   paired_cosine_mean |   l2_delta_mean |   retrieval_top1 |   mean_phred_mean |   n_pairs |   n_features |
|---------:|:--------------|:-----------------------|---------------------:|----------------:|-----------------:|------------------:|----------:|-------------:|
|       69 | high          | EIIP summary           |                1.000 |           0.007 |            0.378 |            25.253 |       400 |            8 |
|       69 | low           | EIIP summary           |                1.000 |           0.010 |            0.168 |            23.006 |       400 |            8 |
|       69 | mid           | EIIP summary           |                1.000 |           0.009 |            0.235 |            24.154 |       400 |            8 |
|       75 | high          | EIIP summary           |                1.000 |           0.009 |            0.250 |            24.575 |       400 |            8 |
|       75 | low           | EIIP summary           |                1.000 |           0.012 |            0.138 |            22.458 |       400 |            8 |
|       75 | mid           | EIIP summary           |                1.000 |           0.009 |            0.240 |            23.521 |       400 |            8 |
|      100 | high          | EIIP summary           |                1.000 |           0.016 |            0.058 |            32.705 |       400 |            8 |
|      100 | low           | EIIP summary           |                1.000 |           0.020 |            0.040 |            30.331 |       400 |            8 |
|      100 | mid           | EIIP summary           |                1.000 |           0.019 |            0.045 |            31.542 |       400 |            8 |
|      125 | high          | EIIP summary           |                1.000 |           0.000 |            0.943 |            37.110 |       400 |            8 |
|      125 | low           | EIIP summary           |                1.000 |           0.001 |            0.838 |            36.272 |       400 |            8 |
|      125 | mid           | EIIP summary           |                1.000 |           0.002 |            0.848 |            36.732 |       400 |            8 |
|      150 | high          | EIIP summary           |                1.000 |           0.001 |            0.885 |            36.887 |       400 |            8 |
|      150 | low           | EIIP summary           |                1.000 |           0.002 |            0.728 |            36.095 |       400 |            8 |
|      150 | mid           | EIIP summary           |                1.000 |           0.001 |            0.818 |            36.531 |       400 |            8 |

## Mean by representation and quality bin

| quality_bin   | representation_label   |   paired_cosine_mean |   l2_delta_mean |   retrieval_top1 |   n_features |
|:--------------|:-----------------------|---------------------:|----------------:|-----------------:|-------------:|
| high          | CSP                    |                0.995 |           0.072 |            1.000 |      147.000 |
| high          | EIIP positional signal |                0.999 |           0.030 |            1.000 |      100.000 |
| high          | EIIP summary           |                1.000 |           0.007 |            0.503 |        8.000 |
| high          | MinHash k=5, s=128     |                0.932 |           0.271 |            0.992 |      128.000 |
| high          | canonical 5-mer        |                0.927 |           0.283 |            1.000 |      512.000 |
| high          | canonical 5-mer + CSP  |                0.961 |           0.207 |            1.000 |      659.000 |
| high          | canonical 7-mer        |                0.878 |           0.367 |            1.000 |     7890.000 |
| high          | canonical spaced count |                0.957 |           0.216 |            1.000 |      136.000 |
| low           | CSP                    |                0.992 |           0.099 |            1.000 |      147.000 |
| low           | EIIP positional signal |                0.998 |           0.042 |            1.000 |      100.000 |
| low           | EIIP summary           |                1.000 |           0.009 |            0.382 |        8.000 |
| low           | MinHash k=5, s=128     |                0.898 |           0.358 |            0.947 |      128.000 |
| low           | canonical 5-mer        |                0.878 |           0.392 |            1.000 |      512.000 |
| low           | canonical 5-mer + CSP  |                0.935 |           0.286 |            1.000 |      659.000 |
| low           | canonical 7-mer        |                0.802 |           0.503 |            1.000 |     7889.000 |
| low           | canonical spaced count |                0.927 |           0.301 |            1.000 |      136.000 |
| mid           | CSP                    |                0.994 |           0.085 |            1.000 |      147.000 |
| mid           | EIIP positional signal |                0.999 |           0.034 |            1.000 |      100.000 |
| mid           | EIIP summary           |                1.000 |           0.008 |            0.437 |        8.000 |
| mid           | MinHash k=5, s=128     |                0.917 |           0.313 |            0.975 |      128.000 |
| mid           | canonical 5-mer        |                0.903 |           0.339 |            1.000 |      512.000 |
| mid           | canonical 5-mer + CSP  |                0.949 |           0.248 |            1.000 |      659.000 |
| mid           | canonical 7-mer        |                0.843 |           0.436 |            1.000 |     7899.000 |
| mid           | canonical spaced count |                0.944 |           0.258 |            1.000 |      136.000 |