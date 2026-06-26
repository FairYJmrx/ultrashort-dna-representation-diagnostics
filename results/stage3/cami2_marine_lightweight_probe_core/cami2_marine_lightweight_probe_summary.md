# CAMI II Marine Lightweight Probe Summary

This probe uses CAMI II marine short-read sample 0 as an external metagenomic short-read source.
It is an unlabeled paired perturbation-stability probe, not a taxonomic classifier benchmark.

## Input

- Reads URL: `https://frl.publisso.de/data/frl:6425521/marine/short_read/marmgCAMI2_sample_0_reads.tar.gz`
- Setup URL: `https://frl.publisso.de/data/frl:6425521/marine/short_read/marmgCAMI2_setup.tar.gz`
- Parsed FASTQ reads: 4000
- Probe rows after length/condition expansion: 48000
- Lengths: [69, 75, 100]
- Conditions: ['clean', 'N_3pct', 'substitution_1pct', 'substitution_1pct_N_3pct']

## Lowest-drift representation by condition and length

| condition                |   length | representation                     |   paired_cosine_mean |   l2_delta_mean |   retrieval_top1 |   n_features |
|:-------------------------|---------:|:-----------------------------------|---------------------:|----------------:|-----------------:|-------------:|
| N_3pct                   |       69 | ckmer4_property_multiscale_mean_l2 |                0.995 |           0.102 |            1.000 |          222 |
| N_3pct                   |       75 | ckmer4_property_multiscale_mean_l2 |                0.995 |           0.095 |            1.000 |          222 |
| N_3pct                   |      100 | ckmer4_property_multiscale_mean_l2 |                0.995 |           0.097 |            1.000 |          222 |
| substitution_1pct        |       69 | ckmer4_property_multiscale_mean_l2 |                0.998 |           0.048 |            1.000 |          222 |
| substitution_1pct        |       75 | ckmer4_property_multiscale_mean_l2 |                0.998 |           0.048 |            1.000 |          222 |
| substitution_1pct        |      100 | ckmer4_property_multiscale_mean_l2 |                0.998 |           0.047 |            1.000 |          222 |
| substitution_1pct_N_3pct |       69 | ckmer4_property_multiscale_mean_l2 |                0.992 |           0.121 |            1.000 |          222 |
| substitution_1pct_N_3pct |       75 | ckmer4_property_multiscale_mean_l2 |                0.993 |           0.114 |            1.000 |          222 |
| substitution_1pct_N_3pct |      100 | ckmer4_property_multiscale_mean_l2 |                0.993 |           0.115 |            1.000 |          222 |

## Interpretation boundary

Because read-level taxonomic labels are not available from the anonymous FASTQ header and the BAM truth files are distributed as large OTU-specific bundles, this run should be reported only as an external short-read stability probe. It should not be described as CAMI II taxonomic validation.