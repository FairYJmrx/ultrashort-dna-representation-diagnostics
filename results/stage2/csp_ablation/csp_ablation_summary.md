# Stage-2 CSP Component Ablation

This audit separates the priors fused in CSP: spaced seeds, reverse-complement canonicalization and individual DNA property summaries.

## Best property additions over canonical spaced counts

| condition                |   length | label                                                                           |   delta_cosine_vs_cspaced_count |   delta_l2_vs_cspaced_count |   paired_cosine_mean |   l2_delta_mean |   n_features |
|:-------------------------|---------:|:--------------------------------------------------------------------------------|--------------------------------:|----------------------------:|---------------------:|----------------:|-------------:|
| N_3pct                   |       69 | full CSP without N fraction                                                     |                          0.0318 |                     -0.1639 |               0.9942 |          0.1072 |          146 |
| N_3pct                   |       75 | full CSP without N fraction                                                     |                          0.0275 |                     -0.1523 |               0.9950 |          0.0995 |          146 |
| N_3pct                   |      100 | full CSP without N fraction                                                     |                          0.0269 |                     -0.1491 |               0.9948 |          0.1020 |          146 |
| N_3pct                   |      150 | full CSP without N fraction                                                     |                          0.0192 |                     -0.1263 |               0.9962 |          0.0869 |          146 |
| local_mismatch_6bp       |       69 | canonical spaced + cumulative hydrogen+gc+purine+eiip+n_fraction+entropy+length |                          0.1013 |                     -0.3172 |               0.9877 |          0.1556 |          147 |
| local_mismatch_6bp       |       75 | canonical spaced + cumulative hydrogen+gc+purine+eiip+n_fraction+entropy+length |                          0.0890 |                     -0.2975 |               0.9892 |          0.1458 |          147 |
| local_mismatch_6bp       |      100 | canonical spaced + cumulative hydrogen+gc+purine+eiip+n_fraction+entropy+length |                          0.0587 |                     -0.2421 |               0.9929 |          0.1180 |          147 |
| local_mismatch_6bp       |      150 | canonical spaced + cumulative hydrogen+gc+purine+eiip+n_fraction+entropy+length |                          0.0315 |                     -0.1785 |               0.9964 |          0.0848 |          147 |
| short_indel              |       69 | canonical spaced + cumulative hydrogen+gc+purine+eiip+n_fraction+entropy+length |                          0.0293 |                     -0.1190 |               0.9964 |          0.0582 |          147 |
| short_indel              |       75 | canonical spaced + cumulative hydrogen+gc+purine+eiip+n_fraction+entropy+length |                          0.0275 |                     -0.1169 |               0.9967 |          0.0568 |          147 |
| short_indel              |      100 | canonical spaced + cumulative hydrogen+gc+purine+eiip+n_fraction+entropy+length |                          0.0235 |                     -0.1173 |               0.9972 |          0.0566 |          147 |
| short_indel              |      150 | canonical spaced + cumulative hydrogen+gc+purine+eiip+n_fraction+entropy+length |                          0.0189 |                     -0.1187 |               0.9978 |          0.0561 |          147 |
| substitution_1pct        |       69 | canonical spaced + cumulative hydrogen+gc+purine+eiip+n_fraction+entropy+length |                          0.0206 |                     -0.0966 |               0.9975 |          0.0471 |          147 |
| substitution_1pct        |       75 | canonical spaced + cumulative hydrogen+gc+purine+eiip+n_fraction+entropy+length |                          0.0214 |                     -0.1041 |               0.9974 |          0.0510 |          147 |
| substitution_1pct        |      100 | canonical spaced + cumulative hydrogen+gc+purine+eiip+n_fraction+entropy+length |                          0.0195 |                     -0.1095 |               0.9977 |          0.0531 |          147 |
| substitution_1pct        |      150 | canonical spaced + cumulative hydrogen+gc+purine+eiip+n_fraction+entropy+length |                          0.0149 |                     -0.1056 |               0.9983 |          0.0501 |          147 |
| substitution_1pct_N_3pct |       69 | full CSP without N fraction                                                     |                          0.0534 |                     -0.2122 |               0.9916 |          0.1270 |          146 |
| substitution_1pct_N_3pct |       75 | full CSP without N fraction                                                     |                          0.0474 |                     -0.1988 |               0.9926 |          0.1189 |          146 |
| substitution_1pct_N_3pct |      100 | full CSP without N fraction                                                     |                          0.0444 |                     -0.1944 |               0.9926 |          0.1198 |          146 |
| substitution_1pct_N_3pct |      150 | full CSP without N fraction                                                     |                          0.0331 |                     -0.1696 |               0.9946 |          0.1031 |          146 |
| trim_5bp                 |       69 | canonical spaced + cumulative hydrogen+gc+purine+eiip+n_fraction+entropy+length |                          0.0228 |                     -0.1503 |               0.9972 |          0.0746 |          147 |
| trim_5bp                 |       75 | canonical spaced + cumulative hydrogen+gc+purine+eiip+n_fraction+entropy+length |                          0.0196 |                     -0.1391 |               0.9976 |          0.0692 |          147 |
| trim_5bp                 |      100 | canonical spaced + cumulative hydrogen+gc+purine+eiip+n_fraction+entropy+length |                          0.0126 |                     -0.1118 |               0.9984 |          0.0555 |          147 |
| trim_5bp                 |      150 | canonical spaced + cumulative hydrogen+gc+purine+eiip+n_fraction+entropy+length |                          0.0066 |                     -0.0811 |               0.9992 |          0.0398 |          147 |

## Full CSP effect

| condition                |   length | label    |   delta_cosine_vs_cspaced_count |   delta_l2_vs_cspaced_count |   paired_cosine_mean |   l2_delta_mean |   n_features |
|:-------------------------|---------:|:---------|--------------------------------:|----------------------------:|---------------------:|----------------:|-------------:|
| substitution_1pct        |       69 | full CSP |                          0.0206 |                     -0.0966 |               0.9975 |          0.0471 |          147 |
| N_3pct                   |       69 | full CSP |                          0.0317 |                     -0.1634 |               0.9941 |          0.1077 |          147 |
| trim_5bp                 |       69 | full CSP |                          0.0228 |                     -0.1503 |               0.9972 |          0.0746 |          147 |
| substitution_1pct_N_3pct |       69 | full CSP |                          0.0534 |                     -0.2118 |               0.9915 |          0.1274 |          147 |
| short_indel              |       69 | full CSP |                          0.0293 |                     -0.1190 |               0.9964 |          0.0582 |          147 |
| local_mismatch_6bp       |       69 | full CSP |                          0.1013 |                     -0.3172 |               0.9877 |          0.1556 |          147 |
| substitution_1pct        |       75 | full CSP |                          0.0214 |                     -0.1041 |               0.9974 |          0.0510 |          147 |
| N_3pct                   |       75 | full CSP |                          0.0274 |                     -0.1519 |               0.9950 |          0.0999 |          147 |
| trim_5bp                 |       75 | full CSP |                          0.0196 |                     -0.1391 |               0.9976 |          0.0692 |          147 |
| substitution_1pct_N_3pct |       75 | full CSP |                          0.0473 |                     -0.1985 |               0.9925 |          0.1193 |          147 |
| short_indel              |       75 | full CSP |                          0.0275 |                     -0.1169 |               0.9967 |          0.0568 |          147 |
| local_mismatch_6bp       |       75 | full CSP |                          0.0890 |                     -0.2975 |               0.9892 |          0.1458 |          147 |
| substitution_1pct        |      100 | full CSP |                          0.0195 |                     -0.1095 |               0.9977 |          0.0531 |          147 |
| N_3pct                   |      100 | full CSP |                          0.0269 |                     -0.1486 |               0.9947 |          0.1025 |          147 |
| trim_5bp                 |      100 | full CSP |                          0.0126 |                     -0.1118 |               0.9984 |          0.0555 |          147 |
| substitution_1pct_N_3pct |      100 | full CSP |                          0.0443 |                     -0.1940 |               0.9926 |          0.1202 |          147 |
| short_indel              |      100 | full CSP |                          0.0235 |                     -0.1173 |               0.9972 |          0.0566 |          147 |
| local_mismatch_6bp       |      100 | full CSP |                          0.0587 |                     -0.2421 |               0.9929 |          0.1180 |          147 |
| substitution_1pct        |      150 | full CSP |                          0.0149 |                     -0.1056 |               0.9983 |          0.0501 |          147 |
| N_3pct                   |      150 | full CSP |                          0.0192 |                     -0.1258 |               0.9962 |          0.0873 |          147 |
| trim_5bp                 |      150 | full CSP |                          0.0066 |                     -0.0811 |               0.9992 |          0.0398 |          147 |
| substitution_1pct_N_3pct |      150 | full CSP |                          0.0331 |                     -0.1693 |               0.9945 |          0.1034 |          147 |
| short_indel              |      150 | full CSP |                          0.0189 |                     -0.1187 |               0.9978 |          0.0561 |          147 |
| local_mismatch_6bp       |      150 | full CSP |                          0.0315 |                     -0.1785 |               0.9964 |          0.0848 |          147 |
