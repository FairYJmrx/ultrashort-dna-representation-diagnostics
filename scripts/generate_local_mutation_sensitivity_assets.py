from __future__ import annotations

import os
from pathlib import Path

os.environ.setdefault("MPLBACKEND", "Agg")

import matplotlib as mpl
import matplotlib.pyplot as plt
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RESULT_DIR = PROJECT_ROOT / "results" / "stage3" / "local_mutation_sensitivity"
RESULT_FIGS = PROJECT_ROOT / "results" / "stage3" / "figures"
MANUSCRIPT_FIGS = PROJECT_ROOT / "manuscript" / "figures"
MANUSCRIPT_TABLES = PROJECT_ROOT / "manuscript" / "tables"

LABELS = {
    "ckmer4_count_l2": "CK4 count",
    "ckmer4_property_l2": "CK4+P global",
    "ckmer4_property_multiscale_mean_l2": "CK4P-MSP",
    "ckmer4_property_multiscale_l2": "CK4P-MSP + std",
    "ckmer5_count_l2": "CK5 count",
    "property_channels": "position property channels",
    "one_hot": "position one-hot",
    "base_property": "one-hot + property",
    "rope_property": "RoPE property",
    "rope_onehot": "RoPE one-hot",
    "kmer_property": "position k-mer property",
    "cspaced_property_l2": "CSP control",
}

ORDER = [
    "CK4 count",
    "CK4+P global",
    "CK4P-MSP",
    "CSP control",
    "position one-hot",
    "position property channels",
    "one-hot + property",
    "position k-mer property",
]

COLORS = {
    "CK4 count": "#6b7280",
    "CK4+P global": "#2563eb",
    "CK4P-MSP": "#16a34a",
    "CSP control": "#d97706",
    "position one-hot": "#7c3aed",
    "position property channels": "#dc2626",
    "one-hot + property": "#db2777",
    "position k-mer property": "#0891b2",
}


def configure() -> None:
    mpl.rcParams.update(
        {
            "font.family": "sans-serif",
            "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans", "sans-serif"],
            "svg.fonttype": "none",
            "pdf.fonttype": 42,
            "font.size": 8,
            "axes.titlesize": 9,
            "axes.labelsize": 8,
            "xtick.labelsize": 7,
            "ytick.labelsize": 7,
            "figure.facecolor": "white",
        }
    )


def load_data() -> tuple[pd.DataFrame, pd.DataFrame]:
    summary = pd.read_csv(RESULT_DIR / "local_mutation_sensitivity_summary.csv")
    readout = pd.read_csv(RESULT_DIR / "local_mutation_delta_readout.csv")
    summary["label"] = summary["representation"].map(LABELS).fillna(summary["representation"])
    readout["label"] = readout["representation"].map(LABELS).fillna(readout["representation"])
    return summary, readout


def aggregate(summary: pd.DataFrame, readout: pd.DataFrame) -> pd.DataFrame:
    distance = summary.groupby(["representation", "label"], as_index=False).agg(
        noise_l2=("noise_l2_mean", "mean"),
        local_l2=("local_l2_mean", "mean"),
        local_minus_noise_l2=("local_minus_noise_l2_mean", "mean"),
        sensitivity_ratio=("selective_sensitivity_ratio_mean", "mean"),
        n_features=("n_features", "mean"),
    )
    readout_logistic = readout[(readout["split"].eq("5fold_cv")) & (readout["classifier"].eq("logistic"))]
    readout_agg = readout_logistic.groupby(["representation"], as_index=False).agg(
        delta_macro_f1=("macro_f1", "mean"),
        delta_accuracy=("accuracy", "mean"),
    )
    merged = distance.merge(readout_agg, on="representation", how="left")
    merged = merged[merged["label"].isin(ORDER)].copy()
    merged["label"] = pd.Categorical(merged["label"], categories=ORDER, ordered=True)
    return merged.sort_values("label").reset_index(drop=True)


def save_table(table: pd.DataFrame) -> None:
    MANUSCRIPT_TABLES.mkdir(parents=True, exist_ok=True)
    out = table.copy()
    out["n_features"] = out["n_features"].round(0).astype(int)
    for col in ["noise_l2", "local_l2", "local_minus_noise_l2", "sensitivity_ratio", "delta_macro_f1"]:
        out[col] = out[col].map(lambda x: f"{x:.3f}")
    out = out[
        [
            "label",
            "noise_l2",
            "local_l2",
            "local_minus_noise_l2",
            "sensitivity_ratio",
            "delta_macro_f1",
            "n_features",
        ]
    ].rename(
        columns={
            "label": "representation",
            "noise_l2": "noise L2",
            "local_l2": "local mutation L2",
            "local_minus_noise_l2": "local - noise L2",
            "sensitivity_ratio": "sensitivity ratio",
            "delta_macro_f1": "delta-readout macro-F1",
            "n_features": "features",
        }
    )
    out.to_csv(MANUSCRIPT_TABLES / "stage3_table_local_mutation_sensitivity.csv", index=False, encoding="utf-8-sig")
    (MANUSCRIPT_TABLES / "stage3_table_local_mutation_sensitivity.md").write_text(
        out.to_markdown(index=False) + "\n",
        encoding="utf-8",
    )


def make_figure(table: pd.DataFrame) -> plt.Figure:
    labels = table["label"].astype(str).tolist()
    y = list(range(len(labels)))
    colors = [COLORS.get(label, "#4b5563") for label in labels]

    fig, axes = plt.subplots(1, 2, figsize=(8.4, 3.8), gridspec_kw={"width_ratios": [1.05, 1.25]})
    ax = axes[0]
    ax.barh(y, table["sensitivity_ratio"], color=colors, edgecolor="#111827", linewidth=0.4)
    ax.axvline(1.0, color="#111827", linewidth=0.9, linestyle="--")
    ax.set_yticks(y)
    ax.set_yticklabels(labels)
    ax.invert_yaxis()
    ax.set_xlabel("local-mutation / random-noise L2")
    ax.set_title("A. Distance-based selective sensitivity")
    ax.text(1.01, -0.35, "local change moves farther", fontsize=6.4, color="#374151")
    ax.grid(axis="x", color="#e5e7eb", linewidth=0.6)
    ax.set_axisbelow(True)

    ax = axes[1]
    sizes = 35 + 70 * (table["n_features"] / table["n_features"].max())
    for _, row in table.iterrows():
        label = str(row["label"])
        ax.scatter(
            row["n_features"],
            row["delta_macro_f1"],
            s=float(35 + 70 * (row["n_features"] / table["n_features"].max())),
            c=COLORS.get(label, "#4b5563"),
            edgecolor="#111827",
            linewidth=0.5,
            alpha=0.92,
            label=label,
        )
    handles, legend_labels = ax.get_legend_handles_labels()
    ax.legend(
        handles,
        legend_labels,
        loc="center left",
        bbox_to_anchor=(1.02, 0.5),
        frameon=False,
        fontsize=6.3,
        handletextpad=0.4,
        borderaxespad=0.0,
        labelspacing=0.55,
    )
    ax.set_xscale("log")
    ax.set_xlabel("feature dimension (log scale)")
    ax.set_ylabel("noise-vs-local delta-readout macro-F1")
    ax.set_title("B. Readable local-change signal versus dimension")
    ax.grid(True, color="#e5e7eb", linewidth=0.6)
    ax.set_axisbelow(True)
    ax.set_ylim(0.55, 1.03)
    ax.set_xlim(100, 2600)

    fig.suptitle(
        "Local biochemical/positional mutation sensitivity is distinct from perturbation invariance",
        fontsize=9.5,
        weight="bold",
        y=1.02,
    )
    fig.tight_layout(rect=(0, 0.00, 0.88, 0.98))
    return fig


def save_figure(fig: plt.Figure, name: str) -> None:
    RESULT_FIGS.mkdir(parents=True, exist_ok=True)
    MANUSCRIPT_FIGS.mkdir(parents=True, exist_ok=True)
    for folder in [RESULT_FIGS, MANUSCRIPT_FIGS]:
        fig.savefig(folder / f"{name}.png", dpi=360, bbox_inches="tight")
        fig.savefig(folder / f"{name}.svg", bbox_inches="tight")
        fig.savefig(folder / f"{name}.pdf", bbox_inches="tight")
        fig.savefig(folder / f"{name}.tiff", dpi=600, bbox_inches="tight")


def main() -> None:
    configure()
    summary, readout = load_data()
    table = aggregate(summary, readout)
    save_table(table)
    fig = make_figure(table)
    save_figure(fig, "stage3_fig_local_mutation_sensitivity")
    plt.close(fig)
    print("Wrote local mutation sensitivity figure and manuscript table")


if __name__ == "__main__":
    main()
