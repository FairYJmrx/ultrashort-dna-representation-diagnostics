# Materials and Methods and Results

## Materials and Methods

### Study design

We designed the study as a representation-diagnostic analysis rather than an end-to-end clinical classification benchmark. The central question was what information remains available in short-read sequence representations after controlled perturbation, and whether biochemical and coarse positional summaries add usable evidence beyond an exact identity backbone. CK4 and CK5 were used as reverse-complement canonical k-mer identity baselines, P denoted global biochemical-property summaries, MSP denoted multi-scale positional property pooling, CK4+P, CK4+MSP and CK4P-MSP tested compact mixed representations, full-position matrices were treated as diagnostic upper bounds, and the canonical spaced-property (CSP) control served as a spaced-seed mechanism comparator.

This design makes two questions testable. First, whether a compact mixed representation remains close to its clean counterpart under nuisance perturbation while retaining enough information for shallow readout. Second, whether any apparent benefit of the P or MSP channels can be separated from dimensionality, normalization, or dilution in a mixed L2 space. We therefore evaluated compact stability, same-dimension PCA/SVD controls, dimension-matched high-k compressed k-mer baselines, block-weight sensitivity, paired non-parametric tests, k-nearest-neighbor mutual-information robustness checks, P/MSP contribution and counterfactual controls, P/MSP redundancy, feature-extraction runtime and error-aware ART strata as parts of one evidence chain. Throughout, L2 in a mixed representation is interpreted as a standardized diagnostic drift after block construction and normalization, not as a natural biophysical distance between commensurate physical units.

The 69 and 75 bp settings were chosen because they fall within the commonly reported 50-75 bp post-QC mNGS read-length regime described in the interpretation literature (Yang, *Practice and Progress of mNGS Report Interpretation*, p. 99). No patient-level reads, labels or sequence content from the restricted clinical context were analyzed; the context informed only the choice of representative ultra-short length conditions. The remaining lengths were selected for sensitivity analysis: 100, 125 and 150 bp test whether the trends persist as reads become less extreme, and 300 bp is used only as an extended-read reference in selected boundary analyses.

[Insert Figure 1 here: representation-diagnostic framework and read-length regime.]

### Representation families

The representation families were defined to separate identity, global biochemical summaries and coarse positional information. CK4 and CK5 count reverse-complement canonical contiguous k-mers. P summarizes hydrogen-bond class, GC content, purine content, electron-ion interaction potential (EIIP)-like values, N fraction, entropy and length-related properties at the read level. MSP applies the same property family over relative-position bins; its purpose is not to create a larger sequence vocabulary, but to return low-dimensional positional information to an otherwise order-poor k-mer frequency vector. The default 2+3+4+6 binset was chosen as a coarse-to-fine relative-position summary whose finest scale remains above single-position resolution across the 69-150 bp regime. CK4+P concatenates canonical 4-mer identity with global property summaries, CK4+MSP tests positionalized property pooling without the global P block, and CK4P-MSP combines all three blocks. Full-position identity or property matrices retain per-position information and were used only to estimate an upper bound on positional readability. CSP combines spaced-seed counts with property summaries and was used to test whether matching-oriented spaced-seed priors transfer into dense representation diagnostics.

For mixed representations, each block was computed separately and internally L2-normalized before weighted assembly. For read $s_i$, let $\mathbf{K}_i$, $\mathbf{P}_i$ and $\mathbf{M}_i$ denote the reverse-complement canonical 4-mer identity block, the global biochemical-property block, and the multi-scale positional-property block, respectively. The internally normalized blocks were defined as

$$
\hat{\mathbf{K}}_i=\frac{\mathbf{K}_i}{\left\|\mathbf{K}_i\right\|_2},\quad
\hat{\mathbf{P}}_i=\frac{\mathbf{P}_i}{\left\|\mathbf{P}_i\right\|_2},\quad
\hat{\mathbf{M}}_i=\frac{\mathbf{M}_i}{\left\|\mathbf{M}_i\right\|_2},
$$

with zero-norm safeguards applied before normalization. The assembled compact representation was then

$$
\mathbf{x}_i
=
\frac{1}{\sqrt{\alpha^2+\beta^2+\gamma^2}}
\left[\alpha \hat{\mathbf{K}}_i \,;\, \beta \hat{\mathbf{P}}_i \,;\, \gamma \hat{\mathbf{M}}_i\right],
$$

where $\alpha$, $\beta$ and $\gamma$ are block weights and $[\cdot\,;\,\cdot]$ denotes concatenation. Because the block norms are fixed before concatenation, the denominator is a fixed scalar for a given weight setting rather than a read-specific global norm. The reported global drift metric was

$$
d(i,j)=\left\|\mathbf{x}_i-\mathbf{x}_j\right\|_2,
$$

which should be interpreted as a standardized diagnostic drift in the assembled feature space, not as a natural physical distance between commensurate biological units. This definition also gives the block-normalized distance identity

$$
d_{\mathrm{mix}}^2(i,j)
=
\frac{
\alpha^2\left\|\hat{\mathbf{K}}_i-\hat{\mathbf{K}}_j\right\|_2^2
+\beta^2\left\|\hat{\mathbf{P}}_i-\hat{\mathbf{P}}_j\right\|_2^2
+\gamma^2\left\|\hat{\mathbf{M}}_i-\hat{\mathbf{M}}_j\right\|_2^2
}{\alpha^2+\beta^2+\gamma^2}.
$$

For comparison with the identity-only drift $d_K(i,j)=\|\hat{\mathbf{K}}_i-\hat{\mathbf{K}}_j\|_2$, the mixed squared drift is lower than $d_K^2$ when

$$
\beta^2\left(d_P^2-d_K^2\right)+\gamma^2\left(d_M^2-d_K^2\right)<0,
$$

where $d_P$ and $d_M$ are the corresponding blockwise drifts. Thus, lower property and MSP drift than identity drift is a sufficient, but not necessary, condition for a lower mixed drift. This explicit block construction allowed us to test whether the observed gains persisted when identity and property weights were changed. The design therefore does not assume that concatenation is intrinsically useful; it treats concatenation as a hypothesis that must survive same-dimension baselines, dimension-matched high-k compressed baselines, block-weight audits, blockwise drift decomposition and P/MSP counterfactual controls.

[Insert Table 1 here: representation families and diagnostic roles.]

### Data layers and perturbation design

The experiments were organized into eight data layers, with the scale of each layer reported in Table 2. The WGS perturbation layer contained 25,200 rows from 3,600 clean templates across six genera, 21 species and six read lengths. The position-property ablation layer expanded this to 36,000 rows over the same template set and length grid. ART Illumina-like simulation contributed 75,592 paired rows from 37,796 templates across 69-150 bp reads. CAMI_TOY_low probes used a 104,166-row initial labelled subset and a 216,000-row expanded subset with 30 labels at 69, 75 and 100 bp. The CAMI II marine lightweight probe used 4,000 anonymous source reads and 48,000 length/condition rows at 69, 75 and 100 bp. The local mutation layer used 250 triplets per analysis cell across 12 representations, four local modes and three read lengths. WGS-derived paired perturbations measured clean-versus-perturbed stability. ART Illumina-like simulation tested whether the same trends persisted under simulator-derived sequencing errors. A quality-stratified ART audit further split simulator outputs by read-quality strata, providing an error-aware check without claiming to model all clinical error processes. CAMI_TOY_low probes tested external metagenomic readability, whereas the CAMI II marine subset tested perturbation stability on anonymous external metagenomic reads without read-level taxonomic labels in this lightweight analysis. Controlled position and order tasks tested whether positional information was recoverable. Local mutation sensitivity compared structured local changes with matched nuisance perturbation. Boundary probes tested spaced-seed transfer, context visibility and ARG/SNP limits.

For CAMI_TOY_low, labels were normalized to a species-level view when available, and genus-level and target-versus-background probes were derived from the same normalized label field. Background or unclassified reads were retained only for probes that explicitly required a target/background split, whereas the labelled subsets were used for lightweight external readout at 30 labels across 69, 75 and 100 bp. The initial labelled subset supported the first external probe, and the expanded subset was used when the probe required broader label coverage. This lightweight CAMI use was intended to test whether representation-level readability survives an external metagenomic probe, not to approximate production-scale community profiling.

We also added a lightweight CAMI II marine subset as an external short-read stability probe. We streamed a prefix of CAMI II marine short-read sample 0 and parsed 4,000 anonymous 150 bp reads from the embedded `anonymous_reads.fq.gz` member. These reads were truncated to 69, 75 and 100 bp and expanded into clean, `N_3pct`, `substitution_1pct` and `substitution_1pct_N_3pct` conditions, yielding 48,000 length/condition rows. CAMI II provides benchmark truth resources, but the anonymous FASTQ headers did not provide read-level taxonomic labels in the streamed-read file used here, and the separate OTU-specific truth bundles were not reconstructed for this lightweight analysis. This CAMI II probe was therefore restricted to paired perturbation-stability metrics. It should be interpreted as an external metagenomic stability check, not as CAMI II taxonomic validation.

This layered simulation design was used because each component isolates a different failure mode. The controlled WGS grid makes perturbation type, read length and representation family directly comparable. ART adds a recognized Illumina-like simulator layer, but it is retained as a consistency check rather than treated as ground-truth clinical sequencing physics. The quality-stratified ART audit adds a more explicit error-aware view of the same simulator-derived layer. It supports statements about robustness across quality strata, but it does not by itself establish clinical validation.

[Insert Table 2 here: data layers, diagnostic questions, metrics and claim boundaries.]

### Metrics and statistical analysis

Perturbation stability was quantified by paired cosine similarity, paired L2 drift and nearest-clean retrieval. Readout was quantified by macro-F1 and accuracy from shallow probes, mainly logistic regression and nearest-centroid classification. Compactness was measured by feature dimension. Local mutation analysis used selective-sensitivity ratios and delta-readout to distinguish nuisance stability from sensitivity to structured local change. Bootstrap intervals summarized cell-level variation. Paired Wilcoxon tests with Benjamini-Hochberg correction were used for matched stability comparisons. Same-dimension PCA/SVD controls addressed dimensionality effects, and block-weight audits tested whether mixed-feature conclusions were stable under reasonable reweighting of identity and property blocks.

The mixed-feature question was also tested through empirical information and counterfactual audits. For a perturbation label $Y$ and representation-derived distance or readout features $X$, we estimated discretized pooled and conditional MI proxies using equal-frequency binning. The main pooled distance audits used eight bins, joint P/MSP summaries used five- or six-bin discretizations depending on the audit, and empirical permutation baselines used 200 shuffles per cell. These values are reported as estimator-dependent descriptive proxies rather than absolute physical information quantities. To test estimator sensitivity, we also ran a nearest-neighbor MI robustness audit using Ross/Kraskov-Stogbauer-Grassberger (KSG)-style estimators for continuous distance summaries and a discrete local-versus-noise perturbation label. This audit used $k=5$, 50 label permutations, 50 stratified subsampling repetitions and low-dimensional summaries including $d_K$, $d_P$, $d_M$, $d_K+d_P$, $d_K+d_M$, and $d_K+d_P+d_M$ across the 69, 100 and 150 bp local-mutation cells. To separate the global and positional property layers, we additionally evaluated CK4, CK4+P, CK4+MSP and CK4P-MSP under the same block-normalized assembly rule. This direct contribution audit measured paired stability and local delta-readout, and was paired with a redundancy audit based on rank, canonical-correlation analysis and row-wise P/MSP alignment. To test whether the P/MSP contribution was more than additional dimensions, we also constructed CK4 plus permuted P/MSP blocks and CK4 plus Gaussian P/MSP blocks. These controls preserve a larger feature space but remove the sequence-linked biochemical mapping. The analysis was used as empirical support for perturbation-associated signal in the added property layers, not as a dataset-independent information-theoretic guarantee or as evidence that P and MSP measure unrelated physical quantities.

We added a dimension-matched high-k compression audit to avoid comparing CK4P-MSP only with short contiguous k-mer baselines. Canonical $k=15$ signals were compressed to approximately the 222-feature CK4P-MSP budget using three controls: MinHash-style signatures, hashing-trick counts and sparse random projection. These baselines were evaluated on the same 69, 75, 100 and 150 bp perturbation grid using paired cosine similarity, L2 drift, nearest-clean retrieval and shallow readout. This audit tests whether the stability of CK4P-MSP persists against high-specificity k-mer information under a comparable compactness constraint. Finally, a feature-extraction runtime audit compared CK4P-MSP with CK4, CK4+P and dimension-matched high-k compressed controls. Runtime was treated as an engineering boundary, not as a primary performance claim.

### Reproducibility

All generated results used local scripts and result tables stored under the project workspace. Main figure assets are in `info/paper/figures`, table assets are in `info/paper/tables`, the baseline supplementary figures are generated by `info/scripts/generate_paper_supplementary_figures.py`, the kNN MI robustness audit by `info/scripts/run_knn_mi_robustness_audit.py`, the high-k compressed baseline audit by `info/scripts/run_high_k_compressed_baselines.py`, the P/MSP contribution audit by `info/scripts/run_p_msp_contribution_audit.py`, the P/MSP redundancy and runtime audit by `info/scripts/run_property_redundancy_and_runtime_audit.py`, the P-channel counterfactual audit by `info/scripts/run_p_channel_counterfactual_audit.py`, the CAMI II marine lightweight probe by `info/scripts/run_cami2_marine_lightweight_probe.py`, and its supplementary figure by `info/scripts/generate_supp_fig_s10_cami2_marine_probe.py`. The supported scope is compact and controlled: biochemical and position-aware summaries are evaluated as auxiliary diagnostic channels for representation-level robustness auditing in short-read settings.

## Results

### Empirical mixed-feature information audit under local perturbation

We first tested whether the added biochemical channel showed perturbation-associated signal rather than simply changing the scale of a mixed feature space. In the local-mutation audit, the equal-frequency MI proxy gave a higher pooled value for joint CK4+P/MSP distances than for CK4 distance alone, and the conditional proxy remained positive after conditioning on CK4 distance. Because discretized MI estimates are estimator-dependent, we treated this result as a descriptive screen and repeated the analysis with a k-nearest-neighbor MI robustness audit on low-dimensional distance summaries. Across the 12 local-mutation cells, the kNN audit estimated higher MI for the joint $d_K+d_P+d_M$ summaries than for $d_K$ alone, with a mean incremental estimate of approximately 0.138 bits beyond $d_K$ and permutation support across the tested cells. This result is reported as estimator-dependent empirical evidence: on the tested perturbation grid and estimators, P/MSP distances showed perturbation-associated signal beyond a pure identity-only distance.

This audit is important for the interpretation of CK4P-MSP. A lower standardized drift could otherwise be attributed to dimensional dilution by low-variance auxiliary features. The MI robustness checks support a more specific conclusion: the property and MSP channels contributed estimator-dependent perturbation-associated signal under the tested local-change regime, while the block-weight audit separately checked that the conclusion was not tied to one arbitrary block scaling. The claim is therefore metric-based and empirical, not a statement that heterogeneous L2 coordinates have identical physical units.

[Insert Supplementary Figure S2 here or cite it from the main text: empirical MI and conditional-MI audit.]

[Insert Supplementary Figure S7 here or cite it from the main text: kNN MI robustness and high-k compressed baseline audit.]

[Insert Supplementary Figure S5 here or cite it from the main text: P-channel counterfactual and short-bin reliability audit.]

### Global and positional property layers have related but distinct roles

We then separated the two property layers directly. In a matched contribution audit over 69, 75, 100 and 150 bp reads, CK4 alone had a mean paired L2 drift of 0.254. Adding either global P or MSP reduced this drift to 0.182 and 0.181, respectively, and CK4P-MSP reduced it further to 0.150. Thus, both property layers contributed to nuisance-perturbation stability under the block-normalized metric.

The local delta-readout pattern was more specific. CK4 and CK4+P achieved mean macro-F1 values of 0.888 and 0.894 for distinguishing structured local change from matched nuisance perturbation, whereas CK4+MSP reached 0.976 and CK4P-MSP reached 0.977. This indicates that the positionalized property layer, rather than the global P block alone, carried most of the coarse positional readout gain. This supports the intended design: P provides a global biochemical stability summary, whereas MSP uses the same property family to return low-dimensional positional information to a compact identity-frequency backbone.

The redundancy audit also cautions against overinterpreting P and MSP as separable sources. Across the tested lengths, the first canonical correlation between P and MSP was near one and their first principal components were strongly aligned, as expected because both blocks are derived from the same biochemical property family. However, MSP had higher numerical rank than P, and row-wise P/MSP alignment after compression was incomplete. We therefore interpret the blocks as related layers at different scales, not as interchangeable evidence sources or as measurements of unrelated physical quantities.

[Insert Supplementary Figure S8 here or cite it from the main text: P/MSP contribution, redundancy and runtime audit.]

[Insert Supplementary Figure S9 here or cite it from the main text: P/MSP relation audit (CCA and correlation heatmap).]

### MSP short-bin reliability remains usable at 69-75 bp

We next tested whether MSP becomes noise-dominated when ultra-short reads are divided into finer relative-position bins. The short-bin audit did not show an immediate loss of reliability at 69 or 75 bp. In the stability screen, moving from a 2-bin MSP to the full 2+3+4+6-bin MSP changed paired cosine and L2 drift only slightly at the default $\gamma=1$ setting: at 69 bp, paired cosine remained approximately 0.986 and L2 drift remained near 0.147; at 75 bp, paired cosine remained approximately 0.987 and L2 drift remained near 0.141. Retrieval also remained effectively saturated.

The local delta-readout audit did not show an immediate short-bin failure. Finer multi-scale pooling increased mutation readout at fixed gamma. At 69 bp and $\gamma=1$, mean macro-F1 increased from approximately 0.865 with 2 bins to approximately 0.899 with 2+3 bins, 0.946 with 2+3+4 bins and 0.953 with 2+3+4+6 bins. The same monotonic pattern persisted at 100 and 150 bp. Bootstrap widths for pooled property features remained small, whereas worst-case binomial sampling error increased as expected when bins narrowed. The combined interpretation is therefore restrained but favorable: static MSP did not become noise-dominated in the tested ultra-short-read regime, yet it should still be interpreted as a coarse positional summary rather than as an optimized variance-aware weighting model.

[Insert Supplementary Figure S6 here or cite it from the main text: MSP binset and gamma-sensitivity audit.]

### Error-aware ART perturbation audit

We next asked whether the external simulator evidence depended on treating ART as one pooled error source. In the quality-stratified ART audit, representative compact controls remained readable across low-, mid- and high-quality bins. The property-aware compact representation preserved high paired cosine and bounded L2 drift across quality strata, and the hybrid identity/spaced representation retained retrieval and readout consistency.

These results strengthen, but do not overstate, the ART evidence. They show that the main pattern is not restricted to an undifferentiated simulator summary. They do not claim that ART quality strata capture the full physical error distribution of a clinical sequencing run.

[Insert Supplementary Figure S3 here or use it as a Figure 4 inset: quality-stratified ART audit.]

### Compact biochemical summaries reduce perturbation drift

The first main experimental block tested whether compact property-aware representations remained closer to their clean counterparts than identity-only baselines. Across the WGS-derived perturbation grid, CK4P-MSP and related property-aware compact representations retained high paired cosine and lower L2 drift while preserving nearest-clean retrieval. In the compact summary, CK4P-MSP achieved paired cosine around 0.991 with L2 drift around 0.116 at 222 features, whereas identity-only compact baselines showed higher drift under the same perturbation families.

The same conclusion survived several fairness checks. Same-dimension PCA/SVD controls showed that the mixed compact result was not simply a consequence of using more features. Dimension-matched high-k compression controls further addressed whether a conventional high-specificity k-mer representation could recover the same behavior under the CK4P-MSP feature budget. In that audit, CK4P-MSP retained higher paired cosine and lower L2 drift than $k=15$ random projection, MinHash and hashed baselines at approximately 222 features (paired cosine 0.996 and L2 drift 0.078 for CK4P-MSP, compared with paired cosine 0.848, 0.841 and 0.794 and L2 drift 0.484, 0.506 and 0.572 for the three compressed high-k controls). Shallow readout differences were modest (logistic macro-F1 0.401 for CK4P-MSP versus 0.396 for the hashed $k=15$ control), so this result supports a compact perturbation-stability advantage rather than an end-to-end classifier claim. Paired Wilcoxon tests over matched analysis cells supported the stability differences for key comparisons after multiple-testing correction. Block-weight audits showed that stability and readout conclusions did not depend on one fixed identity/property weighting. P/MSP counterfactual controls further separated dimensionality from sequence-linked biochemical information: CK4 plus permuted P/MSP approached the stability of CK4P-MSP but did not reproduce its local delta-readout (macro-F1 0.875 versus 0.977), while CK4 plus Gaussian P/MSP collapsed both stability and readout. The P/MSP contribution audit further showed that CK4+P and CK4+MSP both reduced drift relative to CK4, while MSP accounted for most of the positional delta-readout gain. Together, these controls show that the stability trend is not explained by feature count, a single weighting choice or random auxiliary columns.

[Insert Figure 2 here: compact stability under perturbation.]

[Insert Supplementary Figure S1 here or cite it from the Results text: baseline and mixed-metric audit.]

[Insert Supplementary Figure S7 here or cite it from the Results text: kNN MI robustness and high-k compressed baseline audit.]

### CK4P-MSP balances compactness, stability and shallow readout

We then evaluated CK4P-MSP as a nested ablation rather than as a standalone classifier. CK4 tested compact identity alone. CK4+P tested whether global biochemical summaries were sufficient. CK4+MSP tested whether positionalized property pooling carried information beyond identity without the global P block. CK4P-MSP tested the combined trade-off between stability, dimensionality and shallow readout when global and positional property layers were added together. This hierarchy is central to the method: the representation is intended to preserve exact identity evidence while adding interpretable biochemical and positional auxiliary channels.

The resulting trade-off supported the intended role. CK4P-MSP remained compact, reduced perturbation drift relative to CK4 and CK5 identity baselines, and retained competitive macro-F1 in shallow readout. Its role is not standalone readout, but a stable and interpretable middle ground between identity-only compact features and high-dimensional full-position matrices.

[Insert Figure 3 here: stability-readout-dimension trade-off.]

[Insert Table 3 here: exact compact main-method metrics.]

### External ART and CAMI probes separate stability from task-limited readability

ART and CAMI were used to test whether the representation trend survived outside the handcrafted perturbation grid, while keeping stability and readout as separate questions. ART provided simulator-derived sequencing-error evidence: in the paired-cosine summary, property-aware and spaced-property representations retained higher clean-versus-perturbed similarity than the identity-only k-mer comparators (Figure 4A). CAMI_TOY_low provided a lightweight external metagenomic readout probe with two different granularities. A coarse target-versus-background task remained readable across compact representations (Figure 4B), whereas the 30-label fine probe was substantially lower in absolute macro-F1 (Figure 4C). Thus, the external CAMI result supports representation-level readability at a coarse task level, but it also shows that fine-grained label readout remains task-limited and should not be interpreted as production-grade taxonomic classification.

The quality-stratified ART audit complements this result by showing that simulator consistency persisted across read-quality bins. To test whether the compact-stability trend was restricted to CAMI_TOY_low, we added the CAMI II marine anonymous-read subset probe (Supplementary Figure S10). Across all nine combinations of length (69, 75 and 100 bp) and perturbation (`N_3pct`, `substitution_1pct` and `substitution_1pct_N_3pct`), CK4P-MSP had the lowest mean L2 drift among the tested compact representations and retained nearest-clean retrieval. Mean paired cosine for CK4P-MSP was approximately 0.995 under N masking, 0.998 under substitution and 0.992-0.993 under the combined perturbation, with mean L2 drift ranges of 0.095-0.102, 0.047-0.048 and 0.114-0.121, respectively. Marine metagenomes may differ from clinical or pathogen-rich contexts in sequence composition, so this result should be interpreted as an external sequence-source stability probe. It supports the external stability pattern in a more complex CAMI II metagenomic read source, while remaining a stability probe without read-level taxonomic labels in this lightweight analysis rather than a taxonomic validation.

Together, these analyses support external consistency under controlled simulator and benchmark resources, while preserving the manuscript boundary: ART supports simulator-derived stability consistency, CAMI_TOY_low supports external readability at a task-limited level, and CAMI II marine supports anonymous-read stability rather than taxonomic validation.

[Insert Figure 4 here: ART paired-cosine stability, CAMI coarse target/background readout and CAMI fine label-probe readout.]

[Insert Supplementary Figure S10 here or cite it from the main text: CAMI II marine anonymous-read stability probe.]

### Full-position matrices define a positional upper bound rather than a deployment default

Full-position encodings were used to estimate what is gained when fine-grained layout information is retained. In controlled position and order tasks, full-position identity or property matrices improved positional readability compared with compact summaries. This was expected, because these matrices preserve per-position structure that compact summaries intentionally compress.

The result is best interpreted as an upper-bound diagnostic. Full-position matrices clarify the value of positional information, but their high dimensionality and task specificity make them unsuitable as the default representation for compact short-read auditing. CK4P-MSP therefore occupies a different role: it does not match the full positional upper bound, but it recovers part of the positional information at a much smaller feature cost.

[Insert Figure 5 here: full-position diagnostic upper bound.]

### Local mutation analysis separates robustness from selective sensitivity

A robust representation should not be insensitive to all changes. We therefore tested whether local biochemical change remained distinguishable from matched nuisance perturbation. Property-aware and full-position channels showed larger response to structured local mutation than to matched noise in the relevant comparisons, while CK4P-MSP preserved delta-readout at compact dimensionality. The P/MSP counterfactual audit sharpened this result by showing that the real biochemical mapping, not only extra columns, was needed to obtain the strongest local-change readout.

This result supports a division of labor. Paired cosine and L2 drift quantify nuisance stability, whereas selective-sensitivity ratios and delta-readout quantify whether structured local changes remain readable. CK4P-MSP is therefore not merely a smoothed representation. It can remain stable under nuisance perturbation while preserving enough auxiliary information for local-change readout.

[Insert Figure 6 here: local mutation sensitivity and delta-readout.]

[Insert Table 4 here: exact local mutation metrics.]

[Insert Supplementary Figure S4 here or cite it: mutation-fraction sweep.]

### Boundary analyses constrain the interpretation

The boundary probes were included to prevent overextension of the representation claim. Spaced-seed transfer was useful as a mechanism comparator, but matching-oriented seed priors did not automatically become a universal dense-feature advantage. Context visibility depended on whether the relevant relation was present within the read. ARG/SNP interpretation required identity, annotation and allele-level evidence beyond what compact property summaries can provide.

These negative and boundary results are part of the manuscript's logic. They keep the claim focused on representation diagnostics and auxiliary robustness auditing, rather than allowing the compact feature space to be misread as a full biological interpretation system.

[Insert Table 5 here: boundary and mechanism summary.]

## Figure and Table Placement Summary

Main figures: Figure 1 after Study design; Table 1 after Representation families; Table 2 after Data layers; Figure 2 and Supplementary Figure S1 after Compact stability; Figure 3 and Table 3 after CK4P-MSP trade-off; Figure 4 after External probes; Figure 5 after Full-position upper bound; Figure 6, Table 4 and Supplementary Figure S4 after Local mutation; Table 5 after Boundary analyses.

Supplementary figures generated for the paper folder: Supplementary Figure S1 baseline and mixed-metric audit; Supplementary Figure S2 MI audit; Supplementary Figure S3 error-aware ART audit; Supplementary Figure S4 mutation-fraction sweep; Supplementary Figure S5 P-channel counterfactual and short-bin reliability audit; Supplementary Figure S6 MSP binset and gamma-sensitivity audit; Supplementary Figure S7 kNN MI robustness and dimension-matched high-k compressed baseline audit; Supplementary Figure S8 P/MSP contribution, redundancy and runtime audit; Supplementary Figure S9 P/MSP relation audit (CCA and correlation heatmap); Supplementary Figure S10 CAMI II marine anonymous-read stability probe. These figures are intentionally kept separate from the main visual line so that each main figure answers one central manuscript question.
