# Stage-3 ART Illumina Validation Summary

This stage validates representation stability under ART Illumina-like sequencing error profiles. It is a simulator-profile validation, not a clinical endpoint.

- ART executable requested: `art_illumina`
- ART executable found: `False`
- ART command rows: 42

## Command manifest preview

| label                       |   length | profile   |   fold_coverage | command                                                                                                                                                                                                                                                                                                |
|:----------------------------|---------:|:----------|----------------:|:-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Acinetobacter_calcoaceticus |       69 | HS25      |            0.01 | "art_illumina" -ss HS25 -i "D:\AI-NGS\info\data\reference_genomes\close_relative\Acinetobacter\Acinetobacter_calcoaceticus\GCF_000368965.1_genomic.fna" -l 69 -f 0.01 -rs 98 -na -o "D:\AI-NGS\info\results\stage3\art_fullmatrix_property_contribution\fastq\Acinetobacter_calcoaceticus_L69_ART_"    |
| Acinetobacter_calcoaceticus |      100 | HS25      |            0.01 | "art_illumina" -ss HS25 -i "D:\AI-NGS\info\data\reference_genomes\close_relative\Acinetobacter\Acinetobacter_calcoaceticus\GCF_000368965.1_genomic.fna" -l 100 -f 0.01 -rs 129 -na -o "D:\AI-NGS\info\results\stage3\art_fullmatrix_property_contribution\fastq\Acinetobacter_calcoaceticus_L100_ART_" |
| Acinetobacter_nosocomialis  |       69 | HS25      |            0.01 | "art_illumina" -ss HS25 -i "D:\AI-NGS\info\data\reference_genomes\close_relative\Acinetobacter\Acinetobacter_nosocomialis\GCF_041021905.1_genomic.fna" -l 69 -f 0.01 -rs 98 -na -o "D:\AI-NGS\info\results\stage3\art_fullmatrix_property_contribution\fastq\Acinetobacter_nosocomialis_L69_ART_"      |
| Acinetobacter_nosocomialis  |      100 | HS25      |            0.01 | "art_illumina" -ss HS25 -i "D:\AI-NGS\info\data\reference_genomes\close_relative\Acinetobacter\Acinetobacter_nosocomialis\GCF_041021905.1_genomic.fna" -l 100 -f 0.01 -rs 129 -na -o "D:\AI-NGS\info\results\stage3\art_fullmatrix_property_contribution\fastq\Acinetobacter_nosocomialis_L100_ART_"   |
| Acinetobacter_pittii        |       69 | HS25      |            0.01 | "art_illumina" -ss HS25 -i "D:\AI-NGS\info\data\reference_genomes\close_relative\Acinetobacter\Acinetobacter_pittii\GCF_000369045.1_genomic.fna" -l 69 -f 0.01 -rs 98 -na -o "D:\AI-NGS\info\results\stage3\art_fullmatrix_property_contribution\fastq\Acinetobacter_pittii_L69_ART_"                  |
| Acinetobacter_pittii        |      100 | HS25      |            0.01 | "art_illumina" -ss HS25 -i "D:\AI-NGS\info\data\reference_genomes\close_relative\Acinetobacter\Acinetobacter_pittii\GCF_000369045.1_genomic.fna" -l 100 -f 0.01 -rs 129 -na -o "D:\AI-NGS\info\results\stage3\art_fullmatrix_property_contribution\fastq\Acinetobacter_pittii_L100_ART_"               |
| Acinetobacter_baumannii     |       69 | HS25      |            0.01 | "art_illumina" -ss HS25 -i "D:\AI-NGS\info\data\reference_genomes\close_relative\Acinetobacter\Acinetobacter_baumannii\GCF_900011295.1_genomic.fna" -l 69 -f 0.01 -rs 98 -na -o "D:\AI-NGS\info\results\stage3\art_fullmatrix_property_contribution\fastq\Acinetobacter_baumannii_L69_ART_"            |
| Acinetobacter_baumannii     |      100 | HS25      |            0.01 | "art_illumina" -ss HS25 -i "D:\AI-NGS\info\data\reference_genomes\close_relative\Acinetobacter\Acinetobacter_baumannii\GCF_900011295.1_genomic.fna" -l 100 -f 0.01 -rs 129 -na -o "D:\AI-NGS\info\results\stage3\art_fullmatrix_property_contribution\fastq\Acinetobacter_baumannii_L100_ART_"         |
| Burkholderia_cenocepacia    |       69 | HS25      |            0.01 | "art_illumina" -ss HS25 -i "D:\AI-NGS\info\data\reference_genomes\close_relative\Burkholderia\Burkholderia_cenocepacia\GCF_000009485.1_genomic.fna" -l 69 -f 0.01 -rs 98 -na -o "D:\AI-NGS\info\results\stage3\art_fullmatrix_property_contribution\fastq\Burkholderia_cenocepacia_L69_ART_"           |
| Burkholderia_cenocepacia    |      100 | HS25      |            0.01 | "art_illumina" -ss HS25 -i "D:\AI-NGS\info\data\reference_genomes\close_relative\Burkholderia\Burkholderia_cenocepacia\GCF_000009485.1_genomic.fna" -l 100 -f 0.01 -rs 129 -na -o "D:\AI-NGS\info\results\stage3\art_fullmatrix_property_contribution\fastq\Burkholderia_cenocepacia_L100_ART_"        |
| Burkholderia_multivorans    |       69 | HS25      |            0.01 | "art_illumina" -ss HS25 -i "D:\AI-NGS\info\data\reference_genomes\close_relative\Burkholderia\Burkholderia_multivorans\GCF_000010545.1_genomic.fna" -l 69 -f 0.01 -rs 98 -na -o "D:\AI-NGS\info\results\stage3\art_fullmatrix_property_contribution\fastq\Burkholderia_multivorans_L69_ART_"           |
| Burkholderia_multivorans    |      100 | HS25      |            0.01 | "art_illumina" -ss HS25 -i "D:\AI-NGS\info\data\reference_genomes\close_relative\Burkholderia\Burkholderia_multivorans\GCF_000010545.1_genomic.fna" -l 100 -f 0.01 -rs 129 -na -o "D:\AI-NGS\info\results\stage3\art_fullmatrix_property_contribution\fastq\Burkholderia_multivorans_L100_ART_"        |

## Best ART stability by length

|   length | representation    |   paired_cosine_mean |   l2_delta_mean |   retrieval_top1 |   n_features |
|---------:|:------------------|---------------------:|----------------:|-----------------:|-------------:|
|       69 | property_channels |                0.995 |           0.087 |            1.000 |          345 |
|      100 | property_channels |                0.991 |           0.130 |            1.000 |          500 |