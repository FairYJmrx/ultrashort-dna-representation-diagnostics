from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.sklearn_features import build_kmer_matrix, load_dataset, profile_duplicate_rate, sparsity_report


def parse_csv_list(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


def parse_int_list(value: str) -> list[int]:
    return [int(item.strip()) for item in value.split(",") if item.strip()]


def write_json(path: Path, obj: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fh:
        json.dump(obj, fh, indent=2, ensure_ascii=False, sort_keys=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run non-training k-mer sparsity diagnostics.")
    parser.add_argument("--input", default=str(PROJECT_ROOT / "data" / "toy_reads" / "toy_first_wave.csv"))
    parser.add_argument("--output-dir", default=str(PROJECT_ROOT / "results" / "runs" / "kmer_diagnostics"))
    parser.add_argument("--lengths", default="69,75,100,150,200")
    parser.add_argument("--length-column", default="source_length", choices=["length", "source_length"])
    parser.add_argument("--conditions", default="clean,substitution_1pct,N_3pct,trim_to_69,reverse_complement")
    parser.add_argument("--k-values", default="2,3,4,5,6,7,8,10,12")
    parser.add_argument("--canonical", action="store_true")
    args = parser.parse_args()

    df = load_dataset(args.input)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    lengths = parse_int_list(args.lengths)
    conditions = parse_csv_list(args.conditions)
    k_values = parse_int_list(args.k_values)
    length_column = args.length_column if args.length_column in df.columns else "length"
    rows = []
    started = time.time()

    for length in lengths:
        for condition in conditions:
            subset = df[(df[length_column] == length) & (df["condition"] == condition)].copy()
            if subset.empty:
                continue
            sequences = subset["sequence"].tolist()
            for k in k_values:
                if length < k:
                    continue
                matrix, vocab = build_kmer_matrix(sequences, k=k, canonical=args.canonical, vocabulary_mode="observed")
                diag = sparsity_report(matrix)
                diag["profile_duplicate_rate"] = profile_duplicate_rate(matrix)
                diag["observed_vocab_size"] = len(vocab)
                diag["theoretical_vocab_size"] = int(4**k)
                diag.update(
                    {
                        "length": length,
                        "length_column": length_column,
                        "condition": condition,
                        "k": k,
                        "canonical": args.canonical,
                        "n_classes": int(subset["label"].nunique()),
                    }
                )
                rows.append(diag)

    write_json(output_dir / "kmer_diagnostics.json", {"elapsed_seconds": time.time() - started, "results": rows})
    pd.DataFrame(rows).to_csv(output_dir / "kmer_diagnostics.csv", index=False, encoding="utf-8-sig")
    print(f"Wrote {len(rows)} k-mer diagnostic rows to {output_dir}")


if __name__ == "__main__":
    main()
