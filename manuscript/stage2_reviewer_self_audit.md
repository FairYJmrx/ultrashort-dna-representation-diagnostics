# Stage-2 Reviewer-Style Self-Audit

## Review setup

- Input scope: `stage2_manuscript_v2.md`, stage-2 result tables/figures, and rendered PDF QA.
- Assessment boundary: local controlled representation diagnostics, not clinical mNGS validation.
- Shared manuscript claim: canonical k-mers provide high-resolution identity evidence, whereas CSP provides compact perturbation-stable auxiliary evidence for ultra-short mNGS-like reads.
- Evidence base: WGS-slice perturbation grid, 69/75 bp hospital-like stability audit, CSP component ablation, k/pattern sensitivity, lightweight readout probes, attention-context breakpoint diagnostic, and synthetic ARG/SNP boundary probes.

## Reviewer 1: Technical Soundness

### Overall assessment

The revised manuscript is technically more coherent than V1 because it no longer claims that CSP replaces canonical k-mers. The central stability claim is supported by the stage-2 grid: CSP was best in 42/42 length-by-perturbation settings by paired clean-perturbed cosine, and the 69/75 bp results directly address the intended hospital-like short-read scenario.

### Major strengths

- The claim is now decomposed into stability, compactness, identity readout and context visibility rather than collapsed into accuracy.
- CSP is explicitly defined mathematically and biologically.
- The ablation separates spaced seed counts from biochemical property summaries.
- The limitations clearly state that CSP-alone species ID, ARG allele calling and resistance SNP interpretation are not established.

### Major concerns

- The readout tasks remain lightweight and local. They support model-accessibility of features, not clinical accuracy.
- The ARG/SNP tasks are synthetic and in some settings too easy, so they mostly bound claims rather than prove future ARG performance.
- No industry-pipeline comparison against Kraken2/Centrifuge/Kaiju has been completed.
- No real FASTQ quality profile or host/background mixture is included.

### Required before stronger submission

- Server-scale genome-held-out WGS panel with more strains per genus.
- Independent pipeline audit using the same noisy FASTQ input for Kraken2/Centrifuge/Kaiju and the proposed representation readout.
- Real ARG-marker task based on CARD/ResFinder/AMRFinderPlus or similar databases.

## Reviewer 2: Originality and Significance

### Overall assessment

The originality is credible if framed as representation diagnostics and controlled evidence layering. CSP itself is not a revolutionary standalone classifier; its novelty lies in a compact deterministic fusion of canonical spaced evidence with interpretable biochemical summaries, and in the claim that short-read pipelines should separate identity evidence from perturbation-stable auxiliary evidence.

### Major strengths

- The paper avoids a naive "higher accuracy" story.
- The attention-context diagnostic gives a useful conceptual bridge between DNA reads and sequence-model context loss.
- The paper identifies an advantage region rather than overgeneralizing.

### Major concerns

- The novelty could look incremental unless the introduction emphasizes the diagnostic framework and advantage-region mapping.
- Some cited DNA foundation models are large and not directly evaluated. The manuscript correctly places them in motivation, but should avoid implying direct comparison.
- The title should remain diagnostic/framework-oriented rather than claiming a new clinical method.

### Positioning

Best fit is a bioinformatics methods/application-note style venue if server-scale validation is not added. With the present local evidence, BMC Bioinformatics, Frontiers in Bioinformatics, or a preprint-first strategy is safer than claiming readiness for a top-tier methods journal. With the added server experiments, Bioinformatics or NAR Genomics and Bioinformatics becomes more plausible.

## Reviewer 3: Readability and Breadth

### Overall assessment

The manuscript now reads as a bounded methods paper. The abstract states the main result and boundary clearly. The terminology section helps non-specialist readers understand what CSP is and is not.

### Major strengths

- The paper distinguishes perturbation stability from contamination/mixed-species robustness.
- The results are organized as problem -> experiment -> conclusion -> boundary.
- The conclusion is modest and memorable: layer exact identity evidence with auxiliary stability evidence.

### Major concerns

- Some main-body tables are still dense in the Markdown version. PDF intentionally omits the widest tables from the body and points to table files.
- The manuscript could benefit from a final graphical overview figure showing the layered evidence model: canonical k-mer identity block + CSP stability block + downstream readout.
- DOCX visual QA could not be completed because LibreOffice is broken locally; PDF rendering was verified instead.

## Cross-review synthesis

### Consensus strengths

- Clearer claim boundary than V1.
- Stronger stage-2 evidence chain for CSP's true advantage region.
- Proper downgrading of clinical, Transformer and ARG claims to future work.
- Real references now support the literature review.

### Consensus risks

- The paper is not yet a clinical mNGS classifier paper.
- The dataset is still local and intentionally small.
- ARG/SNP evidence is synthetic and should not be overclaimed.
- The strongest next evidence would be external WGS/FASTQ and standard pipeline comparison.

### Most important next steps

1. Run a server-scale close-relative WGS panel with genome-held-out splits.
2. Add same-FASTQ Kraken2/Centrifuge/Kaiju sanity comparisons.
3. Build a real ARG marker task from curated databases.
4. Add a compact schematic figure of the representation layering logic.
5. Convert wide tables to supplementary tables for journal submission.

## Unsupported claims to avoid

- CSP is better than canonical k-mer for all species identification.
- CSP can independently call ARG alleles or resistance SNPs.
- CSP has been proven to improve Transformer models.
- Local readout accuracy estimates clinical diagnostic accuracy.
- The current dataset is representative of all mNGS scenarios.
