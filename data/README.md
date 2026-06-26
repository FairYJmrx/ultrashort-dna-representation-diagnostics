# Data Directory

This folder contains lightweight release data and public benchmark subsets used
by the reproducibility workflows.

Large raw archives, full CAMI downloads, ART intermediate FASTQ/SAM files,
local virtual environments and restricted clinical reads are intentionally not
included in the release.

| Subfolder | Purpose |
|---|---|
| `real_slices/` | WGS-derived slices and close-relative read tables used by the controlled grids. |
| `stage3/cami/` | CAMI_TOY_low labelled subsets used by external readout probes. |
| `toy_reads/` | Controlled toy and hardened read tables for implementation and boundary tasks. |

Generated or downloaded caches for optional reruns should stay under `data/`
and should not be committed unless they are lightweight release inputs.

