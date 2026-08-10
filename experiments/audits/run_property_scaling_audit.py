"""Audit sensitivity to within-block property scaling and P-coordinate groups."""

from __future__ import annotations

import argparse
import json
import math
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler, normalize


def _find_project_root(start: Path) -> Path:
    for candidate in [start.parent, *start.parents]:
        if (candidate / "methods").is_dir() and (candidate / "configs").is_dir():
            return candidate
    raise RuntimeError("Could not locate the release repository root.")


PROJECT_ROOT = _find_project_root(Path(__file__).resolve())
sys.path.insert(0, str(PROJECT_ROOT))

from experiments.main.run_stage2_representation_grid import paired_subsets, parse_csv_list, parse_int_list  # noqa: E402
from methods.ck4p_msp import build_ck4p_msp_features  # noqa: E402
from methods.base_encodings import EIIP, GC, HYDROGEN, PURINE  # noqa: E402
from methods.sequence_utils import shannon_entropy  # noqa: E402
from methods.spaced_features import property_summary_matrix  # noqa: E402
from methods.stage2_features import paired_retrieval_metrics  # noqa: E402


P_GROUPS = {
    "hydrogen": [0, 1],
    "gc": [2, 3],
    "purine": [4, 5],
    "eiip": [6, 7],
    "n_fraction": [8],
    "scaled_length": [9],
    "entropy": [10],
}
PROPERTY_TABLES = [HYDROGEN, GC, PURINE, EIIP]


def safe_norm(matrix: np.ndarray) -> np.ndarray:
    values = np.nan_to_num(np.asarray(matrix, dtype=np.float64), nan=0.0, posinf=0.0, neginf=0.0)
    return normalize(values, norm="l2", axis=1)


def train_standardized(matrix: np.ndarray, n_clean: int) -> np.ndarray:
    scaler = StandardScaler().fit(matrix[:n_clean])
    return safe_norm(scaler.transform(matrix))


def fixed_combine(*blocks: np.ndarray) -> np.ndarray:
    return np.hstack([safe_norm(block) for block in blocks]) / np.sqrt(float(len(blocks)))


def unit_range_tables() -> list[dict[str, float]]:
    scaled = []
    for table in PROPERTY_TABLES:
        values = np.asarray([table[base] for base in "ACGT"], dtype=np.float64)
        low, high = float(values.min()), float(values.max())
        width = max(high - low, 1e-12)
        scaled.append({base: (float(table[base]) - low) / width for base in "ACGT"} | {"N": 0.0})
    return scaled


def range_scaled_property_blocks(sequences: list[str], bins: tuple[int, ...] = (2, 3, 4, 6)) -> tuple[np.ndarray, np.ndarray]:
    tables = unit_range_tables()
    p_rows = []
    msp_rows = []
    for sequence in sequences:
        bases = [base for base in sequence.upper() if base in "ACGTN"] or ["N"]
        signal = np.asarray(
            [[table.get(base, 0.0) for table in tables] + [1.0 if base == "N" else 0.0] for base in bases],
            dtype=np.float64,
        )
        p_values = []
        for column in range(4):
            p_values.extend([float(signal[:, column].mean()), float(signal[:, column].std())])
        p_values.extend(
            [
                float(signal[:, 4].mean()),
                len(sequence) / 200.0,
                shannon_entropy(sequence) / math.log2(5),
            ]
        )
        p_rows.append(p_values)
        pooled = []
        for n_bins in bins:
            edges = np.linspace(0, len(bases), n_bins + 1)
            for left_value, right_value in zip(edges[:-1], edges[1:]):
                left = int(np.floor(left_value))
                right = max(left + 1, int(np.floor(right_value)))
                right = min(right, len(bases))
                pooled.extend(signal[left:right].mean(axis=0).tolist())
        msp_rows.append(pooled)
    return safe_norm(np.asarray(p_rows)), safe_norm(np.asarray(msp_rows))


def run_audit(
    reads: pd.DataFrame,
    lengths: list[int],
    conditions: list[str],
    max_pairs: int,
    seed: int,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    scaling_rows = []
    ablation_rows = []
    for length in lengths:
        for condition in conditions:
            clean, perturbed = paired_subsets(reads, length, condition)
            if clean.empty:
                continue
            if max_pairs > 0 and len(clean) > max_pairs:
                keep = clean["clean_read_id"].drop_duplicates().sample(
                    n=max_pairs,
                    random_state=seed + length,
                ).tolist()
                clean = clean[clean["clean_read_id"].isin(keep)].sort_values("clean_read_id").reset_index(drop=True)
                perturbed = perturbed[perturbed["clean_read_id"].isin(keep)].sort_values("clean_read_id").reset_index(drop=True)
            sequences = clean["sequence"].astype(str).tolist() + perturbed["sequence"].astype(str).tolist()
            n = len(clean)
            features = build_ck4p_msp_features(sequences, train_indices=list(range(n)))
            p_standardized = train_standardized(features.p, n)
            msp_standardized = train_standardized(features.msp, n)
            p_range, msp_range = range_scaled_property_blocks(sequences)
            raw_p = property_summary_matrix(sequences)
            p_property = safe_norm(raw_p[:, :8])
            p_auxiliary = safe_norm(raw_p[:, 8:])
            representations = {
                "P_declared": features.p,
                "P_property_only": p_property,
                "P_auxiliary_only": p_auxiliary,
                "P_train_zscore": p_standardized,
                "P_unit_range": p_range,
                "MSP_declared": features.msp,
                "MSP_train_zscore": msp_standardized,
                "MSP_unit_range": msp_range,
                "CK4+P_declared": fixed_combine(features.ck4, features.p),
                "CK4+P_property_only": fixed_combine(features.ck4, p_property),
                "CK4+P_auxiliary_only": fixed_combine(features.ck4, p_auxiliary),
                "CK4+P_train_zscore": fixed_combine(features.ck4, p_standardized),
                "CK4+P_unit_range": fixed_combine(features.ck4, p_range),
                "CK4P-MSP_declared": fixed_combine(features.ck4, features.p, features.msp),
                "CK4P-MSP_property_only": fixed_combine(features.ck4, p_property, features.msp),
                "CK4P-MSP_auxiliary_only": fixed_combine(features.ck4, p_auxiliary, features.msp),
                "CK4P-MSP_train_zscore": fixed_combine(features.ck4, p_standardized, msp_standardized),
                "CK4P-MSP_unit_range": fixed_combine(features.ck4, p_range, msp_range),
            }
            for name, matrix in representations.items():
                metrics = paired_retrieval_metrics(matrix[:n], matrix[n:])
                scaling_rows.append(
                    {
                        "length": int(length),
                        "condition": condition,
                        "representation": name,
                        "n_pairs": int(n),
                        "n_features": int(matrix.shape[1]),
                        **metrics,
                    }
                )

            for omitted, indices in {"none": [], **P_GROUPS}.items():
                keep_indices = [idx for idx in range(raw_p.shape[1]) if idx not in indices]
                reduced_p = safe_norm(raw_p[:, keep_indices])
                matrix = fixed_combine(features.ck4, reduced_p)
                metrics = paired_retrieval_metrics(matrix[:n], matrix[n:])
                ablation_rows.append(
                    {
                        "length": int(length),
                        "condition": condition,
                        "omitted_p_group": omitted,
                        "n_pairs": int(n),
                        "p_features_remaining": int(len(keep_indices)),
                        **metrics,
                    }
                )
    return pd.DataFrame(scaling_rows), pd.DataFrame(ablation_rows)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", default=str(PROJECT_ROOT / "results" / "stage3" / "contract_v2" / "compact_baselines" / "stage3_compact_baseline_reads.csv"))
    parser.add_argument("--output-dir", default=str(PROJECT_ROOT / "results" / "stage3" / "contract_v2" / "property_scaling"))
    parser.add_argument("--lengths", default="69,75,100,150")
    parser.add_argument("--conditions", default="substitution_1pct,N_3pct,trim_5bp,substitution_1pct_N_3pct,local_mismatch_6bp,short_indel")
    parser.add_argument("--max-pairs", type=int, default=250)
    parser.add_argument("--seed", type=int, default=20260728)
    args = parser.parse_args()

    started = time.time()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    reads = pd.read_csv(args.input)
    scaling, ablation = run_audit(
        reads,
        lengths=parse_int_list(args.lengths),
        conditions=parse_csv_list(args.conditions),
        max_pairs=args.max_pairs,
        seed=args.seed,
    )
    scaling.to_csv(output_dir / "property_scaling_stability.csv", index=False, encoding="utf-8-sig")
    ablation.to_csv(output_dir / "p_group_ablation_stability.csv", index=False, encoding="utf-8-sig")
    scaling_summary = (
        scaling.groupby("representation", as_index=False)
        .agg(
            n_cells=("l2_delta_mean", "count"),
            paired_cosine=("paired_cosine_mean", "mean"),
            l2_drift=("l2_delta_mean", "mean"),
            retrieval_top1=("retrieval_top1", "mean"),
        )
        .sort_values("l2_drift")
    )
    ablation_summary = (
        ablation.groupby("omitted_p_group", as_index=False)
        .agg(
            n_cells=("l2_delta_mean", "count"),
            paired_cosine=("paired_cosine_mean", "mean"),
            l2_drift=("l2_delta_mean", "mean"),
            retrieval_top1=("retrieval_top1", "mean"),
        )
        .sort_values("l2_drift")
    )
    scaling_summary.to_csv(output_dir / "property_scaling_summary.csv", index=False, encoding="utf-8-sig")
    ablation_summary.to_csv(output_dir / "p_group_ablation_summary.csv", index=False, encoding="utf-8-sig")
    metadata = {
        "elapsed_seconds": time.time() - started,
        "input": args.input,
        "lengths": parse_int_list(args.lengths),
        "conditions": parse_csv_list(args.conditions),
        "max_pairs": args.max_pairs,
        "seed": args.seed,
        "scaling_boundary": "Train-fitted coordinate z-scoring is a sensitivity analysis, not the declared method.",
        "p_attribution": {
            "property_only_columns": "hydrogen, GC, purine and EIIP means and population standard deviations (8 coordinates)",
            "auxiliary_only_columns": "N fraction, scaled length and normalized entropy (3 coordinates)",
            "purpose": "separate nucleotide-property summaries from auxiliary global read-level summaries without changing the declared CK4P-MSP representation",
        },
    }
    (output_dir / "property_scaling_run.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    (output_dir / "property_scaling_summary.md").write_text(
        "# Property scaling audit\n\n"
        "The declared row-normalized encoding is compared with train-fitted coordinate z-scoring. "
        "The latter is a sensitivity analysis and does not redefine CK4P-MSP.\n\n"
        "## Scaling sensitivity\n\n"
        + scaling_summary.to_markdown(index=False, floatfmt=".4f")
        + "\n\n## P-group leave-one-out audit\n\n"
        + ablation_summary.to_markdown(index=False, floatfmt=".4f")
        + "\n",
        encoding="utf-8",
    )
    print(f"Wrote property scaling audit to {output_dir}")


if __name__ == "__main__":
    main()
