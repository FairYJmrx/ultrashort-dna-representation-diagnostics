"""Build a deterministic balanced FASTQ batch from per-species FASTQ files.

The input manifest is a tab-separated file with columns ``label``, ``species``
and ``fastq``. Each source file is counted, then a reproducible subset is
selected without requiring a read-level mapping file. The output FASTQ and
label arrays are written in the same order, so every representation can reuse
the exact batch.
"""

from __future__ import annotations

import argparse
import gzip
import json
import random
from pathlib import Path
from typing import TextIO

import numpy as np


def open_text(path: Path, mode: str) -> TextIO:
    if path.suffix == ".gz":
        return gzip.open(path, mode, encoding="utf-8")  # type: ignore[return-value]
    return path.open(mode, encoding="utf-8")


def read_manifest(path: Path) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    with path.open(encoding="utf-8") as handle:
        header = handle.readline().rstrip("\n\r").split("\t")
        required = ["label", "species", "fastq"]
        if header != required:
            raise ValueError(f"manifest header must be {required}, got {header}")
        for line_no, line in enumerate(handle, start=2):
            fields = line.rstrip("\n\r").split("\t")
            if len(fields) != 3:
                raise ValueError(f"manifest line {line_no} must contain 3 columns")
            label = int(fields[0])
            fastq = Path(fields[2]).expanduser()
            if not fastq.exists():
                raise FileNotFoundError(fastq)
            rows.append({"label": label, "species": fields[1], "fastq": fastq})
    rows.sort(key=lambda row: int(row["label"]))
    labels = [int(row["label"]) for row in rows]
    if labels != list(range(len(labels))):
        raise ValueError(f"labels must be contiguous from zero, got {labels}")
    return rows


def count_records(path: Path) -> int:
    line_count = 0
    with open_text(path, "rt") as handle:
        for line_count, _ in enumerate(handle, start=1):
            pass
    if line_count % 4:
        raise ValueError(f"FASTQ is not divisible into four-line records: {path}")
    return line_count // 4


def allocate_counts(available: list[int], max_per_species: int, total_cap: int) -> list[int]:
    target = [min(value, max_per_species) for value in available]
    if sum(target) <= total_cap:
        return target
    allocation = [0] * len(target)
    remaining = total_cap
    while remaining:
        candidates = [index for index, limit in enumerate(target) if allocation[index] < limit]
        if not candidates:
            raise RuntimeError("could not allocate the requested total cap")
        for index in candidates:
            allocation[index] += 1
            remaining -= 1
            if remaining == 0:
                break
    return allocation


def write_selected_records(
    source: Path,
    selected: set[int],
    output: TextIO,
    label: int,
    labels: list[int],
    read_length: int | None,
) -> None:
    with open_text(source, "rt") as handle:
        record_index = 0
        while True:
            record = [handle.readline() for _ in range(4)]
            if not record[0]:
                break
            if any(not line for line in record):
                raise ValueError(f"truncated FASTQ record in {source} at {record_index}")
            sequence = record[1].strip()
            if read_length is not None and len(sequence) != read_length:
                raise ValueError(
                    f"unexpected read length in {source}: {len(sequence)} != {read_length}"
                )
            if record_index in selected:
                output.writelines(record)
                labels.append(label)
            record_index += 1


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output-fastq", type=Path, required=True)
    parser.add_argument("--output-labels", type=Path, required=True)
    parser.add_argument("--output-metadata", type=Path, required=True)
    parser.add_argument("--max-per-species", type=int, default=50_000)
    parser.add_argument("--total-cap", type=int, default=1_500_000)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--read-length", type=int, default=75)
    args = parser.parse_args()
    if args.max_per_species < 1 or args.total_cap < 1:
        raise ValueError("sampling caps must be positive")

    rows = read_manifest(args.manifest)
    available = [count_records(row["fastq"]) for row in rows]  # type: ignore[arg-type]
    allocation = allocate_counts(available, args.max_per_species, args.total_cap)
    args.output_fastq.parent.mkdir(parents=True, exist_ok=True)
    args.output_labels.parent.mkdir(parents=True, exist_ok=True)
    args.output_metadata.parent.mkdir(parents=True, exist_ok=True)
    selected_by_species: dict[str, int] = {}
    labels: list[int] = []
    with open_text(args.output_fastq, "wt") as output:
        for row, available_count, selected_count in zip(rows, available, allocation):
            rng = random.Random(args.seed + int(row["label"]) * 1_000_003)
            selected = set(rng.sample(range(available_count), selected_count))
            write_selected_records(
                row["fastq"],  # type: ignore[arg-type]
                selected,
                output,
                int(row["label"]),
                labels,
                args.read_length,
            )
            selected_by_species[str(row["species"])] = selected_count

    labels_array = np.asarray(labels, dtype=np.int64)
    np.save(args.output_labels, labels_array)
    metadata = {
        "manifest": str(args.manifest.resolve()),
        "seed": args.seed,
        "read_length_bp": args.read_length,
        "max_per_species": args.max_per_species,
        "total_cap": args.total_cap,
        "n_species": len(rows),
        "n_reads": int(labels_array.size),
        "available_by_species": {
            str(row["species"]): count for row, count in zip(rows, available)
        },
        "selected_by_species": selected_by_species,
        "selection_rule": "deterministic per-species sampling followed by concatenation in label order",
        "fastq_and_labels_are_row_aligned": True,
    }
    args.output_metadata.write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(metadata, indent=2))


if __name__ == "__main__":
    main()
