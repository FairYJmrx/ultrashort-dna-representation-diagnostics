from __future__ import annotations

import argparse
import csv
import gzip
import re
import sys
import zipfile
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def parse_csv_list(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


def safe_name(value: str) -> str:
    value = re.sub(r"[^A-Za-z0-9_.-]+", "_", str(value).strip())
    return value.strip("_") or "unknown"


def find_local_genomes(wgs_root: Path) -> dict[str, Path]:
    index: dict[str, Path] = {}
    if not wgs_root.exists():
        return index
    for path in wgs_root.rglob("*"):
        if not path.is_file():
            continue
        if not (path.name.endswith(".fna") or path.name.endswith(".fna.gz") or path.name.endswith(".fa") or path.name.endswith(".fasta")):
            continue
        match = re.search(r"(GC[AF]_\d+\.\d+)", path.name)
        if match:
            index.setdefault(match.group(1), path)
    return index


def count_fasta_bases(path: Path) -> int:
    opener = gzip.open if path.name.endswith(".gz") else open
    total = 0
    with opener(path, "rt", encoding="utf-8", errors="ignore") as fh:
        for line in fh:
            if not line.startswith(">"):
                total += sum(1 for base in line.strip().upper() if base in "ACGTN")
    return total


def download_genome_fasta(accession: str, output_path: Path, timeout: int = 120) -> tuple[str, str]:
    if output_path.exists() and output_path.stat().st_size > 0:
        return "cached", ""

    url = (
        "https://api.ncbi.nlm.nih.gov/datasets/v2/genome/accession/"
        f"{accession}/download?include_annotation_type=GENOME_FASTA"
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    zip_path = output_path.with_suffix(".zip")
    request = Request(url, method="GET", headers={"User-Agent": "AI-NGS-close-relative-benchmark/0.1"})
    try:
        with urlopen(request, timeout=timeout) as response:
            zip_path.write_bytes(response.read())
        with zipfile.ZipFile(zip_path) as zf:
            fasta_members = [
                name
                for name in zf.namelist()
                if name.endswith(".fna") or name.endswith(".fa") or name.endswith(".fasta")
            ]
            if not fasta_members:
                return "failed", "No FASTA member found in NCBI datasets zip."
            fasta_member = sorted(fasta_members, key=len)[0]
            with zf.open(fasta_member) as src, output_path.open("wb") as dst:
                dst.write(src.read())
        return "downloaded", ""
    except (HTTPError, URLError, TimeoutError, zipfile.BadZipFile, OSError) as exc:
        return "failed", f"{type(exc).__name__}: {exc}"


def load_candidates(excel_path: Path, sheet: str, genera: list[str]) -> pd.DataFrame:
    df = pd.read_excel(excel_path, sheet_name=sheet)
    required = [
        "genus",
        "species",
        "taxid",
        "benchmark_role",
        "dataset_role",
        "assembly_accession",
        "representative_strain",
    ]
    missing = [col for col in required if col not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns in {excel_path}: {missing}")
    out = df[df["genus"].isin(genera)][required].copy()
    out = out.dropna(subset=["genus", "species", "assembly_accession"])
    out["assembly_accession"] = out["assembly_accession"].astype(str).str.strip()
    out = out[out["assembly_accession"].str.match(r"GC[AF]_\d+\.\d+", na=False)]
    return out.sort_values(["genus", "benchmark_role", "species"])


def main() -> None:
    parser = argparse.ArgumentParser(description="Prepare close-relative RefSeq genomes from Excel metadata.")
    parser.add_argument(
        "--excel",
        default=str(PROJECT_ROOT / "data" / "metadata" / "AI_NGS_blood_ALL_P0.xlsx"),
        help="Excel metadata file. Copy or symlink the blood-panel spreadsheet here, or pass an explicit path.",
    )
    parser.add_argument("--sheet", default="Blood_ALL_Master")
    parser.add_argument("--genera", default="Candida,Klebsiella,Acinetobacter,Burkholderia,Enterobacter,Escherichia")
    parser.add_argument(
        "--wgs-root",
        default=str(PROJECT_ROOT / "data" / "reference_genomes" / "local_wgs"),
        help="Optional local FASTA root used before NCBI download.",
    )
    parser.add_argument("--output-dir", default=str(PROJECT_ROOT / "data" / "reference_genomes" / "close_relative"))
    parser.add_argument("--manifest", default=str(PROJECT_ROOT / "data" / "real_slices" / "close_relative_genomes_manifest.csv"))
    parser.add_argument("--download-missing", action="store_true")
    parser.add_argument("--timeout", type=int, default=120)
    args = parser.parse_args()

    excel_path = Path(args.excel)
    if not excel_path.exists():
        raise FileNotFoundError(excel_path)

    genera = parse_csv_list(args.genera)
    candidates = load_candidates(excel_path, args.sheet, genera)
    local_index = find_local_genomes(Path(args.wgs_root))
    output_dir = Path(args.output_dir)

    rows: list[dict[str, object]] = []
    for _, item in candidates.iterrows():
        accession = str(item["assembly_accession"]).strip()
        genus = str(item["genus"]).strip()
        species = str(item["species"]).strip()
        local_path = local_index.get(accession)
        notes = ""
        if local_path and local_path.exists():
            genome_path = local_path
            status = "local_wgs"
        elif args.download_missing:
            genome_path = output_dir / safe_name(genus) / safe_name(species) / f"{accession}_genomic.fna"
            status, notes = download_genome_fasta(accession, genome_path, timeout=args.timeout)
        else:
            genome_path = output_dir / safe_name(genus) / safe_name(species) / f"{accession}_genomic.fna"
            status = "missing_not_downloaded"

        base_count = ""
        if genome_path.exists() and status != "failed":
            try:
                base_count = count_fasta_bases(genome_path)
            except OSError as exc:
                notes = f"{notes}; count_failed={exc}".strip("; ")

        rows.append(
            {
                "genus": genus,
                "species": species,
                "label": safe_name(species),
                "taxid": item["taxid"],
                "benchmark_role": item["benchmark_role"],
                "dataset_role": item["dataset_role"],
                "assembly_accession": accession,
                "representative_strain": item["representative_strain"],
                "genome_path": str(genome_path),
                "genome_status": status,
                "base_count": base_count,
                "notes": notes,
            }
        )

    manifest = Path(args.manifest)
    manifest.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "genus",
        "species",
        "label",
        "taxid",
        "benchmark_role",
        "dataset_role",
        "assembly_accession",
        "representative_strain",
        "genome_path",
        "genome_status",
        "base_count",
        "notes",
    ]
    with manifest.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    status_counts: dict[str, int] = {}
    for row in rows:
        status_counts[str(row["genome_status"])] = status_counts.get(str(row["genome_status"]), 0) + 1
    print(f"Wrote {len(rows)} genome manifest rows to {manifest}")
    print(status_counts)
    failed = [row for row in rows if row["genome_status"] == "failed"]
    if failed:
        print("Failed accessions:", ", ".join(str(row["assembly_accession"]) for row in failed), file=sys.stderr)


if __name__ == "__main__":
    main()
