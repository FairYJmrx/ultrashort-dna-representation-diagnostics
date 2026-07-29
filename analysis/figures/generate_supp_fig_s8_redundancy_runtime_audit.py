from __future__ import annotations

from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def _find_project_root(start: Path) -> Path:
    for candidate in [start.parent, *start.parents]:
        if (candidate / "methods").is_dir() and (candidate / "configs").is_dir():
            return candidate
    raise RuntimeError("Could not locate the release repository root.")


ROOT = _find_project_root(Path(__file__).resolve())
REDUNDANCY_AUDIT = ROOT / "results" / "stage3" / "contract_v2" / "property_redundancy_runtime"
CONTRIBUTION_AUDIT = ROOT / "results" / "stage3" / "contract_v2" / "p_msp_contribution"
OUT = ROOT / "figures" / "contract_v2"


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
        "xtick.labelsize": 6.5,
        "ytick.labelsize": 6.5,
        "legend.fontsize": 6.4,
        "legend.frameon": False,
    }
)

COLORS = {
    "CK4": "#6C757D",
    "CK4+P": "#4D908E",
    "CK4+MSP": "#577590",
    "CK4P-MSP": "#1B9E77",
    "highk": "#B56576",
    "warning": "#D97706",
    "light": "#E9ECEF",
    "dark": "#212529",
}

def save_all(fig: plt.Figure, stem: str) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    base = OUT / stem
    fig.savefig(base.with_suffix(".svg"), bbox_inches="tight")
    fig.savefig(base.with_suffix(".pdf"), bbox_inches="tight")
    fig.savefig(base.with_suffix(".png"), dpi=450, bbox_inches="tight")
    fig.savefig(base.with_suffix(".tiff"), dpi=600, bbox_inches="tight")
    plt.close(fig)


def method_color(label: str) -> str:
    return COLORS.get(label, COLORS["highk"])


def annotate_bars(ax: plt.Axes, values: pd.Series, fmt: str, pad: float) -> None:
    for idx, value in enumerate(values):
        ax.text(float(value) + pad, idx, fmt.format(float(value)), va="center", ha="left", fontsize=6.2)


def main() -> None:
    stability = pd.read_csv(CONTRIBUTION_AUDIT / "p_msp_contribution_stability_summary.csv")
    readout = pd.read_csv(CONTRIBUTION_AUDIT / "p_msp_contribution_delta_readout_summary.csv")
    redundancy = pd.read_csv(REDUNDANCY_AUDIT / "property_msp_redundancy_summary.csv")

    rep_order = ["CK4", "CK4+P", "CK4+MSP", "CK4P-MSP"]
    stability = stability.set_index("representation_label").reindex(rep_order).reset_index()
    readout = readout.set_index("representation_label").reindex(rep_order).reset_index()

    fig, (ax_a, ax_b, ax_c) = plt.subplots(1, 3, figsize=(7.2, 4.8))
    fig.subplots_adjust(left=0.09, right=0.98, top=0.90, bottom=0.14, wspace=0.55)

    # Panel A: contribution to perturbation stability.
    y = np.arange(len(stability))
    ax_a.barh(y, stability["l2_delta_mean"], color=[method_color(v) for v in stability["representation_label"]], height=0.62)
    ax_a.set_yticks(y)
    ax_a.set_yticklabels(stability["representation_label"])
    ax_a.invert_yaxis()
    ax_a.set_xlabel("Mean paired L2 drift")
    ax_a.set_title("A  Both property blocks reduce drift", loc="left", fontweight="bold")
    ax_a.grid(axis="x", color=COLORS["light"], linewidth=0.6)
    annotate_bars(ax_a, stability["l2_delta_mean"], "{:.3f}", 0.006)
    ax_a.set_xlim(0, float(stability["l2_delta_mean"].max()) * 1.25)

    # Panel B: contribution to local delta-readout.
    ax_b.barh(y, readout["macro_f1_mean"], color=[method_color(v) for v in readout["representation_label"]], height=0.62)
    ax_b.set_yticks(y)
    ax_b.set_yticklabels(readout["representation_label"])
    ax_b.invert_yaxis()
    ax_b.set_xlabel("Noise-vs-local delta-readout macro-F1")
    ax_b.set_title("B  MSP drives local-change readout", loc="left", fontweight="bold")
    ax_b.grid(axis="x", color=COLORS["light"], linewidth=0.6)
    annotate_bars(ax_b, readout["macro_f1_mean"], "{:.3f}", 0.006)
    ax_b.set_xlim(0.70, 1.02)

    # Panel C: redundancy is present but incomplete.
    x = redundancy["length"].astype(int).to_numpy()
    c_lines = [
        ("CCA1 |r|", redundancy["cca1_abs"], COLORS["warning"]),
        ("Mean CCA |r|", redundancy["cca_mean_abs"], COLORS["CK4+MSP"]),
        ("Row |cosine|, 95th", redundancy["row_cosine_p95_abs"], COLORS["CK4"]),
        ("Row |cosine|, median", redundancy["row_cosine_median_abs"], COLORS["CK4+P"]),
    ]
    for label, values, color in c_lines:
        ax_c.plot(x, values, color=color, marker="o", linewidth=1.15, label=label)
    ax_c.set_xlabel("Read length (bp)")
    ax_c.set_ylabel("P/MSP association")
    ax_c.set_ylim(0, 1.04)
    ax_c.set_xlim(int(x.min()) - 4, int(x.max()) + 8)
    ax_c.set_title("C  Related, not interchangeable", loc="left", fontweight="bold")
    ax_c.grid(axis="y", color=COLORS["light"], linewidth=0.6)
    ax_c.legend(
        loc="center right",
        bbox_to_anchor=(1.0, 0.59),
        ncol=2,
        fontsize=5.4,
        handlelength=1.2,
        columnspacing=0.7,
        labelspacing=0.2,
    )
    rank_text = f"P rank {int(redundancy['p_rank'].median())}; MSP rank {int(redundancy['msp_rank'].median())}"
    ax_c.text(0.02, 0.08, rank_text, transform=ax_c.transAxes, fontsize=6.4, color=COLORS["dark"])

    for ax in (ax_a, ax_b, ax_c):
        ax.tick_params(length=2.5, width=0.7)

    fig.suptitle(
        "Supplementary Figure S8 | P/MSP contribution and relation audit",
        x=0.01,
        y=1.02,
        ha="left",
        fontsize=10,
        fontweight="bold",
    )
    save_all(fig, "supp_fig_s8_redundancy_runtime_audit")


if __name__ == "__main__":
    main()

