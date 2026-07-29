"""Frozen-head label-retention audit on the labelled CAMI_TOY subset.

The audit trains one logistic probe on 100-bp clean reads and evaluates the
same fitted scaler and classifier on held-out source reads under length and
perturbation shifts. Mate reads sharing a ``clean_read_id`` are reduced to one
deterministic representative before splitting, so no source group can occur in
both training and testing.
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
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    balanced_accuracy_score,
    f1_score,
    matthews_corrcoef,
    roc_auc_score,
)
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

from experiments.audits.run_high_k_compressed_baselines import hashed_kmer_matrix  # noqa: E402
from experiments.main.run_stage2_representation_grid import apply_stage2_condition  # noqa: E402
from methods.ck4p_msp import (  # noqa: E402
    CK4PMSPConfig,
    build_block_combination,
    build_ck4_block,
    build_ck4p_msp_features,
)
from methods.historical_descriptors import build_historical_descriptor_matrix  # noqa: E402


REPRESENTATION_LABELS = {
    "ck4": "CK4",
    "ck4_p": "CK4+P",
    "ck4_msp": "CK4+MSP",
    "ck4p_msp": "CK4P-MSP",
    "ck5": "CK5",
    "pseknc_k3_l3": "PseKNC",
    "ncp_anf": "NCP+ANF",
    "pseeiip": "PseEIIP",
    "hash_k15_d222": "Hashed k=15",
}

DEFAULT_REPRESENTATIONS = ",".join(REPRESENTATION_LABELS)


def parse_csv_list(text: str) -> list[str]:
    return [item.strip() for item in text.split(",") if item.strip()]


def parse_int_list(text: str) -> list[int]:
    return [int(item) for item in parse_csv_list(text)]


def select_balanced_source_reads(
    reads: pd.DataFrame,
    *,
    target_label: str,
    seed: int,
    max_target_groups: int,
) -> pd.DataFrame:
    required = {"clean_read_id", "read_id", "sequence", "label"}
    missing = required - set(reads.columns)
    if missing:
        raise ValueError(f"Input is missing required columns: {sorted(missing)}")

    source = reads.copy()
    source["sequence"] = source["sequence"].astype(str).str.upper()
    source = source[source["sequence"].str.len() >= 100].copy()
    source = source.sort_values(["clean_read_id", "read_id"]).drop_duplicates("clean_read_id", keep="first")
    source["binary_label"] = source["label"].astype(str).eq(str(target_label)).astype(int)

    target = source[source["binary_label"].eq(1)].copy()
    background = source[source["binary_label"].eq(0)].copy()
    if target.empty or background.empty:
        raise ValueError("Both target and background source groups are required.")
    if max_target_groups > 0 and len(target) > max_target_groups:
        target = target.sample(n=max_target_groups, random_state=seed)

    n_target = len(target)
    labels = sorted(background["label"].astype(str).unique())
    quota = int(np.ceil(n_target / max(1, len(labels))))
    sampled_parts = [
        part.sample(n=min(quota, len(part)), random_state=seed + idx)
        for idx, (_, part) in enumerate(background.groupby("label", sort=True))
    ]
    sampled_background = pd.concat(sampled_parts, ignore_index=False)
    if len(sampled_background) < n_target:
        remaining = background.loc[~background.index.isin(sampled_background.index)]
        fill = remaining.sample(n=n_target - len(sampled_background), random_state=seed + 1000)
        sampled_background = pd.concat([sampled_background, fill], ignore_index=False)
    elif len(sampled_background) > n_target:
        sampled_background = sampled_background.sample(n=n_target, random_state=seed + 2000)

    selected = pd.concat([target, sampled_background], ignore_index=True)
    selected = selected.sample(frac=1.0, random_state=seed).reset_index(drop=True)
    selected["source_id"] = selected["clean_read_id"].astype(str)
    return selected


def build_shifted_rows(
    source: pd.DataFrame,
    *,
    lengths: list[int],
    conditions: list[str],
    seed: int,
) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for _, row in source.iterrows():
        for length in lengths:
            clean = row.copy()
            clean["sequence"] = str(row["sequence"])[:length]
            clean["source_length"] = length
            clean["length"] = length
            clean["condition"] = "clean"
            clean["read_id"] = f"{row['source_id']}_L{length}_clean"
            for condition in conditions:
                if condition == "clean":
                    shifted = clean.to_dict()
                else:
                    # Include the length in the deterministic perturbation key.
                    keyed = clean.copy()
                    keyed["clean_read_id"] = f"{row['source_id']}_L{length}"
                    shifted = apply_stage2_condition(keyed, condition, seed)
                    shifted["clean_read_id"] = row["source_id"]
                shifted["source_id"] = row["source_id"]
                shifted["binary_label"] = int(row["binary_label"])
                shifted["source_length"] = length
                shifted["length"] = length
                shifted["condition"] = condition
                rows.append(shifted)
    shifted = pd.DataFrame(rows)
    shifted = shifted.sort_values(["source_id", "source_length", "condition"]).reset_index(drop=True)
    shifted["row_index"] = np.arange(len(shifted), dtype=int)
    return shifted


def build_representation_matrix(
    sequences: list[str],
    representation: str,
) -> tuple[np.ndarray, int]:
    if representation in {"ck4", "ck4_p", "ck4_msp", "ck4p_msp"}:
        features = build_ck4p_msp_features(sequences)
        matrix = build_block_combination(features, representation)
    elif representation == "ck5":
        matrix, _ = build_ck4_block(sequences, config=CK4PMSPConfig(k=5))
    elif representation in {"pseknc_k3_l3", "ncp_anf", "pseeiip"}:
        # A fixed 100-coordinate budget is required for frozen-head transfer.
        # Shorter NCP+ANF reads are deterministically padded by its public method.
        matrix = build_historical_descriptor_matrix(sequences, representation, length=100)
    elif representation == "hash_k15_d222":
        matrix = hashed_kmer_matrix(sequences, k=15, n_features=222, canonical=True, signed=True)
    else:
        raise ValueError(f"Unsupported representation: {representation}")
    matrix = np.nan_to_num(np.asarray(matrix, dtype=np.float64), nan=0.0, posinf=0.0, neginf=0.0)
    return matrix, int(matrix.shape[1])


def metric_values(y_true: np.ndarray, y_pred: np.ndarray, y_score: np.ndarray) -> dict[str, float]:
    return {
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "balanced_accuracy": float(balanced_accuracy_score(y_true, y_pred)),
        "mcc": float(matthews_corrcoef(y_true, y_pred)),
        "macro_f1": float(f1_score(y_true, y_pred, average="macro", zero_division=0)),
        "auroc": float(roc_auc_score(y_true, y_score)),
        "auprc": float(average_precision_score(y_true, y_score)),
    }


def stratified_bootstrap_indices(y: np.ndarray, rng: np.random.Generator) -> np.ndarray:
    parts = []
    for label in np.unique(y):
        indices = np.flatnonzero(y == label)
        parts.append(rng.choice(indices, size=len(indices), replace=True))
    return np.concatenate(parts)


def summarize_predictions(predictions: pd.DataFrame, n_bootstrap: int, seed: int) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    group_cols = [
        "representation",
        "representation_label",
        "probe_scaling",
        "n_features",
        "length",
        "condition",
    ]
    for group_index, (keys, frame) in enumerate(predictions.groupby(group_cols, sort=False)):
        representation, label, probe_scaling, n_features, length, condition = keys
        frame = frame.sort_values("source_id")
        y = frame["y_true"].to_numpy(dtype=int)
        pred = frame["y_pred"].to_numpy(dtype=int)
        score = frame["y_score"].to_numpy(dtype=float)
        metrics = metric_values(y, pred, score)
        rng = np.random.default_rng(seed + group_index)
        bootstrap_f1 = np.empty(n_bootstrap, dtype=float)
        for iteration in range(n_bootstrap):
            sampled = stratified_bootstrap_indices(y, rng)
            bootstrap_f1[iteration] = f1_score(y[sampled], pred[sampled], average="macro", zero_division=0)
        rows.append(
            {
                "representation": representation,
                "representation_label": label,
                "probe_scaling": probe_scaling,
                "n_features": int(n_features),
                "length": int(length),
                "condition": condition,
                "n_test_sources": int(len(frame)),
                **metrics,
                "macro_f1_ci_low": float(np.quantile(bootstrap_f1, 0.025)),
                "macro_f1_ci_high": float(np.quantile(bootstrap_f1, 0.975)),
            }
        )

    summary = pd.DataFrame(rows)
    enriched: list[pd.DataFrame] = []
    for (representation, probe_scaling), frame in summary.groupby(
        ["representation", "probe_scaling"], sort=False
    ):
        frame = frame.copy()
        baseline = frame[(frame["length"].eq(100)) & (frame["condition"].eq("clean"))]
        if len(baseline) != 1:
            raise ValueError(
                f"Expected one 100-bp clean baseline for {representation}/{probe_scaling}"
            )
        baseline_f1 = float(baseline.iloc[0]["macro_f1"])
        frame["baseline_macro_f1"] = baseline_f1
        frame["delta_macro_f1"] = frame["macro_f1"] - baseline_f1
        frame["label_retention_ratio"] = frame["macro_f1"] / baseline_f1 if baseline_f1 > 0 else np.nan
        enriched.append(frame)
    return pd.concat(enriched, ignore_index=True)


def run_transfer_audit(
    shifted: pd.DataFrame,
    *,
    representations: list[str],
    probe_scalings: list[str],
    n_splits: int,
    seed: int,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    source = shifted[["source_id", "binary_label"]].drop_duplicates().sort_values("source_id")
    source_ids = source["source_id"].to_numpy(dtype=str)
    y_source = source["binary_label"].to_numpy(dtype=int)
    folds = StratifiedGroupKFold(n_splits=n_splits, shuffle=True, random_state=seed)
    fold_assignments: dict[str, int] = {}
    for fold, (_, test_idx) in enumerate(folds.split(source_ids, y_source, groups=source_ids), start=1):
        for source_id in source_ids[test_idx]:
            fold_assignments[str(source_id)] = fold
    shifted = shifted.copy()
    shifted["fold"] = shifted["source_id"].map(fold_assignments).astype(int)

    sequences = shifted["sequence"].astype(str).tolist()
    prediction_rows: list[dict[str, object]] = []
    runtime_rows: list[dict[str, object]] = []

    for representation in representations:
        started = time.perf_counter()
        matrix, n_features = build_representation_matrix(sequences, representation)
        feature_seconds = time.perf_counter() - started
        model_started = time.perf_counter()
        for probe_scaling in probe_scalings:
            if probe_scaling not in {"contract", "train_zscore"}:
                raise ValueError(f"Unsupported probe scaling: {probe_scaling}")
            for fold in range(1, n_splits + 1):
                train_sources = set(source_ids[[fold_assignments[str(item)] != fold for item in source_ids]])
                train_mask = (
                    shifted["source_id"].isin(train_sources)
                    & shifted["length"].eq(100)
                    & shifted["condition"].eq("clean")
                ).to_numpy()
                test_source_mask = shifted["fold"].eq(fold).to_numpy()
                y_train = shifted.loc[train_mask, "binary_label"].to_numpy(dtype=int)
                logistic = LogisticRegression(
                    max_iter=3000,
                    class_weight="balanced",
                    random_state=seed + fold,
                )
                model = (
                    logistic
                    if probe_scaling == "contract"
                    else make_pipeline(StandardScaler(), logistic)
                )
                model.fit(matrix[train_mask], y_train)

                for length in sorted(shifted["length"].unique()):
                    for condition in sorted(shifted["condition"].unique()):
                        test_mask = test_source_mask & shifted["length"].eq(length).to_numpy() & shifted["condition"].eq(condition).to_numpy()
                        if not np.any(test_mask):
                            continue
                        y_true = shifted.loc[test_mask, "binary_label"].to_numpy(dtype=int)
                        y_pred = model.predict(matrix[test_mask]).astype(int)
                        y_score = model.predict_proba(matrix[test_mask])[:, 1]
                        for source_id, truth, prediction, score in zip(
                            shifted.loc[test_mask, "source_id"].astype(str), y_true, y_pred, y_score
                        ):
                            prediction_rows.append(
                                {
                                    "representation": representation,
                                    "representation_label": REPRESENTATION_LABELS[representation],
                                    "probe_scaling": probe_scaling,
                                    "n_features": n_features,
                                    "fold": fold,
                                    "source_id": source_id,
                                    "length": int(length),
                                    "condition": condition,
                                    "y_true": int(truth),
                                    "y_pred": int(prediction),
                                    "y_score": float(score),
                                }
                            )
        runtime_rows.append(
            {
                "representation": representation,
                "representation_label": REPRESENTATION_LABELS[representation],
                "n_features": n_features,
                "n_variant_rows": int(len(shifted)),
                "feature_seconds": float(feature_seconds),
                "probe_seconds": float(time.perf_counter() - model_started),
            }
        )
        print(
            f"[cami-fixed-head] {representation}: {n_features} features, "
            f"feature={feature_seconds:.2f}s, predictions={len(prediction_rows)}",
            flush=True,
        )
    return pd.DataFrame(prediction_rows), pd.DataFrame(runtime_rows)


def write_summary(summary: pd.DataFrame, runtime: pd.DataFrame, output_dir: Path) -> None:
    primary = summary[summary["probe_scaling"].eq("contract")].copy()
    shifted = primary[~((primary["length"].eq(100)) & (primary["condition"].eq("clean")))].copy()
    overview = shifted.groupby(["representation_label", "n_features"], as_index=False).agg(
        baseline_macro_f1=("baseline_macro_f1", "first"),
        mean_shifted_macro_f1=("macro_f1", "mean"),
        worst_shifted_macro_f1=("macro_f1", "min"),
        mean_retention=("label_retention_ratio", "mean"),
        worst_retention=("label_retention_ratio", "min"),
    )
    overview = overview.merge(runtime[["representation_label", "feature_seconds"]], on="representation_label", how="left")
    lines = [
        "# CAMI_TOY frozen-head label-retention audit",
        "",
        "A logistic probe was fitted only to 100-bp clean reads. "
        "The primary contract-space probe preserves the declared feature scaling; a scaler fitted only on the clean training fold is retained as a sensitivity analysis. "
        "All target conditions use held-out source groups without refitting.",
        "",
        overview.sort_values("mean_retention", ascending=False).to_markdown(index=False, floatfmt=".4f"),
        "",
        "The retention ratio is a normalized descriptive summary. Absolute macro-F1, MCC, balanced accuracy, "
        "AUROC and AUPRC remain the primary task metrics.",
    ]
    (output_dir / "cami_fixed_head_transfer_summary.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--reads-csv",
        default=str(PROJECT_ROOT / "data" / "stage3" / "cami" / "cami_toy_low_subset_reads_expanded.csv"),
    )
    parser.add_argument(
        "--output-dir",
        default=str(PROJECT_ROOT / "results" / "stage3" / "contract_v2" / "cami_fixed_head_transfer"),
    )
    parser.add_argument("--target-label", default="tax_1122939")
    parser.add_argument("--lengths", default="69,75,100")
    parser.add_argument("--conditions", default="clean,N_3pct,substitution_1pct")
    parser.add_argument("--representations", default=DEFAULT_REPRESENTATIONS)
    parser.add_argument("--probe-scalings", default="contract,train_zscore")
    parser.add_argument("--n-splits", type=int, default=5)
    parser.add_argument("--n-bootstrap", type=int, default=1000)
    parser.add_argument("--max-target-groups", type=int, default=0)
    parser.add_argument("--seed", type=int, default=20260730)
    args = parser.parse_args()

    started = time.time()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    reads = pd.read_csv(args.reads_csv)
    source = select_balanced_source_reads(
        reads,
        target_label=args.target_label,
        seed=args.seed,
        max_target_groups=args.max_target_groups,
    )
    lengths = parse_int_list(args.lengths)
    conditions = parse_csv_list(args.conditions)
    representations = parse_csv_list(args.representations)
    probe_scalings = parse_csv_list(args.probe_scalings)
    shifted = build_shifted_rows(source, lengths=lengths, conditions=conditions, seed=args.seed)
    source.to_csv(output_dir / "cami_fixed_head_source_reads.csv", index=False, encoding="utf-8-sig")
    shifted.to_csv(output_dir / "cami_fixed_head_shifted_rows.csv", index=False, encoding="utf-8-sig")

    predictions, runtime = run_transfer_audit(
        shifted,
        representations=representations,
        probe_scalings=probe_scalings,
        n_splits=args.n_splits,
        seed=args.seed,
    )
    summary = summarize_predictions(predictions, n_bootstrap=args.n_bootstrap, seed=args.seed)
    predictions.to_csv(output_dir / "cami_fixed_head_predictions.csv", index=False, encoding="utf-8-sig")
    runtime.to_csv(output_dir / "cami_fixed_head_runtime.csv", index=False, encoding="utf-8-sig")
    summary.to_csv(output_dir / "cami_fixed_head_metrics.csv", index=False, encoding="utf-8-sig")
    write_summary(summary, runtime, output_dir)

    metadata = {
        "elapsed_seconds": time.time() - started,
        "reads_csv": str(args.reads_csv),
        "target_label": args.target_label,
        "lengths": lengths,
        "conditions": conditions,
        "representations": representations,
        "probe_scalings": probe_scalings,
        "n_splits": args.n_splits,
        "n_bootstrap": args.n_bootstrap,
        "seed": args.seed,
        "n_input_rows": int(len(reads)),
        "n_source_groups": int(len(source)),
        "n_target_groups": int(source["binary_label"].sum()),
        "n_background_groups": int((1 - source["binary_label"]).sum()),
        "n_shifted_rows": int(len(shifted)),
    }
    (output_dir / "cami_fixed_head_transfer_run.json").write_text(
        json.dumps(metadata, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(f"Wrote CAMI fixed-head audit to {output_dir}")


if __name__ == "__main__":
    main()
