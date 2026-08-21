# 35-species benchmark reproduction

The 35-species experiment is a fixed-capacity multiclass readout probe. It is
not a production taxonomic classifier and it is not a clinical validation.

## External large inputs

The current server benchmark uses the `code-V4` branch and the CAMISIM-derived
75-bp dataset. The large FASTQ and token caches stay outside Git and must be
recreated or accessed from the approved server storage. The release repository
stores only configuration, manifests, split rules and result summaries.

Before a run, record:

- simulator and reference-panel version;
- the 35-species label map;
- FASTQ, labels and split hashes;
- read length and filtering command;
- random seed and fixed readout architecture.

## CAMISIM input preparation

The 35-species panel is prepared from the public reference metadata workbook;
the release entrypoint writes `genome_to_id.tsv`, `metadata.tsv`, a sorted
species label map and a small panel CSV. It does not fetch or copy reference
genomes:

```text
python data_pipeline/simulate/prepare_camisim_35species_inputs.py \
  --panel-csv data/e5_35species/species_panel.csv \
  --output-dir results/e5_35species/camisim_input \
  --wgs-root /external/reference_genomes
```

An original metadata workbook can be used instead with `--panel-xlsx`.

The exact simulation contract is recorded in `configs/e5_35species.yaml`.
The observed fastp report is provenance for the existing server dataset; it is
not a replacement for rerunning CAMISIM when a fresh dataset is required.

Reference genomes can be planned or downloaded separately:

```text
python data_pipeline/download/download_35_species_references.py \
  --panel data/e5_35species/species_panel.csv \
  --output-root /external/reference_genomes \
  --manifest results/e5_35species/reference_download_manifest.csv
```

Add `--execute` only after installing and checking the NCBI `datasets` CLI.

## Manifest command

```text
python data_pipeline/simulate/prepare_35_species_manifest.py \
  --fastq /external/path/R1_qc.fastq \
  --labels /external/path/labels.npy \
  --label-map /external/path/label_map.json \
  --split-indices /external/path/split_indices.npz \
  --output-dir results/e5_35species/manifest
```

## Split command

Prefer a source/template group file. The grouped splitter assigns source groups
within each label, so all species are represented in each partition. The
independent-read override is allowed only when simulator documentation
guarantees independent generated reads:

```text
python data_pipeline/preprocess/build_35_species_splits.py \
  --labels /external/path/labels.npy \
  --groups /external/path/source_group_ids.npy \
  --output results/e5_35species/splits.npz
```

## Representation construction

After the FASTQ/label row alignment has been recorded, build matrices directly
from the FASTQ stream. The writer uses bounded batches and keeps the row order
identical to the input FASTQ:

```text
python data_pipeline/preprocess/build_35_species_representations.py \
  --fastq /external/path/R1_qc.fastq \
  --labels /external/path/labels.npy \
  --output-dir results/e5_35species/representations \
  --representation CK4 --representation CK5 --representation CK7 \
  --representation CK4P-MSP --batch-size 4096 --read-length 75
```

The script writes float32 NumPy matrices plus
`representation_build_manifest.json`. Historical PseKNC/PseEIIP controls can
be requested with `--representation PseKNC` and `--representation PseEIIP`;
they are kept as explicit boundary controls and use the same rows. By default,
the script requires exactly one FASTQ record per label and exactly the declared
read length; use `--max-reads` only for an explicitly recorded smoke subset.

## Reproducibility boundary

The versioned experiment contract is `configs/e5_35species.yaml`. It fixes the
dataset identifier, read length, class count, split policy and readout budget;
the generated manifest records the external input hashes used for a run.

## Read-ID alignment command

When a CAMISIM `reads_mapping.tsv` is available, align labels to the FASTQ by
the original read identifier before building representations. Do not pair a
label cache with a FASTQ solely because both have the same row count:

```text
python data_pipeline/preprocess/align_35_species_labels.py \
  --fastq /external/path/R1_qc.fastq \
  --mapping-tsv /external/path/reads_mapping.tsv \
  --panel-csv data/e5_35species/species_panel.csv \
  --label-map data/e5_35species/label_map.json \
  --output-labels results/e5_35species/labels.npy \
  --output-groups results/e5_35species/coordinate_bucket_groups.npy
```

The command fails if FASTQ and mapping order differ. Coordinate buckets are an
audit aid derived from read headers, not simulator-native source groups; they
must not be described as an unseen-genome split without further validation.

The 35-species FASTQ is a large external input and is not redistributed by the
release repository. A run is reproducible when the same public simulator
configuration, reference panel, label map, split policy and input hashes are
available. A server-only result must not be described as locally reproducible
without those artifacts.
