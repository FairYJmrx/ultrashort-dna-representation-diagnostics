from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RUNS = PROJECT_ROOT / "results" / "runs"
FIGS = PROJECT_ROOT / "results" / "figures"
TABLES = PROJECT_ROOT / "manuscript" / "tables"
MANUSCRIPT = PROJECT_ROOT / "manuscript"


REP_LABELS = {
    "kmer5_count_l2": "5-mer count",
    "ckmer5_count_l2": "canonical 5-mer",
    "spaced_count_l2": "spaced seed",
    "cspaced_count_l2": "canonical spaced",
    "cspaced_property_l2": "canonical spaced + property",
    "property_channels": "property channels",
    "spaced_kmer_no_phase": "spaced property",
    "spaced_kmer_phase": "spaced property + phase",
    "rope_onehot": "RoPE one-hot",
    "rope_property": "RoPE property",
    "kmer5_presence": "5-mer presence",
}

CORE_REPS = [
    "ckmer5_count_l2",
    "cspaced_count_l2",
    "cspaced_property_l2",
    "property_channels",
    "spaced_kmer_phase",
    "rope_property",
]

COLORS = {
    "ckmer5_count_l2": "#1f4e79",
    "cspaced_count_l2": "#7b3294",
    "cspaced_property_l2": "#00876c",
    "property_channels": "#d95f02",
    "spaced_kmer_phase": "#7570b3",
    "rope_property": "#a6761d",
    "kmer5_count_l2": "#4d4d4d",
}


def load_csv(path: Path) -> pd.DataFrame:
    return pd.read_csv(path) if path.exists() else pd.DataFrame()


def ensure_dirs() -> None:
    FIGS.mkdir(parents=True, exist_ok=True)
    TABLES.mkdir(parents=True, exist_ok=True)


def rep_label(name: str) -> str:
    return REP_LABELS.get(name, name)


def markdown_table(df: pd.DataFrame, path: Path, floatfmt: str = ".3f") -> None:
    path.write_text(df.to_markdown(index=False, floatfmt=floatfmt), encoding="utf-8")


def format_length_label(length: int | float) -> str:
    length_int = int(length)
    return "PE150 proxy" if length_int == 300 else f"{length_int} bp"


def add_length_ticks(ax: plt.Axes) -> None:
    ticks = [69, 75, 100, 125, 150, 300]
    ax.set_xticks(ticks)
    ax.set_xticklabels([format_length_label(t) for t in ticks], rotation=25, ha="right")


def plot_perturbation_stability(metrics: pd.DataFrame) -> pd.DataFrame:
    if metrics.empty:
        return pd.DataFrame()
    df = metrics[
        (metrics["task"] == "perturbation_stability")
        & (metrics["group"] == "close_relative_wgs")
        & (metrics["condition"].isin(["N_3pct", "substitution_1pct"]))
        & (metrics["representation"].isin(CORE_REPS + ["kmer5_count_l2"]))
    ].copy()
    df["label"] = df["representation"].map(rep_label)

    summary = (
        df[["condition", "length", "representation", "paired_cosine_mean", "paired_cosine_p05", "l2_delta_mean"]]
        .sort_values(["condition", "length", "representation"])
        .reset_index(drop=True)
    )
    markdown_table(summary.assign(representation=summary["representation"].map(rep_label)), TABLES / "table_perturbation_stability.md")

    fig, axes = plt.subplots(1, 2, figsize=(12, 4.8), sharey=True)
    for ax, condition in zip(axes, ["N_3pct", "substitution_1pct"]):
        sub = df[df["condition"] == condition]
        for rep in CORE_REPS + ["kmer5_count_l2"]:
            line = sub[sub["representation"] == rep].sort_values("length")
            if line.empty:
                continue
            ax.plot(
                line["length"],
                line["paired_cosine_mean"],
                marker="o",
                linewidth=2,
                color=COLORS.get(rep),
                label=rep_label(rep),
            )
        ax.set_title(condition.replace("_", " "))
        ax.set_xlabel("Observed read length")
        ax.set_ylabel("Clean-perturbed paired cosine")
        ax.set_ylim(0.75, 1.01)
        ax.grid(alpha=0.25)
        add_length_ticks(ax)
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower center", ncol=4, frameon=False)
    fig.suptitle("Perturbation stability across read length")
    fig.tight_layout(rect=[0, 0.12, 1, 0.94])
    fig.savefig(FIGS / "fig_publication_perturbation_stability.png", dpi=220)
    plt.close(fig)
    return summary


def plot_property_ablation(deltas: pd.DataFrame) -> pd.DataFrame:
    if deltas.empty:
        return pd.DataFrame()
    df = deltas[
        (deltas["comparison"] == "property_added_to_cspaced")
        & (deltas["task"] == "perturbation_stability")
        & (deltas["group"] == "close_relative_wgs")
        & (deltas["condition"].isin(["N_3pct", "substitution_1pct"]))
    ].copy()
    df["l2_improvement"] = -df["delta_l2_delta_mean"]
    summary = df[
        [
            "condition",
            "length",
            "delta_paired_cosine_mean",
            "delta_paired_cosine_p05",
            "delta_l2_delta_mean",
            "l2_improvement",
        ]
    ].sort_values(["condition", "length"])
    markdown_table(summary, TABLES / "table_property_ablation.md")

    fig, axes = plt.subplots(1, 2, figsize=(11, 4.5))
    for condition, color in [("N_3pct", "#00876c"), ("substitution_1pct", "#3b6ea8")]:
        sub = df[df["condition"] == condition].sort_values("length")
        axes[0].plot(sub["length"], sub["delta_paired_cosine_mean"], marker="o", linewidth=2, color=color, label=condition)
        axes[1].plot(sub["length"], sub["l2_improvement"], marker="o", linewidth=2, color=color, label=condition)
    axes[0].axhline(0, color="#555555", linewidth=0.8)
    axes[1].axhline(0, color="#555555", linewidth=0.8)
    axes[0].set_ylabel("Delta paired cosine")
    axes[1].set_ylabel("Reduction in L2 perturbation")
    for ax in axes:
        ax.set_xlabel("Observed read length")
        ax.grid(alpha=0.25)
        add_length_ticks(ax)
        ax.legend(frameon=False)
    fig.suptitle("Ablation: adding DNA property summaries to canonical spaced seeds")
    fig.tight_layout(rect=[0, 0, 1, 0.92])
    fig.savefig(FIGS / "fig_publication_property_ablation.png", dpi=220)
    plt.close(fig)
    return summary


def summarize_close_relative(species: pd.DataFrame, target: pd.DataFrame) -> pd.DataFrame:
    frames: list[pd.DataFrame] = []
    for task_name, df in [("within-genus species probe", species), ("target/background probe", target)]:
        if df.empty:
            continue
        sub = df[df["representation"].isin(CORE_REPS + ["kmer5_count_l2"])].copy()
        if sub.empty:
            continue
        grouped = (
            sub.groupby(["length", "condition", "representation"], as_index=False)
            .agg(
                mean_macro_f1=("macro_f1", "mean"),
                sd_macro_f1=("macro_f1", "std"),
                mean_accuracy=("accuracy", "mean"),
                genera=("group", "nunique"),
                mean_features=("n_features", "mean"),
            )
        )
        grouped.insert(0, "probe", task_name)
        frames.append(grouped)
    if not frames:
        return pd.DataFrame()
    out = pd.concat(frames, ignore_index=True)
    out["representation_label"] = out["representation"].map(rep_label)
    table = out[
        [
            "probe",
            "condition",
            "length",
            "representation_label",
            "mean_macro_f1",
            "sd_macro_f1",
            "mean_accuracy",
            "genera",
            "mean_features",
        ]
    ].sort_values(["probe", "condition", "length", "mean_macro_f1"], ascending=[True, True, True, False])
    markdown_table(table, TABLES / "table_close_relative_probe_summary.md")
    return out


def plot_close_relative(summary: pd.DataFrame) -> None:
    if summary.empty:
        return
    clean = summary[summary["condition"] == "clean"].copy()
    probes = ["within-genus species probe", "target/background probe"]
    fig, axes = plt.subplots(1, 2, figsize=(13, 4.8), sharey=False)
    for ax, probe in zip(axes, probes):
        sub = clean[clean["probe"] == probe]
        for rep in CORE_REPS + ["kmer5_count_l2"]:
            line = sub[sub["representation"] == rep].sort_values("length")
            if line.empty:
                continue
            ax.plot(
                line["length"],
                line["mean_macro_f1"],
                marker="o",
                linewidth=2,
                color=COLORS.get(rep),
                label=rep_label(rep),
            )
        ax.set_title(probe)
        ax.set_xlabel("Observed read length")
        ax.set_ylabel("Mean macro-F1 across genera")
        ax.grid(alpha=0.25)
        add_length_ticks(ax)
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower center", ncol=4, frameon=False)
    fig.suptitle("Close-relative WGS-slice classification probes (clean reads)")
    fig.tight_layout(rect=[0, 0.12, 1, 0.94])
    fig.savefig(FIGS / "fig_publication_close_relative_probes.png", dpi=220)
    plt.close(fig)


def summarize_attention(attention: pd.DataFrame) -> pd.DataFrame:
    if attention.empty:
        return pd.DataFrame()
    visibility = (
        attention.groupby(["length", "observed_layout"], as_index=False)
        .agg(
            pair_visible_rate=("pair_visible_rate", "first"),
            class_motif_visible_rate=("class_motif_visible_rate", "first"),
            partial_class_prefix_visible_rate=("partial_class_prefix_visible_rate", "first"),
            base_tokens=("base_tokens", "first"),
            k5_tokens=("k5_tokens", "first"),
            full_attention_base_pairs=("full_attention_base_pairs", "first"),
            full_attention_k5_pairs=("full_attention_k5_pairs", "first"),
        )
        .sort_values("length")
    )
    best = (
        attention.sort_values(["length", "macro_f1"], ascending=[True, False])
        .groupby(["length", "observed_layout"], as_index=False)
        .first()[["length", "observed_layout", "representation", "macro_f1", "accuracy"]]
    )
    merged = visibility.merge(best, on=["length", "observed_layout"], how="left")
    merged["representation"] = merged["representation"].map(rep_label)
    markdown_table(merged, TABLES / "table_attention_context_visibility.md")
    return merged


def summarize_parameter_sensitivity(stability: pd.DataFrame, classification: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    if stability.empty:
        return pd.DataFrame(), pd.DataFrame()

    perturb = stability[stability["condition"].isin(["N_3pct", "substitution_1pct"])].copy()
    best_stability = (
        perturb.sort_values(["condition", "length", "paired_cosine_mean"], ascending=[True, True, False])
        .groupby(["condition", "length"], as_index=False)
        .first()
        .sort_values(["condition", "length"])
    )
    markdown_table(
        best_stability[
            [
                "condition",
                "length",
                "family",
                "parameter",
                "paired_cosine_mean",
                "paired_cosine_p05",
                "l2_delta_mean",
                "observed_vocab_size",
            ]
        ],
        TABLES / "table_parameter_sensitivity_best_stability.md",
    )

    fig, axes = plt.subplots(1, 2, figsize=(12, 4.8))
    n75 = perturb[(perturb["condition"] == "N_3pct") & (perturb["length"] == 75)].copy()
    kmer = n75[n75["family"].isin(["k-mer", "canonical k-mer"])].sort_values(["family", "k"])
    for family, color in [("k-mer", "#666666"), ("canonical k-mer", "#1f4e79")]:
        sub = kmer[kmer["family"] == family]
        if not sub.empty:
            axes[0].plot(sub["k"], sub["paired_cosine_mean"], marker="o", linewidth=2, color=color, label=family)
    axes[0].set_xlabel("k")
    axes[0].set_ylabel("Paired cosine under 3% N at 75 bp")
    axes[0].set_ylim(0.85, 1.01)
    axes[0].grid(alpha=0.25)
    axes[0].legend(frameon=False)

    spaced = n75[n75["family"].isin(["canonical spaced", "canonical spaced + property"])].copy()
    if not spaced.empty:
        order = sorted(spaced["parameter"].unique().tolist())
        x = np.arange(len(order))
        width = 0.35
        for offset, family, color in [(-width / 2, "canonical spaced", "#7b3294"), (width / 2, "canonical spaced + property", "#00876c")]:
            sub = spaced[spaced["family"] == family].set_index("parameter").reindex(order)
            axes[1].bar(x + offset, sub["paired_cosine_mean"], width=width, color=color, label=family)
        axes[1].set_xticks(x)
        axes[1].set_xticklabels([item.replace("pattern=", "") for item in order], rotation=25, ha="right")
    axes[1].set_xlabel("Spaced-seed pattern")
    axes[1].set_ylabel("Paired cosine under 3% N at 75 bp")
    axes[1].set_ylim(0.85, 1.01)
    axes[1].grid(axis="y", alpha=0.25)
    axes[1].legend(frameon=False)
    fig.suptitle("Parameter sensitivity audit")
    fig.tight_layout(rect=[0, 0, 1, 0.92])
    fig.savefig(FIGS / "fig_publication_parameter_sensitivity.png", dpi=220)
    plt.close(fig)

    if classification.empty:
        return best_stability, pd.DataFrame()

    valid = classification.dropna(subset=["macro_f1"]).copy()
    best_classification = pd.DataFrame()
    if not valid.empty:
        grouped = (
            valid.groupby(["probe", "length", "method", "parameter"], as_index=False)
            .agg(
                mean_macro_f1=("macro_f1", "mean"),
                sd_macro_f1=("macro_f1", "std"),
                mean_accuracy=("accuracy", "mean"),
                mean_features=("n_features", "mean"),
                genera=("genus", "nunique"),
            )
        )
        best_classification = (
            grouped.sort_values(["probe", "length", "mean_macro_f1"], ascending=[True, True, False])
            .groupby(["probe", "length"], as_index=False)
            .first()
            .sort_values(["probe", "length"])
        )
        markdown_table(best_classification, TABLES / "table_parameter_sensitivity_best_classification.md")
    return best_stability, best_classification


def representation_taxonomy() -> pd.DataFrame:
    rows = [
        {
            "representation": "5-mer count",
            "definition": "Counts contiguous length-5 words and L2-normalizes the vector.",
            "information emphasized": "local composition and exact short words",
            "strength region": "simple composition probes and strong conventional baseline",
            "limitation": "not strand-invariant unless canonicalized; vocabulary grows as 4^k",
        },
        {
            "representation": "canonical 5-mer",
            "definition": "Counts min(word, reverse-complement word) for each 5-mer.",
            "information emphasized": "strand-symmetric local composition",
            "strength region": "close-relative classification stress tests",
            "limitation": "may discard strand-specific signals and remains high-dimensional for larger k",
        },
        {
            "representation": "canonical spaced",
            "definition": "Counts spaced-seed tokens after reverse-complement canonicalization.",
            "information emphasized": "non-contiguous local patterns with strand symmetry",
            "strength region": "compact strand-friendly baseline",
            "limitation": "less exact than contiguous k-mer for some close-relative tasks",
        },
        {
            "representation": "canonical spaced + property",
            "definition": "Concatenates canonical spaced-token counts with DNA property summaries, then L2-normalizes.",
            "information emphasized": "strand symmetry plus GC, purine, hydrogen-bond, EIIP, and N-mask summaries",
            "strength region": "compact auxiliary representation with perturbation stability",
            "limitation": "not a universal replacement for canonical k-mer",
        },
        {
            "representation": "property channels",
            "definition": "Maps each base to biochemical/numeric channels along sequence position.",
            "information emphasized": "per-position biochemical signal and ambiguity masks",
            "strength region": "substitution-stability and model-compatible dense input",
            "limitation": "weak taxonomy signal without a model that uses positional context",
        },
        {
            "representation": "spaced property + phase",
            "definition": "Uses spaced-token property vectors with explicit three-phase positional sine/cosine terms.",
            "information emphasized": "spaced local signal plus reading-frame-like phase prior",
            "strength region": "position-sensitive controlled tasks",
            "limitation": "current ablation did not show independent phase gain",
        },
        {
            "representation": "RoPE property",
            "definition": "Rotates DNA property channels with RoPE-like relative positional phases.",
            "information emphasized": "attention-compatible property and relative-position signal",
            "strength region": "hypothesis-driven input for tiny Transformer/server follow-up",
            "limitation": "not yet validated with a full Transformer in this local study",
        },
    ]
    df = pd.DataFrame(rows)
    markdown_table(df, TABLES / "table_representation_taxonomy.md", floatfmt=".3f")
    return df


def write_synthesis(
    perturb: pd.DataFrame,
    prop_ablation: pd.DataFrame,
    close_summary: pd.DataFrame,
    attention_summary: pd.DataFrame,
    parameter_stability: pd.DataFrame,
    parameter_classification: pd.DataFrame,
) -> None:
    lines: list[str] = []
    lines.append("# Publication Evidence Synthesis\n")
    lines.append("This synthesis enforces the revised manuscript position: the project compares DNA-read representations, not clinical species-identification accuracy.\n")
    lines.append("## Main Claim Boundary\n")
    lines.append("`cspaced_property_l2` should be described as a compact, strand-friendly, perturbation-stable auxiliary representation. It complements canonical k-mer baselines; it does not replace them.\n")

    if not prop_ablation.empty:
        best_l2 = prop_ablation.sort_values("l2_improvement", ascending=False).iloc[0]
        best_cos = prop_ablation.sort_values("delta_paired_cosine_mean", ascending=False).iloc[0]
        lines.append("## Property-Ablation Result\n")
        lines.append(
            "Adding DNA property summaries to canonical spaced seeds improved perturbation stability in the close-relative WGS-slice audit. "
            f"The largest cosine gain was {best_cos['delta_paired_cosine_mean']:.3f} under {best_cos['condition']} at {format_length_label(best_cos['length'])}; "
            f"the largest L2 reduction was {best_l2['l2_improvement']:.3f} under {best_l2['condition']} at {format_length_label(best_l2['length'])}."
        )
        lines.append("This supports the auxiliary-robustness claim, not a universal taxonomy claim.\n")

    if not perturb.empty:
        n75 = perturb[(perturb["condition"] == "N_3pct") & (perturb["length"] == 75)]
        if not n75.empty:
            best = n75.sort_values("paired_cosine_mean", ascending=False).iloc[0]
            lines.append("## Perturbation Stability\n")
            lines.append(
                f"At 75 bp with 3% N masking, the strongest mean clean-perturbed cosine among the audited representations was "
                f"{rep_label(best['representation'])} ({best['paired_cosine_mean']:.3f}). "
                "Across lengths, canonical spaced + property stayed close to the top stability region."
            )
            lines.append("This is the clearest local advantage region for the proposed hybrid representation.\n")

    if not close_summary.empty:
        clean = close_summary[close_summary["condition"] == "clean"]
        species = clean[clean["probe"] == "within-genus species probe"]
        target = clean[clean["probe"] == "target/background probe"]
        lines.append("## Close-Relative Probe\n")
        if not species.empty:
            best_species = species.sort_values("mean_macro_f1", ascending=False).iloc[0]
            lines.append(
                f"In the clean within-genus species probe, the best averaged readout was {rep_label(best_species['representation'])} "
                f"at {format_length_label(best_species['length'])} (mean macro-F1 {best_species['mean_macro_f1']:.3f})."
            )
        if not target.empty:
            best_target = target.sort_values("mean_macro_f1", ascending=False).iloc[0]
            lines.append(
                f"In the clean target/background probe, the best averaged readout was {rep_label(best_target['representation'])} "
                f"at {format_length_label(best_target['length'])} (mean macro-F1 {best_target['mean_macro_f1']:.3f})."
            )
        lines.append("These results must be framed as lightweight separability probes over 21 selected genomes, not as a representative clinical mNGS benchmark.\n")

    if not attention_summary.empty:
        short = attention_summary[attention_summary["length"].isin([69, 75, 100, 125])]
        long = attention_summary[attention_summary["length"].isin([150, 300])]
        short_pair = float(short["pair_visible_rate"].max()) if not short.empty else float("nan")
        long_pair = float(long["pair_visible_rate"].min()) if not long.empty else float("nan")
        lines.append("## Attention Context-Loss Diagnostic\n")
        lines.append(
            f"The synthetic motif-pair diagnostic showed pair visibility near {short_pair:.3f} below 150 bp and {long_pair:.3f} at 150 bp/PE150. "
            "This supports the user's hypothesis that short reads can lose an entire contextual relation, not merely a proportional number of bases."
        )
        lines.append("The local diagnostic does not prove Transformer superiority; it explains when attention-compatible encodings have enough observed context to be meaningful.\n")

    if not parameter_stability.empty:
        n3 = parameter_stability[parameter_stability["condition"] == "N_3pct"]
        stable_family_counts = n3["family"].value_counts().to_dict()
        lines.append("## Parameter Sensitivity\n")
        lines.append(
            "The k/pattern sensitivity audit prevents a single-parameter claim. "
            f"Across N-masking stability winners, the family counts were {stable_family_counts}. "
            "The downstream close-relative readout remained parameter-sensitive, so classification probes should not be used as a universal method ranking."
        )
        if not parameter_classification.empty:
            best = parameter_classification.sort_values("mean_macro_f1", ascending=False).iloc[0]
            lines.append(
                f"The best sampled classification probe was {best['method']} with {best['parameter']} "
                f"for {best['probe']} at {format_length_label(best['length'])} "
                f"(mean macro-F1 {best['mean_macro_f1']:.3f}), reinforcing that canonical k-mer and spaced variants remain strong baselines."
            )
        lines.append("")

    lines.append("## Accuracy Policy\n")
    lines.append("Accuracy and macro-F1 should appear as tertiary downstream probes. They help ask whether a representation exposes information to a simple readout, but they do not establish clinical performance or universal taxonomy superiority.\n")

    lines.append("## Server-Scale Follow-Up\n")
    lines.append("A larger server experiment should expand close-relative panels, add realistic FASTQ simulation, and compare tiny CNN/Transformer models under matched representation inputs. These are follow-up validation steps rather than prerequisites for reporting the current lightweight representation diagnostics.\n")

    (MANUSCRIPT / "publication_evidence_synthesis.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    ensure_dirs()
    metrics = load_csv(RUNS / "prior_ablation_wgs_lengths" / "prior_ablation_metrics.csv")
    deltas = load_csv(RUNS / "prior_ablation_wgs_lengths" / "prior_ablation_deltas.csv")
    species = load_csv(RUNS / "close_relative_species_core" / "classification_results_with69_100.csv")
    target = load_csv(RUNS / "close_relative_target_binary_core" / "classification_results_with69_100.csv")
    attention = load_csv(RUNS / "attention_context_loss" / "attention_context_results.csv")
    parameter_stability_raw = load_csv(RUNS / "parameter_sensitivity" / "parameter_stability_metrics.csv")
    parameter_classification_raw = load_csv(RUNS / "parameter_sensitivity" / "parameter_classification_probes.csv")

    representation_taxonomy()
    perturb = plot_perturbation_stability(metrics)
    prop_ablation = plot_property_ablation(deltas)
    close_summary = summarize_close_relative(species, target)
    plot_close_relative(close_summary)
    attention_summary = summarize_attention(attention)
    parameter_stability, parameter_classification = summarize_parameter_sensitivity(parameter_stability_raw, parameter_classification_raw)
    write_synthesis(perturb, prop_ablation, close_summary, attention_summary, parameter_stability, parameter_classification)

    print(f"Wrote publication tables to {TABLES}")
    print(f"Wrote publication figures to {FIGS}")
    print(f"Wrote {MANUSCRIPT / 'publication_evidence_synthesis.md'}")


if __name__ == "__main__":
    main()
