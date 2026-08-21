"""Create or execute the reference-genome download plan for E5.

The default action is a dry run that writes a deterministic manifest. Passing
``--execute`` requires the NCBI ``datasets`` CLI and downloads one genome FASTA
per accession into the directory layout consumed by the CAMISIM input builder.
"""

from __future__ import annotations

import argparse
import csv
import shutil
import subprocess
import tempfile
import zipfile
from pathlib import Path

import pandas as pd


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--panel", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--datasets-executable", default="datasets")
    args = parser.parse_args()

    frame = pd.read_csv(args.panel)
    required = {"species", "kingdom", "genus", "assembly_accession"}
    missing = required.difference(frame.columns)
    if missing:
        raise ValueError(f"panel is missing columns: {sorted(missing)}")
    rows = []
    for row in frame.itertuples(index=False):
        accession = str(row.assembly_accession).strip()
        target = args.output_root / str(row.kingdom) / str(row.genus) / str(row.species) / f"{accession}_genomic.fna"
        rows.append(
            {
                "species": str(row.species),
                "assembly_accession": accession,
                "ncbi_url": f"https://www.ncbi.nlm.nih.gov/datasets/genome/{accession}/",
                "target_fasta": str(target.resolve()),
            }
        )

    args.manifest.parent.mkdir(parents=True, exist_ok=True)
    with args.manifest.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    if not args.execute:
        print(f"dry-run: wrote {len(rows)} reference download records to {args.manifest}")
        return

    if shutil.which(args.datasets_executable) is None:
        raise RuntimeError("--execute requires the NCBI datasets CLI on PATH")
    for item in rows:
        target = Path(item["target_fasta"])
        target.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(prefix="e5_datasets_") as temp_dir:
            archive = Path(temp_dir) / f"{item['assembly_accession']}.zip"
            subprocess.run(
                [
                    args.datasets_executable,
                    "download",
                    "genome",
                    "accession",
                    item["assembly_accession"],
                    "--include",
                    "genome",
                    "--filename",
                    str(archive),
                ],
                check=True,
            )
            with zipfile.ZipFile(archive) as zipped:
                fasta_names = [name for name in zipped.namelist() if name.endswith(".fna")]
                if len(fasta_names) != 1:
                    raise RuntimeError(f"expected one FASTA in {archive}, found {fasta_names}")
                with zipped.open(fasta_names[0]) as source, target.open("wb") as destination:
                    shutil.copyfileobj(source, destination)
        print(f"downloaded {item['assembly_accession']} -> {target}")


if __name__ == "__main__":
    main()
