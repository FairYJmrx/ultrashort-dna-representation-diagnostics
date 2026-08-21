"""Run a fixed-capacity multiclass probe on precomputed representations.

Feature construction is intentionally separate from this readout script. The
same labels, split indices, MLP architecture and random seed are applied to
every representation. This keeps E5 a representation-accessibility probe,
not a classifier architecture comparison.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
from sklearn.metrics import balanced_accuracy_score, f1_score, recall_score
from sklearn.neural_network import MLPClassifier


def sha256_file(path: Path, chunk_size: int = 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(chunk_size), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_matrix(path: Path) -> np.ndarray:
    if path.suffix == ".npz":
        archive = np.load(path)
        if "features" not in archive:
            raise ValueError(f"feature archive must contain 'features': {path}")
        matrix = archive["features"]
    else:
        matrix = np.load(path, mmap_mode="r")
    if matrix.ndim != 2:
        raise ValueError(f"features must be two-dimensional: {path} -> {matrix.shape}")
    return np.asarray(matrix, dtype=np.float32)


def evaluate_representation(
    matrix: np.ndarray,
    labels: np.ndarray,
    splits: dict[str, np.ndarray],
    seed: int,
    hidden: tuple[int, ...],
    max_iter: int,
) -> dict[str, object]:
    model = MLPClassifier(
        hidden_layer_sizes=hidden,
        activation="relu",
        solver="adam",
        batch_size=256,
        learning_rate_init=1e-3,
        max_iter=max_iter,
        random_state=seed,
        early_stopping=False,
        verbose=False,
    )
    train = splits["train"]
    model.fit(matrix[train], labels[train])
    output: dict[str, object] = {}
    for name in ("train", "validation", "test"):
        indices = splits[name]
        predicted = model.predict(matrix[indices])
        output[name] = {
            "n": int(indices.size),
            "macro_f1": float(f1_score(labels[indices], predicted, average="macro")),
            "balanced_accuracy": float(balanced_accuracy_score(labels[indices], predicted)),
            "macro_recall": float(recall_score(labels[indices], predicted, average="macro", zero_division=0)),
        }
    return output


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--representation", action="append", nargs=2, metavar=("NAME", "PATH"), required=True)
    parser.add_argument("--labels", type=Path, required=True)
    parser.add_argument("--splits", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--hidden", default="128,64")
    parser.add_argument("--max-iter", type=int, default=50)
    args = parser.parse_args()

    labels = np.asarray(np.load(args.labels, mmap_mode="r"))
    split_archive = np.load(args.splits)
    splits = {key: np.asarray(split_archive[key], dtype=np.int64) for key in ("train", "validation", "test")}
    if any(np.intersect1d(splits[left], splits[right]).size for left, right in (("train", "validation"), ("train", "test"), ("validation", "test"))):
        raise ValueError("split indices overlap")
    hidden = tuple(int(value) for value in args.hidden.split(",") if value)
    results = []
    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    for name, raw_path in args.representation:
        path = Path(raw_path)
        matrix = load_matrix(path)
        if matrix.shape[0] != labels.size:
            raise ValueError(f"row mismatch for {name}: {matrix.shape[0]} vs {labels.size}")
        metrics = evaluate_representation(matrix, labels, splits, args.seed, hidden, args.max_iter)
        results.append({"representation": name, "feature_path": str(path.resolve()), "feature_sha256": sha256_file(path), "dimension": int(matrix.shape[1]), "metrics": metrics})

    manifest = {
        "experiment": "E5_fixed_capacity_multiclass_probe",
        "seed": args.seed,
        "hidden_layer_sizes": hidden,
        "max_iter": args.max_iter,
        "labels_path": str(args.labels.resolve()),
        "labels_sha256": sha256_file(args.labels),
        "splits_path": str(args.splits.resolve()),
        "splits_sha256": sha256_file(args.splits),
        "results": results,
        "scope": "closed-set representation accessibility; not production taxonomy classification",
    }
    (output_dir / "e5_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    rows = []
    for result in results:
        for split_name, metrics in result["metrics"].items():
            rows.append({"representation": result["representation"], "split": split_name, "dimension": result["dimension"], **metrics})
    import csv

    with (output_dir / "e5_metrics.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=sorted(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    main()
