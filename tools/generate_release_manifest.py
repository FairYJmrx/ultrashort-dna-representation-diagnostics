"""Generate the release inventory from tracked and pending tracked files."""

from __future__ import annotations

import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def files_for_release() -> list[str]:
    command = ["git", "ls-files", "--cached", "--others", "--exclude-standard"]
    output = subprocess.check_output(command, cwd=ROOT, text=True, encoding="utf-8")
    return sorted(line.strip().replace("\\", "/") for line in output.splitlines() if line.strip())


def main() -> None:
    files = [item for item in files_for_release() if item != "RELEASE_MANIFEST.md"]
    lines = [
        "# Release Manifest",
        "",
        "This manifest is generated from the release worktree by",
        "`python tools/generate_release_manifest.py`.",
        "",
        f"Tracked release files: **{len(files)}**",
        "",
        "## Source-of-truth directories",
        "",
        "- `methods/`: canonical representation implementations.",
        "- `data_pipeline/`: download, preprocessing and simulation entrypoints.",
        "- `experiments/`: main experiments and bounded audits.",
        "- `analysis/`: figure, table and provenance generation.",
        "- `results/stage3/contract_v2/`: manuscript-facing frozen results.",
        "- `paper_latex/`: canonical manuscript and supplementary sources.",
        "",
        "Historical Word/Markdown drafts, local environments, raw download caches",
        "and ART FASTQ/SAM intermediates are excluded.",
        "",
        "## Files",
        "",
        *[f"- `{item}`" for item in files],
        "",
    ]
    (ROOT / "RELEASE_MANIFEST.md").write_text("\n".join(lines), encoding="utf-8", newline="\n")
    print(f"ok: wrote {len(files)} release entries")


if __name__ == "__main__":
    main()
