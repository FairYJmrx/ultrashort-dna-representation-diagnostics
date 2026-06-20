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
from src.sklearn_features import load_dataset
from src.token_audit import (
    apply_ablation,
    build_token_vocab,
    token_bag_matrix,
    token_numeric_summary,
    token_transition_matrix,
    tokenize_to_ids,
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
    parser = argparse.ArgumentParser(description="Audit ordered k-mer token information.")
    parser.add_argument("--input", default=str(PROJECT_ROOT / "data" / "toy_reads" / "toy_reads.csv"))
    parser.add_argument("--output-dir", default=str(PROJECT_ROOT / "results" / "runs" / "token_audit_smoke"))
    parser.add_argument("--lengths", default="69,75,100,150,200")
    parser.add_argument("--length-column", default="source_length", choices=["length", "source_length"])
    parser.add_argument("--conditions", default="clean,substitution_1pct,N_3pct,trim_to_69,reverse_complement")
    parser.add_argument("--k-values", default="3,5,7,9,12")
    parser.add_argument("--features", default="bag,transition,numeric_summary")
    parser.add_argument("--ablations", default="none,token_shuffle,position_shuffle,token_id_permutation")
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
    features = parse_csv_list(args.features)
    ablations = parse_csv_list(args.ablations)
    classifier_names = parse_csv_list(args.classifiers)
    length_column = args.length_column if args.length_column in df.columns else "length"
    rows: list[dict[str, object]] = []
    started = time.time()

    for length in lengths:
        for condition in conditions:
            subset = df[(df[length_column] == length) & (df["condition"] == condition)].copy()
            if subset.empty or subset["label"].nunique() < 2:
                continue
            sequences = subset["sequence"].tolist()
            labels = subset["label"].tolist()
            train_idx, test_idx = make_split(labels, seed=args.seed)
            for k in k_values:
                if length < k:
                    continue
                train_sequences = [sequences[i] for i in train_idx]
                vocab = build_token_vocab(train_sequences, k=k, canonical=args.canonical)
                token_ids = tokenize_to_ids(sequences, k=k, vocab=vocab, canonical=args.canonical)
                for ablation in ablations:
                    ablated = apply_ablation(token_ids, ablation, seed=args.seed)
                    for feature in features:
                        try:
                            if feature == "bag":
                                x = token_bag_matrix(ablated, vocab_size=len(vocab))
                            elif feature == "transition":
                                x = token_transition_matrix(ablated, vocab_size=len(vocab))
                            elif feature == "numeric_summary":
                                x = token_numeric_summary(ablated)
                            else:
                                raise ValueError(f"Unsupported feature: {feature}")
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
                                    "k": k,
                                    "canonical": args.canonical,
                                    "ablation": ablation,
                                    "feature": feature,
                                    "vocab_size": len(vocab),
                                    "n_samples": int(len(subset)),
                                    "classifiers": classifiers,
                                }
                            )
                        except Exception as exc:
                            rows.append(
                                {
                                    "length": length,
                                    "condition": condition,
                                    "k": k,
                                    "ablation": ablation,
                                    "feature": feature,
                                    "error": f"{type(exc).__name__}: {exc}",
                                }
                            )

    write_json(output_dir / "token_audit_results.json", {"elapsed_seconds": time.time() - started, "results": rows})
    flat_rows = []
    for row in rows:
        for clf_name, clf_result in row.get("classifiers", {}).items():
            flat_rows.append(
                {
                    "length": row.get("length"),
                    "condition": row.get("condition"),
                    "k": row.get("k"),
                    "ablation": row.get("ablation"),
                    "feature": row.get("feature"),
                    "classifier": clf_name,
                    "accuracy": clf_result.get("accuracy") if isinstance(clf_result, dict) else None,
                    "macro_f1": clf_result.get("macro_f1") if isinstance(clf_result, dict) else None,
                    "vocab_size": row.get("vocab_size"),
                }
            )
    flat = pd.DataFrame(flat_rows)
    flat.to_csv(output_dir / "token_audit_results_flat.csv", index=False, encoding="utf-8-sig")
    if not flat.empty:
        flat.sort_values(["macro_f1", "accuracy"], ascending=False).head(30).to_csv(
            output_dir / "token_audit_top30.csv", index=False, encoding="utf-8-sig"
        )
    print(f"Wrote {len(rows)} token audit rows to {output_dir}")


if __name__ == "__main__":
    main()
