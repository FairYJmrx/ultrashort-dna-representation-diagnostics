# Materials and Methods and Results

## Materials and Methods

### Study design

We designed the study as a representation-diagnostic analysis of controlled short-read perturbation settings. Here, representation diagnostics denotes a prespecified set of representation-level measurements rather than a clinical decision rule: paired stability, nearest-clean retrieval, grouped local-change readout, feature dimension and blockwise decomposition. The central question was whether biochemical and coarse positional summaries add auditable evidence to a canonical local k-mer-composition backbone. CK4 and CK5 were reverse-complement canonical k-mer-composition baselines; P denoted global biochemical-property summaries; MSP denoted multi-scale positional property pooling. The seven non-empty K/P/MSP combinations were evaluated, full-position matrices were treated as positional upper bounds, and the canonical spaced-property (CSP) control served as a spaced-seed mechanism comparator.

This design makes two questions testable. First, whether a compact mixed representation remains close to its clean counterpart under nuisance perturbation while retaining representation-level readability. Second, whether the observed behavior can be assigned to metric-specific K, P or MSP contributions rather than to dimensionality, normalization or dilution in a mixed L2 space. We therefore combined a seven-group ablation with same-dimension PCA/SVD controls, dimension-matched high-k compressed k-mer baselines, block-weight sensitivity, paired non-parametric tests, k-nearest-neighbour mutual-information robustness checks, P/MSP relation analysis, feature-extraction runtime and error-aware ART strata. Shallow readout probes tested whether signal remained linearly accessible; they were not treated as production classifier performance. Throughout, mixed-space L2 is interpreted as standardized diagnostic drift after block construction and normalization, not as a natural biophysical distance between commensurate physical units.

The 69 and 75 bp settings fall within a commonly reported 50-75 bp mNGS read-length range [@Yang2026mNGS] and correspond to aggregate pre- and post-quality-control mean-length conditions observed in a restricted local sequencing context. Only these aggregate length conditions informed the design; no patient-level reads, labels, identifiers or sequence content were analysed. The two lengths were used as lower-read-length stress conditions, not as a claim that short reads are unusable. The remaining lengths were selected for sensitivity analysis: 100, 125 and 150 bp test whether the trends persist as reads become less extreme, and 300 bp is used only as an extended-read reference in selected boundary analyses.

[Insert Figure 1 here: representation-diagnostic framework and read-length regime.]

### Representation families

The representation families were defined to separate local k-mer composition, global biochemical summaries and coarse positional information. CK4 and CK5 count reverse-complement canonical contiguous k-mers. P summarizes hydrogen-bond class, GC content, purine content, electron-ion interaction potential (EIIP)-like values, N fraction, entropy and length-related properties at the read level. MSP applies per-base property channels over relative-position bins. Its purpose is not to create a larger sequence vocabulary or to reconstruct full position. Instead, it adds a coarse positional property summary to an otherwise order-poor k-mer-frequency vector. The default 2+3+4+6 binset was prespecified as a coarse-to-fine relative-position summary whose finest scale remains above single-position resolution across the 69-150 bp range. The seven-group ablation comprised K (136 dimensions), P (11), MSP (75), K+P (147), K+MSP (211), P+MSP (86) and K+P+MSP (222). Full-position composition or property matrices retained per-position information and were used only to estimate an upper bound on positional readability. CSP combines spaced-seed counts with property summaries and was used to test whether matching-oriented spaced-seed priors transfer into dense representation diagnostics.

For mixed representations, each block was computed separately and internally L2-normalized before weighted assembly. For read $s_i$, let $\mathbf{K}_i$, $\mathbf{P}_i$ and $\mathbf{M}_i$ denote the reverse-complement canonical 4-mer composition block, the global biochemical-property block, and the multi-scale positional-property block, respectively. The internally normalized blocks were defined as

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

where $\alpha$, $\beta$ and $\gamma$ are block weights and $[\cdot\,;\,\cdot]$ denotes concatenation. Unless otherwise stated, all three weights were set to 1. The block-weight audit compared equal weights with K-dominant $(2,1,1)$ and property-dominant $(1,2,2)$ settings; the separate MSP audit evaluated $\gamma\in\{0,0.25,0.5,1,2\}$. Because the block norms are fixed before concatenation, the denominator is a fixed scalar for a given weight setting rather than a read-specific global norm. The reported global drift metric was

$$
d(i,j)=\left\|\mathbf{x}_i-\mathbf{x}_j\right\|_2,
$$

which should be interpreted as a standardized diagnostic drift in the assembled feature space, not as a natural physical distance between commensurate biological units. This definition also gives the block-normalized distance identity

$$
\begin{aligned}
d_{\mathrm{mix}}^2(i,j)
&=
\frac{1}{\alpha^2+\beta^2+\gamma^2}
\Bigl[
\alpha^2\left\|\hat{\mathbf{K}}_i-\hat{\mathbf{K}}_j\right\|_2^2 \\
&\quad+
\beta^2\left\|\hat{\mathbf{P}}_i-\hat{\mathbf{P}}_j\right\|_2^2 \\
&\quad+
\gamma^2\left\|\hat{\mathbf{M}}_i-\hat{\mathbf{M}}_j\right\|_2^2
\Bigr].
\end{aligned}
$$

For comparison with the composition-only drift $d_K(i,j)=\|\hat{\mathbf{K}}_i-\hat{\mathbf{K}}_j\|_2$, the mixed squared drift is lower than $d_K^2$ when

$$
\beta^2\left(d_P^2-d_K^2\right)+\gamma^2\left(d_M^2-d_K^2\right)<0,
$$

where $d_P$ and $d_M$ are the corresponding blockwise drifts. Thus, lower P and MSP drift than K drift is a sufficient, but not necessary, condition for a lower mixed drift. The diagnostic protocol takes matched clean/perturbed reads, reports stability and nearest-clean retrieval, tests structured local change with grouped delta-readout, and decomposes the result through the seven-group ablation and prespecified conditional contrasts. It yields a representation profile rather than an automated acceptance threshold.

[Insert Table 1 here: representation families and diagnostic roles.]

### Data layers and perturbation design

The experiments were organized into eight data layers, with the scale of each layer reported in Table 2. The WGS perturbation layer contained 25,200 rows from 3,600 clean templates across six genera, 21 species and six read lengths. The position-property ablation layer expanded this to 36,000 rows over the same template set and length grid. ART Illumina-like simulation contributed 75,592 paired rows from 37,796 templates across 69-150 bp reads. CAMI_TOY_low probes used a 104,166-row initial labelled subset and a 216,000-row expanded subset with 30 candidate taxon identifiers at 69, 75 and 100 bp. The CAMI II marine lightweight probe used 4,000 anonymous source reads and 48,000 length/condition rows at 69, 75 and 100 bp. The local mutation layer used 250 triplets per analysis cell, four local modes and three read lengths. WGS-derived paired perturbations measured clean-versus-perturbed stability; ART added simulator-derived errors; CAMI resources supplied bounded external probes; controlled position and order tasks tested positional readability; and boundary probes tested spaced-seed transfer, context visibility and ARG/SNP limits.

For CAMI_TOY_low, read identifiers were joined to the available taxon mapping and normalized to a common label field [@Sczyrba2017; @Meyer2022]; the expanded source subset contained 30 candidate taxon identifiers. Unclassified reads were excluded from the labelled probe and retained only when a target-versus-background split explicitly required background reads. Per-class sampling was capped to prevent dominant labels from controlling the shallow probe. These CAMI readouts were generated before the public block-normalized CK4P-MSP contract and are retained only as external context; historical feature aliases were not relabelled as the current method. Consequently, the main text uses the coarse target-versus-background result and does not present the historical 30-label probe as a contract-v2 CK4P-MSP comparison.

We also added a lightweight CAMI II marine subset as an external short-read stability probe [@Meyer2022]. We streamed a prefix of CAMI II marine short-read sample 0 and parsed 4,000 anonymous 150 bp reads from the embedded `anonymous_reads.fq.gz` member. These reads were truncated to 69, 75 and 100 bp and expanded into clean, `N_3pct`, `substitution_1pct` and `substitution_1pct_N_3pct` conditions, yielding 48,000 length/condition rows. CAMI II provides benchmark truth resources, but the anonymous FASTQ headers did not provide read-level taxonomic labels in the streamed-read file used here, and the separate OTU-specific truth bundles were not reconstructed for this lightweight analysis. This CAMI II probe therefore reports paired perturbation-stability metrics on an external metagenomic sequence source rather than CAMI II taxonomic validation.

This layered simulation design was used because each component isolates a different failure mode. The controlled WGS grid makes perturbation type, read length and representation family directly comparable. ART adds a recognized Illumina-like simulator layer [@Huang2012ART], but it is retained as a consistency check rather than treated as ground-truth clinical sequencing physics. The quality-stratified ART audit adds a more explicit error-aware view of the same simulator-derived layer. It supports statements about robustness across quality strata, but it does not by itself establish validation on clinical sequencing data.

[Insert Table 2 here: data layers, diagnostic questions, metrics and claim boundaries.]

### Metrics and statistical analysis

Perturbation stability was quantified by paired cosine similarity, paired L2 drift and nearest-clean retrieval. Representation readability was quantified by macro-F1 and accuracy from shallow logistic-regression or nearest-centroid probes. Compactness was measured by feature dimension. Local mutation analysis used selective-sensitivity ratios and grouped delta-readout; all derivatives of one template were kept in the same fold through stratified grouped cross-validation. For the seven-group audit, three contrasts were prespecified: K+P+MSP versus P+MSP for the conditional K contribution, versus K+MSP for P, and versus K+P for MSP. Mean matched-cell differences were summarized by 10,000 paired bootstrap resamples. Two-sided paired Wilcoxon signed-rank tests [@Wilcoxon1945] were adjusted across the 12 metric-by-contrast rows by the Benjamini-Hochberg procedure [@Benjamini1995].

The mixed-feature question was also tested through empirical information audits. The historical equal-frequency discretized screen was retained as a supplementary descriptive check. The primary analysis used a Ross/Kraskov-Stogbauer-Grassberger (KSG)-style nearest-neighbour estimator [@Kraskov2004; @Ross2014] with $k=5$ on low-dimensional continuous summaries and a discrete local-versus-nuisance label, with 100 label permutations and 100 stratified subsamples per cell. These estimates are estimator-dependent empirical summaries rather than absolute physical information quantities. The seven-group contribution audit was paired with a relation audit based on rank, canonical-correlation analysis and row-wise P/MSP alignment. Together, these analyses test conditional empirical roles; they do not imply that P and MSP measure unrelated physical quantities.

We added a dimension-matched high-k compression audit to avoid comparing CK4P-MSP only with short contiguous k-mer baselines. Canonical $k=15$ signals were compressed to the 222-feature CK4P-MSP budget using hashing-trick counts and sparse random projection; these vector controls were evaluated on the same 69, 75, 100 and 150 bp perturbation grid using paired cosine similarity, L2 drift, nearest-clean retrieval and shallow readout. MinHash was assessed separately in its native collision/Jaccard geometry and was not treated as an L2 vector or linear readout feature. This audit tests whether compact stability persists against high-specificity k-mer information under a comparable vector budget. Finally, a feature-extraction runtime audit compared CK4P-MSP with CK4, CK4+P and the compact high-k controls. Runtime was treated as an engineering boundary, not as a primary performance claim.

### Reproducibility

The public implementation and the contract-v2 result namespace are maintained in the release repository. The manuscript-facing API is `methods/ck4p_msp.py`; the contribution, high-k, KSG, MSP sensitivity and redundancy/runtime audits are executed from `experiments/audits/` and mapped to their result tables in `docs/contract_v2_evidence_map.md`. Historical scripts and outputs remain available for provenance but are not aliases for the public block-normalized CK4P-MSP method. The supported scope is compact and controlled: biochemical and position-aware summaries are evaluated as block-decomposable representation-level audit coordinates in short-read settings.

## Results

### Empirical mixed-feature information audit under local perturbation

We first tested whether the added property channels showed perturbation-associated signal rather than only changing the scale of a mixed feature space. The contract-v2 KSG-style audit was applied to low-dimensional blockwise distance summaries for local change versus matched nuisance perturbation. Across 12 local-mutation cells, the mean estimate was 0.889 bits for $d_K+d_P+d_M$ and 0.752 bits for $d_K$ alone, an average incremental estimate of 0.138 bits. All primary summaries exceeded their label-permutation reference under the tested audit. This result is estimator-dependent empirical evidence: under the tested perturbation grid and estimator, P/MSP distance summaries improved local-versus-noise separability beyond the CK4 distance summary.

This audit does not turn the mixed representation into an information-theoretic theorem. It provides a complementary check on the ablation results: the property blocks contribute empirically detectable perturbation signal under the tested local-change regime, while the block-normalized metric remains a standardized diagnostic drift rather than a physical distance with commensurate units.

[Insert Supplementary Figure S2 here or cite it from the main text: KSG-style empirical separability audit.]

### Global and positional property layers have related but distinct roles

We then evaluated all seven non-empty K/P/MSP combinations over 69, 75, 100 and 150 bp reads. Pure property summaries had the lowest numerical drift (P, 0.025; MSP, 0.027; P+MSP, 0.027), but they did not preserve the same nearest-clean behavior as K-containing representations: retrieval was 0.295 for P and 0.942 for P+MSP, compared with 1.000 for CK4P-MSP. Relative to P+MSP, adding K increased retrieval by 0.058 (95% bootstrap CI 0.036-0.081; BH-adjusted $q=7.3\times10^{-4}$) while increasing, rather than decreasing, drift.

Conditional effects differed by audit axis. Adding P to CK4+MSP reduced mean drift from 0.156 to 0.129 (improvement 0.027, 95% CI 0.023-0.031; $q=2.4\times10^{-7}$), but did not materially change grouped delta-readout. Adding MSP to CK4+P produced a similar drift reduction and increased grouped local-change macro-F1 from 0.904 to 0.979 (difference 0.074, 95% CI 0.035-0.117; $q=7.3\times10^{-4}$). Adding K to P+MSP increased macro-F1 by only 0.008 and the interval included zero. These results assign P primarily to global stability, MSP to local-change readability and K to composition-linked retrieval under the tested grid; they do not establish statistical independence or universal necessity.

The redundancy audit also cautions against overinterpreting P and MSP as separable sources. Across the tested lengths, the first canonical correlation between P and MSP was near one and their first principal components were strongly aligned, as expected because both blocks are derived from the same biochemical property family. However, MSP had higher numerical rank than P, and row-wise P/MSP alignment after compression was incomplete. We therefore interpret the blocks as related layers at different scales, not as interchangeable evidence sources or as measurements of unrelated physical quantities.

[Insert Figure 2 here: seven-group K/P/MSP drift, grouped delta-readout and nearest-clean retrieval audit.]

[Insert Supplementary Figure S8 here or cite it from the main text: P/MSP contribution, redundancy and runtime audit.]

### MSP short-bin reliability remains usable at 69-75 bp

We next tested whether MSP becomes noise-dominated when ultra-short reads are divided into finer relative-position bins. The short-bin audit did not show an immediate loss of reliability at 69 or 75 bp. At the pre-specified $\gamma=1$ setting, the full 2+3+4+6 binset had paired cosine of approximately 0.985 and L2 drift of 0.153 at 69 bp, and paired cosine of approximately 0.987 and L2 drift of 0.140 at 75 bp. Retrieval remained effectively saturated.

The grouped local delta-readout audit did not show an immediate short-bin failure. At 69 bp and $\gamma=1$, mean macro-F1 increased from 0.876 with 2 bins to 0.907 with 2+3 bins, 0.951 with 2+3+4 bins and 0.959 with 2+3+4+6 bins. The same monotonic pattern persisted at 100 and 150 bp. Increasing $\gamma$ to 2 further reduced global drift, so the default $\gamma=1$ should be understood as a fixed balanced setting rather than an empirically optimal stability weight. The combined interpretation is restrained but favorable: static MSP did not become noise-dominated in the tested ultra-short-read regime, yet it remains a coarse positional summary rather than an optimized variance-aware weighting model.

[Insert Supplementary Figure S6 here or cite it from the main text: MSP binset and gamma-sensitivity audit.]

### Error-aware ART perturbation audit

We next asked whether the external simulator evidence depended on treating ART as one pooled error source. In the quality-stratified ART audit, representative compact controls remained readable across low-, mid- and high-quality bins. The property-aware compact representation preserved high paired cosine and bounded L2 drift across quality strata, and the hybrid identity/spaced representation retained retrieval and readout consistency.

These results strengthen, but do not overstate, the ART evidence. They show that the main pattern is not restricted to an undifferentiated simulator summary. They do not claim that ART quality strata capture the full physical error distribution of a clinical sequencing run.

[Insert Supplementary Figure S3 here or use it as a Figure 4 inset: quality-stratified ART audit.]

### Compact biochemical summaries reduce perturbation drift

The main compact-representation audit tested whether property-aware summaries remained closer to their clean counterparts than composition-only or compressed high-k baselines. Across the WGS-derived perturbation grid, CK4P-MSP retained paired cosine of 0.989 and mean L2 drift of 0.129 at 222 features, compared with 0.969 and 0.219 for CK4 (136 features) and 0.946 and 0.293 for CK5 (512 features). CK4+P was more globally stable than CK4P-MSP (paired cosine 0.996; drift 0.078), which is consistent with its role as a global property stability summary rather than a positional representation.

Dimension-matched high-k vector controls further addressed whether a conventional high-specificity k-mer representation could show the same behavior under the CK4P-MSP feature budget. At approximately 222 features, CK4P-MSP retained paired cosine 0.989 and L2 drift 0.129, compared with 0.821 and 0.524 for hashed $k=15$ counts and 0.868 and 0.447 for sparse random projection of $k=15$ counts. Shallow-readout differences were modest and did not favour CK4P-MSP over all high-k controls, so the result supports a compact perturbation-stability advantage rather than a predictive-performance claim. MinHash was assessed separately through its native estimated-versus-exact Jaccard agreement (mean estimated Jaccard 0.711, exact Jaccard 0.711, mean absolute error 0.021); it was not used as an L2-vector baseline. Paired Wilcoxon tests over matched analysis cells supported the primary stability contrasts after multiple-testing correction. Together, these controls show that the stability trend is not explained solely by feature count or by an arbitrary global feature projection.

[Insert Figure 3 here: dimension-matched compact stability and readability audit.]

[Insert Supplementary Figure S1 here or cite it from the Results text: baseline and mixed-metric audit.]

[Insert Supplementary Figure S7 here or cite it from the Results text: kNN MI robustness and high-k compressed baseline audit.]

### CK4P-MSP balances compactness, stability and representation readability

We next evaluated CK4P-MSP as a compact trade-off rather than as a single-metric winner. The seven-group result showed why the complete representation contains all three blocks: property-only variants were numerically stable but weakened nearest-clean retrieval, P improved global stability after conditioning on K+MSP, and MSP improved local-change readout after conditioning on K+P. CK4P-MSP therefore preserves a compact canonical local-composition backbone while exposing global biochemical and coarse positional audit channels.

The resulting trade-off supported the intended role. CK4P-MSP remained compact, reduced perturbation drift relative to CK4 and CK5 composition baselines, retained near-perfect nearest-clean retrieval and preserved accessible local-change signal. Its role is to provide a block-decomposable audit coordinate system between composition-only compact features and high-dimensional full-position matrices, rather than to maximize predictive accuracy against learned embeddings.

[Insert Table 3 here: exact compact main-method metrics.]

### External ART and CAMI probes separate stability from task-limited readability

ART and CAMI were used to test whether the general representation family showed consistent behaviour outside the handcrafted perturbation grid, while keeping stability and readout as separate questions. ART provided simulator-derived paired-error context, CAMI_TOY_low provided a lightweight external coarse target-versus-background readout probe, and CAMI II marine provided an anonymous external stability probe. These legacy external probes remain useful contextual checks, but they were generated before the public block-normalized method contract was introduced. They therefore do not supply the primary quantitative CK4P-MSP claims in this revision; those claims are restricted to the contract-v2 WGS perturbation, ablation and grouped local-readout analyses.

[Insert Figure 4 here: ART paired-cosine stability, CAMI coarse target/background readout and CAMI II anonymous-read stability.]

The quality-stratified ART audit and the CAMI II marine subset remain supplementary external checks. The former stratifies a simulator-derived error layer by read quality; the latter applies paired perturbations to anonymous public marine reads without reconstructing read-level taxonomic labels. Marine composition can differ materially from pathogen-rich or low-biomass mNGS sources. These probes therefore provide context for the breadth of the perturbation setting, not external taxonomic validation or a contract-v2 method comparison.

Together, the external resources motivate a future public-API rerun with a larger labelled benchmark. In the present revision, ART supports simulator context, CAMI_TOY_low supports task-limited external readability, and CAMI II supports anonymous-read stability only; the primary quantitative evidence remains the contract-v2 controlled WGS and grouped local-mutation analyses.

[Insert Supplementary Figure S10 here or cite it from the main text: CAMI II marine anonymous-read stability probe.]

### Full-position matrices define a positional upper bound rather than a deployment default

Full-position encodings were used to estimate what is gained when fine-grained layout information is retained. In controlled position and order tasks, full-position identity or property matrices improved positional readability compared with compact summaries. This was expected, because these matrices preserve per-position structure that compact summaries intentionally compress.

[Insert Figure 5 here: full-position diagnostic upper bound.]

The result is best interpreted as an upper-bound diagnostic. Full-position matrices clarify the value of positional information, but their high dimensionality and task specificity make them unsuitable as the default representation for compact short-read auditing. CK4P-MSP therefore occupies a different role: it does not match the full positional upper bound, but it retains a coarse positional property summary at a much smaller feature cost.

### Local mutation analysis separates robustness from selective sensitivity

A stable audit representation should remain responsive to structured changes, but the relevant notion of responsiveness depends on the metric. We therefore tested whether local biochemical change remained distinguishable from matched nuisance perturbation. In a distance-ratio analysis, CK4P-MSP did not exceed CK4: its local-mutation/random-noise L2 ratio was 0.752 compared with 0.750 for CK4. Full-position and property-channel representations were stronger distance-amplification probes. CK4P-MSP's positive result was different: it retained high grouped delta-readout at compact dimensionality, with local-versus-noise macro-F1 of 0.979. The seven-group ablation assigned most of this local-readout increment to MSP, while P contributed primarily to global stability and K to nearest-clean retrieval.

[Insert Figure 6 here: local-change readout and distance-ratio boundary.]

[Insert FloatBarrier here.]

This result supports a division of labour. Paired cosine and L2 drift quantify nuisance stability, distance ratios identify upper-bound local-change probes, and grouped delta-readout asks whether structured local changes remain accessible without template leakage. CK4P-MSP should therefore not be described as a distance-amplifying mutation detector. Its value in this analysis is that it remains stable relative to CK4/CK5 while preserving decomposable information for local-change readout at much lower dimensionality than full-position matrices.

[Insert Table 4 here: seven-group block-ablation metrics.]

[Insert Supplementary Figure S4 here or cite it: mutation-fraction sweep.]

### Boundary analyses constrain the interpretation

The boundary probes were included to prevent overextension of the representation claim. Spaced-seed transfer was useful as a mechanism comparator, but matching-oriented seed priors did not automatically become a universal dense-feature advantage. Context visibility depended on whether the relevant relation was present within the read. ARG/SNP interpretation required identity, annotation and allele-level evidence beyond what compact property summaries can provide.

These negative and boundary results are part of the manuscript's logic. They keep the claim focused on representation diagnostics and representation-level perturbation auditing, rather than allowing the compact feature space to be misread as a full biological interpretation system.

[Insert Table 5 here: boundary and mechanism summary.]

## Figure and Table Placement Summary

Main figures: Figure 1 after Study design; Table 1 after Representation families; Table 2 after Data layers; Figure 2 after the P/MSP contribution section; Figure 3, Supplementary Figure S1 and Supplementary Figure S7 after the compact stability and high-k audit section; Table 3 after the CK4P-MSP trade-off section; Figure 4 after External probes; Figure 5 after Full-position upper bound; Figure 6, Table 4 and Supplementary Figure S4 after Local mutation; Table 5 after Boundary analyses.

Supplementary figures generated for the paper folder: Supplementary Figure S1 baseline audit; Supplementary Figure S2 KSG-style empirical separability audit; Supplementary Figure S3 error-aware ART audit; Supplementary Figure S4 mutation-fraction sweep; Supplementary Figure S6 MSP binset and gamma-sensitivity audit; Supplementary Figure S7 dimension-matched high-k vector and native MinHash audit; Supplementary Figure S8 P/MSP relation and runtime audit; and Supplementary Figure S10 CAMI II marine anonymous-read stability probe. These figures are intentionally kept separate from the main visual line so that each main figure answers one central manuscript question.
