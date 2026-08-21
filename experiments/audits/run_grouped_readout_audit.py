"""Re-audit compact readouts with source-template grouped cross-validation.

This audit intentionally does not overwrite the historical stage-3 outputs.
It reuses the same stage-2 derivation and balanced sampling rules, while
keeping every condition derived from one ``clean_read_id`` in one fold.
"""

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
from sklearn.model_selection import StratifiedGroupKFold
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

from experiments.main.run_stage2_representation_grid import (  # noqa: E402
    balanced_sample,
    derive_stage2_reads,
    parse_csv_list,
    parse_int_list,
    set_global_seed,
)
from methods.stage2_features import build_feature_matrix  # noqa: E402


DEFAULT_REPRESENTATIONS = "ck4,ck4_p,ck4p_msp,ckmer5_count_l2"


def classifier_registry(seed: int) -> dict[str, object]:
    return {
        "nearest_centroid": NearestCentroid(),
        "logistic": make_pipeline(
            StandardScaler(), LogisticRegression(max_iter=3000, random_state=seed)
        ),
    }


def evaluate_grouped(
    subset: pd.DataFrame,
    representation: str,
    label_col: str,
    length: int,
    seed: int,
    n_splits: int,
) -> list[dict[str, object]]:
    labels = subset[label_col].astype(str).to_numpy()
    groups = subset["clean_read_id"].astype(str).to_numpy()
    unique, counts = np.unique(labels, return_counts=True)
    if len(unique) < 2 or np.min(counts) < n_splits:
        return [
            {
                "error": "not enough labels or groups",
                "representation": representation,
                "classifier": "all",
                "n_classes": int(len(unique)),
                "n_groups": int(len(np.unique(groups))),
            }
        ]

    y = LabelEncoder().fit_transform(labels)
    split_rows: list[dict[str, object]] = []
    splitter = StratifiedGroupKFold(n_splits=n_splits, shuffle=True, random_state=seed)
    for fold, (train_idx, test_idx) in enumerate(
        splitter.split(np.zeros(len(y)), y, groups), start=1
    ):
        sequences = subset["sequence"].astype(str).tolist()
        x, info = build_feature_matrix(
            sequences,
            representation,
            length=length,
            train_indices=train_idx.tolist(),
        )
        for classifier_name, model in classifier_registry(seed + fold).items():
            model.fit(x[train_idx], y[train_idx])
            pred = model.predict(x[test_idx])
            split_rows.append(
                {
                    "representation": representation,
                    "classifier": classifier_name,
                    "split": f"{n_splits}fold_grouped_cv",
                    "fold": fold,
                    "task": "",
                    "length": length,
                    "condition": str(subset["condition"].iloc[0]),
                    "n_samples": int(len(subset)),
                    "n_groups": int(len(np.unique(groups))),
                    "n_classes": int(len(unique)),
                    "n_features": int(info.n_features),
                    "accuracy": float(accuracy_score(y[test_idx], pred)),
                    "macro_f1": float(
                        f1_score(y[test_idx], pred, average="macro", zero_division=0)
                    ),
                }
            )
    return split_rows


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input",
        default=str(PROJECT_ROOT / "data" / "real_slices" / "close_relative_reads.csv"),
    )
    parser.add_argument(
        "--output-dir",
        default=str(PROJECT_ROOT / "results" / "stage3" / "contract_v2" / "grouped_readout_audit"),
    )
    parser.add_argument("--lengths", default="69,75,100,150")
    parser.add_argument(
        "--conditions",
        default="clean,substitution_1pct,N_3pct,trim_5bp,substitution_1pct_N_3pct",
    )
    parser.add_argument("--representations", default=DEFAULT_REPRESENTATIONS)
    parser.add_argument("--max-clean-per-length", type=int, default=600)
    parser.add_argument("--max-per-class", type=int, default=80)
    parser.add_argument("--n-splits", type=int, default=5)
    parser.add_argument("--seed", type=int, default=20260730)
    args = parser.parse_args()

    started = time.time()
    set_global_seed(args.seed)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    lengths = parse_int_list(args.lengths)
    conditions = parse_csv_list(args.conditions)
    representations = parse_csv_list(args.representations)

    source = pd.read_csv(args.input)
    source["source_length"] = source["source_length"].astype(int)
    source["sequence"] = source["sequence"].astype(str).str.upper()
    derived = derive_stage2_reads(
        source,
        lengths=lengths,
        conditions=conditions,
        seed=args.seed,
        max_clean_per_length=args.max_clean_per_length,
    )
    derived.to_csv(output_dir / "grouped_readout_derived_reads.csv", index=False, encoding="utf-8-sig")

    rows: list[dict[str, object]] = []
    for length in lengths:
        for condition in conditions:
            subset = derived[
                (derived["source_length"] == length)
                & (derived["condition"] == condition)
            ].copy()
            if subset.empty:
                continue
            for genus, genus_df in subset.groupby("genus", sort=True):
                for task, label_col in (
                    ("within_genus_species", "label"),
                    ("target_background", "target_binary"),
                ):
                    if genus_df[label_col].nunique() < 2:
                        continue
                    sampled = balanced_sample(
                        genus_df,
                        label_col,
                        max_per_class=args.max_per_class,
                        seed=args.seed + length,
                    )
                    for representation in representations:
                        for row in evaluate_grouped(
                            sampled,
                            representation=representation,
                            label_col=label_col,
                            length=length,
                            seed=args.seed,
                            n_splits=args.n_splits,
                        ):
                            row.update({"task": task, "genus": genus, "label_col": label_col})
                            rows.append(row)

    result = pd.DataFrame(rows)
    result.to_csv(output_dir / "grouped_readout_by_cell.csv", index=False, encoding="utf-8-sig")
    valid = result.dropna(subset=["macro_f1"]).copy()
    summary = (
        valid.groupby(["task", "length", "condition", "representation", "classifier"], as_index=False)
        .agg(
            macro_f1_mean=("macro_f1", "mean"),
            macro_f1_sd=("macro_f1", "std"),
            accuracy_mean=("accuracy", "mean"),
            n_cells=("genus", "count"),
        )
    )
    summary.to_csv(output_dir / "grouped_readout_summary.csv", index=False, encoding="utf-8-sig")
    metadata = {
        "input": args.input,
        "lengths": lengths,
        "conditions": conditions,
        "representations": representations,
        "max_clean_per_length": args.max_clean_per_length,
        "max_per_class": args.max_per_class,
        "n_splits": args.n_splits,
        "group_column": "clean_read_id",
        "split": "StratifiedGroupKFold",
        "elapsed_seconds": time.time() - started,
    }
    (output_dir / "grouped_readout_audit_run.json").write_text(
        json.dumps(metadata, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(f"Wrote {len(result)} fold rows and {len(summary)} summary rows to {output_dir}")


if __name__ == "__main__":
    main()
