from __future__ import annotations

from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def load(path: Path) -> pd.DataFrame:
    return pd.read_csv(path) if path.exists() else pd.DataFrame()


def to_numeric(df: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    out = df.copy()
    for col in cols:
        if col in out.columns:
            out[col] = pd.to_numeric(out[col], errors="coerce")
    return out


def table(df: pd.DataFrame, cols: list[str], n: int = 12) -> str:
    if df.empty:
        return "_No data._"
    shown = df[[col for col in cols if col in df.columns]].head(n)
    if shown.empty:
        return "_No matching columns._"
    return shown.to_markdown(index=False, floatfmt=".4f")


def best_classification(df: pd.DataFrame, task: str) -> pd.DataFrame:
    error_col = df["error"].fillna("") if "error" in df.columns else pd.Series([""] * len(df), index=df.index)
    sub = df[(df["task"] == task) & (error_col == "")].copy()
    sub = to_numeric(sub, ["accuracy", "macro_f1"])
    if sub.empty:
        return sub
    return sub.sort_values(["macro_f1", "accuracy"], ascending=False)


def best_paired_by_condition(df: pd.DataFrame, conditions: list[str]) -> pd.DataFrame:
    sub = df[(df["task"] == "paired_retrieval") & (df["condition"].isin(conditions))].copy()
    sub = to_numeric(sub, ["top1", "mean_paired_cosine", "mean_pair_margin", "margin_positive_rate"])
    if sub.empty:
        return sub
    return (
        sub.sort_values(["condition", "mean_pair_margin", "top1"], ascending=[True, False, False])
        .groupby("condition", as_index=False)
        .first()
        .sort_values("condition")
    )


def main() -> None:
    runs = PROJECT_ROOT / "results" / "runs"
    core = load(runs / "lightweight_downstream_stress_core75" / "lightweight_downstream_results.csv")
    cls = load(runs / "lightweight_downstream_stress_classification75" / "lightweight_downstream_results.csv")

    core = to_numeric(
        core,
        [
            "top1",
            "top5",
            "mrr",
            "mean_rank",
            "mean_paired_cosine",
            "mean_pair_margin",
            "margin_positive_rate",
            "accuracy",
            "macro_f1",
            "auroc",
            "known_detection_auroc",
            "ood_detection_auroc",
            "known_accept_rate_at_train_p05",
            "ood_reject_rate_at_train_p05",
        ],
    )
    cls = to_numeric(cls, ["accuracy", "macro_f1"])

    out: list[str] = []
    out.append("# Stage 2 Lightweight Downstream Task Report\n")
    out.append("This report records the first compact downstream task suite after deciding not to use full species identification as the initial validation target.\n")
    out.append("All data are controlled lightweight simulations. Scores are representation-diagnostic evidence, not clinical mNGS accuracy claims.\n")

    out.append("## 1. Why These Tasks Replace Early Full Species Identification\n")
    out.append("Full mNGS species identification mixes representation quality with database coverage, model capacity, host background, near-neighbor taxonomy, and classifier design. For this subproject, the cleaner question is whether a DNA representation preserves useful information under short-read constraints.\n")
    out.append("The current stage therefore uses small downstream tasks that isolate separate information requirements: perturbation robustness, strand consistency, order, position, quality/contamination, read-length transfer, near-SNP discrimination, and OOD rejection.\n")

    out.append("## 2. Dataset and Run Scope\n")
    out.append("- Dataset: `data/toy_reads/toy_downstream_stress.csv`.\n")
    out.append("- Labels: `GC_rich`, `AT_rich`, `near_SNP`, `host_like`, `same_comp_A/B`, `motif_front/middle/back`.\n")
    out.append("- Conditions: clean, substitutions, N masking, N clusters, trim/crop, reverse complement, indel stress, low-complexity, adapter-like, terminal error gradient.\n")
    out.append("- Main reported read length: 75 bp. Longer and shorter length-transfer curves remain in the earlier first-wave results.\n")

    out.append("## 3. Task Map\n")
    out.append("| Task | Purpose | Training need | Main metric |\n")
    out.append("|---|---|---|---|\n")
    out.append("| T1 paired retrieval | clean-read vs perturbed-read stability | none | top-1, paired cosine, pair margin |\n")
    out.append("| T2 RC consistency | strand-direction invariance | none | paired cosine, margin |\n")
    out.append("| T3 same-composition order | order information beyond composition | tiny classifier | macro-F1 |\n")
    out.append("| T4 motif position | positional information | tiny classifier | macro-F1 |\n")
    out.append("| T5 contamination/QC | low-complexity, adapter, N-like signal | logistic regression | AUROC, macro-F1 |\n")
    out.append("| T7 near-SNP discrimination | near-neighbor strain-like separation | tiny classifier | macro-F1 |\n")
    out.append("| T8 OOD rejection | unknown/read-space separation | centroid similarity | AUROC, reject rate |\n")

    out.append("## 4. T1 Paired Retrieval Under Stress\n")
    paired_best = best_paired_by_condition(
        core,
        [
            "substitution_1pct",
            "substitution_5pct",
            "N_3pct",
            "N_cluster_5pct",
            "trim_to_69",
            "indel_stress",
            "terminal_substitution_gradient",
        ],
    )
    out.append(table(paired_best, ["condition", "representation", "top1", "mean_paired_cosine", "mean_pair_margin", "margin_positive_rate"], 20))
    out.append("\nInterpretation: paired retrieval is useful but still relatively easy at 75 bp. The strongest method depends on the perturbation: one-hot/RoPE-property are strong for substitution-like noise, high-k TF-IDF is strong for indel/trim retrieval, and property-style encodings keep high paired cosine but can have smaller margins because many reads remain close in the same class.\n")

    out.append("## 5. T2 Reverse-Complement Consistency\n")
    rc = core[core["task"] == "rc_consistency"].sort_values("mean_paired_cosine", ascending=False)
    out.append(table(rc, ["representation", "mean_paired_cosine", "mean_pair_margin", "margin_positive_rate", "nearest_rc_hit_rate"], 12))
    out.append("\nInterpretation: canonical k-mer is the correct strong baseline for strand invariance and currently wins this task. This is important: RC pooling should be improved or combined with canonicalization rather than claimed to dominate canonical k-mer.\n")

    out.append("## 6. T5 Contamination / QC Detection\n")
    contam = core[core["task"] == "contamination_detection"].sort_values("auroc", ascending=False)
    out.append(table(contam, ["representation", "accuracy", "macro_f1", "auroc"], 12))
    out.append("\nInterpretation: this task separates representations well. `spaced_kmer_phase`, `property_channels`, `one_hot`, `rc_rope_pool`, and `rope_property` outperform ordinary high-k TF-IDF on this stress set. This is one of the best early downstream tasks for showing practical value without a full species classifier.\n")

    out.append("## 7. T8 OOD Rejection\n")
    ood = core[core["task"] == "ood_rejection"].sort_values("ood_detection_auroc", ascending=False)
    out.append(table(ood, ["representation", "ood_detection_auroc", "known_accept_rate_at_train_p05", "ood_reject_rate_at_train_p05"], 12))
    out.append("\nInterpretation: k-mer count/canonical k-mer currently performs best for centroid-based OOD rejection. This indicates that the best representation may be task-dependent: global composition can be valuable for coarse unknown separation, while prior-aware position encodings help more in QC/order/position tasks.\n")

    out.append("## 8. T3/T4/T7 Lightweight Classification\n")
    out.append("### Same-Composition Order\n")
    out.append(table(best_classification(cls, "same_composition_order"), ["representation", "condition", "classifier", "accuracy", "macro_f1"], 12))
    out.append("\nThis task is too easy in the current synthetic form: many methods reach 1.0. It should be hardened by exact k-mer-spectrum matching or sequence shuffling constraints before being used as a major paper figure.\n")

    out.append("### Motif Position\n")
    out.append(table(best_classification(cls, "motif_position"), ["representation", "condition", "classifier", "accuracy", "macro_f1"], 12))
    out.append("\nThis task validates that base/property/RoPE/codon-frame representations carry position information. It is useful as a controlled positive control but needs jitter and distractor motifs for a stronger paper result.\n")

    out.append("### Near-SNP Discrimination\n")
    out.append(table(best_classification(cls, "near_snp_discrimination"), ["representation", "condition", "classifier", "accuracy", "macro_f1"], 12))
    out.append("\nThis is the hardest current task. Most shallow results hover near chance, with only modest improvements. This is a useful negative result: near-neighbor discrimination likely needs better prototype matching, alignment-aware features, contrastive training, or a small model rather than only flattened handcrafted features.\n")

    out.append("## 9. Current Answer to the Research Design Question\n")
    out.append("We do not need to start with full species identification. A stronger and more publishable early path is to use multiple compact downstream tasks, each linked to a specific information capacity. However, a paper with no downstream task at all would be weak; at minimum it should include retrieval, RC consistency, QC/contamination detection, OOD rejection, and one or two tiny classification tasks.\n")

    out.append("## 10. Method Implications\n")
    out.append("- `canonical k-mer`: best current strand-invariance baseline; must remain in comparisons.\n")
    out.append("- `spaced_kmer_phase`: strongest current candidate for noisy/QC-like tasks and a good bridge between k-mer literature and biological priors.\n")
    out.append("- `property_channels` / `one_hot`: reliable low-cost inputs, especially for shallow CNN or small attention models.\n")
    out.append("- `RoPE-property`: conceptually best suited to future attention models, but flattened evaluation does not fully test its advantage.\n")
    out.append("- `RC pooling`: biologically important but not yet superior to canonical k-mer; it needs redesign or hybridization.\n")
    out.append("- `near-SNP`: current weak point; should become a focused next improvement target, not be hidden.\n")

    out.append("## 11. Next Experiments\n")
    out.append("1. Harden T3 by constructing exact-composition or exact low-k-spectrum matched sequences.\n")
    out.append("2. Harden T4 by adding motif jitter, distractor motifs, and multiple motif families.\n")
    out.append("3. Add a tiny CNN over one-hot/property/spaced-kmer channels for T5 and T7.\n")
    out.append("4. Redesign RC-aware methods as `canonical spaced-kmer + property/phase` hybrids.\n")
    out.append("5. Build a small real-genome-slice benchmark from the Excel-selected species list before making any mNGS-specific claim.\n")

    output = runs / "lightweight_downstream_stage2_report.md"
    output.write_text("\n".join(out), encoding="utf-8")
    print(f"Wrote {output}")


if __name__ == "__main__":
    main()
