from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.ml_eval import evaluate_classifiers, make_split
from src.position_encodings import encode_position_sequences
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
    parser = argparse.ArgumentParser(description="Run position-base joint encoding baselines.")
    parser.add_argument("--input", default=str(PROJECT_ROOT / "data" / "toy_reads" / "toy_order_position.csv"))
    parser.add_argument("--output-dir", default=str(PROJECT_ROOT / "results" / "runs" / "position_encoding_order_position"))
    parser.add_argument("--lengths", default="69,75,100")
    parser.add_argument("--length-column", default="source_length", choices=["length", "source_length"])
    parser.add_argument("--conditions", default="clean,substitution_1pct,N_3pct,reverse_complement")
    parser.add_argument(
        "--schemes",
        default="base_property,joint_phase_prior,joint_phase_learnable_proxy,joint_phase_prior_residual,gated_pe_gc,gated_pe_hydrogen,gated_pe_multi,gated_pe_learnable_proxy,rope_property,rope_onehot,kmer_property",
    )
    parser.add_argument("--poolings", default="flatten,mean_std,fft")
    parser.add_argument("--dim", type=int, default=16)
    parser.add_argument("--k-values", default="3,5,7")
    parser.add_argument("--classifiers", default="nearest_centroid,knn_3,linear_svm,logistic_regression")
    parser.add_argument("--seed", type=int, default=13)
    args = parser.parse_args()

    df = load_dataset(args.input)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    lengths = parse_int_list(args.lengths)
    conditions = parse_csv_list(args.conditions)
    schemes = parse_csv_list(args.schemes)
    poolings = parse_csv_list(args.poolings)
    k_values = parse_int_list(args.k_values)
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
            for scheme in schemes:
                scheme_k_values = k_values if scheme == "kmer_property" else [0]
                for k in scheme_k_values:
                    for pooling in poolings:
                        try:
                            x = encode_position_sequences(
                                sequences,
                                scheme=scheme,
                                length=length,
                                dim=args.dim,
                                pooling=pooling,
                                k=max(1, k),
                            )
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
                                    "scheme": scheme,
                                    "pooling": pooling,
                                    "dim": args.dim,
                                    "k": k,
                                    "n_samples": int(len(subset)),
                                    "n_features": int(x.shape[1]),
                                    "classifiers": classifiers,
                                }
                            )
                        except Exception as exc:
                            rows.append(
                                {
                                    "length": length,
                                    "condition": condition,
                                    "scheme": scheme,
                                    "pooling": pooling,
                                    "k": k,
                                    "error": f"{type(exc).__name__}: {exc}",
                                }
                            )

    write_json(output_dir / "position_encoding_results.json", {"elapsed_seconds": time.time() - started, "results": rows})
    flat_rows = []
    for row in rows:
        for clf_name, clf_result in row.get("classifiers", {}).items():
            flat_rows.append(
                {
                    "length": row.get("length"),
                    "condition": row.get("condition"),
                    "scheme": row.get("scheme"),
                    "pooling": row.get("pooling"),
                    "dim": row.get("dim"),
                    "k": row.get("k"),
                    "classifier": clf_name,
                    "accuracy": clf_result.get("accuracy") if isinstance(clf_result, dict) else None,
                    "macro_f1": clf_result.get("macro_f1") if isinstance(clf_result, dict) else None,
                    "n_features": row.get("n_features"),
                }
            )
    flat = pd.DataFrame(flat_rows)
    flat.to_csv(output_dir / "position_encoding_results_flat.csv", index=False, encoding="utf-8-sig")
    if not flat.empty:
        flat.sort_values(["macro_f1", "accuracy"], ascending=False).head(50).to_csv(
            output_dir / "position_encoding_top50.csv", index=False, encoding="utf-8-sig"
        )
    print(f"Wrote {len(rows)} position encoding rows to {output_dir}")


if __name__ == "__main__":
    main()
