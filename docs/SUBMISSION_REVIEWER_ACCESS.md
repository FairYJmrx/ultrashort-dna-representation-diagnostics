# Submission Reviewer Access Plan

This repository is prepared for a public, versioned archival release.

Repository:

`https://github.com/FairYJmrx/ultrashort-dna-representation-diagnostics`

Release branch for the reproducible manuscript package:

`release`

## Access model for NAR Genomics and Bioinformatics submission

The versioned GitHub Release and Zenodo record are the reviewer-access route.
Until the DOI is minted, the manuscript retains an explicit repository-release
placeholder that must be replaced before submission.

## Files intentionally excluded

The repository does not include patient sequencing reads, patient-level labels,
patient identifiers, local environments, full CAMI
archives, ART FASTQ/SAM intermediates or historical scratch outputs. The
manuscript uses representative read-length conditions, public benchmark
resources and generated result tables.

## Submission checklist

- Run `python tools/release_preflight.py` from a clean checkout.
- Confirm reviewer access through the public GitHub Release and Zenodo record.
- Replace the placeholder repository DOI in the manuscript after Zenodo or
  another archive has been minted.
- Keep the `release` branch frozen during active review unless a revision
  release is explicitly created.
