"""Separate spatial localization from substitution chemistry in local-change audits."""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import wilcoxon
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score
from sklearn.model_selection import StratifiedGroupKFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler


def _find_project_root(start: Path) -> Path:
    for candidate in [start.parent, *start.parents]:
        if (candidate / "methods").is_dir() and (candidate / "configs").is_dir():
            return candidate
    raise RuntimeError("Could not locate the release repository root.")


PROJECT_ROOT = _find_project_root(Path(__file__).resolve())
sys.path.insert(0, str(PROJECT_ROOT))

from methods.ck4p_msp import build_block_combination, build_ck4p_msp_features  # noqa: E402


BASES = np.asarray(list("ACGT"))
PROPERTY_SHIFT = {"A": "C", "C": "A", "G": "T", "T": "G", "N": "A"}
REPRESENTATIONS = ["ck4", "p", "msp", "ck4_p", "ck4_msp", "p_msp", "ck4p_msp"]
REP_LABELS = {
    "ck4": "CK4",
    "p": "P",
    "msp": "MSP",
    "ck4_p": "CK4+P",
    "ck4_msp": "CK4+MSP",
    "p_msp": "P+MSP",
    "ck4p_msp": "CK4P-MSP",
}
VARIANTS = ["dispersed_random", "contiguous_random", "dispersed_property", "contiguous_property"]
CONDITIONAL_COMPARATORS = {
    "K | P+MSP": "p_msp",
    "P | CK4+MSP": "ck4_msp",
    "MSP | CK4+P": "ck4_p",
}


def parse_int_list(value: str) -> list[int]:
    return [int(item.strip()) for item in value.split(",") if item.strip()]


def parse_csv_list(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


def random_read(rng: np.random.Generator, length: int) -> str:
    return "".join(rng.choice(BASES, size=length, replace=True).tolist())


def local_positions(length: int, n_changes: int, mode: str, rng: np.random.Generator) -> list[int]:
    if mode == "center":
        center = length // 2
    elif mode == "left":
        center = length // 4
    elif mode == "right":
        center = (3 * length) // 4
    elif mode == "jittered":
        center = int(rng.integers(max(0, length // 4), max(1, (3 * length) // 4)))
    else:
        raise ValueError(f"Unsupported local mode: {mode}")
    start = max(0, min(length - n_changes, center - n_changes // 2))
    return list(range(start, start + n_changes))


def mutate(
    sequence: str,
    positions: list[int],
    chemistry: str,
    rng: np.random.Generator,
) -> str:
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


def make_factorial_reads(
    lengths: list[int],
    local_modes: list[str],
    n_reads: int,
    mutation_fraction: float,
    seed: int,
) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    rows = []
    for length in lengths:
        n_changes = max(1, int(round(length * mutation_fraction)))
        for mode in local_modes:
            for read_id in range(n_reads):
                clean = random_read(rng, length)
                dispersed = sorted(rng.choice(np.arange(length), size=n_changes, replace=False).astype(int).tolist())
                contiguous = local_positions(length, n_changes, mode, rng)
                sample_id = f"L{length}_{mode}_{read_id:05d}"
                rows.append(
                    {
                        "sample_id": sample_id,
                        "source_length": length,
                        "local_mode": mode,
                        "variant": "clean",
                        "spatial_pattern": "clean",
                        "chemistry": "clean",
                        "sequence": clean,
                        "n_changes": 0,
                    }
                )
                for spatial_pattern, positions in [("dispersed", dispersed), ("contiguous", contiguous)]:
                    for chemistry in ["random", "property"]:
                        rows.append(
                            {
                                "sample_id": sample_id,
                                "source_length": length,
                                "local_mode": mode,
                                "variant": f"{spatial_pattern}_{chemistry}",
                                "spatial_pattern": spatial_pattern,
                                "chemistry": chemistry,
                                "sequence": mutate(clean, positions, chemistry, rng),
                                "n_changes": n_changes,
                            }
                        )
    return pd.DataFrame(rows)


def grouped_readout(
    deltas: np.ndarray,
    metadata: pd.DataFrame,
    target: str,
    seed: int,
    cv_folds: int,
) -> tuple[float, float, float, float]:
    labels = metadata[target].astype(str).to_numpy()
    groups = metadata["sample_id"].astype(str).to_numpy()
    splitter = StratifiedGroupKFold(n_splits=cv_folds, shuffle=True, random_state=seed)
    accuracy, macro_f1 = [], []
    for train_idx, test_idx in splitter.split(deltas, labels, groups):
        model = make_pipeline(
            StandardScaler(),
            LogisticRegression(max_iter=5000, random_state=seed),
        )
        model.fit(deltas[train_idx], labels[train_idx])
        predicted = model.predict(deltas[test_idx])
        accuracy.append(float(accuracy_score(labels[test_idx], predicted)))
        macro_f1.append(float(f1_score(labels[test_idx], predicted, average="macro", zero_division=0)))
    return float(np.mean(accuracy)), float(np.std(accuracy)), float(np.mean(macro_f1)), float(np.std(macro_f1))


def bootstrap_mean_ci(values: np.ndarray, seed: int, n_bootstrap: int = 10000) -> tuple[float, float]:
    rng = np.random.default_rng(seed)
    indices = rng.integers(0, len(values), size=(n_bootstrap, len(values)))
    means = values[indices].mean(axis=1)
    return float(np.quantile(means, 0.025)), float(np.quantile(means, 0.975))


def benjamini_hochberg(p_values: list[float]) -> list[float]:
    values = np.asarray(p_values, dtype=np.float64)
    order = np.argsort(values)
    adjusted = np.empty_like(values)
    running = 1.0
    for reverse_position, index in enumerate(order[::-1], start=1):
        rank = len(values) - reverse_position + 1
        running = min(running, values[index] * len(values) / rank)
        adjusted[index] = min(running, 1.0)
    return adjusted.tolist()


def conditional_readout_contrasts(readout: pd.DataFrame, seed: int) -> pd.DataFrame:
    rows = []
    full = "ck4p_msp"
    for contrast_idx, (contrast, comparator) in enumerate(CONDITIONAL_COMPARATORS.items()):
        for target_idx, target in enumerate(["spatial_pattern", "chemistry"]):
            subset = readout[
                readout["representation"].isin([full, comparator]) & readout["target"].eq(target)
            ]
            pivot = subset.pivot_table(
                index=["length", "local_mode"],
                columns="representation",
                values="macro_f1_mean",
                aggfunc="mean",
            )[[full, comparator]].dropna()
            differences = pivot[full].to_numpy(dtype=float) - pivot[comparator].to_numpy(dtype=float)
            ci_low, ci_high = bootstrap_mean_ci(
                differences,
                seed=seed + 100 * contrast_idx + target_idx,
            )
            p_value = (
                1.0
                if np.allclose(differences, 0.0)
                else float(wilcoxon(differences, alternative="two-sided", zero_method="wilcox").pvalue)
            )
            rows.append(
                {
                    "contrast": contrast,
                    "target": target,
                    "paired_unit": "length+local_mode",
                    "n_cells": int(len(differences)),
                    "full_mean": float(pivot[full].mean()),
                    "comparator_mean": float(pivot[comparator].mean()),
                    "mean_macro_f1_difference": float(np.mean(differences)),
                    "bootstrap_95_ci_low": ci_low,
                    "bootstrap_95_ci_high": ci_high,
                    "wilcoxon_two_sided_p": p_value,
                }
            )
    output = pd.DataFrame(rows)
    output["bh_q"] = benjamini_hochberg(output["wilcoxon_two_sided_p"].tolist())
    return output


def run_audit(reads: pd.DataFrame, seed: int, cv_folds: int) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    metric_rows = []
    readout_rows = []
    for (length, mode), cell in reads.groupby(["source_length", "local_mode"], sort=True):
        sample_ids = sorted(cell["sample_id"].unique())
        ordered = []
        for variant in ["clean", *VARIANTS]:
            ordered.extend(cell[cell["variant"].eq(variant)].set_index("sample_id").loc[sample_ids, "sequence"].tolist())
        n = len(sample_ids)
        features = build_ck4p_msp_features(ordered, train_indices=list(range(n)))
        clean_metadata = cell[cell["variant"].eq("clean")].set_index("sample_id").loc[sample_ids]
        del clean_metadata
        variant_metadata = pd.concat(
            [cell[cell["variant"].eq(variant)].set_index("sample_id").loc[sample_ids].reset_index() for variant in VARIANTS],
            ignore_index=True,
        )
        for representation in REPRESENTATIONS:
            matrix = build_block_combination(features, representation)
            clean = matrix[:n]
            variant_blocks = {
                variant: matrix[(idx + 1) * n : (idx + 2) * n]
                for idx, variant in enumerate(VARIANTS)
            }
            delta_blocks = []
            for variant in VARIANTS:
                delta = np.abs(variant_blocks[variant] - clean)
                delta_blocks.append(delta)
                l2 = np.linalg.norm(delta, axis=1)
                for sample_id, value in zip(sample_ids, l2):
                    metric_rows.append(
                        {
                            "sample_id": sample_id,
                            "length": int(length),
                            "local_mode": str(mode),
                            "representation": representation,
                            "representation_label": REP_LABELS[representation],
                            "variant": variant,
                            "spatial_pattern": variant.split("_", 1)[0],
                            "chemistry": variant.split("_", 1)[1],
                            "l2_drift": float(value),
                            "n_features": int(matrix.shape[1]),
                        }
                    )
            all_deltas = np.vstack(delta_blocks)
            for target in ["spatial_pattern", "chemistry"]:
                accuracy_mean, accuracy_std, f1_mean, f1_std = grouped_readout(
                    all_deltas,
                    variant_metadata,
                    target=target,
                    seed=seed + int(length) + len(str(mode)) + len(target),
                    cv_folds=cv_folds,
                )
                readout_rows.append(
                    {
                        "length": int(length),
                        "local_mode": str(mode),
                        "representation": representation,
                        "representation_label": REP_LABELS[representation],
                        "target": target,
                        "accuracy_mean": accuracy_mean,
                        "accuracy_std": accuracy_std,
                        "macro_f1_mean": f1_mean,
                        "macro_f1_std": f1_std,
                        "n_templates": int(n),
                        "n_features": int(matrix.shape[1]),
                        "cv_folds": int(cv_folds),
                    }
                )
    metrics = pd.DataFrame(metric_rows)
    readout = pd.DataFrame(readout_rows)
    pivot = metrics.pivot_table(
        index=["sample_id", "length", "local_mode", "representation", "representation_label", "n_features"],
        columns=["spatial_pattern", "chemistry"],
        values="l2_drift",
        aggfunc="mean",
    ).reset_index()
    pivot.columns = ["_".join(col).strip("_") if isinstance(col, tuple) else col for col in pivot.columns]
    pivot["spatial_effect"] = 0.5 * (
        pivot["contiguous_property"] + pivot["contiguous_random"]
        - pivot["dispersed_property"] - pivot["dispersed_random"]
    )
    pivot["chemistry_effect"] = 0.5 * (
        pivot["contiguous_property"] + pivot["dispersed_property"]
        - pivot["contiguous_random"] - pivot["dispersed_random"]
    )
    summary = (
        pivot.groupby(["representation", "representation_label"], as_index=False)
        .agg(
            n_template_cells=("sample_id", "count"),
            n_features=("n_features", "median"),
            spatial_effect_mean=("spatial_effect", "mean"),
            chemistry_effect_mean=("chemistry_effect", "mean"),
        )
        .merge(
            readout.groupby(["representation", "representation_label", "target"], as_index=False)["macro_f1_mean"].mean()
            .pivot(index=["representation", "representation_label"], columns="target", values="macro_f1_mean")
            .reset_index()
            .rename(columns={"spatial_pattern": "spatial_readout_macro_f1", "chemistry": "chemistry_readout_macro_f1"}),
            on=["representation", "representation_label"],
            how="left",
        )
    )
    return metrics, readout, summary


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", default=str(PROJECT_ROOT / "results" / "stage3" / "contract_v2" / "local_change_factorial"))
    parser.add_argument("--lengths", default="69,100,150")
    parser.add_argument("--local-modes", default="center,left,right,jittered")
    parser.add_argument("--n-reads", type=int, default=250)
    parser.add_argument("--mutation-fraction", type=float, default=0.03)
    parser.add_argument("--cv-folds", type=int, default=5)
    parser.add_argument("--seed", type=int, default=20260728)
    args = parser.parse_args()

    started = time.time()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    reads = make_factorial_reads(
        lengths=parse_int_list(args.lengths),
        local_modes=parse_csv_list(args.local_modes),
        n_reads=args.n_reads,
        mutation_fraction=args.mutation_fraction,
        seed=args.seed,
    )
    metrics, readout, summary = run_audit(reads, seed=args.seed, cv_folds=args.cv_folds)
    contrasts = conditional_readout_contrasts(readout, seed=args.seed)
    reads.to_csv(output_dir / "local_change_factorial_reads.csv", index=False, encoding="utf-8-sig")
    metrics.to_csv(output_dir / "local_change_factorial_metrics.csv", index=False, encoding="utf-8-sig")
    readout.to_csv(output_dir / "local_change_factorial_readout.csv", index=False, encoding="utf-8-sig")
    summary.to_csv(output_dir / "local_change_factorial_summary.csv", index=False, encoding="utf-8-sig")
    contrasts.to_csv(output_dir / "local_change_factorial_conditional_contrasts.csv", index=False, encoding="utf-8-sig")
    metadata = {
        "elapsed_seconds": time.time() - started,
        "lengths": parse_int_list(args.lengths),
        "local_modes": parse_csv_list(args.local_modes),
        "n_reads_per_cell": args.n_reads,
        "mutation_fraction": args.mutation_fraction,
        "cv_folds": args.cv_folds,
        "seed": args.seed,
        "paired_unit": "template_id",
    }
    (output_dir / "local_change_factorial_run.json").write_text(
        json.dumps(metadata, indent=2), encoding="utf-8"
    )
    (output_dir / "local_change_factorial_summary.md").write_text(
        "# Local-change factorial audit\n\n"
        "This 2 x 2 audit separates spatial localization (contiguous versus dispersed) "
        "from substitution chemistry (property-directed versus random). All derivatives "
        "of one template remain in the same grouped-CV fold.\n\n"
        + summary.to_markdown(index=False, floatfmt=".4f")
        + "\n\n## Prespecified conditional readout contrasts\n\n"
        + contrasts.to_markdown(index=False, floatfmt=".4f")
        + "\n",
        encoding="utf-8",
    )
    print(f"Wrote local-change factorial audit to {output_dir}")


if __name__ == "__main__":
    main()
