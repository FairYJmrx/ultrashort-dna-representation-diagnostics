# CAMI II marine lightweight probe inputs

This folder contains only the lightweight input cache used for the CAMI II marine
anonymous-read stability probe. The complete CAMI II archives are public
resources and are not vendored here in full.

Public source URLs:

- Reads archive: `https://frl.publisso.de/data/frl:6425521/marine/short_read/marmgCAMI2_sample_0_reads.tar.gz`
- Setup archive: `https://frl.publisso.de/data/frl:6425521/marine/short_read/marmgCAMI2_setup.tar.gz`

Local cached files:

- `marmgCAMI2_sample_0_reads.head8mb.tar.gz.part`: streamed prefix used to
  parse 4,000 anonymous reads from the embedded `anonymous_reads.fq.gz` member.
- `marmgCAMI2_setup.head64mb.tar.gz.part`: streamed prefix used to inspect the
  setup metadata and taxonomic profiles.
- `setup_head_extract/`: files extracted from the setup prefix for provenance
  inspection.

Boundary:

The FASTQ read headers in this lightweight analysis are anonymous and do not
directly provide read-level taxonomic labels. The separate CAMI II truth bundles
were not reconstructed for this run. The associated results should therefore be
interpreted as paired perturbation-stability outputs, not as CAMI II taxonomic
validation.
