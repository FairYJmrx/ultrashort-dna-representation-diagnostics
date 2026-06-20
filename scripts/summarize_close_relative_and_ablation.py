from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


def fmt(x: float | int | str | None) -> str:
    if x is None or pd.isna(x):
        return ""
    if isinstance(x, (float, int)):
        return f"{float(x):.3f}"
    return str(x)


def normalize_group(value: object) -> str:
    if pd.isna(value) or str(value).strip() == "":
        return "toy_control"
    return str(value)


def best_by(df: pd.DataFrame, metric: str, keys: list[str], ascending: bool = False) -> pd.DataFrame:
    subset = df.dropna(subset=[metric]).copy()
    if subset.empty:
        return subset
    idx = subset.groupby(keys)[metric].idxmin() if ascending else subset.groupby(keys)[metric].idxmax()
    return subset.loc[idx].reset_index(drop=True)


def write_markdown(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Summarize close-relative and prior-ablation experiments.")
    parser.add_argument("--manifest", default="data/real_slices/close_relative_genomes_manifest.csv")
    parser.add_argument("--ablation", default="results/runs/prior_ablation_core/prior_ablation_metrics.csv")
    parser.add_argument("--deltas", default="results/runs/prior_ablation_core/prior_ablation_deltas.csv")
    parser.add_argument("--components", default="results/runs/prior_ablation_core/prior_component_table.csv")
    parser.add_argument("--species", default="results/runs/close_relative_species_core/classification_results.csv")
    parser.add_argument("--target", default="results/runs/close_relative_target_binary_core/classification_results.csv")
    parser.add_argument("--output", default="manuscript/close_relative_ablation_results.md")
    args = parser.parse_args()

    manifest = pd.read_csv(args.manifest)
    ab = pd.read_csv(args.ablation)
    delta = pd.read_csv(args.deltas)
    comp = pd.read_csv(args.components)
    species = pd.read_csv(args.species)
    target = pd.read_csv(args.target)

    lines: list[str] = []
    lines.append("# Close-relative benchmark and prior-ablation results")
    lines.append("")
    lines.append("## Data source")
    lines.append("")
    lines.append(
        "The close-relative benchmark was constructed from the blood-panel Excel metadata and RefSeq/NCBI Datasets FASTA files. "
        "It contains six clinically relevant genera with target pathogens and close-relative or background species."
    )
    lines.append("")
    lines.append("| Genus | Genomes | Target pathogens | Close/background |")
    lines.append("|---|---:|---:|---:|")
    for genus, g in manifest.groupby("genus"):
        target_n = int((g["benchmark_role"] == "target_pathogen_candidate").sum())
        bg_n = int(len(g) - target_n)
        lines.append(f"| {genus} | {len(g)} | {target_n} | {bg_n} |")
    lines.append("")
    lines.append(
        "Each genome was sampled into 69, 75, 100, 125, and 150 bp single-end reads plus a PE150 proxy "
        "formed by concatenating R1 and reverse-complemented R2. For the close-relative core experiment, "
        "the report focuses on 75, 125, 150, and PE150 under clean and N_3pct conditions."
    )
    lines.append("")

    lines.append("## Component definitions used for ablation")
    lines.append("")
    lines.append("| Representation | Components | Short definition |")
    lines.append("|---|---|---|")
    for _, row in comp.iterrows():
        bits = []
        for col, label in [
            ("contiguous_kmer", "contiguous k-mer"),
            ("spaced_seed", "spaced seed"),
            ("canonical_rc", "canonical RC"),
            ("property_summary", "DNA property"),
            ("position_phase", "phase"),
            ("rope_position", "RoPE"),
        ]:
            if int(row.get(col, 0) or 0):
                bits.append(label)
        lines.append(f"| {row['representation']} | {', '.join(bits) or 'none'} | {row.get('description', '')} |")
    lines.append("")

    lines.append("## Ablation findings")
    lines.append("")
    rc = ab[(ab["task"] == "rc_consistency") & (ab["length"].isin([75, 150, 300]))]
    rc = rc.copy()
    rc["group"] = rc["group"].map(normalize_group)
    rc_best = best_by(rc, "paired_cosine_mean", ["group", "length"])
    lines.append("### Reverse-complement consistency")
    lines.append("")
    lines.append("| Evidence set | Length | Best representation | Mean paired cosine | P05 paired cosine |")
    lines.append("|---|---:|---|---:|---:|")
    for _, row in rc_best.iterrows():
        lines.append(
            f"| {row['group']} | {int(row['length'])} | {row['representation']} | {fmt(row['paired_cosine_mean'])} | {fmt(row['paired_cosine_p05'])} |"
        )
    lines.append("")
    rc_delta = delta[
        (delta["comparison"].isin(["canonicalization_on_contiguous", "canonicalization_on_spaced"]))
        & (delta["task"] == "rc_consistency")
    ].copy()
    if not rc_delta.empty:
        rc_delta["group"] = rc_delta["group"].map(normalize_group)
        lines.append("Canonicalization is the decisive source of strand robustness:")
        lines.append("")
        lines.append("| Evidence set | Comparison | Length | Delta mean paired cosine | Delta P05 paired cosine |")
        lines.append("|---|---|---:|---:|---:|")
        for _, row in rc_delta.sort_values(["group", "comparison", "length"]).iterrows():
            lines.append(
                f"| {row['group']} | {row['comparison']} | {int(row['length'])} | {fmt(row['delta_paired_cosine_mean'])} | {fmt(row['delta_paired_cosine_p05'])} |"
            )
        lines.append("")

    lines.append("### Perturbation stability")
    lines.append("")
    stab = ab[(ab["task"] == "perturbation_stability") & (ab["condition"].isin(["N_3pct", "substitution_1pct"]))]
    stab = stab.copy()
    stab["group"] = stab["group"].map(normalize_group)
    stab_best = best_by(stab, "paired_cosine_mean", ["group", "length", "condition"])
    lines.append("| Evidence set | Condition | Length | Best representation | Mean paired cosine | Mean L2 delta |")
    lines.append("|---|---|---:|---|---:|---:|")
    for _, row in stab_best.sort_values(["group", "condition", "length"]).iterrows():
        lines.append(
            f"| {row['group']} | {row['condition']} | {int(row['length'])} | {row['representation']} | {fmt(row['paired_cosine_mean'])} | {fmt(row['l2_delta_mean'])} |"
        )
    lines.append("")

    prop_delta = delta[
        (delta["comparison"] == "property_added_to_cspaced")
        & (delta["task"] == "perturbation_stability")
        & (delta["condition"].isin(["N_3pct", "substitution_1pct"]))
    ].copy()
    if not prop_delta.empty:
        prop_delta["group"] = prop_delta["group"].map(normalize_group)
        lines.append("Adding property summaries to canonical spaced counts changes perturbation stability as follows:")
        lines.append("")
        lines.append("| Evidence set | Condition | Length | Delta mean paired cosine | Delta mean L2 delta |")
        lines.append("|---|---|---:|---:|---:|")
        for _, row in prop_delta.sort_values(["group", "condition", "length"]).iterrows():
            lines.append(
                f"| {row['group']} | {row['condition']} | {int(row['length'])} | {fmt(row['delta_paired_cosine_mean'])} | {fmt(row['delta_l2_delta_mean'])} |"
            )
        lines.append("")

    lines.append("### Motif-position task")
    lines.append("")
    motif = ab[(ab["task"] == "motif_position") & (ab["classifier"] == "nearest_centroid")]
    motif_best = best_by(motif, "macro_f1", ["length", "condition"])
    lines.append("| Condition | Length | Best representation | Macro-F1 |")
    lines.append("|---|---:|---|---:|")
    for _, row in motif_best.sort_values(["condition", "length"]).iterrows():
        lines.append(f"| {row['condition']} | {int(row['length'])} | {row['representation']} | {fmt(row['macro_f1'])} |")
    lines.append("")
    phase_delta = delta[
        (delta["comparison"] == "phase_added_to_spaced_property")
        & (delta["task"] == "motif_position")
        & (delta["classifier"] == "nearest_centroid")
    ].copy()
    if not phase_delta.empty:
        lines.append("The explicit phase component is evaluated by comparing spaced_kmer_no_phase with spaced_kmer_phase:")
        lines.append("")
        lines.append("| Condition | Length | Delta macro-F1 |")
        lines.append("|---|---:|---:|")
        for _, row in phase_delta.sort_values(["condition", "length"]).iterrows():
            lines.append(f"| {row['condition']} | {int(row['length'])} | {fmt(row['delta_macro_f1'])} |")
        lines.append("")

    lines.append("## Close-relative classification findings")
    lines.append("")
    lines.append("### Within-genus species labels")
    lines.append("")
    species_best = best_by(species, "macro_f1", ["group", "length", "condition"])
    lines.append("| Genus | Condition | Length | Best representation | Macro-F1 | Accuracy |")
    lines.append("|---|---|---:|---|---:|---:|")
    for _, row in species_best.sort_values(["group", "condition", "length"]).iterrows():
        lines.append(
            f"| {row['group']} | {row['condition']} | {int(row['length'])} | {row['representation']} | {fmt(row['macro_f1'])} | {fmt(row['accuracy'])} |"
        )
    lines.append("")
    lines.append("### Target pathogen versus close-relative/background labels")
    lines.append("")
    target_best = best_by(target, "macro_f1", ["group", "length", "condition"])
    lines.append("| Genus | Condition | Length | Best representation | Macro-F1 | Accuracy |")
    lines.append("|---|---|---:|---|---:|---:|")
    for _, row in target_best.sort_values(["group", "condition", "length"]).iterrows():
        lines.append(
            f"| {row['group']} | {row['condition']} | {int(row['length'])} | {row['representation']} | {fmt(row['macro_f1'])} | {fmt(row['accuracy'])} |"
        )
    lines.append("")

    lines.append("## Reviewer-facing interpretation")
    lines.append("")
    lines.append(
        "1. The previous experiments did not fully test close-relative separation. The new benchmark adds six genera and 21 genomes, "
        "including Candida, Klebsiella, Acinetobacter, Burkholderia, Enterobacter, and Escherichia."
    )
    lines.append(
        "2. The close-relative task should be interpreted as a lightweight representation-stress test, not as a clinical mNGS classifier. "
        "Random genome slices avoid cherry-picking similar regions; they allow natural conserved and divergent regions to appear in the sampled reads."
    )
    lines.append(
        "3. The ablation is necessary because cspaced_property_l2 and related methods mix multiple priors. The results separate the effects of "
        "spaced seeds, reverse-complement canonicalization, property summaries, phase, and RoPE-like position."
    )
    lines.append(
        "4. A defensible claim is not that the proposed methods dominate canonical k-mers in species classification. The safer claim is that "
        "canonical spaced-property features provide a compact, strand-aware and perturbation-aware auxiliary representation, while canonical k-mers remain a strong backbone for close-relative classification."
    )

    write_markdown(Path(args.output), "\n".join(lines) + "\n")
    print(f"Wrote {args.output}")


if __name__ == "__main__":
    main()
