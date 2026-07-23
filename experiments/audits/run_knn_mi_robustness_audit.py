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

from experiments.main.run_stage2_representation_grid import parse_int_list, set_global_seed  # noqa: E402
from src.stage2_features import build_feature_matrix  # noqa: E402


def digamma_approx(x: np.ndarray | float) -> np.ndarray | float:
    """Small dependency-free digamma approximation for positive arguments."""
    arr = np.asarray(x, dtype=np.float64)
    out = np.zeros_like(arr, dtype=np.float64)
    y = arr.copy()
    mask = y < 6.0
    while np.any(mask):
        out[mask] -= 1.0 / y[mask]
        y[mask] += 1.0
        mask = y < 6.0
    inv = 1.0 / y
    inv2 = inv * inv
    out += np.log(y) - 0.5 * inv - inv2 * (1.0 / 12.0 - inv2 * (1.0 / 120.0 - inv2 / 252.0))
    if np.isscalar(x):
        return float(out)
    return out


def _safe_norm(x: np.ndarray) -> np.ndarray:
    return normalize(np.nan_to_num(np.asarray(x, dtype=np.float64), nan=0.0, posinf=0.0, neginf=0.0), norm="l2", axis=1)


def _standardize(x: np.ndarray, seed: int) -> np.ndarray:
    x = np.asarray(x, dtype=np.float64)
    if x.ndim == 1:
        x = x.reshape(-1, 1)
    x = np.nan_to_num(x, nan=0.0, posinf=0.0, neginf=0.0)
    x = StandardScaler().fit_transform(x)
    # Deterministic tiny jitter avoids zero-radius ties in repeated distances.
    rng = np.random.default_rng(seed)
    return x + rng.normal(0.0, 1e-10, size=x.shape)


def mixed_knn_mi_bits(x: np.ndarray, y: np.ndarray, k: int = 5, seed: int = 0) -> float:
    """Estimate I(X;Y) for continuous X and discrete Y using a Ross/KSG-style kNN estimator.

    This estimator is used as a robustness audit rather than as an absolute
    information-theoretic claim. It operates on low-dimensional distance
    summaries, not on the full mixed representation vectors.
    """
    x = _standardize(x, seed=seed)
    y = np.asarray(y)
    n = len(y)
    if n < 8 or len(np.unique(y)) < 2:
        return float("nan")
    class_counts = {label: int(np.sum(y == label)) for label in np.unique(y)}
    k_eff = min(int(k), min(class_counts.values()) - 1)
    if k_eff < 1:
        return float("nan")

    # Cells are small (typically 500 rows), so a dense pairwise Chebyshev
    # distance matrix is faster and more deterministic than repeated radius
    # queries.
    dist_all = np.max(np.abs(x[:, None, :] - x[None, :, :]), axis=2)
    eps = np.empty(n, dtype=np.float64)
    for label in np.unique(y):
        idx = np.where(y == label)[0]
        dist_label = dist_all[np.ix_(idx, idx)]
        dist_label.sort(axis=1)
        eps[idx] = dist_label[:, k_eff]

    m = np.empty(n, dtype=np.int64)
    for i in range(n):
        # Subtract a tiny epsilon to mimic the open-radius KSG count and avoid
        # counting points exactly on the kth same-class boundary.
        radius = max(float(eps[i]) - 1e-12, 0.0)
        m[i] = max(1, int(np.sum(dist_all[i] < radius)))

    class_count_vec = np.asarray([class_counts[label] for label in y], dtype=np.float64)
    mi_nat = float(digamma_approx(n)) + float(digamma_approx(k_eff)) - float(np.mean(digamma_approx(class_count_vec) + digamma_approx(m)))
    return float(max(mi_nat / np.log(2.0), 0.0))


def build_blocks(sequences: list[str], length: int, train_indices: list[int]) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    k, _ = build_feature_matrix(sequences, "ckmer4_count_l2", length=length, train_indices=train_indices)
    p, _ = build_feature_matrix(sequences, "property_l2", length=length, train_indices=train_indices)
    msp, _ = build_feature_matrix(sequences, "property_multiscale_mean_l2", length=length, train_indices=train_indices)
    return _safe_norm(k), _safe_norm(p), _safe_norm(msp)


def distances_for_cell(subset: pd.DataFrame, max_triplets: int, seed: int) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    sample_ids = sorted(subset["sample_id"].unique().tolist())
    if max_triplets > 0 and len(sample_ids) > max_triplets:
        rng = np.random.default_rng(seed)
        sample_ids = sorted(rng.choice(sample_ids, size=max_triplets, replace=False).tolist())
    ordered: list[str] = []
    for variant in ["clean", "random_noise", "local_property_shift"]:
        variant_df = subset[subset["variant"].eq(variant)].set_index("sample_id").loc[sample_ids]
        ordered.extend(variant_df["sequence"].astype(str).tolist())
    n = len(sample_ids)
    length = int(subset["source_length"].iloc[0])
    k, p, m = build_blocks(ordered, length=length, train_indices=list(range(n)))
    out = []
    for block in [k, p, m]:
        clean, noise, local = block[:n], block[n : 2 * n], block[2 * n : 3 * n]
        out.append(np.concatenate([np.linalg.norm(clean - noise, axis=1), np.linalg.norm(clean - local, axis=1)]))
    y = np.asarray([0] * n + [1] * n, dtype=int)
    return out[0], out[1], out[2], y


def permutation_p(x: np.ndarray, y: np.ndarray, observed: float, k: int, n_perm: int, seed: int) -> tuple[float, float]:
    rng = np.random.default_rng(seed)
    vals = []
    for i in range(n_perm):
        vals.append(mixed_knn_mi_bits(x, rng.permutation(y), k=k, seed=seed + i + 1))
    vals = np.asarray(vals, dtype=np.float64)
    vals = vals[np.isfinite(vals)]
    if vals.size == 0:
        return float("nan"), float("nan")
    p = float((1.0 + np.sum(vals >= observed)) / (1.0 + len(vals)))
    return p, float(np.mean(vals))


def subsample_ci(x: np.ndarray, y: np.ndarray, k: int, n_subsamples: int, frac: float, seed: int) -> tuple[float, float, float]:
    rng = np.random.default_rng(seed)
    vals = []
    labels = np.unique(y)
    for i in range(n_subsamples):
        keep = []
        for label in labels:
            idx = np.where(y == label)[0]
            size = max(k + 2, int(round(len(idx) * frac)))
            size = min(size, len(idx))
            keep.extend(rng.choice(idx, size=size, replace=False).tolist())
        keep = np.asarray(sorted(keep), dtype=int)
        vals.append(mixed_knn_mi_bits(x[keep], y[keep], k=k, seed=seed + 1000 + i))
    vals = np.asarray(vals, dtype=np.float64)
    vals = vals[np.isfinite(vals)]
    if vals.size == 0:
        return float("nan"), float("nan"), float("nan")
    return float(np.mean(vals)), float(np.quantile(vals, 0.025)), float(np.quantile(vals, 0.975))


def run_audit(triplets: pd.DataFrame, lengths: list[int], max_triplets: int, k_neighbors: int, n_perm: int, n_subsamples: int, seed: int) -> tuple[pd.DataFrame, pd.DataFrame]:
    rows = []
    triplets = triplets[triplets["source_length"].astype(int).isin(lengths)].copy()
    for (length, mode), subset in triplets.groupby(["source_length", "local_mode"], sort=True):
        dk, dp, dm, y = distances_for_cell(subset, max_triplets=max_triplets, seed=seed + int(length) + len(str(mode)))
        features = {
            "dK": dk.reshape(-1, 1),
            "dP": dp.reshape(-1, 1),
            "dM": dm.reshape(-1, 1),
            "dP_dM": np.column_stack([dp, dm]),
            "dK_dP": np.column_stack([dk, dp]),
            "dK_dM": np.column_stack([dk, dm]),
            "dK_dP_dM": np.column_stack([dk, dp, dm]),
        }
        mi_vals = {}
        for name, x in features.items():
            mi = mixed_knn_mi_bits(x, y, k=k_neighbors, seed=seed + int(length) + len(name))
            p, perm_mean = permutation_p(x, y, mi, k=k_neighbors, n_perm=n_perm, seed=seed + 2000 + int(length) + len(name))
            sub_mean, ci_low, ci_high = subsample_ci(x, y, k=k_neighbors, n_subsamples=n_subsamples, frac=0.8, seed=seed + 4000 + int(length) + len(name))
            mi_vals[name] = mi
            rows.append(
                {
                    "length": int(length),
                    "local_mode": mode,
                    "feature_set": name,
                    "knn_mi_bits": mi,
                    "perm_p": p,
                    "perm_mean_bits": perm_mean,
                    "subsample_mean_bits": sub_mean,
                    "subsample_ci_low": ci_low,
                    "subsample_ci_high": ci_high,
                    "n_rows": int(len(y)),
                    "k_neighbors": int(k_neighbors),
                }
            )
        rows.append(
            {
                "length": int(length),
                "local_mode": mode,
                "feature_set": "increment_dP_dM_given_dK",
                "knn_mi_bits": float(max(mi_vals["dK_dP_dM"] - mi_vals["dK"], 0.0)),
                "perm_p": np.nan,
                "perm_mean_bits": np.nan,
                "subsample_mean_bits": np.nan,
                "subsample_ci_low": np.nan,
                "subsample_ci_high": np.nan,
                "n_rows": int(len(y)),
                "k_neighbors": int(k_neighbors),
            }
        )
    detail = pd.DataFrame(rows)
    summary = (
        detail.groupby("feature_set", as_index=False)
        .agg(
            n_cells=("knn_mi_bits", "count"),
            mean_knn_mi_bits=("knn_mi_bits", "mean"),
            median_knn_mi_bits=("knn_mi_bits", "median"),
            mean_perm_p=("perm_p", "mean"),
            mean_subsample_ci_low=("subsample_ci_low", "mean"),
            mean_subsample_ci_high=("subsample_ci_high", "mean"),
        )
        .sort_values("mean_knn_mi_bits", ascending=False)
    )
    return detail, summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Run kNN/KSG-style MI robustness audit on local perturbation distance summaries.")
    parser.add_argument("--triplets-csv", default=str(PROJECT_ROOT / "results" / "stage3" / "local_mutation_sensitivity" / "local_mutation_triplets.csv"))
    parser.add_argument("--output-dir", default=str(PROJECT_ROOT / "results" / "stage3" / "reviewer_response" / "knn_mi_robustness"))
    parser.add_argument("--lengths", default="69,100,150")
    parser.add_argument("--max-triplets", type=int, default=250)
    parser.add_argument("--k-neighbors", type=int, default=5)
    parser.add_argument("--n-perm", type=int, default=100)
    parser.add_argument("--n-subsamples", type=int, default=100)
    parser.add_argument("--seed", type=int, default=20260625)
    args = parser.parse_args()

    started = time.time()
    set_global_seed(args.seed)
    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    triplets = pd.read_csv(args.triplets_csv)
    detail, summary = run_audit(
        triplets=triplets,
        lengths=parse_int_list(args.lengths),
        max_triplets=args.max_triplets,
        k_neighbors=args.k_neighbors,
        n_perm=args.n_perm,
        n_subsamples=args.n_subsamples,
        seed=args.seed,
    )
    detail.to_csv(out_dir / "knn_mi_detail.csv", index=False, encoding="utf-8-sig")
    summary.to_csv(out_dir / "knn_mi_summary.csv", index=False, encoding="utf-8-sig")
    lines = [
        "# kNN/KSG-style MI robustness audit",
        "",
        "This audit estimates MI between low-dimensional continuous perturbation-distance summaries and the local-vs-noise perturbation label using a k-nearest-neighbor mixed continuous/discrete estimator. It is a robustness check for the earlier discretized MI proxy, not an absolute information-theoretic proof over the full representation space.",
        "",
        "## Summary",
        "",
        summary.to_markdown(index=False, floatfmt=".4f") if not summary.empty else "No rows.",
        "",
    ]
    (out_dir / "knn_mi_summary.md").write_text("\n".join(lines), encoding="utf-8")
    (out_dir / "knn_mi_run.json").write_text(
        json.dumps(
            {
                "elapsed_seconds": time.time() - started,
                "triplets_csv": args.triplets_csv,
                "lengths": parse_int_list(args.lengths),
                "max_triplets": args.max_triplets,
                "k_neighbors": args.k_neighbors,
                "n_perm": args.n_perm,
                "n_subsamples": args.n_subsamples,
                "n_detail_rows": int(len(detail)),
            },
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    print(f"Wrote kNN MI robustness audit to {out_dir}")


if __name__ == "__main__":
    main()

