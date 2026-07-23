from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd


def _find_project_root(start: Path) -> Path:
    for candidate in [start.parent, *start.parents]:
        if (candidate / "methods").is_dir() and (candidate / "configs").is_dir():
            return candidate
    raise RuntimeError("Could not locate the release repository root.")


PROJECT_ROOT = _find_project_root(Path(__file__).resolve())


REP_LABELS = {
    "ckmer5_count_l2": "canonical 5-mer",
    "ckmer7_count_l2": "canonical 7-mer",
    "cspaced_count_l2": "canonical spaced count",
    "cspaced_property_l2": "CSP",
    "hybrid_ckmer5_csp": "canonical 5-mer + CSP",
    "hybrid_ckmer7_csp": "canonical 7-mer + CSP",
    "minhash_k5_s128": "MinHash k=5, s=128",
    "minhash_k7_s128": "MinHash k=7, s=128",
    "eiip_l2": "EIIP positional signal",
    "eiip_summary_l2": "EIIP summary",
}


FOCUS_REPS = [
    "ckmer5_count_l2",
    "ckmer7_count_l2",
    "cspaced_count_l2",
    "cspaced_property_l2",
    "hybrid_ckmer5_csp",
    "minhash_k5_s128",
    "minhash_k7_s128",
    "eiip_l2",
    "eiip_summary_l2",
]


def bootstrap_mean_ci(values: pd.Series, rng: np.random.Generator, n_boot: int) -> tuple[float, float]:
    arr = pd.to_numeric(values, errors="coerce").dropna().to_numpy(dtype=float)
    if arr.size == 0:
        return float("nan"), float("nan")
    idx = rng.integers(0, arr.size, size=(n_boot, arr.size))
    means = arr[idx].mean(axis=1)
    return float(np.quantile(means, 0.025)), float(np.quantile(means, 0.975))


def summarize_with_ci(
    df: pd.DataFrame,
    group_cols: list[str],
    value_cols: list[str],
    n_boot: int,
    seed: int,
) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    rng = np.random.default_rng(seed)
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
    return pd.DataFrame(rows)


def add_labels(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    if "representation" in out.columns:
        out["representation_label"] = out["representation"].map(REP_LABELS).fillna(out["representation"])
    return out


def save_table(df: pd.DataFrame, csv_path: Path, md_path: Path) -> None:
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(csv_path, index=False, encoding="utf-8-sig")
    display = df.copy()
    for col in display.columns:
        if pd.api.types.is_float_dtype(display[col]):
            display[col] = display[col].map(lambda value: "" if pd.isna(value) else f"{value:.3f}")
    md_path.write_text(display.to_markdown(index=False), encoding="utf-8")


def ci_text(mean: float, lo: float, hi: float) -> str:
    if pd.isna(mean):
        return ""
    return f"{mean:.3f} [{lo:.3f}, {hi:.3f}]"


def compact_summary(input_dir: Path, out_dir: Path, table_dir: Path, n_boot: int, seed: int) -> pd.DataFrame:
    df = pd.read_csv(input_dir / "compact_baseline_stability.csv")
    df = df[df["representation"].isin(FOCUS_REPS)].copy()
    out = summarize_with_ci(
        df,
        group_cols=["representation"],
        value_cols=["paired_cosine_mean", "l2_delta_mean", "retrieval_top1"],
        n_boot=n_boot,
        seed=seed,
    )
    dim = df.groupby("representation", as_index=False).agg(
        median_features=("n_features", "median"),
        mean_density=("density", "mean"),
    )
    out = add_labels(out.merge(dim, on="representation", how="left"))
    order = {rep: idx for idx, rep in enumerate(FOCUS_REPS)}
    out["_order"] = out["representation"].map(order)
    out = out.sort_values("_order").drop(columns="_order")
    out["paired cosine (95% CI)"] = out.apply(
        lambda r: ci_text(r["paired_cosine_mean_mean"], r["paired_cosine_mean_ci95_low"], r["paired_cosine_mean_ci95_high"]),
        axis=1,
    )
    out["L2 drift (95% CI)"] = out.apply(
        lambda r: ci_text(r["l2_delta_mean_mean"], r["l2_delta_mean_ci95_low"], r["l2_delta_mean_ci95_high"]),
        axis=1,
    )
    out["top-1 retrieval (95% CI)"] = out.apply(
        lambda r: ci_text(r["retrieval_top1_mean"], r["retrieval_top1_ci95_low"], r["retrieval_top1_ci95_high"]),
        axis=1,
    )
    save_table(out, out_dir / "stage3_compact_bootstrap_ci.csv", table_dir / "stage3_table_compact_bootstrap_ci.md")
    return out


def art_summary(input_dir: Path, quality_dir: Path, out_dir: Path, table_dir: Path, n_boot: int, seed: int) -> tuple[pd.DataFrame, pd.DataFrame]:
    df = pd.read_csv(input_dir / "art_stability_metrics.csv")
    df = df[df["representation"].isin(FOCUS_REPS)].copy()
    overall = summarize_with_ci(
        df,
        group_cols=["representation"],
        value_cols=["paired_cosine_mean", "l2_delta_mean", "retrieval_top1"],
        n_boot=n_boot,
        seed=seed + 101,
    )
    dim = df.groupby("representation", as_index=False).agg(
        median_features=("n_features", "median"),
        mean_density=("density", "mean"),
    )
    overall = add_labels(overall.merge(dim, on="representation", how="left"))
    order = {rep: idx for idx, rep in enumerate(FOCUS_REPS)}
    overall["_order"] = overall["representation"].map(order)
    overall = overall.sort_values("_order").drop(columns="_order")
    overall["paired cosine (95% CI)"] = overall.apply(
        lambda r: ci_text(r["paired_cosine_mean_mean"], r["paired_cosine_mean_ci95_low"], r["paired_cosine_mean_ci95_high"]),
        axis=1,
    )
    overall["L2 drift (95% CI)"] = overall.apply(
        lambda r: ci_text(r["l2_delta_mean_mean"], r["l2_delta_mean_ci95_low"], r["l2_delta_mean_ci95_high"]),
        axis=1,
    )
    overall["top-1 retrieval (95% CI)"] = overall.apply(
        lambda r: ci_text(r["retrieval_top1_mean"], r["retrieval_top1_ci95_low"], r["retrieval_top1_ci95_high"]),
        axis=1,
    )
    save_table(overall, out_dir / "stage3_art_bootstrap_ci.csv", table_dir / "stage3_table_art_bootstrap_ci.md")

    qdf = pd.read_csv(quality_dir / "art_quality_stratified_stability.csv")
    qdf = qdf[qdf["representation"].isin(FOCUS_REPS)].copy()
    quality = summarize_with_ci(
        qdf,
        group_cols=["quality_bin", "representation"],
        value_cols=["paired_cosine_mean", "l2_delta_mean", "retrieval_top1"],
        n_boot=n_boot,
        seed=seed + 202,
    )
    quality = add_labels(quality)
    quality["paired cosine (95% CI)"] = quality.apply(
        lambda r: ci_text(r["paired_cosine_mean_mean"], r["paired_cosine_mean_ci95_low"], r["paired_cosine_mean_ci95_high"]),
        axis=1,
    )
    quality["L2 drift (95% CI)"] = quality.apply(
        lambda r: ci_text(r["l2_delta_mean_mean"], r["l2_delta_mean_ci95_low"], r["l2_delta_mean_ci95_high"]),
        axis=1,
    )
    quality["top-1 retrieval (95% CI)"] = quality.apply(
        lambda r: ci_text(r["retrieval_top1_mean"], r["retrieval_top1_ci95_low"], r["retrieval_top1_ci95_high"]),
        axis=1,
    )
    save_table(quality, out_dir / "stage3_art_quality_bootstrap_ci.csv", table_dir / "stage3_table_art_quality_bootstrap_ci.md")
    return overall, quality


def cami_summary(input_dir: Path, out_dir: Path, table_dir: Path, n_boot: int, seed: int) -> pd.DataFrame:
    df = pd.read_csv(input_dir / "cami_probe_readout.csv")
    df = df[df["representation"].isin(FOCUS_REPS)].copy()
    df = df.dropna(subset=["macro_f1"])
    out = summarize_with_ci(
        df,
        group_cols=["task", "representation"],
        value_cols=["macro_f1", "accuracy"],
        n_boot=n_boot,
        seed=seed + 303,
    )
    dim = df.groupby(["task", "representation"], as_index=False).agg(mean_features=("n_features", "mean"))
    out = add_labels(out.merge(dim, on=["task", "representation"], how="left"))
    out = out.sort_values(["task", "macro_f1_mean"], ascending=[True, False])
    out["macro-F1 (95% CI)"] = out.apply(
        lambda r: ci_text(r["macro_f1_mean"], r["macro_f1_ci95_low"], r["macro_f1_ci95_high"]),
        axis=1,
    )
    out["accuracy (95% CI)"] = out.apply(
        lambda r: ci_text(r["accuracy_mean"], r["accuracy_ci95_low"], r["accuracy_ci95_high"]),
        axis=1,
    )
    save_table(out, out_dir / "stage3_cami_macro_f1_bootstrap_ci.csv", table_dir / "stage3_table_cami_macro_f1_bootstrap_ci.md")
    return out


def concise_view(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    present = [col for col in columns if col in df.columns]
    return df[present].copy()


def write_summary(compact: pd.DataFrame, art: pd.DataFrame, quality: pd.DataFrame, cami: pd.DataFrame, out_path: Path) -> None:
    c_view = concise_view(
        compact,
        ["representation_label", "n_cells", "paired cosine (95% CI)", "L2 drift (95% CI)", "top-1 retrieval (95% CI)", "median_features"],
    )
    a_view = concise_view(
        art,
        ["representation_label", "n_cells", "paired cosine (95% CI)", "L2 drift (95% CI)", "top-1 retrieval (95% CI)", "median_features"],
    )
    q_focus = quality[quality["representation"].eq("cspaced_property_l2")].copy()
    q_view = concise_view(
        q_focus,
        ["quality_bin", "representation_label", "n_cells", "paired cosine (95% CI)", "L2 drift (95% CI)", "top-1 retrieval (95% CI)"],
    )
    cami_view = concise_view(
        cami,
        ["task", "representation_label", "n_cells", "macro-F1 (95% CI)", "accuracy (95% CI)", "mean_features"],
    )
    lines = [
        "# Stage-3 Bootstrap CI Summary",
        "",
        "Confidence intervals are analysis-cell bootstrap intervals. Stability cells are length-by-perturbation or length-by-quality strata; CAMI cells are task/length/condition/classifier readout rows. These intervals quantify robustness across the controlled analysis grid and should not be read as clinical sample-level uncertainty.",
        "",
        "## Compact baseline stability",
        "",
        c_view.to_markdown(index=False),
        "",
        "## ART Illumina stability",
        "",
        a_view.to_markdown(index=False),
        "",
        "## ART quality-stratified CSP stability",
        "",
        q_view.to_markdown(index=False),
        "",
        "## CAMI_TOY_low macro-F1",
        "",
        cami_view.to_markdown(index=False),
        "",
    ]
    out_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate stage-3 analysis-cell bootstrap confidence intervals.")
    parser.add_argument("--n-boot", type=int, default=2000)
    parser.add_argument("--seed", type=int, default=20260623)
    parser.add_argument("--output-dir", default=str(PROJECT_ROOT / "results" / "stage3" / "bootstrap_ci"))
    parser.add_argument("--table-dir", default=str(PROJECT_ROOT / "manuscript" / "tables"))
    args = parser.parse_args()

    out_dir = Path(args.output_dir)
    table_dir = Path(args.table_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    table_dir.mkdir(parents=True, exist_ok=True)

    compact = compact_summary(
        PROJECT_ROOT / "results" / "stage3" / "compact_baselines",
        out_dir,
        table_dir,
        args.n_boot,
        args.seed,
    )
    art, quality = art_summary(
        PROJECT_ROOT / "results" / "stage3" / "art_illumina",
        PROJECT_ROOT / "results" / "stage3" / "art_quality_stratified",
        out_dir,
        table_dir,
        args.n_boot,
        args.seed,
    )
    cami = cami_summary(
        PROJECT_ROOT / "results" / "stage3" / "cami_probe_expanded",
        out_dir,
        table_dir,
        args.n_boot,
        args.seed,
    )
    write_summary(compact, art, quality, cami, out_dir / "stage3_bootstrap_ci_summary.md")
    print(f"Wrote bootstrap CI outputs to {out_dir}")


if __name__ == "__main__":
    main()

