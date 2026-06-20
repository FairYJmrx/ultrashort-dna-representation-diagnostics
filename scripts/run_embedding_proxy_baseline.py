from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.decomposition import TruncatedSVD
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import accuracy_score, f1_score

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.ml_eval import evaluate_classifiers, make_split
from src.sklearn_features import load_dataset
from src.token_audit import build_token_vocab, token_bag_matrix, tokenize_to_ids


def parse_csv_list(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


def parse_int_list(value: str) -> list[int]:
    return [int(item.strip()) for item in value.split(",") if item.strip()]


def write_json(path: Path, obj: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fh:
        json.dump(obj, fh, indent=2, ensure_ascii=False, sort_keys=True)


def random_embedding_pool(token_ids: list[list[int]], vocab_size: int, dim: int, seed: int) -> np.ndarray:
    rng = np.random.default_rng(seed)
    emb = rng.normal(0, 1.0 / np.sqrt(dim), size=(vocab_size + 1, dim))
    rows = []
    for tokens in token_ids:
        if not tokens:
            rows.append(np.zeros(dim * 2, dtype=np.float64))
            continue
        arr = emb[np.asarray(tokens, dtype=np.int64)]
        rows.append(np.concatenate([arr.mean(axis=0), arr.std(axis=0)]))
    return np.vstack(rows)


def svd_embedding_pool(token_ids: list[list[int]], train_idx: list[int], vocab_size: int, dim: int, seed: int) -> np.ndarray:
    bag = token_bag_matrix(token_ids, vocab_size=vocab_size)
    max_dim = min(dim, max(2, bag.shape[1] - 1), max(2, len(train_idx) - 1))
    svd = TruncatedSVD(n_components=max_dim, random_state=seed)
    svd.fit(bag[train_idx])
    return svd.transform(bag)


def evaluate_mlp(x: np.ndarray, labels: list[str], train_idx: list[int], test_idx: list[int], seed: int) -> dict[str, float | str]:
    y = np.asarray(labels)
    try:
        clf = MLPClassifier(hidden_layer_sizes=(32,), activation="relu", max_iter=500, random_state=seed, early_stopping=True)
        clf.fit(x[train_idx], y[train_idx])
        pred = clf.predict(x[test_idx])
        return {
            "accuracy": float(accuracy_score(y[test_idx], pred)),
            "macro_f1": float(f1_score(y[test_idx], pred, average="macro", zero_division=0)),
        }
    except Exception as exc:
        return {"error": f"{type(exc).__name__}: {exc}"}


def main() -> None:
    parser = argparse.ArgumentParser(description="Run ordinary k-mer embedding proxy baselines.")
    parser.add_argument("--input", default=str(PROJECT_ROOT / "data" / "toy_reads" / "toy_order_position.csv"))
    parser.add_argument("--output-dir", default=str(PROJECT_ROOT / "results" / "runs" / "embedding_proxy_order_position"))
    parser.add_argument("--lengths", default="69,75,100")
    parser.add_argument("--length-column", default="source_length", choices=["length", "source_length"])
    parser.add_argument("--conditions", default="clean,substitution_1pct,N_3pct,reverse_complement")
    parser.add_argument("--k-values", default="3,5,7")
    parser.add_argument("--dims", default="16,32,64")
    parser.add_argument("--seed", type=int, default=13)
    args = parser.parse_args()

    df = load_dataset(args.input)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    lengths = parse_int_list(args.lengths)
    conditions = parse_csv_list(args.conditions)
    k_values = parse_int_list(args.k_values)
    dims = parse_int_list(args.dims)
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
            train_sequences = [sequences[i] for i in train_idx]
            for k in k_values:
                if length < k:
                    continue
                vocab = build_token_vocab(train_sequences, k=k, canonical=False)
                token_ids = tokenize_to_ids(sequences, k=k, vocab=vocab, canonical=False)
                for dim in dims:
                    for method in ["random_embedding_mean_std", "svd_bag_embedding"]:
                        if method == "random_embedding_mean_std":
                            x = random_embedding_pool(token_ids, len(vocab), dim, seed=args.seed)
                        else:
                            x = svd_embedding_pool(token_ids, train_idx, len(vocab), dim, seed=args.seed)
                        classifiers = evaluate_classifiers(
                            x,
                            labels,
                            train_idx,
                            test_idx,
                            seed=args.seed,
                            classifier_names=["nearest_centroid", "knn_3", "linear_svm"],
                        )
                        classifiers["mlp_32"] = evaluate_mlp(x, labels, train_idx, test_idx, seed=args.seed)
                        rows.append(
                            {
                                "length": length,
                                "condition": condition,
                                "k": k,
                                "dim": dim,
                                "method": method,
                                "vocab_size": len(vocab),
                                "n_features": int(x.shape[1]),
                                "classifiers": classifiers,
                            }
                        )

    write_json(output_dir / "embedding_proxy_results.json", {"elapsed_seconds": time.time() - started, "results": rows})
    flat_rows = []
    for row in rows:
        for clf_name, clf_result in row.get("classifiers", {}).items():
            flat_rows.append(
                {
                    "length": row.get("length"),
                    "condition": row.get("condition"),
                    "k": row.get("k"),
                    "dim": row.get("dim"),
                    "method": row.get("method"),
                    "classifier": clf_name,
                    "accuracy": clf_result.get("accuracy") if isinstance(clf_result, dict) else None,
                    "macro_f1": clf_result.get("macro_f1") if isinstance(clf_result, dict) else None,
                    "vocab_size": row.get("vocab_size"),
                    "n_features": row.get("n_features"),
                }
            )
    flat = pd.DataFrame(flat_rows)
    flat.to_csv(output_dir / "embedding_proxy_results_flat.csv", index=False, encoding="utf-8-sig")
    if not flat.empty:
        flat.sort_values(["macro_f1", "accuracy"], ascending=False).head(50).to_csv(
            output_dir / "embedding_proxy_top50.csv", index=False, encoding="utf-8-sig"
        )
    print(f"Wrote {len(rows)} embedding proxy rows to {output_dir}")


if __name__ == "__main__":
    main()
