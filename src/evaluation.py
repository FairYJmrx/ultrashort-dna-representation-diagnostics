"""Small, dependency-free metrics for feature diagnostics."""

from __future__ import annotations

import csv
import json
import math
import random
from collections import Counter, defaultdict
from pathlib import Path
from statistics import mean

SparseVector = dict[str, float]


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def write_json(path: Path, obj: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fh:
        json.dump(obj, fh, indent=2, ensure_ascii=False, sort_keys=True)


def l1_distance(a: SparseVector, b: SparseVector) -> float:
    keys = set(a) | set(b)
    return sum(abs(a.get(k, 0.0) - b.get(k, 0.0)) for k in keys)


def cosine_similarity(a: SparseVector, b: SparseVector) -> float:
    if not a or not b:
        return 0.0
    dot = sum(v * b.get(k, 0.0) for k, v in a.items())
    norm_a = math.sqrt(sum(v * v for v in a.values()))
    norm_b = math.sqrt(sum(v * v for v in b.values()))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


def cosine_distance(a: SparseVector, b: SparseVector) -> float:
    return 1.0 - cosine_similarity(a, b)


def vector_signature(vec: SparseVector, precision: int = 6) -> tuple[tuple[str, float], ...]:
    return tuple(sorted((k, round(v, precision)) for k, v in vec.items() if v != 0))


def stratified_split(rows: list[dict[str, str]], label_key: str = "label", test_fraction: float = 0.3, seed: int = 13) -> tuple[list[int], list[int]]:
    rng = random.Random(seed)
    by_label: dict[str, list[int]] = defaultdict(list)
    for i, row in enumerate(rows):
        by_label[row[label_key]].append(i)
    train: list[int] = []
    test: list[int] = []
    for indices in by_label.values():
        shuffled = indices[:]
        rng.shuffle(shuffled)
        test_n = max(1, round(len(shuffled) * test_fraction)) if len(shuffled) > 1 else 0
        test.extend(shuffled[:test_n])
        train.extend(shuffled[test_n:])
    return sorted(train), sorted(test)


def nearest_centroid_report(rows: list[dict[str, str]], vectors: list[SparseVector], seed: int = 13) -> dict[str, object]:
    if len({row["label"] for row in rows}) < 2:
        return {"accuracy": None, "macro_f1": None, "note": "need at least two labels"}

    train_idx, test_idx = stratified_split(rows, seed=seed)
    centroids: dict[str, SparseVector] = {}
    counts: Counter[str] = Counter()
    for idx in train_idx:
        label = rows[idx]["label"]
        counts[label] += 1
        centroid = centroids.setdefault(label, {})
        for key, value in vectors[idx].items():
            centroid[key] = centroid.get(key, 0.0) + value
    for label, centroid in centroids.items():
        denom = counts[label] or 1
        for key in list(centroid):
            centroid[key] /= denom

    y_true: list[str] = []
    y_pred: list[str] = []
    for idx in test_idx:
        vec = vectors[idx]
        best_label = None
        best_dist = float("inf")
        for label, centroid in centroids.items():
            dist = cosine_distance(vec, centroid)
            if dist < best_dist:
                best_dist = dist
                best_label = label
        y_true.append(rows[idx]["label"])
        y_pred.append(best_label or "")

    return classification_report(y_true, y_pred)


def classification_report(y_true: list[str], y_pred: list[str]) -> dict[str, object]:
    labels = sorted(set(y_true) | set(y_pred))
    correct = sum(1 for a, b in zip(y_true, y_pred) if a == b)
    accuracy = correct / len(y_true) if y_true else 0.0
    per_class: dict[str, dict[str, float]] = {}
    f1_values: list[float] = []
    for label in labels:
        tp = sum(1 for a, b in zip(y_true, y_pred) if a == label and b == label)
        fp = sum(1 for a, b in zip(y_true, y_pred) if a != label and b == label)
        fn = sum(1 for a, b in zip(y_true, y_pred) if a == label and b != label)
        precision = tp / (tp + fp) if (tp + fp) else 0.0
        recall = tp / (tp + fn) if (tp + fn) else 0.0
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) else 0.0
        per_class[label] = {"precision": precision, "recall": recall, "f1": f1}
        f1_values.append(f1)
    return {
        "accuracy": accuracy,
        "macro_f1": mean(f1_values) if f1_values else 0.0,
        "per_class": per_class,
        "support": len(y_true),
    }


def distance_summary(rows: list[dict[str, str]], vectors: list[SparseVector], max_pairs_per_type: int = 2000, seed: int = 13) -> dict[str, float | None]:
    rng = random.Random(seed)
    intra: list[float] = []
    inter: list[float] = []
    n = len(rows)
    if n < 2:
        return {"avg_intra_cosine_distance": None, "avg_inter_cosine_distance": None, "distance_gap": None}

    pairs = [(i, j) for i in range(n) for j in range(i + 1, n)]
    rng.shuffle(pairs)
    for i, j in pairs:
        target = intra if rows[i]["label"] == rows[j]["label"] else inter
        if len(target) < max_pairs_per_type:
            target.append(cosine_distance(vectors[i], vectors[j]))
        if len(intra) >= max_pairs_per_type and len(inter) >= max_pairs_per_type:
            break
    avg_intra = mean(intra) if intra else None
    avg_inter = mean(inter) if inter else None
    gap = (avg_inter - avg_intra) if avg_intra is not None and avg_inter is not None else None
    return {
        "avg_intra_cosine_distance": avg_intra,
        "avg_inter_cosine_distance": avg_inter,
        "distance_gap": gap,
    }


def duplicate_rate(vectors: list[SparseVector]) -> float:
    if not vectors:
        return 0.0
    unique = {vector_signature(v) for v in vectors}
    return 1.0 - (len(unique) / len(vectors))

