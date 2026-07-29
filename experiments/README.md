# Experiment Entrypoints

This folder groups reproducible experiment entrypoints.

| Subfolder | Purpose |
|---|---|
| `main/` | Main manuscript experiments and boundary probes. |
| `audits/` | Reviewer-response and method-hardening audits. |

Each entrypoint wraps a corresponding module in `scripts/`, which is retained
as an import-compatible implementation layer.

The dense lower-bound read-length audit is
`audits/run_short_read_length_continuity_audit.py`. It evaluates every integer
length from 50 to 75 bp on shared templates; 100, 125 and 150 bp remain broader
anchors in the main and ART grids rather than a second dense sweep.
