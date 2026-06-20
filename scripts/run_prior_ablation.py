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
from sklearn.metrics import accuracy_score, f1_score, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.neighbors import NearestCentroid
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import LabelEncoder, StandardScaler, normalize

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.representation_registry import build_representation, parse_kmer_representation
from src.sequence_utils import reverse_complement
from src.sklearn_features import build_kmer_matrix, transform_feature_matrix
from src.spaced_features import spaced_count_dense


REPRESENTATION_COMPONENTS: dict[str, dict[str, object]] = {
    "kmer5_count_l2": {
        "family": "contiguous k-mer",
        "contiguous_kmer": 1,
        "spaced_seed": 0,
        "canonical_rc": 0,
        "property_summary": 0,
        "position_phase": 0,
        "rope_position": 0,
        "description": "Contiguous 5-mer count vector with L2 normalization.",
    },
    "ckmer5_count_l2": {
        "family": "canonical contiguous k-mer",
        "contiguous_kmer": 1,
        "spaced_seed": 0,
        "canonical_rc": 1,
        "property_summary": 0,
        "position_phase": 0,
        "rope_position": 0,
        "description": "5-mer counts after min(k-mer, reverse-complement k-mer) canonicalization.",
    },
    "spaced_count_l2": {
        "family": "spaced seed",
        "contiguous_kmer": 0,
        "spaced_seed": 1,
        "canonical_rc": 0,
        "property_summary": 0,
        "position_phase": 0,
        "rope_position": 0,
        "description": "Spaced seed counts using pattern positions (0,2,4,6).",
    },
    "cspaced_count_l2": {
        "family": "canonical spaced seed",
        "contiguous_kmer": 0,
        "spaced_seed": 1,
        "canonical_rc": 1,
        "property_summary": 0,
        "position_phase": 0,
        "rope_position": 0,
        "description": "Spaced seed counts with reverse-complement canonicalization.",
    },
    "cspaced_property_l2": {
        "family": "canonical spaced-property",
        "contiguous_kmer": 0,
        "spaced_seed": 1,
        "canonical_rc": 1,
        "property_summary": 1,
        "position_phase": 0,
        "rope_position": 0,
        "description": "Canonical spaced seed counts concatenated with DNA property summaries and L2 normalization.",
    },
    "property_channels": {
        "family": "base property channels",
        "contiguous_kmer": 0,
        "spaced_seed": 0,
        "canonical_rc": 0,
        "property_summary": 1,
        "position_phase": 0,
        "rope_position": 0,
        "description": "Per-position hydrogen-bond, GC, purine, EIIP and N-mask channels.",
    },
    "spaced_kmer_no_phase": {
        "family": "spaced property token",
        "contiguous_kmer": 0,
        "spaced_seed": 1,
        "canonical_rc": 0,
        "property_summary": 1,
        "position_phase": 0,
        "rope_position": 0,
        "description": "Spaced token property sequence without explicit three-phase position signal.",
    },
    "spaced_kmer_phase": {
        "family": "phase-aware spaced property token",
        "contiguous_kmer": 0,
        "spaced_seed": 1,
        "canonical_rc": 0,
        "property_summary": 1,
        "position_phase": 1,
        "rope_position": 0,
        "description": "Spaced token property sequence with sine/cosine start-position phase.",
    },
    "rope_property": {
        "family": "RoPE-property",
        "contiguous_kmer": 0,
        "spaced_seed": 0,
        "canonical_rc": 0,
        "property_summary": 1,
        "position_phase": 0,
        "rope_position": 1,
        "description": "DNA property vectors rotated by RoPE-like positional phases.",
    },
    "rope_onehot": {
        "family": "RoPE-onehot",
        "contiguous_kmer": 0,
        "spaced_seed": 0,
        "canonical_rc": 0,
        "property_summary": 0,
        "position_phase": 0,
        "rope_position": 1,
        "description": "One-hot base vectors rotated by RoPE-like positional phases.",
    },
}


def parse_csv_list(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


def parse_int_list(value: str) -> list[int]:
    return [int(item.strip()) for item in value.split(",") if item.strip()]


def build_representation_matrix(
    sequences: list[str],
    representation: str,
    length: int,
    train_indices: list[int] | None = None,
) -> np.ndarray:
    parsed = parse_kmer_representation(representation)
    if parsed:
        k, feature_type, normalization, canonical = parsed
        if train_indices is None:
            train_indices = list(range(len(sequences)))
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


def cosine_diag(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    a = normalize(a, norm="l2", axis=1)
    b = normalize(b, norm="l2", axis=1)
    return np.sum(a * b, axis=1)


def paired_matrix(
    df: pd.DataFrame,
    representation: str,
    length: int,
    condition: str,
) -> tuple[pd.DataFrame, pd.DataFrame, np.ndarray, np.ndarray]:
    clean = df[(df["source_length"] == length) & (df["condition"] == "clean")].copy()
    pert = df[(df["source_length"] == length) & (df["condition"] == condition)].copy()
    common = sorted(set(clean["clean_read_id"]) & set(pert["clean_read_id"]))
    clean = clean[clean["clean_read_id"].isin(common)].sort_values("clean_read_id").reset_index(drop=True)
    pert = pert[pert["clean_read_id"].isin(common)].sort_values("clean_read_id").reset_index(drop=True)
    all_sequences = clean["sequence"].tolist() + pert["sequence"].tolist()
    x = build_representation_matrix(all_sequences, representation, length, train_indices=list(range(len(clean))))
    return clean, pert, x[: len(clean)], x[len(clean):]


def rc_consistency(df: pd.DataFrame, representation: str, length: int) -> dict[str, object]:
    clean, rc, x_clean, x_rc = paired_matrix(df, representation, length, "reverse_complement")
    if clean.empty:
        return {"error": "missing clean/reverse-complement pairs"}
    cos = cosine_diag(x_clean, x_rc)
    return {
        "task": "rc_consistency",
        "representation": representation,
        "length": length,
        "condition": "reverse_complement",
        "n": int(len(clean)),
        "paired_cosine_mean": float(np.mean(cos)),
        "paired_cosine_median": float(np.median(cos)),
        "paired_cosine_p05": float(np.quantile(cos, 0.05)),
    }


def perturbation_stability(df: pd.DataFrame, representation: str, length: int, condition: str) -> dict[str, object]:
    clean, pert, x_clean, x_pert = paired_matrix(df, representation, length, condition)
    if clean.empty:
        return {"error": f"missing clean/{condition} pairs"}
    cos = cosine_diag(x_clean, x_pert)
    delta = np.linalg.norm(normalize(x_clean, norm="l2", axis=1) - normalize(x_pert, norm="l2", axis=1), axis=1)
    return {
        "task": "perturbation_stability",
        "representation": representation,
        "length": length,
        "condition": condition,
        "n": int(len(clean)),
        "paired_cosine_mean": float(np.mean(cos)),
        "paired_cosine_p05": float(np.quantile(cos, 0.05)),
        "l2_delta_mean": float(np.mean(delta)),
        "l2_delta_p95": float(np.quantile(delta, 0.95)),
    }


def binary_or_multiclass_cv(
    subset: pd.DataFrame,
    representation: str,
    length: int,
    label_col: str,
    seed: int,
    task: str,
    group: str,
) -> list[dict[str, object]]:
    if subset.empty or subset[label_col].nunique() < 2:
        return [
            {
                "task": task,
                "group": group,
                "representation": representation,
                "length": length,
                "error": "empty or single-class subset",
            }
        ]
    encoder = LabelEncoder()
    y = encoder.fit_transform(subset[label_col].astype(str).to_numpy())
    unique, counts = np.unique(y, return_counts=True)
    if np.min(counts) < 4:
        return [
            {
                "task": task,
                "group": group,
                "representation": representation,
                "length": length,
                "error": "not enough samples per class",
            }
        ]
    idx = np.arange(len(y))
    train_idx, test_idx = train_test_split(idx, test_size=0.3, random_state=seed, stratify=y)
    x = build_representation_matrix(subset["sequence"].tolist(), representation, length, train_indices=train_idx.tolist())
    classifiers = {
        "nearest_centroid": NearestCentroid(),
        "logistic_regression": make_pipeline(StandardScaler(), LogisticRegression(max_iter=2500, random_state=seed)),
    }
    rows: list[dict[str, object]] = []
    for clf_name, clf in classifiers.items():
        try:
            clf.fit(x[train_idx], y[train_idx])
            pred = clf.predict(x[test_idx])
            row: dict[str, object] = {
                "task": task,
                "group": group,
                "representation": representation,
                "length": length,
                "condition": str(subset["condition"].iloc[0]),
                "classifier": clf_name,
                "n": int(len(subset)),
                "n_classes": int(len(unique)),
                "accuracy": float(accuracy_score(y[test_idx], pred)),
                "macro_f1": float(f1_score(y[test_idx], pred, average="macro", zero_division=0)),
            }
            if len(unique) == 2 and hasattr(clf, "predict_proba"):
                try:
                    score = clf.predict_proba(x[test_idx])[:, 1]
                    row["auroc"] = float(roc_auc_score(y[test_idx], score))
                except Exception:
                    pass
            rows.append(row)
        except Exception as exc:
            rows.append(
                {
                    "task": task,
                    "group": group,
                    "representation": representation,
                    "length": length,
                    "condition": str(subset["condition"].iloc[0]),
                    "classifier": clf_name,
                    "error": f"{type(exc).__name__}: {exc}",
                }
            )
    return rows


def close_relative_tasks(
    df: pd.DataFrame,
    representation: str,
    length: int,
    condition: str,
    seed: int,
    max_per_class: int,
) -> list[dict[str, object]]:
    def downsample_by_class(frame: pd.DataFrame, class_col: str, n: int, random_state: int) -> pd.DataFrame:
        parts = []
        for _, part in frame.groupby(class_col):
            parts.append(part.sample(n=min(n, len(part)), random_state=random_state))
        if not parts:
            return frame.iloc[0:0].copy()
        return pd.concat(parts, ignore_index=True)

    rows: list[dict[str, object]] = []
    for genus, group_df in df[(df["source_length"] == length) & (df["condition"] == condition)].groupby("genus"):
        # Downsample per class for speed while preserving the close-relative question.
        sampled = downsample_by_class(group_df, "label", max_per_class, seed)
        rows.extend(binary_or_multiclass_cv(sampled, representation, length, "label", seed, "close_relative_species", str(genus)))
        if sampled["target_binary"].nunique() >= 2:
            sampled_binary = downsample_by_class(sampled, "target_binary", max_per_class * 2, seed + 1)
            rows.extend(
                binary_or_multiclass_cv(
                    sampled_binary,
                    representation,
                    length,
                    "target_binary",
                    seed,
                    "close_relative_target_binary",
                    str(genus),
                )
            )
    return rows


def component_delta_table(metrics: pd.DataFrame) -> pd.DataFrame:
    comparisons = [
        ("canonicalization_on_contiguous", "kmer5_count_l2", "ckmer5_count_l2"),
        ("spaced_seed_vs_contiguous", "kmer5_count_l2", "spaced_count_l2"),
        ("canonicalization_on_spaced", "spaced_count_l2", "cspaced_count_l2"),
        ("property_added_to_cspaced", "cspaced_count_l2", "cspaced_property_l2"),
        ("phase_added_to_spaced_property", "spaced_kmer_no_phase", "spaced_kmer_phase"),
        ("rope_property_vs_rope_onehot", "rope_onehot", "rope_property"),
    ]
    value_cols = [
        "paired_cosine_mean",
        "paired_cosine_p05",
        "l2_delta_mean",
        "l2_delta_p95",
        "accuracy",
        "macro_f1",
        "auroc",
    ]
    rows: list[dict[str, object]] = []
    key_cols = ["task", "group", "length", "condition", "classifier"]
    for comparison, base_rep, test_rep in comparisons:
        base = metrics[metrics["representation"] == base_rep]
        test = metrics[metrics["representation"] == test_rep]
        if base.empty or test.empty:
            continue
        merged = base.merge(test, on=key_cols, suffixes=("_base", "_test"))
        for _, row in merged.iterrows():
            out = {
                "comparison": comparison,
                "base_representation": base_rep,
                "test_representation": test_rep,
            }
            for key in key_cols:
                out[key] = row[key]
            for col in value_cols:
                b = row.get(f"{col}_base")
                t = row.get(f"{col}_test")
                if pd.notna(b) and pd.notna(t):
                    out[f"delta_{col}"] = float(t) - float(b)
            rows.append(out)
    return pd.DataFrame(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run component ablations for hybrid DNA priors.")
    parser.add_argument("--toy-input", default="data/toy_reads/toy_hardened_tasks.csv")
    parser.add_argument("--close-input", default="data/real_slices/close_relative_reads.csv")
    parser.add_argument("--output-dir", default="results/runs/prior_ablation")
    parser.add_argument(
        "--representations",
        default="kmer5_count_l2,ckmer5_count_l2,spaced_count_l2,cspaced_count_l2,cspaced_property_l2,property_channels,spaced_kmer_no_phase,spaced_kmer_phase,rope_onehot,rope_property",
    )
    parser.add_argument("--lengths", default="75,150,300")
    parser.add_argument("--conditions", default="clean,N_3pct,substitution_1pct")
    parser.add_argument("--max-per-class", type=int, default=45)
    parser.add_argument("--seed", type=int, default=73)
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    reps = parse_csv_list(args.representations)
    lengths = parse_int_list(args.lengths)
    conditions = parse_csv_list(args.conditions)
    rows: list[dict[str, object]] = []
    started = time.time()

    toy_df = pd.read_csv(args.toy_input)
    toy_df["source_length"] = toy_df["source_length"].astype(int)
    close_df = pd.read_csv(args.close_input)
    close_df["source_length"] = close_df["source_length"].astype(int)

    for rep in reps:
        for length in lengths:
            if length in set(toy_df["source_length"]):
                try:
                    rows.append(rc_consistency(toy_df, rep, length))
                except Exception as exc:
                    rows.append({"task": "rc_consistency", "representation": rep, "length": length, "condition": "reverse_complement", "error": f"{type(exc).__name__}: {exc}"})
                for condition in ["N_3pct", "substitution_1pct"]:
                    try:
                        rows.append(perturbation_stability(toy_df, rep, length, condition))
                    except Exception as exc:
                        rows.append({"task": "perturbation_stability", "representation": rep, "length": length, "condition": condition, "error": f"{type(exc).__name__}: {exc}"})
                for condition in ["clean", "N_3pct"]:
                    subset = toy_df[
                        (toy_df["source_length"] == length)
                        & (toy_df["condition"] == condition)
                        & (toy_df["label"].isin(["motif_jitter_front", "motif_jitter_middle", "motif_jitter_back"]))
                    ].copy()
                    rows.extend(binary_or_multiclass_cv(subset, rep, length, "label", args.seed, "motif_position", "toy_motif"))
            if length in set(close_df["source_length"]):
                try:
                    rc_row = rc_consistency(close_df, rep, length)
                    rc_row["group"] = "close_relative_wgs"
                    rows.append(rc_row)
                except Exception as exc:
                    rows.append(
                        {
                            "task": "rc_consistency",
                            "group": "close_relative_wgs",
                            "representation": rep,
                            "length": length,
                            "condition": "reverse_complement",
                            "error": f"{type(exc).__name__}: {exc}",
                        }
                    )
                for perturb_condition in ["N_3pct", "substitution_1pct"]:
                    try:
                        stab_row = perturbation_stability(close_df, rep, length, perturb_condition)
                        stab_row["group"] = "close_relative_wgs"
                        rows.append(stab_row)
                    except Exception as exc:
                        rows.append(
                            {
                                "task": "perturbation_stability",
                                "group": "close_relative_wgs",
                                "representation": rep,
                                "length": length,
                                "condition": perturb_condition,
                                "error": f"{type(exc).__name__}: {exc}",
                            }
                        )
                for condition in conditions:
                    if condition == "substitution_1pct":
                        continue
                    rows.extend(close_relative_tasks(close_df, rep, length, condition, args.seed, args.max_per_class))

    metrics = pd.DataFrame(rows)
    component_rows = []
    for rep in reps:
        item = {"representation": rep}
        item.update(REPRESENTATION_COMPONENTS.get(rep, {}))
        component_rows.append(item)
    components = pd.DataFrame(component_rows)
    deltas = component_delta_table(metrics)

    metrics.to_csv(output_dir / "prior_ablation_metrics.csv", index=False, encoding="utf-8-sig")
    components.to_csv(output_dir / "prior_component_table.csv", index=False, encoding="utf-8-sig")
    deltas.to_csv(output_dir / "prior_ablation_deltas.csv", index=False, encoding="utf-8-sig")
    payload = {
        "elapsed_seconds": time.time() - started,
        "representations": reps,
        "lengths": lengths,
        "conditions": conditions,
        "n_metric_rows": int(len(metrics)),
        "n_delta_rows": int(len(deltas)),
    }
    (output_dir / "prior_ablation_run.json").write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote prior ablation to {output_dir}")
    print(payload)


if __name__ == "__main__":
    main()
