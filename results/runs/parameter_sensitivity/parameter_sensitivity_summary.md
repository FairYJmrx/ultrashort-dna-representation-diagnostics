# Parameter Sensitivity Results

This lightweight audit tests whether manuscript conclusions depend on a single arbitrary k value or one spaced-seed pattern.

## Best perturbation-stability settings by length

| condition         |   length | family                      | parameter       |   paired_cosine_mean |   l2_delta_mean |   observed_vocab_size |
|:------------------|---------:|:----------------------------|:----------------|---------------------:|----------------:|----------------------:|
| N_3pct            |       69 | canonical spaced + property | pattern=0-1-2-3 |                0.994 |           0.105 |                   147 |
| N_3pct            |       75 | canonical spaced + property | pattern=0-1-2-3 |                0.995 |           0.098 |                   147 |
| N_3pct            |      100 | canonical spaced + property | pattern=0-1-2-3 |                0.995 |           0.100 |                   147 |
| N_3pct            |      125 | canonical spaced + property | pattern=0-1-2-3 |                0.995 |           0.100 |                   147 |
| N_3pct            |      150 | canonical spaced + property | pattern=0-1-2-3 |                0.996 |           0.084 |                   147 |
| N_3pct            |      300 | canonical spaced + property | pattern=0-1-2-3 |                0.997 |           0.074 |                   147 |
| substitution_1pct |       69 | canonical spaced + property | pattern=0-1-2-3 |                0.998 |           0.043 |                   147 |
| substitution_1pct |       75 | canonical spaced + property | pattern=0-1-2-3 |                0.998 |           0.043 |                   147 |
| substitution_1pct |      100 | canonical spaced + property | pattern=0-1-2-3 |                0.998 |           0.050 |                   147 |
| substitution_1pct |      125 | canonical spaced + property | pattern=0-1-2-3 |                0.998 |           0.051 |                   147 |
| substitution_1pct |      150 | canonical spaced + property | pattern=0-1-2-3 |                0.998 |           0.050 |                   147 |
| substitution_1pct |      300 | canonical spaced + property | pattern=0-1-2-3 |                0.999 |           0.037 |                   147 |

Canonical 5-mer is retained as a strong conventional baseline, but the sensitivity grid shows that stability trends should be discussed across k rather than claimed for k=5 alone.

## Best close-relative readout settings by length

| probe                |   length | method           | parameter       |   mean_macro_f1 |   sd_macro_f1 |   mean_features |
|:---------------------|---------:|:-----------------|:----------------|----------------:|--------------:|----------------:|
| target_background    |       75 | canonical spaced | pattern=0-1-3-6 |           0.547 |         0.158 |         136.000 |
| target_background    |      150 | canonical k-mer  | k=7             |           0.534 |         0.129 |        4111.000 |
| target_background    |      300 | k-mer            | k=5             |           0.539 |         0.097 |        1007.600 |
| within_genus_species |       75 | k-mer            | k=6             |           0.330 |         0.237 |        2109.500 |
| within_genus_species |      150 | canonical k-mer  | k=6             |           0.351 |         0.156 |        1779.833 |
| within_genus_species |      300 | canonical spaced | pattern=0-1-3-6 |           0.370 |         0.124 |         136.000 |

These values remain downstream probes only. They show sensitivity to parameterization and reinforce the need to avoid a single-method accuracy claim.
