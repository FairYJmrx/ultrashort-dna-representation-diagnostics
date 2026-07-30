# Figure, Experiment and Method-Value Audit

Working date: 2026-07-16

This note records the current evidence base, figure role, interpretation boundary and next experimental priorities for the CK4P-MSP manuscript. It is meant to prevent the figure set from becoming only defensive. The central question is whether the manuscript visually proves a positive method value: compact, interpretable, property-aware representation diagnostics for ultra-short reads.

## 1. Current method value statement

CK4P-MSP should not be framed as a production taxonomic classifier or as a replacement for exact matching, transformer embeddings or database-backed pipelines. Its defensible value is:

> CK4P-MSP provides a compact, block-decomposable representation that combines reverse-complement canonical 4-mer identity with global biochemical summaries and multi-scale positional property pooling. It improves perturbation stability relative to identity-only compact k-mer baselines, retains low-dimensional readable signal, and exposes interpretable biochemical/positional channels that can be audited before or alongside downstream models.

The most plausible future application is a candidate-aware secondary stage: a high-capacity first-stage model or database method narrows the candidate space, and CK4P-MSP/CSP-style interpretable channels then provide a lightweight secondary audit or readout. This should remain Future Work unless a pipeline-facing experiment is added.

## 2. Meaning of "not enough labels" in CAMI_TOY

The CAMI_TOY CK4P-MSP fine-label probe contains rows marked `not enough labels`. This does not mean CK4P-MSP performed poorly. It means that, after the subset and task filters were applied, the fine-grained label-probe split did not contain enough valid labels/classes/samples for the script to run the classifier and report macro-F1. Therefore:

- It is invalid to plot this as a low CK4P-MSP fine-label score.
- It is invalid to claim fine-label CAMI validation from that subset.
- It is valid to use CAMI_TOY for the coarse target/background probe where metrics were computed.
- It is valid to use CAMI II marine as an anonymous-read stability probe, not as a taxonomic readout probe.

## 3. Main experiments and what they prove

| Experiment block | Main result | What it proves | What it does not prove | Figure status |
|---|---|---|---|---|
| Compact main-method trade-off | CK4P-MSP: paired cosine 0.991, L2 drift 0.116, readout macro-F1 0.401, 222 features; CK4: 0.935 / 0.316 / 0.378 / 136; CK5: 0.882 / 0.433 / 0.373 / 512. | CK4P-MSP improves compact stability and modest readout under a low-dimensional feature budget. | It is not a strong standalone species classifier. | Should be central main evidence. |
| ART CK4P external stability | CK4P-MSP: mean paired cosine 0.991, L2 0.127; CK4: 0.907 / 0.400; CK5: 0.838 / 0.534; CSP: 0.989 / 0.137. | The compact stability pattern persists under simulator-derived sequencing errors. | It does not prove clinical classification benefit. | Should replace the old Figure 4 ART panel. |
| CAMI_TOY coarse readout | CK4P-MSP mean macro-F1 0.715; CK5 0.772; at 100 bp both reach 0.944; at 69 bp CK4P-MSP is lower (0.486). | Coarse target/background information remains readable, with task and length dependence. | It does not prove fine-grained taxonomic classification. | Can be used, but must be described as coarse readability. |
| CAMI_TOY fine-label probe | Fine-label CK4P-MSP rows report `not enough labels`. | The selected subset is not suitable for this fine-label CK4P-MSP probe. | It must not be plotted as a CK4P-MSP failure or success. | Remove from main CK4P-MSP comparison. |
| CAMI II marine anonymous-read stability | CK4P-MSP combined perturbation paired cosine 0.993, L2 0.117; CK4 0.944 / 0.323; CK5 0.902 / 0.431; CSP 0.992 / 0.124. | CK4P-MSP stability extends to a more complex external sequence source. | No read-level taxonomic labels; not a classification validation. | Good supplementary or Figure 4C stability panel. |
| Full-position upper bound | Full-position/property matrices outperform CK4P-MSP on positional readout but require much higher dimensionality. | Position information has value; CK4P-MSP is a compact approximation, not an upper bound. | CK4P-MSP is not the strongest possible positional representation. | Keep as boundary/upper-bound main figure. |
| Local mutation sensitivity | CK4P-MSP sensitivity ratio 0.754, close to CK4 0.750; P-channels 1.255; position k-mer property 1.125. CK4P-MSP delta-readout macro-F1 0.977. | CK4P-MSP preserves readable local-change signal at compact dimension. | CK4P-MSP is not a distance-ratio local-sensitivity winner. | Figure 6 must emphasize delta-readout, not ratio as a win. |
| P/MSP relation and redundancy audits | P and MSP are correlated but not identical; MSP adds coarse position-linked property summaries. | Supports "related but not equivalent channels." | Does not establish strict orthogonality. | Supplementary support. |
| MI / kNN MI audits | Positive but estimator-dependent signal audit. | Supports empirical additional signal beyond CK4 under tested estimators. | Not a universal information-theoretic theorem. | Supplementary support; wording must stay empirical. |
| High-k compressed / PCA/SVD baselines | CK4P-MSP remains competitive under dimension-matched controls. | Counters dimension-expansion and trivial compression critiques. | Does not make CK4P-MSP globally superior to all learned embeddings. | Supplementary support. |

## 4. Current figure problems

### Figure 2

Current status: revised to center the method mechanism rather than a broad method pile-up.

Figure contract:

- Figure 2A: all seven non-empty K/P/MSP combinations show the global-drift boundary; property-only summaries are smoothest, while CK4P-MSP reduces drift relative to CK4 and retains K.
- Figure 2B: the same seven groups show that MSP-containing variants retain the strongest grouped local-change readout.
- Figure 2C: K-containing variants preserve nearest-clean composition-linked retrieval, whereas property-only variants lose that axis.
- Message: K, P and MSP contribute along different audit axes; the complete representation is a compact attributable trade-off, not a single-metric winner.

### Figure 4

Current status: revised to include CK4P-MSP directly and to separate stability from coarse readout.

Figure contract:

- Figure 4A: ART within-length drift ratios compare CK4, CK4+P, CK4+MSP, CK4P-MSP and CK5; this is simulator stability, not a monotonic length law.
- Figure 4B: six source-grouped CAMI_TOY target tasks show shifted fixed-head macro-F1. Target points share one source pool and are descriptive task blocks.
- Figure 4C: the same task definitions show retention relative to each method's own 100-bp clean baseline.
- CAMI II marine anonymous-read stability remains in Supplementary Figure S10 because it has no reconstructed read-level taxonomic labels in this lightweight probe.

### Figure 6

Current status: revised so the visual lead is local-change readability.

Figure contract:

- Figure 6A: CK4, CK4+P, CK4+MSP and CK4P-MSP show that MSP carries the local-change readout gain.
- Figure 6B: the distance-ratio panel is retained as a boundary, showing that full-position/property channels are stronger distance-amplification probes.
- Message: CK4P-MSP preserves local-change readability at compact dimension, but it should not be described as a distance-sensitivity upper bound.

## 5. Experiment gaps after the current evidence audit

### Gap A: Candidate-aware secondary-stage value

This is the best way to support the user's proposed future value: a high-cost first-stage model or database method does coarse identification, then CK4P-MSP/CSP-like compact interpretable features serve as secondary audit/readout channels.

Current status: not proven.

Recommended optional experiment:

- Construct a candidate-aware task where labels are restricted to a small candidate set, such as target/background or within-candidate groups.
- Compare CK4, CK4+P, CK4P-MSP, CSP and CK5 under the same shallow secondary readout.
- Report feature dimension, macro-F1/AUPRC and perturbation stability.
- Do not claim clinical triage or false-positive reduction unless a real downstream classifier is connected.

### Gap B: External CK4P-MSP fine-label readout

The current CAMI_TOY audit is a valid six-task coarse target-versus-background probe, but it is not a fine-label taxonomic benchmark.

Possible experiment if needed:

- Build a larger CAMI/CAMI II labeled subset with enough labels and enough samples per label.
- Then run CK4P-MSP, CK4, CK5, CSP and perhaps a high-k compressed baseline.
- This is more expensive and may still show that exact k-mer or transformer features outperform compact interpretable summaries. It should be optional unless the manuscript insists on fine-label external validation.

### Gap C: Learned embedding comparison

Current manuscript should not start a transformer comparison unless we are ready to make it a resource-bounded representation experiment.

Possible future experiment:

- Compare CK4P-MSP to a frozen embedding or PCA-compressed learned embedding under the same feature budget and same perturbation audits.
- This is not required for the current representation-diagnostic claim, but it would strengthen a higher-impact submission.

## 6. Writing constraints to preserve

- Do not claim CK4P-MSP is the strongest species classifier.
- Do not claim CK4P-MSP is a universal mathematical optimum.
- Do not claim CAMI_TOY fine-label validation where the result is `not enough labels`.
- Do not claim that Figure 6A proves CK4P-MSP local distance sensitivity.
- It is acceptable to say CK4P-MSP is a compact, interpretable, block-decomposable secondary representation/audit candidate.
- The two-stage transformer/database-first scenario belongs in Future Work unless a specific experiment is added.

## 7. Figure action status (2026-07-30)

1. [x] Figure 2 rebuilt as the seven-group K/P/MSP contribution audit.
2. [x] Figure 4 rebuilt to separate ART simulator stability, CAMI shifted readout and relative retention.
3. [x] Figure 6 rebuilt with grouped local-change readability as the lead panel and raw distance ratio as a boundary.
4. [x] Captions and adjacent Results text aligned with the current figure contracts.
5. [x] Main and Supplementary PDFs recompiled and visually inspected for overlap, clipping, internal whitespace and float placement.
6. [ ] Sync the final manuscript assets and source files to the release branch after the current language-polish pass.
