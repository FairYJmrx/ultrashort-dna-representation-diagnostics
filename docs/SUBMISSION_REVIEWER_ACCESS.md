# Submission Reviewer Access Plan

This repository is currently maintained as a private GitHub repository for
pre-submission and peer-review use.

Repository:

`https://github.com/FairYJmrx/ultrashort-dna-representation-diagnostics`

Current branch for the reproducible manuscript package:

`release`

## Access model for NAR Genomics and Bioinformatics submission

For initial submission, editors and reviewers should be given access through
one of the following routes:

1. Add the handling editor or journal-provided reviewer account as a read-only
   collaborator to the private GitHub repository.
2. Provide a read-only private access route in the confidential submission
   field, if the submission system requests a token, username/password or
   equivalent reviewer credential.
3. If the editorial office does not accept private GitHub access, create an
   embargoed Zenodo/Figshare/OSF record or a public GitHub release before
   review begins.

The public archival DOI has not yet been minted. It should be created from the
accepted or submission-frozen release when the authors decide to make the
repository public.

## Files intentionally excluded

The repository does not include restricted clinical sequencing reads,
patient-level labels, patient identifiers, local environments, full CAMI
archives, ART FASTQ/SAM intermediates or historical scratch outputs. The
manuscript uses representative read-length conditions, public benchmark
resources and generated result tables.

## Submission checklist

- Confirm that the repository remains private until the authors choose public
  release.
- Confirm reviewer access route before submission.
- Replace placeholder author names in `CITATION.cff`.
- Replace the placeholder repository DOI in the manuscript after Zenodo or
  another archive has been minted.
- Keep the `release` branch frozen during active review unless a revision
  release is explicitly created.
