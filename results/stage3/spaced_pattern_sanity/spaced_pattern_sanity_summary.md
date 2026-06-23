# Spaced-Pattern Sanity Validation

This run keeps earlier parameter-sensitivity outputs intact and tests whether CSP conclusions depend on one four-position default seed.
Expanded four-position layouts are the primary point-layout scan. Three-position and five-position layouts are supplementary cardinality sanity checks, not an exhaustive seed-design search.

## Pattern set

| pattern   |   cardinality |   span | role                       |
|:----------|--------------:|-------:|:---------------------------|
| 0-1-2     |             3 |      3 | cardinality sanity check   |
| 0-2-4     |             3 |      5 | cardinality sanity check   |
| 0-3-6     |             3 |      7 | cardinality sanity check   |
| 0-1-2-3   |             4 |      4 | primary four-position scan |
| 0-1-3-6   |             4 |      7 | primary four-position scan |
| 0-2-4-6   |             4 |      7 | primary four-position scan |
| 0-1-4-7   |             4 |      8 | primary four-position scan |
| 0-2-5-7   |             4 |      8 | primary four-position scan |
| 0-2-5-8   |             4 |      9 | primary four-position scan |
| 0-3-5-8   |             4 |      9 | primary four-position scan |
| 0-3-6-9   |             4 |     10 | primary four-position scan |
| 0-1-2-3-4 |             5 |      5 | cardinality sanity check   |
| 0-1-3-6-9 |             5 |     10 | cardinality sanity check   |
| 0-2-4-6-8 |             5 |      9 | cardinality sanity check   |

## CSP summary by seed cardinality

|   cardinality | role                       |   n_patterns |   n_stability_cells |   min_features |   median_features |   max_features |   mean_paired_cosine |   min_paired_cosine |   max_paired_cosine |   mean_l2_delta |   mean_retrieval_top1 |
|--------------:|:---------------------------|-------------:|--------------------:|---------------:|------------------:|---------------:|---------------------:|--------------------:|--------------------:|----------------:|----------------------:|
|             3 | cardinality sanity check   |            3 |                  18 |             43 |            43.000 |             43 |                0.997 |               0.994 |               0.999 |           0.068 |                 1.000 |
|             4 | primary four-position scan |            8 |                  48 |            147 |           147.000 |            147 |                0.993 |               0.985 |               0.998 |           0.104 |                 1.000 |
|             5 | cardinality sanity check   |            3 |                  18 |            523 |           523.000 |            523 |                0.990 |               0.980 |               0.996 |           0.126 |                 1.000 |

## Best four-position CSP pattern by perturbation and length

| Perturbation        |   Length | Best 4-position CSP pattern   |   Mean paired cosine |   Mean L2 drift |   Nearest-clean retrieval |   Features |
|:--------------------|---------:|:------------------------------|---------------------:|----------------:|--------------------------:|-----------:|
| 3% N mask           |       69 | 0-1-2-3                       |                0.994 |           0.106 |                     1.000 |        147 |
| 3% N mask           |       75 | 0-1-2-3                       |                0.995 |           0.098 |                     1.000 |        147 |
| 6-bp local mismatch |       69 | 0-1-2-3                       |                0.991 |           0.130 |                     1.000 |        147 |
| 6-bp local mismatch |       75 | 0-1-2-3                       |                0.992 |           0.124 |                     1.000 |        147 |
| 1% substitution     |       69 | 0-1-2-3                       |                0.997 |           0.051 |                     1.000 |        147 |
| 1% substitution     |       75 | 0-1-2-3                       |                0.998 |           0.051 |                     1.000 |        147 |

## Best clean readout setting within this spaced-pattern sanity run

Readout was skipped for this focused sanity run; the reported evidence is stability and feature-scale only.

Interpretation: the expanded four-position scan is a sensitivity check. A best pattern changing across cells should be read as evidence against a universal seed prescription, not as evidence that a newly observed best pattern is globally optimized.