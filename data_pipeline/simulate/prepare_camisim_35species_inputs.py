"""Prepare the small CAMISIM input manifests for the 35-species panel.

The script consumes a panel spreadsheet containing public reference metadata
and writes only CAMISIM input tables. Reference FASTA files are external and
are never copied or downloaded by this entrypoint.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd


REQUIRED_COLUMNS = {"species", "taxid", "kingdom", "genus", "assembly_accession"}


def load_panel(path: Path, sheet_name: str, expected_species: int) -> pd.DataFrame:
    frame = pd.read_excel(path, sheet_name=sheet_name) if path.suffix.lower() in {".xlsx", ".xls"} else pd.read_csv(path)
    missing = REQUIRED_COLUMNS.difference(frame.columns)
    if missing:
        raise ValueError(f"panel is missing columns: {sorted(missing)}")
    frame = frame[frame["species"].astype(str).str.strip() != "Homo sapiens"].copy()
    if len(frame) != expected_species:
        raise ValueError(f"expected {expected_species} non-human species, found {len(frame)}")
    frame["species"] = frame["species"].astype(str).str.strip()
    frame["kingdom"] = frame["kingdom"].astype(str).str.strip()
    frame["genus"] = frame["genus"].astype(str).str.strip()
    frame["assembly_accession"] = frame["assembly_accession"].astype(str).str.strip()
    if frame["species"].duplicated().any():
        raise ValueError("the panel must contain one representative assembly per species")
    return frame


def build_reference_path(row: pd.Series, wgs_root: str) -> str:
    return "/".join(
        [
            wgs_root.rstrip("/"),
            row.kingdom,
            row.genus,
            row.species,
            f"{row.assembly_accession}_genomic.fna",
        ]
    )


def write_inputs(frame: pd.DataFrame, output_dir: Path, wgs_root: str) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    genome_lines = [
        f"{row.assembly_accession}\t{build_reference_path(row, wgs_root)}"
        for row in frame.itertuples(index=False)
    ]
    (output_dir / "genome_to_id.tsv").write_text("\n".join(genome_lines) + "\n", encoding="utf-8")

    species_to_otu = {species: f"OTU{index + 1}" for index, species in enumerate(sorted(frame["species"]))}
    metadata_lines = ["genome_ID\tOTU\tNCBI_ID\tnovelty_category"]
    for row in frame.itertuples(index=False):
        metadata_lines.append(
            f"{row.assembly_accession}\t{species_to_otu[row.species]}\t{int(row.taxid)}\tknown_species"
        )
    (output_dir / "metadata.tsv").write_text("\n".join(metadata_lines) + "\n", encoding="utf-8")

    label_map = {str(index): species for index, species in enumerate(sorted(frame["species"]))}
    (output_dir / "label_map.json").write_text(json.dumps(label_map, indent=2) + "\n", encoding="utf-8")
    panel = frame[["species", "taxid", "kingdom", "genus", "assembly_accession"]].copy()
    panel.to_csv(output_dir / "species_panel.csv", index=False)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    panel_group = parser.add_mutually_exclusive_group(required=True)
    panel_group.add_argument("--panel-xlsx", type=Path)
    panel_group.add_argument("--panel-csv", type=Path)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--sheet-name", default="Blood_ALL_Master")
    parser.add_argument("--wgs-root", default="/external/reference_genomes")
    parser.add_argument("--expected-species", type=int, default=35)
    args = parser.parse_args()

    panel_path = args.panel_xlsx or args.panel_csv
    if not panel_path.exists():
        raise FileNotFoundError(panel_path)
    frame = load_panel(panel_path, args.sheet_name, args.expected_species)
    write_inputs(frame, args.output_dir.resolve(), args.wgs_root)
    print(f"wrote CAMISIM input manifests for {len(frame)} species to {args.output_dir.resolve()}")


if __name__ == "__main__":
    main()
