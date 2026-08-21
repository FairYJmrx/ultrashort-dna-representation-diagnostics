"""Align CAMISIM mapping labels to a FASTQ without assuming row order."""

from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import json
import re
from pathlib import Path

import numpy as np


def open_text(path: Path):
    return gzip.open(path, "rt", encoding="utf-8") if path.suffix == ".gz" else path.open("r", encoding="utf-8")


def read_label_map(path: Path) -> dict[str, int]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError("label map must be a JSON object")
    result: dict[str, int] = {}
    for key, value in raw.items():
        if isinstance(value, int):
            result[str(key)] = value
        elif str(key).isdigit() and isinstance(value, str):
            result[value] = int(key)
        else:
            raise ValueError(f"unsupported label-map entry: {key!r}: {value!r}")
    if sorted(result.values()) != list(range(len(result))):
        raise ValueError("label ids must be contiguous from zero")
    return result


def read_panel(path: Path) -> dict[str, str]:
    with path.open(newline="", encoding="utf-8") as handle:
        rows = csv.DictReader(handle)
        required = {"assembly_accession", "species"}
        if not required.issubset(rows.fieldnames or []):
            raise ValueError(f"panel must contain {sorted(required)}")
        return {row["assembly_accession"]: row["species"] for row in rows}


def normalize_read_id(header: str) -> str:
    return header[1:].strip().split()[0] if header.startswith("@") else header.strip().split()[0]


def coordinate_group(read_id: str, group_span: int) -> int:
    match = re.search(r"(?P<accession>[A-Za-z]{1,4}_[A-Za-z0-9]+\.\d+)-(?P<start>\d+)", read_id)
    if not match:
        return 0
    key = f"{match.group('accession')}:{int(match.group('start')) // group_span}"
    return int.from_bytes(hashlib.blake2b(key.encode(), digest_size=8).digest(), "little")


def count_mapping_rows(path: Path) -> int:
    with path.open("r", encoding="utf-8") as handle:
        next(handle)
        return sum(1 for _ in handle)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fastq", type=Path, required=True)
    parser.add_argument("--mapping-tsv", type=Path, required=True)
    parser.add_argument("--panel-csv", type=Path, required=True)
    parser.add_argument("--label-map", type=Path, required=True)
    parser.add_argument("--output-labels", type=Path, required=True)
    parser.add_argument("--output-groups", type=Path)
    parser.add_argument("--group-span", type=int, default=1000)
    args = parser.parse_args()
    if args.group_span < 1:
        raise ValueError("group span must be positive")

    labels_by_species = read_label_map(args.label_map)
    species_by_genome = read_panel(args.panel_csv)
    n_rows = count_mapping_rows(args.mapping_tsv)
    args.output_labels.parent.mkdir(parents=True, exist_ok=True)
    labels = np.lib.format.open_memmap(args.output_labels, mode="w+", dtype=np.int64, shape=(n_rows,))
    groups = None
    if args.output_groups:
        args.output_groups.parent.mkdir(parents=True, exist_ok=True)
        groups = np.lib.format.open_memmap(args.output_groups, mode="w+", dtype=np.uint64, shape=(n_rows,))

    with args.mapping_tsv.open("r", encoding="utf-8") as mapping, open_text(args.fastq) as fastq:
        header = mapping.readline().rstrip("\n\r").split("\t")
        required = {"anonymous_read_id", "genome_id", "original_read_id"}
        if not required.issubset(header):
            raise ValueError(f"mapping file must contain {sorted(required)}")
        positions = {name: header.index(name) for name in required}
        for index in range(n_rows):
            fields = mapping.readline().rstrip("\n\r").split("\t")
            if len(fields) <= max(positions.values()):
                raise ValueError(f"truncated mapping row at {index}")
            fastq_header = fastq.readline()
            if not fastq_header:
                raise ValueError(f"FASTQ ended before mapping row {index}")
            fastq_id = normalize_read_id(fastq_header)
            mapped_id = fields[positions["original_read_id"]]
            if fastq_id != mapped_id:
                raise ValueError(
                    f"FASTQ/mapping order mismatch at row {index}: FASTQ={fastq_id!r}, mapping={mapped_id!r}"
                )
            sequence, plus, quality = fastq.readline(), fastq.readline(), fastq.readline()
            if not sequence or not plus or not quality:
                raise ValueError(f"truncated FASTQ record at row {index}")
            genome_id = fields[positions["genome_id"]]
            species = species_by_genome.get(genome_id)
            if species is None or species not in labels_by_species:
                raise ValueError(f"genome is absent from the 35-species panel: {genome_id}")
            labels[index] = labels_by_species[species]
            if groups is not None:
                groups[index] = coordinate_group(mapped_id, args.group_span)

    labels.flush()
    if groups is not None:
        groups.flush()
    print(json.dumps({"n_rows": n_rows, "labels": str(args.output_labels.resolve()), "groups": str(args.output_groups.resolve()) if args.output_groups else None}, indent=2))


if __name__ == "__main__":
    main()
