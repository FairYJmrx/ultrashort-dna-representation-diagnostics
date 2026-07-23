from __future__ import annotations

from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "paper" / "figures"
DOCX = ROOT / "paper" / "figures_docx"
MI_DIR = ROOT / "results" / "stage3" / "reviewer_response" / "knn_mi_robustness"
HIGH_K_DIR = ROOT / "results" / "stage3" / "reviewer_response" / "high_k_compressed_baselines"


mpl.rcParams.update(
    {
        "font.family": "sans-serif",
        "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans", "sans-serif"],
        "svg.fonttype": "none",
        "pdf.fonttype": 42,
        "font.size": 7,
        "axes.spines.right": False,
        "axes.spines.top": False,
        "axes.linewidth": 0.7,
        "axes.labelsize": 7,
        "axes.titlesize": 8,
        "xtick.labelsize": 6.5,
        "ytick.labelsize": 6.5,
        "legend.fontsize": 6.5,
        "legend.frameon": False,
    }
)

COLORS = {
    "proposed": "#2A6F97",
    "property": "#5B8E7D",
    "identity": "#7A7F87",
    "highk": "#B56576",
    "increment": "#D97706",
    "light": "#E9ECEF",
    "dark": "#212529",
}


def save_all(fig: plt.Figure, stem: str, docx_width: int = 1800) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    DOCX.mkdir(parents=True, exist_ok=True)
    base = OUT / stem
    fig.savefig(base.with_suffix(".svg"), bbox_inches="tight")
    fig.savefig(base.with_suffix(".pdf"), bbox_inches="tight")
    fig.savefig(base.with_suffix(".png"), dpi=450, bbox_inches="tight")
    fig.savefig(base.with_suffix(".tiff"), dpi=600, bbox_inches="tight")
    image = Image.open(base.with_suffix(".png")).convert("RGB")
    scale = docx_width / image.width
    if scale < 1:
        image = image.resize((int(image.width * scale), int(image.height * scale)), Image.Resampling.LANCZOS)
    image.save(DOCX / f"{stem}.jpg", quality=92, optimize=True)
    plt.close(fig)


def label_feature_set(name: str) -> str:
    labels = {
        "dK": "CK4 distance",
        "dP": "P distance",
        "dM": "MSP distance",
        "dP_dM": "P + MSP",
        "dK_dP": "CK4 + P",
        "dK_dM": "CK4 + MSP",
        "dK_dP_dM": "CK4 + P + MSP",
    }
    return labels.get(str(name), str(name))


def family_color(label: str) -> str:
    if label == "CK4P-MSP":
        return COLORS["proposed"]
    if label in {"CK4+P"}:
        return COLORS["property"]
    if label in {"CK4", "CK5"}:
        return COLORS["identity"]
    return COLORS["highk"]


def main() -> None:
    mi = pd.read_csv(MI_DIR / "knn_mi_summary.csv")
    stability = pd.read_csv(HIGH_K_DIR / "high_k_stability_summary.csv")
    readout = pd.read_csv(HIGH_K_DIR / "high_k_readout_summary.csv")

    fig = plt.figure(figsize=(7.2, 5.1), constrained_layout=True)
    gs = fig.add_gridspec(2, 2, height_ratios=[1.05, 1.0], width_ratios=[1.05, 1.0])
    ax_a = fig.add_subplot(gs[:, 0])
    ax_b = fig.add_subplot(gs[0, 1])
    ax_c = fig.add_subplot(gs[1, 1])

    # Panel A: kNN MI robustness.
    mi_order = ["dK", "dP", "dM", "dP_dM", "dK_dP", "dK_dM", "dK_dP_dM"]
    mi_plot = mi[mi["feature_set"].isin(mi_order)].copy()
    mi_plot["feature_set"] = pd.Categorical(mi_plot["feature_set"], mi_order, ordered=True)
    mi_plot = mi_plot.sort_values("feature_set")
    y = np.arange(len(mi_plot))
    xerr_low = mi_plot["mean_knn_mi_bits"] - mi_plot["mean_subsample_ci_low"]
    xerr_high = mi_plot["mean_subsample_ci_high"] - mi_plot["mean_knn_mi_bits"]
    colors = [
        COLORS["identity"] if fs == "dK" else COLORS["proposed"] if fs == "dK_dP_dM" else COLORS["property"]
        for fs in mi_plot["feature_set"].astype(str)
    ]
    ax_a.barh(y, mi_plot["mean_knn_mi_bits"], color=colors, alpha=0.88, height=0.58)
    ax_a.errorbar(
        mi_plot["mean_knn_mi_bits"],
        y,
        xerr=[xerr_low, xerr_high],
        fmt="none",
        ecolor=COLORS["dark"],
        elinewidth=0.7,
        capsize=2,
        capthick=0.7,
    )
    d_k = float(mi.loc[mi["feature_set"].eq("dK"), "mean_knn_mi_bits"].iloc[0])
    increment = float(mi.loc[mi["feature_set"].eq("increment_dP_dM_given_dK"), "mean_knn_mi_bits"].iloc[0])
    ax_a.axvline(d_k, color=COLORS["identity"], linestyle="--", linewidth=0.8)
    ax_a.text(
        d_k + 0.01,
        -0.55,
        f"CK4 baseline\n+{increment:.3f} bits for joint P/MSP",
        color=COLORS["identity"],
        fontsize=6.3,
        ha="left",
        va="top",
    )
    ax_a.set_yticks(y)
    ax_a.set_yticklabels([label_feature_set(v) for v in mi_plot["feature_set"].astype(str)])
    ax_a.invert_yaxis()
    ax_a.set_xlabel("kNN MI estimate (bits)")
    ax_a.set_title("A  kNN MI audit supports added perturbation information", loc="left", fontweight="bold")
    ax_a.set_xlim(0, max(0.98, float(mi_plot["mean_subsample_ci_high"].max()) + 0.06))
    ax_a.grid(axis="x", color=COLORS["light"], linewidth=0.6)

    # Panel B: high-k compressed baseline stability.
    stability_order = [
        "CK4P-MSP",
        "CK4+P",
        "CK4",
        "CK5",
        "CK15 random projection, d=222",
        "MinHash k=15, s=222",
        "Hashed k=15, d=222",
    ]
    stab = stability.set_index("representation_label").reindex(stability_order).dropna(subset=["l2_drift"]).reset_index()
    yb = np.arange(len(stab))
    ax_b.barh(yb, stab["l2_drift"], color=[family_color(v) for v in stab["representation_label"]], height=0.58, alpha=0.9)
    ax_b.set_yticks(yb)
    ax_b.set_yticklabels(stab["representation_label"])
    ax_b.invert_yaxis()
    ax_b.set_xlabel("Paired L2 drift")
    ax_b.set_title("B  Same-budget high-k controls drift more", loc="left", fontweight="bold")
    ax_b.grid(axis="x", color=COLORS["light"], linewidth=0.6)
    for yi, value in zip(yb, stab["l2_drift"]):
        ax_b.text(value + 0.012, yi, f"{value:.3f}", va="center", ha="left", fontsize=6.2)
    ax_b.set_xlim(0, max(stab["l2_drift"]) * 1.18)

    # Panel C: readout is not the main claim.
    read = readout[readout["classifier"].eq("logistic")].copy()
    read_order = [
        "CK4P-MSP",
        "Hashed k=15, d=222",
        "MinHash k=15, s=222",
        "CK5",
        "CK4+P",
        "CK4",
        "CK15 random projection, d=222",
    ]
    read = read.set_index("representation_label").reindex(read_order).dropna(subset=["macro_f1"]).reset_index()
    yc = np.arange(len(read))
    ax_c.barh(yc, read["macro_f1"], color=[family_color(v) for v in read["representation_label"]], height=0.58, alpha=0.9)
    ax_c.set_yticks(yc)
    ax_c.set_yticklabels(read["representation_label"])
    ax_c.invert_yaxis()
    ax_c.set_xlabel("Logistic macro-F1")
    ax_c.set_title("C  Shallow readout differences are modest", loc="left", fontweight="bold")
    ax_c.grid(axis="x", color=COLORS["light"], linewidth=0.6)
    for yi, value in zip(yc, read["macro_f1"]):
        ax_c.text(value + 0.006, yi, f"{value:.3f}", va="center", ha="left", fontsize=6.2)
    ax_c.set_xlim(0.22, max(read["macro_f1"]) * 1.12)

    fig.suptitle(
        "Supplementary Figure S7 | Methodological hardening audit",
        x=0.01,
        y=1.02,
        ha="left",
        fontsize=10,
        fontweight="bold",
    )
    save_all(fig, "supp_fig_s7_method_hardening_audit")


if __name__ == "__main__":
    main()

