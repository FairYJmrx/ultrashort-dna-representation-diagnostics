from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RUNS = PROJECT_ROOT / "results" / "runs"
FIGS = PROJECT_ROOT / "results" / "figures"


def load(path: Path) -> pd.DataFrame:
    return pd.read_csv(path) if path.exists() else pd.DataFrame()


def numeric(df: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    out = df.copy()
    for col in cols:
        if col in out.columns:
            out[col] = pd.to_numeric(out[col], errors="coerce")
    return out


def table(df: pd.DataFrame, cols: list[str], n: int = 12) -> str:
    if df.empty:
        return "_No data._"
    cols = [col for col in cols if col in df.columns]
    return df[cols].head(n).to_markdown(index=False, floatfmt=".4f")


def best_by_rep(df: pd.DataFrame, metric: str = "macro_f1") -> pd.DataFrame:
    if df.empty:
        return df
    return (
        df.sort_values([metric, "accuracy"], ascending=False)
        .groupby("representation", as_index=False)
        .first()
        .sort_values(metric, ascending=False)
    )


def save_bar(df: pd.DataFrame, x: str, y: str, title: str, path: Path, top_n: int = 12) -> None:
    if df.empty:
        return
    FIGS.mkdir(parents=True, exist_ok=True)
    plot_df = df.head(top_n).copy()
    plt.figure(figsize=(10, 5))
    plt.bar(plot_df[x], plot_df[y], color="#3b6ea8")
    plt.xticks(rotation=35, ha="right")
    plt.ylim(0, 1.02)
    plt.ylabel(y)
    plt.title(title)
    plt.tight_layout()
    plt.savefig(path, dpi=180)
    plt.close()


def main() -> None:
    downstream = numeric(load(RUNS / "spaced_hybrid_smoke75" / "lightweight_downstream_results.csv"), ["auroc", "mean_paired_cosine", "mean_pair_margin", "ood_detection_auroc", "accuracy", "macro_f1"])
    hardened = numeric(load(RUNS / "hardened_task_classification75_trainonly" / "classification_results.csv"), ["accuracy", "macro_f1", "n_features"])
    real75 = numeric(load(RUNS / "real_wgs_slice_classification75_trainonly" / "classification_results.csv"), ["accuracy", "macro_f1", "n_features"])
    length_curve = numeric(load(RUNS / "real_wgs_slice_length_curve_trainonly" / "classification_results.csv"), ["accuracy", "macro_f1", "length"])
    hardened_cv = numeric(load(RUNS / "hardened_task_cv75_trainonly" / "classification_results.csv"), ["accuracy", "macro_f1", "macro_f1_std", "n_features"])
    real_cv = numeric(load(RUNS / "real_wgs_slice_cv75_trainonly" / "classification_results.csv"), ["accuracy", "macro_f1", "macro_f1_std", "n_features"])
    kdiag = numeric(load(RUNS / "kmer_diagnostics_first_wave" / "kmer_diagnostics.csv"), ["k", "theoretical_vocab_size", "observed_vocab_size", "avg_nnz_per_read", "density"])

    contam = downstream[downstream["task"] == "contamination_detection"].sort_values("auroc", ascending=False)
    rc = downstream[downstream["task"] == "rc_consistency"].sort_values("mean_paired_cosine", ascending=False)
    ood = downstream[downstream["task"] == "ood_rejection"].sort_values("ood_detection_auroc", ascending=False)
    hardened_order = best_by_rep(hardened[hardened["task"] == "same_spectrum_order"], "macro_f1")
    hardened_motif = best_by_rep(hardened[hardened["task"] == "motif_jitter_position"], "macro_f1")
    real_best = best_by_rep(real75, "macro_f1")

    save_bar(contam, "representation", "auroc", "QC/contamination AUROC at 75 bp", FIGS / "fig_qc_auroc.png")
    save_bar(rc, "representation", "mean_paired_cosine", "Reverse-complement paired cosine at 75 bp", FIGS / "fig_rc_consistency.png")
    save_bar(real_best, "representation", "macro_f1", "Local WGS slice classification at 75 bp", FIGS / "fig_real_wgs_75bp.png")

    if not length_curve.empty:
        FIGS.mkdir(parents=True, exist_ok=True)
        best_len = (
            length_curve.sort_values(["length", "condition", "macro_f1"], ascending=[True, True, False])
            .groupby(["length", "condition"], as_index=False)
            .first()
            .sort_values(["condition", "length"])
        )
        plt.figure(figsize=(8, 5))
        for condition, sub in best_len.groupby("condition"):
            plt.plot(sub["length"], sub["macro_f1"], marker="o", label=condition)
        plt.ylim(0, 1.02)
        plt.xlabel("read length")
        plt.ylabel("best macro-F1")
        plt.title("Best local WGS-slice classification by read length")
        plt.legend()
        plt.tight_layout()
        plt.savefig(FIGS / "fig_length_curve.png", dpi=180)
        plt.close()

    out: list[str] = []
    out.append("# Paper-Level Result Synthesis\n")
    out.append("All classification results in this synthesis use train-only vocabulary/IDF fitting where applicable. Results are lightweight representation diagnostics, not clinical mNGS performance claims.\n")

    out.append("## Datasets\n")
    out.append("- `toy_first_wave.csv`: controlled composition and perturbation data.\n")
    out.append("- `toy_downstream_stress.csv`: controlled perturbation, QC, OOD, near-SNP, order, and motif-position data.\n")
    out.append("- `toy_hardened_tasks.csv`: same short-block multiset order task and motif-position task with jitter/distractors.\n")
    out.append("- `local_wgs_slices.csv`: lightweight reads sampled from local WGS FASTA files for Aspergillus fumigatus, Candida albicans, and two Escherichia coli assemblies.\n")

    out.append("## k-mer Capacity at 75 bp\n")
    if not kdiag.empty:
        d75 = kdiag[(kdiag["length"].astype(str) == "75") & (kdiag["condition"] == "clean")].sort_values("k")
        out.append(table(d75, ["k", "theoretical_vocab_size", "observed_vocab_size", "avg_nnz_per_read", "density"], 20))
    out.append("\nObservation: theoretical vocabulary grows exponentially with k, while each 75 bp read contributes only around `L-k+1` observed words. This supports comparing multiple k values and using canonical/spaced variants rather than assuming larger k is superior.\n")

    out.append("## Strand Consistency\n")
    out.append(table(rc, ["representation", "mean_paired_cosine", "mean_pair_margin", "margin_positive_rate", "nearest_rc_hit_rate"], 12))
    out.append("\nObservation: canonical k-mer and canonical spaced k-mer are the strongest strand-invariant baselines. The proposed canonical spaced property hybrid preserves near-perfect paired cosine while adding property information, but pure canonical k-mer still gives larger margins.\n")

    out.append("## QC / Contamination Detection\n")
    out.append(table(contam, ["representation", "accuracy", "macro_f1", "auroc"], 12))
    out.append("\nObservation: `cspaced_property_l2` is the strongest result in this stage for contamination/QC detection, reaching AUROC above the older spaced-kmer-phase and ordinary k-mer baselines in the compact stress test.\n")

    out.append("## OOD Rejection\n")
    out.append(table(ood, ["representation", "ood_detection_auroc", "known_accept_rate_at_train_p05", "ood_reject_rate_at_train_p05"], 12))
    out.append("\nObservation: spaced and canonical spaced counts are strong for centroid-style OOD rejection, suggesting that global composition and spaced seed coverage remain valuable for coarse unknown separation.\n")

    out.append("## Hardened Same-Spectrum Order Task\n")
    out.append(table(hardened_order, ["representation", "condition", "classifier", "accuracy", "macro_f1", "n_features"], 15))
    out.append("\nObservation: even the hardened short-block order task remains easy for several methods. It is useful as a controlled positive task, but not sufficient as the paper's central evidence.\n")

    out.append("## Hardened Motif-Jitter Position Task\n")
    out.append(table(hardened_motif, ["representation", "condition", "classifier", "accuracy", "macro_f1", "n_features"], 15))
    out.append("\nObservation: motif-position with jitter and distractors supports base/property/RoPE/codon-frame encodings as position-aware representations. MLP helps some high-dimensional encodings but does not change the broad conclusion.\n")

    out.append("## Local WGS Slice Classification at 75 bp\n")
    out.append(table(real_best, ["representation", "condition", "classifier", "accuracy", "macro_f1", "n_features"], 15))
    out.append("\nObservation: the real-genome-slice task is much harder than controlled synthetic tasks. Canonical k-mer remains the strongest baseline. New representations should therefore be framed as complementary diagnostic/robustness features rather than a proven replacement for k-mer classifiers.\n")

    out.append("## 5-fold CV Checks\n")
    if not hardened_cv.empty:
        hcv = hardened_cv[(hardened_cv["split"] == "5fold_cv") & (hardened_cv["task"] == "motif_jitter_position")].sort_values("macro_f1", ascending=False)
        out.append("### Motif-Jitter Position CV\n")
        out.append(table(hcv, ["representation", "condition", "classifier", "accuracy", "macro_f1", "macro_f1_std"], 12))
    if not real_cv.empty:
        rcv = real_cv[(real_cv["split"] == "5fold_cv") & (real_cv["task"] == "real_genome_slice")].sort_values("macro_f1", ascending=False)
        out.append("\n### Local WGS Slice CV\n")
        out.append(table(rcv, ["representation", "condition", "classifier", "accuracy", "macro_f1", "macro_f1_std"], 12))
    out.append("\nObservation: cross-validation supports the same qualitative pattern as the holdout experiments: position-aware encodings are useful on motif-position tasks, while canonical k-mer is the most stable baseline for local genome-slice classification.\n")

    out.append("## Read-Length Curve on Local WGS Slices\n")
    if not length_curve.empty:
        best_len = (
            length_curve.sort_values(["length", "condition", "macro_f1"], ascending=[True, True, False])
            .groupby(["length", "condition"], as_index=False)
            .first()
            .sort_values(["condition", "length"])
        )
        out.append(table(best_len, ["length", "condition", "representation", "classifier", "accuracy", "macro_f1"], 20))
    out.append("\nObservation: longer reads generally help, but the trend is not perfectly linear in this small benchmark. 150 bp improves over 69/75 bp for the best canonical k-mer results.\n")

    out.append("## Publication Claim Boundary\n")
    out.append("Supported: controlled lightweight benchmarks show that biologically informed representations, especially canonical spaced property features, can improve QC/contamination detection and provide interpretable diagnostics of strand, order, and position information in ultra-short reads.\n")
    out.append("Not supported yet: superiority for clinical mNGS species identification or antimicrobial resistance detection. The local WGS slice benchmark shows canonical k-mer remains a strong baseline and full clinical validation is still needed.\n")

    output = RUNS / "paper_level_result_synthesis.md"
    output.write_text("\n".join(out), encoding="utf-8")
    print(f"Wrote {output}")
    print(f"Wrote figures to {FIGS}")


if __name__ == "__main__":
    main()
