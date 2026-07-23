from __future__ import annotations

import os
from pathlib import Path

os.environ.setdefault("MPLBACKEND", "Agg")

import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch


def _find_project_root(start: Path) -> Path:
    for candidate in [start.parent, *start.parents]:
        if (candidate / "methods").is_dir() and (candidate / "configs").is_dir():
            return candidate
    raise RuntimeError("Could not locate the release repository root.")


PROJECT_ROOT = _find_project_root(Path(__file__).resolve())
MANUSCRIPT_FIGS = PROJECT_ROOT / "manuscript" / "figures"
RESULT_FIGS = PROJECT_ROOT / "results" / "stage3" / "figures"


def configure() -> None:
    mpl.rcParams.update(
        {
            "font.family": "sans-serif",
            "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans", "sans-serif"],
            "svg.fonttype": "none",
            "pdf.fonttype": 42,
            "font.size": 7,
            "figure.facecolor": "white",
        }
    )


def add_box(ax, xy, width, height, title, body, face, edge="#374151"):
    x, y = xy
    patch = FancyBboxPatch(
        (x, y),
        width,
        height,
        boxstyle="round,pad=0.022,rounding_size=0.030",
        linewidth=1.15,
        facecolor=face,
        edgecolor=edge,
    )
    ax.add_patch(patch)
    ax.text(
        x + width / 2,
        y + height - 0.060,
        title,
        ha="center",
        va="top",
        color="#111827",
        weight="bold",
        fontsize=7.5,
    )
    ax.text(
        x + width / 2,
        y + height * 0.40,
        body,
        ha="center",
        va="center",
        color="#111827",
        fontsize=6.1,
        linespacing=1.35,
    )


def add_arrow(ax, start, end, color, rad=0.0):
    ax.add_patch(
        FancyArrowPatch(
            start,
            end,
            arrowstyle="-|>",
            mutation_scale=13,
            linewidth=1.25,
            color=color,
            connectionstyle=f"arc3,rad={rad}",
        )
    )


def evidence_architecture_figure() -> plt.Figure:
    fig, ax = plt.subplots(figsize=(8.4, 3.35))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    add_box(
        ax,
        (0.055, 0.365),
        0.205,
        0.29,
        "Raw short reads",
        "69/75 bp mNGS-like reads\nN-masked, trimmed or\nlocally mismatched",
        "#f3f4f6",
    )
    add_box(
        ax,
        (0.350, 0.650),
        0.245,
        0.255,
        "Exact identity evidence",
        "canonical k-mer\nalignment\ndatabase indices",
        "#dbeafe",
        edge="#2563eb",
    )
    add_box(
        ax,
        (0.350, 0.110),
        0.245,
        0.275,
        "Compact side channel",
        "CK4 + biochemical P\nmulti-scale property pooling\nspaced seed controls",
        "#dcfce7",
        edge="#16a34a",
    )
    add_box(
        ax,
        (0.720, 0.355),
        0.245,
        0.31,
        "Layered readout",
        "probe model\nconfidence audit\nQC/stability side channel",
        "#fef3c7",
        edge="#d97706",
    )

    add_arrow(ax, (0.260, 0.530), (0.350, 0.775), color="#2563eb", rad=0.10)
    add_arrow(ax, (0.260, 0.485), (0.350, 0.260), color="#16a34a", rad=-0.08)
    add_arrow(ax, (0.595, 0.770), (0.720, 0.535), color="#2563eb", rad=-0.05)
    add_arrow(ax, (0.595, 0.245), (0.720, 0.470), color="#16a34a", rad=0.05)

    ax.text(
        0.51,
        0.970,
        "Short-read representation separates exact identity evidence from compact biochemical and position-aware side channels.",
        ha="center",
        va="top",
        fontsize=7.2,
        weight="bold",
        color="#111827",
    )
    ax.text(
        0.51,
        0.035,
        "Full position encodings are used as upper-bound diagnostics, not as the primary clinical classifier.",
        ha="center",
        va="bottom",
        fontsize=6.1,
        color="#4b5563",
    )
    return fig


def save_all(fig: plt.Figure, name: str) -> None:
    MANUSCRIPT_FIGS.mkdir(parents=True, exist_ok=True)
    RESULT_FIGS.mkdir(parents=True, exist_ok=True)
    for folder in [MANUSCRIPT_FIGS, RESULT_FIGS]:
        fig.savefig(folder / f"{name}.png", dpi=360, bbox_inches="tight")
        fig.savefig(folder / f"{name}.svg", bbox_inches="tight")
        fig.savefig(folder / f"{name}.pdf", bbox_inches="tight")
        fig.savefig(folder / f"{name}.tiff", dpi=600, bbox_inches="tight")


def main() -> None:
    configure()
    fig = evidence_architecture_figure()
    save_all(fig, "stage3_fig_layered_evidence_architecture")
    plt.close(fig)
    print("Wrote non-overlapping stage3_fig_layered_evidence_architecture assets")


if __name__ == "__main__":
    main()

