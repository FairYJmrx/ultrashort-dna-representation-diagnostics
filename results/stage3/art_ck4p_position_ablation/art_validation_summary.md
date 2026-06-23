# Stage-3 ART Illumina Validation Summary

This stage validates representation stability under ART Illumina-like sequencing error profiles. It is a simulator-profile validation, not a clinical endpoint.

- ART executable requested: `art_illumina`
- ART executable found: `False`
- ART command rows: 105

## Command manifest preview

| label                       |   length | profile   |   fold_coverage | command                                                                                                                                                                                                                                                                                      |
|:----------------------------|---------:|:----------|----------------:|:---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Acinetobacter_calcoaceticus |       69 | HS25      |            0.01 | "art_illumina" -ss HS25 -i "D:\AI-NGS\info\data\reference_genomes\close_relative\Acinetobacter\Acinetobacter_calcoaceticus\GCF_000368965.1_genomic.fna" -l 69 -f 0.01 -rs 473 -na -o "D:\AI-NGS\info\results\stage3\art_ck4p_position_ablation\fastq\Acinetobacter_calcoaceticus_L69_ART_"   |
| Acinetobacter_calcoaceticus |       75 | HS25      |            0.01 | "art_illumina" -ss HS25 -i "D:\AI-NGS\info\data\reference_genomes\close_relative\Acinetobacter\Acinetobacter_calcoaceticus\GCF_000368965.1_genomic.fna" -l 75 -f 0.01 -rs 479 -na -o "D:\AI-NGS\info\results\stage3\art_ck4p_position_ablation\fastq\Acinetobacter_calcoaceticus_L75_ART_"   |
| Acinetobacter_calcoaceticus |      100 | HS25      |            0.01 | "art_illumina" -ss HS25 -i "D:\AI-NGS\info\data\reference_genomes\close_relative\Acinetobacter\Acinetobacter_calcoaceticus\GCF_000368965.1_genomic.fna" -l 100 -f 0.01 -rs 504 -na -o "D:\AI-NGS\info\results\stage3\art_ck4p_position_ablation\fastq\Acinetobacter_calcoaceticus_L100_ART_" |
| Acinetobacter_calcoaceticus |      125 | HS25      |            0.01 | "art_illumina" -ss HS25 -i "D:\AI-NGS\info\data\reference_genomes\close_relative\Acinetobacter\Acinetobacter_calcoaceticus\GCF_000368965.1_genomic.fna" -l 125 -f 0.01 -rs 529 -na -o "D:\AI-NGS\info\results\stage3\art_ck4p_position_ablation\fastq\Acinetobacter_calcoaceticus_L125_ART_" |
| Acinetobacter_calcoaceticus |      150 | HS25      |            0.01 | "art_illumina" -ss HS25 -i "D:\AI-NGS\info\data\reference_genomes\close_relative\Acinetobacter\Acinetobacter_calcoaceticus\GCF_000368965.1_genomic.fna" -l 150 -f 0.01 -rs 554 -na -o "D:\AI-NGS\info\results\stage3\art_ck4p_position_ablation\fastq\Acinetobacter_calcoaceticus_L150_ART_" |
| Acinetobacter_nosocomialis  |       69 | HS25      |            0.01 | "art_illumina" -ss HS25 -i "D:\AI-NGS\info\data\reference_genomes\close_relative\Acinetobacter\Acinetobacter_nosocomialis\GCF_041021905.1_genomic.fna" -l 69 -f 0.01 -rs 473 -na -o "D:\AI-NGS\info\results\stage3\art_ck4p_position_ablation\fastq\Acinetobacter_nosocomialis_L69_ART_"     |
| Acinetobacter_nosocomialis  |       75 | HS25      |            0.01 | "art_illumina" -ss HS25 -i "D:\AI-NGS\info\data\reference_genomes\close_relative\Acinetobacter\Acinetobacter_nosocomialis\GCF_041021905.1_genomic.fna" -l 75 -f 0.01 -rs 479 -na -o "D:\AI-NGS\info\results\stage3\art_ck4p_position_ablation\fastq\Acinetobacter_nosocomialis_L75_ART_"     |
| Acinetobacter_nosocomialis  |      100 | HS25      |            0.01 | "art_illumina" -ss HS25 -i "D:\AI-NGS\info\data\reference_genomes\close_relative\Acinetobacter\Acinetobacter_nosocomialis\GCF_041021905.1_genomic.fna" -l 100 -f 0.01 -rs 504 -na -o "D:\AI-NGS\info\results\stage3\art_ck4p_position_ablation\fastq\Acinetobacter_nosocomialis_L100_ART_"   |
| Acinetobacter_nosocomialis  |      125 | HS25      |            0.01 | "art_illumina" -ss HS25 -i "D:\AI-NGS\info\data\reference_genomes\close_relative\Acinetobacter\Acinetobacter_nosocomialis\GCF_041021905.1_genomic.fna" -l 125 -f 0.01 -rs 529 -na -o "D:\AI-NGS\info\results\stage3\art_ck4p_position_ablation\fastq\Acinetobacter_nosocomialis_L125_ART_"   |
| Acinetobacter_nosocomialis  |      150 | HS25      |            0.01 | "art_illumina" -ss HS25 -i "D:\AI-NGS\info\data\reference_genomes\close_relative\Acinetobacter\Acinetobacter_nosocomialis\GCF_041021905.1_genomic.fna" -l 150 -f 0.01 -rs 554 -na -o "D:\AI-NGS\info\results\stage3\art_ck4p_position_ablation\fastq\Acinetobacter_nosocomialis_L150_ART_"   |
| Acinetobacter_pittii        |       69 | HS25      |            0.01 | "art_illumina" -ss HS25 -i "D:\AI-NGS\info\data\reference_genomes\close_relative\Acinetobacter\Acinetobacter_pittii\GCF_000369045.1_genomic.fna" -l 69 -f 0.01 -rs 473 -na -o "D:\AI-NGS\info\results\stage3\art_ck4p_position_ablation\fastq\Acinetobacter_pittii_L69_ART_"                 |
| Acinetobacter_pittii        |       75 | HS25      |            0.01 | "art_illumina" -ss HS25 -i "D:\AI-NGS\info\data\reference_genomes\close_relative\Acinetobacter\Acinetobacter_pittii\GCF_000369045.1_genomic.fna" -l 75 -f 0.01 -rs 479 -na -o "D:\AI-NGS\info\results\stage3\art_ck4p_position_ablation\fastq\Acinetobacter_pittii_L75_ART_"                 |

## Best ART stability by length

|   length | representation                     |   paired_cosine_mean |   l2_delta_mean |   retrieval_top1 |   n_features |
|---------:|:-----------------------------------|---------------------:|----------------:|-----------------:|-------------:|
|       69 | ckmer4_property_multiscale_mean_l2 |                0.992 |           0.119 |            0.998 |          222 |
|       75 | ckmer4_property_multiscale_mean_l2 |                0.992 |           0.115 |            1.000 |          222 |
|      100 | ckmer4_property_multiscale_mean_l2 |                0.989 |           0.147 |            1.000 |          226 |
|      125 | ckmer4_property_multiscale_mean_l2 |                1.000 |           0.009 |            1.000 |          222 |
|      150 | ckmer4_property_multiscale_mean_l2 |                1.000 |           0.013 |            1.000 |          226 |