from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import sparse
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score
from sklearn.model_selection import StratifiedKFold, train_test_split
from sklearn.neighbors import KNeighborsClassifier, NearestCentroid
from sklearn.neural_network import MLPClassifier
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.svm import LinearSVC

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.representation_registry import build_representation, parse_kmer_representation
from src.sklearn_features import build_kmer_matrix, transform_feature_matrix
from src.spaced_features import spaced_count_dense


def parse_csv_list(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


def parse_int_list(value: str) -> list[int]:
    return [int(item.strip()) for item in value.split(",") if item.strip()]


def parse_str_list(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


def classifier_registry(seed: int) -> dict[str, object]:
    return {
        "nearest_centroid": NearestCentroid(),
        "knn_3": KNeighborsClassifier(n_neighbors=3),
        "linear_svm": make_pipeline(StandardScaler(), LinearSVC(C=1.0, random_state=seed, max_iter=5000)),
        "logistic_regression": make_pipeline(StandardScaler(), LogisticRegression(max_iter=5000, random_state=seed)),
        "mlp_small": make_pipeline(
            StandardScaler(),
            MLPClassifier(
                hidden_layer_sizes=(32,),
                activation="relu",
                alpha=1e-3,
                learning_rate_init=1e-3,
                max_iter=500,
                early_stopping=True,
                random_state=seed,
            ),
        ),
    }


def build_representation_matrix(
    sequences: list[str],
    representation: str,
    length: int,
    train_indices: list[int],
) -> np.ndarray:
    """Build feature matrix with train-only vocabulary/IDF when applicable."""
    parsed = parse_kmer_representation(representation)
    if parsed:
        k, feature_type, normalization, canonical = parsed
        train_sequences = [sequences[i] for i in train_indices]
        _, vocabulary = build_kmer_matrix(train_sequences, k=k, canonical=canonical, vocabulary_mode="observed")
        mat, _ = build_kmer_matrix(sequences, k=k, canonical=canonical, vocabulary=vocabulary)
        feat, _ = transform_feature_matrix(
            mat,
            feature_type=feature_type,
            normalization=normalization,
            train_indices=train_indices,
        )
        return feat.toarray() if sparse.issparse(feat) else np.asarray(feat)
    if representation in {"spaced_count_l2", "cspaced_count_l2", "cspaced_property_l2"}:
        canonical = representation.startswith("cs")
        add_property = representation == "cspaced_property_l2"
        return spaced_count_dense(sequences, canonical=canonical, train_indices=train_indices, add_property_summary=add_property)
    return build_representation(sequences, representation, length=length, train_indices=train_indices)


def evaluate_holdout(
    sequences: list[str],
    representation: str,
    length: int,
    labels: np.ndarray,
    classifier_names: list[str],
    seed: int,
) -> list[dict[str, object]]:
    unique, counts = np.unique(labels, return_counts=True)
    if len(unique) < 2 or np.min(counts) < 2:
        return [{"error": "need at least two classes and two samples per class"}]
    train_idx, test_idx = train_test_split(
        np.arange(len(labels)),
        test_size=0.3,
        random_state=seed,
        stratify=labels,
    )
    x = build_representation_matrix(sequences, representation, length, train_idx.tolist())
    rows: list[dict[str, object]] = []
    classifiers = classifier_registry(seed)
    for clf_name in classifier_names:
        clf = classifiers[clf_name]
        try:
            clf.fit(x[train_idx], labels[train_idx])
            pred = clf.predict(x[test_idx])
            rows.append(
                {
                    "split": "holdout",
                    "classifier": clf_name,
                    "accuracy": float(accuracy_score(labels[test_idx], pred)),
                    "macro_f1": float(f1_score(labels[test_idx], pred, average="macro", zero_division=0)),
                    "n_features": int(x.shape[1]),
                }
            )
        except Exception as exc:
            rows.append({"split": "holdout", "classifier": clf_name, "error": f"{type(exc).__name__}: {exc}"})
    return rows


def evaluate_cv(
    sequences: list[str],
    representation: str,
    length: int,
    labels: np.ndarray,
    classifier_names: list[str],
    seed: int,
    folds: int,
) -> list[dict[str, object]]:
    unique, counts = np.unique(labels, return_counts=True)
    if len(unique) < 2 or np.min(counts) < folds:
        return [{"error": "not enough samples for stratified CV"}]
    skf = StratifiedKFold(n_splits=folds, shuffle=True, random_state=seed)
    rows: list[dict[str, object]] = []
    classifiers = classifier_registry(seed)
    for clf_name in classifier_names:
        scores_acc: list[float] = []
        scores_f1: list[float] = []
        feature_counts: list[int] = []
        try:
            indices = np.arange(len(labels))
            for train_idx, test_idx in skf.split(indices, labels):
                x = build_representation_matrix(sequences, representation, length, train_idx.tolist())
                feature_counts.append(int(x.shape[1]))
                clf = classifiers[clf_name]
                clf.fit(x[train_idx], labels[train_idx])
                pred = clf.predict(x[test_idx])
                scores_acc.append(float(accuracy_score(labels[test_idx], pred)))
                scores_f1.append(float(f1_score(labels[test_idx], pred, average="macro", zero_division=0)))
            rows.append(
                {
                    "split": f"{folds}fold_cv",
                    "classifier": clf_name,
                    "accuracy": float(np.mean(scores_acc)),
                    "macro_f1": float(np.mean(scores_f1)),
                    "accuracy_std": float(np.std(scores_acc)),
                    "macro_f1_std": float(np.std(scores_f1)),
                    "n_features": int(round(float(np.mean(feature_counts)))) if feature_counts else None,
                }
            )
        except Exception as exc:
            rows.append({"split": f"{folds}fold_cv", "classifier": clf_name, "error": f"{type(exc).__name__}: {exc}"})
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description="Run representation classification experiments.")
    parser.add_argument("--input", default="data/toy_reads/toy_hardened_tasks.csv")
    parser.add_argument("--output-dir", default="results/runs/representation_classification")
    parser.add_argument("--representations", default="kmer5_count_l2,ckmer5_count_l2,kmer7_tfidf_l2,ckmer7_tfidf_l2,one_hot,property_channels,spaced_kmer_phase,codon_frame_channels,rope_property,cspaced_count_l2,cspaced_property_l2")
    parser.add_argument("--lengths", default="75")
    parser.add_argument("--conditions", default="clean,N_3pct,N_cluster_5pct")
    parser.add_argument("--tasks", default="same_spectrum_order,motif_jitter_position")
    parser.add_argument("--classifiers", default="nearest_centroid,knn_3,logistic_regression,mlp_small")
    parser.add_argument("--group-col", default="", help="Optional column used to split tasks into independent subgroups.")
    parser.add_argument("--groups", default="", help="Comma-separated group values to keep when --group-col is set.")
    parser.add_argument("--label-col", default="label", help="Column used as the supervised label.")
    parser.add_argument("--cv-folds", type=int, default=0)
    parser.add_argument("--seed", type=int, default=13)
    args = parser.parse_args()

    df = pd.read_csv(args.input)
    df["source_length"] = df["source_length"].astype(int)
    tasks = {
        "same_spectrum_order": ["same_spectrum_A", "same_spectrum_B"],
        "motif_jitter_position": ["motif_jitter_front", "motif_jitter_middle", "motif_jitter_back"],
        "template_species": ["GC_rich", "AT_rich", "near_SNP", "host_like"],
        "real_genome_slice": sorted(df["label"].unique().tolist()),
        "all_labels": sorted(df[args.label_col].dropna().astype(str).unique().tolist()),
    }
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, object]] = []
    started = time.time()
    group_col = args.group_col.strip()
    requested_groups = parse_str_list(args.groups)
    if group_col:
        if group_col not in df.columns:
            raise ValueError(f"Missing --group-col column: {group_col}")
        available_groups = sorted(df[group_col].dropna().astype(str).unique().tolist())
        group_values = requested_groups or available_groups
    else:
        group_values = [""]

    if args.label_col not in df.columns:
        raise ValueError(f"Missing --label-col column: {args.label_col}")

    for task in parse_csv_list(args.tasks):
        labels_keep = tasks.get(task)
        if not labels_keep:
            raise ValueError(f"Unknown task: {task}")
        for length in parse_int_list(args.lengths):
            for condition in parse_csv_list(args.conditions):
                for group_value in group_values:
                    subset = df[(df["source_length"] == length) & (df["condition"] == condition)].copy()
                    if group_col:
                        subset = subset[subset[group_col].astype(str) == group_value]
                    subset = subset[subset[args.label_col].astype(str).isin(labels_keep)]
                    if subset.empty or subset[args.label_col].nunique() < 2:
                        rows.append(
                            {
                                "task": task,
                                "group_col": group_col,
                                "group": group_value,
                                "length": length,
                                "condition": condition,
                                "error": "empty or single-class subset",
                            }
                        )
                        continue
                    encoder = LabelEncoder()
                    y = encoder.fit_transform(subset[args.label_col].astype(str).to_numpy())
                    sequences = subset["sequence"].tolist()
                    for rep in parse_csv_list(args.representations):
                        try:
                            eval_rows = evaluate_holdout(sequences, rep, length, y, parse_csv_list(args.classifiers), args.seed)
                            if args.cv_folds and args.cv_folds > 1:
                                eval_rows.extend(evaluate_cv(sequences, rep, length, y, parse_csv_list(args.classifiers), args.seed, args.cv_folds))
                            for row in eval_rows:
                                row.update(
                                    {
                                        "task": task,
                                        "group_col": group_col,
                                        "group": group_value,
                                        "label_col": args.label_col,
                                        "length": length,
                                        "condition": condition,
                                        "representation": rep,
                                        "n_samples": int(len(subset)),
                                        "n_classes": int(subset[args.label_col].nunique()),
                                    }
                                )
                                rows.append(row)
                        except Exception as exc:
                            rows.append(
                                {
                                    "task": task,
                                    "group_col": group_col,
                                    "group": group_value,
                                    "label_col": args.label_col,
                                    "length": length,
                                    "condition": condition,
                                    "representation": rep,
                                    "error": f"{type(exc).__name__}: {exc}",
                                }
                            )

    payload = {"elapsed_seconds": time.time() - started, "results": rows}
    (output_dir / "classification_results.json").write_text(json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True), encoding="utf-8")
    pd.DataFrame(rows).to_csv(output_dir / "classification_results.csv", index=False, encoding="utf-8-sig")
    print(f"Wrote {len(rows)} classification rows to {output_dir}")


if __name__ == "__main__":
    main()
