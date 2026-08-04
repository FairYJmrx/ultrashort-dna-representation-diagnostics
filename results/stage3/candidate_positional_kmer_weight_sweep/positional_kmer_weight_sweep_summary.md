# Fixed-weight positional k-mer augment screen

Weights were prespecified before viewing this screen. This is a Pareto audit, not task-specific tuning.
A candidate can replace CK4P-MSP only after passing every scientific and engineering gate and reproducing under an independent seed/template split.

| representation    | representation_label   | route   |   candidate_weight |   n_features |   wgs_l2 |   wgs_retrieval |   local_macro_f1 |   motif_macro_f1 |   art_l2 |   cami_mean_retention |   runtime_seconds | runtime_source                                                        |   motif_gain_vs_main |   wgs_l2_change_vs_main |   wgs_retrieval_change_vs_main |   local_f1_change_vs_main |   art_l2_change_vs_main |   cami_retention_change_vs_main |   runtime_ratio_vs_main | pass_motif   | pass_wgs_l2   | pass_retrieval   | pass_local   | pass_art   | pass_cami   | pass_runtime   | eligible_scientific_confirmation   | eligible_main_confirmation   |
|:------------------|:-----------------------|:--------|-------------------:|-------------:|---------:|----------------:|-----------------:|-----------------:|---------:|----------------------:|------------------:|:----------------------------------------------------------------------|---------------------:|------------------------:|-------------------------------:|--------------------------:|------------------------:|--------------------------------:|------------------------:|:-------------|:--------------|:-----------------|:-------------|:-----------|:------------|:---------------|:-----------------------------------|:-----------------------------|
| ck4p_msp          | CK4P-MSP               | main    |             0.0000 |          222 |   0.1289 |          0.9999 |           0.8882 |           0.6323 |   0.1572 |                0.9910 |            0.7945 | direct route extraction; fixed weight does not change extraction cost |               0.0000 |                  0.0000 |                         0.0000 |                    0.0000 |                  0.0000 |                          0.0000 |                  1.0000 | False        | True          | True             | True         | True       | True        | True           | False                              | False                        |
| pkm_weight_w010  | PKM weight=0.1   | pkm     |             0.1000 |          297 |   0.1305 |          0.9998 |           0.9013 |           0.6480 |   0.1585 |                0.9908 |            1.4352 | direct route extraction; fixed weight does not change extraction cost |               0.0158 |                  0.0016 |                        -0.0001 |                    0.0131 |                  0.0013 |                         -0.0002 |                  1.8065 | False        | True          | True             | True         | True       | True        | True           | False                              | False                        |
| ck4p_msp_pkm_w025  | CK4P-MSP-PKM  | pkm     |             0.2500 |          297 |   0.1379 |          0.9999 |           0.9283 |           0.7103 |   0.1651 |                0.9928 |            1.4352 | direct route extraction; fixed weight does not change extraction cost |               0.0780 |                  0.0090 |                         0.0000 |                    0.0401 |                  0.0079 |                          0.0018 |                  1.8065 | True         | True          | True             | True         | True       | True        | True           | True                               | True                         |
| pkm_weight_w050  | PKM weight=0.5   | pkm     |             0.5000 |          297 |   0.1587 |          0.9999 |           0.9185 |           0.7574 |   0.1846 |                0.9984 |            1.4352 | direct route extraction; fixed weight does not change extraction cost |               0.1251 |                  0.0298 |                         0.0000 |                    0.0303 |                  0.0274 |                          0.0074 |                  1.8065 | True         | False         | True             | True         | False      | True        | True           | False                              | False                        |
| pkm_weight_w075  | PKM weight=0.75  | pkm     |             0.7500 |          297 |   0.1830 |          0.9999 |           0.8953 |           0.7475 |   0.2085 |                0.9994 |            1.4352 | direct route extraction; fixed weight does not change extraction cost |               0.1152 |                  0.0540 |                         0.0000 |                    0.0071 |                  0.0513 |                          0.0084 |                  1.8065 | True         | False         | True             | True         | False      | True        | True           | False                              | False                        |
| pkm_weight_w100  | PKM weight=1     | pkm     |             1.0000 |          297 |   0.2064 |          0.9999 |           0.8813 |           0.7435 |   0.2322 |                0.9964 |            1.4352 | direct route extraction; fixed weight does not change extraction cost |               0.1113 |                  0.0775 |                         0.0000 |                   -0.0069 |                  0.0750 |                          0.0054 |                  1.8065 | True         | False         | True             | True         | False      | True        | True           | False                              | False                        |
| cpkm_weight_w010 | CPKM weight=0.1  | cpkm    |             0.1000 |          297 |   0.1308 |          0.9999 |           0.8982 |           0.6402 |   0.1588 |                0.9914 |           17.0417 | direct route extraction; fixed weight does not change extraction cost |               0.0079 |                  0.0018 |                         0.0000 |                    0.0100 |                  0.0016 |                          0.0003 |                 21.4508 | False        | True          | True             | True         | True       | True        | False          | False                              | False                        |
| cpkm_weight_w025 | CPKM weight=0.25 | cpkm    |             0.2500 |          297 |   0.1394 |          0.9999 |           0.9234 |           0.7120 |   0.1663 |                0.9904 |           17.0417 | direct route extraction; fixed weight does not change extraction cost |               0.0797 |                  0.0105 |                         0.0000 |                    0.0352 |                  0.0091 |                         -0.0006 |                 21.4508 | True         | False         | True             | True         | True       | True        | False          | False                              | False                        |
| cpkm_weight_w050 | CPKM weight=0.5  | cpkm    |             0.5000 |          297 |   0.1632 |          0.9999 |           0.9153 |           0.7718 |   0.1884 |                0.9898 |           17.0417 | direct route extraction; fixed weight does not change extraction cost |               0.1395 |                  0.0343 |                         0.0000 |                    0.0271 |                  0.0312 |                         -0.0013 |                 21.4508 | True         | False         | True             | True         | False      | True        | False          | False                              | False                        |
| cpkm_weight_w075 | CPKM weight=0.75 | cpkm    |             0.7500 |          297 |   0.1909 |          0.9999 |           0.8859 |           0.7888 |   0.2151 |                0.9900 |           17.0417 | direct route extraction; fixed weight does not change extraction cost |               0.1565 |                  0.0619 |                         0.0000 |                   -0.0023 |                  0.0579 |                         -0.0010 |                 21.4508 | True         | False         | True             | True         | False      | True        | False          | False                              | False                        |
| cpkm_weight_w100 | CPKM weight=1    | cpkm    |             1.0000 |          297 |   0.2173 |          0.9999 |           0.8698 |           0.7884 |   0.2414 |                0.9860 |           17.0417 | direct route extraction; fixed weight does not change extraction cost |               0.1562 |                  0.0884 |                         0.0000 |                   -0.0184 |                  0.0842 |                         -0.0050 |                 21.4508 | True         | False         | True             | False        | False      | True        | False          | False                              | False                        |

## Outcome

Scientifically eligible for independent confirmation: ck4p_msp_pkm_w025

Eligible for main-method confirmation including runtime: ck4p_msp_pkm_w025

Runtime is measured directly for each extraction route; changing the fixed concatenation weight does not change extraction cost.

## Run metadata

```json
{
  "elapsed_seconds": 210.821,
  "weights": [
    0.1,
    0.25,
    0.5,
    0.75,
    1.0
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
  "seed": 20260805,
  "python": "3.13.9 | packaged by Anaconda, Inc. | (main, Oct 21 2025, 19:09:58) [MSC v.1929 64 bit (AMD64)]",
  "platform": "Windows-11-10.0.26200-SP0",
  "processor": "Intel64 Family 6 Model 170 Stepping 4, GenuineIntel"
}
```