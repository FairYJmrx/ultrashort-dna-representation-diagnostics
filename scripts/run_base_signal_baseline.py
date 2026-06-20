from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.base_encodings import encode_sequences
from src.ml_eval import evaluate_classifiers, make_split
from src.sklearn_features import load_dataset


def parse_csv_list(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


def parse_int_list(value: str) -> list[int]:
    return [int(item.strip()) for item in value.split(",") if item.strip()]


def write_json(path: Path, obj: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fh:
        json.dump(obj, fh, indent=2, ensure_ascii=False, sort_keys=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run raw-base and signal encoding baselines.")
    parser.add_argument("--input", default=str(PROJECT_ROOT / "data" / "toy_reads" / "toy_reads.csv"))
    parser.add_argument("--output-dir", default=str(PROJECT_ROOT / "results" / "runs" / "base_signal_smoke"))
    parser.add_argument("--lengths", default="69,75,100,150,200")
    parser.add_argument("--length-column", default="source_length", choices=["length", "source_length"])
    parser.add_argument("--conditions", default="clean,substitution_1pct,N_3pct,trim_to_69,reverse_complement")
    parser.add_argument(
        "--encodings",
        default="one_hot,eiip,hydrogen_bond_scalar,property_channels,tetrahedron,three_phase,fft_eiip,fft_three_phase,summary_entropy",
    )
    parser.add_argument("--seed", type=int, default=13)
    parser.add_argument("--classifiers", default="nearest_centroid,knn_3,linear_svm,logistic_regression")
    args = parser.parse_args()

    df = load_dataset(args.input)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    lengths = parse_int_list(args.lengths)
    conditions = parse_csv_list(args.conditions)
    encodings = parse_csv_list(args.encodings)
    classifier_names = parse_csv_list(args.classifiers)
    length_column = args.length_column if args.length_column in df.columns else "length"
    rows: list[dict[str, object]] = []
    started = time.time()

    for length in lengths:
        for condition in conditions:
            subset = df[(df[length_column] == length) & (df["condition"] == condition)].copy()
            if subset.empty or subset["label"].nunique() < 2:
                continue
            labels = subset["label"].tolist()
            train_idx, test_idx = make_split(labels, seed=args.seed)
            sequences = subset["sequence"].tolist()
            actual_max_len = int(subset["length"].max())
            encode_len = actual_max_len if args.length_column == "length" else length
            for encoding in encodings:
                try:
                    x = encode_sequences(sequences, encoding, encode_len)
                    classifiers = evaluate_classifiers(
                        x,
                        labels,
                        train_idx,
                        test_idx,
                        seed=args.seed,
                        classifier_names=classifier_names,
                    )
                    rows.append(
                        {
                            "length": length,
                            "length_column": length_column,
                            "condition": condition,
                            "encoding": encoding,
                            "n_samples": int(len(subset)),
                            "n_features": int(x.shape[1]),
                            "n_classes": int(subset["label"].nunique()),
                            "classifiers": classifiers,
                        }
                    )
                except Exception as exc:
                    rows.append(
                        {
                            "length": length,
                            "condition": condition,
                            "encoding": encoding,
                            "error": f"{type(exc).__name__}: {exc}",
                        }
                    )

    write_json(output_dir / "base_signal_results.json", {"elapsed_seconds": time.time() - started, "results": rows})
    flat_rows = []
    for row in rows:
        for clf_name, clf_result in row.get("classifiers", {}).items():
            flat_rows.append(
                {
                    "length": row.get("length"),
                    "condition": row.get("condition"),
                    "encoding": row.get("encoding"),
                    "classifier": clf_name,
                    "accuracy": clf_result.get("accuracy") if isinstance(clf_result, dict) else None,
                    "macro_f1": clf_result.get("macro_f1") if isinstance(clf_result, dict) else None,
                    "n_features": row.get("n_features"),
                }
            )
    flat = pd.DataFrame(flat_rows)
    flat.to_csv(output_dir / "base_signal_results_flat.csv", index=False, encoding="utf-8-sig")
    if not flat.empty:
        flat.sort_values(["macro_f1", "accuracy"], ascending=False).head(30).to_csv(
            output_dir / "base_signal_top30.csv", index=False, encoding="utf-8-sig"
        )
    print(f"Wrote {len(rows)} base/signal experiment rows to {output_dir}")


if __name__ == "__main__":
    main()
