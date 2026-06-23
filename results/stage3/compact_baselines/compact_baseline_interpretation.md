# Stage-3 Compact Baseline Interpretation

This note summarizes the completed MinHash/EIIP compact-baseline run. It should be treated as completed evidence, unlike ART/CAMI results that still require external tool/data execution.

## Run scope

- Reads analyzed: 25,200 WGS-derived rows across 69, 75, 100, 110, 125, 150 and 300 bp.

- Representations: canonical k-mer, canonical spaced count, CSP, hybrid k-mer+CSP, MinHash sketches and EIIP baselines.

- Perturbations: substitution, N masking, trim, substitution+N, short indel and local mismatch.

## Stability winners by perturbation family

### N_3pct

- 300 bp: cspaced_property_l2 cosine=0.997, L2=0.077, retrieval=1.000, dim=147.

- 150 bp: cspaced_property_l2 cosine=0.996, L2=0.087, retrieval=1.000, dim=147.

- 75 bp: cspaced_property_l2 cosine=0.995, L2=0.101, retrieval=1.000, dim=147.

### local_mismatch_6bp

- 300 bp: eiip_summary_l2 cosine=1.000, L2=0.004, retrieval=0.068, dim=8.

- 75 bp: eiip_summary_l2 cosine=1.000, L2=0.014, retrieval=0.037, dim=8.

- 69 bp: eiip_summary_l2 cosine=1.000, L2=0.015, retrieval=0.022, dim=8.

### short_indel

- 300 bp: eiip_summary_l2 cosine=0.999, L2=0.019, retrieval=0.090, dim=8.

- 69 bp: eiip_summary_l2 cosine=0.999, L2=0.023, retrieval=0.557, dim=8.

- 300 bp: cspaced_property_l2 cosine=0.999, L2=0.045, retrieval=1.000, dim=147.

### substitution_1pct

- 300 bp: eiip_summary_l2 cosine=1.000, L2=0.003, retrieval=0.203, dim=8.

- 69 bp: eiip_summary_l2 cosine=1.000, L2=0.003, retrieval=0.665, dim=8.

- 75 bp: eiip_summary_l2 cosine=1.000, L2=0.003, retrieval=0.623, dim=8.

### substitution_1pct_N_3pct

- 300 bp: cspaced_property_l2 cosine=0.996, L2=0.088, retrieval=1.000, dim=147.

- 150 bp: cspaced_property_l2 cosine=0.994, L2=0.104, retrieval=1.000, dim=147.

- 125 bp: cspaced_property_l2 cosine=0.993, L2=0.120, retrieval=1.000, dim=147.

### trim_5bp

- 300 bp: cspaced_property_l2 cosine=1.000, L2=0.021, retrieval=1.000, dim=147.

- 150 bp: cspaced_property_l2 cosine=0.999, L2=0.040, retrieval=1.000, dim=147.

- 125 bp: cspaced_property_l2 cosine=0.999, L2=0.046, retrieval=1.000, dim=147.

## Representation-level interpretation

- cspaced_property_l2: mean cosine=0.996, mean L2=0.079, mean retrieval=1.000, median dim=147.

- minhash_k5_s128: mean cosine=0.951, mean L2=0.266, mean retrieval=1.000, median dim=128.

- minhash_k7_s128: mean cosine=0.925, mean L2=0.338, mean retrieval=0.999, median dim=128.

- eiip_l2: mean cosine=0.988, mean L2=0.129, mean retrieval=0.943, median dim=112.

- eiip_summary_l2: mean cosine=0.979, mean L2=0.139, mean retrieval=0.148, median dim=8.

- hybrid_ckmer5_csp: mean cosine=0.973, mean L2=0.205, mean retrieval=1.000, median dim=659.

- ckmer5_count_l2: mean cosine=0.951, mean L2=0.278, mean retrieval=1.000, median dim=512.


## Readout probe caveat

Readout F1 values are intentionally lightweight probes rather than clinical classifier claims. The compact-baseline run shows no single representation dominates every label/length/noise condition, supporting a bounded paper claim: CSP is a compact perturbation-stable auxiliary block, while exact k-mer and hybrid features remain important for identity evidence.


## Best readout probes by task/condition/length

| task                 | condition                |   length | representation      | classifier       |   macro_f1 |   accuracy |   n_features |
|:---------------------|:-------------------------|---------:|:--------------------|:-----------------|-----------:|-----------:|-------------:|
| target_background    | N_3pct                   |       69 | ckmer5_count_l2     | logistic         |      0.721 |      0.750 |          491 |
| target_background    | N_3pct                   |       75 | cspaced_property_l2 | logistic         |      0.812 |      0.833 |          147 |
| target_background    | N_3pct                   |      100 | cspaced_property_l2 | nearest_centroid |      0.697 |      0.750 |          146 |
| target_background    | N_3pct                   |      150 | eiip_l2             | nearest_centroid |      0.697 |      0.750 |          150 |
| target_background    | clean                    |       69 | cspaced_count_l2    | nearest_centroid |      0.714 |      0.722 |          136 |
| target_background    | clean                    |       75 | eiip_l2             | logistic         |      0.867 |      0.875 |           75 |
| target_background    | clean                    |      100 | cspaced_count_l2    | logistic         |      0.733 |      0.750 |          135 |
| target_background    | clean                    |      150 | eiip_l2             | logistic         |      0.635 |      0.643 |          150 |
| target_background    | substitution_1pct        |       69 | eiip_l2             | logistic         |      0.721 |      0.722 |           69 |
| target_background    | substitution_1pct        |       75 | eiip_l2             | logistic         |      0.867 |      0.875 |           75 |
| target_background    | substitution_1pct        |      100 | cspaced_count_l2    | logistic         |      0.734 |      0.778 |          136 |
| target_background    | substitution_1pct        |      150 | minhash_k5_s128     | logistic         |      0.673 |      0.714 |          128 |
| target_background    | substitution_1pct_N_3pct |       69 | minhash_k5_s128     | nearest_centroid |      0.665 |      0.667 |          128 |
| target_background    | substitution_1pct_N_3pct |       75 | eiip_summary_l2     | nearest_centroid |      0.733 |      0.750 |            8 |
| target_background    | substitution_1pct_N_3pct |      100 | cspaced_count_l2    | nearest_centroid |      0.758 |      0.792 |          135 |
| target_background    | substitution_1pct_N_3pct |      150 | eiip_summary_l2     | logistic         |      0.721 |      0.722 |            8 |
| target_background    | trim_5bp                 |       69 | cspaced_count_l2    | nearest_centroid |      0.714 |      0.722 |          136 |
| target_background    | trim_5bp                 |       75 | eiip_l2             | nearest_centroid |      0.792 |      0.812 |           75 |
| target_background    | trim_5bp                 |      100 | cspaced_property_l2 | logistic         |      0.719 |      0.750 |          146 |
| target_background    | trim_5bp                 |      150 | eiip_summary_l2     | nearest_centroid |      0.642 |      0.679 |            8 |
| within_genus_species | N_3pct                   |       69 | hybrid_ckmer5_csp   | logistic         |      0.714 |      0.722 |          653 |
| within_genus_species | N_3pct                   |       75 | eiip_l2             | logistic         |      0.806 |      0.812 |           75 |
| within_genus_species | N_3pct                   |      100 | ckmer5_count_l2     | logistic         |      0.667 |      0.667 |          509 |
| within_genus_species | N_3pct                   |      150 | eiip_summary_l2     | nearest_centroid |      0.662 |      0.667 |            8 |
| within_genus_species | clean                    |       69 | cspaced_count_l2    | nearest_centroid |      0.714 |      0.722 |          136 |
| within_genus_species | clean                    |       75 | eiip_l2             | logistic         |      0.867 |      0.875 |           75 |
| within_genus_species | clean                    |      100 | hybrid_ckmer5_csp   | logistic         |      0.611 |      0.619 |          657 |
| within_genus_species | clean                    |      150 | ckmer5_count_l2     | nearest_centroid |      0.600 |      0.611 |          508 |
| within_genus_species | substitution_1pct        |       69 | eiip_l2             | logistic         |      0.721 |      0.722 |           69 |
| within_genus_species | substitution_1pct        |       75 | eiip_l2             | logistic         |      0.867 |      0.875 |           75 |
| within_genus_species | substitution_1pct        |      100 | ckmer5_count_l2     | nearest_centroid |      0.667 |      0.667 |          510 |
| within_genus_species | substitution_1pct        |      150 | ckmer5_count_l2     | logistic         |      0.600 |      0.611 |          511 |
| within_genus_species | substitution_1pct_N_3pct |       69 | eiip_l2             | logistic         |      0.649 |      0.667 |           69 |
| within_genus_species | substitution_1pct_N_3pct |       75 | eiip_summary_l2     | nearest_centroid |      0.733 |      0.750 |            8 |
| within_genus_species | substitution_1pct_N_3pct |      100 | eiip_summary_l2     | nearest_centroid |      0.611 |      0.619 |            8 |
| within_genus_species | substitution_1pct_N_3pct |      150 | eiip_summary_l2     | logistic         |      0.721 |      0.722 |            8 |
| within_genus_species | trim_5bp                 |       69 | cspaced_count_l2    | nearest_centroid |      0.714 |      0.722 |          136 |
| within_genus_species | trim_5bp                 |       75 | eiip_l2             | nearest_centroid |      0.792 |      0.812 |           75 |
| within_genus_species | trim_5bp                 |      100 | ckmer5_count_l2     | logistic         |      0.611 |      0.619 |          509 |
| within_genus_species | trim_5bp                 |      150 | eiip_l2             | nearest_centroid |      0.550 |      0.556 |          150 |

