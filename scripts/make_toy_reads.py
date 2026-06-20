from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.toy_data import generate_dataset


def parse_csv_list(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


def parse_int_list(value: str) -> list[int]:
    return [int(item.strip()) for item in value.split(",") if item.strip()]


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate controlled lightweight DNA reads.")
    parser.add_argument("--output", default=str(PROJECT_ROOT / "data" / "toy_reads" / "toy_reads.csv"))
    parser.add_argument("--species", default="GC_rich,AT_rich,near_SNP")
    parser.add_argument("--lengths", default="69,75,100,150,200")
    parser.add_argument("--conditions", default="clean,substitution_1pct,N_3pct,trim_to_69,reverse_complement")
    parser.add_argument("--reads-per-species", type=int, default=20)
    parser.add_argument("--seed", type=int, default=13)
    parser.add_argument("--template-length", type=int, default=6000)
    args = parser.parse_args()

    rows = generate_dataset(
        output_csv=Path(args.output),
        species=parse_csv_list(args.species),
        lengths=parse_int_list(args.lengths),
        conditions=parse_csv_list(args.conditions),
        reads_per_species=args.reads_per_species,
        seed=args.seed,
        template_length=args.template_length,
    )
    print(f"Wrote {len(rows)} reads to {args.output}")


if __name__ == "__main__":
    main()
