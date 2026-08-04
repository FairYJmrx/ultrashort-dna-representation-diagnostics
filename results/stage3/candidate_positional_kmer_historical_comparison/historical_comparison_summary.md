# Current-contract historical descriptor comparison

| representation   | representation_label   |   wgs_l2 |   wgs_retrieval |   local_macro_f1 |   motif_macro_f1 |   art_l2 |   cami_mean_retention |
|:-----------------|:-----------------------|---------:|----------------:|-----------------:|-----------------:|---------:|----------------------:|
| ck4              | CK4                    |   0.2180 |          1.0000 |           0.8857 |           0.6581 |   0.2742 |                1.0003 |
| ck5              | CK5                    |   0.2922 |          1.0000 |           0.8537 |           0.6861 |   0.3623 |                0.9912 |
| ck4p_msp         | CK4P-MSP               |   0.1285 |          1.0000 |           0.8882 |           0.6323 |   0.1592 |                0.9908 |
| ck4p_msp_pkm_w025 | CK4P-MSP-PKM  |   0.1374 |          1.0000 |           0.9283 |           0.7103 |   0.1672 |                0.9907 |
| pseknc_k3_l3     | PseKNC (k=3, lambda=3) |   0.1164 |          1.0000 |           0.8434 |           0.5930 |   0.1481 |                0.9913 |
| pseeiip          | PseEIIP                |   0.1619 |          1.0000 |           0.8315 |           0.6042 |   0.2029 |                1.0030 |
| ncp_anf          | NCP+ANF                |   0.2265 |          0.9794 |           0.9766 |           0.8700 |   0.1534 |                0.9583 |

This lightweight comparison uses the same current feature contract, grouped probes and sampled evidence cells for every representation. It is a comparative profile, not a universal ranking.
