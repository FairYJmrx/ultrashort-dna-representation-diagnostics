# Stage-3 ART Illumina Completed Summary

- ART executable: `tools/art/extracted_bp/Win64/art_illumina.exe`
- Fold coverage: `0.005`
- Generated paired rows: `75592`
- Generated clean/error pairs: `37796`

## Best ART stability by length

|   length | representation      |   paired_cosine_mean |   l2_delta_mean |   retrieval_top1 |   n_features |   density |
|---------:|:--------------------|---------------------:|----------------:|-----------------:|-------------:|----------:|
|       69 | eiip_summary_l2     |                1.000 |           0.008 |            0.285 |            8 |     1.000 |
|       75 | eiip_summary_l2     |                1.000 |           0.010 |            0.177 |            8 |     1.000 |
|      100 | eiip_summary_l2     |                1.000 |           0.017 |            0.065 |            8 |     1.000 |
|      125 | eiip_summary_l2     |                1.000 |           0.001 |            0.865 |            8 |     1.000 |
|      150 | cspaced_property_l2 |                0.999 |           0.017 |            1.000 |          147 |     0.604 |