"""Generate Supplementary Figure S15 for the CK4P-MSP-PKM extension.

The figure is deliberately a Pareto audit. It shows the positional-readability
gains together with stability, dimension, runtime and strand-sensitivity costs;
it must not be interpreted as evidence that the extension dominates CK4P-MSP.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import numpy as np
import pandas as pd

try:
    from .figure_style import METHOD_COLORS
except ImportError:
    from figure_style import METHOD_COLORS


def _find_project_root(start: Path) -> Path:
    for candidate in [start.parent, *start.parents]:
        if (candidate / "methods").is_dir() and (candidate / "configs").is_dir():
            return candidate
    raise RuntimeError("Could not locate the release repository root.")


ROOT = _find_project_root(Path(__file__).resolve())
DISCOVERY = ROOT / "results" / "stage3" / "candidate_positional_kmer_weight_sweep"
RESAMPLE = ROOT / "results" / "stage3" / "candidate_positional_kmer_weight_confirmation"
STRAND = ROOT / "results" / "stage3" / "candidate_positional_kmer_strand_audit"
UNIFIED_RUNTIME = ROOT / "results" / "stage3" / "contract_v2" / "unified_runtime_benchmark"
OUT = ROOT / "figures" / "contract_v2"

MAIN_KEY = "ck4p_msp"
VARIANT_KEY = "ck4p_msp_pkm_w025"
MAIN_LABEL = "CK4P-MSP"
VARIANT_LABEL = "CK4P-MSP-PKM"
MAIN_COLOR = METHOD_COLORS[MAIN_LABEL]
VARIANT_COLOR = METHOD_COLORS[VARIANT_LABEL]
NEUTRAL = "#A4ABB4"
GRID = "#E1E4E8"


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


def _load() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    discovery = pd.read_csv(DISCOVERY / "weight_decision_table.csv")
    resample = pd.read_csv(RESAMPLE / "weight_decision_table.csv")
    strand = pd.read_csv(STRAND / "strand_audit.csv")
    runtime = pd.read_csv(UNIFIED_RUNTIME / "unified_runtime_summary.csv")
    return discovery, resample, strand, runtime


def _pkm_path(frame: pd.DataFrame) -> pd.DataFrame:
    keep = frame[frame["route"].isin(["main", "pkm"])].copy()
    return keep.sort_values("candidate_weight")


def _annotate_weight_path(ax: plt.Axes, frame: pd.DataFrame, x: str, y: str) -> None:
    offsets = {
        0.0: (5, -11),
        0.1: (4, 5),
        0.25: (5, 5),
        0.5: (5, 4),
        0.75: (-22, 5),
        1.0: (-22, -11),
    }
    for row in frame.itertuples(index=False):
        weight = float(row.candidate_weight)
        label = "main" if weight == 0 else rf"$\delta={weight:g}$"
        dx, dy = offsets.get(weight, (4, 4))
        ax.annotate(
            label,
            (float(getattr(row, x)), float(getattr(row, y))),
            xytext=(dx, dy),
            textcoords="offset points",
            fontsize=5.8,
            color="#3D434B",
        )


def _pareto_panel(
    ax: plt.Axes,
    discovery: pd.DataFrame,
    resample: pd.DataFrame,
    *,
    x: str,
    y: str,
    title: str,
    xlabel: str,
    ylabel: str,
) -> None:
    path = _pkm_path(discovery)
    ax.plot(path[x], path[y], color=NEUTRAL, linewidth=1.1, zorder=1)
    candidates = path[path["route"].eq("pkm")]
    ax.scatter(candidates[x], candidates[y], s=28, color="#C8879E", edgecolor="white", linewidth=0.45, zorder=2)

    main = path[path["representation"].eq(MAIN_KEY)].iloc[0]
    selected = path[path["representation"].eq(VARIANT_KEY)].iloc[0]
    check = resample[resample["representation"].eq(VARIANT_KEY)].iloc[0]
    ax.scatter(main[x], main[y], marker="D", s=43, color=MAIN_COLOR, edgecolor="#20262E", linewidth=0.55, zorder=4)
    ax.scatter(selected[x], selected[y], marker="X", s=54, color=VARIANT_COLOR, edgecolor="#20262E", linewidth=0.55, zorder=5)
    ax.scatter(check[x], check[y], marker="o", s=58, facecolor="none", edgecolor=VARIANT_COLOR, linewidth=1.0, zorder=6)
    _annotate_weight_path(ax, path, x, y)
    ax.set_title(title, loc="left", fontweight="bold")
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.grid(color=GRID, linewidth=0.65, zorder=0)


def _readout_panel(ax: plt.Axes, discovery: pd.DataFrame) -> None:
    values = discovery.set_index("representation")
    metrics = [
        ("motif_macro_f1", "Motif-position"),
        ("local_macro_f1", "Local-change"),
        ("cami_mean_retention", "CAMI retention"),
    ]
    y = np.arange(len(metrics))
    for idx, (column, _) in enumerate(metrics):
        main = float(values.loc[MAIN_KEY, column])
        variant = float(values.loc[VARIANT_KEY, column])
        ax.plot([main, variant], [idx, idx], color=NEUTRAL, linewidth=1.6, zorder=1)
        ax.scatter(main, idx, marker="D", s=40, color=MAIN_COLOR, edgecolor="#20262E", linewidth=0.45, zorder=3)
        ax.scatter(variant, idx, marker="X", s=48, color=VARIANT_COLOR, edgecolor="#20262E", linewidth=0.45, zorder=4)
    ax.set_yticks(y)
    ax.set_yticklabels([label for _, label in metrics])
    ax.invert_yaxis()
    ax.set_xlim(0.58, 1.015)
    ax.set_xlabel("Macro-F1 or retention ratio")
    ax.set_title("C  Selected readout profile", loc="left", fontweight="bold")
    ax.grid(axis="x", color=GRID, linewidth=0.65, zorder=0)


def _cost_panel(
    ax: plt.Axes,
    discovery: pd.DataFrame,
    strand: pd.DataFrame,
    runtime: pd.DataFrame,
) -> None:
    values = discovery.set_index("representation")
    runtime_median = runtime.set_index("method")["median_ms_per_10000_reads"] / 1000.0
    strand_values = strand.set_index("representation")
    ratios = [
        float(values.loc[VARIANT_KEY, "n_features"]) / float(values.loc[MAIN_KEY, "n_features"]),
        float(runtime_median.loc["ck4p_msp_pkm"]) / float(runtime_median.loc["ck4p_msp"]),
        float(strand_values.loc[VARIANT_KEY, "l2_delta_mean"]) / float(strand_values.loc[MAIN_KEY, "l2_delta_mean"]),
    ]
    labels = ["Feature dimension", "Extraction time", "Reverse-complement drift"]
    y = np.arange(len(labels))
    ax.barh(y, ratios, color=VARIANT_COLOR, height=0.55)
    ax.axvline(1.0, color="#20262E", linestyle="--", linewidth=0.85)
    for idx, value in enumerate(ratios):
        ax.text(value + 0.06, idx, f"{value:.2f}x", va="center", fontsize=6.2)
    ax.set_yticks(y)
    ax.set_yticklabels(labels)
    ax.invert_yaxis()
    ax.set_xlim(0.8, 3.55)
    ax.set_xlabel(f"Ratio to {MAIN_LABEL} (1.0)")
    ax.set_title("D  Added cost and direction sensitivity", loc="left", fontweight="bold")
    ax.grid(axis="x", color=GRID, linewidth=0.65, zorder=0)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    discovery, resample, strand, runtime = _load()

    fig, axes = plt.subplots(2, 2, figsize=(7.2, 5.15))
    fig.subplots_adjust(left=0.105, right=0.98, top=0.89, bottom=0.105, wspace=0.34, hspace=0.42)
    ax_a, ax_b, ax_c, ax_d = axes.ravel()

    _pareto_panel(
        ax_a,
        discovery,
        resample,
        x="wgs_l2",
        y="motif_macro_f1",
        title="A  WGS stability-position trade-off",
        xlabel="Standardized WGS drift (lower is better)",
        ylabel="Motif-position macro-F1",
    )
    _pareto_panel(
        ax_b,
        discovery,
        resample,
        x="art_l2",
        y="local_macro_f1",
        title="B  ART stability-local readout trade-off",
        xlabel="Standardized ART drift (lower is better)",
        ylabel="Grouped local-change macro-F1",
    )
    _readout_panel(ax_c, discovery)
    _cost_panel(ax_d, discovery, strand, runtime)

    legend = [
        Line2D([0], [0], marker="D", color="none", markerfacecolor=MAIN_COLOR, markeredgecolor="#20262E", markersize=5.5, label=MAIN_LABEL),
        Line2D([0], [0], marker="X", color="none", markerfacecolor=VARIANT_COLOR, markeredgecolor="#20262E", markersize=6.0, label=VARIANT_LABEL),
        Line2D([0], [0], marker="o", color="none", markerfacecolor="none", markeredgecolor=VARIANT_COLOR, markersize=6.0, label="New-seed resampling check"),
    ]
    fig.legend(handles=legend, loc="upper center", ncol=3, bbox_to_anchor=(0.54, 0.985), columnspacing=1.5, handletextpad=0.45)

    source = discovery.copy()
    source.loc[source["representation"].eq(VARIANT_KEY), "representation_label"] = VARIANT_LABEL
    runtime_indexed = runtime.set_index("method")
    source["runtime_seconds"] = source["representation"].map(
        {
            MAIN_KEY: float(runtime_indexed.loc["ck4p_msp", "median_seconds_per_call"]),
            VARIANT_KEY: float(runtime_indexed.loc["ck4p_msp_pkm", "median_seconds_per_call"]),
        }
    )
    source["runtime_source"] = "unified long-duration full-run median"
    source["source"] = "prespecified_weight_sweep"
    resample_source = resample[resample["representation"].isin([MAIN_KEY, VARIANT_KEY])].copy()
    resample_source.loc[
        resample_source["representation"].eq(VARIANT_KEY), "representation_label"
    ] = VARIANT_LABEL
    resample_source["source"] = "new_seed_resampling_check"
    pd.concat([source, resample_source], ignore_index=True).to_csv(
        DISCOVERY / "supplementary_figure_s15_source.csv",
        index=False,
        encoding="utf-8-sig",
    )

    selected = discovery[
        discovery["representation"].isin([MAIN_KEY, VARIANT_KEY])
    ].copy()
    selected.loc[
        selected["representation"].eq(MAIN_KEY), "representation_label"
    ] = MAIN_LABEL
    selected.loc[
        selected["representation"].eq(VARIANT_KEY), "representation"
    ] = "ck4p_msp_pkm_w025"
    selected.loc[
        selected["representation"].eq("ck4p_msp_pkm_w025"),
        "representation_label",
    ] = VARIANT_LABEL
    selected["runtime_seconds"] = selected["representation"].map(
        {
            MAIN_KEY: float(runtime_indexed.loc["ck4p_msp", "median_seconds_per_call"]),
            "ck4p_msp_pkm_w025": float(
                runtime_indexed.loc["ck4p_msp_pkm", "median_seconds_per_call"]
            ),
        }
    )
    strand_indexed = strand.set_index("representation")
    selected["reverse_complement_l2"] = selected["representation"].map(
        {
            MAIN_KEY: float(strand_indexed.loc[MAIN_KEY, "l2_delta_mean"]),
            "ck4p_msp_pkm_w025": float(
                strand_indexed.loc[VARIANT_KEY, "l2_delta_mean"]
            ),
        }
    )
    selected[
        [
            "representation",
            "representation_label",
            "candidate_weight",
            "n_features",
            "wgs_l2",
            "wgs_retrieval",
            "local_macro_f1",
            "motif_macro_f1",
            "art_l2",
            "cami_mean_retention",
            "runtime_seconds",
            "reverse_complement_l2",
        ]
    ].to_csv(
        DISCOVERY / "ck4p_msp_pkm_selected_profile.csv",
        index=False,
        encoding="utf-8-sig",
    )

    stem = OUT / "supplementary_figure_s15_pkm_pareto_audit"
    fig.savefig(stem.with_suffix(".svg"), bbox_inches="tight")
    fig.savefig(stem.with_suffix(".pdf"), bbox_inches="tight")
    fig.savefig(stem.with_suffix(".png"), dpi=450, bbox_inches="tight")
    fig.savefig(stem.with_suffix(".tiff"), dpi=600, bbox_inches="tight")
    plt.close(fig)
    print(f"Wrote CK4P-MSP-PKM Pareto audit figure to {stem}")


if __name__ == "__main__":
    main()
