# Attention Context-Loss Diagnostic

This experiment tests the user hypothesis that ultra-short reads lose more than a linear number of bases: when a class depends on a motif pair, a truncated read may contain the shared anchor motif but not the class-defining second motif. Full self-attention cannot recover a token that is absent from the observed read.

Synthetic latent templates contain a shared anchor motif near position 18 and a class-specific motif near position 138. Reads are cropped to 69, 75, 100, 125, and 150 bp, with PE150 represented by concatenating R1 and reverse-complemented R2.

## Visibility Metrics

| Length/layout | Pair visible | Class motif visible | Partial motif prefix visible | MI(label; pair visible) | Mean context distance |
|---|---:|---:|---:|---:|---:|
| 69 bp | 0.000 | 0.000 | 0.137 | 0.000 |  |
| 75 bp | 0.000 | 0.000 | 0.139 | 0.000 |  |
| 100 bp | 0.000 | 0.000 | 0.159 | 0.000 |  |
| 125 bp | 0.002 | 0.002 | 0.189 | 0.002 | 78.0 |
| 150 bp | 1.000 | 1.000 | 1.000 | 0.000 | 119.9 |
| PE150 | 1.000 | 1.000 | 1.000 | 0.000 | 119.9 |

## Lightweight Classifier Results

| Representation | Length/layout | Macro-F1 | Accuracy |
|---|---|---:|---:|
| ckmer5_count_l2 | 69 bp | 0.352 | 0.352 |
| ckmer5_count_l2 | 75 bp | 0.315 | 0.315 |
| ckmer5_count_l2 | 100 bp | 0.373 | 0.377 |
| ckmer5_count_l2 | 125 bp | 0.361 | 0.364 |
| ckmer5_count_l2 | 150 bp | 0.988 | 0.988 |
| ckmer5_count_l2 | PE150 | 0.914 | 0.914 |
| cspaced_property_l2 | 69 bp | 0.358 | 0.358 |
| cspaced_property_l2 | 75 bp | 0.327 | 0.327 |
| cspaced_property_l2 | 100 bp | 0.364 | 0.364 |
| cspaced_property_l2 | 125 bp | 0.383 | 0.383 |
| cspaced_property_l2 | 150 bp | 0.772 | 0.772 |
| cspaced_property_l2 | PE150 | 0.567 | 0.568 |
| kmer5_count_l2 | 69 bp | 0.349 | 0.352 |
| kmer5_count_l2 | 75 bp | 0.394 | 0.395 |
| kmer5_count_l2 | 100 bp | 0.376 | 0.377 |
| kmer5_count_l2 | 125 bp | 0.400 | 0.401 |
| kmer5_count_l2 | 150 bp | 0.982 | 0.981 |
| kmer5_count_l2 | PE150 | 0.975 | 0.975 |
| kmer5_presence | 69 bp | 0.361 | 0.364 |
| kmer5_presence | 75 bp | 0.444 | 0.444 |
| kmer5_presence | 100 bp | 0.358 | 0.358 |
| kmer5_presence | 125 bp | 0.393 | 0.395 |
| kmer5_presence | 150 bp | 0.982 | 0.981 |
| kmer5_presence | PE150 | 0.981 | 0.981 |
| oracle_motif_pair | 69 bp | 0.167 | 0.333 |
| oracle_motif_pair | 75 bp | 0.167 | 0.333 |
| oracle_motif_pair | 100 bp | 0.167 | 0.333 |
| oracle_motif_pair | 125 bp | 0.167 | 0.333 |
| oracle_motif_pair | 150 bp | 1.000 | 1.000 |
| oracle_motif_pair | PE150 | 1.000 | 1.000 |
| property_channels | 69 bp | 0.339 | 0.340 |
| property_channels | 75 bp | 0.370 | 0.370 |
| property_channels | 100 bp | 0.321 | 0.321 |
| property_channels | 125 bp | 0.273 | 0.272 |
| property_channels | 150 bp | 1.000 | 1.000 |
| property_channels | PE150 | 1.000 | 1.000 |
| rope_property | 69 bp | 0.351 | 0.352 |
| rope_property | 75 bp | 0.312 | 0.315 |
| rope_property | 100 bp | 0.315 | 0.315 |
| rope_property | 125 bp | 0.323 | 0.321 |
| rope_property | 150 bp | 1.000 | 1.000 |
| rope_property | PE150 | 1.000 | 1.000 |
| spaced_kmer_phase | 69 bp | 0.303 | 0.302 |
| spaced_kmer_phase | 75 bp | 0.322 | 0.321 |
| spaced_kmer_phase | 100 bp | 0.352 | 0.352 |
| spaced_kmer_phase | 125 bp | 0.286 | 0.290 |
| spaced_kmer_phase | 150 bp | 1.000 | 1.000 |
| spaced_kmer_phase | PE150 | 1.000 | 1.000 |

## Interpretation

The diagnostic separates two effects. Short reads have fewer possible attention pairs, but the more important failure mode here is semantic absence: the class-defining motif is not observed below the designed boundary. In that regime, attention can only attend over the shared prefix and distractors, so label information is structurally unavailable. Once the second motif enters the observed read, simple pair-aware features and ordinary sequence representations recover the label more easily.

This supports a restrained manuscript claim: read-length effects can be nonlinear for context-dependent tasks because the observed sequence may lose an entire motif co-occurrence relation. It does not prove that a full Transformer is superior; it shows why attention-compatible encodings require enough observed context to be meaningful.
