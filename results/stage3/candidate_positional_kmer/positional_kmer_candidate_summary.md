# Positional k-mer candidate screen

This is a prespecified engineering screen, not a confirmatory superiority test.
The current CK4P-MSP method remains unchanged unless a candidate passes all gates and then reproduces on an independent seed or template split.

| representation         | representation_label             |   n_features |   wgs_l2 |   wgs_retrieval |   local_macro_f1 |   motif_macro_f1 |   art_l2 |   cami_mean_retention |   runtime_seconds |   motif_gain_vs_main |   wgs_l2_change_vs_main |   wgs_retrieval_change_vs_main |   local_f1_change_vs_main |   art_l2_change_vs_main |   cami_retention_change_vs_main |   runtime_ratio_vs_main | screen_pass_motif   | screen_pass_wgs_l2   | screen_pass_retrieval   | screen_pass_local   | screen_pass_art   | screen_pass_cami   | screen_pass_runtime   | eligible_for_independent_confirmation   |
|:-----------------------|:---------------------------------|-------------:|---------:|----------------:|-----------------:|-----------------:|---------:|----------------------:|------------------:|---------------------:|------------------------:|-------------------------------:|--------------------------:|------------------------:|--------------------------------:|------------------------:|:--------------------|:---------------------|:------------------------|:--------------------|:------------------|:-------------------|:----------------------|:----------------------------------------|
| ck4                    | CK4                              |          136 |   0.2188 |          0.9998 |           0.8923 |           0.6581 |   0.2709 |                0.9896 |          nan      |               0.0258 |                  0.0899 |                        -0.0001 |                   -0.0863 |                  0.1137 |                         -0.0015 |                nan      | True                | False                | True                    | False               | False             | True               | False                 | False                                   |
| ck5                    | CK5                              |          512 |   0.2932 |          0.9998 |           0.8663 |           0.6861 |   0.3583 |                0.9895 |          nan      |               0.0538 |                  0.1643 |                        -0.0001 |                   -0.1124 |                  0.2011 |                         -0.0016 |                nan      | True                | False                | True                    | False               | False             | True               | False                 | False                                   |
| ck4p_msp               | CK4P-MSP                         |          222 |   0.1289 |          0.9999 |           0.9786 |           0.6323 |   0.1572 |                0.9910 |            0.7978 |               0.0000 |                  0.0000 |                         0.0000 |                    0.0000 |                  0.0000 |                          0.0000 |                  1.0000 | False               | True                 | True                    | True                | True              | True               | True                  | False                                   |
| candidate_pkm_replace  | PKM replace (222D)               |          222 |   0.2377 |          0.9999 |           0.9347 |           0.7479 |   0.2680 |                0.9977 |            1.9654 |               0.1157 |                  0.1088 |                         0.0000 |                   -0.0439 |                  0.1108 |                          0.0067 |                  2.4636 | True                | False                | True                    | False               | False             | True               | False                 | False                                   |
| candidate_cpkm_replace | CPKM replace (222D)              |          222 |   0.2504 |          0.9999 |           0.9303 |           0.7920 |   0.2787 |                0.9854 |           15.5216 |               0.1597 |                  0.1214 |                         0.0000 |                   -0.0483 |                  0.1215 |                         -0.0056 |                 19.4558 | True                | False                | True                    | False               | False             | True               | False                 | False                                   |
| candidate_pkm_augment  | PKM augmentation screen (297D)           |          297 |   0.2064 |          0.9999 |           0.9796 |           0.7435 |   0.2322 |                0.9964 |            2.2818 |               0.1113 |                  0.0775 |                         0.0000 |                    0.0010 |                  0.0750 |                          0.0054 |                  2.8601 | True                | False                | True                    | True                | False             | True               | False                 | False                                   |
| candidate_cpkm_augment | CPKM augmentation screen (297D)          |          297 |   0.2173 |          0.9999 |           0.9790 |           0.7884 |   0.2414 |                0.9860 |           15.4457 |               0.1562 |                  0.0884 |                         0.0000 |                    0.0003 |                  0.0842 |                         -0.0050 |                 19.3606 | True                | False                | True                    | True                | False             | True               | False                 | False                                   |
| candidate_dual_augment | PKM-CPKM upper screen (372D) |          372 |   0.2483 |          0.9998 |           0.9806 |           0.7818 |   0.2738 |                0.9937 |           17.1086 |               0.1495 |                  0.1193 |                        -0.0001 |                    0.0020 |                  0.1166 |                          0.0027 |                 21.4450 | True                | False                | True                    | True                | False             | True               | False                 | False                                   |

## Screen outcome

No candidate passed every prespecified gate.

ART and CAMI are lightweight screening subsets at this stage; a passing candidate requires full-layer reruns.

## Run metadata

```json
{
  "elapsed_seconds": 285.551,
  "representations": [
    "ck4",
    "ck5",
    "ck4p_msp",
    "candidate_pkm_replace",
    "candidate_cpkm_replace",
    "candidate_pkm_augment",
    "candidate_cpkm_augment",
    "candidate_dual_augment"
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
  "seed": 20260805,
  "python": "3.13.9 | packaged by Anaconda, Inc. | (main, Oct 21 2025, 19:09:58) [MSC v.1929 64 bit (AMD64)]",
  "platform": "Windows-11-10.0.26200-SP0",
  "processor": "Intel64 Family 6 Model 170 Stepping 4, GenuineIntel"
}
```