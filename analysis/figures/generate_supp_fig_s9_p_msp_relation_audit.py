from __future__ import annotations

from pathlib import Path
import sys

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from PIL import Image

PROJECT_ROOT = Path(r"D:\AI-NGS\info")
sys.path.insert(0, str(PROJECT_ROOT))

from src.stage2_features import build_feature_matrix


ROOT = PROJECT_ROOT
RESULTS = ROOT / "results" / "stage3" / "reviewer_response" / "property_redundancy_runtime"
OUT = ROOT / "paper" / "figures"
DOCX = ROOT / "paper" / "figures_docx"
SAMPLE = RESULTS / "audit_clean_read_sample.csv"
CCA_DETAIL = RESULTS / "property_msp_cca_detail.csv"


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
        "xtick.labelsize": 6.2,
        "ytick.labelsize": 6.2,
        "legend.fontsize": 6.3,
        "legend.frameon": False,
    }
)

PALETTE = {
    "dark": "#212529",
    "green": "#1B9E77",
    "blue": "#2C7FB8",
}

P_LABELS = [
    "H mean",
    "H sd",
    "GC mean",
    "GC sd",
    "Pur mean",
    "Pur sd",
    "EIIP mean",
    "EIIP sd",
    "N%",
    "Length",
    "Entropy",
]

MSP_BIN_SIZES = (2, 3, 4, 6)
MSP_CHANNELS = ("H", "GC", "Pur", "EIIP", "N")


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


def safe_corr(a: np.ndarray, b: np.ndarray) -> float:
    a = np.asarray(a, dtype=np.float64)
    b = np.asarray(b, dtype=np.float64)
    if a.size < 3 or b.size < 3:
        return np.nan
    if np.nanstd(a) < 1e-12 or np.nanstd(b) < 1e-12:
        return np.nan
    corr = np.corrcoef(a, b)[0, 1]
    return float(corr) if np.isfinite(corr) else np.nan


def p_feature_heatmap(sample: pd.DataFrame) -> tuple[np.ndarray, list[str]]:
    group_labels = [f"{size}-bin" for size in MSP_BIN_SIZES]
    per_length = []
    for length, group in sample.groupby("source_length", sort=True):
        seqs = group["sequence"].astype(str).tolist()
        if not seqs:
            continue
        p, _ = build_feature_matrix(seqs, "property_l2", length=int(length), train_indices=list(range(len(seqs))))
        m, _ = build_feature_matrix(
            seqs,
            "property_multiscale_mean_l2",
            length=int(length),
            train_indices=list(range(len(seqs))),
        )

        corr_rows = np.zeros((len(P_LABELS), len(group_labels)), dtype=np.float64)
        start = 0
        for col_idx, size in enumerate(MSP_BIN_SIZES):
            block = m[:, start : start + size * len(MSP_CHANNELS)]
            for p_idx in range(len(P_LABELS)):
                vals = [safe_corr(p[:, p_idx], block[:, j]) for j in range(block.shape[1])]
                vals = [abs(v) for v in vals if np.isfinite(v)]
                corr_rows[p_idx, col_idx] = float(np.mean(vals)) if vals else 0.0
            start += size * len(MSP_CHANNELS)
        per_length.append(corr_rows)

    if not per_length:
        return np.zeros((len(P_LABELS), len(group_labels)), dtype=np.float64), group_labels

    stack = np.stack(per_length, axis=0)
    return np.mean(stack, axis=0), group_labels


def cca_heatmap() -> pd.DataFrame:
    detail = pd.read_csv(CCA_DETAIL)
    detail["length"] = detail["length"].astype(int)
    detail["component"] = detail["component"].astype(int)
    pivot = detail.pivot(index="component", columns="length", values="canonical_correlation")
    pivot = pivot.reindex(index=sorted(detail["component"].unique()), columns=sorted(detail["length"].unique()))
    return pivot


def main() -> None:
    if not SAMPLE.exists():
        raise FileNotFoundError(f"Missing audit sample: {SAMPLE}")

    sample = pd.read_csv(SAMPLE)
    sample = sample[sample["condition"].eq("clean") & sample["source_length"].isin([69, 75, 100, 150])].copy()

    cca = cca_heatmap()
    corr, corr_labels = p_feature_heatmap(sample)

    fig = plt.figure(figsize=(6.3, 6.15))
    gs = fig.add_gridspec(2, 1, height_ratios=[0.78, 1.22], hspace=0.42)
    ax_a = fig.add_subplot(gs[0, 0])
    ax_b = fig.add_subplot(gs[1, 0])
    fig.subplots_adjust(left=0.13, right=0.955, top=0.94, bottom=0.07)

    # Panel A: shared latent structure via CCA. Components CC1, CC2 and CC4
    # are near-identical, so they are shown as a narrow range rather than as
    # overlapping traces.
    xvals = np.asarray(cca.columns, dtype=float)
    high_components = cca.loc[[1, 2, 4]].to_numpy(dtype=float)
    high_min = high_components.min(axis=0)
    high_max = high_components.max(axis=0)
    high_mid = high_components.mean(axis=0)
    ax_a.fill_between(xvals, high_min, high_max, color="#80CDC1", alpha=0.22, linewidth=0)
    ax_a.plot(xvals, high_mid, marker="o", markersize=3.2, linewidth=1.25, color="#018571", label="CC1/2/4 range")
    ax_a.plot(
        xvals,
        cca.loc[3].to_numpy(dtype=float),
        marker="o",
        markersize=3.2,
        linewidth=1.25,
        color="#2B8CBE",
        label="CC3",
    )
    ax_a.plot(
        xvals,
        cca.loc[5].to_numpy(dtype=float),
        marker="o",
        markersize=3.2,
        linewidth=1.25,
        color="#A6BDDB",
        label="CC5",
    )
    ax_a.set_xlim(xvals.min() - 4, xvals.max() + 10)
    ax_a.set_ylim(0.18, 1.045)
    ax_a.set_xticks(xvals)
    ax_a.set_xticklabels([f"{int(c)} bp" for c in xvals])
    ax_a.set_ylabel("Canonical correlation")
    ax_a.set_title("A  CCA reveals shared latent structure", loc="left", fontweight="bold")
    ax_a.grid(axis="y", color="#DEE2E6", linewidth=0.65)
    ax_a.legend(loc="center right", handlelength=1.5)
    ax_a.text(
        0.01,
        -0.23,
        "Early components stay near unity across all lengths; later components separate more.",
        transform=ax_a.transAxes,
        fontsize=5.9,
        color=PALETTE["dark"],
        va="top",
    )

    # Panel B: coarse P-vs-MSP redundancy heatmap.
    im_b = ax_b.imshow(corr, aspect="auto", cmap="YlGnBu", vmin=0.0, vmax=1.0, interpolation="nearest")
    ax_b.set_xticks(np.arange(len(corr_labels)))
    ax_b.set_xticklabels(corr_labels)
    ax_b.set_yticks(np.arange(len(P_LABELS)))
    ax_b.set_yticklabels(P_LABELS)
    ax_b.set_xlabel("MSP bin size")
    ax_b.set_ylabel("P feature")
    ax_b.set_title("B  P and MSP are related but not identical", loc="left", fontweight="bold")
    ax_b.tick_params(length=0)
    for i in range(corr.shape[0]):
        for j in range(corr.shape[1]):
            value = float(corr[i, j])
            color = "white" if value >= 0.65 else PALETTE["dark"]
            ax_b.text(j, i, f"{value:.2f}", ha="center", va="center", fontsize=5.9, color=color)
    for sep in np.arange(1.5, len(P_LABELS), 2.0):
        ax_b.hlines(sep, -0.5, len(corr_labels) - 0.5, colors="white", linewidth=0.85)
    cbar_b = fig.colorbar(im_b, ax=ax_b, fraction=0.035, pad=0.02)
    cbar_b.ax.tick_params(labelsize=6)
    cbar_b.set_label("Mean |Pearson r|", fontsize=6.5)
    ax_b.text(
        0.01,
        -0.16,
        "Averaged over clean 69, 75, 100 and 150 bp audit samples; values support related-but-not-interchangeable wording.",
        transform=ax_b.transAxes,
        fontsize=5.9,
        color=PALETTE["dark"],
        va="top",
    )

    save_all(fig, "supp_fig_s9_p_msp_relation_audit")


if __name__ == "__main__":
    main()

