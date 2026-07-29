# CAMI_TOY frozen-head label-retention audit

A logistic probe was fitted only to 100-bp clean reads. The primary contract-space probe preserves the declared feature scaling; a scaler fitted only on the clean training fold is retained as a sensitivity analysis. All target conditions use held-out source groups without refitting.

| representation_label   |   n_features |   baseline_macro_f1 |   mean_shifted_macro_f1 |   worst_shifted_macro_f1 |   mean_retention |   worst_retention |   feature_seconds |
|:-----------------------|-------------:|--------------------:|------------------------:|-------------------------:|-----------------:|------------------:|------------------:|
| CK4+MSP                |          211 |              0.8938 |                  0.8869 |                   0.8816 |           0.9922 |            0.9863 |            1.9426 |
| CK4P-MSP               |          222 |              0.8926 |                  0.8855 |                   0.8809 |           0.9921 |            0.9869 |            1.9086 |
| CK4+P                  |          147 |              0.8943 |                  0.8868 |                   0.8808 |           0.9917 |            0.9850 |            1.8090 |
| PseKNC                 |           67 |              0.8911 |                  0.8809 |                   0.8744 |           0.9886 |            0.9813 |           34.1199 |
| PseEIIP                |           64 |              0.8959 |                  0.8848 |                   0.8800 |           0.9876 |            0.9822 |            0.7173 |
| Hashed k=15            |          222 |              0.5188 |                  0.5116 |                   0.5007 |           0.9860 |            0.9651 |            4.0480 |
| CK4                    |          136 |              0.9012 |                  0.8872 |                   0.8789 |           0.9845 |            0.9752 |            2.1002 |
| CK5                    |          512 |              0.8992 |                  0.8819 |                   0.8668 |           0.9808 |            0.9640 |            1.7451 |
| NCP+ANF                |          400 |              0.8623 |                  0.8362 |                   0.8131 |           0.9697 |            0.9430 |            1.1966 |

The retention ratio is a normalized descriptive summary. Absolute macro-F1, MCC, balanced accuracy, AUROC and AUPRC remain the primary task metrics.