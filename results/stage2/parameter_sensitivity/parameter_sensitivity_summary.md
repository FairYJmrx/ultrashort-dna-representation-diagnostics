# Parameter Sensitivity Results

This lightweight audit tests whether manuscript conclusions depend on a single arbitrary k value or one spaced-seed pattern.

## Best perturbation-stability settings by length

| condition         |   length | family                      | parameter       |   paired_cosine_mean |   l2_delta_mean |   observed_vocab_size |
|:------------------|---------:|:----------------------------|:----------------|---------------------:|----------------:|----------------------:|
| N_3pct            |       69 | canonical spaced + property | pattern=0-1-2-3 |                0.994 |           0.106 |                   147 |
| N_3pct            |       75 | canonical spaced + property | pattern=0-1-2-3 |                0.995 |           0.098 |                   147 |
| N_3pct            |      150 | canonical spaced + property | pattern=0-1-2-3 |                0.996 |           0.086 |                   147 |
| substitution_1pct |       69 | canonical spaced + property | pattern=0-1-2-3 |                0.997 |           0.049 |                   147 |
| substitution_1pct |       75 | canonical spaced + property | pattern=0-1-2-3 |                0.998 |           0.044 |                   147 |
| substitution_1pct |      150 | canonical spaced + property | pattern=0-1-2-3 |                0.998 |           0.051 |                   147 |

Canonical 5-mer is retained as a strong conventional baseline, but the sensitivity grid shows that stability trends should be discussed across k rather than claimed for k=5 alone.

## Best close-relative readout settings by length

| probe                |   length | method                      | parameter       |   mean_macro_f1 |   sd_macro_f1 |   mean_features |
|:---------------------|---------:|:----------------------------|:----------------|----------------:|--------------:|----------------:|
| target_background    |       69 | canonical spaced            | pattern=0-2-5-7 |           0.555 |         0.085 |         136.000 |
| target_background    |       75 | k-mer                       | k=5             |           0.543 |         0.110 |         983.800 |
| target_background    |      150 | canonical k-mer             | k=6             |           0.582 |         0.075 |        1957.200 |
| within_genus_species |       69 | canonical spaced + property | pattern=0-3-5-8 |           0.351 |         0.124 |         147.000 |
| within_genus_species |       75 | k-mer                       | k=5             |           0.373 |         0.135 |         979.500 |
| within_genus_species |      150 | canonical k-mer             | k=6             |           0.398 |         0.181 |        1971.333 |

These values remain downstream probes only. They show sensitivity to parameterization and reinforce the need to avoid a single-method accuracy claim.
