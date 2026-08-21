"""Create a deterministic manifest for a panel of per-species FASTQ files."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--panel-csv", type=Path, required=True)
    parser.add_argument("--fastq-root", type=Path, required=True)
    parser.add_argument("--filename-template", default="R1_Batch1_{species}.fastq")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    with args.panel_csv.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    required = {"species", "kingdom", "genus"}
    if not rows or not required.issubset(rows[0]):
        raise ValueError(f"panel must contain columns {sorted(required)}")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8", newline="") as handle:
        handle.write("label\tspecies\tfastq\n")
        for label, row in enumerate(rows):
            species = row["species"]
            path = (
                args.fastq_root
                / row["kingdom"]
                / row["genus"]
                / species
                / args.filename_template.format(species=species)
            ).resolve()
            if not path.exists():
                raise FileNotFoundError(path)
            handle.write(f"{label}\t{species}\t{path}\n")
    print(f"wrote {len(rows)} FASTQ entries to {args.output}")


if __name__ == "__main__":
    main()
