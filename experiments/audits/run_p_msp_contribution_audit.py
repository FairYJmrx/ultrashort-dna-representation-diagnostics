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
from sklearn.preprocessing import StandardScaler, normalize

def _find_project_root(start: Path) -> Path:
    for candidate in [start.parent, *start.parents]:
        if (candidate / "methods").is_dir() and (candidate / "configs").is_dir():
            return candidate
    raise RuntimeError("Could not locate the release repository root.")


PROJECT_ROOT = _find_project_root(Path(__file__).resolve())
sys.path.insert(0, str(PROJECT_ROOT))

from experiments.main.run_stage2_representation_grid import paired_subsets, parse_csv_list, parse_int_list, set_global_seed  # noqa: E402
from methods.ck4p_msp import build_ck4p_msp_features  # noqa: E402
from src.stage2_features import paired_retrieval_metrics  # noqa: E402


REP_BLOCKS = {
    "ck4": ("K",),
    "p": ("P",),
    "msp": ("M",),
    "ck4_p": ("K", "P"),
    "ck4_msp": ("K", "M"),
    "p_msp": ("P", "M"),
    "ck4p_msp": ("K", "P", "M"),
}

REP_LABELS = {
    "ck4": "CK4",
    "p": "P",
    "msp": "MSP",
    "ck4_p": "CK4+P",
    "ck4_msp": "CK4+MSP",
    "p_msp": "P+MSP",
    "ck4p_msp": "CK4P-MSP",
}


CONDITIONAL_CONTRASTS = {
    "K | P+MSP": "p_msp",
    "P | CK4+MSP": "ck4_msp",
    "MSP | CK4+P": "ck4_p",
}

RATIO_DENOMINATOR_TOLERANCE = 1e-8


def safe_norm(x: np.ndarray) -> np.ndarray:
    arr = np.nan_to_num(np.asarray(x, dtype=np.float64), nan=0.0, posinf=0.0, neginf=0.0)
    return normalize(arr, norm="l2", axis=1)


def build_blocks(sequences: list[str], length: int, train_indices: list[int]) -> dict[str, np.ndarray]:
    features = build_ck4p_msp_features(sequences, train_indices=train_indices)
    return {"K": features.ck4, "P": features.p, "M": features.msp}


def assemble(blocks: dict[str, np.ndarray], parts: tuple[str, ...]) -> np.ndarray:
    x = np.hstack([blocks[part] for part in parts])
    # Each block is internally L2-normalized before concatenation. The final
    # normalization is therefore equivalent to a fixed sqrt(n_blocks) scaling
    # for nonzero rows, not a data-dependent cross-block reweighting.
    return safe_norm(x)


def benjamini_hochberg(p_values: list[float]) -> list[float]:
    values = np.asarray(p_values, dtype=float)
    adjusted = np.full(values.shape, np.nan, dtype=float)
    valid = np.where(np.isfinite(values))[0]
    if valid.size == 0:
        return adjusted.tolist()
    ordered = valid[np.argsort(values[valid])]
    running = 1.0
    m = float(valid.size)
    for reverse_rank, idx in enumerate(ordered[::-1], start=1):
        rank = valid.size - reverse_rank + 1
        running = min(running, float(values[idx]) * m / float(rank))
        adjusted[idx] = min(running, 1.0)
    return adjusted.tolist()


def bootstrap_mean_ci(values: np.ndarray, seed: int, n_bootstrap: int = 10000) -> tuple[float, float]:
    values = np.asarray(values, dtype=float)
    if values.size == 0:
        return np.nan, np.nan
    rng = np.random.default_rng(seed)
    indices = rng.integers(0, values.size, size=(n_bootstrap, values.size))
    means = values[indices].mean(axis=1)
    low, high = np.quantile(means, [0.025, 0.975])
    return float(low), float(high)


def conditional_contrast_row(
    df: pd.DataFrame,
    *,
    contrast: str,
    comparator: str,
    metric: str,
    keys: list[str],
    higher_is_better: bool,
    evidence_layer: str,
    seed: int,
) -> dict[str, object]:
    full = "ck4p_msp"
    subset = df[df["representation"].isin([full, comparator])].copy()
    pivot = subset.pivot_table(index=keys, columns="representation", values=metric, aggfunc="mean")
    if full not in pivot.columns or comparator not in pivot.columns:
        return {
            "contrast": contrast,
            "evidence_layer": evidence_layer,
            "metric": metric,
            "paired_unit": "+".join(keys),
            "n_pairs": 0,
        }
    paired = pivot[[full, comparator]].dropna()
    raw_difference = paired[full].to_numpy(dtype=float) - paired[comparator].to_numpy(dtype=float)
    improvement = raw_difference if higher_is_better else -raw_difference
    ci_low, ci_high = bootstrap_mean_ci(improvement, seed=seed)
    if improvement.size == 0 or np.allclose(improvement, 0.0):
        p_value = 1.0
    else:
        p_value = float(wilcoxon(improvement, alternative="two-sided", zero_method="wilcox").pvalue)
    return {
        "contrast": contrast,
        "full_representation": full,
        "comparator": comparator,
        "evidence_layer": evidence_layer,
        "metric": metric,
        "metric_direction": "higher" if higher_is_better else "lower",
        "paired_unit": "+".join(keys),
        "n_pairs": int(len(paired)),
        "full_mean": float(paired[full].mean()),
        "comparator_mean": float(paired[comparator].mean()),
        "mean_improvement_positive_is_better": float(improvement.mean()),
        "bootstrap_95_ci_low": ci_low,
        "bootstrap_95_ci_high": ci_high,
        "wilcoxon_two_sided_p": p_value,
        "full_better_fraction": float(np.mean(improvement > 0)),
    }


def conditional_contribution_tests(
    stability: pd.DataFrame,
    readout: pd.DataFrame,
    seed: int,
) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    stability_metrics = {
        "paired_cosine_mean": True,
        "l2_delta_mean": False,
        "retrieval_top1": True,
    }
    grouped_readout = readout[readout["split"].astype(str).str.contains("grouped_cv")].copy()
    for contrast_index, (contrast, comparator) in enumerate(CONDITIONAL_CONTRASTS.items()):
        for metric_index, (metric, higher_is_better) in enumerate(stability_metrics.items()):
            rows.append(
                conditional_contrast_row(
                    stability,
                    contrast=contrast,
                    comparator=comparator,
                    metric=metric,
                    keys=["length", "condition"],
                    higher_is_better=higher_is_better,
                    evidence_layer="global_perturbation_stability",
                    seed=seed + 100 * contrast_index + metric_index,
                )
            )
        rows.append(
            conditional_contrast_row(
                grouped_readout,
                contrast=contrast,
                comparator=comparator,
                metric="macro_f1",
                keys=["length", "local_mode", "split"],
                higher_is_better=True,
                evidence_layer="grouped_local_delta_readout",
                seed=seed + 100 * contrast_index + 50,
            )
        )
    out = pd.DataFrame(rows)
    out["bh_q"] = benjamini_hochberg(out["wilcoxon_two_sided_p"].astype(float).tolist())
    return out


def assemble_all(blocks: dict[str, np.ndarray]) -> dict[str, np.ndarray]:
    return {rep: assemble(blocks, parts) for rep, parts in REP_BLOCKS.items()}


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
            clean, pert = paired_subsets(reads, int(length), condition)
            if clean.empty:
                continue
            if max_pairs > 0 and len(clean) > max_pairs:
                keep = clean["clean_read_id"].drop_duplicates().sample(n=max_pairs, random_state=seed + int(length)).tolist()
                clean = clean[clean["clean_read_id"].isin(keep)].sort_values("clean_read_id").reset_index(drop=True)
                pert = pert[pert["clean_read_id"].isin(keep)].sort_values("clean_read_id").reset_index(drop=True)
            sequences = clean["sequence"].astype(str).tolist() + pert["sequence"].astype(str).tolist()
            train = list(range(len(clean)))
            reps = assemble_all(build_blocks(sequences, int(length), train))
            for rep, x in reps.items():
                metrics = paired_retrieval_metrics(x[: len(clean)], x[len(clean) :])
                metrics.update(
                    {
                        "length": int(length),
                        "condition": condition,
                        "representation": rep,
                        "representation_label": REP_LABELS[rep],
                        "n_pairs": int(len(clean)),
                        "n_features": int(x.shape[1]),
                    }
                )
                rows.append(metrics)
    return pd.DataFrame(rows)


def classifier_registry(seed: int) -> dict[str, object]:
    return {"logistic": make_pipeline(StandardScaler(), LogisticRegression(max_iter=5000, random_state=seed))}


def evaluate_delta_readout(
    clean: np.ndarray,
    noise: np.ndarray,
    local: np.ndarray,
    sample_ids: list[str],
    seed: int,
    cv_folds: int,
) -> list[dict[str, object]]:
    x_delta = np.vstack([np.abs(noise - clean), np.abs(local - clean)])
    y = np.asarray([0] * clean.shape[0] + [1] * clean.shape[0])
    groups = np.asarray(sample_ids + sample_ids)
    if len(groups) != len(y):
        raise ValueError("sample_ids must contain one entry per clean/read perturbation triplet.")
    rows: list[dict[str, object]] = []
    holdout_splitter = StratifiedGroupKFold(n_splits=3, shuffle=True, random_state=seed)
    train_idx, test_idx = next(holdout_splitter.split(x_delta, y, groups))
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
    n_groups = len(np.unique(groups))
    if cv_folds > 1 and n_groups >= 2:
        n_splits = min(cv_folds, n_groups)
        skf = StratifiedGroupKFold(n_splits=n_splits, shuffle=True, random_state=seed)
        for clf_name in classifier_registry(seed):
            acc, f1 = [], []
            for train_cv, test_cv in skf.split(x_delta, y, groups):
                clf = classifier_registry(seed)[clf_name]
                clf.fit(x_delta[train_cv], y[train_cv])
                pred = clf.predict(x_delta[test_cv])
                acc.append(float(accuracy_score(y[test_cv], pred)))
                f1.append(float(f1_score(y[test_cv], pred, average="macro", zero_division=0)))
            rows.append(
                {
                    "split": f"{n_splits}fold_grouped_cv",
                    "classifier": clf_name,
                    "accuracy": float(np.mean(acc)),
                    "accuracy_std": float(np.std(acc)),
                    "macro_f1": float(np.mean(f1)),
                    "macro_f1_std": float(np.std(f1)),
                }
            )
    return rows


def local_delta_audit(
    triplets: pd.DataFrame,
    lengths: list[int],
    max_triplets: int,
    seed: int,
    cv_folds: int,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    pair_rows: list[dict[str, object]] = []
    readout_rows: list[dict[str, object]] = []
    triplets = triplets[triplets["source_length"].astype(int).isin(lengths)].copy()
    for (length, mode), subset in triplets.groupby(["source_length", "local_mode"], sort=True):
        sample_ids = sorted(subset["sample_id"].unique().tolist())
        if max_triplets > 0 and len(sample_ids) > max_triplets:
            rng = np.random.default_rng(seed + int(length) + len(str(mode)))
            sample_ids = sorted(rng.choice(sample_ids, size=max_triplets, replace=False).tolist())
        ordered: list[str] = []
        for variant in ["clean", "random_noise", "local_property_shift"]:
            variant_df = subset[subset["variant"].eq(variant)].set_index("sample_id").loc[sample_ids]
            ordered.extend(variant_df["sequence"].astype(str).tolist())
        n = len(sample_ids)
        reps = assemble_all(build_blocks(ordered, int(length), list(range(n))))
        for rep, x in reps.items():
            clean_x = x[:n]
            noise_x = x[n : 2 * n]
            local_x = x[2 * n : 3 * n]
            noise_l2 = np.linalg.norm(clean_x - noise_x, axis=1)
            local_l2 = np.linalg.norm(clean_x - local_x, axis=1)
            ratio_valid = noise_l2 > RATIO_DENOMINATOR_TOLERANCE
            ratio = np.full_like(local_l2, np.nan, dtype=np.float64)
            ratio[ratio_valid] = local_l2[ratio_valid] / noise_l2[ratio_valid]
            for idx, sample_id in enumerate(sample_ids):
                pair_rows.append(
                    {
                        "sample_id": sample_id,
                        "length": int(length),
                        "local_mode": str(mode),
                        "representation": rep,
                        "representation_label": REP_LABELS[rep],
                        "noise_l2": float(noise_l2[idx]),
                        "local_l2": float(local_l2[idx]),
                        "local_minus_noise_l2": float(local_l2[idx] - noise_l2[idx]),
                        "selective_sensitivity_ratio": float(ratio[idx]),
                        "selective_sensitivity_ratio_valid": bool(ratio_valid[idx]),
                        "n_features": int(x.shape[1]),
                    }
                )
            for row in evaluate_delta_readout(
                clean_x,
                noise_x,
                local_x,
                sample_ids=sample_ids,
                seed=seed + int(length),
                cv_folds=cv_folds,
            ):
                row.update(
                    {
                        "length": int(length),
                        "local_mode": str(mode),
                        "representation": rep,
                        "representation_label": REP_LABELS[rep],
                        "n_triplets": int(n),
                        "n_features": int(x.shape[1]),
                    }
                )
                readout_rows.append(row)
    return pd.DataFrame(pair_rows), pd.DataFrame(readout_rows)


def summarize(
    stability: pd.DataFrame,
    local_pairs: pd.DataFrame,
    readout: pd.DataFrame,
    out_dir: Path,
    meta: dict[str, object],
) -> None:
    stability.to_csv(out_dir / "p_msp_contribution_stability.csv", index=False, encoding="utf-8-sig")
    local_pairs.to_csv(out_dir / "p_msp_contribution_local_pairs.csv", index=False, encoding="utf-8-sig")
    readout.to_csv(out_dir / "p_msp_contribution_delta_readout.csv", index=False, encoding="utf-8-sig")
    contrasts = conditional_contribution_tests(stability, readout, seed=int(meta["seed"]))
    contrasts.to_csv(out_dir / "p_msp_contribution_conditional_contrasts.csv", index=False, encoding="utf-8-sig")

    stability_summary = (
        stability.groupby(["representation", "representation_label"], as_index=False)
        .agg(
            n_cells=("paired_cosine_mean", "count"),
            n_features=("n_features", "median"),
            paired_cosine_mean=("paired_cosine_mean", "mean"),
            l2_delta_mean=("l2_delta_mean", "mean"),
            retrieval_top1_mean=("retrieval_top1", "mean"),
        )
        .sort_values("l2_delta_mean")
    )
    stability_by_length = (
        stability.groupby(["length", "representation", "representation_label"], as_index=False)
        .agg(
            n_cells=("paired_cosine_mean", "count"),
            paired_cosine_mean=("paired_cosine_mean", "mean"),
            l2_delta_mean=("l2_delta_mean", "mean"),
            retrieval_top1_mean=("retrieval_top1", "mean"),
        )
        .sort_values(["length", "l2_delta_mean"])
    )
    pair_summary = (
        local_pairs.groupby(["representation", "representation_label"], as_index=False)
        .agg(
            n_cells=("local_minus_noise_l2", "count"),
            n_features=("n_features", "median"),
            noise_l2_mean=("noise_l2", "mean"),
            local_l2_mean=("local_l2", "mean"),
            local_minus_noise_l2_mean=("local_minus_noise_l2", "mean"),
            selective_sensitivity_ratio_mean=("selective_sensitivity_ratio", "mean"),
            selective_sensitivity_ratio_n_valid=("selective_sensitivity_ratio", "count"),
            selective_sensitivity_ratio_valid_fraction=("selective_sensitivity_ratio_valid", "mean"),
        )
        .sort_values("local_minus_noise_l2_mean", ascending=False)
    )
    cv = readout[readout["split"].astype(str).str.contains("grouped_cv")].copy()
    readout_summary = (
        cv.groupby(["representation", "representation_label", "classifier"], as_index=False)
        .agg(
            n_cells=("macro_f1", "count"),
            n_features=("n_features", "median"),
            macro_f1_mean=("macro_f1", "mean"),
            macro_f1_std_mean=("macro_f1_std", "mean"),
            accuracy_mean=("accuracy", "mean"),
        )
        .sort_values("macro_f1_mean", ascending=False)
    )
    readout_by_length = (
        cv.groupby(["length", "representation", "representation_label"], as_index=False)
        .agg(
            n_cells=("macro_f1", "count"),
            macro_f1_mean=("macro_f1", "mean"),
            macro_f1_std_mean=("macro_f1_std", "mean"),
            accuracy_mean=("accuracy", "mean"),
        )
        .sort_values(["length", "macro_f1_mean"], ascending=[True, False])
    )

    outputs = {
        "p_msp_contribution_stability_summary": stability_summary,
        "p_msp_contribution_stability_by_length": stability_by_length,
        "p_msp_contribution_local_pair_summary": pair_summary,
        "p_msp_contribution_delta_readout_summary": readout_summary,
        "p_msp_contribution_delta_readout_by_length": readout_by_length,
    }
    for name, df in outputs.items():
        df.to_csv(out_dir / f"{name}.csv", index=False, encoding="utf-8-sig")

    lines = [
        "# Seven-group K/P/MSP contribution audit",
        "",
        "Purpose: evaluate all seven non-empty combinations of the canonical local k-mer composition block (K), global biochemical property block (P), and multi-scale positional property block (MSP) under the same internally normalized block-concatenation rule used in the manuscript.",
        "",
        "Interpretation boundary: this audit does not assume that K, P and MSP are orthogonal or statistically independent. It tests metric-specific conditional contributions under the controlled perturbation grid.",
        "",
        "## Run metadata",
        "",
        pd.DataFrame([meta]).to_markdown(index=False),
        "",
        "## Stability summary",
        "",
        stability_summary.to_markdown(index=False, floatfmt=".4f"),
        "",
        "## Stability by length",
        "",
        stability_by_length.to_markdown(index=False, floatfmt=".4f"),
        "",
        "## Local mutation distance summary",
        "",
        pair_summary.to_markdown(index=False, floatfmt=".4f"),
        "",
        "## Delta-readout summary",
        "",
        readout_summary.to_markdown(index=False, floatfmt=".4f"),
        "",
        "## Delta-readout by length",
        "",
        readout_by_length.to_markdown(index=False, floatfmt=".4f"),
        "",
        "## Prespecified conditional-contribution contrasts",
        "",
        "Positive improvement values favour the complete CK4P-MSP representation. Confidence intervals are paired-cell bootstrap intervals; Wilcoxon tests are two-sided and q values use Benjamini-Hochberg correction across the 12 prespecified rows.",
        "",
        contrasts.to_markdown(index=False, floatfmt=".4f"),
        "",
    ]
    (out_dir / "p_msp_contribution_summary.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the seven-group K/P/MSP contribution audit.")
    parser.add_argument("--reads", default=str(PROJECT_ROOT / "results" / "stage3" / "contract_v2" / "compact_baselines" / "stage3_compact_baseline_reads.csv"))
    parser.add_argument("--triplets", default=str(PROJECT_ROOT / "results" / "stage3" / "contract_v2" / "local_mutation_sensitivity" / "local_mutation_triplets.csv"))
    parser.add_argument("--output-dir", default=str(PROJECT_ROOT / "results" / "stage3" / "contract_v2" / "p_msp_contribution"))
    parser.add_argument("--lengths", default="69,75,100,150")
    parser.add_argument("--conditions", default="substitution_1pct,N_3pct,trim_5bp,substitution_1pct_N_3pct,local_mismatch_6bp,short_indel")
    parser.add_argument("--max-pairs", type=int, default=500)
    parser.add_argument("--max-triplets", type=int, default=400)
    parser.add_argument("--cv-folds", type=int, default=5)
    parser.add_argument("--seed", type=int, default=20260625)
    args = parser.parse_args()

    started = time.time()
    set_global_seed(args.seed)
    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    reads = pd.read_csv(args.reads)
    triplets = pd.read_csv(args.triplets)
    lengths = parse_int_list(args.lengths)
    conditions = parse_csv_list(args.conditions)
    stability = stability_audit(reads, lengths=lengths, conditions=conditions, max_pairs=args.max_pairs, seed=args.seed)
    local_pairs, readout = local_delta_audit(triplets, lengths=lengths, max_triplets=args.max_triplets, seed=args.seed, cv_folds=args.cv_folds)
    meta = {
        "elapsed_seconds": round(time.time() - started, 3),
        "reads": args.reads,
        "triplets": args.triplets,
        "lengths": lengths,
        "conditions": conditions,
        "max_pairs": int(args.max_pairs),
        "max_triplets": int(args.max_triplets),
        "cv_folds": int(args.cv_folds),
        "seed": int(args.seed),
    }
    (out_dir / "p_msp_contribution_run.json").write_text(json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8")
    summarize(stability, local_pairs, readout, out_dir, meta)
    print(f"Wrote seven-group K/P/MSP contribution audit to {out_dir}")


if __name__ == "__main__":
    main()

