from __future__ import annotations

import argparse
import csv
import gzip
import random
import sys
from pathlib import Path

def _find_project_root(start: Path) -> Path:
    for candidate in [start.parent, *start.parents]:
        if (candidate / "methods").is_dir() and (candidate / "configs").is_dir():
            return candidate
    raise RuntimeError("Could not locate the release repository root.")


PROJECT_ROOT = _find_project_root(Path(__file__).resolve())
sys.path.insert(0, str(PROJECT_ROOT))

from src.toy_data import apply_condition


def parse_csv_list(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


def parse_int_list(value: str) -> list[int]:
    return [int(item.strip()) for item in value.split(",") if item.strip()]


def fasta_sequences(path: Path, max_bases: int) -> str:
    opener = gzip.open if path.suffix == ".gz" else open
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


def default_genomes() -> list[tuple[str, Path]]:
    """Return conventional local filenames without embedding machine paths.

    Public releases cannot assume a contributor's private directory layout.
    Use ``--genome LABEL=PATH`` to supply actual FASTA locations.
    """
    root = PROJECT_ROOT / "data" / "reference_genomes" / "local_wgs"
    return [
        ("Aspergillus_fumigatus", root / "GCF_000002655.1_genomic.fna"),
        ("Candida_albicans", root / "GCF_000182965.3_genomic.fna"),
        ("Escherichia_coli_K12", root / "GCF_000005845.2_genomic.fna"),
        ("Escherichia_coli_O157", root / "GCF_000008865.2_genomic.fna"),
    ]


def parse_genome_specs(specs: list[str]) -> list[tuple[str, Path]]:
    genomes: list[tuple[str, Path]] = []
    for spec in specs:
        if "=" not in spec:
            raise ValueError("Each --genome value must use LABEL=PATH.")
        label, path_text = spec.split("=", 1)
        label = label.strip()
        if not label or not path_text.strip():
            raise ValueError("Each --genome value must provide a non-empty label and path.")
        genomes.append((label, Path(path_text).expanduser()))
    return genomes


def sample_rows(
    genomes: list[tuple[str, Path]],
    lengths: list[int],
    reads_per_genome: int,
    max_bases: int,
    seed: int,
    pe_lengths: list[int] | None = None,
    insert_size: int = 400,
) -> list[dict[str, str]]:
    templates: dict[str, str] = {}
    template_sources: dict[str, str] = {}
    for label, path in genomes:
        if not path.exists():
            gz = Path(str(path) + ".gz")
            if gz.exists():
                path = gz
            else:
                continue
        seq = fasta_sequences(path, max_bases=max_bases)
        if len(seq) >= max(lengths):
            templates[label] = seq
            template_sources[label] = str(path)
    if len(templates) < 2:
        raise RuntimeError("Need at least two readable genomes.")

    rows: list[dict[str, str]] = []
    for length in lengths:
        for label, seq in templates.items():
            rng = random.Random(f"{seed}:{label}:{length}")
            max_start = len(seq) - length
            for idx in range(reads_per_genome):
                for _ in range(100):
                    start = rng.randrange(0, max_start + 1)
                    read = seq[start:start + length].upper()
                    if "N" not in read and len(read) == length:
                        break
                else:
                    read = seq[start:start + length].replace("N", "A")
                clean_id = f"{label}_L{length}_R{idx:04d}"
                rows.append(
                    {
                        "read_id": f"{clean_id}_clean",
                        "clean_read_id": clean_id,
                        "sequence": read,
                        "label": label,
                        "species_id": label,
                        "condition": "clean",
                        "source_rule": "real_wgs_slice",
                        "source_length": str(length),
                        "length": str(len(read)),
                        "template_start": str(start),
                        "mutation_profile": "{}",
                        "notes": template_sources.get(label, ""),
                    }
                )
    for pe_length in pe_lengths or []:
        observed_length = pe_length * 2
        for label, seq in templates.items():
            rng = random.Random(f"{seed}:{label}:PE{pe_length}")
            min_span = pe_length * 2
            max_start = len(seq) - max(insert_size, min_span)
            if max_start <= 0:
                continue
            for idx in range(reads_per_genome):
                for _ in range(100):
                    start = rng.randrange(0, max_start + 1)
                    r1 = seq[start:start + pe_length].upper()
                    r2_start = min(len(seq) - pe_length, start + max(pe_length, insert_size - pe_length))
                    r2 = seq[r2_start:r2_start + pe_length].upper()
                    read = r1 + r2
                    if "N" not in read and len(read) == observed_length:
                        break
                else:
                    read = read.replace("N", "A")
                clean_id = f"{label}_PE{pe_length}_R{idx:04d}"
                rows.append(
                    {
                        "read_id": f"{clean_id}_clean",
                        "clean_read_id": clean_id,
                        "sequence": read,
                        "label": label,
                        "species_id": label,
                        "condition": "clean",
                        "source_rule": "real_wgs_paired_end_concat",
                        "source_length": str(observed_length),
                        "length": str(len(read)),
                        "template_start": str(start),
                        "mutation_profile": "{}",
                        "notes": f"PE{pe_length};insert_size={insert_size};{template_sources.get(label, '')}",
                    }
                )
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate lightweight real-genome slice reads from local FASTA files.")
    parser.add_argument("--output", default=str(PROJECT_ROOT / "data" / "real_slices" / "local_wgs_slices.csv"))
    parser.add_argument("--lengths", default="69,75,100,150")
    parser.add_argument("--paired-end-lengths", default="")
    parser.add_argument("--insert-size", type=int, default=400)
    parser.add_argument("--conditions", default="clean,substitution_1pct,N_3pct,reverse_complement")
    parser.add_argument("--reads-per-genome", type=int, default=120)
    parser.add_argument("--max-bases", type=int, default=500000)
    parser.add_argument("--seed", type=int, default=41)
    parser.add_argument(
        "--genome",
        action="append",
        default=[],
        metavar="LABEL=PATH",
        help="Optional repeatable FASTA source. Overrides conventional local defaults.",
    )
    args = parser.parse_args()

    base_rows = sample_rows(
        parse_genome_specs(args.genome) if args.genome else default_genomes(),
        parse_int_list(args.lengths),
        args.reads_per_genome,
        args.max_bases,
        args.seed,
        pe_lengths=parse_int_list(args.paired_end_lengths) if args.paired_end_lengths.strip() else [],
        insert_size=args.insert_size,
    )
    rows: list[dict[str, str]] = []
    for row in base_rows:
        for condition in parse_csv_list(args.conditions):
            rows.append(apply_condition(row, condition, args.seed))

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "read_id",
        "clean_read_id",
        "sequence",
        "label",
        "species_id",
        "condition",
        "source_rule",
        "source_length",
        "length",
        "template_start",
        "mutation_profile",
        "notes",
    ]
    with output.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {len(rows)} reads to {output}")


if __name__ == "__main__":
    main()

