"""Generate manuscript figures exclusively from the public contract-v2 results.

The script deliberately keeps each figure to one claim.  It does not relabel
historic feature aliases as CK4P-MSP and it never plots MinHash as an L2-vector
baseline: MinHash is shown only through native estimated-versus-exact Jaccard
agreement.

Outputs are publication-ready PNG, PDF and SVG assets.  The default directory
is ``figures/contract_v2`` in the release repository.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
RESULTS = ROOT / "results" / "stage3" / "contract_v2"
DEFAULT_OUT = ROOT / "figures" / "contract_v2"

COLORS = {
    "CK4": "#5B677A",
    "P": "#70A5D8",
    "MSP": "#5DBA9B",
    "CK4+P": "#2F6BDE",
    "CK4+MSP": "#009E73",
    "P+MSP": "#7C6EA8",
    "CK4P-MSP": "#B83A62",
    "CK5": "#9A7D4F",
    "Hashed k=15": "#D17A22",
    "Sparse RP k=15": "#7768AE",
}
ABLATION_ORDER = ["CK4", "P", "MSP", "CK4+P", "CK4+MSP", "P+MSP", "CK4P-MSP"]
NESTED_ORDER = ["CK4", "CK4+P", "CK4+MSP", "CK4P-MSP"]


def style() -> None:
    plt.rcParams.update(
        {
            "font.family": "Arial",
            "font.size": 8.2,
            "axes.labelsize": 8.2,
            "axes.titlesize": 9.2,
            "axes.titleweight": "bold",
            "xtick.labelsize": 7.5,
            "ytick.labelsize": 7.5,
            "legend.fontsize": 7.2,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
            "svg.fonttype": "none",
        }
    )


def save(fig: plt.Figure, out: Path, stem: str) -> None:
    out.mkdir(parents=True, exist_ok=True)
    for suffix in ("png", "pdf", "svg"):
        fig.savefig(out / f"{stem}.{suffix}", dpi=400, bbox_inches="tight", pad_inches=0.04)
    plt.close(fig)


def clean_axes(ax: plt.Axes) -> None:
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis="y", color="#D9DDE3", linewidth=0.6, alpha=0.8)
    ax.set_axisbelow(True)


def panel_label(ax: plt.Axes, label: str, title: str) -> None:
    ax.set_title(f"{label}. {title}", loc="left", pad=7)


def contribution_data() -> tuple[pd.DataFrame, pd.DataFrame]:
    base = RESULTS / "p_msp_contribution"
    stability = pd.read_csv(base / "p_msp_contribution_stability_summary.csv")
    readout = pd.read_csv(base / "p_msp_contribution_delta_readout_summary.csv")
    return stability, readout


def figure_2(out: Path) -> None:
    """Show metric-specific K, P and MSP roles across all seven combinations."""
    stability, readout = contribution_data()
    stability = stability.set_index("representation_label").loc[ABLATION_ORDER].reset_index()
    readout = readout.set_index("representation_label").loc[ABLATION_ORDER].reset_index()
    merged = stability.merge(
        readout[["representation_label", "macro_f1_mean", "macro_f1_std_mean"]],
        on="representation_label",
        how="left",
    )
    y = np.arange(len(ABLATION_ORDER))[::-1]
    fig, axes = plt.subplots(1, 3, figsize=(7.15, 3.05), sharey=True, gridspec_kw={"wspace": 0.16})
    panel_specs = [
        ("l2_delta_mean", "mean paired L2 drift", (0.0, 0.27), "A", "Global drift"),
        ("macro_f1_mean", "grouped delta-readout macro-F1", (0.56, 1.005), "B", "Local-change readout"),
        ("retrieval_top1_mean", "nearest-clean retrieval", (0.0, 1.09), "C", "Nearest-clean retrieval"),
    ]
    for ax, (column, xlabel, xlim, tag, title) in zip(axes, panel_specs):
        values = merged[column].to_numpy(dtype=float)
        ax.hlines(y, xlim[0], values, color="#D9DDE3", linewidth=1.1, zorder=1)
        for yy, label, value in zip(y, ABLATION_ORDER, values):
            ax.scatter(value, yy, s=46, color=COLORS[label], edgecolor="white", linewidth=0.65, zorder=3)
            offset = 0.008 * (xlim[1] - xlim[0])
            ax.text(min(value + offset, xlim[1] - 0.005), yy, f"{value:.3f}", va="center", ha="left", fontsize=6.4)
        ax.set_xlim(*xlim)
        ax.set_xlabel(xlabel)
        ax.grid(axis="x", color="#E1E4E8", linewidth=0.55, alpha=0.85)
        ax.grid(axis="y", visible=False)
        ax.spines[["top", "right"]].set_visible(False)
        panel_label(ax, tag, title)
    axes[0].set_yticks(y, ABLATION_ORDER)
    axes[0].tick_params(axis="y", length=0)
    fig.suptitle("K, P and MSP contribute along different representation-audit axes", y=1.01, fontsize=10.4, fontweight="bold")
    fig.subplots_adjust(left=0.12, right=0.995, bottom=0.17, top=0.83, wspace=0.20)
    save(fig, out, "figure_2_p_msp_contribution")


def figure_3(out: Path) -> None:
    """Compare compact stability with contiguous and compressed high-k vectors."""
    df = pd.read_csv(RESULTS / "high_k_compressed_baselines" / "high_k_stability_summary.csv")
    labels = {"CK4+P": "CK4+P", "CK4P-MSP": "CK4P-MSP", "CK4": "CK4", "CK5": "CK5"}
    df["short"] = df["representation_label"].map(labels).fillna(df["representation_label"])
    vector = df[df["short"].isin(["CK4+P", "CK4P-MSP", "CK4", "CK5", "Hashed k=15, d=222", "CK15 random projection, d=222"])].copy()
    vector["display"] = vector["short"].replace({"Hashed k=15, d=222": "Hashed k=15", "CK15 random projection, d=222": "Sparse RP k=15"})
    order = ["CK4", "CK4+P", "CK4P-MSP", "CK5", "Hashed k=15", "Sparse RP k=15"]
    vector = vector.set_index("display").loc[order].reset_index()
    short_ticks = ["CK4", "CK4+P", "CK4P-\nMSP", "CK5", "Hash\nk=15", "RP\nk=15"]

    fig, axes = plt.subplots(1, 3, figsize=(7.15, 2.35), gridspec_kw={"width_ratios": [1.1, 1.05, 1.15]})
    for ax, col, ylabel, tag, title in [
        (axes[0], "paired_cosine", "mean paired cosine", "A", "Similarity under perturbation"),
        (axes[1], "l2_drift", "mean paired L2 drift", "B", "Standardized representation drift"),
    ]:
        values = vector[col].to_numpy()
        ax.bar(np.arange(len(order)), values, color=[COLORS[x] for x in order], width=0.7)
        ax.set_xticks(np.arange(len(order)), [label.replace("\n", " ") for label in short_ticks], fontsize=6.4, rotation=32, ha="right")
        ax.set_ylabel(ylabel)
        clean_axes(ax)
        panel_label(ax, tag, title)
        ax.set_ylim((0.75, 1.01) if col == "paired_cosine" else (0, 0.60))
    label_offsets = {
        "CK4": (5, 5), "CK4+P": (5, 5), "CK4P-MSP": (5, 5), "CK5": (5, 5),
        "Hashed k=15": (5, 4), "Sparse RP k=15": (5, -20),
    }
    label_text = {"CK4P-MSP": "CK4P-MSP", "Hashed k=15": "Hash k=15", "Sparse RP k=15": "RP k=15"}
    for _, row in vector.iterrows():
        label = row["display"]
        axes[2].scatter(row["median_features"], row["l2_drift"], s=58, color=COLORS[label], edgecolor="white", linewidth=0.7, zorder=3)
        axes[2].annotate(label_text.get(label, label), (row["median_features"], row["l2_drift"]), xytext=label_offsets[label], textcoords="offset points", fontsize=6.7)
    axes[2].set_xlabel("feature dimension")
    axes[2].set_ylabel("mean paired L2 drift")
    axes[2].set_xscale("log")
    axes[2].set_xlim(110, 620)
    axes[2].set_ylim(0.02, 0.58)
    clean_axes(axes[2])
    panel_label(axes[2], "C", "Dimension-constrained comparison")
    fig.suptitle("Compact CK4P-MSP retains stability relative to CK4/CK5 and compressed high-k vectors", y=1.03, fontsize=10.1, fontweight="bold")
    fig.tight_layout()
    save(fig, out, "figure_3_contract_v2_stability")


def figure_4(out: Path) -> None:
    """Separate external stability, coarse readability and fine-label limits."""
    cami2 = pd.read_csv(RESULTS / "cami2_marine_stability" / "cami2_marine_stability.csv")
    cami = pd.read_csv(RESULTS / "cami_toy_readout" / "cami_probe_readout.csv")
    label_map = {
        "ck4": "CK4",
        "ck4_p": "CK4+P",
        "ck4p_msp": "CK4P-MSP",
        "ckmer5_count_l2": "CK5",
    }
    order = ["CK4", "CK4+P", "CK4P-MSP", "CK5"]

    panels: list[tuple[pd.DataFrame, str, str, tuple[float, float], str, str]] = []
    external = cami2[cami2["condition"].ne("clean")].copy()
    external["display"] = external["representation"].map(label_map)
    panels.append((external, "l2_delta_mean", "mean paired L2 drift", (0.0, 0.38), "A", "CAMI II stability"))

    logistic = cami[cami["classifier"].eq("logistic")].copy()
    logistic["display"] = logistic["representation"].map(label_map)
    coarse = logistic[logistic["task"].eq("target_background")].copy()
    fine = logistic[logistic["task"].eq("label_probe")].copy()
    panels.append((coarse, "macro_f1", "logistic macro-F1", (0.0, 1.0), "B", "Coarse target/background"))
    panels.append((fine, "macro_f1", "logistic macro-F1", (0.0, 0.35), "C", "Thirty-label boundary"))

    fig, axes = plt.subplots(1, 3, figsize=(7.15, 2.55), gridspec_kw={"wspace": 0.30})
    for panel_index, (ax, (frame, column, ylabel, ylim, tag, title)) in enumerate(zip(axes, panels)):
        means, lows, highs = [], [], []
        for rep_index, representation in enumerate(order):
            values = frame.loc[frame["display"].eq(representation), column].to_numpy(dtype=float)
            low, high = _cell_bootstrap_interval(values, seed=20260729 + 10 * panel_index + rep_index)
            mean = float(values.mean())
            means.append(mean)
            lows.append(mean - low)
            highs.append(high - mean)
        x = np.arange(len(order))
        ax.bar(
            x,
            means,
            yerr=np.vstack([lows, highs]),
            capsize=2.5,
            width=0.70,
            color=[COLORS[label] for label in order],
        )
        ax.set_xticks(x, ["CK4", "CK4+P", "CK4P-\nMSP", "CK5"], rotation=20, ha="right")
        ax.set_ylabel(ylabel)
        ax.set_ylim(*ylim)
        clean_axes(ax)
        panel_label(ax, tag, title)
    fig.suptitle(
        "External probes distinguish compact stability from task-granularity limits",
        y=1.02,
        fontsize=10.0,
        fontweight="bold",
    )
    fig.subplots_adjust(left=0.08, right=0.99, bottom=0.22, top=0.78, wspace=0.34)
    save(fig, out, "figure_4_external_contract_v2")


def figure_6(out: Path) -> None:
    """Make local readability the result and the L2 ratio a transparent boundary."""
    # Use the matched contribution audit for all four nested representations.
    _, contribution = contribution_data()
    readout = contribution.rename(columns={"representation_label": "display", "macro_f1_mean": "macro_f1", "macro_f1_std_mean": "std"})
    readout = readout.set_index("display").loc[NESTED_ORDER].reset_index()

    ratio = pd.read_csv(RESULTS / "local_mutation_sensitivity" / "local_mutation_sensitivity_summary.csv")
    labels = {"ck4": "CK4", "ck4_p": "CK4+P", "ck4_msp": "CK4+MSP", "ck4p_msp": "CK4P-MSP"}
    ratio = ratio[ratio["representation"].isin(labels)].copy()
    ratio["display"] = ratio["representation"].map(labels)
    ratio = ratio.groupby("display", as_index=False)["selective_sensitivity_ratio_mean"].mean()
    ratio = ratio.set_index("display").loc[NESTED_ORDER].reset_index()

    fig, axes = plt.subplots(1, 2, figsize=(7.15, 2.35), gridspec_kw={"width_ratios": [1.18, 0.82]})
    x = np.arange(len(NESTED_ORDER))
    axes[0].bar(x, readout["macro_f1"], yerr=readout["std"], capsize=2.5, color=[COLORS[v] for v in NESTED_ORDER], width=0.7)
    axes[0].set_xticks(x, NESTED_ORDER, rotation=20, ha="right")
    axes[0].set_ylim(0.84, 1.025)
    axes[0].set_ylabel("grouped delta-readout macro-F1")
    clean_axes(axes[0])
    panel_label(axes[0], "A", "Structured local-change readout")
    for i, row in readout.iterrows():
        axes[0].text(i, row["macro_f1"] + row["std"] + 0.006, f"{row['macro_f1']:.3f}", ha="center", va="bottom", fontsize=7)

    x = np.arange(len(ratio))
    axes[1].bar(x, ratio["selective_sensitivity_ratio_mean"], color=[COLORS[v] for v in ratio["display"]], width=0.68)
    axes[1].axhline(1, color="#343A40", linestyle="--", linewidth=0.8)
    axes[1].set_xticks(x, ratio["display"], rotation=20, ha="right")
    axes[1].set_ylim(0, 1.12)
    axes[1].set_ylabel("local / nuisance L2 ratio")
    clean_axes(axes[1])
    panel_label(axes[1], "B", "Distance-ratio boundary")
    axes[1].text(1.0, 1.03, "1 = equal response", ha="center", va="bottom", fontsize=6.8, color="#343A40")
    fig.suptitle("CK4P-MSP preserves grouped local-change readout; raw L2 ratios remain a boundary", y=1.03, fontsize=10.0, fontweight="bold")
    fig.tight_layout()
    save(fig, out, "figure_6_local_readout_boundary")


def supplementary_s2(out: Path) -> None:
    df = pd.read_csv(RESULTS / "knn_mi_robustness" / "knn_mi_summary.csv")
    inference = pd.read_csv(RESULTS / "knn_mi_robustness" / "knn_mi_increment_inference.csv").iloc[0]
    labels = {"dK": "$d_K$", "dK_dP": "$d_K+d_P$", "dK_dM": "$d_K+d_M$", "dK_dP_dM": "$d_K+d_P+d_M$"}
    order = ["dK", "dK_dP", "dK_dM", "dK_dP_dM"]
    df = df.set_index("feature_set").loc[order].reset_index()
    labels_out = [labels[v] for v in df["feature_set"]]
    err_low = df["mean_knn_mi_bits"] - df["mean_subsample_ci_low"]
    err_hi = df["mean_subsample_ci_high"] - df["mean_knn_mi_bits"]
    fig, ax = plt.subplots(figsize=(5.2, 2.9))
    colors = ["#5B677A", "#2F6BDE", "#009E73", "#B83A62"]
    ax.bar(np.arange(4), df["mean_knn_mi_bits"], yerr=np.vstack([err_low, err_hi]), capsize=3, color=colors, width=0.68)
    ax.set_xticks(np.arange(4), labels_out)
    ax.set_ylabel("KSG-style MI estimate (bits)")
    ax.set_ylim(0.65, 0.96)
    clean_axes(ax)
    panel_label(ax, "S2", "Estimator-dependent local-versus-noise separability audit")
    ax.text(
        0.02,
        -0.28,
        (
            "Error bars: 2.5th-97.5th percentiles across stratified subsamples.\n"
            f"Signed joint-minus-K increment = {inference['mean_signed_increment_bits']:.3f} bits; "
            f"cell bootstrap 95% CI {inference['bootstrap_95_ci_low']:.3f}-"
            f"{inference['bootstrap_95_ci_high']:.3f}.\n"
            f"Aggregate label-permutation P = {inference['aggregate_label_permutation_p']:.4f}."
        ),
        transform=ax.transAxes,
        fontsize=6.5,
        va="top",
    )
    fig.subplots_adjust(left=0.13, right=0.99, top=0.84, bottom=0.30)
    save(fig, out, "supplementary_figure_s2_knn_mi")


def supplementary_s1(out: Path) -> None:
    """Show the fitted-reduction boundary and fixed-contract weight audit."""
    base = RESULTS / "dimension_reduction_baselines"
    stability = pd.read_csv(base / "dimension_reduction_stability_summary.csv")
    readout = pd.read_csv(base / "dimension_reduction_readout_summary.csv")
    weight_stability = pd.read_csv(RESULTS / "mixed_metric_audit" / "block_weight_stability_summary.csv")
    weight_readout = pd.read_csv(RESULTS / "mixed_metric_audit" / "block_weight_delta_readout_summary.csv")

    keep = [
        "CK4",
        "CK4+P",
        "CK4P-MSP",
        "CK5",
        "CK7 PCA-147",
        "CK7 SVD-147",
        "CK7 PCA-222",
        "CK7 SVD-222",
    ]
    stability = stability[stability["representation_label"].isin(keep)].copy()
    stability["representation_label"] = pd.Categorical(stability["representation_label"], keep, ordered=True)
    stability = stability.sort_values("representation_label")

    logistic = readout[
        readout["classifier"].eq("logistic") & readout["representation_label"].isin(keep)
    ].copy()
    logistic["representation_label"] = pd.Categorical(logistic["representation_label"], keep, ordered=True)
    logistic = logistic.sort_values("representation_label")

    fig = plt.figure(figsize=(7.15, 6.2))
    gs = fig.add_gridspec(3, 1, height_ratios=[1.0, 1.0, 1.15], hspace=0.58)
    axes = [fig.add_subplot(gs[index, 0]) for index in range(3)]

    x = np.arange(len(stability))
    colors = [COLORS.get(str(label), "#7768AE") for label in stability["representation_label"]]
    axes[0].bar(x, stability["l2_drift"], color=colors, width=0.68)
    axes[0].set_xticks(x, [str(v).replace(" ", "\n") for v in stability["representation_label"]])
    axes[0].set_ylabel("mean paired L2 drift")
    clean_axes(axes[0])
    panel_label(axes[0], "A", "Data-fitted CK7 reductions define a stability boundary")

    x = np.arange(len(logistic))
    colors = [COLORS.get(str(label), "#7768AE") for label in logistic["representation_label"]]
    axes[1].bar(x, logistic["macro_f1"], color=colors, width=0.68)
    axes[1].set_xticks(x, [str(v).replace(" ", "\n") for v in logistic["representation_label"]])
    axes[1].set_ylabel("logistic macro-F1")
    axes[1].set_ylim(0.36, 0.44)
    clean_axes(axes[1])
    panel_label(axes[1], "B", "Shallow readout remains low and task-limited")

    order = ["identity_only", "ck4_plus_p", "ck4p_msp", "identity_dominant", "property_dominant", "property_only"]
    labels = ["K only", "K+P", "K+P+MSP", "K-dominant", "property-dominant", "P+MSP only"]
    ws = weight_stability.set_index("weight_name").loc[order].reset_index()
    wr = weight_readout.set_index("weight_name").loc[order].reset_index()
    x = np.arange(len(order))
    axes[2].bar(x, ws["l2_drift"], color="#7C6EA8", alpha=0.82, width=0.62, label="paired L2 drift")
    axes[2].set_xticks(x, labels, rotation=18, ha="right")
    axes[2].set_ylabel("mean paired L2 drift")
    axes[2].grid(axis="y", color="#D9DDE3", linewidth=0.6)
    axes[2].spines[["top", "right"]].set_visible(False)
    ax2 = axes[2].twinx()
    ax2.plot(x, wr["macro_f1"], color="#B83A62", marker="o", linewidth=1.4, label="grouped delta-readout")
    ax2.set_ylabel("grouped macro-F1")
    ax2.set_ylim(0.86, 1.00)
    ax2.spines["top"].set_visible(False)
    handles, labels_out = axes[2].get_legend_handles_labels()
    handles2, labels2 = ax2.get_legend_handles_labels()
    axes[2].legend(handles + handles2, labels_out + labels2, frameon=False, loc="upper center", ncol=2)
    panel_label(axes[2], "C", "Fixed-contract block-weight audit")

    fig.suptitle(
        "Fitted projection can improve drift; CK4P-MSP remains training-free and block-decomposable",
        y=0.985,
        fontsize=10.0,
        fontweight="bold",
    )
    fig.subplots_adjust(left=0.10, right=0.90, bottom=0.09, top=0.92)
    save(fig, out, "supplementary_figure_s1_baseline_audit")


def supplementary_s4(out: Path) -> None:
    df = pd.read_csv(
        RESULTS / "local_mutation_fraction_sweep" / "local_mutation_fraction_delta_readout_summary.csv"
    )
    df = df[df["classifier"].eq("logistic")].copy()
    labels = {"ck4": "CK4", "ck4_p": "CK4+P", "ck4_msp": "CK4+MSP", "ck4p_msp": "CK4P-MSP"}
    fig, ax = plt.subplots(figsize=(5.7, 3.15))
    for representation, label in labels.items():
        part = df[df["representation"].eq(representation)].sort_values("mutation_fraction")
        ax.plot(
            100.0 * part["mutation_fraction"],
            part["macro_f1"],
            marker="o",
            linewidth=1.7 if representation == "ck4p_msp" else 1.2,
            color=COLORS[label],
            label=label,
        )
    ax.set_xlabel("locally changed positions (%)")
    ax.set_ylabel("grouped delta-readout macro-F1")
    ax.set_ylim(0.55, 1.01)
    clean_axes(ax)
    panel_label(ax, "S4", "MSP-associated readability persists across effect sizes")
    ax.legend(frameon=False, loc="lower right", ncol=2)
    fig.tight_layout()
    save(fig, out, "supplementary_figure_s4_mutation_fraction")


def supplementary_s6(out: Path) -> None:
    stability = pd.read_csv(RESULTS / "msp_bin_gamma_sensitivity" / "stability_summary.csv")
    readout = pd.read_csv(RESULTS / "msp_bin_gamma_sensitivity" / "delta_readout_summary.csv")
    bin_order = ["2", "2_3", "2_3_4", "2_3_4_6"]
    bin_labels = ["2", "2+3", "2+3+4", "2+3+4+6"]
    fig, axes = plt.subplots(1, 2, figsize=(7.15, 2.4))
    for length, color in [(69, "#B83A62"), (75, "#2F6BDE")]:
        part = stability[(stability["length"] == length) & (stability["binset"] == "2_3_4_6")]
        axes[0].plot(part["gamma"], part["l2_delta_mean"], marker="o", color=color, label=f"{length} bp")
    axes[0].axvline(1.0, color="#343A40", linestyle="--", linewidth=0.8, label="default $\\gamma=1$")
    axes[0].set_xlabel("MSP block weight $\\gamma$")
    axes[0].set_ylabel("mean paired L2 drift")
    clean_axes(axes[0]); panel_label(axes[0], "A", "Weight sensitivity at the full binset")
    axes[0].legend(frameon=False, loc="upper right")
    part = readout[(readout["gamma"] == 1.0) & (readout["binset"].isin(bin_order))]
    for length, color in [(69, "#B83A62"), (100, "#009E73"), (150, "#2F6BDE")]:
        d = part[part["length"] == length].set_index("binset").loc[bin_order].reset_index()
        axes[1].plot(np.arange(len(bin_order)), d["macro_f1_mean"], marker="o", color=color, label=f"{length} bp")
    axes[1].set_xticks(np.arange(len(bin_order)), bin_labels)
    axes[1].set_xlabel("cumulative MSP binset")
    axes[1].set_ylabel("grouped delta-readout macro-F1")
    axes[1].set_ylim(0.75, 1.01)
    clean_axes(axes[1]); panel_label(axes[1], "B", "Binset sensitivity at $\\gamma=1$")
    axes[1].legend(frameon=False, loc="lower right")
    fig.suptitle("Static MSP remains usable over the tested short-read grid", y=1.03, fontsize=10.2, fontweight="bold")
    fig.tight_layout()
    save(fig, out, "supplementary_figure_s6_msp_sensitivity")


def supplementary_s7(out: Path) -> None:
    stability = pd.read_csv(RESULTS / "high_k_compressed_baselines" / "high_k_stability_summary.csv")
    stability["display"] = stability["representation_label"].replace({"Hashed k=15, d=222": "Hashed k=15", "CK15 random projection, d=222": "Sparse RP k=15"})
    order = ["CK4", "CK4P-MSP", "CK5", "Hashed k=15", "Sparse RP k=15"]
    stability = stability.set_index("display").loc[order].reset_index()
    minhash = pd.read_csv(RESULTS / "high_k_compressed_baselines" / "high_k_minhash_jaccard.csv")
    fig, axes = plt.subplots(1, 2, figsize=(7.15, 2.35), gridspec_kw={"width_ratios": [1.1, 1]})
    axes[0].bar(np.arange(len(order)), stability["l2_drift"], color=[COLORS[x] for x in order], width=0.68)
    axes[0].set_xticks(np.arange(len(order)), [x.replace(" ", "\n") for x in order], fontsize=6.8)
    axes[0].set_ylabel("mean paired L2 drift")
    axes[0].set_ylim(0, 0.58)
    clean_axes(axes[0]); panel_label(axes[0], "A", "Vector-space comparison")
    axes[1].scatter(minhash["exact_jaccard_mean"], minhash["minhash_jaccard_mean"], s=25, alpha=0.7, color="#7768AE", edgecolors="none")
    lims = [min(minhash["exact_jaccard_mean"].min(), minhash["minhash_jaccard_mean"].min()), max(minhash["exact_jaccard_mean"].max(), minhash["minhash_jaccard_mean"].max())]
    axes[1].plot(lims, lims, color="#343A40", linestyle="--", linewidth=0.8)
    axes[1].set_xlim(lims); axes[1].set_ylim(lims)
    axes[1].set_xlabel("exact Jaccard")
    axes[1].set_ylabel("estimated MinHash Jaccard")
    axes[1].text(0.03, 0.94, f"mean MAE = {minhash['mean_absolute_error'].mean():.3f}", transform=axes[1].transAxes, va="top", fontsize=7.3)
    clean_axes(axes[1]); panel_label(axes[1], "B", "Native MinHash audit")
    fig.suptitle("Compressed high-k vector controls and native MinHash use separate geometries", y=1.03, fontsize=10.0, fontweight="bold")
    fig.tight_layout()
    save(fig, out, "supplementary_figure_s7_high_k_audit")


def supplementary_s8(out: Path) -> None:
    cca = pd.read_csv(RESULTS / "property_redundancy_runtime" / "property_msp_cca_detail.csv")
    runtime = pd.read_csv(RESULTS / "property_redundancy_runtime" / "feature_runtime_summary.csv")
    runtime = runtime.groupby("representation_label", as_index=False).agg(ms_per_10k_reads=("ms_per_10k_reads", "mean"))
    keep = ["CK4", "CK4+P", "CK4P-MSP", "Hashed k=15, d=222", "CK15 random projection, d=222"]
    runtime = runtime[runtime["representation_label"].isin(keep)].copy()
    runtime["display"] = runtime["representation_label"].replace({"Hashed k=15, d=222": "Hashed k=15", "CK15 random projection, d=222": "Sparse RP k=15"})
    runtime = runtime.sort_values("ms_per_10k_reads")
    fig, axes = plt.subplots(1, 2, figsize=(7.15, 2.35), gridspec_kw={"width_ratios": [1.05, 1]})
    for length, part in cca.groupby("length"):
        axes[0].plot(part["component"], part["canonical_correlation"], marker="o", linewidth=1.2, label=f"{length} bp")
    axes[0].set_xlabel("canonical component")
    axes[0].set_ylabel("canonical correlation (P vs MSP)")
    axes[0].set_ylim(0, 1.05)
    clean_axes(axes[0]); panel_label(axes[0], "A", "Related, not independent, property layers")
    axes[0].legend(frameon=False, ncol=2, loc="lower left")
    axes[1].barh(np.arange(len(runtime)), runtime["ms_per_10k_reads"], color=[COLORS.get(x, "#7768AE") for x in runtime["display"]])
    axes[1].set_yticks(np.arange(len(runtime)), runtime["display"])
    axes[1].set_xlabel("mean feature extraction time (ms / 10k reads)")
    clean_axes(axes[1]); axes[1].grid(axis="x", color="#D9DDE3", linewidth=0.6); axes[1].grid(axis="y", visible=False)
    panel_label(axes[1], "B", "Runtime boundary")
    fig.suptitle("P and MSP share a global property component; compactness is not a speed claim", y=1.03, fontsize=10.0, fontweight="bold")
    fig.tight_layout()
    save(fig, out, "supplementary_figure_s8_redundancy_runtime")


def _cell_bootstrap_interval(values: np.ndarray, seed: int = 20260728) -> tuple[float, float]:
    rng = np.random.default_rng(seed)
    indices = rng.integers(0, len(values), size=(10000, len(values)))
    means = values[indices].mean(axis=1)
    return float(np.quantile(means, 0.025)), float(np.quantile(means, 0.975))


def supplementary_s11(out: Path) -> None:
    """Separate positional and chemistry readouts and show the scaling boundary."""
    readout = pd.read_csv(RESULTS / "local_change_factorial" / "local_change_factorial_readout.csv")
    scaling = pd.read_csv(RESULTS / "property_scaling" / "property_scaling_summary.csv")
    high_k = pd.read_csv(RESULTS / "high_k_compressed_baselines" / "high_k_stability_summary.csv")
    reps = ["CK4", "CK4+P", "CK4+MSP", "CK4P-MSP"]
    targets = [("spatial_pattern", "spatial localization"), ("chemistry", "substitution chemistry")]

    fig, axes = plt.subplots(1, 2, figsize=(7.15, 3.05), gridspec_kw={"width_ratios": [1.2, 0.9]})
    x = np.arange(len(reps))
    width = 0.34
    for target_index, (target, label) in enumerate(targets):
        means, lows, highs = [], [], []
        for rep_index, representation in enumerate(reps):
            values = readout.loc[
                readout["target"].eq(target) & readout["representation_label"].eq(representation),
                "macro_f1_mean",
            ].to_numpy(dtype=float)
            low, high = _cell_bootstrap_interval(values, seed=20260728 + 10 * target_index + rep_index)
            means.append(float(values.mean()))
            lows.append(float(values.mean() - low))
            highs.append(float(high - values.mean()))
        positions = x + (target_index - 0.5) * width
        axes[0].bar(
            positions,
            means,
            width=width,
            yerr=np.vstack([lows, highs]),
            capsize=2.5,
            color=["#4C78A8", "#E39D47"][target_index],
            label=label,
        )
    axes[0].set_xticks(x, ["CK4", "CK4+P", "CK4+MSP", "CK4P-\nMSP"])
    axes[0].set_ylim(0.45, 1.02)
    axes[0].set_ylabel("grouped delta-readout macro-F1")
    handles, labels = axes[0].get_legend_handles_labels()
    clean_axes(axes[0])
    panel_label(axes[0], "A", "Factorial mechanism readout")

    schemes = ["declared", "unit_range", "train_zscore"]
    scheme_labels = ["declared maps", "fixed [0,1] maps", "train z-score"]
    for prefix, label, color, marker in [
        ("CK4P-MSP", "CK4P-MSP", COLORS["CK4P-MSP"], "o"),
        ("CK4+P", "CK4+P", COLORS["CK4+P"], "s"),
    ]:
        values = []
        for scheme in schemes:
            row = scaling[scaling["representation"].eq(f"{prefix}_{scheme}")]
            values.append(float(row["l2_drift"].iloc[0]))
        axes[1].plot(np.arange(3), values, color=color, marker=marker, linewidth=1.5, label=label)
    ck4_drift = float(high_k.loc[high_k["representation_label"].eq("CK4"), "l2_drift"].iloc[0])
    axes[1].axhline(ck4_drift, color=COLORS["CK4"], linestyle="--", linewidth=1.0, label="CK4 reference")
    axes[1].set_xticks(np.arange(3), scheme_labels, rotation=18, ha="right")
    axes[1].set_ylabel("mean paired L2 drift")
    axes[1].set_ylim(0, 0.46)
    axes[1].legend(frameon=False, loc="upper left")
    clean_axes(axes[1])
    panel_label(axes[1], "B", "Within-block scaling boundary")

    fig.suptitle(
        "MSP exposes spatial structure; fixed map rescaling preserves the compact trade-off",
        y=0.985,
        fontsize=10.0,
        fontweight="bold",
    )
    fig.legend(
        handles,
        labels,
        frameon=False,
        loc="upper left",
        bbox_to_anchor=(0.085, 0.895),
        ncol=2,
        columnspacing=1.2,
        handlelength=1.5,
    )
    fig.subplots_adjust(left=0.09, right=0.985, bottom=0.20, top=0.68, wspace=0.30)
    save(fig, out, "supplementary_figure_s11_factorial_scaling")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--outdir", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()
    style()
    figure_2(args.outdir)
    figure_3(args.outdir)
    figure_4(args.outdir)
    figure_6(args.outdir)
    supplementary_s1(args.outdir)
    supplementary_s2(args.outdir)
    supplementary_s4(args.outdir)
    supplementary_s6(args.outdir)
    supplementary_s7(args.outdir)
    supplementary_s8(args.outdir)
    supplementary_s11(args.outdir)
    print(f"Wrote contract-v2 assets to {args.outdir}")


if __name__ == "__main__":
    main()
