# Submission Reviewer Access Plan

This repository is prepared for a public, versioned archival release.

Repository:

`https://github.com/FairYJmrx/ultrashort-dna-representation-diagnostics`

Release branch for the reproducible manuscript package:

`release`

## Access model for NAR Genomics and Bioinformatics submission

The versioned GitHub Release and Zenodo record are the reviewer-access route.
The submission snapshot will be GitHub Release `v1.2.1` after the final tag is
linked through the stable Zenodo concept DOI
`https://doi.org/10.5281/zenodo.21792340`; the current version DOI is
`https://doi.org/10.5281/zenodo.22055051`.

## Files intentionally excluded

The repository does not include patient sequencing reads, patient-level labels,
patient identifiers, local environments, full CAMI
archives, ART FASTQ/SAM intermediates or historical scratch outputs. The
manuscript uses representative read-length conditions, public benchmark
resources and generated result tables.

## Submission checklist

- Run `python tools/release_preflight.py` from a clean checkout.
- Confirm reviewer access through the public `v1.2.1` GitHub Release and its Zenodo record.
- Keep the `release` branch frozen during active review unless a revision
  release is explicitly created.
