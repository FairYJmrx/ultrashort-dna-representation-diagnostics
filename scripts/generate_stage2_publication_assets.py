from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
STAGE2 = PROJECT_ROOT / "results" / "stage2"
ASSETS = STAGE2 / "publication_assets"
ASSET_FIGS = ASSETS / "figures"
ASSET_TABLES = ASSETS / "tables"
MANUSCRIPT = PROJECT_ROOT / "manuscript"
MS_FIGS = MANUSCRIPT / "figures"
MS_TABLES = MANUSCRIPT / "tables"


REP_LABELS = {
    "ckmer5_count_l2": "Canonical 5-mer",
    "ckmer7_count_l2": "Canonical 7-mer",
    "cspaced_count_l2": "Canonical spaced seed",
    "cspaced_property_l2": "CSP",
    "hybrid_ckmer5_csp": "Canonical 5-mer + CSP",
    "hybrid_ckmer7_csp": "Canonical 7-mer + CSP",
}

REP_COLORS = {
    "ckmer5_count_l2": "#3b5b92",
    "ckmer7_count_l2": "#8a4f7d",
    "cspaced_count_l2": "#b96f00",
    "cspaced_property_l2": "#1f8a70",
    "hybrid_ckmer5_csp": "#2f6f9f",
    "hybrid_ckmer7_csp": "#6f7f2f",
}

CONDITION_LABELS = {
    "substitution_1pct": "1% substitution",
    "N_3pct": "3% N mask",
    "trim_5bp": "5-bp trim",
    "substitution_1pct_N_3pct": "1% substitution + 3% N",
    "short_indel": "Short indel",
    "local_mismatch_6bp": "6-bp local mismatch",
    "clean": "Clean",
}


def load_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    return pd.read_csv(path)


def ensure_dirs() -> None:
    for path in [ASSETS, ASSET_FIGS, ASSET_TABLES, MS_FIGS, MS_TABLES]:
        path.mkdir(parents=True, exist_ok=True)


def rep_label(name: str) -> str:
    return REP_LABELS.get(name, name)


def condition_label(name: str) -> str:
    return CONDITION_LABELS.get(name, name)


def write_table(df: pd.DataFrame, name: str, floatfmt: str = ".3f") -> None:
    csv_path = ASSET_TABLES / f"{name}.csv"
    md_path = ASSET_TABLES / f"{name}.md"
    ms_md_path = MS_TABLES / f"{name}.md"
    df.to_csv(csv_path, index=False, encoding="utf-8-sig")
    md = df.to_markdown(index=False, floatfmt=floatfmt)
    md_path.write_text(md + "\n", encoding="utf-8")
    ms_md_path.write_text(md + "\n", encoding="utf-8")


def save_figure(fig: plt.Figure, name: str) -> None:
    for folder in [ASSET_FIGS, MS_FIGS]:
        fig.savefig(folder / f"{name}.png", dpi=260, bbox_inches="tight")


def set_style() -> None:
    plt.rcParams.update(
        {
            "font.size": 9,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.grid": True,
            "grid.alpha": 0.22,
            "figure.facecolor": "white",
            "axes.facecolor": "white",
            "legend.frameon": False,
        }
    )


def format_length(length: int | float) -> str:
    value = int(length)
    return "PE150 proxy" if value == 300 else f"{value} bp"


def format_length_tick(length: int | float) -> str:
    value = int(length)
    return "PE150\nproxy" if value == 300 else f"{value}\nbp"


def load_inputs() -> dict[str, pd.DataFrame]:
    return {
        "stability": load_csv(STAGE2 / "representation_grid" / "stability_grid.csv"),
        "readout": load_csv(STAGE2 / "representation_grid" / "readout_grid.csv"),
        "csp_ablation": load_csv(STAGE2 / "csp_ablation" / "csp_ablation_deltas.csv"),
        "arg_stability": load_csv(STAGE2 / "arg_snp_boundary" / "arg_snp_stability.csv"),
        "arg_readout": load_csv(STAGE2 / "arg_snp_boundary" / "arg_snp_readout.csv"),
        "attention": load_csv(STAGE2 / "attention_breakpoint" / "attention_breakpoint_results.csv"),
        "attention_cp": load_csv(STAGE2 / "attention_breakpoint" / "attention_breakpoint_change_points.csv"),
        "param_stability": load_csv(STAGE2 / "parameter_sensitivity" / "parameter_stability_metrics.csv"),
        "param_readout": load_csv(STAGE2 / "parameter_sensitivity" / "parameter_classification_probes.csv"),
    }


def plot_stability_grid(stability: pd.DataFrame) -> dict[str, object]:
    if stability.empty:
        return {}

    reps = [
        "ckmer5_count_l2",
        "ckmer7_count_l2",
        "cspaced_count_l2",
        "cspaced_property_l2",
        "hybrid_ckmer5_csp",
    ]
    focus_conditions = ["substitution_1pct", "N_3pct", "local_mismatch_6bp", "substitution_1pct_N_3pct"]
    focus = stability[
        stability["representation"].isin(reps) & stability["condition"].isin(focus_conditions)
    ].copy()
    focus["Representation"] = focus["representation"].map(rep_label)
    focus["Condition"] = focus["condition"].map(condition_label)
    focus["Read length"] = focus["length"].map(format_length)

    best = (
        stability.sort_values(["condition", "length", "paired_cosine_mean", "l2_delta_mean"], ascending=[True, True, False, True])
        .groupby(["condition", "length"], as_index=False)
        .first()
    )
    best_table = best[
        ["condition", "length", "representation", "paired_cosine_mean", "l2_delta_mean", "retrieval_top1", "n_features", "density"]
    ].copy()
    best_table["condition"] = best_table["condition"].map(condition_label)
    best_table["representation"] = best_table["representation"].map(rep_label)
    best_table = best_table.rename(
        columns={
            "condition": "Perturbation",
            "length": "Length",
            "representation": "Best representation",
            "paired_cosine_mean": "Mean paired cosine",
            "l2_delta_mean": "Mean L2 drift",
            "retrieval_top1": "Nearest-clean retrieval",
            "n_features": "Features",
            "density": "Density",
        }
    )
    write_table(best_table, "stage2_table_best_stability")

    hospital = focus[(focus["length"].isin([69, 75]))].copy()
    hospital_table = hospital[
        [
            "Condition",
            "length",
            "Representation",
            "paired_cosine_mean",
            "paired_cosine_p05",
            "l2_delta_mean",
            "l2_delta_p95",
            "retrieval_top1",
            "n_features",
            "density",
        ]
    ].rename(
        columns={
            "length": "Length",
            "paired_cosine_mean": "Mean paired cosine",
            "paired_cosine_p05": "5th percentile paired cosine",
            "l2_delta_mean": "Mean L2 drift",
            "l2_delta_p95": "95th percentile L2 drift",
            "retrieval_top1": "Nearest-clean retrieval",
            "n_features": "Features",
            "density": "Density",
        }
    )
    write_table(hospital_table, "stage2_table_hospital_69_75_focus")

    pivot = stability.pivot_table(index=["condition", "length"], columns="representation", values="paired_cosine_mean")
    comparisons = []
    for baseline in ["ckmer5_count_l2", "ckmer7_count_l2", "cspaced_count_l2", "hybrid_ckmer5_csp"]:
        if baseline not in pivot.columns or "cspaced_property_l2" not in pivot.columns:
            continue
        delta = (pivot["cspaced_property_l2"] - pivot[baseline]).dropna()
        comparisons.append(
            {
                "Comparison": f"CSP minus {rep_label(baseline)}",
                "Mean cosine gain": float(delta.mean()),
                "Minimum gain": float(delta.min()),
                "Maximum gain": float(delta.max()),
                "Wins": int((delta > 0).sum()),
                "Comparisons": int(len(delta)),
            }
        )
    comparison_table = pd.DataFrame(comparisons)
    write_table(comparison_table, "stage2_table_stability_gain_summary")

    fig, axes = plt.subplots(2, 2, figsize=(12.8, 7.4), sharex=True, sharey=True)
    for ax, condition in zip(axes.ravel(), focus_conditions):
        sub = focus[focus["condition"] == condition]
        for rep in reps:
            line = sub[sub["representation"] == rep].sort_values("length")
            ax.plot(
                line["length"],
                line["paired_cosine_mean"],
                marker="o",
                linewidth=2,
                color=REP_COLORS.get(rep, "#555555"),
                label=rep_label(rep),
            )
        ax.set_title(condition_label(condition))
        ax.set_ylim(0.80, 1.005)
        ax.set_xticks([69, 75, 100, 110, 125, 150, 300])
        ax.set_xticklabels([format_length_tick(x) for x in [69, 75, 100, 110, 125, 150, 300]], rotation=0)
        ax.set_ylabel("Paired cosine")
        ax.set_xlabel("Read length")
    handles, labels = axes[0, 0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower center", ncol=3)
    fig.suptitle("Clean-perturbed feature stability across read length")
    fig.tight_layout(rect=[0, 0.08, 1, 0.96])
    save_figure(fig, "stage2_fig_stability_grid")
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(8.5, 4.8))
    sub = hospital[hospital["condition"].isin(["N_3pct", "local_mismatch_6bp"])]
    width = 0.16
    x_labels = [f"{condition_label(c)}\n{l} bp" for c in ["N_3pct", "local_mismatch_6bp"] for l in [69, 75]]
    x = np.arange(len(x_labels))
    for i, rep in enumerate(reps):
        vals = []
        for condition in ["N_3pct", "local_mismatch_6bp"]:
            for length in [69, 75]:
                row = sub[(sub["condition"] == condition) & (sub["length"] == length) & (sub["representation"] == rep)]
                vals.append(float(row["l2_delta_mean"].iloc[0]) if not row.empty else np.nan)
        ax.bar(x + (i - 2) * width, vals, width=width, label=rep_label(rep), color=REP_COLORS.get(rep))
    ax.set_xticks(x)
    ax.set_xticklabels(x_labels)
    ax.set_ylabel("Mean L2 drift")
    ax.set_title("Hospital-like 69/75 bp perturbation drift")
    ax.legend(ncol=2)
    fig.tight_layout()
    save_figure(fig, "stage2_fig_hospital_69_75_l2")
    plt.close(fig)

    return {
        "stability_best_csp_count": int((best["representation"] == "cspaced_property_l2").sum()),
        "stability_best_total": int(len(best)),
        "csp_gain_summary": comparisons,
    }


def summarize_readout(readout: pd.DataFrame) -> dict[str, object]:
    if readout.empty:
        return {}
    reps = ["ckmer5_count_l2", "ckmer7_count_l2", "cspaced_count_l2", "cspaced_property_l2", "hybrid_ckmer5_csp"]
    readout = readout[readout["representation"].isin(reps)].copy()
    readout["Representation"] = readout["representation"].map(rep_label)
    readout["Condition"] = readout["condition"].map(condition_label)
    readout["Task"] = readout["task"].replace(
        {
            "within_genus_species": "Within-genus species",
            "target_background": "Target/background",
        }
    )

    best = (
        readout.sort_values(["task", "condition", "length", "macro_f1", "accuracy"], ascending=[True, True, True, False, False])
        .groupby(["task", "condition", "length"], as_index=False)
        .first()
    )
    best_table = best[
        ["Task", "Condition", "length", "Representation", "classifier", "macro_f1", "accuracy", "n_features"]
    ].rename(
        columns={
            "length": "Length",
            "classifier": "Best readout",
            "macro_f1": "Macro-F1",
            "accuracy": "Accuracy",
            "n_features": "Features",
        }
    )
    write_table(best_table, "stage2_table_best_readout")

    aggregate = (
        readout.groupby(["Task", "Representation"], as_index=False)
        .agg(Mean_macro_F1=("macro_f1", "mean"), Mean_accuracy=("accuracy", "mean"), Mean_features=("n_features", "mean"))
        .sort_values(["Task", "Mean_macro_F1"], ascending=[True, False])
    )
    write_table(aggregate, "stage2_table_readout_aggregate")

    fig, axes = plt.subplots(1, 2, figsize=(11, 4.2), sharey=True)
    for ax, task in zip(axes, ["Within-genus species", "Target/background"]):
        sub = aggregate[aggregate["Task"] == task]
        ax.bar(sub["Representation"], sub["Mean_macro_F1"], color=[REP_COLORS.get(k, "#666666") for k in readout["representation"].drop_duplicates()][: len(sub)])
        ax.set_title(task)
        ax.set_ylim(0, max(0.75, float(sub["Mean_macro_F1"].max()) + 0.1 if not sub.empty else 0.75))
        ax.tick_params(axis="x", rotation=35)
        ax.set_ylabel("Mean macro-F1")
    fig.suptitle("Lightweight readout probes remain task-dependent")
    fig.tight_layout(rect=[0, 0, 1, 0.92])
    save_figure(fig, "stage2_fig_readout_aggregate")
    plt.close(fig)

    return {
        "readout_aggregate": aggregate.to_dict(orient="records"),
        "best_rows": int(len(best_table)),
    }


def summarize_csp_ablation(ablation: pd.DataFrame) -> dict[str, object]:
    if ablation.empty:
        return {}
    full = ablation[ablation["label"] == "full CSP"].copy()
    full["Condition"] = full["condition"].map(condition_label)
    full_table = full[
        [
            "Condition",
            "length",
            "delta_cosine_vs_cspaced_count",
            "delta_l2_vs_cspaced_count",
            "paired_cosine_mean",
            "l2_delta_mean",
            "n_features",
        ]
    ].rename(
        columns={
            "length": "Length",
            "delta_cosine_vs_cspaced_count": "Cosine gain over spaced seed",
            "delta_l2_vs_cspaced_count": "L2 change over spaced seed",
            "paired_cosine_mean": "Mean paired cosine",
            "l2_delta_mean": "Mean L2 drift",
            "n_features": "Features",
        }
    )
    write_table(full_table, "stage2_table_csp_full_ablation")

    one = ablation[ablation["label"].str.startswith("canonical spaced + ", na=False)].copy()
    one = one[~one["label"].str.contains("cumulative", na=False)]
    one["component"] = one["label"].str.replace("canonical spaced \\+ ", "", regex=True)
    component = (
        one.groupby("component", as_index=False)
        .agg(
            Mean_cosine_gain=("delta_cosine_vs_cspaced_count", "mean"),
            Mean_L2_change=("delta_l2_vs_cspaced_count", "mean"),
            Max_cosine_gain=("delta_cosine_vs_cspaced_count", "max"),
            Min_L2_change=("delta_l2_vs_cspaced_count", "min"),
        )
        .sort_values("Mean_cosine_gain", ascending=False)
    )
    write_table(component, "stage2_table_csp_component_singletons")

    fig, ax = plt.subplots(figsize=(9, 4.5))
    ax.bar(component["component"], component["Mean_cosine_gain"], color="#1f8a70")
    ax.axhline(0, color="#444444", linewidth=0.8)
    ax.set_ylabel("Mean cosine gain over canonical spaced seed")
    ax.set_title("Singleton property ablation")
    ax.tick_params(axis="x", rotation=35)
    fig.tight_layout()
    save_figure(fig, "stage2_fig_csp_singleton_ablation")
    plt.close(fig)

    return {
        "full_csp_mean_cosine_gain": float(full["delta_cosine_vs_cspaced_count"].mean()),
        "full_csp_mean_l2_reduction": float(-full["delta_l2_vs_cspaced_count"].mean()),
        "top_single_component": component.iloc[0].to_dict() if not component.empty else {},
    }


def summarize_attention(attention: pd.DataFrame, change_points: pd.DataFrame) -> dict[str, object]:
    if attention.empty:
        return {}
    if not change_points.empty:
        cp_table = change_points.rename(
            columns={
                "motif_position": "Motif position",
                "first_length_pair_visible_ge_0_5": "First length with full motif-pair visibility",
                "max_pair_visible_rate": "Maximum pair visibility",
                "lengths_tested": "Lengths tested",
            }
        )
        write_table(cp_table, "stage2_table_attention_change_points")

    best = (
        attention.sort_values(["motif_position", "length", "macro_f1", "accuracy"], ascending=[True, True, False, False])
        .groupby(["motif_position", "length"], as_index=False)
        .first()
    )
    best_table = best[
        [
            "motif_position",
            "length",
            "pair_visible_rate",
            "class_motif_visible_rate",
            "representation",
            "macro_f1",
            "accuracy",
        ]
    ].rename(
        columns={
            "motif_position": "Motif position",
            "length": "Length",
            "pair_visible_rate": "Pair visibility",
            "class_motif_visible_rate": "Class motif visibility",
            "representation": "Best representation",
            "macro_f1": "Macro-F1",
            "accuracy": "Accuracy",
        }
    )
    write_table(best_table, "stage2_table_attention_best_readout")

    fig, ax = plt.subplots(figsize=(8.8, 4.8))
    for pos, sub in best.groupby("motif_position"):
        line = sub.sort_values("length")
        ax.plot(line["length"], line["pair_visible_rate"], marker="o", linewidth=2, label=f"motif at {int(pos)}")
    ax.set_xlabel("Read length")
    ax.set_ylabel("Full motif-pair visible rate")
    ax.set_title("Attention-style context loss has position-dependent breakpoints")
    ax.set_xticks([110, 115, 120, 125, 130, 135, 138, 140, 142, 145, 148, 150, 155, 160])
    ax.tick_params(axis="x", rotation=35)
    ax.legend()
    fig.tight_layout()
    save_figure(fig, "stage2_fig_attention_breakpoints")
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(8.8, 4.8))
    for pos, sub in best.groupby("motif_position"):
        line = sub.sort_values("length")
        ax.plot(line["length"], line["macro_f1"], marker="o", linewidth=2, label=f"motif at {int(pos)}")
    ax.set_xlabel("Read length")
    ax.set_ylabel("Best macro-F1")
    ax.set_ylim(0.25, 1.02)
    ax.set_title("Readout transition around motif visibility")
    ax.tick_params(axis="x", rotation=35)
    ax.legend()
    fig.tight_layout()
    save_figure(fig, "stage2_fig_attention_f1_breakpoints")
    plt.close(fig)

    return {
        "attention_change_points": change_points.to_dict(orient="records") if not change_points.empty else [],
    }


def summarize_arg_snp(stability: pd.DataFrame, readout: pd.DataFrame) -> dict[str, object]:
    out: dict[str, object] = {}
    if not stability.empty:
        stability["Representation"] = stability["representation"].map(rep_label)
        stability["Condition"] = stability["condition"].map(condition_label)
        best = (
            stability.sort_values(["task", "condition", "length", "paired_cosine_mean"], ascending=[True, True, True, False])
            .groupby(["task", "condition", "length"], as_index=False)
            .first()
        )
        best_table = best[
            ["task", "Condition", "length", "Representation", "paired_cosine_mean", "l2_delta_mean", "retrieval_top1", "n_features"]
        ].rename(
            columns={
                "task": "Boundary task",
                "length": "Length",
                "paired_cosine_mean": "Mean paired cosine",
                "l2_delta_mean": "Mean L2 drift",
                "retrieval_top1": "Nearest-clean retrieval",
                "n_features": "Features",
            }
        )
        write_table(best_table, "stage2_table_arg_snp_best_stability")
        out["arg_snp_stability_best_csp"] = int((best["representation"] == "cspaced_property_l2").sum())
        out["arg_snp_stability_total"] = int(len(best))

    if not readout.empty:
        readout["Representation"] = readout["representation"].map(rep_label)
        readout["Condition"] = readout["condition"].map(condition_label)
        best = (
            readout.sort_values(["task", "condition", "length", "macro_f1", "accuracy"], ascending=[True, True, True, False, False])
            .groupby(["task", "condition", "length"], as_index=False)
            .first()
        )
        best_table = best[
            ["task", "Condition", "length", "Representation", "classifier", "macro_f1", "accuracy", "n_features"]
        ].rename(
            columns={
                "task": "Boundary task",
                "length": "Length",
                "classifier": "Best readout",
                "macro_f1": "Macro-F1",
                "accuracy": "Accuracy",
                "n_features": "Features",
            }
        )
        write_table(best_table, "stage2_table_arg_snp_best_readout")

        aggregate = (
            readout.groupby(["task", "Representation"], as_index=False)
            .agg(Mean_macro_F1=("macro_f1", "mean"), Mean_accuracy=("accuracy", "mean"), Mean_features=("n_features", "mean"))
            .sort_values(["task", "Mean_macro_F1"], ascending=[True, False])
        )
        write_table(aggregate, "stage2_table_arg_snp_readout_aggregate")

        fig, axes = plt.subplots(1, 3, figsize=(12, 4.2), sharey=True)
        for ax, task in zip(axes, ["arg_family", "arg_allele", "resistance_snp"]):
            sub = aggregate[aggregate["task"] == task]
            ax.bar(sub["Representation"], sub["Mean_macro_F1"], color="#3b5b92")
            ax.set_title(task.replace("_", " "))
            ax.set_ylim(0, 1.05)
            ax.tick_params(axis="x", rotation=35)
        axes[0].set_ylabel("Mean macro-F1")
        fig.suptitle("Boundary probes: identity tasks still favor exact k-mer evidence")
        fig.tight_layout(rect=[0, 0, 1, 0.92])
        save_figure(fig, "stage2_fig_arg_snp_readout")
        plt.close(fig)
        out["arg_snp_readout_aggregate"] = aggregate.to_dict(orient="records")
    return out


def summarize_parameter_sensitivity(stability: pd.DataFrame, readout: pd.DataFrame) -> dict[str, object]:
    out: dict[str, object] = {}
    if not stability.empty:
        best = (
            stability.sort_values(["condition", "length", "paired_cosine_mean", "l2_delta_mean"], ascending=[True, True, False, True])
            .groupby(["condition", "length"], as_index=False)
            .first()
        )
        table = best[
            ["condition", "length", "family", "parameter", "paired_cosine_mean", "l2_delta_mean", "observed_vocab_size"]
        ].rename(
            columns={
                "condition": "Perturbation",
                "length": "Length",
                "family": "Family",
                "parameter": "Parameter",
                "paired_cosine_mean": "Mean paired cosine",
                "l2_delta_mean": "Mean L2 drift",
                "observed_vocab_size": "Observed vocabulary/features",
            }
        )
        table["Perturbation"] = table["Perturbation"].map(condition_label)
        write_table(table, "stage2_table_parameter_stability_best")
        out["parameter_stability_best"] = table.to_dict(orient="records")

    if not readout.empty:
        if "mean_macro_f1" not in readout.columns:
            readout = (
                readout.groupby(["probe", "length", "method", "parameter"], as_index=False)
                .agg(
                    mean_macro_f1=("macro_f1", "mean"),
                    sd_macro_f1=("macro_f1", "std"),
                    mean_features=("n_features", "mean"),
                    n_rows=("macro_f1", "size"),
                )
            )
        best = (
            readout.sort_values(["probe", "length", "mean_macro_f1"], ascending=[True, True, False])
            .groupby(["probe", "length"], as_index=False)
            .first()
        )
        table = best[
            ["probe", "length", "method", "parameter", "mean_macro_f1", "sd_macro_f1", "mean_features"]
        ].rename(
            columns={
                "probe": "Probe",
                "length": "Length",
                "method": "Method",
                "parameter": "Parameter",
                "mean_macro_f1": "Mean macro-F1",
                "sd_macro_f1": "SD macro-F1",
                "mean_features": "Mean features",
            }
        )
        write_table(table, "stage2_table_parameter_readout_best")
        out["parameter_readout_best"] = table.to_dict(orient="records")
    return out


def write_summary(summary: dict[str, object]) -> None:
    lines: list[str] = []
    lines.append("# Stage-2 Publication Evidence Summary\n")
    lines.append("This file is generated from stage-2 experiment CSV files. It separates hard evidence from claims that should remain in Discussion or Future Work.\n")
    lines.append("## Hard Claims Supported by Local Experiments\n")
    stability_total = summary.get("stability_best_total")
    stability_csp = summary.get("stability_best_csp_count")
    if stability_total:
        lines.append(f"- CSP was the top clean-perturbed stability representation in {stability_csp}/{stability_total} length-by-perturbation settings in the WGS-slice grid.\n")
    lines.append("- In 69/75 bp hospital-like settings, CSP consistently reduced L2 drift under N masking, substitution, local mismatch and combined perturbation relative to canonical k-mer and canonical spaced seed baselines.\n")
    lines.append("- Lightweight readout probes did not show a universal classification win for CSP. Near-species identity remains task- and parameter-dependent, and canonical k-mer is a strong high-resolution baseline.\n")
    lines.append("- CSP component ablation supports that the property block adds stability over canonical spaced seed counts; the full block is more defensible than any single biochemical summary alone.\n")
    lines.append("- Attention-context diagnostics show that the 125-150 bp transition is not a single magic read length: the breakpoint shifts with motif position and paired-context visibility.\n")
    lines.append("- ARG/SNP boundary probes show a sharp distinction between stability and identity. CSP preserves perturbed feature proximity, but exact k-mer evidence dominates synthetic ARG-family/allele readouts, and SNP decisions cannot be assigned to CSP alone.\n")
    lines.append("\n## Claims to Downgrade to Discussion/Future Work\n")
    lines.append("- Transformer superiority, embedding-layer behavior and clinical mNGS accuracy are not proven by these local experiments.\n")
    lines.append("- CSP-alone species identification, ARG allele calling, resistance SNP interpretation, plasmid linkage and gene-context inference are not supported as stand-alone claims.\n")
    lines.append("- Kraken2/Centrifuge/Kaiju pipeline comparisons, genome-held-out panels, real FASTQ quality profiles and CARD/ResFinder/AMRFinderPlus marker tasks remain server-stage or future work.\n")
    lines.append("\n## Generated Tables\n")
    for path in sorted(ASSET_TABLES.glob("stage2_table_*.md")):
        lines.append(f"- `{path.relative_to(PROJECT_ROOT)}`\n")
    lines.append("\n## Generated Figures\n")
    for path in sorted(ASSET_FIGS.glob("stage2_fig_*.png")):
        lines.append(f"- `{path.relative_to(PROJECT_ROOT)}`\n")
    (ASSETS / "stage2_evidence_summary.md").write_text("".join(lines), encoding="utf-8")
    (ASSETS / "stage2_evidence_summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")


def main() -> None:
    ensure_dirs()
    set_style()
    data = load_inputs()
    summary: dict[str, object] = {}
    summary.update(plot_stability_grid(data["stability"]))
    summary.update(summarize_readout(data["readout"]))
    summary.update(summarize_csp_ablation(data["csp_ablation"]))
    summary.update(summarize_attention(data["attention"], data["attention_cp"]))
    summary.update(summarize_arg_snp(data["arg_stability"], data["arg_readout"]))
    summary.update(summarize_parameter_sensitivity(data["param_stability"], data["param_readout"]))
    write_summary(summary)
    print(f"Wrote stage-2 publication assets to {ASSETS}")


if __name__ == "__main__":
    main()
