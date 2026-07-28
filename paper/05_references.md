# Back Matter and Reference Support

This file records citation support, availability statements and submission back matter for the paper-folder manuscript. Reference formatting remains provisional until the final bibliography is exported in the target journal style.

## Citation support plan

### Abstract support

Short-read mNGS context can be supported by `Wilson2014`, `Wilson2019`, `Chiu2019`, `Martin2011`, `Bolger2014` and `Salter2014`. ART and CAMI resources can be supported by `Huang2012ART`, `Sczyrba2017` and `Meyer2022`. The abstract should normally remain uncited unless the final venue requests abstract citations.

### Introduction support

The exact identity backbone should cite Kraken/Kraken 2, CLARK, Centrifuge and Kaiju, with benchmark context from CAMI where appropriate (`Wood2014`, `Wood2019`, `Ounit2015`, `Kim2016`, `Menzel2016`, `Sczyrba2017`, `Meyer2022`). Alignment-free and sketching routes should cite Mash/MinHash and alignment-free reviews (`Ondov2016`, `Zielezinski2017`). Biochemical and signal encodings should cite classic Voss, Jeffrey and EIIP-style representations (`Voss1992`, `Jeffrey1990`, `Anastassiou2001`, `Cristea2002`, `Nair2006`). Deep metagenomic and sequence-token methods should cite DeepMicrobes, MetaTransformer, BarcodeBERT and related classifiers, while DNA foundation-model context can cite DNABERT, DNABERT-2, Nucleotide Transformer, HyenaDNA, Evo and GENA-LM (`Liang2020`, `Ji2021`, `Zhou2024`, `DallaTorre2025`, `Nguyen2023`, `Nguyen2024Evo`, `Fishman2025`, `Wichmann2023`). These models should be discussed as representation context, not as direct 69/75 bp comparators in the current study.

For the read-length sentence, *Practice and Progress of mNGS Report Interpretation* (Yang, p. 99) can be used as background support for the commonly reported 50-75 bp post-QC mNGS regime. Verify the exact edition, publisher and page number from the copyright page before the final reference export. Keep this citation separate from the Data Availability provenance statement, which is about the specific design choice for 69/75 bp and not about the general field range.

### Results support

Most Results claims are supported by internal experiments rather than external literature. The figure/table inventory in `info/paper/figure_table_inventory.md` maps each claim to generated assets and source scripts. Statistical and baseline controls are supported by reviewer-response outputs under `info/results/stage3/reviewer_response`, including same-dimension PCA/SVD baselines, mixed-metric block-weight audits, MI and conditional-MI proxy summaries, k-nearest-neighbor MI robustness checks, dimension-matched high-k compressed k-mer baselines, P/MSP contribution audits, P/MSP redundancy and runtime audits, P-channel counterfactual controls, MSP bin/gamma sensitivity analyses, and the CAMI II marine lightweight stability probe.

## Data Availability

All processed data tables, figure source summaries and analysis outputs generated for this study are maintained in a private GitHub review repository under the FairYJmrx account, in the ultrashort-dna-representation-diagnostics repository on the release branch. Reviewer access will be provided through the submission system or by adding a journal-supplied account as a read-only collaborator. A public archival DOI will be minted from the frozen release when the authors make the repository public.

Publicly reused resources include simulator- and benchmark-derived materials used for ART, CAMI_TOY_low and CAMI II marine analyses, which will be cited through the corresponding primary publications and public resource records in the final reference list. The CAMI II marine lightweight probe used the public CAMI II marine short-read sample 0 reads archive and its corresponding setup archive; exact resource URLs are listed in the review-access repository and will be included in the public archived release. Only a streamed prefix was parsed for the lightweight stability probe, and read-level taxonomic labels were not reconstructed from the separate truth resources for this analysis. The generated subset tables, stability summaries and source figure table are included in the review-access repository and will be included in the public release. Local restricted sequencing records were used only as read-length provenance for the 69 and 75 bp conditions. The underlying clinical sequencing reads were not used as experimental input, are not part of the study data package, and cannot be publicly shared.

## Code Availability

The analysis scripts used to generate tables, figures and reviewer-response audits are maintained in the same private review-access repository under an MIT licence. The repository README and release manifest map each manuscript figure, table and supplementary audit to its source script, input tables and generated outputs. Reviewer access will be provided during submission, and a public archived release identifier will be added after public release.

## Supplementary Data

Supplementary Data are available at *NAR Genomics and Bioinformatics* Online. The supplementary file includes Supplementary Figures S1-S10 and Supplementary Tables S1 and S2. The underlying machine-readable source tables and figure-generation inputs are included in the review-access repository and will be included in the public archived release.

## Ethics and Data Governance

No patient-level clinical sequencing reads, patient identifiers or patient-derived labels were analyzed in this study. Institutional wording for this boundary statement must be finalized before submission.

## Author Contributions

Ruixiang Mei: Conceptualization, methodology, software, formal analysis, investigation, data curation, visualization, writing - original draft, and writing - review and editing. Jianhua Huang: Supervision and writing - review and editing. Ruixiang Mei ORCID: https://orcid.org/0009-0003-2128-0726.

## Funding

Funding information will be finalized before submission.

## Acknowledgements

Acknowledgements, if any, will be finalized before submission.

## Conflict of Interest

The authors declare no competing interests.

## References

The final submission copy should convert temporary citation keys such as `[@Wood2019]` into NAR/OUP-compliant numbered references. Do not leave citation keys in the final submission manuscript. The current working bibliography is `info/paper_latex/references.bib`; unresolved or newly added citation keys should be checked against primary metadata before export.
