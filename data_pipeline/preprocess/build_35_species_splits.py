"""Build deterministic, label-balanced splits for the 35-species probe.

Group IDs are required by default. Grouped inputs are split within each label
at the source-group level so all labels are represented in train, validation
and test. Passing --assume-independent-reads is an explicit opt-in for a
benchmark whose simulator guarantees independent reads. The flag is recorded
in the output metadata and must not be used to claim unseen-genome
generalization.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
from sklearn.model_selection import StratifiedShuffleSplit


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--labels", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--groups", type=Path)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--train-fraction", type=float, default=0.70)
    parser.add_argument("--validation-fraction", type=float, default=0.15)
    parser.add_argument("--assume-independent-reads", action="store_true")
    args = parser.parse_args()

    labels = np.asarray(np.load(args.labels, mmap_mode="r"))
    if labels.ndim != 1:
        raise ValueError(f"labels must be one-dimensional: {labels.shape}")
    if args.groups is None and not args.assume_independent_reads:
        raise ValueError(
            "Provide --groups, or explicitly pass --assume-independent-reads "
            "for simulator-certified independent reads."
        )
    groups = np.arange(labels.size) if args.groups is None else np.asarray(np.load(args.groups, mmap_mode="r"))
    if groups.shape != labels.shape:
        raise ValueError(f"groups and labels must have the same shape: {groups.shape} vs {labels.shape}")

    all_indices = np.arange(labels.size)
    if args.groups is None:
        first = StratifiedShuffleSplit(n_splits=1, test_size=1.0 - args.train_fraction, random_state=args.seed)
        train_pos, held_pos = next(first.split(all_indices, labels))
        held_labels = labels[held_pos]
        val_fraction_of_held = args.validation_fraction / (1.0 - args.train_fraction)
        second = StratifiedShuffleSplit(n_splits=1, test_size=1.0 - val_fraction_of_held, random_state=args.seed)
        val_rel, test_rel = next(second.split(held_pos, held_labels))
        split = {
            "train": all_indices[train_pos],
            "validation": held_pos[val_rel],
            "test": held_pos[test_rel],
        }
    else:
        if not 0 < args.train_fraction < 1 or not 0 < args.validation_fraction < 1:
            raise ValueError("split fractions must be in (0, 1)")
        unique_groups, first_positions = np.unique(groups, return_index=True)
        group_labels = labels[first_positions]
        order = np.argsort(groups, kind="stable")
        sorted_groups = groups[order]
        sorted_labels = labels[order]
        boundaries = np.flatnonzero(np.r_[True, sorted_groups[1:] != sorted_groups[:-1], True])
        for left, right in zip(boundaries[:-1], boundaries[1:]):
            if np.unique(sorted_labels[left:right]).size != 1:
                raise ValueError("each source group must map to exactly one label for stratified grouping")

        rng = np.random.default_rng(args.seed)
        train_group_pos: list[int] = []
        validation_group_pos: list[int] = []
        test_group_pos: list[int] = []
        for label in np.unique(group_labels):
            positions = np.flatnonzero(group_labels == label)
            if positions.size < 3:
                raise ValueError(
                    f"label {label!r} has only {positions.size} source groups; "
                    "at least three are required for train/validation/test"
                )
            positions = positions.copy()
            rng.shuffle(positions)
            n_validation = max(1, int(round(positions.size * args.validation_fraction)))
            n_test = max(1, int(round(positions.size * (1.0 - args.train_fraction - args.validation_fraction))))
            if n_validation + n_test >= positions.size:
                n_validation = 1
                n_test = 1
            validation_group_pos.extend(positions[:n_validation].tolist())
            test_group_pos.extend(positions[n_validation : n_validation + n_test].tolist())
            train_group_pos.extend(positions[n_validation + n_test :].tolist())
        train_groups = unique_groups[np.asarray(train_group_pos, dtype=np.int64)]
        validation_groups = unique_groups[np.asarray(validation_group_pos, dtype=np.int64)]
        test_groups = unique_groups[np.asarray(test_group_pos, dtype=np.int64)]
        split = {
            "train": np.flatnonzero(np.isin(groups, train_groups)),
            "validation": np.flatnonzero(np.isin(groups, validation_groups)),
            "test": np.flatnonzero(np.isin(groups, test_groups)),
        }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(args.output, **split)
    metadata = {
        "labels": str(args.labels.resolve()),
        "groups": str(args.groups.resolve()) if args.groups else None,
        "seed": args.seed,
        "train_fraction_requested": args.train_fraction,
        "validation_fraction_requested": args.validation_fraction,
        "assume_independent_reads": bool(args.assume_independent_reads),
        "n_rows": int(labels.size),
        "split_sizes": {key: int(value.size) for key, value in split.items()},
    }
    args.output.with_suffix(".json").write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
