from __future__ import annotations

import argparse
import csv
import gzip
import random
import sys
from pathlib import Path

import pandas as pd

def _find_project_root(start: Path) -> Path:
    for candidate in [start.parent, *start.parents]:
        if (candidate / "methods").is_dir() and (candidate / "configs").is_dir():
            return candidate
    raise RuntimeError("Could not locate the release repository root.")


PROJECT_ROOT = _find_project_root(Path(__file__).resolve())
sys.path.insert(0, str(PROJECT_ROOT))

from src.sequence_utils import reverse_complement
from src.toy_data import apply_condition


def parse_csv_list(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


def parse_int_list(value: str) -> list[int]:
    return [int(item.strip()) for item in value.split(",") if item.strip()]


def fasta_sequences(path: Path, max_bases: int) -> str:
    opener = gzip.open if path.name.endswith(".gz") else open
    chunks: list[str] = []
    total = 0
    with opener(path, "rt", encoding="utf-8", errors="ignore") as fh:
        for line in fh:
            if line.startswith(">"):
                continue
            seq = "".join(base for base in line.strip().upper() if base in "ACGTN")
            if not seq:
                continue
            chunks.append(seq)
            total += len(seq)
            if total >= max_bases:
                break
    return "".join(chunks)[:max_bases]


def choose_clean_slice(seq: str, length: int, rng: random.Random) -> tuple[str, int]:
    max_start = len(seq) - length
    if max_start < 0:
        raise ValueError("Sequence shorter than requested read length.")
    start = 0
    read = ""
    for _ in range(200):
        start = rng.randrange(0, max_start + 1)
        read = seq[start:start + length].upper()
        if len(read) == length and "N" not in read:
            return read, start
    return read.replace("N", "A"), start


def choose_paired_end(seq: str, pe_length: int, insert_size: int, rng: random.Random) -> tuple[str, int, int]:
    observed = pe_length * 2
    min_span = max(insert_size, observed)
    max_start = len(seq) - min_span
    if max_start < 0:
        raise ValueError("Sequence shorter than requested paired-end span.")
    start = 0
    r2_start = 0
    read = ""
    for _ in range(200):
        start = rng.randrange(0, max_start + 1)
        r1 = seq[start:start + pe_length].upper()
        r2_start = start + max(pe_length, insert_size - pe_length)
        r2_template = seq[r2_start:r2_start + pe_length].upper()
        r2 = reverse_complement(r2_template)
        read = r1 + r2
        if len(read) == observed and "N" not in read:
            return read, start, r2_start
    return read.replace("N", "A"), start, r2_start


def load_templates(manifest: Path, max_bases: int, genera: list[str]) -> list[dict[str, object]]:
    df = pd.read_csv(manifest)
    if genera:
        df = df[df["genus"].isin(genera)]
    df = df[df["genome_status"].isin(["local_wgs", "downloaded", "cached"])]
    records: list[dict[str, object]] = []
    for _, row in df.iterrows():
        path = Path(str(row["genome_path"]))
        if not path.exists():
            continue
        seq = fasta_sequences(path, max_bases=max_bases)
        if seq:
            record = row.to_dict()
            record["sequence_template"] = seq
            records.append(record)
    if not records:
        raise RuntimeError("No readable genomes in manifest.")
    return records


def make_base_rows(
    records: list[dict[str, object]],
    lengths: list[int],
    paired_end_lengths: list[int],
    reads_per_genome: int,
    seed: int,
    insert_size: int,
) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for record in records:
        seq = str(record["sequence_template"])
        label = str(record["label"])
        genus = str(record["genus"])
        species = str(record["species"])
        benchmark_role = str(record["benchmark_role"])
        accession = str(record["assembly_accession"])
        for length in lengths:
            if len(seq) < length:
                continue
            rng = random.Random(f"{seed}:{accession}:{length}")
            for idx in range(reads_per_genome):
                read, start = choose_clean_slice(seq, length, rng)
                clean_id = f"{label}_L{length}_R{idx:04d}"
                rows.append(
                    {
                        "read_id": f"{clean_id}_clean",
                        "clean_read_id": clean_id,
                        "sequence": read,
                        "label": label,
                        "species_id": label,
                        "genus": genus,
                        "species": species,
                        "benchmark_role": benchmark_role,
                        "target_binary": "target_pathogen"
                        if benchmark_role == "target_pathogen_candidate"
                        else "close_or_background",
                        "condition": "clean",
                        "source_rule": "close_relative_wgs_slice",
                        "source_length": str(length),
                        "observed_layout": f"SE{length}",
                        "length": str(len(read)),
                        "template_start": str(start),
                        "template_end": str(start + length),
                        "mutation_profile": "{}",
                        "notes": f"{accession};{record['genome_path']}",
                    }
                )
        for pe_length in paired_end_lengths:
            if len(seq) < max(insert_size, pe_length * 2):
                continue
            rng = random.Random(f"{seed}:{accession}:PE{pe_length}:{insert_size}")
            observed = pe_length * 2
            for idx in range(reads_per_genome):
                read, start, r2_start = choose_paired_end(seq, pe_length, insert_size, rng)
                clean_id = f"{label}_PE{pe_length}_R{idx:04d}"
                rows.append(
                    {
                        "read_id": f"{clean_id}_clean",
                        "clean_read_id": clean_id,
                        "sequence": read,
                        "label": label,
                        "species_id": label,
                        "genus": genus,
                        "species": species,
                        "benchmark_role": benchmark_role,
                        "target_binary": "target_pathogen"
                        if benchmark_role == "target_pathogen_candidate"
                        else "close_or_background",
                        "condition": "clean",
                        "source_rule": "close_relative_wgs_paired_end_concat",
                        "source_length": str(observed),
                        "observed_layout": f"PE{pe_length}",
                        "length": str(len(read)),
                        "template_start": str(start),
                        "template_end": str(r2_start + pe_length),
                        "mutation_profile": "{}",
                        "notes": f"{accession};insert_size={insert_size};{record['genome_path']}",
                    }
                )
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate close-relative lightweight WGS reads.")
    parser.add_argument("--manifest", default=str(PROJECT_ROOT / "data" / "real_slices" / "close_relative_genomes_manifest.csv"))
    parser.add_argument("--output", default=str(PROJECT_ROOT / "data" / "real_slices" / "close_relative_reads.csv"))
    parser.add_argument("--genera", default="")
    parser.add_argument("--lengths", default="69,75,100,125,150")
    parser.add_argument("--paired-end-lengths", default="150")
    parser.add_argument("--insert-size", type=int, default=400)
    parser.add_argument("--conditions", default="clean,N_3pct,substitution_1pct,reverse_complement")
    parser.add_argument("--reads-per-genome", type=int, default=80)
    parser.add_argument("--max-bases", type=int, default=500000)
    parser.add_argument("--seed", type=int, default=57)
    args = parser.parse_args()

    records = load_templates(Path(args.manifest), args.max_bases, parse_csv_list(args.genera))
    base_rows = make_base_rows(
        records,
        parse_int_list(args.lengths),
        parse_int_list(args.paired_end_lengths),
        args.reads_per_genome,
        args.seed,
        args.insert_size,
    )

    rows: list[dict[str, str]] = []
    conditions = parse_csv_list(args.conditions)
    for row in base_rows:
        for condition in conditions:
            conditioned = apply_condition(row, condition, args.seed)
            conditioned["genus"] = row["genus"]
            conditioned["species"] = row["species"]
            conditioned["benchmark_role"] = row["benchmark_role"]
            conditioned["target_binary"] = row["target_binary"]
            conditioned["observed_layout"] = row["observed_layout"]
            conditioned["template_end"] = row["template_end"]
            rows.append(conditioned)

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "read_id",
        "clean_read_id",
        "sequence",
        "label",
        "species_id",
        "genus",
        "species",
        "benchmark_role",
        "target_binary",
        "condition",
        "source_rule",
        "source_length",
        "observed_layout",
        "length",
        "template_start",
        "template_end",
        "mutation_profile",
        "notes",
    ]
    with output.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {len(rows)} close-relative reads from {len(records)} genomes to {output}")


if __name__ == "__main__":
    main()

