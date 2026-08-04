"""Generate ART and 50--75 bp continuity figures for the current contract."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
RESULTS = ROOT / "results" / "stage3" / "contract_v2"
OUT = ROOT / "figures" / "contract_v2"

COLORS = {
    "CK4": "#5B677A",
    "CK4+P": "#2F6BDE",
    "CK4+MSP": "#009E73",
    "CK4P-MSP": "#B83A62",
    "CK5": "#9A7D4F",
}


def style() -> None:
    plt.rcParams.update(
        {
            "font.family": "Arial",
            "font.size": 8.2,
            "axes.labelsize": 8.2,
            "axes.titlesize": 9.0,
            "axes.titleweight": "bold",
            "xtick.labelsize": 7.2,
            "ytick.labelsize": 7.2,
            "legend.fontsize": 6.8,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
            "svg.fonttype": "none",
        }
    )


def save(fig: plt.Figure, stem: str) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for suffix in ("png", "pdf", "svg"):
        fig.savefig(OUT / f"{stem}.{suffix}", dpi=450, bbox_inches="tight", pad_inches=0.04)
    plt.close(fig)


def clean_axes(ax: plt.Axes, grid_axis: str = "y") -> None:
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis=grid_axis, color="#D9DDE3", linewidth=0.55, alpha=0.85)
    ax.set_axisbelow(True)


def panel_label(ax: plt.Axes, label: str, title: str) -> None:
    ax.set_title(f"{label}. {title}", loc="left", pad=7)


def supplementary_s3() -> None:
    path = RESULTS / "art_current_contract" / "quality_stratified" / "art_quality_stratified_stability.csv"
    data = pd.read_csv(path)
    labels = {
        "ck4": "CK4",
        "ck4_p": "CK4+P",
        "ck4_msp": "CK4+MSP",
        "ck4p_msp": "CK4P-MSP",
        "ckmer5_count_l2": "CK5",
    }
    data["display"] = data["representation"].map(labels)
    lengths = sorted(data["length"].astype(int).unique().tolist())
    quality_order = ["low", "mid", "high"]

    fig, axes = plt.subplots(1, 3, figsize=(7.15, 2.75), gridspec_kw={"width_ratios": [1.0, 1.35, 1.05]})
    burden = data.drop_duplicates(["length", "quality_bin"])
    burden = burden.groupby("length", as_index=False).agg(
        difference_rate=("observed_base_difference_rate_mean", "mean"),
        mean_phred=("mean_phred_mean", "mean"),
    )
    axes[0].bar(burden["length"].astype(str), 100 * burden["difference_rate"], color="#7C6EA8", width=0.68)
    axes[0].set_xlabel("ART read length (bp)")
    axes[0].set_ylabel("observed base difference (%)")
    axes[0].tick_params(axis="x", rotation=35)
    clean_axes(axes[0])
    panel_label(axes[0], "A", "Simulator error load")

    ratios = []
    for (length, quality), part in data.groupby(["length", "quality_bin"]):
        pivot = part.set_index("display")["l2_delta_mean"]
        if "CK4" not in pivot or "CK4P-MSP" not in pivot:
            continue
        ratios.append({"length": int(length), "quality_bin": str(quality), "ratio": float(pivot["CK4P-MSP"] / pivot["CK4"])})
    ratio_frame = pd.DataFrame(ratios)
    matrix = ratio_frame.pivot(index="quality_bin", columns="length", values="ratio").reindex(index=quality_order, columns=lengths)
    image = axes[1].imshow(matrix.to_numpy(), aspect="auto", cmap="viridis_r", vmin=0.45, vmax=0.80)
    axes[1].set_xticks(np.arange(len(lengths)), lengths, rotation=35)
    axes[1].set_yticks(np.arange(len(quality_order)), quality_order)
    axes[1].set_xlabel("ART read length (bp)")
    axes[1].set_ylabel("quality stratum")
    panel_label(axes[1], "B", "CK4P-MSP / CK4 drift")
    for row in range(matrix.shape[0]):
        for col in range(matrix.shape[1]):
            value = matrix.iloc[row, col]
            axes[1].text(col, row, f"{value:.2f}", ha="center", va="center", fontsize=5.8, color="white" if value > 0.64 else "black")
    colorbar = fig.colorbar(image, ax=axes[1], fraction=0.042, pad=0.025)
    colorbar.ax.tick_params(labelsize=6.5)

    order = ["CK4", "CK4+P", "CK4+MSP", "CK4P-MSP", "CK5"]
    ratio_rows = []
    for (length, quality), part in data.groupby(["length", "quality_bin"]):
        pivot = part.set_index("display")["l2_delta_mean"]
        if "CK4" not in pivot:
            continue
        for representation in order:
            if representation in pivot:
                ratio_rows.append({"quality_bin": str(quality), "display": representation, "ratio": float(pivot[representation] / pivot["CK4"])})
    ratio_summary = pd.DataFrame(ratio_rows).groupby(["quality_bin", "display"], as_index=False)["ratio"].mean()
    for representation in order:
        part = ratio_summary[ratio_summary["display"].eq(representation)].set_index("quality_bin").reindex(quality_order)
        axes[2].plot(
            quality_order,
            part["ratio"],
            marker="o",
            linewidth=1.7 if representation == "CK4P-MSP" else 1.0,
            color=COLORS[representation],
            label=representation,
        )
    axes[2].axhline(1.0, color="#5B677A", linestyle="--", linewidth=0.7)
    axes[2].set_xlabel("quality stratum")
    axes[2].set_ylabel("L2 drift / CK4 drift")
    axes[2].set_ylim(0.45, 1.45)
    clean_axes(axes[2])
    panel_label(axes[2], "C", "Within-stratum ordering")
    axes[2].legend(frameon=False, ncol=2, loc="upper center", bbox_to_anchor=(0.5, -0.25), fontsize=5.9)
    fig.suptitle("ART error load varies by cycle profile; property-aware stability persists within strata", y=1.00, fontsize=9.8, fontweight="bold")
    fig.subplots_adjust(left=0.075, right=0.985, bottom=0.28, top=0.78, wspace=0.43)
    save(fig, "supplementary_figure_s3_art_current_contract")


def supplementary_s6() -> None:
    legacy = RESULTS / "msp_bin_gamma_sensitivity"
    stability = pd.read_csv(legacy / "stability_summary.csv")
    continuity = pd.read_csv(RESULTS / "short_read_length_continuity" / "length_continuity_binset_readout_summary.csv")
    bin_order = ["2", "2_3", "2_3_4", "2_3_4_6"]
    bin_labels = {"2": "2", "2_3": "2+3", "2_3_4": "2+3+4", "2_3_4_6": "2+3+4+6"}
    bin_colors = {"2": "#5B677A", "2_3": "#2F6BDE", "2_3_4": "#009E73", "2_3_4_6": "#B83A62"}
    fig, axes = plt.subplots(1, 2, figsize=(7.15, 3.0), gridspec_kw={"width_ratios": [0.9, 1.4]})
    for length, color in [(75, "#B83A62"), (100, "#2F6BDE")]:
        part = stability[(stability["length"].eq(length)) & (stability["binset"].eq("2_3_4_6"))].sort_values("gamma")
        axes[0].plot(part["gamma"], part["l2_delta_mean"], marker="o", linewidth=1.4, color=color, label=f"{length} bp")
    axes[0].axvline(1.0, color="#343A40", linestyle="--", linewidth=0.8, label="default $\\gamma=1$")
    axes[0].set_xlabel("MSP block weight $\\gamma$")
    axes[0].set_ylabel("mean paired L2 drift")
    clean_axes(axes[0])
    panel_label(axes[0], "A", "Weight sensitivity")
    axes[0].legend(frameon=False, loc="upper right")

    for binset in bin_order:
        part = continuity[continuity["binset"].eq(binset)].sort_values("length")
        axes[1].plot(part["length"], part["macro_f1_mean"], marker="o", markersize=2.6, linewidth=1.35, color=bin_colors[binset], label=bin_labels[binset])
    axes[1].set_xlabel("read length (bp)")
    axes[1].set_ylabel("grouped delta-readout macro-F1")
    axes[1].set_xticks([50, 55, 60, 65, 70, 75])
    axes[1].set_ylim(0.94, 1.002)
    clean_axes(axes[1])
    panel_label(axes[1], "B", "Binset continuity at $\\gamma=1$")
    axes[1].legend(frameon=False, ncol=2, loc="upper center", bbox_to_anchor=(0.5, -0.23))
    fig.suptitle("Static MSP sensitivity across representative WGS conditions and the 50 to 75 bp sweep", y=0.99, fontsize=9.7, fontweight="bold")
    fig.subplots_adjust(left=0.09, right=0.99, bottom=0.25, top=0.78, wspace=0.31)
    save(fig, "supplementary_figure_s6_msp_sensitivity")


def supplementary_s13() -> None:
    base = RESULTS / "short_read_length_continuity"
    stability = pd.read_csv(base / "length_continuity_stability_summary.csv")
    readout = pd.read_csv(base / "length_continuity_delta_readout_summary.csv")
    labels = {"ck4": "CK4", "ck4_p": "CK4+P", "ck4_msp": "CK4+MSP", "ck4p_msp": "CK4P-MSP"}
    order = ["CK4", "CK4+P", "CK4+MSP", "CK4P-MSP"]
    stability["display"] = stability["representation"].map(labels)
    readout["display"] = readout["representation"].map(labels)
    stability = stability[stability["display"].notna()].copy()
    readout = readout[readout["display"].notna()].copy()
    fig, axes = plt.subplots(1, 3, figsize=(7.15, 2.72), gridspec_kw={"width_ratios": [1.0, 1.0, 1.12]})
    for representation in order:
        part = stability[stability["display"].eq(representation)].sort_values("length")
        axes[0].plot(part["length"], part["l2_delta_mean"], marker="o", markersize=2.5, linewidth=1.7 if representation == "CK4P-MSP" else 1.0, color=COLORS[representation], label=representation)
        part = readout[readout["display"].eq(representation)].sort_values("length")
        axes[1].plot(part["length"], part["macro_f1_mean"], marker="o", markersize=2.5, linewidth=1.7 if representation == "CK4P-MSP" else 1.0, color=COLORS[representation], label=representation)
    for ax in axes[:2]:
        ax.set_xticks([50, 55, 60, 65, 70, 75])
        ax.set_xlabel("read length (bp)")
        clean_axes(ax)
    axes[0].set_ylabel("mean paired L2 drift")
    axes[0].set_ylim(0.12, 0.31)
    panel_label(axes[0], "A", "Controlled perturbation drift")
    axes[1].set_ylabel("grouped delta-readout macro-F1")
    axes[1].set_ylim(0.92, 1.003)
    panel_label(axes[1], "B", "Structured local-change readout")

    stab_pivot = stability.pivot(index="length", columns="display", values="l2_delta_mean")
    read_pivot = readout.pivot(index="length", columns="display", values="macro_f1_mean")
    p_gain = stab_pivot["CK4+MSP"] - stab_pivot["CK4P-MSP"]
    msp_gain = read_pivot["CK4P-MSP"] - read_pivot["CK4+P"]
    axes[2].plot(p_gain.index, p_gain, color=COLORS["CK4+P"], linewidth=1.5, marker="o", markersize=2.7, label="P: drift reduction | K+MSP")
    axes[2].plot(msp_gain.index, msp_gain, color=COLORS["CK4+MSP"], linewidth=1.5, marker="o", markersize=2.7, label="MSP: F1 increment | K+P")
    axes[2].axhline(0, color="#343A40", linewidth=0.7)
    axes[2].set_xticks([50, 55, 60, 65, 70, 75])
    axes[2].set_xlabel("read length (bp)")
    axes[2].set_ylabel("conditional increment")
    clean_axes(axes[2])
    panel_label(axes[2], "C", "Block-specific increments")
    axes[2].legend(frameon=False, fontsize=5.7, loc="upper center", bbox_to_anchor=(0.5, -0.26))
    handles, legend_labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, legend_labels, frameon=False, ncol=4, loc="upper center", bbox_to_anchor=(0.39, 0.055), fontsize=6.3)
    fig.suptitle("CK4P-MSP retains its stability-readability profile across 50 to 75 bp", y=1.00, fontsize=9.8, fontweight="bold")
    fig.subplots_adjust(left=0.075, right=0.995, bottom=0.31, top=0.79, wspace=0.33)
    save(fig, "supplementary_figure_s13_short_read_continuity")


def main() -> None:
    style()
    supplementary_s3()
    supplementary_s6()
    supplementary_s13()
    print(f"Generated short-read continuity figures in {OUT}")


if __name__ == "__main__":
    main()
