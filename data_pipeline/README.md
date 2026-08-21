# Data Pipeline Entrypoints

This folder groups data-facing workflows.

| Subfolder | Purpose |
|---|---|
| `download/` | Public dataset inspection and download helpers. |
| `preprocess/` | Read construction, subset preparation and metadata preprocessing. |
| `simulate/` | ART and CAMI-derived simulation or perturbation probes. |

The 35-species workflow is split between
`simulate/prepare_camisim_35species_inputs.py` (CAMISIM panel manifests),
`download/download_35_species_references.py` (NCBI reference download plan),
`simulate/prepare_35_species_manifest.py` (large-input provenance),
`preprocess/build_35_species_splits.py` (group-aware split construction) and
`preprocess/align_35_species_labels.py` (read-ID-checked FASTQ/mapping label
alignment) and
`preprocess/select_35_species_subset.py` (deterministic per-species and total
read caps) and
`preprocess/build_35_species_representations.py` (bounded-batch FASTQ to
representation matrices) and
the fixed-capacity readout in
`experiments/main/run_e5_multispecies_probe.py`. Large server inputs are never
silently copied into the repository.

The implementation modules remain in `scripts/` for compatibility. Files here
are runnable entrypoint wrappers.
