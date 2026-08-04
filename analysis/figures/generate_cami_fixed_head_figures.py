"""Generate manuscript figures for the CAMI frozen-head transfer audits."""

from __future__ import annotations

import os
import shutil
from pathlib import Path

os.environ.setdefault("MPLBACKEND", "Agg")

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.lines import Line2D

try:
    from .figure_style import METHOD_COLORS, METHOD_MARKERS, SUPPORT_COLORS
except ImportError:
    from figure_style import METHOD_COLORS, METHOD_MARKERS, SUPPORT_COLORS


PROJECT_ROOT = Path(__file__).resolve().parents[2]
INFO_ROOT = PROJECT_ROOT.parent
RESULT_ROOT = PROJECT_ROOT / "results" / "stage3" / "contract_v2"
OUTPUT_ROOT = PROJECT_ROOT / "figures" / "contract_v2"
LATEX_MAIN = INFO_ROOT / "paper_latex" / "figures" / "main"
LATEX_SUPP = INFO_ROOT / "paper_latex" / "figures" / "supplementary"

COLORS = METHOD_COLORS


def configure() -> None:
    mpl.rcParams.update(
        {
            "font.family": "sans-serif",
            "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans", "sans-serif"],
            "svg.fonttype": "none",
            "pdf.fonttype": 42,
            "font.size": 7.2,
            "axes.titlesize": 8.3,
            "axes.labelsize": 7.2,
            "xtick.labelsize": 6.6,
            "ytick.labelsize": 6.6,
            "legend.fontsize": 6.2,
            "axes.spines.right": False,
            "axes.spines.top": False,
            "axes.linewidth": 0.7,
            "figure.facecolor": "white",
        }
    )


def save_and_sync(fig: plt.Figure, stem: str, latex_dir: Path, latex_stem: str) -> None:
    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    latex_dir.mkdir(parents=True, exist_ok=True)
    for suffix in ("pdf", "svg", "png"):
        output = OUTPUT_ROOT / f"{stem}.{suffix}"
        if suffix == "png":
            fig.savefig(output, dpi=600, bbox_inches="tight")
        else:
            fig.savefig(output, bbox_inches="tight")
        shutil.copy2(output, latex_dir / f"{latex_stem}.{suffix}")
    plt.close(fig)


def main_figure() -> plt.Figure:
    art = pd.read_csv(RESULT_ROOT / "art_current_contract" / "art_stability_metrics.csv")
    target = pd.read_csv(
        RESULT_ROOT / "cami_multitarget_fixed_head" / "cami_multitarget_target_summary.csv"
    )
    art_names = {
        "ck4": "CK4",
        "ck4_p": "CK4+P",
        "ck4_msp": "CK4+MSP",
        "ck4p_msp": "CK4P-MSP",
        "ckmer5_count_l2": "CK5",
    }
    art = art[art["representation"].isin(art_names)].copy()
    baseline = art[art["representation"].eq("ck4")].set_index("length")["l2_delta_mean"]
    art["drift_ratio"] = [value / baseline.loc[length] for value, length in zip(art["l2_delta_mean"], art["length"])]
    art["label"] = art["representation"].map(art_names)

    display = ["PseKNC", "PseEIIP", "CK4", "CK4+P", "CK4+MSP", "CK4P-MSP", "CK5"]
    target = target[target["representation_label"].isin(display)].copy()
    target["representation_label"] = pd.Categorical(
        target["representation_label"], categories=display, ordered=True
    )

    fig, axes = plt.subplots(
        1,
        3,
        figsize=(7.45, 3.45),
        gridspec_kw={"width_ratios": [1.05, 1.12, 1.12]},
    )
    for label in ["CK5", "CK4", "CK4+P", "CK4+MSP", "CK4P-MSP"]:
        frame = art[art["label"].eq(label)].sort_values("length")
        axes[0].plot(
            frame["length"],
            frame["drift_ratio"],
            color=COLORS[label],
            marker=METHOD_MARKERS[label],
            markersize=3.6 if label == "CK4P-MSP" else 3.1,
            linewidth=1.8 if label == "CK4P-MSP" else 1.05,
            linestyle="--" if label == "CK4" else "-",
            label=label,
            zorder=4 if label == "CK4P-MSP" else 2,
        )
    axes[0].axhline(1.0, color=SUPPORT_COLORS["neutral_mid"], linestyle="--", linewidth=0.7)
    axes[0].set_xticks([50, 75, 100, 125, 150])
    axes[0].set_ylim(0.5, 1.55)
    axes[0].set_xlabel("read length (bp)")
    axes[0].set_ylabel("drift relative to CK4 (lower is better)")
    axes[0].set_title("A. ART stability", loc="left", weight="bold")
    axes[0].grid(True, color=SUPPORT_COLORS["grid"], linewidth=0.5)
    axes[0].legend(frameon=False, loc="upper left", ncol=2, columnspacing=0.8, handletextpad=0.3)

    def target_panel(ax: plt.Axes, value: str, xlabel: str, title: str, xlim: tuple[float, float]) -> None:
        for target_label, frame in target.groupby("target_label", observed=True):
            frame = frame.sort_values("representation_label")
            ax.plot(
                frame[value],
                np.arange(len(frame)),
                color=SUPPORT_COLORS["neutral_line"],
                linewidth=0.60,
                alpha=0.70,
                zorder=1,
            )
        for y_index, label in enumerate(display):
            values = target[target["representation_label"].astype(str).eq(label)][value].to_numpy(dtype=float)
            ax.scatter(
                values,
                np.full(len(values), y_index),
                s=16,
                facecolor=SUPPORT_COLORS["neutral_point"],
                edgecolor="white",
                linewidth=0.30,
                alpha=0.72,
                zorder=2,
            )
            ax.scatter(
                np.mean(values),
                y_index,
                marker="D",
                s=48 if label == "CK4P-MSP" else 34,
                facecolor=COLORS[label],
                edgecolor=SUPPORT_COLORS["ink"],
                linewidth=1.0 if label == "CK4P-MSP" else 0.65,
                zorder=4,
            )
        ax.set_yticks(np.arange(len(display)))
        ax.set_yticklabels(display)
        ax.set_xlim(*xlim)
        ax.set_xlabel(xlabel)
        ax.set_title(title, loc="left", weight="bold")
        ax.axhline(1.5, color=SUPPORT_COLORS["neutral_line"], linewidth=0.75, zorder=0)
        ax.grid(axis="x", color=SUPPORT_COLORS["grid"], linewidth=0.5)

    target_panel(
        axes[1],
        "mean_shifted_macro_f1",
        "fixed-head macro-F1 (higher is better)",
        "B. Fixed-head label readout",
        (0.64, 0.91),
    )
    target_panel(
        axes[2],
        "mean_retention",
        "F1 retention / 100-bp clean (higher is better)",
        "C. Relative F1 retention",
        (0.91, 1.005),
    )
    task_handles = [
        Line2D(
            [0],
            [0],
            color="none",
            marker="o",
            markerfacecolor=SUPPORT_COLORS["neutral_point"],
            markeredgecolor="white",
            linewidth=0,
            markersize=4.2,
            label="target task (n=6)",
        ),
        Line2D(
            [0],
            [0],
            color="none",
            marker="D",
            markerfacecolor="white",
            markeredgecolor=SUPPORT_COLORS["ink"],
            linewidth=0,
            markersize=5.0,
            label="cross-target mean (method colour)",
        ),
        Line2D(
            [0],
            [0],
            color=SUPPORT_COLORS["neutral_line"],
            linewidth=0.9,
            label="same target across methods",
        ),
    ]
    fig.legend(
        handles=task_handles,
        frameon=False,
        loc="upper center",
        bbox_to_anchor=(0.72, 0.88),
        ncol=3,
        columnspacing=1.0,
        handletextpad=0.45,
        fontsize=6.1,
    )
    fig.suptitle(
        "External probes separate representation stability from fixed-head label retention",
        y=0.995,
        fontsize=9.3,
        weight="bold",
    )
    fig.tight_layout(rect=(0, 0.01, 1, 0.83), w_pad=1.8)
    return fig


def supplementary_figure() -> plt.Figure:
    single_metrics = pd.read_csv(
        RESULT_ROOT / "cami_fixed_head_transfer" / "cami_fixed_head_metrics.csv"
    )
    coordinates = pd.read_csv(
        RESULT_ROOT / "cami_fixed_head_transfer" / "cami_fixed_head_p_coordinate_audit.csv"
    )
    sensitivity = pd.read_csv(
        RESULT_ROOT.parent / "contract_v2" / "cami_multitarget_c_sensitivity" / "cami_multitarget_c_sensitivity.csv"
    )
    fig, axes = plt.subplots(
        1,
        3,
        figsize=(7.45, 3.45),
        gridspec_kw={"width_ratios": [1.18, 1.0, 1.05]},
    )

    frame = single_metrics[single_metrics["representation"].eq("ck4p_msp")].copy()
    condition_order = ["clean", "N_3pct", "substitution_1pct"]
    frame["condition"] = pd.Categorical(frame["condition"], categories=condition_order, ordered=True)
    frame = frame.sort_values(["length", "condition"])
    frame["cell"] = frame["length"].astype(str) + "\n" + frame["condition"].astype(str).replace(
        {"N_3pct": "N-mask", "substitution_1pct": "substitution"}
    )
    for scaling, color, label in [
        ("contract", "#16a34a", "contract space"),
        ("train_zscore", "#dc2626", "train z-score"),
    ]:
        local = frame[frame["probe_scaling"].eq(scaling)]
        axes[0].plot(
            np.arange(len(local)),
            local["macro_f1"],
            color=color,
            marker="o",
            linewidth=1.35,
            markersize=3.5,
            label=label,
        )
    axes[0].set_xticks(np.arange(len(local)))
    axes[0].set_xticklabels(local["cell"], rotation=45, ha="right")
    axes[0].set_ylim(0.5, 0.94)
    axes[0].set_ylabel("fixed-head macro-F1")
    axes[0].set_title("A. Preprocessing boundary", loc="left", weight="bold")
    axes[0].grid(axis="y", color="#e5e7eb", linewidth=0.5)
    axes[0].legend(frameon=False, loc="lower right")

    coord = coordinates[
        coordinates["representation"].eq("ck4p_msp")
        & coordinates["length"].eq(100)
        & coordinates["condition"].eq("N_3pct")
    ]
    coord = (
        coord.groupby(["probe_scaling", "coordinate"], as_index=False)["mean_abs_logit_shift"]
        .mean()
        .pivot(index="coordinate", columns="probe_scaling", values="mean_abs_logit_shift")
        .fillna(0)
    )
    coord = coord.sort_values("train_zscore", ascending=False).head(7).sort_values("train_zscore")
    y = np.arange(len(coord))
    axes[1].barh(y - 0.16, coord["contract"], height=0.3, color="#16a34a", label="contract space")
    axes[1].barh(y + 0.16, coord["train_zscore"], height=0.3, color="#dc2626", label="train z-score")
    axes[1].set_yticks(y)
    axes[1].set_yticklabels(coord.index)
    axes[1].set_xscale("log")
    axes[1].set_xlim(1e-4, 2.0)
    axes[1].set_xlabel("mean absolute logit shift")
    axes[1].set_title("B. N-mask coordinate effect", loc="left", weight="bold")
    axes[1].grid(axis="x", color="#e5e7eb", linewidth=0.5)
    axes[1].legend(
        frameon=False,
        loc="upper center",
        bbox_to_anchor=(0.5, -0.24),
        ncol=2,
        columnspacing=0.7,
        handletextpad=0.35,
        fontsize=5.8,
    )

    selected = ["CK4", "CK4P-MSP", "CK5", "PseKNC", "PseEIIP"]
    sensitivity = sensitivity[sensitivity["representation_label"].isin(selected)]
    for label in selected:
        local = sensitivity[sensitivity["representation_label"].eq(label)].sort_values("c_value")
        axes[2].plot(
            local["c_value"],
            local["mean_shifted_macro_f1"],
            color=COLORS[label],
            marker="o",
            markersize=3.5,
            linewidth=1.8 if label == "CK4P-MSP" else 1.0,
            label=label,
        )
    axes[2].set_xscale("log")
    axes[2].set_xticks([0.1, 1, 10], labels=["0.1", "1", "10"])
    axes[2].set_ylim(0.74, 0.81)
    axes[2].set_xlabel("logistic regularization C")
    axes[2].set_ylabel("mean shifted macro-F1")
    axes[2].set_title("C. Regularization sensitivity", loc="left", weight="bold")
    axes[2].grid(True, color="#e5e7eb", linewidth=0.5)
    axes[2].legend(frameon=False, loc="lower center", ncol=2, columnspacing=0.7, handletextpad=0.3)

    fig.suptitle(
        "Frozen-head audits distinguish representation geometry from learned preprocessing",
        y=1.02,
        fontsize=9.2,
        weight="bold",
    )
    fig.tight_layout(rect=(0, 0, 1, 0.97), w_pad=1.7)
    return fig


def main() -> None:
    configure()
    save_and_sync(
        main_figure(),
        "figure_4_external_fixed_head",
        LATEX_MAIN,
        "nature_fig4_external_probes",
    )
    save_and_sync(
        supplementary_figure(),
        "supplementary_figure_s14_fixed_head_sensitivity",
        LATEX_SUPP,
        "supp_fig_s14_fixed_head_sensitivity",
    )
    print(f"Wrote fixed-head figures to {OUTPUT_ROOT}")


if __name__ == "__main__":
    main()
