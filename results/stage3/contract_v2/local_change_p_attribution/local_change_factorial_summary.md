# Local-change factorial audit

This 2 x 2 audit separates spatial localization (contiguous versus dispersed) from substitution chemistry (property-directed versus random). All derivatives of one template remain in the same grouped-CV fold.

| representation          | representation_label           |   n_template_cells |   n_features |   spatial_effect_mean |   chemistry_effect_mean |   chemistry_readout_macro_f1 |   spatial_readout_macro_f1 |
|:------------------------|:-------------------------------|-------------------:|-------------:|----------------------:|------------------------:|-----------------------------:|---------------------------:|
| ck4                     | CK4                            |               3000 |     136.0000 |               -0.0901 |                  0.0007 |                       0.4987 |                     0.9101 |
| ck4_msp                 | CK4+MSP                        |               3000 |     211.0000 |               -0.0636 |                  0.0007 |                       0.6845 |                     0.9750 |
| ck4_p                   | CK4+P                          |               3000 |     147.0000 |               -0.0637 |                  0.0006 |                       0.6191 |                     0.9093 |
| ck4_p_auxiliary_only    | CK4+P auxiliary coordinates    |               3000 |     139.0000 |               -0.0637 |                  0.0005 |                       0.5007 |                     0.9098 |
| ck4_p_property_only     | CK4+P property coordinates     |               3000 |     144.0000 |               -0.0637 |                  0.0006 |                       0.6136 |                     0.9095 |
| ck4p_msp                | CK4P-MSP                       |               3000 |     222.0000 |               -0.0519 |                  0.0006 |                       0.7092 |                     0.9765 |
| ck4p_msp_auxiliary_only | CK4P-MSP auxiliary coordinates |               3000 |     214.0000 |               -0.0519 |                  0.0006 |                       0.6868 |                     0.9750 |
| ck4p_msp_property_only  | CK4P-MSP property coordinates  |               3000 |     219.0000 |               -0.0519 |                  0.0006 |                       0.7104 |                     0.9761 |
| msp                     | MSP                            |               3000 |      75.0000 |               -0.0009 |                  0.0039 |                       0.7240 |                     0.9631 |
| p                       | P                              |               3000 |      11.0000 |               -0.0001 |                  0.0012 |                       0.6614 |                     0.4942 |
| p_auxiliary_only        | P auxiliary coordinates        |               3000 |       3.0000 |                0.0000 |                 -0.0001 |                       0.5055 |                     0.4982 |
| p_msp                   | P+MSP                          |               3000 |      86.0000 |               -0.0007 |                  0.0029 |                       0.7592 |                     0.9658 |
| p_property_only         | P property coordinates         |               3000 |       8.0000 |               -0.0001 |                  0.0013 |                       0.6469 |                     0.4923 |

## Prespecified conditional readout contrasts

| contrast    | target          | paired_unit       |   n_cells |   full_mean |   comparator_mean |   mean_macro_f1_difference |   bootstrap_95_ci_low |   bootstrap_95_ci_high |   wilcoxon_two_sided_p |   bh_q |
|:------------|:----------------|:------------------|----------:|------------:|------------------:|---------------------------:|----------------------:|-----------------------:|-----------------------:|-------:|
| K | P+MSP   | spatial_pattern | length+local_mode |        12 |      0.9765 |            0.9658 |                     0.0107 |               -0.0004 |                 0.0239 |                 0.1763 | 0.1763 |
| K | P+MSP   | chemistry       | length+local_mode |        12 |      0.7092 |            0.7592 |                    -0.0500 |               -0.0613 |                -0.0390 |                 0.0005 | 0.0010 |
| P | CK4+MSP | spatial_pattern | length+local_mode |        12 |      0.9765 |            0.9750 |                     0.0015 |                0.0001 |                 0.0033 |                 0.1309 | 0.1570 |
| P | CK4+MSP | chemistry       | length+local_mode |        12 |      0.7092 |            0.6845 |                     0.0246 |                0.0083 |                 0.0410 |                 0.0342 | 0.0513 |
| MSP | CK4+P | spatial_pattern | length+local_mode |        12 |      0.9765 |            0.9093 |                     0.0671 |                0.0354 |                 0.1023 |                 0.0005 | 0.0010 |
| MSP | CK4+P | chemistry       | length+local_mode |        12 |      0.7092 |            0.6191 |                     0.0900 |                0.0544 |                 0.1314 |                 0.0005 | 0.0010 |
