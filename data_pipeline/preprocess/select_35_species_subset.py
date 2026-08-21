"""Select a deterministic, capped multiclass subset from aligned labels.

The E5 contract uses at most 50,000 reads per species and a total cap of
1,500,000 reads. Allocation is balanced as far as the available class counts
allow; selected row indices are then sorted so every representation can reuse
the same input order.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np


def allocate_counts(available: np.ndarray, per_class_cap: int, total_cap: int) -> np.ndarray:
    target = np.minimum(available, per_class_cap).astype(np.int64)
    if int(target.sum()) <= total_cap:
        return target
    allocation = np.zeros_like(target)
    target_level = int(total_cap // target.size)
    allocation = np.minimum(target, target_level)
    remaining = int(total_cap - allocation.sum())
    while remaining:
        progressed = False
        for label in range(target.size):
            if allocation[label] < target[label]:
                allocation[label] += 1
                remaining -= 1
                progressed = True
                if remaining == 0:
                    break
        if not progressed:
            raise RuntimeError("allocation could not reach the requested total cap")
    return allocation


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--labels", type=Path, required=True)
    parser.add_argument("--output-indices", type=Path, required=True)
    parser.add_argument("--output-labels", type=Path, required=True)
    parser.add_argument("--output-metadata", type=Path, required=True)
    parser.add_argument("--max-per-species", type=int, default=50_000)
    parser.add_argument("--total-cap", type=int, default=1_500_000)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    if args.max_per_species < 1 or args.total_cap < 1:
        raise ValueError("sampling caps must be positive")

    labels = np.asarray(np.load(args.labels, mmap_mode="r"))
    if labels.ndim != 1:
        raise ValueError(f"labels must be one-dimensional: {labels.shape}")
    unique, available = np.unique(labels, return_counts=True)
    if not np.array_equal(unique, np.arange(unique.size)):
        raise ValueError("labels must be contiguous integer ids starting at zero")
    allocation = allocate_counts(available, args.max_per_species, args.total_cap)
    rng = np.random.default_rng(args.seed)
    selected_parts = []
    for label, count in enumerate(allocation):
        positions = np.flatnonzero(labels == label)
        if count:
            selected_parts.append(rng.choice(positions, size=int(count), replace=False))
    selected = np.sort(np.concatenate(selected_parts).astype(np.int64))
    args.output_indices.parent.mkdir(parents=True, exist_ok=True)
    args.output_labels.parent.mkdir(parents=True, exist_ok=True)
    args.output_metadata.parent.mkdir(parents=True, exist_ok=True)
    np.save(args.output_indices, selected)
    np.save(args.output_labels, labels[selected].astype(np.int64, copy=False))
    metadata = {
        "labels": str(args.labels.resolve()),
        "seed": args.seed,
        "max_per_species": args.max_per_species,
        "total_cap": args.total_cap,
        "n_available": int(labels.size),
        "n_selected": int(selected.size),
        "available_by_label": {str(int(k)): int(v) for k, v in zip(unique, available)},
        "selected_by_label": {str(int(k)): int(v) for k, v in zip(unique, allocation)},
        "selection_rule": "class-balanced deterministic sampling with per-class and total caps",
    }
    args.output_metadata.write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(metadata, indent=2))


if __name__ == "__main__":
    main()
