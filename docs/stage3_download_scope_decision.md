# Stage 3 External Data Download Scope Decision

Date: 2026-06-22

This note defines the download boundary for the ART Illumina and CAMI low-complexity validation stage. The purpose is not to build a large end-to-end metagenomic classifier, but to complete a controlled external validation layer for representation-level information-preservation diagnostics.

## 1. Current Local Status

- Local WGS-derived reference panel is already available under `data/reference_genomes/close_relative/`.
- The MinHash/EIIP compact-baseline experiment has already been completed locally.
- `art_illumina` is not currently available in PATH or in the project environment.
- CAMI FASTQ/gold-standard files are not currently present in the project.
- Conda is available through `D:\anaconda\_conda.exe`, but is not exposed in the default PowerShell PATH.

## 2. Do We Need Full CAMI Data?

No. Full CAMI datasets are not necessary for this manuscript stage.

This manuscript asks whether DNA representations preserve information under short-read perturbation, not whether a new pipeline outperforms CAMI leaderboard tools. Therefore, downloading a complete CAMI benchmark would add storage and processing burden without directly improving the central claim. A controlled subset is scientifically cleaner because it preserves external benchmark provenance while keeping the experiment aligned with the paper's representation-level question.

## 3. Recommended Download Boundary

### Recommended CAMI Plan

Use a small CAMI low-complexity or toy-low subset rather than a full benchmark release.

Target:

- one low-complexity or toy-low short-read sample if available;
- the matching read-level or mapping-based gold-standard labels;
- no assembly files, no binning submissions, no full benchmark output bundles.

Local experimental subset after download:

- sample only 20,000-50,000 reads for feature extraction;
- run 69, 75, 100, 125 and 150 bp truncation;
- use clean plus light perturbations only: `clean`, `N_3pct`, `substitution_1pct`;
- run lightweight readout probes: nearest centroid and logistic regression first; MLP only if runtime remains acceptable.

Expected local retained data:

- raw compressed CAMI download: target under 1-5 GB if a toy/low single-sample file is available;
- normalized project CSV after subsampling: usually under 100-300 MB;
- feature/readout result files: usually under 100 MB.

If only large CAMI III toy human gut files are available, do not download all short-read samples. The CAMI page currently announces a CAMI III toy human gut benchmark, but full short-read releases can be much larger than this subproject needs. In that case, select one sample only, or defer full CAMI to server-side validation.

### Recommended ART Plan

ART does not require downloading new genomes, because the 21 WGS reference genomes are already local. We only need the ART Illumina simulator executable.

Target ART run:

- use existing 21 WGS reference genomes;
- generate only low-coverage/lightweight reads;
- read lengths: 69, 75, 100, 125 and 150 bp;
- use one Illumina profile supported by the installed ART build, preferably HiSeq-style if NovaSeq-style is unavailable;
- keep per-genome/per-length output small enough for local analysis.

Expected ART generated data:

- if using about 100-300 reads per genome per length, final normalized CSV should be below a few hundred MB;
- raw FASTQ should likely stay under 1 GB for the planned lightweight run.

## 4. Should CAMI Data Be Split Into Separate Experiments?

Yes, but only after normalization. We should not run one large mixed experiment first, because different CAMI labels answer different questions.

Recommended split:

1. `CAMI target/background probe`
   - Question: can the representation support coarse target-vs-background readability?
   - Expected conclusion: hybrid or k-mer may be stronger for identity; CSP may help under noisy/short conditions if degradation is slower.

2. `CAMI genus/species probe`
   - Question: is the representation readable for external taxonomic labels?
   - Expected conclusion: canonical k-mer/hybrid should remain strong for identity; CSP alone should not be overclaimed.

3. `CAMI noise-degradation probe`
   - Question: after truncation and perturbation, which representation loses readout signal more slowly?
   - Expected conclusion: this is the best place to test whether CSP offers auxiliary robustness beyond exact k-mer evidence.

## 5. What Each Stage-3 Experiment Can Conclude

| Experiment | Download needed | Main comparison | Valid conclusion |
|---|---:|---|---|
| MinHash/EIIP compact baseline | no | CSP vs MinHash vs EIIP vs k-mer/hybrid | CSP is not merely low-dimensional sketching or arbitrary biochemical numeric encoding |
| ART Illumina validation | ART tool only | artificial perturbation vs Illumina-like sequencing profile | stability results are not limited to hand-designed substitution/N/trim perturbations |
| CAMI low-complexity probe | small CAMI sample plus gold standard | local WGS panel vs external metagenomic benchmark | representation trends transfer to an external benchmark probe, without claiming clinical endpoint performance |

## 6. Decision Needed Before Download

Recommended next action:

1. Install or locate ART Illumina first, because ART uses our existing local WGS genomes and should have the smallest data burden.
2. For CAMI, download only a toy-low or low-complexity single-sample subset plus gold-standard labels.
3. Avoid full CAMI benchmark downloads unless a later server-side stage explicitly targets large-scale external generalization.

The confirmation needed from the user is only for external download/install actions, not for local parsing, analysis, or script execution.
