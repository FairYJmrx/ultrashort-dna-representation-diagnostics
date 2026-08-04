"""Replace machine-local provenance paths with accessions or repository paths."""

from __future__ import annotations

import csv
import re
from pathlib import Path, PureWindowsPath


ROOT = Path(__file__).resolve().parents[1]
ACCESSION = re.compile(r"GC[AF]_\d+\.\d+")
ABSOLUTE = re.compile(r"[A-Za-z]:[\\/]")

READ_TABLES = [
    "data/real_slices/close_relative_reads.csv",
    "data/real_slices/local_wgs_slices.csv",
    "data/real_slices/stage2_close_relative_base_reads.csv",
    "results/stage3/contract_v2/compact_baselines/stage3_compact_baseline_reads.csv",
    "results/stage3/contract_v2/property_redundancy_runtime/audit_clean_read_sample.csv",
]

TEXT_FILES = [
    "results/stage3/art_ck4p_position_ablation/art_validation_summary.md",
    "results/stage3/art_fullmatrix_property_contribution/art_validation_summary.md",
    "results/stage3/art_illumina/art_completed_summary.md",
    "results/stage3/contract_v2/art_current_contract/art_completed_summary.md",
    "results/stage3/contract_v2/p_msp_contribution/p_msp_contribution_summary.md",
    "results/stage3/contract_v2/property_redundancy_runtime/property_redundancy_runtime_summary.md",
]


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader.fieldnames or []), list(reader)


def write_csv(path: Path, fields: list[str], rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def sanitize_manifests() -> dict[str, str]:
    accessions: dict[str, str] = {}
    for relative in (
        "data/real_slices/close_relative_genomes_manifest.csv",
        "data/real_slices/close_relative_genomes_manifest_preview.csv",
    ):
        path = ROOT / relative
        fields, rows = read_csv(path)
        for row in rows:
            label = row.get("label", "")
            accession = row.get("assembly_accession", "")
            genus = row.get("genus", "")
            if label and accession:
                accessions[label] = accession
                row["genome_path"] = (
                    f"data/reference_genomes/close_relative/{genus}/{label}/"
                    f"{accession}_genomic.fna"
                )
                if row.get("genome_status") == "local_wgs":
                    row["genome_status"] = "public_accession"
        write_csv(path, fields, rows)
    return accessions


def sanitize_read_tables(accessions: dict[str, str]) -> None:
    for relative in READ_TABLES:
        path = ROOT / relative
        fields, rows = read_csv(path)
        if "notes" not in fields:
            continue
        for row in rows:
            notes = row.get("notes", "")
            if relative.endswith("local_wgs_slices.csv"):
                row["notes"] = f"source_label={row.get('label', '')}"
                continue
            if not ABSOLUTE.search(notes):
                continue
            accession = accessions.get(row.get("label", ""), "")
            if not accession:
                match = ACCESSION.search(notes)
                accession = match.group(0) if match else ""
            row["notes"] = f"assembly_accession={accession}" if accession else f"source_label={row.get('label', '')}"
        write_csv(path, fields, rows)


def sanitize_art_manifest() -> None:
    path = ROOT / "results/stage3/contract_v2/art_current_contract/art_generation_manifest.csv"
    fields, rows = read_csv(path)
    for row in rows:
        for field, value in list(row.items()):
            if value and ABSOLUTE.search(value):
                name = PureWindowsPath(value).name
                row[field] = f"results/stage3/contract_v2/art_current_contract/fastq/{name}"
    write_csv(path, fields, rows)


def sanitize_inventory() -> None:
    path = ROOT / "results/audits/result_inventory/run_json_configuration_inventory.csv"
    fields, rows = read_csv(path)
    roots = (
        "D:\\AI-NGS\\info\\release_code\\",
        "D:\\AI-NGS\\info\\",
        "D:/AI-NGS/info/release_code/",
        "D:/AI-NGS/info/",
        "D:/AI-NGS/信息学/",
    )
    for row in rows:
        for field, value in list(row.items()):
            if not value:
                continue
            for root in roots:
                value = value.replace(root, "")
            row[field] = value.replace("\\", "/")
    write_csv(path, fields, rows)


def sanitize_text() -> None:
    replacements = (
        ("D:\\AI-NGS\\info\\release_code\\", ""),
        ("D:\\AI-NGS\\info\\", ""),
        ("D:\\AI-NGS\\信息学\\", ""),
        ("D:/AI-NGS/info/release_code/", ""),
        ("D:/AI-NGS/info/", ""),
    )
    for relative in TEXT_FILES:
        path = ROOT / relative
        text = path.read_text(encoding="utf-8-sig")
        for old, new in replacements:
            text = text.replace(old, new)
        path.write_text(text.replace("\\", "/"), encoding="utf-8", newline="\n")


def main() -> None:
    accessions = sanitize_manifests()
    sanitize_read_tables(accessions)
    sanitize_art_manifest()
    sanitize_inventory()
    sanitize_text()
    print("ok: machine-local paths replaced with accessions or repository-relative paths")


if __name__ == "__main__":
    main()
