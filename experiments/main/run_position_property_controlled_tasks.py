from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score
from sklearn.model_selection import StratifiedKFold, train_test_split
from sklearn.neighbors import NearestCentroid
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import LabelEncoder, StandardScaler

def _find_project_root(start: Path) -> Path:
    for candidate in [start.parent, *start.parents]:
        if (candidate / "methods").is_dir() and (candidate / "configs").is_dir():
            return candidate
    raise RuntimeError("Could not locate the release repository root.")


PROJECT_ROOT = _find_project_root(Path(__file__).resolve())
sys.path.insert(0, str(PROJECT_ROOT))

from src.stage2_features import build_feature_matrix  # noqa: E402


def parse_csv_list(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


def parse_int_list(value: str) -> list[int]:
    return [int(item.strip()) for item in value.split(",") if item.strip()]


def classifier_registry(seed: int) -> dict[str, object]:
    return {
        "nearest_centroid": NearestCentroid(),
        "logistic": make_pipeline(StandardScaler(), LogisticRegression(max_iter=5000, random_state=seed)),
    }


def task_labels(task: str, labels: list[str]) -> list[str]:
    if task == "same_spectrum_order":
        return ["same_spectrum_A", "same_spectrum_B"]
    if task == "motif_jitter_position":
        return ["motif_jitter_front", "motif_jitter_middle", "motif_jitter_back"]
    if task == "all_labels":
        return sorted(labels)
    raise ValueError(f"Unsupported task: {task}")


def eval_split(
    x: np.ndarray,
    y: np.ndarray,
    train_idx: np.ndarray,
    test_idx: np.ndarray,
    classifiers: dict[str, object],
    split_name: str,
) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for clf_name, clf in classifiers.items():
        try:
            clf.fit(x[train_idx], y[train_idx])
            pred = clf.predict(x[test_idx])
            rows.append(
                {
                    "split": split_name,
                    "classifier": clf_name,
                    "accuracy": float(accuracy_score(y[test_idx], pred)),
                    "macro_f1": float(f1_score(y[test_idx], pred, average="macro", zero_division=0)),
                }
            )
        except Exception as exc:
            rows.append({"split": split_name, "classifier": clf_name, "error": f"{type(exc).__name__}: {exc}"})
    return rows


def evaluate_subset(
    sequences: list[str],
    labels: list[str],
    representation: str,
    length: int,
    classifier_names: list[str],
    seed: int,
    cv_folds: int,
) -> list[dict[str, object]]:
    encoder = LabelEncoder()
    y = encoder.fit_transform(labels)
    unique, counts = np.unique(y, return_counts=True)
    if len(unique) < 2 or np.min(counts) < 2:
        return [{"error": "need at least two classes and two samples per class"}]
    classifiers = classifier_registry(seed)
    classifiers = {name: classifiers[name] for name in classifier_names}
    train_idx, test_idx = train_test_split(
        np.arange(len(y)),
        test_size=0.3,
        random_state=seed,
        stratify=y,
    )
    x, info = build_feature_matrix(sequences, representation, length=length, train_indices=train_idx.tolist())
    rows = eval_split(x, y, train_idx, test_idx, classifiers, "holdout")
    for row in rows:
        row["n_features"] = info.n_features
    if cv_folds > 1 and np.min(counts) >= cv_folds:
        skf = StratifiedKFold(n_splits=cv_folds, shuffle=True, random_state=seed)
        for clf_name in classifier_names:
            scores_acc: list[float] = []
            scores_f1: list[float] = []
            feature_counts: list[int] = []
            for cv_train, cv_test in skf.split(np.arange(len(y)), y):
                x_cv, info_cv = build_feature_matrix(sequences, representation, length=length, train_indices=cv_train.tolist())
                clf = classifier_registry(seed)[clf_name]
                clf.fit(x_cv[cv_train], y[cv_train])
                pred = clf.predict(x_cv[cv_test])
                scores_acc.append(float(accuracy_score(y[cv_test], pred)))
                scores_f1.append(float(f1_score(y[cv_test], pred, average="macro", zero_division=0)))
                feature_counts.append(info_cv.n_features)
            rows.append(
                {
                    "split": f"{cv_folds}fold_cv",
                    "classifier": clf_name,
                    "accuracy": float(np.mean(scores_acc)),
                    "macro_f1": float(np.mean(scores_f1)),
                    "accuracy_std": float(np.std(scores_acc)),
                    "macro_f1_std": float(np.std(scores_f1)),
                    "n_features": int(round(float(np.mean(feature_counts)))) if feature_counts else info.n_features,
                }
            )
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description="Run controlled tasks for compact position-aware biochemical features.")
    parser.add_argument("--input", default=str(PROJECT_ROOT / "data" / "toy_reads" / "toy_hardened_tasks.csv"))
    parser.add_argument("--output-dir", default=str(PROJECT_ROOT / "results" / "stage3" / "position_property_controlled_tasks"))
    parser.add_argument("--representations", default="ckmer4_count_l2,ckmer4_property_l2,ck4p_msp,ckmer4_property_moment_l2,ckmer4_property_multiscale_l2,ckmer4_property_anchor_l2,cspaced_property_l2,property_channels,rope_property")
    parser.add_argument("--lengths", default="69,75,100")
    parser.add_argument("--conditions", default="clean,substitution_1pct,N_3pct,N_cluster_5pct,reverse_complement")
    parser.add_argument("--tasks", default="same_spectrum_order,motif_jitter_position")
    parser.add_argument("--classifiers", default="nearest_centroid,logistic")
    parser.add_argument("--cv-folds", type=int, default=5)
    parser.add_argument("--seed", type=int, default=1001)
    args = parser.parse_args()

    started = time.time()
    df = pd.read_csv(args.input)
    df["source_length"] = df["source_length"].astype(int)
    df["sequence"] = df["sequence"].astype(str).str.upper()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    reps = parse_csv_list(args.representations)
    lengths = parse_int_list(args.lengths)
    conditions = parse_csv_list(args.conditions)
    tasks = parse_csv_list(args.tasks)
    classifiers = parse_csv_list(args.classifiers)
    rows: list[dict[str, object]] = []

    all_labels = sorted(df["label"].dropna().astype(str).unique().tolist())
    for task in tasks:
        labels_keep = task_labels(task, all_labels)
        for length in lengths:
            for condition in conditions:
                subset = df[(df["source_length"] == length) & (df["condition"] == condition)].copy()
                subset = subset[subset["label"].astype(str).isin(labels_keep)]
                if subset.empty or subset["label"].nunique() < 2:
                    rows.append({"task": task, "length": length, "condition": condition, "error": "empty or single-class subset"})
                    continue
                sequences = subset["sequence"].tolist()
                labels = subset["label"].astype(str).tolist()
                for rep in reps:
                    eval_rows = evaluate_subset(
                        sequences=sequences,
                        labels=labels,
                        representation=rep,
                        length=length,
                        classifier_names=classifiers,
                        seed=args.seed,
                        cv_folds=args.cv_folds,
                    )
                    for row in eval_rows:
                        row.update(
                            {
                                "task": task,
                                "length": length,
                                "condition": condition,
                                "representation": rep,
                                "n_samples": int(len(subset)),
                                "n_classes": int(subset["label"].nunique()),
                            }
                        )
                        rows.append(row)

    result = pd.DataFrame(rows)
    result.to_csv(output_dir / "position_property_controlled_results.csv", index=False, encoding="utf-8-sig")
    (output_dir / "position_property_controlled_run.json").write_text(
        json.dumps(
            {
                "elapsed_seconds": time.time() - started,
                "input": args.input,
                "representations": reps,
                "lengths": lengths,
                "conditions": conditions,
                "tasks": tasks,
                "classifiers": classifiers,
                "cv_folds": args.cv_folds,
                "n_rows": int(len(result)),
            },
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    print(f"Wrote {len(result)} controlled-task rows to {output_dir}")


if __name__ == "__main__":
    main()

