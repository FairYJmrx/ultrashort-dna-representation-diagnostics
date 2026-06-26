# Back Matter and Reference Support

This file records citation support, availability statements and submission back matter for the paper-folder manuscript. Reference formatting remains provisional until the final bibliography is exported in the target journal style.

## Citation support plan

### Abstract support

Short-read mNGS context can be supported by `Wilson2014`, `Wilson2019`, `Chiu2019`, `Martin2011`, `Bolger2014` and `Salter2014`. ART and CAMI resources can be supported by `Huang2012ART`, `Sczyrba2017` and `Meyer2022`. The abstract should normally remain uncited unless the final venue requests abstract citations.

### Introduction support

The exact identity backbone should cite Kraken/Kraken 2, CLARK, Centrifuge and Kaiju, with benchmark context from CAMI where appropriate (`Wood2014`, `Wood2019`, `Ounit2015`, `Kim2016`, `Menzel2016`, `Sczyrba2017`, `Meyer2022`). Alignment-free and sketching routes should cite Mash/MinHash and alignment-free reviews (`Ondov2016`, `Zielezinski2017`). Biochemical and signal encodings should cite classic Voss, Jeffrey and EIIP-style representations (`Voss1992`, `Jeffrey1990`, `Anastassiou2001`, `Cristea2002`, `Nair2006`). Deep metagenomic and sequence-token methods should cite DeepMicrobes, MetaTransformer, BarcodeBERT and related classifiers, while DNA foundation-model context can cite DNABERT, DNABERT-2, Nucleotide Transformer, HyenaDNA, Evo and GENA-LM (`Liang2020`, `Ji2021`, `Zhou2024`, `DallaTorre2025`, `Nguyen2023`, `Nguyen2024Evo`, `Fishman2025`, `Wichmann2023`). These models should be discussed as representation context, not as direct 69/75 bp comparators in the current study.

For the read-length sentence, *Practice and Progress of mNGS Report Interpretation* (Yang, p. 99) can be used as background support for the commonly reported 50-75 bp post-QC mNGS regime. Verify the exact edition, publisher and page number from the copyright page before the final reference export. Keep this citation separate from the Data Availability provenance statement, which is about the specific design choice for 69/75 bp and not about the general field range.

### Results support

Most Results claims are supported by internal experiments rather than external literature. The figure/table inventory in `info/paper/figure_table_inventory.md` maps each claim to generated assets and source scripts. Statistical and baseline controls are supported by reviewer-response outputs under `info/results/stage3/reviewer_response`, including same-dimension PCA/SVD baselines, mixed-metric block-weight audits, MI and conditional-MI proxy summaries, k-nearest-neighbor MI robustness checks, dimension-matched high-k compressed k-mer baselines, P/MSP contribution audits, P/MSP redundancy and runtime audits, P-channel counterfactual controls, and MSP bin/gamma sensitivity analyses.

## Data Availability

All processed data tables, figure source summaries and analysis outputs generated for this study are available in the project result folders and will be deposited in a public repository before submission. The current local source locations are `info/results`, `info/paper/figures`, `info/paper/tables` and `info/scripts`. The final public repository name, DOI/accession and licence are to be inserted before journal submission.

Publicly reused resources include simulator- and benchmark-derived materials used for ART and CAMI analyses, which should be cited through the corresponding primary publications and public resource records in the final reference list. The restricted clinical sequencing provenance was used only to motivate the 69 and 75 bp read-length conditions, and the underlying clinical sequencing reads were not used as experimental input, are not part of the study data package, and cannot be publicly shared because they derive from a restricted clinical sequencing context.

## Code Availability

The analysis scripts used to generate tables, figures and reviewer-response audits are maintained under `info/scripts` and will be released with the processed data package before submission. Key audit scripts include `run_knn_mi_robustness_audit.py`, `run_high_k_compressed_baselines.py`, `run_p_msp_contribution_audit.py`, `run_property_redundancy_and_runtime_audit.py`, `generate_supp_fig_s8_redundancy_runtime_audit.py`, `run_p_channel_counterfactual_audit.py` and `run_msp_bin_gamma_sensitivity_audit.py`. The final repository URL, software licence and archived release identifier are to be inserted before journal submission.

## Ethics and Data Governance

No patient-level clinical sequencing reads, patient identifiers or patient-derived labels were analyzed in this study. The authors should confirm the institutional wording for this boundary statement before submission.

## Author Contributions

TBD before submission. Suggested CRediT-style roles to confirm: conceptualization; methodology; software; formal analysis; investigation; data curation; writing - original draft; writing - review and editing; visualization; supervision; funding acquisition.

## Funding

TBD before submission. Insert grant numbers and funder names exactly as required by NAR/OUP.

## Acknowledgements

TBD before submission. Include only contributors who meet acknowledgement criteria and do not meet authorship criteria.

## Conflict of Interest

The authors should confirm the final statement before submission. If accurate, use: `The authors declare no competing interests.`

## References

The final submission copy should convert temporary citation keys such as `[@Wood2019]` into NAR/OUP-compliant numbered references. Do not leave citation keys in the final submission manuscript. The current working bibliography is `info/references/references.bib`; unresolved or newly added citation keys should be checked against primary metadata before export.
