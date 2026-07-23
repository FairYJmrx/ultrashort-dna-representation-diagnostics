from __future__ import annotations

import argparse
import json
import sys
import time
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score
from sklearn.model_selection import StratifiedKFold, train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import normalize


def _find_project_root(start: Path) -> Path:
    for candidate in [start.parent, *start.parents]:
        if (candidate / "methods").is_dir() and (candidate / "configs").is_dir():
            return candidate
    raise RuntimeError("Could not locate the release repository root.")


PROJECT_ROOT = _find_project_root(Path(__file__).resolve())
sys.path.insert(0, str(PROJECT_ROOT))

from experiments.main.run_stage2_representation_grid import paired_subsets, parse_csv_list, parse_int_list, set_global_seed  # noqa: E402
from src.stage2_features import build_feature_matrix, paired_retrieval_metrics  # noqa: E402


@dataclass(frozen=True)
class BlockWeight:
    name: str
    count_weight: float
    property_weight: float
    msp_weight: float

    @property
    def label(self) -> str:
        return f"{self.name} (k={self.count_weight:g}, P={self.property_weight:g}, MSP={self.msp_weight:g})"


WEIGHTS = [
    BlockWeight("identity_only", 1.0, 0.0, 0.0),
    BlockWeight("property_only", 0.0, 1.0, 1.0),
    BlockWeight("ck4_plus_p", 1.0, 1.0, 0.0),
    BlockWeight("ck4p_msp", 1.0, 1.0, 1.0),
    BlockWeight("identity_dominant", 2.0, 1.0, 1.0),
    BlockWeight("property_dominant", 1.0, 2.0, 2.0),
]


def weighted_block_features(
    sequences: list[str],
    length: int,
    train_indices: list[int],
    weight: BlockWeight,
) -> np.ndarray:
    count, _ = build_feature_matrix(sequences, "ckmer4_count_l2", length=length, train_indices=train_indices)
    prop, _ = build_feature_matrix(sequences, "property_l2", length=length, train_indices=train_indices)
    msp, _ = build_feature_matrix(sequences, "property_multiscale_mean_l2", length=length, train_indices=train_indices)
    blocks = [
        weight.count_weight * np.asarray(count, dtype=np.float64),
        weight.property_weight * np.asarray(prop, dtype=np.float64),
        weight.msp_weight * np.asarray(msp, dtype=np.float64),
    ]
    x = np.hstack(blocks)
    return normalize(np.nan_to_num(x, nan=0.0, posinf=0.0, neginf=0.0), norm="l2", axis=1)


def stability_audit(
    reads: pd.DataFrame,
    lengths: list[int],
    conditions: list[str],
    max_pairs: int,
    seed: int,
) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for length in lengths:
        for condition in [c for c in conditions if c != "clean"]:
            clean, pert = paired_subsets(reads, length, condition)
            if clean.empty:
                continue
            if max_pairs > 0 and len(clean) > max_pairs:
                keep = clean["clean_read_id"].drop_duplicates().sample(n=max_pairs, random_state=seed + length).tolist()
                clean = clean[clean["clean_read_id"].isin(keep)].sort_values("clean_read_id").reset_index(drop=True)
                pert = pert[pert["clean_read_id"].isin(keep)].sort_values("clean_read_id").reset_index(drop=True)
            sequences = clean["sequence"].astype(str).tolist() + pert["sequence"].astype(str).tolist()
            train_indices = list(range(len(clean)))
            for weight in WEIGHTS:
                x = weighted_block_features(sequences, length=length, train_indices=train_indices, weight=weight)
                clean_x = x[: len(clean)]
                pert_x = x[len(clean) :]
                metrics = paired_retrieval_metrics(clean_x, pert_x)
                metrics.update(
                    {
                        "length": int(length),
                        "condition": condition,
                        "weight_name": weight.name,
                        "weight_label": weight.label,
                        "count_weight": weight.count_weight,
                        "property_weight": weight.property_weight,
                        "msp_weight": weight.msp_weight,
                        "n_pairs": int(len(clean)),
                        "n_features": int(x.shape[1]),
                    }
                )
                rows.append(metrics)
    return pd.DataFrame(rows)


def classifier_registry(seed: int) -> dict[str, object]:
    return {
        "logistic": make_pipeline(StandardScaler(), LogisticRegression(max_iter=5000, random_state=seed)),
    }


def evaluate_delta_readout(clean: np.ndarray, noise: np.ndarray, local: np.ndarray, seed: int, cv_folds: int = 5) -> list[dict[str, object]]:
    x_delta = np.vstack([np.abs(noise - clean), np.abs(local - clean)])
    y = np.asarray([0] * clean.shape[0] + [1] * clean.shape[0])
    train_idx, test_idx = train_test_split(np.arange(len(y)), test_size=0.3, random_state=seed, stratify=y)
    rows: list[dict[str, object]] = []
    for clf_name, clf in classifier_registry(seed).items():
        clf.fit(x_delta[train_idx], y[train_idx])
        pred = clf.predict(x_delta[test_idx])
        rows.append(
            {
                "split": "holdout",
                "classifier": clf_name,
                "accuracy": float(accuracy_score(y[test_idx], pred)),
                "macro_f1": float(f1_score(y[test_idx], pred, average="macro", zero_division=0)),
            }
        )
    if cv_folds > 1:
        skf = StratifiedKFold(n_splits=cv_folds, shuffle=True, random_state=seed)
        for clf_name in classifier_registry(seed):
            scores_acc: list[float] = []
            scores_f1: list[float] = []
            for cv_train, cv_test in skf.split(x_delta, y):
                clf = classifier_registry(seed)[clf_name]
                clf.fit(x_delta[cv_train], y[cv_train])
                pred = clf.predict(x_delta[cv_test])
                scores_acc.append(float(accuracy_score(y[cv_test], pred)))
                scores_f1.append(float(f1_score(y[cv_test], pred, average="macro", zero_division=0)))
            rows.append(
                {
                    "split": f"{cv_folds}fold_cv",
                    "classifier": clf_name,
                    "accuracy": float(np.mean(scores_acc)),
                    "macro_f1": float(np.mean(scores_f1)),
                    "accuracy_std": float(np.std(scores_acc)),
                    "macro_f1_std": float(np.std(scores_f1)),
                }
            )
    return rows


def local_mutation_audit(triplets: pd.DataFrame, seed: int) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    metric_rows: list[dict[str, object]] = []
    summary_rows: list[dict[str, object]] = []
    readout_rows: list[dict[str, object]] = []
    for (length, mode), subset in triplets.groupby(["source_length", "local_mode"], sort=True):
        ordered = []
        sample_ids = sorted(subset["sample_id"].unique().tolist())
        for variant in ["clean", "random_noise", "local_property_shift"]:
            variant_df = subset[subset["variant"].eq(variant)].set_index("sample_id").loc[sample_ids]
            ordered.extend(variant_df["sequence"].astype(str).tolist())
        n_triplets = len(sample_ids)
        train_indices = list(range(n_triplets))
        for weight in WEIGHTS:
            x = weighted_block_features(ordered, length=int(length), train_indices=train_indices, weight=weight)
            clean = x[0:n_triplets]
            noise = x[n_triplets : 2 * n_triplets]
            local = x[2 * n_triplets : 3 * n_triplets]
            clean_norm = normalize(clean, norm="l2", axis=1)
            noise_norm = normalize(noise, norm="l2", axis=1)
            local_norm = normalize(local, norm="l2", axis=1)
            noise_l2 = np.linalg.norm(clean_norm - noise_norm, axis=1)
            local_l2 = np.linalg.norm(clean_norm - local_norm, axis=1)
            ratio = local_l2 / np.maximum(noise_l2, 1e-12)
            for idx, sample_id in enumerate(sample_ids):
                metric_rows.append(
                    {
                        "sample_id": sample_id,
                        "length": int(length),
                        "local_mode": mode,
                        "weight_name": weight.name,
                        "weight_label": weight.label,
                        "noise_l2": float(noise_l2[idx]),
                        "local_l2": float(local_l2[idx]),
                        "local_minus_noise_l2": float(local_l2[idx] - noise_l2[idx]),
                        "selective_sensitivity_ratio": float(ratio[idx]),
                        "n_features": int(x.shape[1]),
                    }
                )
            summary_rows.append(
                {
                    "length": int(length),
                    "local_mode": mode,
                    "weight_name": weight.name,
                    "weight_label": weight.label,
                    "noise_l2_mean": float(np.mean(noise_l2)),
                    "local_l2_mean": float(np.mean(local_l2)),
                    "local_minus_noise_l2_mean": float(np.mean(local_l2 - noise_l2)),
                    "selective_sensitivity_ratio_mean": float(np.mean(local_l2) / max(float(np.mean(noise_l2)), 1e-12)),
                    "selective_sensitivity_ratio_per_sample_mean": float(np.mean(ratio)),
                    "n_features": int(x.shape[1]),
                    "n_triplets": int(n_triplets),
                }
            )
            for row in evaluate_delta_readout(clean, noise, local, seed=seed + int(length)):
                row.update(
                    {
                        "length": int(length),
                        "local_mode": mode,
                        "weight_name": weight.name,
                        "weight_label": weight.label,
                        "n_samples": int(2 * n_triplets),
                        "n_features": int(x.shape[1]),
                    }
                )
                readout_rows.append(row)
    return pd.DataFrame(metric_rows), pd.DataFrame(summary_rows), pd.DataFrame(readout_rows)


def write_summary(stability: pd.DataFrame, local_summary: pd.DataFrame, local_readout: pd.DataFrame, out_dir: Path) -> None:
    lines = [
        "# Mixed-metric block-weight audit",
        "",
        "This audit keeps the k-mer, global property, and multi-scale property blocks separate and varies their weights before final L2 normalization. The point is to test whether the observed stability and selective-sensitivity trends survive reasonable block reweighting instead of relying on one fixed concatenation scale.",
        "",
    ]
    if not stability.empty:
        stab = (
            stability.groupby(["weight_name", "weight_label"], as_index=False)
            .agg(
                n_cells=("paired_cosine_mean", "count"),
                paired_cosine=("paired_cosine_mean", "mean"),
                l2_drift=("l2_delta_mean", "mean"),
                retrieval_top1=("retrieval_top1", "mean"),
            )
            .sort_values(["paired_cosine", "l2_drift"], ascending=[False, True])
        )
        stab.to_csv(out_dir / "block_weight_stability_summary.csv", index=False, encoding="utf-8-sig")
        lines.extend(["## Stability across block weights", "", stab.to_markdown(index=False, floatfmt=".3f"), ""])
    if not local_summary.empty:
        loc = (
            local_summary.groupby(["weight_name", "weight_label"], as_index=False)
            .agg(
                n_cells=("selective_sensitivity_ratio_mean", "count"),
                noise_l2=("noise_l2_mean", "mean"),
                local_l2=("local_l2_mean", "mean"),
                local_minus_noise_l2=("local_minus_noise_l2_mean", "mean"),
                selective_sensitivity_ratio=("selective_sensitivity_ratio_mean", "mean"),
            )
            .sort_values(["selective_sensitivity_ratio", "local_minus_noise_l2"], ascending=False)
        )
        loc.to_csv(out_dir / "block_weight_local_mutation_summary.csv", index=False, encoding="utf-8-sig")
        lines.extend(["## Local mutation sensitivity across block weights", "", loc.to_markdown(index=False, floatfmt=".3f"), ""])
    if not local_readout.empty:
        readout = (
            local_readout[local_readout["split"].astype(str).str.contains("fold_cv")]
            .groupby(["weight_name", "weight_label", "classifier"], as_index=False)
            .agg(
                n_cells=("macro_f1", "count"),
                macro_f1=("macro_f1", "mean"),
                accuracy=("accuracy", "mean"),
                n_features=("n_features", "median"),
            )
            .sort_values(["macro_f1", "accuracy"], ascending=False)
        )
        readout.to_csv(out_dir / "block_weight_delta_readout_summary.csv", index=False, encoding="utf-8-sig")
        lines.extend(["## Delta-readout across block weights", "", readout.to_markdown(index=False, floatfmt=".3f"), ""])
    (out_dir / "block_weight_audit_summary.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Audit block weighting for mixed k-mer + property features.")
    parser.add_argument("--input", default=str(PROJECT_ROOT / "results" / "stage3" / "position_property_ablation" / "stage3_compact_baseline_reads.csv"))
    parser.add_argument("--triplets", default=str(PROJECT_ROOT / "results" / "stage3" / "local_mutation_sensitivity" / "local_mutation_triplets.csv"))
    parser.add_argument("--output-dir", default=str(PROJECT_ROOT / "results" / "stage3" / "reviewer_response" / "mixed_metric_audit"))
    parser.add_argument("--lengths", default="69,75,100,150")
    parser.add_argument("--conditions", default="substitution_1pct,N_3pct,trim_5bp,substitution_1pct_N_3pct,local_mismatch_6bp,short_indel")
    parser.add_argument("--max-pairs", type=int, default=250)
    parser.add_argument("--seed", type=int, default=20260624)
    args = parser.parse_args()

    started = time.time()
    set_global_seed(args.seed)
    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    reads = pd.read_csv(args.input)
    reads["source_length"] = reads["source_length"].astype(int)
    reads["sequence"] = reads["sequence"].astype(str).str.upper()
    stability = stability_audit(reads, parse_int_list(args.lengths), parse_csv_list(args.conditions), args.max_pairs, args.seed)
    stability.to_csv(out_dir / "block_weight_stability.csv", index=False, encoding="utf-8-sig")

    triplets = pd.read_csv(args.triplets)
    local_metric, local_summary, local_readout = local_mutation_audit(triplets, seed=args.seed)
    local_metric.to_csv(out_dir / "block_weight_local_mutation_metrics.csv", index=False, encoding="utf-8-sig")
    local_summary.to_csv(out_dir / "block_weight_local_mutation_summary.csv", index=False, encoding="utf-8-sig")
    local_readout.to_csv(out_dir / "block_weight_delta_readout.csv", index=False, encoding="utf-8-sig")
    write_summary(stability, local_summary, local_readout, out_dir)

    (out_dir / "block_weight_audit_run.json").write_text(
        json.dumps(
            {
                "elapsed_seconds": time.time() - started,
                "input": args.input,
                "triplets": args.triplets,
                "lengths": parse_int_list(args.lengths),
                "conditions": parse_csv_list(args.conditions),
                "weights": [w.__dict__ for w in WEIGHTS],
                "max_pairs": args.max_pairs,
                "n_stability_rows": int(len(stability)),
                "n_local_metric_rows": int(len(local_metric)),
                "n_local_readout_rows": int(len(local_readout)),
            },
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    print(f"Wrote mixed-metric audit to {out_dir}")


if __name__ == "__main__":
    main()

