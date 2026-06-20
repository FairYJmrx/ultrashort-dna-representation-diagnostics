"""scikit-learn evaluation helpers for lightweight baselines."""

from __future__ import annotations

import numpy as np
import warnings
from scipy import sparse
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, f1_score
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier, NearestCentroid
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import LinearSVC


def make_split(labels: list[str], seed: int = 13, test_size: float = 0.3) -> tuple[list[int], list[int]]:
    indices = np.arange(len(labels))
    unique, counts = np.unique(labels, return_counts=True)
    stratify = labels if len(unique) > 1 and np.min(counts) >= 2 else None
    train_idx, test_idx = train_test_split(indices, test_size=test_size, random_state=seed, stratify=stratify)
    return train_idx.tolist(), test_idx.tolist()


def subset_matrix(x, indices: list[int]):
    return x[indices]


def evaluate_classifiers(
    x,
    labels: list[str],
    train_idx: list[int],
    test_idx: list[int],
    seed: int = 13,
    classifier_names: list[str] | None = None,
) -> dict[str, object]:
    y = np.asarray(labels)
    results: dict[str, object] = {}

    classifiers = {
        "nearest_centroid": NearestCentroid(),
        "knn_3": KNeighborsClassifier(n_neighbors=min(3, max(1, len(train_idx)))),
        "linear_svm": LinearSVC(C=1.0, random_state=seed, max_iter=5000),
        "logistic_regression": LogisticRegression(max_iter=5000, random_state=seed, n_jobs=None),
    }
    if classifier_names:
        classifiers = {name: clf for name, clf in classifiers.items() if name in set(classifier_names)}

    for name, clf in classifiers.items():
        try:
            model = clf
            x_train = subset_matrix(x, train_idx)
            x_test = subset_matrix(x, test_idx)
            if name in {"linear_svm", "logistic_regression"} and not sparse.issparse(x):
                model = make_pipeline(StandardScaler(), clf)
            with warnings.catch_warnings():
                warnings.filterwarnings("ignore", category=UserWarning)
                warnings.filterwarnings("ignore", category=RuntimeWarning)
                model.fit(x_train, y[train_idx])
                pred = model.predict(x_test)
            results[name] = {
                "accuracy": float(accuracy_score(y[test_idx], pred)),
                "macro_f1": float(f1_score(y[test_idx], pred, average="macro", zero_division=0)),
                "report": classification_report(y[test_idx], pred, output_dict=True, zero_division=0),
            }
        except Exception as exc:
            results[name] = {"error": f"{type(exc).__name__}: {exc}"}
    return results
