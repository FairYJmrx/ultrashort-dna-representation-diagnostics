# Close-relative benchmark and prior-ablation results

## Data source

The close-relative benchmark was constructed from the blood-panel Excel metadata and RefSeq/NCBI Datasets FASTA files. It contains six clinically relevant genera with target pathogens and close-relative or background species.

| Genus | Genomes | Target pathogens | Close/background |
|---|---:|---:|---:|
| Acinetobacter | 4 | 0 | 4 |
| Burkholderia | 3 | 1 | 2 |
| Candida | 4 | 3 | 1 |
| Enterobacter | 5 | 1 | 4 |
| Escherichia | 2 | 1 | 1 |
| Klebsiella | 3 | 1 | 2 |

Each genome was sampled into 69, 75, 100, 125, and 150 bp single-end reads plus a PE150 proxy formed by concatenating R1 and reverse-complemented R2. For the close-relative core experiment, the report focuses on 75, 125, 150, and PE150 under clean and N_3pct conditions.

## Component definitions used for ablation

| Representation | Components | Short definition |
|---|---|---|
| kmer5_count_l2 | contiguous k-mer | Contiguous 5-mer count vector with L2 normalization. |
| ckmer5_count_l2 | contiguous k-mer, canonical RC | 5-mer counts after min(k-mer, reverse-complement k-mer) canonicalization. |
| spaced_count_l2 | spaced seed | Spaced seed counts using pattern positions (0,2,4,6). |
| cspaced_count_l2 | spaced seed, canonical RC | Spaced seed counts with reverse-complement canonicalization. |
| cspaced_property_l2 | spaced seed, canonical RC, DNA property | Canonical spaced seed counts concatenated with DNA property summaries and L2 normalization. |
| property_channels | DNA property | Per-position hydrogen-bond, GC, purine, EIIP and N-mask channels. |
| spaced_kmer_no_phase | spaced seed, DNA property | Spaced token property sequence without explicit three-phase position signal. |
| spaced_kmer_phase | spaced seed, DNA property, phase | Spaced token property sequence with sine/cosine start-position phase. |
| rope_onehot | RoPE | One-hot base vectors rotated by RoPE-like positional phases. |
| rope_property | DNA property, RoPE | DNA property vectors rotated by RoPE-like positional phases. |

## Ablation findings

### Reverse-complement consistency

| Evidence set | Length | Best representation | Mean paired cosine | P05 paired cosine |
|---|---:|---|---:|---:|
| close_relative_wgs | 75 | ckmer5_count_l2 | 1.000 | 1.000 |
| close_relative_wgs | 150 | ckmer5_count_l2 | 1.000 | 1.000 |
| close_relative_wgs | 300 | ckmer5_count_l2 | 1.000 | 1.000 |
| toy_control | 75 | ckmer5_count_l2 | 1.000 | 1.000 |

Canonicalization is the decisive source of strand robustness:

| Evidence set | Comparison | Length | Delta mean paired cosine | Delta P05 paired cosine |
|---|---|---:|---:|---:|
| close_relative_wgs | canonicalization_on_contiguous | 75 | 0.875 | 1.000 |
| close_relative_wgs | canonicalization_on_contiguous | 100 | 0.849 | 0.966 |
| close_relative_wgs | canonicalization_on_contiguous | 125 | 0.821 | 0.943 |
| close_relative_wgs | canonicalization_on_contiguous | 150 | 0.799 | 0.926 |
| close_relative_wgs | canonicalization_on_contiguous | 300 | 0.658 | 0.794 |
| close_relative_wgs | canonicalization_on_spaced | 75 | 0.692 | 0.871 |
| close_relative_wgs | canonicalization_on_spaced | 100 | 0.640 | 0.824 |
| close_relative_wgs | canonicalization_on_spaced | 125 | 0.595 | 0.775 |
| close_relative_wgs | canonicalization_on_spaced | 150 | 0.558 | 0.729 |
| close_relative_wgs | canonicalization_on_spaced | 300 | 0.383 | 0.512 |
| toy_control | canonicalization_on_contiguous | 75 | 0.877 | 1.000 |
| toy_control | canonicalization_on_contiguous | 100 | 0.849 | 0.982 |
| toy_control | canonicalization_on_spaced | 75 | 0.676 | 0.852 |
| toy_control | canonicalization_on_spaced | 100 | 0.616 | 0.794 |

### Perturbation stability

| Evidence set | Condition | Length | Best representation | Mean paired cosine | Mean L2 delta |
|---|---|---:|---|---:|---:|
| close_relative_wgs | N_3pct | 75 | cspaced_property_l2 | 0.995 | 0.101 |
| close_relative_wgs | N_3pct | 100 | cspaced_property_l2 | 0.995 | 0.103 |
| close_relative_wgs | N_3pct | 125 | cspaced_property_l2 | 0.995 | 0.103 |
| close_relative_wgs | N_3pct | 150 | cspaced_property_l2 | 0.996 | 0.087 |
| close_relative_wgs | N_3pct | 300 | cspaced_property_l2 | 0.997 | 0.077 |
| close_relative_wgs | substitution_1pct | 75 | property_channels | 0.999 | 0.036 |
| close_relative_wgs | substitution_1pct | 100 | property_channels | 0.999 | 0.041 |
| close_relative_wgs | substitution_1pct | 125 | property_channels | 0.999 | 0.044 |
| close_relative_wgs | substitution_1pct | 150 | property_channels | 0.999 | 0.044 |
| close_relative_wgs | substitution_1pct | 300 | cspaced_property_l2 | 0.999 | 0.039 |
| toy_control | N_3pct | 75 | cspaced_property_l2 | 0.995 | 0.096 |
| toy_control | N_3pct | 100 | cspaced_property_l2 | 0.995 | 0.098 |
| toy_control | substitution_1pct | 75 | property_channels | 0.999 | 0.035 |
| toy_control | substitution_1pct | 100 | property_channels | 0.999 | 0.041 |

Adding property summaries to canonical spaced counts changes perturbation stability as follows:

| Evidence set | Condition | Length | Delta mean paired cosine | Delta mean L2 delta |
|---|---|---:|---:|---:|
| close_relative_wgs | N_3pct | 75 | 0.028 | -0.154 |
| close_relative_wgs | N_3pct | 100 | 0.027 | -0.150 |
| close_relative_wgs | N_3pct | 125 | 0.026 | -0.144 |
| close_relative_wgs | N_3pct | 150 | 0.019 | -0.126 |
| close_relative_wgs | N_3pct | 300 | 0.014 | -0.104 |
| close_relative_wgs | substitution_1pct | 75 | 0.021 | -0.102 |
| close_relative_wgs | substitution_1pct | 100 | 0.019 | -0.108 |
| close_relative_wgs | substitution_1pct | 125 | 0.017 | -0.110 |
| close_relative_wgs | substitution_1pct | 150 | 0.015 | -0.106 |
| close_relative_wgs | substitution_1pct | 300 | 0.009 | -0.094 |
| toy_control | N_3pct | 75 | 0.025 | -0.146 |
| toy_control | N_3pct | 100 | 0.024 | -0.140 |
| toy_control | substitution_1pct | 75 | 0.020 | -0.100 |
| toy_control | substitution_1pct | 100 | 0.018 | -0.106 |

### Motif-position task

| Condition | Length | Best representation | Macro-F1 |
|---|---:|---|---:|
| N_3pct | 75 | spaced_kmer_no_phase | 0.638 |
| N_3pct | 100 | rope_onehot | 0.503 |
| clean | 75 | spaced_kmer_no_phase | 0.638 |
| clean | 100 | spaced_kmer_no_phase | 0.540 |

The explicit phase component is evaluated by comparing spaced_kmer_no_phase with spaced_kmer_phase:

| Condition | Length | Delta macro-F1 |
|---|---:|---:|
| N_3pct | 75 | 0.000 |
| N_3pct | 100 | 0.000 |
| clean | 75 | 0.000 |
| clean | 100 | 0.000 |

## Close-relative classification findings

### Within-genus species labels

| Genus | Condition | Length | Best representation | Macro-F1 | Accuracy |
|---|---|---:|---|---:|---:|
| Acinetobacter | N_3pct | 69 | spaced_kmer_phase | 0.263 | 0.260 |
| Acinetobacter | N_3pct | 75 | ckmer5_count_l2 | 0.263 | 0.260 |
| Acinetobacter | N_3pct | 100 | cspaced_count_l2 | 0.292 | 0.292 |
| Acinetobacter | N_3pct | 125 | cspaced_property_l2 | 0.303 | 0.312 |
| Acinetobacter | N_3pct | 150 | spaced_kmer_phase | 0.372 | 0.375 |
| Acinetobacter | N_3pct | 300 | ckmer5_count_l2 | 0.312 | 0.312 |
| Acinetobacter | clean | 69 | cspaced_property_l2 | 0.283 | 0.281 |
| Acinetobacter | clean | 75 | spaced_kmer_phase | 0.311 | 0.323 |
| Acinetobacter | clean | 100 | ckmer5_count_l2 | 0.297 | 0.302 |
| Acinetobacter | clean | 125 | cspaced_property_l2 | 0.336 | 0.354 |
| Acinetobacter | clean | 150 | rope_property | 0.397 | 0.396 |
| Acinetobacter | clean | 300 | ckmer5_count_l2 | 0.329 | 0.333 |
| Burkholderia | N_3pct | 69 | ckmer5_count_l2 | 0.375 | 0.375 |
| Burkholderia | N_3pct | 75 | spaced_kmer_phase | 0.388 | 0.389 |
| Burkholderia | N_3pct | 100 | rope_property | 0.416 | 0.417 |
| Burkholderia | N_3pct | 125 | ckmer5_count_l2 | 0.430 | 0.431 |
| Burkholderia | N_3pct | 150 | cspaced_count_l2 | 0.402 | 0.403 |
| Burkholderia | N_3pct | 300 | ckmer5_count_l2 | 0.406 | 0.403 |
| Burkholderia | clean | 69 | cspaced_property_l2 | 0.358 | 0.361 |
| Burkholderia | clean | 75 | spaced_kmer_phase | 0.418 | 0.417 |
| Burkholderia | clean | 100 | rope_property | 0.443 | 0.444 |
| Burkholderia | clean | 125 | ckmer5_count_l2 | 0.454 | 0.458 |
| Burkholderia | clean | 150 | cspaced_count_l2 | 0.415 | 0.417 |
| Burkholderia | clean | 300 | ckmer5_count_l2 | 0.401 | 0.403 |
| Candida | N_3pct | 69 | spaced_kmer_phase | 0.316 | 0.323 |
| Candida | N_3pct | 75 | cspaced_property_l2 | 0.337 | 0.344 |
| Candida | N_3pct | 100 | cspaced_property_l2 | 0.388 | 0.406 |
| Candida | N_3pct | 125 | cspaced_property_l2 | 0.379 | 0.396 |
| Candida | N_3pct | 150 | cspaced_property_l2 | 0.372 | 0.396 |
| Candida | N_3pct | 300 | spaced_kmer_phase | 0.340 | 0.344 |
| Candida | clean | 69 | rope_property | 0.308 | 0.323 |
| Candida | clean | 75 | cspaced_count_l2 | 0.378 | 0.385 |
| Candida | clean | 100 | cspaced_count_l2 | 0.412 | 0.427 |
| Candida | clean | 125 | cspaced_property_l2 | 0.363 | 0.385 |
| Candida | clean | 150 | cspaced_property_l2 | 0.370 | 0.385 |
| Candida | clean | 300 | cspaced_count_l2 | 0.330 | 0.354 |
| Enterobacter | N_3pct | 69 | spaced_kmer_phase | 0.222 | 0.225 |
| Enterobacter | N_3pct | 75 | spaced_kmer_phase | 0.243 | 0.242 |
| Enterobacter | N_3pct | 100 | ckmer5_count_l2 | 0.243 | 0.242 |
| Enterobacter | N_3pct | 125 | cspaced_property_l2 | 0.263 | 0.275 |
| Enterobacter | N_3pct | 150 | rope_property | 0.225 | 0.233 |
| Enterobacter | N_3pct | 300 | rope_property | 0.233 | 0.233 |
| Enterobacter | clean | 69 | spaced_kmer_phase | 0.224 | 0.233 |
| Enterobacter | clean | 75 | spaced_kmer_phase | 0.221 | 0.225 |
| Enterobacter | clean | 100 | ckmer5_count_l2 | 0.255 | 0.258 |
| Enterobacter | clean | 125 | ckmer5_count_l2 | 0.277 | 0.283 |
| Enterobacter | clean | 150 | ckmer5_count_l2 | 0.217 | 0.217 |
| Enterobacter | clean | 300 | ckmer5_count_l2 | 0.231 | 0.233 |
| Escherichia | N_3pct | 69 | cspaced_count_l2 | 0.644 | 0.646 |
| Escherichia | N_3pct | 75 | cspaced_count_l2 | 0.644 | 0.646 |
| Escherichia | N_3pct | 100 | cspaced_property_l2 | 0.604 | 0.604 |
| Escherichia | N_3pct | 125 | cspaced_property_l2 | 0.684 | 0.688 |
| Escherichia | N_3pct | 150 | ckmer5_count_l2 | 0.407 | 0.417 |
| Escherichia | N_3pct | 300 | cspaced_count_l2 | 0.562 | 0.562 |
| Escherichia | clean | 69 | cspaced_count_l2 | 0.664 | 0.667 |
| Escherichia | clean | 75 | rope_property | 0.553 | 0.562 |
| Escherichia | clean | 100 | cspaced_count_l2 | 0.583 | 0.583 |
| Escherichia | clean | 125 | cspaced_count_l2 | 0.614 | 0.625 |
| Escherichia | clean | 150 | rope_property | 0.365 | 0.375 |
| Escherichia | clean | 300 | spaced_kmer_phase | 0.561 | 0.562 |
| Klebsiella | N_3pct | 69 | rope_property | 0.468 | 0.472 |
| Klebsiella | N_3pct | 75 | ckmer5_count_l2 | 0.419 | 0.417 |
| Klebsiella | N_3pct | 100 | spaced_kmer_phase | 0.388 | 0.389 |
| Klebsiella | N_3pct | 125 | spaced_kmer_phase | 0.403 | 0.403 |
| Klebsiella | N_3pct | 150 | rope_property | 0.375 | 0.375 |
| Klebsiella | N_3pct | 300 | spaced_kmer_phase | 0.428 | 0.431 |
| Klebsiella | clean | 69 | rope_property | 0.470 | 0.472 |
| Klebsiella | clean | 75 | ckmer5_count_l2 | 0.460 | 0.458 |
| Klebsiella | clean | 100 | ckmer5_count_l2 | 0.430 | 0.431 |
| Klebsiella | clean | 125 | cspaced_count_l2 | 0.407 | 0.417 |
| Klebsiella | clean | 150 | rope_property | 0.418 | 0.417 |
| Klebsiella | clean | 300 | spaced_kmer_phase | 0.472 | 0.472 |

### Target pathogen versus close-relative/background labels

| Genus | Condition | Length | Best representation | Macro-F1 | Accuracy |
|---|---|---:|---|---:|---:|
| Burkholderia | N_3pct | 69 | rope_property | 0.437 | 0.472 |
| Burkholderia | N_3pct | 75 | spaced_kmer_phase | 0.641 | 0.653 |
| Burkholderia | N_3pct | 100 | spaced_kmer_phase | 0.639 | 0.667 |
| Burkholderia | N_3pct | 125 | spaced_kmer_phase | 0.615 | 0.639 |
| Burkholderia | N_3pct | 150 | cspaced_count_l2 | 0.613 | 0.653 |
| Burkholderia | N_3pct | 300 | cspaced_property_l2 | 0.603 | 0.625 |
| Burkholderia | clean | 69 | spaced_kmer_phase | 0.440 | 0.458 |
| Burkholderia | clean | 75 | spaced_kmer_phase | 0.641 | 0.653 |
| Burkholderia | clean | 100 | spaced_kmer_phase | 0.597 | 0.625 |
| Burkholderia | clean | 125 | ckmer5_count_l2 | 0.632 | 0.653 |
| Burkholderia | clean | 150 | ckmer5_count_l2 | 0.573 | 0.597 |
| Burkholderia | clean | 300 | spaced_kmer_phase | 0.597 | 0.667 |
| Candida | N_3pct | 69 | ckmer5_count_l2 | 0.535 | 0.656 |
| Candida | N_3pct | 75 | ckmer5_count_l2 | 0.554 | 0.635 |
| Candida | N_3pct | 100 | ckmer5_count_l2 | 0.605 | 0.677 |
| Candida | N_3pct | 125 | cspaced_count_l2 | 0.515 | 0.562 |
| Candida | N_3pct | 150 | ckmer5_count_l2 | 0.629 | 0.688 |
| Candida | N_3pct | 300 | cspaced_count_l2 | 0.605 | 0.667 |
| Candida | clean | 69 | ckmer5_count_l2 | 0.570 | 0.656 |
| Candida | clean | 75 | ckmer5_count_l2 | 0.588 | 0.667 |
| Candida | clean | 100 | cspaced_property_l2 | 0.588 | 0.646 |
| Candida | clean | 125 | rope_property | 0.479 | 0.594 |
| Candida | clean | 150 | ckmer5_count_l2 | 0.645 | 0.698 |
| Candida | clean | 300 | ckmer5_count_l2 | 0.652 | 0.698 |
| Enterobacter | N_3pct | 69 | rope_property | 0.549 | 0.725 |
| Enterobacter | N_3pct | 75 | spaced_kmer_phase | 0.550 | 0.625 |
| Enterobacter | N_3pct | 100 | spaced_kmer_phase | 0.527 | 0.642 |
| Enterobacter | N_3pct | 125 | spaced_kmer_phase | 0.522 | 0.633 |
| Enterobacter | N_3pct | 150 | ckmer5_count_l2 | 0.557 | 0.717 |
| Enterobacter | N_3pct | 300 | cspaced_property_l2 | 0.525 | 0.625 |
| Enterobacter | clean | 69 | cspaced_property_l2 | 0.483 | 0.592 |
| Enterobacter | clean | 75 | ckmer5_count_l2 | 0.556 | 0.667 |
| Enterobacter | clean | 100 | rope_property | 0.543 | 0.717 |
| Enterobacter | clean | 125 | ckmer5_count_l2 | 0.517 | 0.642 |
| Enterobacter | clean | 150 | ckmer5_count_l2 | 0.583 | 0.733 |
| Enterobacter | clean | 300 | cspaced_count_l2 | 0.549 | 0.658 |
| Escherichia | N_3pct | 69 | spaced_kmer_phase | 0.661 | 0.667 |
| Escherichia | N_3pct | 75 | ckmer5_count_l2 | 0.500 | 0.500 |
| Escherichia | N_3pct | 100 | ckmer5_count_l2 | 0.561 | 0.562 |
| Escherichia | N_3pct | 125 | cspaced_count_l2 | 0.600 | 0.604 |
| Escherichia | N_3pct | 150 | ckmer5_count_l2 | 0.473 | 0.479 |
| Escherichia | N_3pct | 300 | rope_property | 0.580 | 0.583 |
| Escherichia | clean | 69 | cspaced_count_l2 | 0.644 | 0.646 |
| Escherichia | clean | 75 | ckmer5_count_l2 | 0.457 | 0.458 |
| Escherichia | clean | 100 | ckmer5_count_l2 | 0.604 | 0.604 |
| Escherichia | clean | 125 | cspaced_count_l2 | 0.561 | 0.562 |
| Escherichia | clean | 150 | cspaced_count_l2 | 0.455 | 0.458 |
| Escherichia | clean | 300 | rope_property | 0.666 | 0.667 |
| Klebsiella | N_3pct | 69 | spaced_kmer_phase | 0.573 | 0.597 |
| Klebsiella | N_3pct | 75 | cspaced_count_l2 | 0.651 | 0.681 |
| Klebsiella | N_3pct | 100 | ckmer5_count_l2 | 0.532 | 0.556 |
| Klebsiella | N_3pct | 125 | cspaced_count_l2 | 0.579 | 0.611 |
| Klebsiella | N_3pct | 150 | spaced_kmer_phase | 0.548 | 0.583 |
| Klebsiella | N_3pct | 300 | cspaced_count_l2 | 0.632 | 0.667 |
| Klebsiella | clean | 69 | ckmer5_count_l2 | 0.556 | 0.583 |
| Klebsiella | clean | 75 | rope_property | 0.617 | 0.667 |
| Klebsiella | clean | 100 | spaced_kmer_phase | 0.542 | 0.597 |
| Klebsiella | clean | 125 | cspaced_property_l2 | 0.602 | 0.639 |
| Klebsiella | clean | 150 | spaced_kmer_phase | 0.619 | 0.681 |
| Klebsiella | clean | 300 | cspaced_count_l2 | 0.602 | 0.639 |

## Reviewer-facing interpretation

1. The previous experiments did not fully test close-relative separation. The new benchmark adds six genera and 21 genomes, including Candida, Klebsiella, Acinetobacter, Burkholderia, Enterobacter, and Escherichia.
2. The close-relative task should be interpreted as a lightweight representation-stress test, not as a clinical mNGS classifier. Random genome slices avoid cherry-picking similar regions; they allow natural conserved and divergent regions to appear in the sampled reads.
3. The ablation is necessary because cspaced_property_l2 and related methods mix multiple priors. The results separate the effects of spaced seeds, reverse-complement canonicalization, property summaries, phase, and RoPE-like position.
4. A defensible claim is not that the proposed methods dominate canonical k-mers in species classification. The safer claim is that canonical spaced-property features provide a compact, strand-aware and perturbation-aware auxiliary representation, while canonical k-mers remain a strong backbone for close-relative classification.
