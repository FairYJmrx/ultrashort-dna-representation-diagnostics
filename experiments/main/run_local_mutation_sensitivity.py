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
from sklearn.neighbors import NearestCentroid
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler, normalize

def _find_project_root(start: Path) -> Path:
    for candidate in [start.parent, *start.parents]:
        if (candidate / "methods").is_dir() and (candidate / "configs").is_dir():
            return candidate
    raise RuntimeError("Could not locate the release repository root.")


PROJECT_ROOT = _find_project_root(Path(__file__).resolve())
sys.path.insert(0, str(PROJECT_ROOT))

from src.stage2_features import build_feature_matrix  # noqa: E402


BASES = np.asarray(list("ACGT"))
PROPERTY_SHIFT = {
    "A": "C",
    "C": "A",
    "G": "T",
    "T": "G",
    "N": "A",
}


def parse_csv_list(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


def parse_int_list(value: str) -> list[int]:
    return [int(item.strip()) for item in value.split(",") if item.strip()]


def random_read(rng: np.random.Generator, length: int) -> str:
    return "".join(rng.choice(BASES, size=length, replace=True).tolist())


def mutate_random_noise(seq: str, n_changes: int, rng: np.random.Generator) -> tuple[str, list[int]]:
    chars = list(seq)
    n_changes = min(n_changes, len(chars))
    positions = rng.choice(np.arange(len(chars)), size=n_changes, replace=False)
    for pos in positions:
        current = chars[int(pos)]
        choices = [base for base in "ACGT" if base != current]
        chars[int(pos)] = str(rng.choice(choices))
    return "".join(chars), sorted(int(pos) for pos in positions)


def local_window_positions(length: int, n_changes: int, mode: str, rng: np.random.Generator) -> list[int]:
    if mode == "center":
        center = length // 2
    elif mode == "left":
        center = max(0, length // 4)
    elif mode == "right":
        center = min(length - 1, (3 * length) // 4)
    elif mode == "jittered":
        low = max(0, length // 4)
        high = max(low + 1, (3 * length) // 4)
        center = int(rng.integers(low, high))
    else:
        raise ValueError(f"Unsupported local mutation mode: {mode}")
    half = n_changes // 2
    start = max(0, min(length - n_changes, center - half))
    return list(range(start, start + n_changes))


def mutate_local_property_shift(
    seq: str,
    n_changes: int,
    mode: str,
    rng: np.random.Generator,
) -> tuple[str, list[int]]:
    chars = list(seq)
    positions = local_window_positions(len(chars), min(n_changes, len(chars)), mode=mode, rng=rng)
    for pos in positions:
        chars[pos] = PROPERTY_SHIFT.get(chars[pos], "A")
    return "".join(chars), positions


def make_triplets(
    lengths: list[int],
    n_reads: int,
    mutation_fraction: float,
    local_modes: list[str],
    seed: int,
) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    rows: list[dict[str, object]] = []
    for length in lengths:
        n_changes = max(1, int(round(length * mutation_fraction)))
        for mode in local_modes:
            for read_id in range(n_reads):
                clean = random_read(rng, length)
                noise, noise_positions = mutate_random_noise(clean, n_changes, rng)
                local, local_positions = mutate_local_property_shift(clean, n_changes, mode, rng)
                sample_id = f"L{length}_{mode}_{read_id:05d}"
                for variant, sequence, positions in [
                    ("clean", clean, []),
                    ("random_noise", noise, noise_positions),
                    ("local_property_shift", local, local_positions),
                ]:
                    rows.append(
                        {
                            "sample_id": sample_id,
                            "source_length": length,
                            "local_mode": mode,
                            "variant": variant,
                            "sequence": sequence,
                            "n_changes": n_changes if variant != "clean" else 0,
                            "mutation_positions": ",".join(str(pos) for pos in positions),
                        }
                    )
    return pd.DataFrame(rows)


def classifier_registry(seed: int) -> dict[str, object]:
    return {
        "nearest_centroid": NearestCentroid(),
        "logistic": make_pipeline(StandardScaler(), LogisticRegression(max_iter=5000, random_state=seed)),
    }


def split_feature_blocks(x: np.ndarray, n_triplets: int) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    clean = x[0:n_triplets]
    noise = x[n_triplets: 2 * n_triplets]
    local = x[2 * n_triplets: 3 * n_triplets]
    return clean, noise, local


def pair_metrics(clean: np.ndarray, other: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    clean_norm = normalize(clean, norm="l2", axis=1)
    other_norm = normalize(other, norm="l2", axis=1)
    cosine = np.sum(clean_norm * other_norm, axis=1)
    l2 = np.linalg.norm(clean_norm - other_norm, axis=1)
    return cosine, l2


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
    # Noise and local deltas from a common clean template are correlated. Keep
    # each template wholly in train or test to avoid paired-template leakage.
    holdout_splitter = StratifiedGroupKFold(n_splits=3, shuffle=True, random_state=seed)
    train_idx, test_idx = next(holdout_splitter.split(x_delta, y, groups))
    rows: list[dict[str, object]] = []
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
            scores_acc: list[float] = []
            scores_f1: list[float] = []
            for cv_train, cv_test in skf.split(x_delta, y, groups):
                clf = classifier_registry(seed)[clf_name]
                clf.fit(x_delta[cv_train], y[cv_train])
                pred = clf.predict(x_delta[cv_test])
                scores_acc.append(float(accuracy_score(y[cv_test], pred)))
                scores_f1.append(float(f1_score(y[cv_test], pred, average="macro", zero_division=0)))
            rows.append(
                {
                    "split": f"{n_splits}fold_grouped_cv",
                    "classifier": clf_name,
                    "accuracy": float(np.mean(scores_acc)),
                    "macro_f1": float(np.mean(scores_f1)),
                    "accuracy_std": float(np.std(scores_acc)),
                    "macro_f1_std": float(np.std(scores_f1)),
                }
            )
    return rows


def bootstrap_ci(values: np.ndarray, seed: int, n_bootstrap: int = 1000) -> tuple[float, float]:
    if values.size == 0:
        return float("nan"), float("nan")
    rng = np.random.default_rng(seed)
    means = []
    for _ in range(n_bootstrap):
        sample = rng.choice(values, size=values.size, replace=True)
        means.append(float(np.mean(sample)))
    return float(np.quantile(means, 0.025)), float(np.quantile(means, 0.975))


def format_ci(mean: float, low: float, high: float) -> str:
    return f"{mean:.3f} [{low:.3f}, {high:.3f}]"


def run_experiment(
    triplets: pd.DataFrame,
    representations: list[str],
    seed: int,
    cv_folds: int,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    metric_rows: list[dict[str, object]] = []
    readout_rows: list[dict[str, object]] = []
    summary_rows: list[dict[str, object]] = []

    for (length, mode), subset in triplets.groupby(["source_length", "local_mode"], sort=True):
        ordered = []
        sample_ids = sorted(subset["sample_id"].unique().tolist())
        for variant in ["clean", "random_noise", "local_property_shift"]:
            variant_df = subset[subset["variant"].eq(variant)].set_index("sample_id").loc[sample_ids]
            ordered.extend(variant_df["sequence"].astype(str).tolist())
        n_triplets = len(sample_ids)
        train_indices = list(range(n_triplets))
        for rep in representations:
            x, info = build_feature_matrix(ordered, rep, length=int(length), train_indices=train_indices)
            clean, noise, local = split_feature_blocks(x, n_triplets)
            noise_cos, noise_l2 = pair_metrics(clean, noise)
            local_cos, local_l2 = pair_metrics(clean, local)
            ratio = local_l2 / np.maximum(noise_l2, 1e-12)
            delta = local_l2 - noise_l2
            for idx, sample_id in enumerate(sample_ids):
                metric_rows.append(
                    {
                        "sample_id": sample_id,
                        "length": int(length),
                        "local_mode": mode,
                        "representation": rep,
                        "noise_cosine": float(noise_cos[idx]),
                        "local_cosine": float(local_cos[idx]),
                        "noise_l2": float(noise_l2[idx]),
                        "local_l2": float(local_l2[idx]),
                        "local_minus_noise_l2": float(delta[idx]),
                        "selective_sensitivity_ratio": float(ratio[idx]),
                        "n_features": info.n_features,
                        "density": info.density,
                        "avg_nnz_per_read": info.avg_nnz_per_read,
                    }
                )
            for row in evaluate_delta_readout(
                clean,
                noise,
                local,
                sample_ids=sample_ids,
                seed=seed,
                cv_folds=cv_folds,
            ):
                row.update(
                    {
                        "length": int(length),
                        "local_mode": mode,
                        "representation": rep,
                        "n_samples": int(2 * n_triplets),
                        "n_features": info.n_features,
                    }
                )
                readout_rows.append(row)

            ratio_low, ratio_high = bootstrap_ci(ratio, seed=seed + int(length))
            delta_low, delta_high = bootstrap_ci(delta, seed=seed + int(length) + 17)
            summary_rows.append(
                {
                    "length": int(length),
                    "local_mode": mode,
                    "representation": rep,
                    "noise_l2_mean": float(np.mean(noise_l2)),
                    "local_l2_mean": float(np.mean(local_l2)),
                    "local_minus_noise_l2_mean": float(np.mean(delta)),
                    "local_minus_noise_l2_ci_low": delta_low,
                    "local_minus_noise_l2_ci_high": delta_high,
                    "selective_sensitivity_ratio_mean": float(np.mean(ratio)),
                    "selective_sensitivity_ratio_ci_low": ratio_low,
                    "selective_sensitivity_ratio_ci_high": ratio_high,
                    "noise_cosine_mean": float(np.mean(noise_cos)),
                    "local_cosine_mean": float(np.mean(local_cos)),
                    "n_features": info.n_features,
                    "density": info.density,
                    "avg_nnz_per_read": info.avg_nnz_per_read,
                    "n_triplets": n_triplets,
                }
            )
    return pd.DataFrame(metric_rows), pd.DataFrame(readout_rows), pd.DataFrame(summary_rows)


def write_summary(summary: pd.DataFrame, readout: pd.DataFrame, path: Path) -> None:
    focus = summary.groupby("representation", as_index=False).agg(
        noise_l2=("noise_l2_mean", "mean"),
        local_l2=("local_l2_mean", "mean"),
        local_minus_noise_l2=("local_minus_noise_l2_mean", "mean"),
        selective_sensitivity_ratio=("selective_sensitivity_ratio_mean", "mean"),
        n_features=("n_features", "mean"),
    )
    focus = focus.sort_values(["selective_sensitivity_ratio", "local_minus_noise_l2"], ascending=False)
    readout_focus = (
        readout[readout["split"].astype(str).str.contains("grouped_cv")]
        .groupby(["representation", "classifier"], as_index=False)
        .agg(macro_f1=("macro_f1", "mean"), accuracy=("accuracy", "mean"), n_features=("n_features", "mean"))
        .sort_values(["macro_f1", "accuracy"], ascending=False)
    )
    lines = [
        "# Local Mutation Sensitivity Summary",
        "",
        "This experiment compares equal-count random substitutions with local property-shift substitutions. A useful selective-sensitivity representation should keep random-noise distance low while making structured local mutation distance higher.",
        "",
        "## Distance-based selective sensitivity",
        "",
        focus.to_markdown(index=False),
        "",
        "## Delta-readout: random noise versus local property shift",
        "",
        readout_focus.to_markdown(index=False),
        "",
        "## Interpretation",
        "",
        "- `selective_sensitivity_ratio > 1` means the representation moved farther for local property-shift mutations than for equal-count random substitutions.",
        "- High macro-F1 in the delta-readout means a shallow model can distinguish local biochemical/positional change from random noise using representation deltas.",
        "- These metrics complement perturbation stability: they test selective sensitivity rather than invariance.",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Measure selective sensitivity to local biochemical/positional mutations.")
    parser.add_argument("--output-dir", default=str(PROJECT_ROOT / "results" / "stage3" / "local_mutation_sensitivity"))
    parser.add_argument(
        "--representations",
        default="ck4,ck4_p,ck4_msp,ck4p_msp",
    )
    parser.add_argument("--lengths", default="69,100,150")
    parser.add_argument("--local-modes", default="center,left,right,jittered")
    parser.add_argument("--n-reads", type=int, default=250)
    parser.add_argument("--mutation-fraction", type=float, default=0.03)
    parser.add_argument("--cv-folds", type=int, default=5)
    parser.add_argument("--seed", type=int, default=20260624)
    args = parser.parse_args()

    started = time.time()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    representations = parse_csv_list(args.representations)
    lengths = parse_int_list(args.lengths)
    local_modes = parse_csv_list(args.local_modes)

    triplets = make_triplets(
        lengths=lengths,
        n_reads=args.n_reads,
        mutation_fraction=args.mutation_fraction,
        local_modes=local_modes,
        seed=args.seed,
    )
    metrics, readout, summary = run_experiment(
        triplets=triplets,
        representations=representations,
        seed=args.seed,
        cv_folds=args.cv_folds,
    )

    triplets.to_csv(output_dir / "local_mutation_triplets.csv", index=False, encoding="utf-8-sig")
    metrics.to_csv(output_dir / "local_mutation_pair_metrics.csv", index=False, encoding="utf-8-sig")
    readout.to_csv(output_dir / "local_mutation_delta_readout.csv", index=False, encoding="utf-8-sig")
    summary.to_csv(output_dir / "local_mutation_sensitivity_summary.csv", index=False, encoding="utf-8-sig")
    write_summary(summary, readout, output_dir / "local_mutation_sensitivity_summary.md")
    (output_dir / "local_mutation_sensitivity_run.json").write_text(
        json.dumps(
            {
                "elapsed_seconds": time.time() - started,
                "representations": representations,
                "lengths": lengths,
                "local_modes": local_modes,
                "n_reads": args.n_reads,
                "mutation_fraction": args.mutation_fraction,
                "cv_folds": args.cv_folds,
                "seed": args.seed,
                "n_triplet_rows": int(len(triplets)),
                "n_metric_rows": int(len(metrics)),
                "n_readout_rows": int(len(readout)),
            },
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    print(f"Wrote local mutation sensitivity results to {output_dir}")


if __name__ == "__main__":
    main()

