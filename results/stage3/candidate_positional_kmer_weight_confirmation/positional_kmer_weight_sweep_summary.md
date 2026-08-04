# Fixed-weight positional k-mer augment screen

Weights were prespecified before viewing this screen. This is a Pareto audit, not task-specific tuning.
A candidate can replace CK4P-MSP only after passing every scientific and engineering gate and reproducing under an independent seed/template split.

| representation    | representation_label   | route   |   candidate_weight |   n_features |   wgs_l2 |   wgs_retrieval |   local_macro_f1 |   motif_macro_f1 |   art_l2 |   cami_mean_retention |   runtime_seconds | runtime_source                                                        |   motif_gain_vs_main |   wgs_l2_change_vs_main |   wgs_retrieval_change_vs_main |   local_f1_change_vs_main |   art_l2_change_vs_main |   cami_retention_change_vs_main |   runtime_ratio_vs_main | pass_motif   | pass_wgs_l2   | pass_retrieval   | pass_local   | pass_art   | pass_cami   | pass_runtime   | eligible_scientific_confirmation   | eligible_main_confirmation   |
|:------------------|:-----------------------|:--------|-------------------:|-------------:|---------:|----------------:|-----------------:|-----------------:|---------:|----------------------:|------------------:|:----------------------------------------------------------------------|---------------------:|------------------------:|-------------------------------:|--------------------------:|------------------------:|--------------------------------:|------------------------:|:-------------|:--------------|:-----------------|:-------------|:-----------|:------------|:---------------|:-----------------------------------|:-----------------------------|
| ck4p_msp          | CK4P-MSP               | main    |             0.0000 |          222 |   0.1286 |          0.9998 |           0.8882 |           0.6323 |   0.1581 |                1.0008 |            0.7830 | direct route extraction; fixed weight does not change extraction cost |               0.0000 |                  0.0000 |                         0.0000 |                    0.0000 |                  0.0000 |                          0.0000 |                  1.0000 | False        | True          | True             | True         | True       | True        | True           | False                              | False                        |
| ck4p_msp_pkm_w025  | CK4P-MSP-PKM  | pkm     |             0.2500 |          297 |   0.1376 |          0.9999 |           0.9283 |           0.7103 |   0.1662 |                1.0008 |            1.4448 | direct route extraction; fixed weight does not change extraction cost |               0.0780 |                  0.0090 |                         0.0001 |                    0.0401 |                  0.0081 |                          0.0000 |                  1.8453 | True         | True          | True             | True         | True       | True        | True           | True                               | True                         |
| cpkm_weight_w025 | CPKM weight=0.25 | cpkm    |             0.2500 |          297 |   0.1391 |          0.9999 |           0.9234 |           0.7120 |   0.1674 |                0.9978 |           17.1529 | direct route extraction; fixed weight does not change extraction cost |               0.0797 |                  0.0104 |                         0.0001 |                    0.0352 |                  0.0092 |                         -0.0030 |                 21.9077 | True         | False         | True             | True         | True       | True        | False          | False                              | False                        |

## Outcome

Scientifically eligible for independent confirmation: ck4p_msp_pkm_w025

Eligible for main-method confirmation including runtime: ck4p_msp_pkm_w025

Runtime is measured directly for each extraction route; changing the fixed concatenation weight does not change extraction cost.

## Run metadata

```json
{
  "elapsed_seconds": 181.926,
  "weights": [
    0.25
  ],
  "lengths": [
    69,
    75,
    100,
    150
  ],
  "conditions": [
    "substitution_1pct",
    "N_3pct",
    "trim_5bp",
    "substitution_1pct_N_3pct",
    "local_mismatch_6bp",
    "short_indel"
  ],
  "max_pairs": 500,
  "max_triplets": 400,
  "max_art_pairs_per_length": 2000,
  "max_cami_sources_per_class": 600,
  "runtime_reads": 10000,
  "runtime_repeats": 2,
  "cv_folds": 5,
  "local_probe_scaling": "none (contract-space primary)",
  "seed": 20260819,
  "python": "3.13.9 | packaged by Anaconda, Inc. | (main, Oct 21 2025, 19:09:58) [MSC v.1929 64 bit (AMD64)]",
  "platform": "Windows-11-10.0.26200-SP0",
  "processor": "Intel64 Family 6 Model 170 Stepping 4, GenuineIntel"
}
```