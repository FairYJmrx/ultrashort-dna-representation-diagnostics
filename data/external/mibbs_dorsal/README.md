# Public Motif-Position Probe Data

This directory contains the small public sequence release used by the
external motif-position probe.

Source:

- Clifford, J. and Adami, C. (2016). Data from: Discovery and
  information-theoretic characterization of transcription factor binding
  sites that act cooperatively. Dryad dataset DOI:
  `10.5061/dryad.8b203`.
- Public source mirror used for reproducible retrieval:
  `https://github.com/jacobclifford/MIBBS/blob/master/sequenceData.tar.gz`

The extracted files contain known Dorsal binding-site sequences and CRM
sequences from Drosophila. The audit identifies exact known-site occurrences
within the corresponding CRM sequence, extracts 50, 75, 100 and 150 bp
windows, and labels the relative position of the known site as left, middle or
right. Windows are grouped by CRM identifier during cross-validation.

This is an external position-readability probe, not a TFBS discovery or
binding-affinity benchmark. It does not establish clinical, species-level or
long-range regulatory performance.
