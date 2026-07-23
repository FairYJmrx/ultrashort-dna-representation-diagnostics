from __future__ import annotations

import argparse
import csv
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

from src.sequence_utils import random_dna
from src.toy_data import apply_condition


def parse_csv_list(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


def parse_int_list(value: str) -> list[int]:
    return [int(item.strip()) for item in value.split(",") if item.strip()]


def block_order_pair(length: int, rng: random.Random) -> tuple[str, str]:
    """Return two reads made from the same short blocks in different order."""
    block_len = 5
    n_blocks = (length + block_len - 1) // block_len
    pool = [
        "AACGT",
        "CCGTA",
        "GGTAC",
        "TTACG",
        "AGGCT",
        "TCGGA",
        "CATGC",
        "GTCCA",
        "ATCGA",
        "CGATC",
    ]
    blocks = [rng.choice(pool) for _ in range(n_blocks)]
    seq_a = "".join(sorted(blocks))[:length]
    even = blocks[::2]
    odd = blocks[1::2]
    seq_b = "".join(odd[::-1] + even)[:length]
    return seq_a, seq_b


def motif_jitter_read(length: int, label: str, rng: random.Random) -> str:
    background = list(random_dna(length, {"A": 0.25, "C": 0.25, "G": 0.25, "T": 0.25}, rng))
    target = "GATTACAGCG"
    distractors = ["GATTTTAGCG", "CATTACAGCA", "GATTGCAGTG"]
    if label == "motif_jitter_front":
        center = 8
    elif label == "motif_jitter_middle":
        center = length // 2 - len(target) // 2
    elif label == "motif_jitter_back":
        center = length - len(target) - 8
    else:
        raise ValueError(f"Unsupported motif label: {label}")
    jitter = rng.randint(-4, 4)
    pos = max(0, min(length - len(target), center + jitter))
    background[pos:pos + len(target)] = target

    for distractor in distractors:
        for _ in range(20):
            dpos = rng.randrange(0, max(1, length - len(distractor) + 1))
            if abs(dpos - pos) > len(target) + 3:
                background[dpos:dpos + len(distractor)] = distractor
                break
    return "".join(background)


def clean_rows(lengths: list[int], reads_per_class: int, seed: int) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for length in lengths:
        for idx in range(reads_per_class):
            rng = random.Random(f"{seed}:block:{length}:{idx}")
            seq_a, seq_b = block_order_pair(length, rng)
            for label, seq in [("same_spectrum_A", seq_a), ("same_spectrum_B", seq_b)]:
                clean_id = f"{label}_L{length}_R{idx:04d}"
                rows.append(
                    {
                        "read_id": f"{clean_id}_clean",
                        "clean_read_id": clean_id,
                        "sequence": seq,
                        "label": label,
                        "species_id": label,
                        "condition": "clean",
                        "source_rule": "same_block_multiset_order",
                        "source_length": str(length),
                        "length": str(len(seq)),
                        "template_start": "-1",
                        "mutation_profile": "{}",
                        "notes": "same short-block multiset, different order",
                    }
                )

        for label in ["motif_jitter_front", "motif_jitter_middle", "motif_jitter_back"]:
            for idx in range(reads_per_class):
                rng = random.Random(f"{seed}:motif:{label}:{length}:{idx}")
                seq = motif_jitter_read(length, label, rng)
                clean_id = f"{label}_L{length}_R{idx:04d}"
                rows.append(
                    {
                        "read_id": f"{clean_id}_clean",
                        "clean_read_id": clean_id,
                        "sequence": seq,
                        "label": label,
                        "species_id": label,
                        "condition": "clean",
                        "source_rule": "motif_position_jitter_with_distractors",
                        "source_length": str(length),
                        "length": str(len(seq)),
                        "template_start": "-1",
                        "mutation_profile": "{}",
                        "notes": "target motif has jitter and distractor motifs",
                    }
                )
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate hardened controlled DNA read tasks.")
    parser.add_argument("--output", default=str(PROJECT_ROOT / "data" / "toy_reads" / "toy_hardened_tasks.csv"))
    parser.add_argument("--lengths", default="69,75,100")
    parser.add_argument("--conditions", default="clean,substitution_1pct,N_3pct,N_cluster_5pct,reverse_complement")
    parser.add_argument("--reads-per-class", type=int, default=80)
    parser.add_argument("--seed", type=int, default=31)
    args = parser.parse_args()

    base_rows = clean_rows(parse_int_list(args.lengths), args.reads_per_class, args.seed)
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

