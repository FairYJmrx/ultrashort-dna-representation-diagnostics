"""Create a lightweight manifest for the server-side 35-species benchmark.

This script never copies FASTQ or token-cache files. It records their hashes,
label cardinality and the exact processing inputs so a large server run can be
audited from the small release repository.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path

import numpy as np


def sha256_file(path: Path, chunk_size: int = 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(chunk_size), b""):
            digest.update(chunk)
    return digest.hexdigest()


def file_record(path: Path) -> dict[str, object]:
    path = path.resolve()
    return {
        "path": str(path),
        "bytes": path.stat().st_size,
        "sha256": sha256_file(path),
    }


def load_labels(path: Path) -> np.ndarray:
    labels = np.load(path, mmap_mode="r")
    if labels.ndim != 1:
        raise ValueError(f"labels must be one-dimensional: {labels.shape}")
    return np.asarray(labels)


def count_fastq_records(path: Path) -> int:
    lines = 0
    with path.open("rb") as handle:
        for _ in handle:
            lines += 1
    if lines % 4:
        raise ValueError(f"FASTQ line count is not divisible by four: {lines}")
    return lines // 4


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fastq", type=Path, required=True)
    parser.add_argument("--labels", type=Path, required=True)
    parser.add_argument("--label-map", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--dataset-id", default="cami_sim_35sp_75bp")
    parser.add_argument("--split-indices", type=Path)
    args = parser.parse_args()

    for path in (args.fastq, args.labels, args.label_map):
        if not path.exists():
            raise FileNotFoundError(path)
    labels = load_labels(args.labels)
    fastq_reads = count_fastq_records(args.fastq)
    if fastq_reads != labels.size:
        raise ValueError(f"FASTQ/label row mismatch: {fastq_reads} vs {labels.size}")
    label_map = json.loads(args.label_map.read_text(encoding="utf-8"))
    if not isinstance(label_map, dict):
        raise ValueError("label map must be a JSON object")

    counts = Counter(int(value) for value in labels.tolist())
    expected_ids = set(range(len(label_map)))
    observed_ids = set(counts)
    if observed_ids != expected_ids:
        raise ValueError(
            f"label ids do not match label map: observed={sorted(observed_ids)} "
            f"expected={sorted(expected_ids)}"
        )

    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "label_map.json").write_text(
        json.dumps(label_map, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    summary = {
        "dataset_id": args.dataset_id,
        "n_reads": int(labels.size),
        "fastq_records": int(fastq_reads),
        "n_labels": len(observed_ids),
        "label_counts": {str(key): value for key, value in sorted(counts.items())},
        "inputs": {
            "fastq": file_record(args.fastq),
            "labels": file_record(args.labels),
            "label_map": file_record(args.label_map),
        },
        "split_indices": file_record(args.split_indices) if args.split_indices else None,
        "warning": "FASTQ and token caches remain external to the release repository.",
    }
    (output_dir / "dataset_manifest.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
