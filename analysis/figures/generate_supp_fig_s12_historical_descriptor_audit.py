"""Generate the historical handcrafted descriptor audit figure.

Core conclusion: CK4P-MSP does not minimize every metric; it provides the
strongest grouped local-change readability while retaining low paired drift and
explicit K/P/MSP attribution relative to representative historical encoders.
"""

from __future__ import annotations

from pathlib import Path
import sys

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import wilcoxon


def _find_project_root(start: Path) -> Path:
    for candidate in [start.parent, *start.parents]:
        if (candidate / "methods").is_dir() and (candidate / "configs").is_dir():
            return candidate
    raise RuntimeError("Could not locate the release repository root.")


ROOT = _find_project_root(Path(__file__).resolve())
RESULTS = ROOT / "results" / "stage3" / "contract_v2" / "historical_descriptor_audit"
OUT = ROOT / "figures" / "contract_v2"

ORDER = ["ck4", "ck4p_msp", "pseknc_k3_l3", "ncp_anf", "pseeiip"]
LABELS = {
    "ck4": "CK4",
    "ck4p_msp": "CK4P-MSP",
    "pseknc_k3_l3": "PseKNC",
    "ncp_anf": "NCP+ANF",
    "pseeiip": "PseEIIP",
}
COLORS = {
    "ck4": "#6C757D",
    "ck4p_msp": "#16865C",
    "pseknc_k3_l3": "#3977A8",
    "ncp_anf": "#C97A91",
    "pseeiip": "#D78B35",
}

mpl.rcParams.update(
    {
        "font.family": "sans-serif",
        "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans", "sans-serif"],
        "svg.fonttype": "none",
        "pdf.fonttype": 42,
        "font.size": 7,
        "axes.spines.right": False,
        "axes.spines.top": False,
        "axes.linewidth": 0.75,
        "axes.labelsize": 7,
        "axes.titlesize": 8,
        "xtick.labelsize": 6.3,
        "ytick.labelsize": 6.3,
        "legend.frameon": False,
    }
)


def bootstrap_mean_ci(values: np.ndarray, seed: int, n_bootstrap: int = 10000) -> tuple[float, float, float]:
    values = np.asarray(values, dtype=np.float64)
    rng = np.random.default_rng(seed)
    draws = rng.choice(values, size=(n_bootstrap, len(values)), replace=True).mean(axis=1)
    return float(values.mean()), float(np.quantile(draws, 0.025)), float(np.quantile(draws, 0.975))


def bh_adjust(p_values: list[float]) -> np.ndarray:
    p = np.asarray(p_values, dtype=np.float64)
    order = np.argsort(p)
    ranked = p[order]
    adjusted = np.minimum.accumulate((ranked * len(p) / np.arange(1, len(p) + 1))[::-1])[::-1]
    out = np.empty_like(adjusted)
    out[order] = np.minimum(adjusted, 1.0)
    return out


def summarize_metric(frame: pd.DataFrame, metric: str, seed: int) -> pd.DataFrame:
    rows = []
    for idx, representation in enumerate(ORDER):
        values = frame.loc[frame["representation"].eq(representation), metric].astype(float).to_numpy()
        mean, low, high = bootstrap_mean_ci(values, seed=seed + idx)
        rows.append(
            {
                "representation": representation,
                "representation_label": LABELS[representation],
                "metric": metric,
                "mean": mean,
                "ci_low": low,
                "ci_high": high,
                "n_cells": len(values),
            }
        )
    return pd.DataFrame(rows)


def paired_contrasts(stability: pd.DataFrame, local: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    designs = [
        (stability, ["length", "condition"], "l2_delta_mean", "stability_drift", -1.0),
        (local, ["length", "local_mode"], "macro_f1", "grouped_local_change_f1", 1.0),
    ]
    for frame, keys, metric, endpoint, direction in designs:
        main = frame[frame["representation"].eq("ck4p_msp")][keys + [metric]].rename(columns={metric: "main"})
        for comparator in [item for item in ORDER if item != "ck4p_msp"]:
            other = frame[frame["representation"].eq(comparator)][keys + [metric]].rename(columns={metric: "other"})
            paired = main.merge(other, on=keys, how="inner")
            improvement = direction * (paired["main"].to_numpy(float) - paired["other"].to_numpy(float))
            mean, low, high = bootstrap_mean_ci(improvement, seed=20260729 + len(rows))
            try:
                p_value = float(wilcoxon(improvement, alternative="two-sided").pvalue)
            except ValueError:
                p_value = 1.0
            rows.append(
                {
                    "endpoint": endpoint,
                    "comparator": comparator,
                    "comparator_label": LABELS[comparator],
                    "n_cells": len(improvement),
                    "ck4p_msp_improvement": mean,
                    "ci_low": low,
                    "ci_high": high,
                    "wilcoxon_p": p_value,
                }
            )
    q_values = bh_adjust([float(row["wilcoxon_p"]) for row in rows])
    for row, q_value in zip(rows, q_values):
        row["bh_q"] = float(q_value)
    return pd.DataFrame(rows)


def point_interval_panel(
    ax: plt.Axes,
    summary: pd.DataFrame,
    *,
    title: str,
    xlabel: str,
    xlim: tuple[float, float] | None = None,
) -> None:
    y = np.arange(len(ORDER))
    summary = summary.set_index("representation").loc[ORDER]
    means = summary["mean"].to_numpy(float)
    low = summary["ci_low"].to_numpy(float)
    high = summary["ci_high"].to_numpy(float)
    for idx, representation in enumerate(ORDER):
        ax.errorbar(
            means[idx],
            y[idx],
            xerr=[[means[idx] - low[idx]], [high[idx] - means[idx]]],
            fmt="o",
            markersize=5.0 if representation == "ck4p_msp" else 4.2,
            color=COLORS[representation],
            ecolor=COLORS[representation],
            elinewidth=1.2,
            capsize=2.2,
            zorder=3,
        )
    ax.set_yticks(y)
    ax.set_yticklabels([LABELS[item] for item in ORDER])
    ax.invert_yaxis()
    ax.set_xlabel(xlabel)
    ax.set_title(title, loc="left", fontweight="bold")
    ax.grid(axis="x", color="#E1E5E8", linewidth=0.65, zorder=0)
    if xlim is not None:
        ax.set_xlim(*xlim)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    stability = pd.read_csv(RESULTS / "historical_descriptor_stability.csv")
    local = pd.read_csv(RESULTS / "historical_descriptor_local_readout.csv")
    local = local[
        local["split"].astype(str).str.contains("grouped_cv")
        & local["classifier"].eq("logistic")
    ].copy()
    runtime = pd.read_csv(RESULTS / "historical_descriptor_runtime.csv")

    stability_summary = summarize_metric(stability, "l2_delta_mean", seed=20260729)
    local_summary = summarize_metric(local, "macro_f1", seed=20260829)
    contrasts = paired_contrasts(stability, local)
    contrasts.to_csv(RESULTS / "historical_descriptor_paired_contrasts.csv", index=False, encoding="utf-8-sig")

    dimensions = (
        stability[stability["length"].eq(75)]
        .groupby("representation", as_index=False)
        .agg(n_features=("n_features", "first"))
        .set_index("representation")
        .loc[ORDER]
    )
    runtime_summary = (
        runtime.groupby("representation", as_index=False)
        .agg(
            runtime_ms=("milliseconds_per_10000_reads", "median"),
            runtime_q25=("milliseconds_per_10000_reads", lambda values: float(np.quantile(values, 0.25))),
            runtime_q75=("milliseconds_per_10000_reads", lambda values: float(np.quantile(values, 0.75))),
        )
        .set_index("representation")
        .loc[ORDER]
    )

    source_rows = []
    for _, row in stability.iterrows():
        source_rows.append(
            {
                "panel": "A",
                "representation": row["representation"],
                "cell_1": int(row["length"]),
                "cell_2": row["condition"],
                "value": float(row["l2_delta_mean"]),
                "metric": "standardized_drift",
            }
        )
    for _, row in local.iterrows():
        source_rows.append(
            {
                "panel": "B",
                "representation": row["representation"],
                "cell_1": int(row["length"]),
                "cell_2": row["local_mode"],
                "value": float(row["macro_f1"]),
                "metric": "grouped_local_change_macro_f1",
            }
        )
    for representation, row in dimensions.iterrows():
        source_rows.append(
            {
                "panel": "C",
                "representation": representation,
                "cell_1": 75,
                "cell_2": "dimension",
                "value": int(row["n_features"]),
                "metric": "feature_dimension",
            }
        )
    for representation, row in runtime.iterrows():
        source_rows.append(
            {
                "panel": "D",
                "representation": row["representation"],
                "cell_1": int(row["repeat"]),
                "cell_2": "75_bp_1000_reads_scaled_to_10000",
                "value": float(row["milliseconds_per_10000_reads"]) / 1000.0,
                "metric": "reference_runtime_seconds",
            }
        )
    pd.DataFrame(source_rows).to_csv(
        RESULTS / "historical_descriptor_figure_source.csv", index=False, encoding="utf-8-sig"
    )

    fig, axes = plt.subplots(2, 2, figsize=(7.2, 5.55))
    fig.subplots_adjust(left=0.14, right=0.97, top=0.95, bottom=0.10, wspace=0.48, hspace=0.48)
    ax_a, ax_b, ax_c, ax_d = axes.ravel()

    point_interval_panel(
        ax_a,
        stability_summary,
        title="A  Paired perturbation stability",
        xlabel="Standardized drift (lower is better)",
        xlim=(0.08, 0.25),
    )
    point_interval_panel(
        ax_b,
        local_summary,
        title="B  Structured local-change readability",
        xlabel="Grouped macro-F1 (higher is better)",
        xlim=(0.83, 1.00),
    )

    y = np.arange(len(ORDER))
    ax_c.barh(
        y,
        dimensions["n_features"].to_numpy(float),
        color=[COLORS[item] for item in ORDER],
        height=0.62,
    )
    ax_c.set_yticks(y)
    ax_c.set_yticklabels([LABELS[item] for item in ORDER])
    ax_c.invert_yaxis()
    ax_c.set_xlim(0, 325)
    ax_c.set_xlabel("Feature dimension at 75 bp")
    ax_c.set_title("C  Representation size", loc="left", fontweight="bold")
    ax_c.grid(axis="x", color="#E1E5E8", linewidth=0.65, zorder=0)
    for idx, value in enumerate(dimensions["n_features"].to_numpy(int)):
        ax_c.text(value + 6, idx, str(value), va="center", fontsize=6.2)

    runtime_seconds = runtime_summary["runtime_ms"].to_numpy(float) / 1000.0
    runtime_low = runtime_summary["runtime_q25"].to_numpy(float) / 1000.0
    runtime_high = runtime_summary["runtime_q75"].to_numpy(float) / 1000.0
    for idx, representation in enumerate(ORDER):
        ax_d.errorbar(
            runtime_seconds[idx],
            idx,
            xerr=[[runtime_seconds[idx] - runtime_low[idx]], [runtime_high[idx] - runtime_seconds[idx]]],
            fmt="o",
            markersize=5.0 if representation == "ck4p_msp" else 4.2,
            color=COLORS[representation],
            ecolor=COLORS[representation],
            elinewidth=1.2,
            capsize=2.2,
            zorder=3,
        )
    ax_d.set_xscale("log")
    ax_d.set_xlim(0.6, 85)
    ax_d.set_yticks(y)
    ax_d.set_yticklabels([LABELS[item] for item in ORDER])
    ax_d.invert_yaxis()
    ax_d.set_xlabel("Seconds per 10,000 reads (log scale)")
    ax_d.set_title("D  Optimized reference implementation", loc="left", fontweight="bold")
    ax_d.grid(axis="x", which="both", color="#E1E5E8", linewidth=0.65, zorder=0)
    for idx, value in enumerate(runtime_seconds):
        ax_d.text(value * 1.12, idx, f"{value:.1f}", va="center", fontsize=6.2)

    stem = OUT / "supplementary_figure_s12_historical_descriptor_audit"
    fig.savefig(stem.with_suffix(".svg"), bbox_inches="tight")
    fig.savefig(stem.with_suffix(".pdf"), bbox_inches="tight")
    fig.savefig(stem.with_suffix(".png"), dpi=450, bbox_inches="tight")
    fig.savefig(stem.with_suffix(".tiff"), dpi=600, bbox_inches="tight")
    plt.close(fig)
    print(f"Wrote historical descriptor figure to {stem}")


if __name__ == "__main__":
    main()
