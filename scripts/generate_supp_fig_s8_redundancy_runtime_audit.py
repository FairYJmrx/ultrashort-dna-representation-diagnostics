from __future__ import annotations

from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
REDUNDANCY_AUDIT = ROOT / "results" / "stage3" / "reviewer_response" / "property_redundancy_runtime"
CONTRIBUTION_AUDIT = ROOT / "results" / "stage3" / "reviewer_response" / "p_msp_contribution"
OUT = ROOT / "paper" / "figures"
DOCX = ROOT / "paper" / "figures_docx"


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

RUNTIME_LABELS = {
    "CK4": "CK4",
    "Hashed k=15, d=222": "Hashed k=15",
    "MinHash k=15, s=222": "MinHash k=15",
    "CK4+P": "CK4+P",
    "CK15 random projection, d=222": "RP k=15",
    "CK4P-MSP": "CK4P-MSP",
}


def save_all(fig: plt.Figure, stem: str, docx_width: int = 1800) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    DOCX.mkdir(parents=True, exist_ok=True)
    base = OUT / stem
    fig.savefig(base.with_suffix(".svg"), bbox_inches="tight")
    fig.savefig(base.with_suffix(".pdf"), bbox_inches="tight")
    fig.savefig(base.with_suffix(".png"), dpi=450, bbox_inches="tight")
    fig.savefig(base.with_suffix(".tiff"), dpi=600, bbox_inches="tight")
    im = Image.open(base.with_suffix(".png")).convert("RGB")
    scale = docx_width / im.width
    if scale < 1:
        im = im.resize((int(im.width * scale), int(im.height * scale)), Image.Resampling.LANCZOS)
    im.save(DOCX / f"{stem}.jpg", quality=92, optimize=True)
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
    runtime = pd.read_csv(REDUNDANCY_AUDIT / "feature_runtime_overall.csv")

    rep_order = ["CK4", "CK4+P", "CK4+MSP", "CK4P-MSP"]
    stability = stability.set_index("representation_label").reindex(rep_order).reset_index()
    readout = readout.set_index("representation_label").reindex(rep_order).reset_index()

    fig = plt.figure(figsize=(7.2, 5.65), constrained_layout=True)
    gs = fig.add_gridspec(2, 2, height_ratios=[1.0, 1.0], width_ratios=[1.0, 1.08])
    ax_a = fig.add_subplot(gs[0, 0])
    ax_b = fig.add_subplot(gs[1, 0])
    ax_c = fig.add_subplot(gs[0, 1])
    ax_d = fig.add_subplot(gs[1, 1])

    # Panel A: contribution to perturbation stability.
    y = np.arange(len(stability))
    ax_a.barh(y, stability["l2_delta_mean"], color=[method_color(v) for v in stability["representation_label"]], height=0.62)
    ax_a.set_yticks(y)
    ax_a.set_yticklabels(stability["representation_label"])
    ax_a.invert_yaxis()
    ax_a.set_xlabel("Mean paired L2 drift")
    ax_a.set_title("A  P and MSP both reduce perturbation drift", loc="left", fontweight="bold")
    ax_a.grid(axis="x", color=COLORS["light"], linewidth=0.6)
    annotate_bars(ax_a, stability["l2_delta_mean"], "{:.3f}", 0.006)
    ax_a.set_xlim(0, float(stability["l2_delta_mean"].max()) * 1.25)

    # Panel B: contribution to local delta-readout.
    ax_b.barh(y, readout["macro_f1_mean"], color=[method_color(v) for v in readout["representation_label"]], height=0.62)
    ax_b.set_yticks(y)
    ax_b.set_yticklabels(readout["representation_label"])
    ax_b.invert_yaxis()
    ax_b.set_xlabel("Noise-vs-local delta-readout macro-F1")
    ax_b.set_title("B  MSP carries most of the positional readout gain", loc="left", fontweight="bold")
    ax_b.grid(axis="x", color=COLORS["light"], linewidth=0.6)
    annotate_bars(ax_b, readout["macro_f1_mean"], "{:.3f}", 0.006)
    ax_b.set_xlim(0.70, 1.02)

    # Panel C: redundancy is present but incomplete.
    x = redundancy["length"].astype(int).to_numpy()
    c_lines = [
        ("First canonical |r|", redundancy["cca1_abs"], COLORS["warning"]),
        ("Mean CCA |r|", redundancy["cca_mean_abs"], COLORS["CK4+MSP"]),
        ("95th row |cosine|", redundancy["row_cosine_p95_abs"], COLORS["CK4"]),
        ("Median row |cosine|", redundancy["row_cosine_median_abs"], COLORS["CK4+P"]),
    ]
    for label, values, color in c_lines:
        ax_c.plot(x, values, color=color, marker="o", linewidth=1.15)
        ax_c.text(int(x[-1]) + 2.2, float(values.iloc[-1]), label, va="center", ha="left", fontsize=6.1, color=color)
    ax_c.set_xlabel("Read length (bp)")
    ax_c.set_ylabel("P/MSP association")
    ax_c.set_ylim(0, 1.04)
    ax_c.set_xlim(int(x.min()) - 4, int(x.max()) + 31)
    ax_c.set_title("C  P and MSP are related, not interchangeable", loc="left", fontweight="bold")
    ax_c.grid(axis="y", color=COLORS["light"], linewidth=0.6)
    rank_text = f"P rank {int(redundancy['p_rank'].median())}; MSP rank {int(redundancy['msp_rank'].median())}"
    ax_c.text(0.02, 0.08, rank_text, transform=ax_c.transAxes, fontsize=6.4, color=COLORS["dark"])

    # Panel D: runtime and dimensionality trade-off.
    order = ["CK4", "Hashed k=15, d=222", "MinHash k=15, s=222", "CK4+P", "CK15 random projection, d=222", "CK4P-MSP"]
    rt = runtime.set_index("representation_label").reindex(order).reset_index()
    rt["short_label"] = rt["representation_label"].map(RUNTIME_LABELS)
    yy = np.arange(len(rt))
    ax_d.barh(yy, rt["ms_per_10k_reads"], color=[method_color(v) for v in rt["short_label"]], height=0.58, alpha=0.92)
    ax_d.set_yticks(yy)
    ax_d.set_yticklabels(rt["short_label"])
    ax_d.invert_yaxis()
    ax_d.set_xlabel("Extraction time (ms per 10k reads)")
    ax_d.set_title("D  CK4P-MSP has a measurable extraction cost", loc="left", fontweight="bold")
    ax_d.grid(axis="x", color=COLORS["light"], linewidth=0.6)
    for yi, (_, row) in zip(yy, rt.iterrows()):
        ax_d.text(
            row["ms_per_10k_reads"] + 130,
            yi,
            f"{row['ms_per_10k_reads']:.0f} ms; {row['median_features']:.0f}D",
            va="center",
            ha="left",
            fontsize=6.0,
        )
    ax_d.set_xlim(0, float(rt["ms_per_10k_reads"].max()) * 1.34)

    for ax in (ax_a, ax_b, ax_c, ax_d):
        ax.tick_params(length=2.5, width=0.7)

    fig.suptitle(
        "Supplementary Figure S8 | P/MSP contribution, redundancy and runtime audit",
        x=0.01,
        y=1.02,
        ha="left",
        fontsize=10,
        fontweight="bold",
    )
    save_all(fig, "supp_fig_s8_redundancy_runtime_audit")


if __name__ == "__main__":
    main()
