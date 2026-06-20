# Publication Evidence Synthesis

This synthesis enforces the revised manuscript position: the project compares DNA-read representations, not clinical species-identification accuracy.

## Main Claim Boundary

`cspaced_property_l2` should be described as a compact, strand-friendly, perturbation-stable auxiliary representation. It complements canonical k-mer baselines; it does not replace them.

## Property-Ablation Result

Adding DNA property summaries to canonical spaced seeds improved perturbation stability in the close-relative WGS-slice audit. The largest cosine gain was 0.028 under N_3pct at 75 bp; the largest L2 reduction was 0.154 under N_3pct at 75 bp.
This supports the auxiliary-robustness claim, not a universal taxonomy claim.

## Perturbation Stability

At 75 bp with 3% N masking, the strongest mean clean-perturbed cosine among the audited representations was canonical spaced + property (0.995). Across lengths, canonical spaced + property stayed close to the top stability region.
This is the clearest local advantage region for the proposed hybrid representation.

## Close-Relative Probe

In the clean within-genus species probe, the best averaged readout was canonical spaced at 125 bp (mean macro-F1 0.393).
In the clean target/background probe, the best averaged readout was canonical spaced + property at PE150 proxy (mean macro-F1 0.575).
These results must be framed as lightweight separability probes over 21 selected genomes, not as a representative clinical mNGS benchmark.

## Attention Context-Loss Diagnostic

The synthetic motif-pair diagnostic showed pair visibility near 0.002 below 150 bp and 1.000 at 150 bp/PE150. This supports the user's hypothesis that short reads can lose an entire contextual relation, not merely a proportional number of bases.
The local diagnostic does not prove Transformer superiority; it explains when attention-compatible encodings have enough observed context to be meaningful.

## Parameter Sensitivity

The k/pattern sensitivity audit prevents a single-parameter claim. Across N-masking stability winners, the family counts were {'canonical spaced + property': 6}. The downstream close-relative readout remained parameter-sensitive, so classification probes should not be used as a universal method ranking.
The best sampled classification probe was canonical spaced with pattern=0-1-3-6 for target_background at 75 bp (mean macro-F1 0.547), reinforcing that canonical k-mer and spaced variants remain strong baselines.

## Accuracy Policy

Accuracy and macro-F1 should appear as tertiary downstream probes. They help ask whether a representation exposes information to a simple readout, but they do not establish clinical performance or universal taxonomy superiority.

## Server-Scale Follow-Up

A larger server experiment should expand close-relative panels, add realistic FASTQ simulation, and compare tiny CNN/Transformer models under matched representation inputs. These are follow-up validation steps rather than prerequisites for reporting the current lightweight representation diagnostics.
