"""Repeat the local-change factorial audit on natural WGS-derived templates."""

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
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler


def find_project_root(start: Path) -> Path:
    for candidate in [start.parent, *start.parents]:
        if (candidate / "methods").is_dir() and (candidate / "configs").is_dir():
            return candidate
    raise RuntimeError("Could not locate the release repository root.")


PROJECT_ROOT = find_project_root(Path(__file__).resolve())
sys.path.insert(0, str(PROJECT_ROOT))

from experiments.audits.run_local_change_factorial_audit import (  # noqa: E402
    PROPERTY_SHIFT,
    local_positions,
)
from methods.ck4p_msp import build_block_combination, build_ck4p_msp_features  # noqa: E402
from methods.historical_descriptors import build_historical_descriptor_matrix  # noqa: E402


REPRESENTATIONS = [
    "ck4",
    "ck4_p",
    "ck4_msp",
    "ck4p_msp",
    "pseknc_k3_l3",
    "pseeiip",
    "ncp_anf",
]

LABELS = {
    "ck4": "CK4",
    "ck4_p": "CK4+P",
    "ck4_msp": "CK4+MSP",
    "ck4p_msp": "CK4P-MSP",
    "pseknc_k3_l3": "PseKNC",
    "pseeiip": "PseEIIP",
    "ncp_anf": "NCP+ANF",
}


def mutate_sequence(sequence: str, positions: list[int], chemistry: str, rng: np.random.Generator) -> str:
    chars = list(sequence)
    for position in positions:
        current = chars[position]
        if chemistry == "property":
            chars[position] = PROPERTY_SHIFT.get(current, "A")
        elif chemistry == "random":
            choices = [base for base in "ACGT" if base != current]
            chars[position] = str(rng.choice(choices))
        else:
            raise ValueError(f"Unsupported chemistry: {chemistry}")
    return "".join(chars)


def sample_natural_templates(
    source: pd.DataFrame,
    lengths: list[int],
    max_per_length: int,
    seed: int,
) -> pd.DataFrame:
    clean = source[
        source["condition"].astype(str).eq("clean")
        & source["source_length"].astype(int).isin(lengths)
        & source["sequence"].astype(str).str.fullmatch("[ACGT]+")
    ].copy()
    parts: list[pd.DataFrame] = []
    for length, group in clean.groupby("source_length", sort=True):
        n = min(max_per_length, len(group))
        parts.append(group.sample(n=n, random_state=seed + int(length)))
    if not parts:
        raise ValueError("No natural clean templates were found for the requested lengths.")
    return pd.concat(parts, ignore_index=True)


def build_natural_factorial_reads(
    source: pd.DataFrame,
    lengths: list[int],
    max_per_length: int,
    mutation_fraction: float,
    seed: int,
) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    templates = sample_natural_templates(source, lengths, max_per_length, seed)
    rows: list[dict[str, object]] = []
    for _, source_row in templates.iterrows():
        sequence = str(source_row["sequence"]).upper()
        length = len(sequence)
        n_changes = max(1, int(round(length * mutation_fraction)))
        dispersed = sorted(
            rng.choice(np.arange(length), size=n_changes, replace=False).astype(int).tolist()
        )
        contiguous = local_positions(length, n_changes, "center", rng)
        template_id = str(source_row["clean_read_id"])
        common = {
            "sample_id": template_id,
            "source_template_id": template_id,
            "source_length": length,
            "label": str(source_row["label"]),
            "source_species": str(source_row.get("species", "")),
        }
        rows.append(
            {
                **common,
                "variant": "clean",
                "spatial_pattern": "clean",
                "chemistry": "clean",
                "sequence": sequence,
                "n_changes": 0,
            }
        )
        for spatial_pattern, positions in [
            ("dispersed", dispersed),
            ("contiguous", contiguous),
        ]:
            for chemistry in ["random", "property"]:
                rows.append(
                    {
                        **common,
                        "variant": f"{spatial_pattern}_{chemistry}",
                        "spatial_pattern": spatial_pattern,
                        "chemistry": chemistry,
                        "sequence": mutate_sequence(sequence, positions, chemistry, rng),
                        "n_changes": n_changes,
                    }
                )
    return pd.DataFrame(rows)


def normalize_rows(matrix: np.ndarray) -> np.ndarray:
    matrix = np.nan_to_num(np.asarray(matrix, dtype=float), nan=0.0, posinf=0.0, neginf=0.0)
    norms = np.linalg.norm(matrix, axis=1, keepdims=True)
    return matrix / np.maximum(norms, 1e-12)


def representation_matrices(sequences: list[str], length: int) -> dict[str, np.ndarray]:
    features = build_ck4p_msp_features(sequences, train_indices=list(range(len(sequences))))
    matrices = {
        "ck4": features.ck4,
        "ck4_p": build_block_combination(features, "ck4_p"),
        "ck4_msp": build_block_combination(features, "ck4_msp"),
        "ck4p_msp": features.matrix,
    }
    for name in ["pseknc_k3_l3", "pseeiip", "ncp_anf"]:
        matrices[name] = build_historical_descriptor_matrix(sequences, name, length=length)
    return {name: normalize_rows(matrix) for name, matrix in matrices.items()}


def grouped_readout(
    matrix: np.ndarray,
    metadata: pd.DataFrame,
    target: str,
    seed: int,
    cv_folds: int,
) -> tuple[float, float, float, float]:
    subset = metadata[metadata["variant"].ne("clean")].reset_index(drop=True)
    features = matrix[subset["_matrix_index"].to_numpy()]
    labels = subset[target].astype(str).to_numpy()
    groups = subset["sample_id"].astype(str).to_numpy()
    splitter = StratifiedGroupKFold(n_splits=cv_folds, shuffle=True, random_state=seed)
    accuracy: list[float] = []
    macro_f1: list[float] = []
    for train_idx, test_idx in splitter.split(features, labels, groups):
        model = make_pipeline(
            StandardScaler(),
            LogisticRegression(max_iter=4000, random_state=seed),
        )
        model.fit(features[train_idx], labels[train_idx])
        predicted = model.predict(features[test_idx])
        accuracy.append(float(accuracy_score(labels[test_idx], predicted)))
        macro_f1.append(float(f1_score(labels[test_idx], predicted, average="macro", zero_division=0)))
    return (
        float(np.mean(accuracy)),
        float(np.std(accuracy)),
        float(np.mean(macro_f1)),
        float(np.std(macro_f1)),
    )


def audit(
    reads: pd.DataFrame,
    seed: int,
    cv_folds: int,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    metric_rows: list[dict[str, object]] = []
    readout_rows: list[dict[str, object]] = []
    for length, group in reads.groupby("source_length", sort=True):
        group = group.reset_index(drop=True)
        matrices = representation_matrices(group["sequence"].astype(str).tolist(), int(length))
        clean_indices = group.index[group["variant"].eq("clean")].tolist()
        clean_by_template = {
            str(group.loc[index, "sample_id"]): index for index in clean_indices
        }
        variants = group[group["variant"].ne("clean")].copy()
        variants["_matrix_index"] = variants.index
        for representation, matrix in matrices.items():
            for _, row in variants.iterrows():
                clean_index = clean_by_template[str(row["sample_id"])]
                perturbed_index = int(row["_matrix_index"])
                clean_vector = matrix[clean_index]
                perturbed_vector = matrix[perturbed_index]
                metric_rows.append(
                    {
                        "sample_id": str(row["sample_id"]),
                        "length": int(length),
                        "representation": representation,
                        "representation_label": LABELS[representation],
                        "variant": str(row["variant"]),
                        "spatial_pattern": str(row["spatial_pattern"]),
                        "chemistry": str(row["chemistry"]),
                        "l2_drift": float(np.linalg.norm(clean_vector - perturbed_vector)),
                        "paired_cosine": float(np.dot(clean_vector, perturbed_vector)),
                        "n_features": int(matrix.shape[1]),
                    }
                )
            for target in ["spatial_pattern", "chemistry"]:
                accuracy, accuracy_sd, macro_f1, macro_f1_sd = grouped_readout(
                    matrix,
                    group.assign(_matrix_index=np.arange(len(group))),
                    target=target,
                    seed=seed + int(length) + len(target),
                    cv_folds=cv_folds,
                )
                readout_rows.append(
                    {
                        "length": int(length),
                        "representation": representation,
                        "representation_label": LABELS[representation],
                        "target": target,
                        "accuracy_mean": accuracy,
                        "accuracy_sd": accuracy_sd,
                        "macro_f1_mean": macro_f1,
                        "macro_f1_sd": macro_f1_sd,
                        "n_templates": int(group["sample_id"].nunique()),
                        "n_features": int(matrix.shape[1]),
                        "cv_folds": int(cv_folds),
                    }
                )
    metrics = pd.DataFrame(metric_rows)
    readout = pd.DataFrame(readout_rows)
    summary = (
        metrics.groupby(["length", "representation", "representation_label"], as_index=False)
        .agg(
            n_templates=("sample_id", "nunique"),
            l2_drift_mean=("l2_drift", "mean"),
            l2_drift_p95=("l2_drift", lambda values: float(np.quantile(values, 0.95))),
            paired_cosine_mean=("paired_cosine", "mean"),
            n_features=("n_features", "first"),
        )
    )
    readout_summary = (
        readout.groupby(["length", "representation", "representation_label"], as_index=False)
        .agg(
            spatial_macro_f1=("macro_f1_mean", lambda values: float(values.iloc[0])),
            chemistry_macro_f1=("macro_f1_mean", lambda values: float(values.iloc[-1])),
        )
    )
    summary = summary.merge(
        readout_summary,
        on=["length", "representation", "representation_label"],
        how="left",
    )
    return metrics, readout, summary


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--source-reads",
        default=str(PROJECT_ROOT / "data" / "real_slices" / "close_relative_reads.csv"),
    )
    parser.add_argument(
        "--output-dir",
        default=str(PROJECT_ROOT / "results" / "decision_stage" / "e3_natural_local_factorial"),
    )
    parser.add_argument("--lengths", default="69,75,100,150")
    parser.add_argument("--max-per-length", type=int, default=250)
    parser.add_argument("--mutation-fraction", type=float, default=0.03)
    parser.add_argument("--cv-folds", type=int, default=5)
    parser.add_argument("--seed", type=int, default=20260804)
    args = parser.parse_args()

    started = time.time()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    lengths = [int(item) for item in args.lengths.split(",") if item.strip()]
    source = pd.read_csv(args.source_reads)
    source["source_length"] = source["source_length"].astype(int)
    reads = build_natural_factorial_reads(
        source,
        lengths=lengths,
        max_per_length=args.max_per_length,
        mutation_fraction=args.mutation_fraction,
        seed=args.seed,
    )
    metrics, readout, summary = audit(reads, seed=args.seed, cv_folds=args.cv_folds)
    reads.to_csv(output_dir / "natural_local_factorial_reads.csv", index=False, encoding="utf-8-sig")
    metrics.to_csv(output_dir / "natural_local_factorial_metrics.csv", index=False, encoding="utf-8-sig")
    readout.to_csv(output_dir / "natural_local_factorial_readout.csv", index=False, encoding="utf-8-sig")
    summary.to_csv(output_dir / "natural_local_factorial_summary.csv", index=False, encoding="utf-8-sig")
    metadata = {
        "elapsed_seconds": round(time.time() - started, 3),
        "source_reads": str(Path(args.source_reads).resolve()),
        "lengths": lengths,
        "max_per_length": args.max_per_length,
        "mutation_fraction": args.mutation_fraction,
        "cv_folds": args.cv_folds,
        "n_templates": int(reads["sample_id"].nunique()),
        "paired_unit": "natural WGS-derived source template",
        "readout_split": "StratifiedGroupKFold; all variants of one source template stay in one fold",
        "negative_result_rule": "loss of the synthetic local-readout pattern on natural templates narrows the claim to a mechanism-aligned probe",
        "seed": args.seed,
    }
    (output_dir / "natural_local_factorial_run.json").write_text(
        json.dumps(metadata, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    (output_dir / "natural_local_factorial_summary.md").write_text(
        "# E3：自然 WGS 模板局部/因子审计\n\n"
        "该审计把原本的空间/化学因子设计应用到自然 WGS-derived clean templates。它检验合成局部探针中的模块差异是否能在自然碱基组成和 motif 背景下重复；它不等价于临床任务验证。\n\n"
        + summary.to_markdown(index=False, floatfmt=".5f")
        + "\n\n## 固定模板分组读出\n\n"
        + readout.to_markdown(index=False, floatfmt=".5f")
        + "\n",
        encoding="utf-8",
    )
    print(f"Wrote E3 natural-template audit to {output_dir}")


if __name__ == "__main__":
    main()
