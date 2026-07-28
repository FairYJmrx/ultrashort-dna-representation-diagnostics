from __future__ import annotations

import json
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


PROJECT_ROOT = _find_project_root(Path(__file__).resolve())
RESULT_DIR = PROJECT_ROOT / "results" / "stage3" / "contract_v2" / "cami2_marine_stability"
FIGURE_DIR = PROJECT_ROOT / "figures" / "contract_v2"


LABELS = {
    "ck4": "CK4",
    "ck4_p": "CK4+P",
    "ck4p_msp": "CK4P-MSP\n(222-dim)",
    "ckmer5_count_l2": "CK5",
}

ORDER = [
    "CK4",
    "CK5",
    "CK4+P",
    "CK4P-MSP\n(222-dim)",
]

CONDITION_LABELS = {
    "N_3pct": "N mask\n3%",
    "substitution_1pct": "Substitution\n1%",
    "substitution_1pct_N_3pct": "Substitution 1%\n+ N mask 3%",
}


def configure_matplotlib() -> None:
    mpl.rcParams.update(
        {
            "font.family": "sans-serif",
            "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans", "sans-serif"],
            "svg.fonttype": "none",
            "pdf.fonttype": 42,
            "font.size": 7,
            "axes.spines.right": False,
            "axes.spines.top": False,
            "axes.linewidth": 0.8,
            "legend.frameon": False,
        }
    )


def pivot_metric(df: pd.DataFrame, metric: str) -> pd.DataFrame:
    d = df.copy()
    d["method"] = d["representation"].map(LABELS)
    d = d[d["method"].notna()]
    out = (
        d.groupby(["method", "condition"], as_index=False)[metric]
        .mean()
        .pivot(index="method", columns="condition", values=metric)
        .reindex(ORDER)
    )
    return out[["N_3pct", "substitution_1pct", "substitution_1pct_N_3pct"]]


def main() -> None:
    configure_matplotlib()
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)

    stability = pd.read_csv(RESULT_DIR / "cami2_marine_stability.csv")
    meta = json.loads((RESULT_DIR / "cami2_marine_lightweight_probe_run.json").read_text(encoding="utf-8"))
    stability["method"] = stability["representation"].map(LABELS)
    stability = stability[stability["method"].notna()].copy()

    l2 = pivot_metric(stability, "l2_delta_mean")
    cos = pivot_metric(stability, "paired_cosine_mean")
    best = (
        stability.sort_values(["condition", "length", "l2_delta_mean"])
        .groupby(["condition", "length"], as_index=False)
        .first()
    )
    best["best_is_ck4pmsp"] = best["representation"].eq("ck4p_msp")
    best_counts = best.groupby("condition")["best_is_ck4pmsp"].sum().reindex(l2.columns)

    fig = plt.figure(figsize=(7.2, 6.35), constrained_layout=True)
    gs = fig.add_gridspec(4, 1, height_ratios=[1.35, 0.26, 1.15, 0.8])
    ax0 = fig.add_subplot(gs[0, 0])
    legend_ax = fig.add_subplot(gs[1, 0])
    ax1 = fig.add_subplot(gs[2, 0])
    ax2 = fig.add_subplot(gs[3, 0])
    legend_ax.axis("off")

    # Panel A: mean L2 drift by perturbation.
    x = np.arange(len(l2.index))
    colors = ["#8aa6c1", "#c69c72", "#7aa974"]
    markers = ["o", "s", "^"]
    for col, color, marker in zip(l2.columns, colors, markers):
        ax0.plot(
            x,
            l2[col].values,
            color=color,
            marker=marker,
            markersize=4.2,
            linewidth=1.5,
            label=CONDITION_LABELS[col].replace("\n", " "),
        )
    ax0.set_xticks(x)
    ax0.set_xticklabels(l2.index, rotation=25, ha="right")
    ax0.set_ylabel("Mean L2 drift")
    ax0.set_title("A  External CAMI II marine stability probe", loc="left", fontweight="bold")
    handles, labels = ax0.get_legend_handles_labels()
    legend_ax.legend(
        handles,
        labels,
        title="Perturbation",
        ncols=3,
        loc="center",
        frameon=False,
        handlelength=1.4,
        columnspacing=1.1,
    )
    ax0.grid(axis="y", color="#e5e5e5", linewidth=0.6)

    # Panel B: paired cosine heatmap.
    im = ax1.imshow(cos.values, aspect="auto", cmap="YlGnBu", vmin=0.90, vmax=1.00)
    ax1.set_yticks(np.arange(len(cos.index)))
    ax1.set_yticklabels(cos.index)
    ax1.set_xticks(np.arange(len(cos.columns)))
    ax1.set_xticklabels([CONDITION_LABELS[c].replace("\n", " ") for c in cos.columns], rotation=0, ha="center")
    ax1.set_title("B  Paired cosine", loc="left", fontweight="bold")
    cbar = fig.colorbar(im, ax=ax1, fraction=0.046, pad=0.02)
    cbar.ax.set_ylabel("Mean cosine", rotation=270, labelpad=10)
    for i in range(cos.shape[0]):
        for j in range(cos.shape[1]):
            value = cos.values[i, j]
            text_color = "white" if value >= 0.975 else "#1f2933"
            ax1.text(j, i, f"{value:.3f}", ha="center", va="center", fontsize=5.8, color=text_color)

    # Panel C: best-by-cell count.
    ax2.bar(np.arange(len(best_counts)), best_counts.values, color="#557a95", width=0.55)
    ax2.set_xticks(np.arange(len(best_counts)))
    ax2.set_xticklabels([CONDITION_LABELS[c].replace("\n", " ") for c in best_counts.index], rotation=0, ha="center")
    ax2.set_ylim(0, 3.25)
    ax2.set_yticks([0, 1, 2, 3])
    ax2.set_ylabel("Best cells\n(out of 3)")
    ax2.set_title("C  Consistency across 69/75/100 bp", loc="left", fontweight="bold")
    ax2.grid(axis="y", color="#e5e5e5", linewidth=0.6)
    for xpos, value in enumerate(best_counts.values):
        ax2.text(xpos, value + 0.06, f"{int(value)}/3", ha="center", va="bottom", fontsize=7)

    fig.suptitle(
        "Supplementary Figure S10 | CAMI II marine subset probe\n"
        f"n={meta['n_clean_reads']:,} reads; {meta['n_probe_rows']:,} length/condition rows; unlabeled perturbation-stability probe",
        x=0.02,
        ha="left",
        fontsize=8.5,
        fontweight="bold",
    )
    base = FIGURE_DIR / "supplementary_figure_s10_cami2_marine_probe"
    fig.savefig(base.with_suffix(".svg"), bbox_inches="tight")
    fig.savefig(base.with_suffix(".pdf"), bbox_inches="tight")
    fig.savefig(base.with_suffix(".png"), dpi=600, bbox_inches="tight")
    plt.close(fig)

    source = stability[
        [
            "length",
            "condition",
            "method",
            "representation",
            "n_pairs",
            "n_features",
            "paired_cosine_mean",
            "paired_cosine_p05",
            "l2_delta_mean",
            "l2_delta_p95",
            "retrieval_top1",
        ]
    ].sort_values(["condition", "length", "method"])
    source.to_csv(RESULT_DIR / "cami2_marine_figure_source.csv", index=False, encoding="utf-8-sig")
    print(f"Wrote {base.with_suffix('.png')}")


if __name__ == "__main__":
    main()

