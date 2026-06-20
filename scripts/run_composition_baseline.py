from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.ml_eval import evaluate_classifiers, make_split
from src.sklearn_features import (
    build_kmer_matrix,
    load_dataset,
    maybe_reduce_svd,
    profile_duplicate_rate,
    sparsity_report,
    transform_feature_matrix,
)


def parse_csv_list(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


def parse_int_list(value: str) -> list[int]:
    return [int(item.strip()) for item in value.split(",") if item.strip()]


def write_json(path: Path, obj: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fh:
        json.dump(obj, fh, indent=2, ensure_ascii=False, sort_keys=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run lightweight k-mer composition baselines.")
    parser.add_argument("--input", default=str(PROJECT_ROOT / "data" / "toy_reads" / "toy_reads.csv"))
    parser.add_argument("--output-dir", default=str(PROJECT_ROOT / "results" / "runs" / "composition_first_wave"))
    parser.add_argument("--lengths", default="69,75,100,150,200")
    parser.add_argument("--length-column", default="source_length", choices=["length", "source_length"])
    parser.add_argument("--conditions", default="clean,substitution_1pct,N_3pct,trim_to_69,reverse_complement")
    parser.add_argument("--k-values", default="2,3,4,5,6,7,8,10,12")
    parser.add_argument("--feature-types", default="count,relative_frequency,tfidf")
    parser.add_argument("--normalizations", default="none,l2")
    parser.add_argument("--svd-components", default="0,16,64")
    parser.add_argument("--canonical", action="store_true")
    parser.add_argument("--classifiers", default="nearest_centroid,knn_3,linear_svm,logistic_regression")
    parser.add_argument("--seed", type=int, default=13)
    args = parser.parse_args()

    df = load_dataset(args.input)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    lengths = parse_int_list(args.lengths)
    conditions = parse_csv_list(args.conditions)
    k_values = parse_int_list(args.k_values)
    feature_types = parse_csv_list(args.feature_types)
    normalizations = parse_csv_list(args.normalizations)
    svd_components = parse_int_list(args.svd_components)
    classifier_names = parse_csv_list(args.classifiers)

    results: list[dict[str, object]] = []
    started = time.time()
    length_column = args.length_column if args.length_column in df.columns else "length"

    for length in lengths:
        for condition in conditions:
            subset = df[(df[length_column] == length) & (df["condition"] == condition)].copy()
            if subset.empty or subset["label"].nunique() < 2:
                continue
            labels = subset["label"].tolist()
            train_idx, test_idx = make_split(labels, seed=args.seed)
            sequences = subset["sequence"].tolist()
            for k in k_values:
                if length < k:
                    continue
                count_matrix, vocab = build_kmer_matrix(sequences, k=k, canonical=args.canonical)
                base_diag = sparsity_report(count_matrix)
                base_diag["profile_duplicate_rate"] = profile_duplicate_rate(count_matrix)
                for feature_type in feature_types:
                    for normalization in normalizations:
                        try:
                            feature_matrix, feature_info = transform_feature_matrix(
                                count_matrix,
                                feature_type=feature_type,
                                normalization=normalization,
                                train_indices=train_idx,
                            )
                        except Exception as exc:
                            results.append(
                                {
                                    "length": length,
                                    "length_column": length_column,
                                    "condition": condition,
                                    "k": k,
                                    "feature_type": feature_type,
                                    "normalization": normalization,
                                    "error": f"{type(exc).__name__}: {exc}",
                                }
                            )
                            continue
                        for n_comp in svd_components:
                            reduced, reducer_info = maybe_reduce_svd(feature_matrix, n_comp, train_idx, args.seed)
                            classifiers = evaluate_classifiers(
                                reduced,
                                labels,
                                train_idx,
                                test_idx,
                                seed=args.seed,
                                classifier_names=classifier_names,
                            )
                            row = {
                                "length": length,
                                "length_column": length_column,
                                "condition": condition,
                                "k": k,
                                "canonical": args.canonical,
                                "feature_type": feature_type,
                                "normalization": normalization,
                                "svd_components": n_comp,
                                "n_samples": int(len(subset)),
                                "n_classes": int(subset["label"].nunique()),
                                "feature_info": feature_info,
                                "reducer_info": reducer_info,
                                "diagnostics": base_diag,
                                "classifiers": classifiers,
                            }
                            results.append(row)

    summary_path = output_dir / "composition_results.json"
    write_json(summary_path, {"elapsed_seconds": time.time() - started, "results": results})

    flat_rows: list[dict[str, object]] = []
    for row in results:
        for clf_name, clf_result in row.get("classifiers", {}).items():
            flat_rows.append(
                {
                    "length": row.get("length"),
                    "length_column": row.get("length_column"),
                    "condition": row.get("condition"),
                    "k": row.get("k"),
                    "feature_type": row.get("feature_type"),
                    "normalization": row.get("normalization"),
                    "svd_components": row.get("svd_components"),
                    "classifier": clf_name,
                    "accuracy": clf_result.get("accuracy") if isinstance(clf_result, dict) else None,
                    "macro_f1": clf_result.get("macro_f1") if isinstance(clf_result, dict) else None,
                    "density": row.get("diagnostics", {}).get("density"),
                    "avg_nnz_per_read": row.get("diagnostics", {}).get("avg_nnz_per_read"),
                    "duplicate_rate": row.get("diagnostics", {}).get("profile_duplicate_rate"),
                    "explained_variance": row.get("reducer_info", {}).get("explained_variance_ratio_sum"),
                }
            )
    try:
        import pandas as pd

        flat = pd.DataFrame(flat_rows)
        flat.to_csv(output_dir / "composition_results_flat.csv", index=False, encoding="utf-8-sig")
        if not flat.empty:
            best = flat.sort_values(["macro_f1", "accuracy"], ascending=False).head(30)
            best.to_csv(output_dir / "composition_top30.csv", index=False, encoding="utf-8-sig")
    except Exception:
        pass

    print(f"Wrote {len(results)} experiment rows to {summary_path}")


if __name__ == "__main__":
    main()
