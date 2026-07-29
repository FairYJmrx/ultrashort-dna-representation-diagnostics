"""Multi-target frozen-head label-retention audit on CAMI_TOY reads.

Six labels are prespecified by source-read abundance. For each one-versus-
background task, a logistic head is fitted only on 100-bp clean reads and is
reused without refitting under length, N-mask and substitution shifts. The
declared representation geometry is retained: no coordinate-wise scaler is
applied. Regularization values other than C=1 are sensitivity analyses only.
"""

from __future__ import annotations

import argparse
import gzip
import json
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import wilcoxon
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import f1_score
from sklearn.model_selection import StratifiedGroupKFold


def _find_project_root(start: Path) -> Path:
    for candidate in [start.parent, *start.parents]:
        if (candidate / "methods").is_dir() and (candidate / "configs").is_dir():
            return candidate
    raise RuntimeError("Could not locate the release repository root.")


PROJECT_ROOT = _find_project_root(Path(__file__).resolve())
sys.path.insert(0, str(PROJECT_ROOT))

from experiments.audits.run_cami_fixed_head_transfer import (  # noqa: E402
    DEFAULT_REPRESENTATIONS,
    REPRESENTATION_LABELS,
    build_representation_matrix,
    build_shifted_rows,
    metric_values,
    parse_csv_list,
    parse_int_list,
    select_balanced_source_reads,
)


DEFAULT_TARGETS = ",".join(
    [
        "tax_434085",
        "tax_247639",
        "tax_1050222",
        "tax_552396",
        "tax_1122939",
        "tax_1097667",
    ]
)
PRIMARY_C = 1.0
PRIMARY_COMPARATORS = [
    "ck4",
    "ck4_p",
    "ck4_msp",
    "ck5",
    "pseknc_k3_l3",
    "ncp_anf",
    "pseeiip",
    "hash_k15_d222",
]


def parse_float_list(text: str) -> list[float]:
    return [float(item) for item in parse_csv_list(text)]


def assign_folds(shifted: pd.DataFrame, n_splits: int, seed: int) -> pd.DataFrame:
    source = shifted[["source_id", "binary_label"]].drop_duplicates().sort_values("source_id")
    source_ids = source["source_id"].astype(str).to_numpy()
    y = source["binary_label"].to_numpy(dtype=int)
    splitter = StratifiedGroupKFold(n_splits=n_splits, shuffle=True, random_state=seed)
    fold_map: dict[str, int] = {}
    for fold, (_, test_idx) in enumerate(splitter.split(source_ids, y, groups=source_ids), start=1):
        for source_id in source_ids[test_idx]:
            fold_map[str(source_id)] = fold
    result = shifted.copy()
    result["fold"] = result["source_id"].astype(str).map(fold_map).astype(int)
    return result


def bootstrap_f1_interval(
    y: np.ndarray,
    pred: np.ndarray,
    *,
    n_bootstrap: int,
    seed: int,
) -> tuple[float, float]:
    rng = np.random.default_rng(seed)
    positive = y == 1
    negative = ~positive
    n_positive = int(np.sum(positive))
    n_negative = int(np.sum(negative))
    tp_probability = float(np.mean(pred[positive] == 1))
    tn_probability = float(np.mean(pred[negative] == 0))
    tp = rng.binomial(n_positive, tp_probability, size=n_bootstrap)
    tn = rng.binomial(n_negative, tn_probability, size=n_bootstrap)
    values = macro_f1_from_counts(tp, tn, n_positive, n_negative)
    return float(np.quantile(values, 0.025)), float(np.quantile(values, 0.975))


def macro_f1_from_counts(
    tp: np.ndarray,
    tn: np.ndarray,
    n_positive: int,
    n_negative: int,
) -> np.ndarray:
    tp = np.asarray(tp, dtype=float)
    tn = np.asarray(tn, dtype=float)
    fn = n_positive - tp
    fp = n_negative - tn
    positive_denominator = 2 * tp + fp + fn
    negative_denominator = 2 * tn + fp + fn
    positive_f1 = np.divide(
        2 * tp,
        positive_denominator,
        out=np.zeros_like(tp, dtype=float),
        where=positive_denominator > 0,
    )
    negative_f1 = np.divide(
        2 * tn,
        negative_denominator,
        out=np.zeros_like(tn, dtype=float),
        where=negative_denominator > 0,
    )
    return 0.5 * (positive_f1 + negative_f1)


def paired_bootstrap_differences(
    y: np.ndarray,
    primary_pred: np.ndarray,
    primary_base_pred: np.ndarray,
    other_pred: np.ndarray,
    other_base_pred: np.ndarray,
    *,
    n_bootstrap: int,
    seed: int,
) -> tuple[np.ndarray, np.ndarray]:
    """Stratified paired bootstrap through joint prediction patterns."""
    rng = np.random.default_rng(seed)
    predictions = np.column_stack(
        [primary_pred, primary_base_pred, other_pred, other_base_pred]
    ).astype(int)
    pattern = (
        predictions[:, 0]
        + 2 * predictions[:, 1]
        + 4 * predictions[:, 2]
        + 8 * predictions[:, 3]
    )
    model_bits = np.asarray(
        [[(code >> bit) & 1 for code in range(16)] for bit in range(4)],
        dtype=int,
    )
    f1_values: list[np.ndarray] = []
    positive_mask = y == 1
    negative_mask = ~positive_mask
    n_positive = int(np.sum(positive_mask))
    n_negative = int(np.sum(negative_mask))
    positive_counts = np.bincount(pattern[positive_mask], minlength=16)
    negative_counts = np.bincount(pattern[negative_mask], minlength=16)
    positive_draws = rng.multinomial(
        n_positive,
        positive_counts / positive_counts.sum(),
        size=n_bootstrap,
    )
    negative_draws = rng.multinomial(
        n_negative,
        negative_counts / negative_counts.sum(),
        size=n_bootstrap,
    )
    for bit in range(4):
        tp = positive_draws @ model_bits[bit]
        tn = negative_draws @ (1 - model_bits[bit])
        f1_values.append(macro_f1_from_counts(tp, tn, n_positive, n_negative))
    primary, primary_base, other, other_base = f1_values
    return primary - other, (primary - primary_base) - (other - other_base)


def run_target(
    shifted: pd.DataFrame,
    *,
    target_label: str,
    representations: list[str],
    c_values: list[float],
    n_splits: int,
    n_bootstrap: int,
    seed: int,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    shifted = assign_folds(shifted, n_splits=n_splits, seed=seed)
    source = shifted[["source_id", "binary_label", "fold"]].drop_duplicates().sort_values("source_id")
    source_ids = source["source_id"].astype(str).to_numpy()
    condition_cells = (
        shifted[["length", "condition"]]
        .drop_duplicates()
        .sort_values(["length", "condition"])
        .itertuples(index=False, name=None)
    )
    condition_cells = [(int(length), str(condition)) for length, condition in condition_cells]

    metric_rows: list[dict[str, object]] = []
    runtime_rows: list[dict[str, object]] = []
    primary_prediction_rows: list[dict[str, object]] = []
    primary_vectors: dict[tuple[str, int, str], tuple[np.ndarray, np.ndarray, np.ndarray]] = {}
    sequences = shifted["sequence"].astype(str).tolist()

    for representation_index, representation in enumerate(representations):
        feature_started = time.perf_counter()
        matrix, n_features = build_representation_matrix(sequences, representation)
        feature_seconds = time.perf_counter() - feature_started
        model_started = time.perf_counter()

        for c_value in c_values:
            cell_predictions: dict[tuple[int, str], list[tuple[str, int, int, float]]] = {
                cell: [] for cell in condition_cells
            }
            for fold in range(1, n_splits + 1):
                train_sources = set(source.loc[source["fold"].ne(fold), "source_id"].astype(str))
                train_mask = (
                    shifted["source_id"].astype(str).isin(train_sources)
                    & shifted["length"].eq(100)
                    & shifted["condition"].eq("clean")
                ).to_numpy()
                model = LogisticRegression(
                    C=c_value,
                    max_iter=3000,
                    class_weight="balanced",
                    random_state=seed + fold,
                )
                model.fit(matrix[train_mask], shifted.loc[train_mask, "binary_label"].to_numpy(dtype=int))

                test_source_mask = shifted["fold"].eq(fold).to_numpy()
                for length, condition in condition_cells:
                    test_mask = (
                        test_source_mask
                        & shifted["length"].eq(length).to_numpy()
                        & shifted["condition"].eq(condition).to_numpy()
                    )
                    y_true = shifted.loc[test_mask, "binary_label"].to_numpy(dtype=int)
                    y_pred = model.predict(matrix[test_mask]).astype(int)
                    y_score = model.predict_proba(matrix[test_mask])[:, 1]
                    ids = shifted.loc[test_mask, "source_id"].astype(str).to_numpy()
                    cell_predictions[(length, condition)].extend(
                        zip(ids.tolist(), y_true.tolist(), y_pred.tolist(), y_score.tolist())
                    )

            for cell_index, ((length, condition), values) in enumerate(cell_predictions.items()):
                ordered = sorted(values, key=lambda item: item[0])
                ids = np.asarray([item[0] for item in ordered], dtype=str)
                y = np.asarray([item[1] for item in ordered], dtype=int)
                pred = np.asarray([item[2] for item in ordered], dtype=int)
                score = np.asarray([item[3] for item in ordered], dtype=float)
                row = {
                    "target_label": target_label,
                    "representation": representation,
                    "representation_label": REPRESENTATION_LABELS[representation],
                    "n_features": n_features,
                    "c_value": c_value,
                    "length": length,
                    "condition": condition,
                    "n_test_sources": len(y),
                    **metric_values(y, pred, score),
                }
                if np.isclose(c_value, PRIMARY_C):
                    ci_low, ci_high = bootstrap_f1_interval(
                        y,
                        pred,
                        n_bootstrap=n_bootstrap,
                        seed=seed + 1000 * representation_index + 10 * cell_index,
                    )
                    row["macro_f1_ci_low"] = ci_low
                    row["macro_f1_ci_high"] = ci_high
                    primary_vectors[(representation, length, condition)] = (y, pred, ids)
                    primary_prediction_rows.extend(
                        {
                            "target_label": target_label,
                            "representation": representation,
                            "source_id": source_id,
                            "length": length,
                            "condition": condition,
                            "y_true": int(truth),
                            "y_pred": int(prediction),
                            "y_score": float(probability),
                        }
                        for source_id, truth, prediction, probability in ordered
                    )
                else:
                    row["macro_f1_ci_low"] = np.nan
                    row["macro_f1_ci_high"] = np.nan
                metric_rows.append(row)

        runtime_rows.append(
            {
                "target_label": target_label,
                "representation": representation,
                "representation_label": REPRESENTATION_LABELS[representation],
                "n_features": n_features,
                "n_variant_rows": len(shifted),
                "feature_seconds": feature_seconds,
                "model_seconds": time.perf_counter() - model_started,
            }
        )
        print(
            f"[cami-multitarget] {target_label} {representation}: "
            f"{n_features} features, feature={feature_seconds:.2f}s",
            flush=True,
        )

    metrics = pd.DataFrame(metric_rows)
    enriched: list[pd.DataFrame] = []
    for (representation, c_value), frame in metrics.groupby(["representation", "c_value"], sort=False):
        frame = frame.copy()
        baseline = frame[frame["length"].eq(100) & frame["condition"].eq("clean")]
        if len(baseline) != 1:
            raise ValueError(f"Missing baseline for {target_label}/{representation}/C={c_value}")
        baseline_f1 = float(baseline.iloc[0]["macro_f1"])
        frame["baseline_macro_f1"] = baseline_f1
        frame["delta_macro_f1"] = frame["macro_f1"] - baseline_f1
        frame["label_retention_ratio"] = frame["macro_f1"] / baseline_f1
        enriched.append(frame)
    metrics = pd.concat(enriched, ignore_index=True)

    contrast_rows: list[dict[str, object]] = []
    for cell_index, (length, condition) in enumerate(condition_cells):
        y, primary_pred, primary_ids = primary_vectors[("ck4p_msp", length, condition)]
        _, primary_base_pred, primary_base_ids = primary_vectors[("ck4p_msp", 100, "clean")]
        available_comparators = [item for item in PRIMARY_COMPARATORS if item in representations]
        for comparator_index, comparator in enumerate(available_comparators):
            other_y, other_pred, other_ids = primary_vectors[(comparator, length, condition)]
            _, other_base_pred, other_base_ids = primary_vectors[(comparator, 100, "clean")]
            if not (
                np.array_equal(y, other_y)
                and np.array_equal(primary_ids, other_ids)
                and np.array_equal(primary_ids, primary_base_ids)
                and np.array_equal(primary_ids, other_base_ids)
            ):
                raise ValueError("Primary predictions are not source-paired.")
            p = f1_score(y, primary_pred, average="macro", zero_division=0)
            pb = f1_score(y, primary_base_pred, average="macro", zero_division=0)
            o = f1_score(y, other_pred, average="macro", zero_division=0)
            ob = f1_score(y, other_base_pred, average="macro", zero_division=0)
            absolute, relative_drop = paired_bootstrap_differences(
                y,
                primary_pred,
                primary_base_pred,
                other_pred,
                other_base_pred,
                n_bootstrap=n_bootstrap,
                seed=seed + 10000 + 100 * cell_index + comparator_index,
            )
            contrast_rows.append(
                {
                    "target_label": target_label,
                    "length": length,
                    "condition": condition,
                    "comparator": comparator,
                    "absolute_f1_difference": p - o,
                    "absolute_ci_low": float(np.quantile(absolute, 0.025)),
                    "absolute_ci_high": float(np.quantile(absolute, 0.975)),
                    "relative_drop_difference": (p - pb) - (o - ob),
                    "relative_drop_ci_low": float(np.quantile(relative_drop, 0.025)),
                    "relative_drop_ci_high": float(np.quantile(relative_drop, 0.975)),
                }
            )

    return (
        metrics,
        pd.DataFrame(contrast_rows),
        pd.DataFrame(runtime_rows),
        pd.DataFrame(primary_prediction_rows),
    )


def benjamini_hochberg(p_values: np.ndarray) -> np.ndarray:
    p_values = np.asarray(p_values, dtype=float)
    order = np.argsort(p_values)
    ranked = p_values[order]
    adjusted = ranked * len(ranked) / np.arange(1, len(ranked) + 1)
    adjusted = np.minimum.accumulate(adjusted[::-1])[::-1]
    result = np.empty_like(adjusted)
    result[order] = np.minimum(adjusted, 1.0)
    return result


def aggregate_results(
    metrics: pd.DataFrame,
    contrasts: pd.DataFrame,
    *,
    n_bootstrap: int,
    seed: int,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    primary = metrics[np.isclose(metrics["c_value"], PRIMARY_C)].copy()
    primary["is_baseline"] = primary["length"].eq(100) & primary["condition"].eq("clean")
    shifted = primary[~primary["is_baseline"]].copy()
    target_summary = (
        shifted.groupby(["target_label", "representation", "representation_label", "n_features"], as_index=False)
        .agg(
            baseline_macro_f1=("baseline_macro_f1", "first"),
            mean_shifted_macro_f1=("macro_f1", "mean"),
            worst_shifted_macro_f1=("macro_f1", "min"),
            mean_retention=("label_retention_ratio", "mean"),
            worst_retention=("label_retention_ratio", "min"),
        )
    )
    aggregate = (
        target_summary.groupby(["representation", "representation_label", "n_features"], as_index=False)
        .agg(
            mean_baseline_macro_f1=("baseline_macro_f1", "mean"),
            mean_shifted_macro_f1=("mean_shifted_macro_f1", "mean"),
            min_target_shifted_macro_f1=("mean_shifted_macro_f1", "min"),
            mean_retention=("mean_retention", "mean"),
            min_target_retention=("mean_retention", "min"),
        )
        .sort_values(["mean_shifted_macro_f1", "mean_retention"], ascending=False)
    )

    shifted_contrasts = contrasts[
        ~(contrasts["length"].eq(100) & contrasts["condition"].eq("clean"))
    ].copy()
    target_contrasts = (
        shifted_contrasts.groupby(["target_label", "comparator"], as_index=False)
        .agg(
            mean_absolute_f1_difference=("absolute_f1_difference", "mean"),
            mean_relative_drop_difference=("relative_drop_difference", "mean"),
        )
    )
    aggregate_contrast_rows: list[dict[str, object]] = []
    for comparator_index, (comparator, frame) in enumerate(target_contrasts.groupby("comparator", sort=False)):
        frame = frame.sort_values("target_label")
        absolute = frame["mean_absolute_f1_difference"].to_numpy(dtype=float)
        relative = frame["mean_relative_drop_difference"].to_numpy(dtype=float)
        rng = np.random.default_rng(seed + 50000 + comparator_index)
        sampled = rng.integers(0, len(frame), size=(n_bootstrap, len(frame)))
        absolute_boot = absolute[sampled].mean(axis=1)
        relative_boot = relative[sampled].mean(axis=1)
        try:
            absolute_p = float(wilcoxon(absolute, alternative="two-sided").pvalue)
        except ValueError:
            absolute_p = 1.0
        try:
            relative_p = float(wilcoxon(relative, alternative="two-sided").pvalue)
        except ValueError:
            relative_p = 1.0
        aggregate_contrast_rows.append(
            {
                "comparator": comparator,
                "n_targets": len(frame),
                "mean_absolute_f1_difference": float(absolute.mean()),
                "absolute_target_bootstrap_ci_low": float(np.quantile(absolute_boot, 0.025)),
                "absolute_target_bootstrap_ci_high": float(np.quantile(absolute_boot, 0.975)),
                "absolute_target_wilcoxon_p": absolute_p,
                "n_targets_absolute_favour_ck4p_msp": int(np.sum(absolute > 0)),
                "mean_relative_drop_difference": float(relative.mean()),
                "relative_target_bootstrap_ci_low": float(np.quantile(relative_boot, 0.025)),
                "relative_target_bootstrap_ci_high": float(np.quantile(relative_boot, 0.975)),
                "relative_target_wilcoxon_p": relative_p,
                "n_targets_relative_favour_ck4p_msp": int(np.sum(relative > 0)),
            }
        )
    aggregate_contrasts = pd.DataFrame(aggregate_contrast_rows)
    p_columns = ["absolute_target_wilcoxon_p", "relative_target_wilcoxon_p"]
    combined = aggregate_contrasts[p_columns].to_numpy().reshape(-1)
    adjusted = benjamini_hochberg(combined).reshape(-1, len(p_columns))
    aggregate_contrasts["absolute_target_wilcoxon_q"] = adjusted[:, 0]
    aggregate_contrasts["relative_target_wilcoxon_q"] = adjusted[:, 1]

    c_sensitivity = (
        metrics[~(metrics["length"].eq(100) & metrics["condition"].eq("clean"))]
        .groupby(["representation", "representation_label", "c_value"], as_index=False)
        .agg(
            mean_shifted_macro_f1=("macro_f1", "mean"),
            mean_retention=("label_retention_ratio", "mean"),
            min_macro_f1=("macro_f1", "min"),
        )
    )
    return target_summary, aggregate, aggregate_contrasts, c_sensitivity


def write_summary(
    aggregate: pd.DataFrame,
    aggregate_contrasts: pd.DataFrame,
    c_sensitivity: pd.DataFrame,
    output_dir: Path,
) -> None:
    lines = [
        "# CAMI_TOY multi-target frozen-head audit",
        "",
        "The primary analysis uses the declared contract space and C=1. Six targets were prespecified by source-read abundance and capped at 1,200 target groups each. Target-level intervals resample six target tasks and therefore describe task-to-task consistency rather than population-level biological generalization.",
        "",
        "## Primary cross-target summary",
        "",
        aggregate.to_markdown(index=False, floatfmt=".4f"),
        "",
        "## CK4P-MSP paired cross-target contrasts",
        "",
        aggregate_contrasts.to_markdown(index=False, floatfmt=".4f"),
        "",
        "## Contract-space regularization sensitivity",
        "",
        c_sensitivity.to_markdown(index=False, floatfmt=".4f"),
    ]
    (output_dir / "cami_multitarget_fixed_head_summary.md").write_text(
        "\n".join(lines), encoding="utf-8"
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--reads-csv",
        default=str(PROJECT_ROOT / "data" / "stage3" / "cami" / "cami_toy_low_subset_reads_expanded.csv"),
    )
    parser.add_argument(
        "--output-dir",
        default=str(PROJECT_ROOT / "results" / "stage3" / "contract_v2" / "cami_multitarget_fixed_head"),
    )
    parser.add_argument("--target-labels", default=DEFAULT_TARGETS)
    parser.add_argument("--lengths", default="69,75,100")
    parser.add_argument("--conditions", default="clean,N_3pct,substitution_1pct")
    parser.add_argument("--representations", default=DEFAULT_REPRESENTATIONS)
    parser.add_argument("--c-values", default="0.1,1,10")
    parser.add_argument("--n-splits", type=int, default=5)
    parser.add_argument("--n-bootstrap", type=int, default=1000)
    parser.add_argument("--max-target-groups", type=int, default=1200)
    parser.add_argument("--seed", type=int, default=20260730)
    args = parser.parse_args()

    started = time.time()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    reads = pd.read_csv(args.reads_csv)
    target_labels = parse_csv_list(args.target_labels)
    lengths = parse_int_list(args.lengths)
    conditions = parse_csv_list(args.conditions)
    representations = parse_csv_list(args.representations)
    c_values = parse_float_list(args.c_values)
    if not any(np.isclose(c_values, PRIMARY_C)):
        raise ValueError("C=1 must be included as the prespecified primary probe.")

    all_metrics: list[pd.DataFrame] = []
    all_contrasts: list[pd.DataFrame] = []
    all_runtime: list[pd.DataFrame] = []
    manifest_rows: list[dict[str, object]] = []
    prediction_path = output_dir / "cami_multitarget_primary_predictions.csv.gz"
    if prediction_path.exists():
        prediction_path.unlink()
    wrote_header = False

    for target_index, target_label in enumerate(target_labels):
        target_seed = args.seed + 100000 * target_index
        source = select_balanced_source_reads(
            reads,
            target_label=target_label,
            seed=target_seed,
            max_target_groups=args.max_target_groups,
        )
        shifted = build_shifted_rows(
            source,
            lengths=lengths,
            conditions=conditions,
            seed=target_seed,
        )
        metrics, contrasts, runtime, predictions = run_target(
            shifted,
            target_label=target_label,
            representations=representations,
            c_values=c_values,
            n_splits=args.n_splits,
            n_bootstrap=args.n_bootstrap,
            seed=target_seed,
        )
        all_metrics.append(metrics)
        all_contrasts.append(contrasts)
        all_runtime.append(runtime)
        manifest_rows.append(
            {
                "target_label": target_label,
                "selection_rank": target_index + 1,
                "n_source_groups": len(source),
                "n_target_groups": int(source["binary_label"].sum()),
                "n_background_groups": int((1 - source["binary_label"]).sum()),
                "n_variant_rows": len(shifted),
                "seed": target_seed,
            }
        )
        predictions.to_csv(
            prediction_path,
            mode="at" if wrote_header else "wt",
            header=not wrote_header,
            index=False,
            compression="gzip",
        )
        wrote_header = True

    metrics = pd.concat(all_metrics, ignore_index=True)
    contrasts = pd.concat(all_contrasts, ignore_index=True)
    runtime = pd.concat(all_runtime, ignore_index=True)
    manifest = pd.DataFrame(manifest_rows)
    target_summary, aggregate, aggregate_contrasts, c_sensitivity = aggregate_results(
        metrics,
        contrasts,
        n_bootstrap=args.n_bootstrap,
        seed=args.seed,
    )

    metrics.to_csv(output_dir / "cami_multitarget_metrics.csv", index=False)
    contrasts.to_csv(output_dir / "cami_multitarget_source_bootstrap_contrasts.csv", index=False)
    runtime.to_csv(output_dir / "cami_multitarget_runtime.csv", index=False)
    manifest.to_csv(output_dir / "cami_multitarget_target_manifest.csv", index=False)
    target_summary.to_csv(output_dir / "cami_multitarget_target_summary.csv", index=False)
    aggregate.to_csv(output_dir / "cami_multitarget_aggregate.csv", index=False)
    aggregate_contrasts.to_csv(output_dir / "cami_multitarget_aggregate_contrasts.csv", index=False)
    c_sensitivity.to_csv(output_dir / "cami_multitarget_c_sensitivity.csv", index=False)
    write_summary(aggregate, aggregate_contrasts, c_sensitivity, output_dir)

    metadata = {
        "elapsed_seconds": time.time() - started,
        "reads_csv": str(args.reads_csv),
        "target_selection": "top six labels by deduplicated source-read abundance",
        "target_labels": target_labels,
        "max_target_groups": args.max_target_groups,
        "lengths": lengths,
        "conditions": conditions,
        "representations": representations,
        "c_values": c_values,
        "primary_c": PRIMARY_C,
        "probe_scaling": "contract",
        "n_splits": args.n_splits,
        "n_bootstrap": args.n_bootstrap,
        "seed": args.seed,
        "n_input_rows": len(reads),
    }
    (output_dir / "cami_multitarget_run.json").write_text(
        json.dumps(metadata, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(f"Wrote CAMI multi-target fixed-head audit to {output_dir}")


if __name__ == "__main__":
    main()
