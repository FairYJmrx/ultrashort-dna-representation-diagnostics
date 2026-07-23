from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import wilcoxon


def _find_project_root(start: Path) -> Path:
    for candidate in [start.parent, *start.parents]:
        if (candidate / "methods").is_dir() and (candidate / "configs").is_dir():
            return candidate
    raise RuntimeError("Could not locate the release repository root.")


PROJECT_ROOT = _find_project_root(Path(__file__).resolve())
OUT_DIR = PROJECT_ROOT / "results" / "stage3" / "reviewer_response" / "statistical_tests"


COMPARISONS = [
    {
        "source": "compact_baselines",
        "path": PROJECT_ROOT / "results" / "stage3" / "compact_baselines" / "compact_baseline_stability.csv",
        "label": "CSP vs canonical 5-mer",
        "left": "cspaced_property_l2",
        "right": "ckmer5_count_l2",
    },
    {
        "source": "compact_baselines",
        "path": PROJECT_ROOT / "results" / "stage3" / "compact_baselines" / "compact_baseline_stability.csv",
        "label": "CSP vs canonical spaced count",
        "left": "cspaced_property_l2",
        "right": "cspaced_count_l2",
    },
    {
        "source": "compact_baselines",
        "path": PROJECT_ROOT / "results" / "stage3" / "compact_baselines" / "compact_baseline_stability.csv",
        "label": "MinHash k5 vs canonical 5-mer",
        "left": "minhash_k5_s128",
        "right": "ckmer5_count_l2",
    },
    {
        "source": "position_property_ablation",
        "path": PROJECT_ROOT / "results" / "stage3" / "position_property_ablation" / "compact_baseline_stability.csv",
        "label": "CK4P-MSP vs CK4",
        "left": "ckmer4_property_multiscale_mean_l2",
        "right": "ckmer4_count_l2",
    },
    {
        "source": "position_property_ablation",
        "path": PROJECT_ROOT / "results" / "stage3" / "position_property_ablation" / "compact_baseline_stability.csv",
        "label": "CK4P-MSP vs CK4+P",
        "left": "ckmer4_property_multiscale_mean_l2",
        "right": "ckmer4_property_l2",
    },
    {
        "source": "position_property_ablation",
        "path": PROJECT_ROOT / "results" / "stage3" / "position_property_ablation" / "compact_baseline_stability.csv",
        "label": "CK4P-MSP vs CK5",
        "left": "ckmer4_property_multiscale_mean_l2",
        "right": "ckmer5_count_l2",
    },
    {
        "source": "ART",
        "path": PROJECT_ROOT / "results" / "stage3" / "art_illumina" / "art_stability_metrics.csv",
        "label": "ART CSP vs canonical 5-mer",
        "left": "cspaced_property_l2",
        "right": "ckmer5_count_l2",
    },
]


METRICS = {
    "paired_cosine_mean": "higher",
    "l2_delta_mean": "lower",
    "retrieval_top1": "higher",
}


def benjamini_hochberg(p_values: list[float]) -> list[float]:
    arr = np.asarray(p_values, dtype=float)
    q = np.full(arr.shape, np.nan, dtype=float)
    valid = np.where(~np.isnan(arr))[0]
    if valid.size == 0:
        return q.tolist()
    ordered = valid[np.argsort(arr[valid])]
    m = float(valid.size)
    running = 1.0
    for rank, idx in enumerate(ordered[::-1], start=1):
        original_rank = valid.size - rank + 1
        value = arr[idx] * m / original_rank
        running = min(running, value)
        q[idx] = min(running, 1.0)
    return q.tolist()


def paired_table(df: pd.DataFrame, left: str, right: str, metric: str) -> pd.DataFrame:
    keys = [col for col in ["length", "condition", "quality_bin"] if col in df.columns]
    sub = df[df["representation"].isin([left, right])].copy()
    if not keys:
        sub["_cell"] = np.arange(len(sub))
        keys = ["_cell"]
    pivot = sub.pivot_table(index=keys, columns="representation", values=metric, aggfunc="mean")
    if left not in pivot.columns or right not in pivot.columns:
        return pd.DataFrame()
    return pivot[[left, right]].dropna().reset_index()


def wilcoxon_row(label: str, source: str, left: str, right: str, metric: str, direction: str, paired: pd.DataFrame) -> dict[str, object]:
    if paired.empty:
        return {
            "comparison": label,
            "source": source,
            "metric": metric,
            "direction": direction,
            "n_cells": 0,
            "mean_left": np.nan,
            "mean_right": np.nan,
            "mean_difference_left_minus_right": np.nan,
            "median_difference_left_minus_right": np.nan,
            "wilcoxon_p": np.nan,
            "left_better_fraction": np.nan,
        }
    diff = paired[left].to_numpy(dtype=float) - paired[right].to_numpy(dtype=float)
    if np.allclose(diff, 0):
        p_value = 1.0
    else:
        alternative = "greater" if direction == "higher" else "less"
        p_value = float(wilcoxon(paired[left], paired[right], alternative=alternative, zero_method="wilcox").pvalue)
    if direction == "higher":
        better = diff > 0
    else:
        better = diff < 0
    return {
        "comparison": label,
        "source": source,
        "metric": metric,
        "direction": direction,
        "n_cells": int(len(paired)),
        "mean_left": float(paired[left].mean()),
        "mean_right": float(paired[right].mean()),
        "mean_difference_left_minus_right": float(np.mean(diff)),
        "median_difference_left_minus_right": float(np.median(diff)),
        "wilcoxon_p": p_value,
        "left_better_fraction": float(np.mean(better)),
    }


def format_float(value: object) -> str:
    if pd.isna(value):
        return ""
    value = float(value)
    if value < 0.001 and value > 0:
        return f"{value:.2e}"
    return f"{value:.3f}"


def write_markdown(df: pd.DataFrame, path: Path) -> None:
    display = df.copy()
    for col in display.columns:
        if pd.api.types.is_float_dtype(display[col]):
            display[col] = display[col].map(format_float)
    lines = [
        "# Reviewer-response paired statistical tests",
        "",
        "Tests are paired over matched analysis cells such as length-by-perturbation cells. For paired cosine and retrieval, the alternative hypothesis is that the left representation is higher. For L2 drift, the alternative hypothesis is that the left representation is lower. Benjamini-Hochberg q-values are computed across all rows in this table.",
        "",
        display.to_markdown(index=False),
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, object]] = []
    for comparison in COMPARISONS:
        path = comparison["path"]
        if not path.exists():
            continue
        df = pd.read_csv(path)
        if "error" in df.columns:
            df = df[df["error"].isna()].copy()
        for metric, direction in METRICS.items():
            if metric not in df.columns:
                continue
            paired = paired_table(df, comparison["left"], comparison["right"], metric)
            rows.append(
                wilcoxon_row(
                    label=comparison["label"],
                    source=comparison["source"],
                    left=comparison["left"],
                    right=comparison["right"],
                    metric=metric,
                    direction=direction,
                    paired=paired,
                )
            )
    out = pd.DataFrame(rows)
    if not out.empty:
        out["bh_q"] = benjamini_hochberg(out["wilcoxon_p"].astype(float).tolist())
        out = out.sort_values(["source", "comparison", "metric"]).reset_index(drop=True)
    out.to_csv(OUT_DIR / "paired_wilcoxon_tests.csv", index=False, encoding="utf-8-sig")
    write_markdown(out, OUT_DIR / "paired_wilcoxon_tests.md")
    print(f"Wrote {OUT_DIR / 'paired_wilcoxon_tests.csv'}")
    print(f"Wrote {OUT_DIR / 'paired_wilcoxon_tests.md'}")


if __name__ == "__main__":
    main()

