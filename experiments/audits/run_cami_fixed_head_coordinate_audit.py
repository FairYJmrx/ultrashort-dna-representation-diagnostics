"""Coordinate and paired-contrast audit for CAMI frozen-head transfer."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import f1_score
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


P_NAMES = [
    "hydrogen_mean",
    "hydrogen_sd",
    "gc_mean",
    "gc_sd",
    "purine_mean",
    "purine_sd",
    "eiip_mean",
    "eiip_sd",
    "n_fraction",
    "length_scaled",
    "base_entropy",
]


def fit_model(x: np.ndarray, y: np.ndarray, scaling: str, seed: int):
    logistic = LogisticRegression(max_iter=3000, class_weight="balanced", random_state=seed)
    if scaling == "contract":
        return logistic.fit(x, y)
    if scaling == "train_zscore":
        return make_pipeline(StandardScaler(), logistic).fit(x, y)
    raise ValueError(f"Unsupported scaling: {scaling}")


def coordinate_audit(
    shifted: pd.DataFrame,
    predictions: pd.DataFrame,
    *,
    seed: int,
) -> pd.DataFrame:
    fold_map = (
        predictions[["source_id", "fold"]]
        .drop_duplicates()
        .set_index("source_id")["fold"]
        .astype(int)
        .to_dict()
    )
    shifted = shifted.copy()
    shifted["fold"] = shifted["source_id"].map(fold_map).astype(int)
    features = build_ck4p_msp_features(shifted["sequence"].astype(str).tolist())
    matrices = {
        "ck4_p": build_block_combination(features, "ck4_p"),
        "ck4p_msp": build_block_combination(features, "ck4p_msp"),
    }
    p_start = features.ck4.shape[1]
    rows: list[dict[str, object]] = []

    for representation, matrix in matrices.items():
        p_slice = slice(p_start, p_start + len(P_NAMES))
        for scaling in ("contract", "train_zscore"):
            for fold in sorted(shifted["fold"].unique()):
                train_mask = (
                    shifted["fold"].ne(fold)
                    & shifted["length"].eq(100)
                    & shifted["condition"].eq("clean")
                ).to_numpy()
                y_train = shifted.loc[train_mask, "binary_label"].to_numpy(dtype=int)
                model = fit_model(matrix[train_mask], y_train, scaling, seed + int(fold))
                if scaling == "contract":
                    coefficient = model.coef_[0]
                    scale = np.ones(matrix.shape[1], dtype=float)
                else:
                    scaler = model.named_steps["standardscaler"]
                    logistic = model.named_steps["logisticregression"]
                    coefficient = logistic.coef_[0]
                    scale = scaler.scale_

                train_p = matrix[train_mask, p_slice]
                train_mean = train_p.mean(axis=0)
                train_sd = train_p.std(axis=0)
                baseline = shifted[
                    shifted["fold"].eq(fold)
                    & shifted["length"].eq(100)
                    & shifted["condition"].eq("clean")
                ].sort_values("source_id")
                baseline_p = matrix[baseline.index.to_numpy(), p_slice]

                for length in sorted(shifted["length"].unique()):
                    for condition in sorted(shifted["condition"].unique()):
                        if length == 100 and condition == "clean":
                            continue
                        target = shifted[
                            shifted["fold"].eq(fold)
                            & shifted["length"].eq(length)
                            & shifted["condition"].eq(condition)
                        ].sort_values("source_id")
                        if not np.array_equal(
                            baseline["source_id"].to_numpy(), target["source_id"].to_numpy()
                        ):
                            raise ValueError("Baseline and target source ordering differ.")
                        target_p = matrix[target.index.to_numpy(), p_slice]
                        raw_delta = target_p - baseline_p
                        scaled_delta = raw_delta / scale[p_slice]
                        contribution = scaled_delta * coefficient[p_slice]
                        for coordinate, name in enumerate(P_NAMES):
                            rows.append(
                                {
                                    "representation": representation,
                                    "probe_scaling": scaling,
                                    "fold": int(fold),
                                    "length": int(length),
                                    "condition": condition,
                                    "coordinate": name,
                                    "train_mean": float(train_mean[coordinate]),
                                    "train_sd": float(train_sd[coordinate]),
                                    "scaler_scale": float(scale[p_slice][coordinate]),
                                    "target_mean": float(target_p[:, coordinate].mean()),
                                    "mean_raw_delta": float(raw_delta[:, coordinate].mean()),
                                    "mean_abs_raw_delta": float(np.abs(raw_delta[:, coordinate]).mean()),
                                    "mean_scaled_delta": float(scaled_delta[:, coordinate].mean()),
                                    "mean_abs_scaled_delta": float(np.abs(scaled_delta[:, coordinate]).mean()),
                                    "logistic_coefficient": float(coefficient[p_slice][coordinate]),
                                    "mean_logit_shift": float(contribution[:, coordinate].mean()),
                                    "mean_abs_logit_shift": float(np.abs(contribution[:, coordinate]).mean()),
                                }
                            )
    return pd.DataFrame(rows)


def stratified_bootstrap_indices(y: np.ndarray, rng: np.random.Generator) -> np.ndarray:
    return np.concatenate(
        [
            rng.choice(indices, size=len(indices), replace=True)
            for label in np.unique(y)
            for indices in [np.flatnonzero(y == label)]
        ]
    )


def stratified_bootstrap_matrix(
    y: np.ndarray,
    rng: np.random.Generator,
    n_bootstrap: int,
) -> np.ndarray:
    parts = []
    for label in np.unique(y):
        indices = np.flatnonzero(y == label)
        parts.append(rng.choice(indices, size=(n_bootstrap, len(indices)), replace=True))
    return np.concatenate(parts, axis=1)


def binary_macro_f1(y_true: np.ndarray, y_pred: np.ndarray) -> np.ndarray:
    """Vectorized binary macro-F1 over the final array axis."""
    y_true = np.asarray(y_true, dtype=int)
    y_pred = np.asarray(y_pred, dtype=int)
    tp = np.sum((y_true == 1) & (y_pred == 1), axis=-1)
    fn = np.sum((y_true == 1) & (y_pred == 0), axis=-1)
    fp = np.sum((y_true == 0) & (y_pred == 1), axis=-1)
    tn = np.sum((y_true == 0) & (y_pred == 0), axis=-1)
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


def _prediction_vectors(
    predictions: pd.DataFrame,
    representation: str,
    scaling: str,
    length: int,
    condition: str,
) -> pd.DataFrame:
    return predictions[
        predictions["representation"].eq(representation)
        & predictions["probe_scaling"].eq(scaling)
        & predictions["length"].eq(length)
        & predictions["condition"].eq(condition)
    ][["source_id", "y_true", "y_pred"]].sort_values("source_id")


def paired_contrasts(
    predictions: pd.DataFrame,
    *,
    n_bootstrap: int,
    seed: int,
) -> pd.DataFrame:
    comparisons = ["ck4", "ck4_p", "ck4_msp", "pseknc_k3_l3", "pseeiip", "ck5"]
    cells = predictions[["probe_scaling", "length", "condition"]].drop_duplicates()
    rows: list[dict[str, object]] = []
    for cell_index, cell in cells.reset_index(drop=True).iterrows():
        scaling = str(cell["probe_scaling"])
        length = int(cell["length"])
        condition = str(cell["condition"])
        primary = _prediction_vectors(predictions, "ck4p_msp", scaling, length, condition)
        primary_base = _prediction_vectors(predictions, "ck4p_msp", scaling, 100, "clean")
        y = primary["y_true"].to_numpy(dtype=int)
        f1_primary = f1_score(y, primary["y_pred"], average="macro", zero_division=0)
        f1_primary_base = f1_score(
            y, primary_base["y_pred"], average="macro", zero_division=0
        )
        for comparison_index, comparator in enumerate(comparisons):
            other = _prediction_vectors(predictions, comparator, scaling, length, condition)
            other_base = _prediction_vectors(predictions, comparator, scaling, 100, "clean")
            if not (
                np.array_equal(primary["source_id"].to_numpy(), other["source_id"].to_numpy())
                and np.array_equal(primary["source_id"].to_numpy(), primary_base["source_id"].to_numpy())
                and np.array_equal(primary["source_id"].to_numpy(), other_base["source_id"].to_numpy())
            ):
                raise ValueError("Prediction sources are not paired.")
            f1_other = f1_score(y, other["y_pred"], average="macro", zero_division=0)
            f1_other_base = f1_score(y, other_base["y_pred"], average="macro", zero_division=0)
            absolute_difference = f1_primary - f1_other
            drop_difference = (f1_primary - f1_primary_base) - (f1_other - f1_other_base)

            rng = np.random.default_rng(seed + 100 * cell_index + comparison_index)
            primary_pred = primary["y_pred"].to_numpy(dtype=int)
            primary_base_pred = primary_base["y_pred"].to_numpy(dtype=int)
            other_pred = other["y_pred"].to_numpy(dtype=int)
            other_base_pred = other_base["y_pred"].to_numpy(dtype=int)
            sampled = stratified_bootstrap_matrix(y, rng, n_bootstrap)
            sampled_y = y[sampled]
            p = binary_macro_f1(sampled_y, primary_pred[sampled])
            pb = binary_macro_f1(sampled_y, primary_base_pred[sampled])
            o = binary_macro_f1(sampled_y, other_pred[sampled])
            ob = binary_macro_f1(sampled_y, other_base_pred[sampled])
            absolute_samples = p - o
            drop_samples = (p - pb) - (o - ob)
            rows.append(
                {
                    "probe_scaling": scaling,
                    "length": length,
                    "condition": condition,
                    "comparator": comparator,
                    "ck4p_msp_macro_f1": float(f1_primary),
                    "comparator_macro_f1": float(f1_other),
                    "absolute_f1_difference": float(absolute_difference),
                    "absolute_difference_ci_low": float(np.quantile(absolute_samples, 0.025)),
                    "absolute_difference_ci_high": float(np.quantile(absolute_samples, 0.975)),
                    "relative_drop_difference": float(drop_difference),
                    "relative_drop_ci_low": float(np.quantile(drop_samples, 0.025)),
                    "relative_drop_ci_high": float(np.quantile(drop_samples, 0.975)),
                }
            )
    return pd.DataFrame(rows)


def write_summary(coordinates: pd.DataFrame, contrasts: pd.DataFrame, output_dir: Path) -> None:
    focus = coordinates[
        coordinates["representation"].eq("ck4p_msp")
        & coordinates["probe_scaling"].eq("train_zscore")
        & coordinates["condition"].eq("N_3pct")
    ]
    ranked = (
        focus.groupby(["length", "coordinate"], as_index=False)
        .agg(
            train_sd=("train_sd", "mean"),
            mean_abs_scaled_delta=("mean_abs_scaled_delta", "mean"),
            mean_abs_logit_shift=("mean_abs_logit_shift", "mean"),
        )
        .sort_values(["length", "mean_abs_logit_shift"], ascending=[False, False])
    )
    contract = contrasts[contrasts["probe_scaling"].eq("contract")].copy()
    lines = [
        "# CAMI frozen-head coordinate audit",
        "",
        "## P-coordinate sensitivity under train-fitted z-scoring and N masking",
        "",
        ranked.to_markdown(index=False, floatfmt=".6f"),
        "",
        "## Contract-space paired contrasts",
        "",
        contract.to_markdown(index=False, floatfmt=".4f"),
        "",
        "Positive absolute differences favour CK4P-MSP at the target condition. Positive relative-drop "
        "differences indicate that CK4P-MSP lost less macro-F1 from its own 100-bp clean baseline.",
    ]
    (output_dir / "cami_fixed_head_coordinate_audit_summary.md").write_text(
        "\n".join(lines), encoding="utf-8"
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--result-dir",
        type=Path,
        default=PROJECT_ROOT / "results" / "stage3" / "contract_v2" / "cami_fixed_head_transfer",
    )
    parser.add_argument("--n-bootstrap", type=int, default=1000)
    parser.add_argument("--seed", type=int, default=20260731)
    args = parser.parse_args()

    shifted = pd.read_csv(args.result_dir / "cami_fixed_head_shifted_rows.csv")
    predictions = pd.read_csv(args.result_dir / "cami_fixed_head_predictions.csv")
    coordinates = coordinate_audit(shifted, predictions, seed=args.seed)
    contrasts = paired_contrasts(predictions, n_bootstrap=args.n_bootstrap, seed=args.seed)
    coordinates.to_csv(args.result_dir / "cami_fixed_head_p_coordinate_audit.csv", index=False)
    contrasts.to_csv(args.result_dir / "cami_fixed_head_paired_contrasts.csv", index=False)
    write_summary(coordinates, contrasts, args.result_dir)
    print(f"Wrote coordinate audit to {args.result_dir}")


if __name__ == "__main__":
    main()
