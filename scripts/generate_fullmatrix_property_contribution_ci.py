from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]


REP_LABELS = {
    "ckmer5_count_l2": "canonical 5-mer",
    "ckmer4_property_multiscale_mean_l2": "CK4P-MSP",
    "one_hot": "position one-hot",
    "property_channels": "position property channels",
    "base_property": "one-hot + property matrix",
    "rope_onehot": "RoPE one-hot",
    "rope_property": "RoPE property",
    "kmer_property": "position k-mer property",
}


PAIR_TESTS = [
    {
        "contrast": "property_channels - one_hot",
        "candidate": "property_channels",
        "baseline": "one_hot",
        "interpretation": "per-position biochemical property channels versus per-position base identity",
    },
    {
        "contrast": "base_property - one_hot",
        "candidate": "base_property",
        "baseline": "one_hot",
        "interpretation": "adding property channels to one-hot positional identity",
    },
    {
        "contrast": "rope_property - rope_onehot",
        "candidate": "rope_property",
        "baseline": "rope_onehot",
        "interpretation": "property semantics under the same RoPE-like positional transform",
    },
    {
        "contrast": "kmer_property - ckmer5_count_l2",
        "candidate": "kmer_property",
        "baseline": "ckmer5_count_l2",
        "interpretation": "position-resolved k-mer property sequence versus compact canonical k-mer counts",
    },
]


def bootstrap_mean_ci(values: pd.Series, rng: np.random.Generator, n_boot: int) -> tuple[float, float]:
    arr = pd.to_numeric(values, errors="coerce").dropna().to_numpy(dtype=float)
    if arr.size == 0:
        return float("nan"), float("nan")
    idx = rng.integers(0, arr.size, size=(n_boot, arr.size))
    means = arr[idx].mean(axis=1)
    return float(np.quantile(means, 0.025)), float(np.quantile(means, 0.975))


def ci_text(mean: float, lo: float, hi: float) -> str:
    if pd.isna(mean):
        return ""
    return f"{mean:.3f} [{lo:.3f}, {hi:.3f}]"


def summarize_with_ci(
    df: pd.DataFrame,
    group_cols: list[str],
    value_cols: list[str],
    n_boot: int,
    seed: int,
) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    rows: list[dict[str, object]] = []
    for key, group in df.groupby(group_cols, dropna=False):
        if not isinstance(key, tuple):
            key = (key,)
        row: dict[str, object] = dict(zip(group_cols, key))
        row["n_cells"] = int(len(group))
        for col in value_cols:
            values = pd.to_numeric(group[col], errors="coerce").dropna()
            row[f"{col}_mean"] = float(values.mean()) if not values.empty else float("nan")
            lo, hi = bootstrap_mean_ci(values, rng, n_boot)
            row[f"{col}_ci95_low"] = lo
            row[f"{col}_ci95_high"] = hi
        rows.append(row)
    out = pd.DataFrame(rows)
    if "representation" in out.columns:
        out["representation_label"] = out["representation"].map(REP_LABELS).fillna(out["representation"])
    return out


def paired_delta_ci(
    df: pd.DataFrame,
    match_cols: list[str],
    value_cols: list[str],
    n_boot: int,
    seed: int,
    task_col: str | None = None,
) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    task_values = [None]
    if task_col and task_col in df.columns:
        task_values = sorted(df[task_col].dropna().unique().tolist())

    rows: list[dict[str, object]] = []
    for task_value in task_values:
        task_df = df if task_value is None else df[df[task_col].eq(task_value)]
        for spec in PAIR_TESTS:
            candidate = task_df[task_df["representation"].eq(spec["candidate"])]
            baseline = task_df[task_df["representation"].eq(spec["baseline"])]
            if candidate.empty or baseline.empty:
                continue
            merged = candidate.merge(
                baseline,
                on=match_cols,
                suffixes=("_candidate", "_baseline"),
            )
            if merged.empty:
                continue
            row: dict[str, object] = {
                "task": task_value if task_value is not None else "",
                "contrast": spec["contrast"],
                "candidate": spec["candidate"],
                "baseline": spec["baseline"],
                "interpretation": spec["interpretation"],
                "n_paired_cells": int(len(merged)),
            }
            for col in value_cols:
                delta = pd.to_numeric(merged[f"{col}_candidate"], errors="coerce") - pd.to_numeric(
                    merged[f"{col}_baseline"], errors="coerce"
                )
                row[f"delta_{col}_mean"] = float(delta.mean())
                lo, hi = bootstrap_mean_ci(delta, rng, n_boot)
                row[f"delta_{col}_ci95_low"] = lo
                row[f"delta_{col}_ci95_high"] = hi
                row[f"delta {col} (95% CI)"] = ci_text(float(delta.mean()), lo, hi)
            rows.append(row)
    return pd.DataFrame(rows)


def save_table(df: pd.DataFrame, csv_path: Path, md_path: Path, display_cols: list[str] | None = None) -> None:
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(csv_path, index=False, encoding="utf-8-sig")
    display = df.copy() if display_cols is None else df[[col for col in display_cols if col in df.columns]].copy()
    for col in display.columns:
        if pd.api.types.is_float_dtype(display[col]):
            display[col] = display[col].map(lambda value: "" if pd.isna(value) else f"{value:.3f}")
    md_path.write_text(display.to_markdown(index=False), encoding="utf-8")


def controlled_summary(input_dir: Path, out_dir: Path, table_dir: Path, n_boot: int, seed: int) -> tuple[pd.DataFrame, pd.DataFrame]:
    df = pd.read_csv(input_dir / "position_property_controlled_results.csv")
    df = df[(df["split"].eq("5fold_cv")) & (df["classifier"].eq("logistic"))].copy()
    summary = summarize_with_ci(df, ["task", "representation"], ["macro_f1", "accuracy"], n_boot, seed)
    dim = df.groupby(["task", "representation"], as_index=False).agg(mean_features=("n_features", "mean"))
    summary = summary.merge(dim, on=["task", "representation"], how="left")
    summary["macro-F1 (95% CI)"] = summary.apply(
        lambda r: ci_text(r["macro_f1_mean"], r["macro_f1_ci95_low"], r["macro_f1_ci95_high"]),
        axis=1,
    )
    summary["accuracy (95% CI)"] = summary.apply(
        lambda r: ci_text(r["accuracy_mean"], r["accuracy_ci95_low"], r["accuracy_ci95_high"]),
        axis=1,
    )
    summary = summary.sort_values(["task", "macro_f1_mean"], ascending=[True, False])
    deltas = paired_delta_ci(
        df,
        match_cols=["length", "condition", "split", "classifier"],
        value_cols=["macro_f1", "accuracy"],
        n_boot=n_boot,
        seed=seed + 11,
        task_col="task",
    )
    save_table(
        summary,
        out_dir / "fullmatrix_property_controlled_ci.csv",
        table_dir / "stage3_table_fullmatrix_property_controlled_ci.md",
        ["task", "representation_label", "n_cells", "macro-F1 (95% CI)", "accuracy (95% CI)", "mean_features"],
    )
    save_table(
        deltas,
        out_dir / "fullmatrix_property_controlled_delta_ci.csv",
        table_dir / "stage3_table_fullmatrix_property_controlled_delta_ci.md",
        ["task", "contrast", "n_paired_cells", "delta macro_f1 (95% CI)", "delta accuracy (95% CI)", "interpretation"],
    )
    return summary, deltas


def art_summary(input_dir: Path, out_dir: Path, table_dir: Path, n_boot: int, seed: int) -> tuple[pd.DataFrame, pd.DataFrame]:
    df = pd.read_csv(input_dir / "art_stability_metrics.csv")
    summary = summarize_with_ci(
        df,
        ["representation"],
        ["paired_cosine_mean", "l2_delta_mean", "retrieval_top1"],
        n_boot,
        seed,
    )
    dim = df.groupby("representation", as_index=False).agg(mean_features=("n_features", "mean"))
    summary = summary.merge(dim, on="representation", how="left")
    summary["paired cosine (95% CI)"] = summary.apply(
        lambda r: ci_text(r["paired_cosine_mean_mean"], r["paired_cosine_mean_ci95_low"], r["paired_cosine_mean_ci95_high"]),
        axis=1,
    )
    summary["L2 drift (95% CI)"] = summary.apply(
        lambda r: ci_text(r["l2_delta_mean_mean"], r["l2_delta_mean_ci95_low"], r["l2_delta_mean_ci95_high"]),
        axis=1,
    )
    summary["top-1 retrieval (95% CI)"] = summary.apply(
        lambda r: ci_text(r["retrieval_top1_mean"], r["retrieval_top1_ci95_low"], r["retrieval_top1_ci95_high"]),
        axis=1,
    )
    summary = summary.sort_values("paired_cosine_mean_mean", ascending=False)
    deltas = paired_delta_ci(
        df,
        match_cols=["length", "condition"],
        value_cols=["paired_cosine_mean", "l2_delta_mean", "retrieval_top1"],
        n_boot=n_boot,
        seed=seed + 22,
    )
    save_table(
        summary,
        out_dir / "fullmatrix_property_art_ci.csv",
        table_dir / "stage3_table_fullmatrix_property_art_ci.md",
        [
            "representation_label",
            "n_cells",
            "paired cosine (95% CI)",
            "L2 drift (95% CI)",
            "top-1 retrieval (95% CI)",
            "mean_features",
        ],
    )
    save_table(
        deltas,
        out_dir / "fullmatrix_property_art_delta_ci.csv",
        table_dir / "stage3_table_fullmatrix_property_art_delta_ci.md",
        [
            "contrast",
            "n_paired_cells",
            "delta paired_cosine_mean (95% CI)",
            "delta l2_delta_mean (95% CI)",
            "delta retrieval_top1 (95% CI)",
            "interpretation",
        ],
    )
    return summary, deltas


def cami_summary(input_dir: Path, out_dir: Path, table_dir: Path, n_boot: int, seed: int) -> tuple[pd.DataFrame, pd.DataFrame]:
    df = pd.read_csv(input_dir / "cami_probe_readout.csv")
    df = df[df["error"].fillna("").eq("")]
    df = df[df["task"].eq("target_background")].copy()
    summary = summarize_with_ci(df, ["representation"], ["macro_f1", "accuracy"], n_boot, seed)
    dim = df.groupby("representation", as_index=False).agg(mean_features=("n_features", "mean"))
    summary = summary.merge(dim, on="representation", how="left")
    summary["macro-F1 (95% CI)"] = summary.apply(
        lambda r: ci_text(r["macro_f1_mean"], r["macro_f1_ci95_low"], r["macro_f1_ci95_high"]),
        axis=1,
    )
    summary["accuracy (95% CI)"] = summary.apply(
        lambda r: ci_text(r["accuracy_mean"], r["accuracy_ci95_low"], r["accuracy_ci95_high"]),
        axis=1,
    )
    summary = summary.sort_values("macro_f1_mean", ascending=False)
    deltas = paired_delta_ci(
        df,
        match_cols=["task", "length", "condition", "classifier", "label_col"],
        value_cols=["macro_f1", "accuracy"],
        n_boot=n_boot,
        seed=seed + 33,
    )
    save_table(
        summary,
        out_dir / "fullmatrix_property_cami_ci.csv",
        table_dir / "stage3_table_fullmatrix_property_cami_ci.md",
        ["representation_label", "n_cells", "macro-F1 (95% CI)", "accuracy (95% CI)", "mean_features"],
    )
    save_table(
        deltas,
        out_dir / "fullmatrix_property_cami_delta_ci.csv",
        table_dir / "stage3_table_fullmatrix_property_cami_delta_ci.md",
        ["contrast", "n_paired_cells", "delta macro_f1 (95% CI)", "delta accuracy (95% CI)", "interpretation"],
    )
    return summary, deltas


def write_summary(
    controlled: pd.DataFrame,
    controlled_delta: pd.DataFrame,
    art: pd.DataFrame,
    art_delta: pd.DataFrame,
    cami: pd.DataFrame,
    cami_delta: pd.DataFrame,
    out_path: Path,
) -> None:
    lines = [
        "# Full-Matrix Property Contribution Bootstrap CI Summary",
        "",
        "Confidence intervals are analysis-cell bootstrap intervals. They quantify stability of the lightweight screen across length, condition and classifier cells, not clinical population uncertainty.",
        "",
        "## Controlled position/order readout",
        "",
        controlled[
            ["task", "representation_label", "n_cells", "macro-F1 (95% CI)", "accuracy (95% CI)", "mean_features"]
        ].to_markdown(index=False),
        "",
        "## Controlled paired deltas",
        "",
        controlled_delta[
            ["task", "contrast", "n_paired_cells", "delta macro_f1 (95% CI)", "delta accuracy (95% CI)", "interpretation"]
        ].to_markdown(index=False),
        "",
        "## ART stability",
        "",
        art[
            [
                "representation_label",
                "n_cells",
                "paired cosine (95% CI)",
                "L2 drift (95% CI)",
                "top-1 retrieval (95% CI)",
                "mean_features",
            ]
        ].to_markdown(index=False),
        "",
        "## ART paired deltas",
        "",
        art_delta[
            [
                "contrast",
                "n_paired_cells",
                "delta paired_cosine_mean (95% CI)",
                "delta l2_delta_mean (95% CI)",
                "delta retrieval_top1 (95% CI)",
                "interpretation",
            ]
        ].to_markdown(index=False),
        "",
        "## CAMI target/background readout",
        "",
        cami[["representation_label", "n_cells", "macro-F1 (95% CI)", "accuracy (95% CI)", "mean_features"]].to_markdown(
            index=False
        ),
        "",
        "## CAMI paired deltas",
        "",
        cami_delta[["contrast", "n_paired_cells", "delta macro_f1 (95% CI)", "delta accuracy (95% CI)", "interpretation"]].to_markdown(
            index=False
        ),
        "",
        "## Interpretation boundary",
        "",
        "- Full-matrix position encodings are retained as high-resolution position-readable diagnostics, not as the main method.",
        "- A positive property-channel stability delta supports a biochemical-property contribution under perturbation.",
        "- CAMI target/background readout remains a small external probe; it should not be described as clinical classification performance.",
    ]
    out_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate CI summaries for full-matrix P-vs-non-P ablations.")
    parser.add_argument("--n-boot", type=int, default=2000)
    parser.add_argument("--seed", type=int, default=20260624)
    parser.add_argument("--controlled-dir", default=str(PROJECT_ROOT / "results" / "stage3" / "fullmatrix_property_contribution_controlled"))
    parser.add_argument("--art-dir", default=str(PROJECT_ROOT / "results" / "stage3" / "art_fullmatrix_property_contribution"))
    parser.add_argument("--cami-dir", default=str(PROJECT_ROOT / "results" / "stage3" / "cami_fullmatrix_property_contribution"))
    parser.add_argument("--output-dir", default=str(PROJECT_ROOT / "results" / "stage3" / "fullmatrix_property_contribution_ci"))
    parser.add_argument("--table-dir", default=str(PROJECT_ROOT / "manuscript" / "tables"))
    args = parser.parse_args()

    out_dir = Path(args.output_dir)
    table_dir = Path(args.table_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    table_dir.mkdir(parents=True, exist_ok=True)

    controlled, controlled_delta = controlled_summary(Path(args.controlled_dir), out_dir, table_dir, args.n_boot, args.seed)
    art, art_delta = art_summary(Path(args.art_dir), out_dir, table_dir, args.n_boot, args.seed + 100)
    cami, cami_delta = cami_summary(Path(args.cami_dir), out_dir, table_dir, args.n_boot, args.seed + 200)
    write_summary(controlled, controlled_delta, art, art_delta, cami, cami_delta, out_dir / "fullmatrix_property_contribution_ci_summary.md")
    print(f"Wrote full-matrix property contribution CI outputs to {out_dir}")


if __name__ == "__main__":
    main()
