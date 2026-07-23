from __future__ import annotations

import os
import sys
from pathlib import Path

os.environ.setdefault("MPLBACKEND", "Agg")

import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
import pandas as pd
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch


def _find_project_root(start: Path) -> Path:
    for candidate in [start.parent, *start.parents]:
        if (candidate / "methods").is_dir() and (candidate / "configs").is_dir():
            return candidate
    raise RuntimeError("Could not locate the release repository root.")


PROJECT_ROOT = _find_project_root(Path(__file__).resolve())
sys.path.insert(0, str(PROJECT_ROOT))
FIG_DIR = PROJECT_ROOT / "manuscript" / "figures"
RESULT_FIG_DIR = PROJECT_ROOT / "results" / "stage3" / "figures"


COLORS = {
    "identity": "#4b5563",
    "property": "#2563eb",
    "msp": "#16a34a",
    "full": "#dc2626",
    "csp": "#d97706",
    "boundary": "#7c3aed",
    "muted": "#9ca3af",
    "ink": "#111827",
}


REP_LABELS = {
    "ckmer4_count_l2": "CK4",
    "ckmer4_property_l2": "CK4+P",
    "ckmer4_property_multiscale_mean_l2": "CK4P-MSP",
    "ckmer4_property_multiscale_l2": "CK4P-MSP + std",
    "ckmer5_count_l2": "CK5",
    "ckmer7_count_l2": "CK7",
    "cspaced_count_l2": "spaced count",
    "cspaced_property_l2": "CSP",
    "hybrid_ckmer5_csp": "CK5+CSP",
    "property_channels": "property channels",
    "one_hot": "one-hot",
    "base_property": "one-hot + property",
    "kmer_property": "position k-mer property",
    "rope_onehot": "RoPE one-hot",
    "rope_property": "RoPE property",
}


def configure() -> None:
    mpl.rcParams.update(
        {
            "font.family": "sans-serif",
            "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans", "sans-serif"],
            "svg.fonttype": "none",
            "pdf.fonttype": 42,
            "font.size": 7.5,
            "axes.titlesize": 8.5,
            "axes.labelsize": 7.5,
            "xtick.labelsize": 7,
            "ytick.labelsize": 7,
            "legend.fontsize": 6.7,
            "axes.spines.right": False,
            "axes.spines.top": False,
            "figure.facecolor": "white",
        }
    )


def save(fig: plt.Figure, name: str) -> None:
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    RESULT_FIG_DIR.mkdir(parents=True, exist_ok=True)
    for folder in (FIG_DIR, RESULT_FIG_DIR):
        fig.savefig(folder / f"{name}.png", dpi=360, bbox_inches="tight")
        fig.savefig(folder / f"{name}.svg", bbox_inches="tight")
        fig.savefig(folder / f"{name}.pdf", bbox_inches="tight")
    plt.close(fig)


def label_rep(values: pd.Series) -> pd.Series:
    return values.map(REP_LABELS).fillna(values)


def barh_metric(ax, df: pd.DataFrame, y_col: str, x_col: str, color_col: str | None = None, title: str = "", xlabel: str = ""):
    labels = df[y_col].tolist()
    y = np.arange(len(labels))
    colors = df[color_col].tolist() if color_col else COLORS["property"]
    ax.barh(y, df[x_col], color=colors, edgecolor=COLORS["ink"], linewidth=0.35)
    ax.set_yticks(y)
    ax.set_yticklabels(labels)
    ax.invert_yaxis()
    ax.set_title(title, loc="left", weight="bold")
    ax.set_xlabel(xlabel)
    ax.grid(axis="x", color="#e5e7eb", linewidth=0.6)
    ax.set_axisbelow(True)


def figure1_framework() -> plt.Figure:
    fig, ax = plt.subplots(figsize=(7.2, 4.15))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    def box(x, y, w, h, title, body, fc, ec):
        patch = FancyBboxPatch(
            (x, y),
            w,
            h,
            boxstyle="round,pad=0.018,rounding_size=0.02",
            facecolor=fc,
            edgecolor=ec,
            linewidth=1.0,
        )
        ax.add_patch(patch)
        title_y = y + h - 0.032
        divider_y = y + h - 0.082
        body_y = y + (divider_y - y) * 0.52
        ax.text(x + w / 2, title_y, title, ha="center", va="top", fontsize=7.4, weight="bold")
        ax.plot([x + 0.025, x + w - 0.025], [divider_y, divider_y], color=ec, linewidth=0.45, alpha=0.28)
        ax.text(x + w / 2, body_y, body, ha="center", va="center", fontsize=5.8, linespacing=1.16)

    def arrow(start, end, color):
        ax.add_patch(FancyArrowPatch(start, end, arrowstyle="-|>", mutation_scale=11, color=color, linewidth=1.05))

    box(0.04, 0.39, 0.18, 0.23, "short reads", "trimmed reads\nN masks\nstrand ambiguity\nlocal errors", "#f3f4f6", "#6b7280")
    box(0.30, 0.69, 0.24, 0.21, "identity", "CK4 / CK5\nalignment\ndatabase indices", "#e5e7eb", COLORS["identity"])
    box(0.30, 0.41, 0.24, 0.21, "biochemical", "P summaries\nCK4+P\nperturbation stability", "#dbeafe", COLORS["property"])
    box(0.30, 0.13, 0.24, 0.21, "position", "CK4P-MSP\nfull-position upper bound\nlocal sensitivity", "#dcfce7", COLORS["msp"])
    box(0.68, 0.55, 0.24, 0.23, "diagnostic readouts", "paired stability\nmacro-F1 probes\nselective sensitivity", "#fef3c7", "#d97706")
    box(0.68, 0.20, 0.24, 0.21, "boundaries", "spaced-seed transfer\ncontext visibility\nARG/SNP limits", "#ede9fe", COLORS["boundary"])
    for start, end, color in [
        ((0.22, 0.505), (0.30, 0.795), COLORS["identity"]),
        ((0.22, 0.505), (0.30, 0.515), COLORS["property"]),
        ((0.22, 0.505), (0.30, 0.235), COLORS["msp"]),
        ((0.54, 0.795), (0.68, 0.665), COLORS["identity"]),
        ((0.54, 0.515), (0.68, 0.655), COLORS["property"]),
        ((0.54, 0.235), (0.68, 0.305), COLORS["msp"]),
    ]:
        arrow(start, end, color)
    ax.text(
        0.5,
        0.96,
        "Representation diagnostics before classification",
        ha="center",
        va="top",
        fontsize=8.6,
        weight="bold",
    )
    return fig


def figure2_compact_stability() -> plt.Figure:
    df = pd.read_csv(PROJECT_ROOT / "results/stage3/bootstrap_ci/stage3_compact_bootstrap_ci.csv")
    keep = ["ckmer5_count_l2", "cspaced_count_l2", "cspaced_property_l2", "hybrid_ckmer5_csp"]
    plot = df[df["representation"].isin(keep)].copy()
    plot["label"] = label_rep(plot["representation"])
    order = ["canonical 5-mer", "canonical spaced count", "CSP", "canonical 5-mer + CSP"]
    plot["label"] = pd.Categorical(plot["representation_label"], categories=order, ordered=True)
    plot = plot.sort_values("label")
    plot["family_color"] = [COLORS["identity"], COLORS["identity"], COLORS["property"], COLORS["csp"]]

    fig, axes = plt.subplots(1, 3, figsize=(7.2, 3.2), gridspec_kw={"width_ratios": [1, 1, 0.85]})
    barh_metric(axes[0], plot, "representation_label", "paired_cosine_mean_mean", "family_color", "A. Paired cosine", "higher is better")
    axes[0].set_xlim(0.9, 1.0)
    barh_metric(axes[1], plot, "representation_label", "l2_delta_mean_mean", "family_color", "B. L2 drift", "lower is better")
    barh_metric(axes[2], plot, "representation_label", "median_features", "family_color", "C. Feature dimension", "features")
    axes[2].set_xscale("log")
    axes[2].set_xlim(90, 850)
    axes[2].xaxis.set_major_locator(mticker.FixedLocator([100, 200, 500]))
    axes[2].xaxis.set_major_formatter(mticker.FixedFormatter(["100", "200", "500"]))
    axes[2].xaxis.set_minor_locator(mticker.NullLocator())
    axes[2].tick_params(axis="x", labelsize=6.2, pad=1)
    fig.suptitle("Biochemical side channels stabilize compact k-mer representations", y=1.02, fontsize=9.5, weight="bold")
    fig.tight_layout()
    return fig


def figure3_msp_tradeoff() -> plt.Figure:
    stability = pd.read_csv(PROJECT_ROOT / "results/stage3/position_property_ablation/compact_baseline_stability.csv")
    readout = pd.read_csv(PROJECT_ROOT / "results/stage3/position_property_ablation/compact_baseline_readout.csv")
    reps = ["ckmer4_count_l2", "ckmer4_property_l2", "ckmer4_property_multiscale_mean_l2", "ckmer5_count_l2"]
    stab = stability[stability["representation"].isin(reps)].groupby("representation", as_index=False).agg(
        paired_cosine=("paired_cosine_mean", "mean"),
        l2_drift=("l2_delta_mean", "mean"),
        features=("n_features", "median"),
    )
    read = readout[(readout["representation"].isin(reps)) & (readout["classifier"].eq("logistic"))].groupby(
        "representation", as_index=False
    ).agg(readout_macro_f1=("macro_f1", "mean"))
    plot = stab.merge(read, on="representation", how="left")
    plot["label"] = label_rep(plot["representation"])
    colors = {"CK4": COLORS["identity"], "CK4+P": COLORS["property"], "CK4P-MSP": COLORS["msp"], "CK5": COLORS["boundary"]}
    fig, axes = plt.subplots(1, 2, figsize=(7.0, 3.55))
    for _, row in plot.iterrows():
        label = row["label"]
        axes[0].scatter(row["features"], row["paired_cosine"], s=80, color=colors.get(label, COLORS["muted"]), edgecolor=COLORS["ink"], label=label)
        axes[1].scatter(row["features"], row["readout_macro_f1"], s=80, color=colors.get(label, COLORS["muted"]), edgecolor=COLORS["ink"], label=label)
    for ax, title, ylabel in [
        (axes[0], "A. Stability versus dimension", "mean paired cosine"),
        (axes[1], "B. Readout versus dimension", "mean macro-F1"),
    ]:
        ax.set_xlim(90, 560)
        ax.xaxis.set_major_locator(mticker.FixedLocator([136, 222, 512]))
        ax.xaxis.set_major_formatter(mticker.FixedFormatter(["136", "222", "512"]))
        ax.xaxis.set_minor_locator(mticker.NullLocator())
        ax.set_xlabel("feature dimension")
        ax.set_ylabel(ylabel)
        ax.set_title(title, loc="left", weight="bold")
        ax.grid(True, color="#e5e7eb", linewidth=0.6)
    handles, labels = axes[1].get_legend_handles_labels()
    # De-duplicate point handles and keep the legend outside the data region.
    unique = dict(zip(labels, handles))
    fig.legend(
        unique.values(),
        unique.keys(),
        frameon=False,
        loc="lower center",
        bbox_to_anchor=(0.52, 0.02),
        ncol=4,
        borderaxespad=0.0,
        title="Representation",
        handletextpad=0.4,
        columnspacing=1.0,
    )
    fig.suptitle("CK4P-MSP provides a compact stability/readability trade-off", y=1.02, fontsize=9.5, weight="bold")
    fig.tight_layout(rect=(0, 0.18, 1, 0.98), w_pad=2.0)
    return fig


def figure4_external_probes() -> plt.Figure:
    art = pd.read_csv(PROJECT_ROOT / "results/stage3/bootstrap_ci/stage3_art_bootstrap_ci.csv")
    cami = pd.read_csv(PROJECT_ROOT / "results/stage3/bootstrap_ci/stage3_cami_macro_f1_bootstrap_ci.csv")
    art_keep = ["ckmer5_count_l2", "cspaced_count_l2", "cspaced_property_l2", "hybrid_ckmer5_csp"]
    art_plot = art[art["representation"].isin(art_keep)].copy()
    keep = ["ckmer5_count_l2", "cspaced_count_l2", "cspaced_property_l2", "hybrid_ckmer5_csp"]
    short_labels = {
        "canonical 5-mer": "CK5",
        "canonical spaced count": "spaced count",
        "CSP": "CSP",
        "canonical 5-mer + CSP": "CK5+CSP",
    }
    label_order = ["CK5", "spaced count", "CSP", "CK5+CSP"]
    cami_plot = cami[cami["task"].isin(["target_background", "label_probe"])].copy()
    cami_plot = cami_plot[cami_plot["representation"].isin(keep)]
    art_plot["short_label"] = art_plot["representation_label"].map(short_labels).fillna(art_plot["representation_label"])
    cami_plot["short_label"] = cami_plot["representation_label"].map(short_labels).fillna(cami_plot["representation_label"])
    fig, axes = plt.subplots(1, 3, figsize=(7.45, 3.45), gridspec_kw={"width_ratios": [1.0, 1.0, 1.0]})
    art_plot = art_plot.sort_values("paired_cosine_mean_mean", ascending=True)
    axes[0].barh(art_plot["short_label"], art_plot["paired_cosine_mean_mean"], color="#93c5fd", edgecolor=COLORS["ink"], linewidth=0.35)
    axes[0].set_xlim(0.8, 1.0)
    axes[0].set_xlabel("ART paired cosine")
    axes[0].set_title("A. ART stability", loc="left", weight="bold")
    axes[0].grid(axis="x", color="#e5e7eb", linewidth=0.6)
    pivot = cami_plot.pivot_table(index="short_label", columns="task", values="macro_f1_mean", aggfunc="mean").reindex(label_order)

    def draw_cami_panel(ax: plt.Axes, values: pd.Series, color: str, title: str) -> None:
        local = values.sort_values(ascending=True)
        ax.barh(local.index, local.values, color=color, edgecolor=COLORS["ink"], linewidth=0.35)
        ax.set_xlim(0, 0.8)
        ax.set_xlabel("CAMI macro-F1")
        ax.set_title(title, loc="left", weight="bold")
        ax.grid(axis="x", color="#e5e7eb", linewidth=0.6)
        for ypos, value in enumerate(local.values):
            ax.text(value + 0.015, ypos, f"{value:.2f}", va="center", fontsize=6.4, color=COLORS["ink"])

    draw_cami_panel(axes[1], pivot["target_background"], "#86efac", "B. Coarse readout")
    draw_cami_panel(axes[2], pivot["label_probe"], "#fca5a5", "C. Fine-label limit")
    fig.suptitle("ART supports stability consistency; CAMI readout remains task-limited", y=1.02, fontsize=9.0, weight="bold")
    fig.tight_layout(w_pad=2.0)
    return fig


def figure5_full_position() -> plt.Figure:
    df = pd.read_csv(PROJECT_ROOT / "results/stage3/fullmatrix_property_contribution_ci/fullmatrix_property_controlled_ci.csv")
    plot = df[df["task"].eq("motif_jitter_position")].copy()
    plot = plot.sort_values("macro_f1_mean", ascending=True)
    def family(label: str) -> str:
        lower = label.lower()
        if "multi-scale" in lower:
            return "compact MSP"
        if "property" in lower:
            return "position + property"
        if "one-hot" in lower or "rope" in lower:
            return "position identity"
        return "k-mer identity"

    family_colors = {
        "compact MSP": COLORS["msp"],
        "position + property": "#fca5a5",
        "position identity": "#c4b5fd",
        "k-mer identity": COLORS["identity"],
    }
    plot["family"] = plot["representation_label"].map(family)
    colors = plot["family"].map(family_colors).tolist()
    fig, axes = plt.subplots(1, 2, figsize=(7.65, 3.75), gridspec_kw={"width_ratios": [1.2, 1.05]})
    axes[0].barh(plot["representation_label"], plot["macro_f1_mean"], color=colors, edgecolor=COLORS["ink"], linewidth=0.35)
    axes[0].set_xlabel("macro-F1")
    axes[0].set_title("A. Readout", loc="left", weight="bold", pad=4)
    axes[0].grid(axis="x", color="#e5e7eb", linewidth=0.6)
    for family_name, family_df in plot.groupby("family", sort=False):
        axes[1].scatter(
            family_df["mean_features"],
            family_df["macro_f1_mean"],
            s=55,
            color=family_colors[family_name],
            edgecolor=COLORS["ink"],
            label=family_name,
        )
    axes[1].set_xscale("log")
    axes[1].xaxis.set_major_locator(mticker.FixedLocator([100, 300, 1000]))
    axes[1].xaxis.set_major_formatter(mticker.FixedFormatter(["100", "300", "1000"]))
    axes[1].xaxis.set_minor_locator(mticker.NullLocator())
    axes[1].set_xlabel("feature dimension")
    axes[1].set_ylabel("macro-F1")
    axes[1].set_title("B. Cost", loc="left", weight="bold", pad=4)
    axes[1].grid(True, color="#e5e7eb", linewidth=0.6)
    handles, labels = axes[1].get_legend_handles_labels()
    fig.legend(
        handles,
        labels,
        frameon=False,
        loc="lower center",
        bbox_to_anchor=(0.58, 0.02),
        ncol=2,
        handletextpad=0.4,
        columnspacing=1.0,
    )
    fig.suptitle("Full-position matrices expose positional information at high dimensional cost", y=1.02, fontsize=9.5, weight="bold")
    fig.tight_layout(rect=(0, 0.22, 1, 0.96), w_pad=3.2)
    return fig


def figure6_local_mutation() -> plt.Figure:
    # Reuse the dedicated asset logic to keep the user's legend-based right panel.
    import scripts.generate_local_mutation_sensitivity_assets as local_assets

    local_assets.configure()
    summary, readout = local_assets.load_data()
    table = local_assets.aggregate(summary, readout)
    local_assets.save_table(table)
    return local_assets.make_figure(table)


def figure7_spaced_seed_transfer() -> plt.Figure:
    df = pd.read_csv(PROJECT_ROOT / "results/stage3/spaced_pattern_sanity/spaced_pattern_sanity_stability.csv")
    prop = df[(df["add_property"]) & (df["role"].eq("four-position scan"))].copy()
    if prop.empty:
        prop = df[(df["add_property"]) & (df["cardinality"].eq(4))].copy()
    focus = prop[prop["length"].isin([69, 75])].copy()
    pivot = focus.pivot_table(index="pattern", columns="condition_label", values="paired_cosine_mean", aggfunc="mean")
    pivot = pivot.sort_index()
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 3.25), gridspec_kw={"width_ratios": [1.05, 0.95]})
    im = axes[0].imshow(pivot.values, aspect="auto", cmap="YlGnBu", vmin=np.nanmin(pivot.values), vmax=np.nanmax(pivot.values))
    axes[0].set_xticks(np.arange(len(pivot.columns)))
    axes[0].set_xticklabels(pivot.columns, rotation=25, ha="right")
    axes[0].set_yticks(np.arange(len(pivot.index)))
    axes[0].set_yticklabels(pivot.index)
    axes[0].set_title("A. Four-position dense-feature stability", loc="left", weight="bold")
    cbar = fig.colorbar(im, ax=axes[0], fraction=0.046, pad=0.04)
    cbar.set_label("paired cosine")
    best = focus.groupby(["condition_label", "length"], as_index=False).apply(lambda x: x.loc[x["paired_cosine_mean"].idxmax()]).reset_index(drop=True)
    counts = best["pattern"].value_counts().sort_values(ascending=True)
    axes[1].barh(counts.index, counts.values, color="#fbbf24", edgecolor=COLORS["ink"], linewidth=0.4)
    axes[1].set_xlabel("wins across condition-length cells")
    axes[1].set_title("B. Best pattern is not fixed spaced seed", loc="left", weight="bold")
    axes[1].grid(axis="x", color="#e5e7eb", linewidth=0.6)
    fig.suptitle("Spaced-seed priors transfer in a regime-specific manner", y=1.02, fontsize=9.5, weight="bold")
    fig.tight_layout()
    return fig


def figure8_boundaries() -> plt.Figure:
    attention = pd.read_csv(PROJECT_ROOT / "results/stage2/attention_breakpoint/attention_breakpoint_change_points.csv")
    arg = pd.read_csv(PROJECT_ROOT / "results/stage2/arg_snp_boundary/arg_snp_readout.csv")
    arg_focus = (
        arg[(arg["classifier"].eq("logistic")) & (arg["condition"].eq("clean"))]
        .groupby(["task", "representation"], as_index=False)
        .agg(macro_f1=("macro_f1", "mean"), features=("n_features", "median"))
    )
    task_order = ["arg_family", "arg_allele", "resistance_snp", "functional_site", "gene_context"]
    arg_focus = arg_focus[arg_focus["task"].isin(task_order)]
    best = arg_focus.sort_values("macro_f1", ascending=False).groupby("task", as_index=False).head(1)
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 3.25))
    axes[0].plot(attention["motif_position"], attention["first_length_pair_visible_ge_0_5"], marker="o", color=COLORS["boundary"], linewidth=1.5)
    axes[0].plot([attention["motif_position"].min(), attention["motif_position"].max()], [attention["motif_position"].min(), attention["motif_position"].max()], linestyle="--", color=COLORS["muted"], linewidth=1)
    axes[0].set_xlabel("motif position")
    axes[0].set_ylabel("first length with pair visibility >= 0.5")
    axes[0].set_title("A. Context is bounded by read visibility", loc="left", weight="bold")
    axes[0].grid(True, color="#e5e7eb", linewidth=0.6)
    best["task"] = pd.Categorical(best["task"], categories=task_order, ordered=True)
    best = best.sort_values("task")
    axes[1].barh(best["task"].astype(str), best["macro_f1"], color="#c4b5fd", edgecolor=COLORS["ink"], linewidth=0.4)
    axes[1].set_xlim(0, 1.05)
    axes[1].set_xlabel("best clean-read logistic macro-F1")
    axes[1].set_title("B. Functional readouts remain task-specific", loc="left", weight="bold")
    axes[1].grid(axis="x", color="#e5e7eb", linewidth=0.6)
    fig.suptitle("Context and allele-level probes define where representation stability stops", y=1.02, fontsize=9.4, weight="bold")
    fig.tight_layout()
    return fig


def main() -> None:
    configure()
    figures = [
        ("nature_fig1_framework", figure1_framework),
        ("nature_fig2_compact_stability", figure2_compact_stability),
        ("nature_fig3_ck4p_msp_tradeoff", figure3_msp_tradeoff),
        ("nature_fig4_external_probes", figure4_external_probes),
        ("nature_fig5_full_position_upper_bound", figure5_full_position),
        ("nature_fig6_local_mutation_sensitivity", figure6_local_mutation),
        ("nature_fig7_spaced_seed_transfer", figure7_spaced_seed_transfer),
        ("nature_fig8_context_arg_boundaries", figure8_boundaries),
    ]
    for name, builder in figures:
        fig = builder()
        save(fig, name)
    print("Wrote Nature-style main manuscript figures")


if __name__ == "__main__":
    main()

