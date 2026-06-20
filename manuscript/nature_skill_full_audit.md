# Nature-skill full manuscript audit

Date: 2026-06-20

## Scope

This audit applies the installed `nature-writing`, `nature-reviewer`, `nature-citation`, and `nature-polishing` rules to the current manuscript `final_manuscript.md`. The detected paper type is a methods / representation-diagnostics paper. The target posture is closer to a cautious Nature Communications-style methods article than to a clinical validation article.

## One-sentence argument

In ultra-short mNGS-like short reads, this study shows that DNA representations preserve different forms of information, and that canonical spaced-property encoding is a compact auxiliary representation with a specific robustness advantage under perturbation, supported by controlled intrinsic metrics, ablation, read-length/context diagnostics, parameter sensitivity and lightweight close-relative WGS-slice probes, with no claim of clinical species or AMR diagnostic validity.

## Reviewer-style assessment

### Reviewer 1: technical soundness emphasis

Overall assessment: The work has a defensible technical direction because it treats DNA representation as an information-preservation problem instead of as a single accuracy leaderboard. The strongest evidence is the perturbation-stability ablation showing that adding property summaries to canonical spaced seeds improves clean-versus-perturbed similarity under N masking.

Major strengths: The manuscript now separates primary representation metrics from tertiary readout metrics; includes component ablation; tests 69, 75, 100, 125, 150 and PE150-proxy lengths; and avoids claiming that the new feature replaces canonical k-mers.

Major concerns: The current evidence remains lightweight. There are no confidence intervals or bootstrap uncertainty intervals for the main delta values. The close-relative panel has only 21 genomes and is not representative. The PE150 condition is a simplified information proxy, not a realistic paired-end simulator. No real FASTQ quality profiles, host mixture or ARG read task are included.

Technical failings to address before a stronger case: add uncertainty estimates for the main perturbation deltas; state the number of paired reads and sampling limits next to the headline effect; explicitly define every proposed representation in Methods; and report component interactions as ablations, not just method-vs-method comparisons.

### Reviewer 2: originality and significance emphasis

Overall assessment: The central idea is not that property-aware summaries are universally superior, but that a compact auxiliary representation exposes a different advantage region. This is a valid contribution if framed as representation diagnostics and not as a clinical classifier.

Major strengths: The paper identifies a useful conceptual gap between exact k-mer identity, strand invariance, perturbation robustness, biochemical summaries and attention-visible context. The attention/context diagnostic is an interesting explanatory experiment because it shows that read shortening can remove a semantic relation entirely.

Major concerns: The Related Work still needs stronger topic synthesis. It should group prior research into alignment-free k-mer/spaced-seed methods, numerical DNA signal representations, deep DNA sequence models, and AMR/ARG evidence systems. The distinction from prior DNA signal processing and learned DNA embeddings must be explicit: the new method is a deterministic, low-dimensional auxiliary representation, not a new language model.

Technical failings to address before a stronger case: add the historical DNA representation thread (chaos-game representation, EIIP/numerical mappings, DeepBind/DeepSEA/DanQ, dna2vec) and explain which prior limitations are relevant to ultra-short reads.

### Reviewer 3: readability and broad-readership emphasis

Overall assessment: The manuscript is much clearer after reframing accuracy as a readout probe, but it still reads like a compressed project report in places. The reader needs a simpler first-page route: what problem, what representation is proposed, what evidence supports it, and where it fails.

Major strengths: The current claim boundary is honest. The text explicitly says that the method does not replace canonical k-mers and does not validate AMR calling.

Major concerns: The title remains somewhat generic. The Results subsections should open with the tested question, not only the result. Methods should appear before Results in a methods-style manuscript, or Results must be self-contained enough for readers to understand how numbers were obtained. Some tables are dense and should be moved to supplement in a journal submission.

Technical failings to address before a stronger case: use a title that names the main contribution and setting; add a short contribution paragraph in the Introduction; enforce claim-evidence-boundary at the end of each Results subsection; and keep the conclusion from promising future mNGS/AMR value beyond the actual evidence.

## Cross-review synthesis

Consensus strengths:

- The corrected manuscript posture is scientifically safer than an accuracy-centered framing.
- The strongest supported advantage of `cspaced_property_l2` is compact perturbation stability under N masking and, secondarily, a useful auxiliary feature role.
- Canonical k-mers and canonical spaced seeds remain strong close-relative baselines and should be treated as such.
- The attention/context diagnostic is a useful conceptual experiment, provided it is not overgeneralized to Transformer performance.

Consensus risks:

- The evidence base is still local and lightweight.
- The current manuscript should not claim clinical mNGS, representative taxonomy or AMR/ARG diagnostic performance.
- Uncertainty reporting is thin.
- The Related Work must better cover DNA information representation as a field, not only mNGS classifiers and large models.
- DOCX render QA remains blocked by a local LibreOffice installation problem.

## Required manuscript revisions

1. Expand Related Work into mechanism-grouped synthesis: alignment-free k-mers and spaced seeds; numerical/genomic signal representations; deep and foundation DNA models; AMR/ARG evidence systems.
2. Add a contribution paragraph to the Introduction with three bounded contributions.
3. Strengthen Problem Formulation and Methods by defining `cspaced_property_l2` mathematically enough to re-implement.
4. Add an explicit evidence-policy sentence: primary metrics are intrinsic representation diagnostics; classification is only a readout probe.
5. Add sample-size and sampling-limit language beside the main perturbation effects.
6. Add a caveat that the current uncertainty is descriptive unless bootstrap/server-scale repeats are added.
7. Add a supplementary/server plan for bootstrap CIs, realistic FASTQ, expanded close-relative panels, tiny CNN/Transformer and ARG marker tasks.

## Current publication readiness

As of this audit, the manuscript is not yet a polished Q2+ submission. It is closer to a credible project manuscript or methods-note draft. With the revisions above, it can become a defensible lightweight representation-diagnostics paper. A stronger Q2+ submission would still require at least one of the following:

- repeated-seed / bootstrap uncertainty for all main deltas;
- a larger close-relative panel;
- realistic FASTQ perturbation simulation;
- a small trainable model comparison using matched representation inputs;
- a controlled ARG marker task grounded in CARD/ResFinder/AMRFinderPlus evidence.

## LibreOffice status

The `D:\AI-NGS\_tools\LibreOfficeExtracted` directory is not a valid runnable LibreOffice installation. Its `program\bootstrap.ini` still contains an unresolved `<installmode>` placeholder, which explains the startup error and the headless `libpng error`. The manuscript file itself is not the source of this error.

