# Experiment Entrypoints

This folder groups reproducible experiment entrypoints.

| Subfolder | Purpose |
|---|---|
| `main/` | Main manuscript experiments and boundary probes. |
| `audits/` | Reviewer-response and method-hardening audits. |

Each entrypoint wraps a corresponding module in `scripts/`, which is retained
as an import-compatible implementation layer.

