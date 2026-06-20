from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import sparse
from sklearn.metrics import accuracy_score, f1_score
from sklearn.model_selection import train_test_split
from sklearn.neighbors import NearestCentroid
from sklearn.preprocessing import LabelEncoder, normalize

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.sequence_utils import reverse_complement
from src.sklearn_features import build_kmer_matrix, sparsity_report, transform_feature_matrix
from src.spaced_features import build_spaced_kmer_matrix, property_summary_matrix


def parse_int_list(value: str) -> list[int]:
    return [int(item.strip()) for item in value.split(",") if item.strip()]


def parse_str_list(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


def parse_pattern(value: str) -> tuple[int, ...]:
    return tuple(int(item.strip()) for item in value.split("-") if item.strip())


def cosine_diag(a: sparse.spmatrix | np.ndarray, b: sparse.spmatrix | np.ndarray) -> np.ndarray:
    a_norm = normalize(a, norm="l2", axis=1)
    b_norm = normalize(b, norm="l2", axis=1)
    if sparse.issparse(a_norm) or sparse.issparse(b_norm):
        return np.asarray(a_norm.multiply(b_norm).sum(axis=1)).ravel()
    return np.sum(a_norm * b_norm, axis=1)


def row_l2_delta(a: sparse.spmatrix | np.ndarray, b: sparse.spmatrix | np.ndarray) -> np.ndarray:
    a_norm = normalize(a, norm="l2", axis=1)
    b_norm = normalize(b, norm="l2", axis=1)
    delta = a_norm - b_norm
    if sparse.issparse(delta):
        return np.sqrt(np.asarray(delta.multiply(delta).sum(axis=1)).ravel())
    return np.linalg.norm(delta, axis=1)


def matrix_with_train_vocabulary(
    train_sequences: list[str],
    all_sequences: list[str],
    family: str,
    k: int | None = None,
    pattern: tuple[int, ...] | None = None,
    canonical: bool = True,
    add_property: bool = False,
) -> tuple[sparse.csr_matrix | np.ndarray, int]:
    if family == "kmer":
        if k is None:
            raise ValueError("k is required for kmer family")
        _, vocab = build_kmer_matrix(train_sequences, k=k, canonical=canonical, vocabulary_mode="observed")
        mat, _ = build_kmer_matrix(all_sequences, k=k, canonical=canonical, vocabulary=vocab)
        feat, _ = transform_feature_matrix(mat, feature_type="count", normalization="l2", train_indices=list(range(len(train_sequences))))
        return feat, len(vocab)
    if family == "spaced":
        if pattern is None:
            raise ValueError("pattern is required for spaced family")
        _, vocab = build_spaced_kmer_matrix(train_sequences, pattern=pattern, canonical=canonical, vocabulary_mode="observed")
        mat, _ = build_spaced_kmer_matrix(all_sequences, pattern=pattern, canonical=canonical, vocabulary=vocab)
        mat = normalize(mat, norm="l2", axis=1).tocsr()
        if add_property:
            props = property_summary_matrix(all_sequences)
            dense = np.hstack([mat.toarray(), props])
            dense = normalize(dense, norm="l2", axis=1)
            return dense, len(vocab) + props.shape[1]
        return mat, len(vocab)
    raise ValueError(f"Unknown family: {family}")


def paired_subsets(df: pd.DataFrame, length: int, condition: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    clean = df[(df["source_length"] == length) & (df["condition"] == "clean")].copy()
    pert = df[(df["source_length"] == length) & (df["condition"] == condition)].copy()
    common = sorted(set(clean["clean_read_id"]) & set(pert["clean_read_id"]))
    clean = clean[clean["clean_read_id"].isin(common)].sort_values("clean_read_id").reset_index(drop=True)
    pert = pert[pert["clean_read_id"].isin(common)].sort_values("clean_read_id").reset_index(drop=True)
    return clean, pert


def sample_paired(
    clean: pd.DataFrame,
    pert: pd.DataFrame,
    max_pairs: int,
    seed: int,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    if max_pairs <= 0 or len(clean) <= max_pairs:
        return clean, pert
    chosen_ids = (
        clean[["clean_read_id"]]
        .drop_duplicates()
        .sample(n=max_pairs, random_state=seed)["clean_read_id"]
        .tolist()
    )
    clean_sample = clean[clean["clean_read_id"].isin(chosen_ids)].sort_values("clean_read_id").reset_index(drop=True)
    pert_sample = pert[pert["clean_read_id"].isin(chosen_ids)].sort_values("clean_read_id").reset_index(drop=True)
    return clean_sample, pert_sample


def run_stability_rows(
    df: pd.DataFrame,
    lengths: list[int],
    k_values: list[int],
    patterns: list[tuple[int, ...]],
    seed: int,
    max_pairs: int,
) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for length in lengths:
        for condition in ["reverse_complement", "N_3pct", "substitution_1pct"]:
            clean, pert = paired_subsets(df, length, condition)
            if clean.empty:
                continue
            clean, pert = sample_paired(clean, pert, max_pairs=max_pairs, seed=seed + length)
            train_sequences = clean["sequence"].tolist()
            sequences = train_sequences + pert["sequence"].tolist()

            for canonical in [False, True]:
                for k in k_values:
                    if length < k:
                        continue
                    mat, vocab_size = matrix_with_train_vocabulary(
                        train_sequences,
                        sequences,
                        family="kmer",
                        k=k,
                        canonical=canonical,
                    )
                    a = mat[: len(clean)]
                    b = mat[len(clean) :]
                    cos = cosine_diag(a, b)
                    l2 = row_l2_delta(a, b)
                    rows.append(
                        {
                            "family": "canonical k-mer" if canonical else "k-mer",
                            "parameter": f"k={k}",
                            "k": k,
                            "pattern": "",
                            "canonical": canonical,
                            "add_property": False,
                            "length": length,
                            "condition": condition,
                            "n": int(len(clean)),
                            "observed_vocab_size": int(vocab_size),
                            "paired_cosine_mean": float(np.mean(cos)),
                            "paired_cosine_p05": float(np.quantile(cos, 0.05)),
                            "l2_delta_mean": float(np.mean(l2)),
                            "l2_delta_p95": float(np.quantile(l2, 0.95)),
                        }
                    )

            for pattern in patterns:
                span = max(pattern) + 1
                if length < span:
                    continue
                for add_property in [False, True]:
                    mat, vocab_size = matrix_with_train_vocabulary(
                        train_sequences,
                        sequences,
                        family="spaced",
                        pattern=pattern,
                        canonical=True,
                        add_property=add_property,
                    )
                    a = mat[: len(clean)]
                    b = mat[len(clean) :]
                    cos = cosine_diag(a, b)
                    l2 = row_l2_delta(a, b)
                    rows.append(
                        {
                            "family": "canonical spaced + property" if add_property else "canonical spaced",
                            "parameter": "pattern=" + "-".join(str(x) for x in pattern),
                            "k": len(pattern),
                            "pattern": "-".join(str(x) for x in pattern),
                            "canonical": True,
                            "add_property": add_property,
                            "length": length,
                            "condition": condition,
                            "n": int(len(clean)),
                            "observed_vocab_size": int(vocab_size),
                            "paired_cosine_mean": float(np.mean(cos)),
                            "paired_cosine_p05": float(np.quantile(cos, 0.05)),
                            "l2_delta_mean": float(np.mean(l2)),
                            "l2_delta_p95": float(np.quantile(l2, 0.95)),
                        }
                    )
    return rows


def classification_probe(
    subset: pd.DataFrame,
    family: str,
    k: int | None,
    pattern: tuple[int, ...] | None,
    canonical: bool,
    add_property: bool,
    label_col: str,
    seed: int,
) -> dict[str, object]:
    labels = subset[label_col].astype(str).to_numpy()
    unique, counts = np.unique(labels, return_counts=True)
    if len(unique) < 2 or np.min(counts) < 2:
        return {"error": "not enough classes or samples"}
    y = LabelEncoder().fit_transform(labels)
    indices = np.arange(len(y))
    train_idx, test_idx = train_test_split(indices, test_size=0.3, random_state=seed, stratify=y)
    train_sequences = subset.iloc[train_idx]["sequence"].tolist()
    all_sequences = subset["sequence"].tolist()
    mat, vocab_size = matrix_with_train_vocabulary(
        train_sequences,
        all_sequences,
        family=family,
        k=k,
        pattern=pattern,
        canonical=canonical,
        add_property=add_property,
    )
    x = mat.toarray() if sparse.issparse(mat) else mat
    clf = NearestCentroid()
    clf.fit(x[train_idx], y[train_idx])
    pred = clf.predict(x[test_idx])
    return {
        "accuracy": float(accuracy_score(y[test_idx], pred)),
        "macro_f1": float(f1_score(y[test_idx], pred, average="macro", zero_division=0)),
        "n_features": int(x.shape[1]),
        "observed_vocab_size": int(vocab_size),
    }


def run_classification_rows(
    df: pd.DataFrame,
    lengths: list[int],
    k_values: list[int],
    patterns: list[tuple[int, ...]],
    seed: int,
    max_samples_per_group: int,
) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    config_rows: list[dict[str, object]] = []
    for canonical in [False, True]:
        for k in k_values:
            config_rows.append(
                {
                    "family": "kmer",
                    "method": "canonical k-mer" if canonical else "k-mer",
                    "parameter": f"k={k}",
                    "k": k,
                    "pattern": "",
                    "canonical": canonical,
                    "add_property": False,
                }
            )
    for pattern in patterns:
        for add_property in [False, True]:
            config_rows.append(
                {
                    "family": "spaced",
                    "method": "canonical spaced + property" if add_property else "canonical spaced",
                    "parameter": "pattern=" + "-".join(str(x) for x in pattern),
                    "k": len(pattern),
                    "pattern": "-".join(str(x) for x in pattern),
                    "canonical": True,
                    "add_property": add_property,
                }
            )

    for length in lengths:
        clean = df[(df["source_length"] == length) & (df["condition"] == "clean")].copy()
        if clean.empty:
            continue
        for genus, group_df in clean.groupby("genus"):
            if max_samples_per_group > 0 and len(group_df) > max_samples_per_group:
                group_df = group_df.sample(n=max_samples_per_group, random_state=seed).reset_index(drop=True)
            for label_col, probe_name in [("label", "within_genus_species"), ("target_binary", "target_background")]:
                if label_col == "target_binary" and group_df[label_col].nunique() < 2:
                    continue
                if label_col == "label" and group_df[label_col].nunique() < 2:
                    continue
                for cfg in config_rows:
                    if cfg["family"] == "kmer" and length < int(cfg["k"]):
                        continue
                    if cfg["family"] == "spaced":
                        pattern = parse_pattern(cfg["pattern"])
                        if length < max(pattern) + 1:
                            continue
                    else:
                        pattern = None
                    result = classification_probe(
                        group_df,
                        family=cfg["family"],
                        k=int(cfg["k"]) if cfg["family"] == "kmer" else None,
                        pattern=pattern,
                        canonical=bool(cfg["canonical"]),
                        add_property=bool(cfg["add_property"]),
                        label_col=label_col,
                        seed=seed,
                    )
                    row = {
                        "probe": probe_name,
                        "genus": genus,
                        "length": length,
                        "condition": "clean",
                        "method": cfg["method"],
                        "parameter": cfg["parameter"],
                        "k": cfg["k"],
                        "pattern": cfg["pattern"],
                        "canonical": cfg["canonical"],
                        "add_property": cfg["add_property"],
                        "n_samples": int(len(group_df)),
                        "n_classes": int(group_df[label_col].nunique()),
                    }
                    row.update(result)
                    rows.append(row)
    return rows


def write_summary(stability: pd.DataFrame, classification: pd.DataFrame, output_dir: Path) -> None:
    lines: list[str] = []
    lines.append("# Parameter Sensitivity Results\n")
    lines.append("This lightweight audit tests whether manuscript conclusions depend on a single arbitrary k value or one spaced-seed pattern.\n")
    if not stability.empty:
        clean = stability[stability["condition"].isin(["N_3pct", "substitution_1pct"])]
        best = (
            clean.sort_values(["condition", "length", "paired_cosine_mean"], ascending=[True, True, False])
            .groupby(["condition", "length"], as_index=False)
            .first()
        )
        lines.append("## Best perturbation-stability settings by length\n")
        lines.append(best[["condition", "length", "family", "parameter", "paired_cosine_mean", "l2_delta_mean", "observed_vocab_size"]].to_markdown(index=False, floatfmt=".3f"))
        lines.append("")
        k5 = clean[(clean["family"] == "canonical k-mer") & (clean["k"] == 5)]
        if not k5.empty:
            lines.append("Canonical 5-mer is retained as a strong conventional baseline, but the sensitivity grid shows that stability trends should be discussed across k rather than claimed for k=5 alone.\n")
    if not classification.empty:
        valid = classification.dropna(subset=["macro_f1"])
        if not valid.empty:
            grouped = (
                valid.groupby(["probe", "length", "method", "parameter"], as_index=False)
                .agg(mean_macro_f1=("macro_f1", "mean"), sd_macro_f1=("macro_f1", "std"), mean_features=("n_features", "mean"))
            )
            best_probe = (
                grouped.sort_values(["probe", "length", "mean_macro_f1"], ascending=[True, True, False])
                .groupby(["probe", "length"], as_index=False)
                .first()
            )
            lines.append("## Best close-relative readout settings by length\n")
            lines.append(best_probe[["probe", "length", "method", "parameter", "mean_macro_f1", "sd_macro_f1", "mean_features"]].to_markdown(index=False, floatfmt=".3f"))
            lines.append("")
            lines.append("These values remain downstream probes only. They show sensitivity to parameterization and reinforce the need to avoid a single-method accuracy claim.\n")
    (output_dir / "parameter_sensitivity_summary.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run k and spaced-pattern sensitivity diagnostics.")
    parser.add_argument("--input", default=str(PROJECT_ROOT / "data" / "real_slices" / "close_relative_reads.csv"))
    parser.add_argument("--output-dir", default=str(PROJECT_ROOT / "results" / "runs" / "parameter_sensitivity"))
    parser.add_argument("--lengths", default="69,75,100,125,150,300")
    parser.add_argument("--classification-lengths", default="75,150,300")
    parser.add_argument("--k-values", default="3,4,5,6,7,8")
    parser.add_argument("--patterns", default="0-1-2-3,0-2-4-6,0-1-3-6,0-2-5-8")
    parser.add_argument("--max-paired-reads", type=int, default=240)
    parser.add_argument("--max-samples-per-group", type=int, default=160)
    parser.add_argument("--seed", type=int, default=13)
    args = parser.parse_args()

    started = time.time()
    df = pd.read_csv(args.input)
    df["sequence"] = df["sequence"].astype(str).str.upper()
    df["source_length"] = df["source_length"].astype(int)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    lengths = parse_int_list(args.lengths)
    classification_lengths = parse_int_list(args.classification_lengths)
    k_values = parse_int_list(args.k_values)
    patterns = [parse_pattern(item) for item in parse_str_list(args.patterns)]

    stability_rows = run_stability_rows(
        df,
        lengths=lengths,
        k_values=k_values,
        patterns=patterns,
        seed=args.seed,
        max_pairs=args.max_paired_reads,
    )
    classification_rows = run_classification_rows(
        df,
        lengths=classification_lengths,
        k_values=k_values,
        patterns=patterns,
        seed=args.seed,
        max_samples_per_group=args.max_samples_per_group,
    )

    stability = pd.DataFrame(stability_rows)
    classification = pd.DataFrame(classification_rows)
    stability.to_csv(output_dir / "parameter_stability_metrics.csv", index=False, encoding="utf-8-sig")
    classification.to_csv(output_dir / "parameter_classification_probes.csv", index=False, encoding="utf-8-sig")
    write_summary(stability, classification, output_dir)
    with (output_dir / "parameter_sensitivity_run.json").open("w", encoding="utf-8") as fh:
        json.dump(
            {
                "elapsed_seconds": time.time() - started,
                "input": args.input,
                "lengths": lengths,
                "classification_lengths": classification_lengths,
                "k_values": k_values,
                "patterns": ["-".join(str(x) for x in pattern) for pattern in patterns],
                "max_paired_reads": args.max_paired_reads,
                "max_samples_per_group": args.max_samples_per_group,
                "n_stability_rows": int(len(stability)),
                "n_classification_rows": int(len(classification)),
            },
            fh,
            indent=2,
            ensure_ascii=False,
        )
    print(f"Wrote parameter sensitivity outputs to {output_dir}")


if __name__ == "__main__":
    main()
