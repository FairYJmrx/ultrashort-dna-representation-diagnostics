# Property redundancy and runtime audit

This lightweight audit addresses two reviewer-risk questions: whether global P and MSP channels are assumed to be orthogonal, and what feature-extraction cost is paid for CK4P-MSP relative to identity and high-k compressed baselines.

## Run metadata
|   elapsed_seconds | input                                                                                                      | lengths            |   n_sampled_reads |   max_per_length |   runtime_repeats |   max_cca_components |
|------------------:|:-----------------------------------------------------------------------------------------------------------|:-------------------|------------------:|-----------------:|------------------:|---------------------:|
|            21.778 | D:\AI-NGS\info\release_code\results\stage3\contract_v2\compact_baselines\stage3_compact_baseline_reads.csv | [69, 75, 100, 150] |              1600 |              400 |                 5 |                    5 |

## P/MSP redundancy summary
|   length |   n_reads |   p_dim |   msp_dim |   p_rank |   msp_rank |   pc1_corr_abs |   cca1_abs |   cca_mean_abs |   row_cosine_median_abs |   row_cosine_p95_abs |
|---------:|----------:|--------:|----------:|---------:|-----------:|---------------:|-----------:|---------------:|------------------------:|---------------------:|
|  69.0000 |  400.0000 | 11.0000 |   75.0000 |   8.0000 |    25.0000 |         0.9841 |     1.0000 |         0.7968 |                  0.3571 |               0.7532 |
|  75.0000 |  400.0000 | 11.0000 |   75.0000 |   8.0000 |    25.0000 |         0.9819 |     1.0000 |         0.7854 |                  0.3979 |               0.7571 |
| 100.0000 |  400.0000 | 11.0000 |   75.0000 |   8.0000 |    25.0000 |         0.9877 |     1.0000 |         0.8106 |                  0.4392 |               0.7774 |
| 150.0000 |  400.0000 | 11.0000 |   75.0000 |   8.0000 |    25.0000 |         0.9917 |     1.0000 |         0.8350 |                  0.4889 |               0.7838 |

## Feature runtime summary
| representation   | representation_label          |   n_lengths |   median_features |   ms_per_10k_reads |   microseconds_per_read |   density |
|:-----------------|:------------------------------|------------:|------------------:|-------------------:|------------------------:|----------:|
| hash_k15_d222    | Hashed k=15, d=222            |           4 |          222.0000 |          2257.1253 |                225.7125 |    0.2846 |
| minhash_k15_s222 | MinHash k=15, s=222           |           4 |          222.0000 |          2514.3725 |                251.4373 |    1.0000 |
| ck4              | CK4                           |           4 |          136.0000 |          4685.2381 |                468.5238 |    0.4397 |
| ck4p_msp         | CK4P-MSP                      |           4 |          222.0000 |          4791.8163 |                479.1816 |    0.5846 |
| ck4_p            | CK4+P                         |           4 |          147.0000 |          4798.4793 |                479.8479 |    0.4748 |
| rp_ck15_d222     | CK15 random projection, d=222 |           4 |          222.0000 |          6615.5834 |                661.5583 |    0.3296 |
