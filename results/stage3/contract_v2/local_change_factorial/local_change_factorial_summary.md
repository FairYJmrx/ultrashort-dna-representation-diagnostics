# Local-change factorial audit

This 2 x 2 audit separates spatial localization (contiguous versus dispersed) from substitution chemistry (property-directed versus random). All derivatives of one template remain in the same grouped-CV fold.

| representation   | representation_label   |   n_template_cells |   n_features |   spatial_effect_mean |   chemistry_effect_mean |   chemistry_readout_macro_f1 |   spatial_readout_macro_f1 |
|:-----------------|:-----------------------|-------------------:|-------------:|----------------------:|------------------------:|-----------------------------:|---------------------------:|
| ck4              | CK4                    |               3000 |     136.0000 |               -0.0901 |                  0.0007 |                       0.5032 |                     0.9158 |
| ck4_msp          | CK4+MSP                |               3000 |     211.0000 |               -0.0636 |                  0.0007 |                       0.6804 |                     0.9766 |
| ck4_p            | CK4+P                  |               3000 |     147.0000 |               -0.0637 |                  0.0006 |                       0.6185 |                     0.9122 |
| ck4p_msp         | CK4P-MSP               |               3000 |     222.0000 |               -0.0519 |                  0.0006 |                       0.7103 |                     0.9770 |
| msp              | MSP                    |               3000 |      75.0000 |               -0.0009 |                  0.0039 |                       0.7273 |                     0.9621 |
| p                | P                      |               3000 |      11.0000 |               -0.0001 |                  0.0012 |                       0.6649 |                     0.4962 |
| p_msp            | P+MSP                  |               3000 |      86.0000 |               -0.0007 |                  0.0029 |                       0.7579 |                     0.9644 |

## Prespecified conditional readout contrasts

| contrast    | target          | paired_unit       |   n_cells |   full_mean |   comparator_mean |   mean_macro_f1_difference |   bootstrap_95_ci_low |   bootstrap_95_ci_high |   wilcoxon_two_sided_p |   bh_q |
|:------------|:----------------|:------------------|----------:|------------:|------------------:|---------------------------:|----------------------:|-----------------------:|-----------------------:|-------:|
| K | P+MSP   | spatial_pattern | length+local_mode |        12 |      0.9770 |            0.9644 |                     0.0126 |                0.0013 |                 0.0252 |                 0.1294 | 0.1553 |
| K | P+MSP   | chemistry       | length+local_mode |        12 |      0.7103 |            0.7579 |                    -0.0476 |               -0.0576 |                -0.0369 |                 0.0005 | 0.0010 |
| P | CK4+MSP | spatial_pattern | length+local_mode |        12 |      0.9770 |            0.9766 |                     0.0003 |               -0.0012 |                 0.0018 |                 0.5195 | 0.5195 |
| P | CK4+MSP | chemistry       | length+local_mode |        12 |      0.7103 |            0.6804 |                     0.0300 |                0.0126 |                 0.0483 |                 0.0210 | 0.0315 |
| MSP | CK4+P | spatial_pattern | length+local_mode |        12 |      0.9770 |            0.9122 |                     0.0647 |                0.0344 |                 0.0981 |                 0.0005 | 0.0010 |
| MSP | CK4+P | chemistry       | length+local_mode |        12 |      0.7103 |            0.6185 |                     0.0919 |                0.0585 |                 0.1296 |                 0.0005 | 0.0010 |
