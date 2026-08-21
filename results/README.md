# Results Directory

This folder contains generated tables, summaries, run manifests and audit
outputs used by the manuscript.

| Subfolder | Purpose |
|---|---|
| `stage2/` | Boundary and earlier representation-grid outputs retained for provenance. |
| `stage3/` | Main manuscript outputs and reviewer-response audit outputs. |
| `audits/` | Result inventory and final provenance checks. |

The main manuscript-to-output mapping is recorded in
`docs/manuscript_script_mapping.md` and `docs/final_release_provenance_map.md`.
## E5 regenerated 35-species batch

`e5_35species_regenerated_75bp/` records the result of a fresh, deterministic
75-bp batch assembled from the approved server workspace's per-species FASTQ
files. The batch contains 1,500,000 reads across 35 species, with the same
labels and rows reused for CK4, CK4+P, CK4+MSP and CK4P-MSP.

The large FASTQ and feature matrices are intentionally external to Git.
`provenance.json` records the server workspace, selection contract and SHA-256
hashes. `e5_metrics.csv` is the fixed MLP readout summary. In this probe,
CK4+P slightly exceeded CK4 on the held-out test set, whereas adding MSP
reduced the closed-set readout; this result is a boundary analysis and must
not be converted into a claim that CK4P-MSP is a better species classifier.
