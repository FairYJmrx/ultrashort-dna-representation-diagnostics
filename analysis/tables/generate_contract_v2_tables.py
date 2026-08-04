"""Generate manuscript LaTeX tables from contract-v2 result files."""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
RESULTS = ROOT / "results" / "stage3" / "contract_v2"
DEFAULT_MAIN_OUT = ROOT / "paper_latex" / "tables" / "main"
DEFAULT_SUPP_OUT = ROOT / "paper_latex" / "tables" / "supplementary"


def _write(path: Path, lines: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def compact_table(out: Path, filename: str = "table3_contract_v2.tex") -> None:
    stability = pd.read_csv(RESULTS / "high_k_compressed_baselines" / "high_k_stability_summary.csv")
    readout = pd.read_csv(RESULTS / "high_k_compressed_baselines" / "high_k_readout_summary.csv")
    readout = readout[readout["classifier"].eq("logistic")]
    merged = stability.merge(readout[["representation_label", "macro_f1"]], on="representation_label", how="left")
    order = ["CK4", "CK4+P", "CK4P-MSP", "CK5"]
    merged = merged.set_index("representation_label").loc[order].reset_index()
    lines = [
        r"\begin{tabular}{@{}lrrrr@{}}",
        r"\toprule",
        r"\textbf{representation} & \textbf{paired cosine} & \textbf{L2 drift} & \textbf{logistic macro-F1} & \textbf{features} \\",
        r"\midrule",
    ]
    for row in merged.itertuples(index=False):
        lines.append(
            f"{row.representation_label} & {row.paired_cosine:.3f} & {row.l2_drift:.3f} & "
            f"{row.macro_f1:.3f} & {int(round(row.median_features))} \\\\"
        )
    lines.extend([r"\bottomrule", r"\end{tabular}"])
    _write(out / filename, lines)


def mi_table(out: Path) -> None:
    row = pd.read_csv(RESULTS / "knn_mi_robustness" / "knn_mi_increment_inference.csv").iloc[0]
    lines = [
        r"\begin{tabular}{@{}p{0.25\textwidth}rrrrrr@{}}",
        r"\toprule",
        r"\textbf{contrast} & \textbf{$n$ cells} & \textbf{mean (bits)} & \textbf{95\% CI} & \textbf{Wilcoxon $P$} & \textbf{permutation $P$} & \textbf{$k$} \\",
        r"\midrule",
        (
            r"$\widehat I(d_K,d_P,d_M;Y)-\widehat I(d_K;Y)$"
            f" & {int(row['n_cells'])} & {row['mean_signed_increment_bits']:.3f} & "
            f"[{row['bootstrap_95_ci_low']:.3f}, {row['bootstrap_95_ci_high']:.3f}] & "
            f"{row['wilcoxon_two_sided_p']:.4g} & {row['aggregate_label_permutation_p']:.4g} & "
            f"{int(row['k_neighbors'])} \\\\"
        ),
        r"\bottomrule",
        r"\end{tabular}",
    ]
    _write(out / "table_s3_mi_inference.tex", lines)


def factorial_table(out: Path) -> None:
    frame = pd.read_csv(RESULTS / "local_change_factorial" / "local_change_factorial_conditional_contrasts.csv")
    target_labels = {"spatial_pattern": "spatial localization", "chemistry": "substitution chemistry"}
    lines = [
        r"\begin{tabular}{@{}llrrrr@{}}",
        r"\toprule",
        r"\textbf{conditional block} & \textbf{readout target} & \textbf{full} & \textbf{comparator} & \textbf{$\Delta$ macro-F1 [95\% CI]} & \textbf{BH $q$} \\",
        r"\midrule",
    ]
    for row in frame.itertuples(index=False):
        lines.append(
            f"{row.contrast.replace('|', r'$\mid$')} & {target_labels[row.target]} & "
            f"{row.full_mean:.3f} & {row.comparator_mean:.3f} & {row.mean_macro_f1_difference:.3f} "
            f"[{row.bootstrap_95_ci_low:.3f}, {row.bootstrap_95_ci_high:.3f}] & {row.bh_q:.4g} \\\\"
        )
    lines.extend([r"\bottomrule", r"\end{tabular}"])
    _write(out / "table_s4_factorial_contrasts.tex", lines)


def scaling_table(out: Path) -> None:
    frame = pd.read_csv(RESULTS / "property_scaling" / "property_scaling_summary.csv")
    keep = frame[frame["representation"].str.startswith(("CK4P-MSP_", "CK4+P_"))].copy()
    order = [
        "CK4P-MSP_declared", "CK4P-MSP_unit_range", "CK4P-MSP_train_zscore",
        "CK4+P_declared", "CK4+P_unit_range", "CK4+P_train_zscore",
    ]
    keep = keep.set_index("representation").loc[order].reset_index()
    labels = {
        "declared": "declared maps", "unit_range": "fixed [0,1] maps", "train_zscore": "train-fit coordinate z-score"
    }
    lines = [
        r"\begin{tabular}{@{}llrrr@{}}",
        r"\toprule",
        r"\textbf{representation} & \textbf{property scaling} & \textbf{paired cosine} & \textbf{L2 drift} & \textbf{retrieval} \\",
        r"\midrule",
    ]
    for row in keep.itertuples(index=False):
        representation, scheme = row.representation.rsplit("_", 1)
        if scheme == "zscore":
            representation, scheme = row.representation.rsplit("_train_zscore", 1)[0], "train_zscore"
        elif scheme == "range":
            representation, scheme = row.representation.rsplit("_unit_range", 1)[0], "unit_range"
        lines.append(
            f"{representation} & {labels[scheme]} & {row.paired_cosine:.3f} & {row.l2_drift:.3f} & {row.retrieval_top1:.3f} \\\\"
        )
    lines.extend([r"\bottomrule", r"\end{tabular}"])
    _write(out / "table_s5_property_scaling.tex", lines)


def feature_definition_table(out: Path) -> None:
    lines = [
        r"\begin{tabular}{@{}p{0.13\textwidth}p{0.23\textwidth}p{0.42\textwidth}p{0.10\textwidth}@{}}",
        r"\toprule",
        r"\textbf{block} & \textbf{coordinate family} & \textbf{definition} & \textbf{dimensions} \\",
        r"\midrule",
        r"P & hydrogen-bond class & Mean and population SD of A/T$=2$, C/G$=3$, N$=0$ & 2 \\",
        r"P & GC indicator & Mean and population SD of C/G$=1$, A/T/N$=0$ & 2 \\",
        r"P & purine indicator & Mean and population SD of A/G$=1$, C/T/N$=0$ & 2 \\",
        r"P & EIIP mapping & Mean and population SD of A$=0.1260$, C$=0.1340$, G$=0.0806$, T$=0.1335$, N$=0$ & 2 \\",
        r"P & ambiguity & Fraction of N bases among A/C/G/T/N characters & 1 \\",
        r"P & scaled length & Read length divided by 200 & 1 \\",
        r"P & scaled entropy & Shannon entropy over A/C/G/T/N divided by $\log_2 5$ & 1 \\",
        r"\addlinespace",
        r"MSP & five per-base channels & Hydrogen, GC, purine, EIIP and N-indicator values; mean pooled within each relative-position bin & $5\times15=75$ \\",
        r"MSP & relative-position bins & For each $b\in\{2,3,4,6\}$, edges are $\lfloor jL/b\rfloor$; empty bins use a zero row; the main method excludes within-bin SD & 15 bins \\",
        r"\bottomrule",
        r"\end{tabular}",
    ]
    _write(out / "table_s6_feature_definitions.tex", lines)


def genome_accession_table(out: Path) -> None:
    manifest = pd.read_csv(ROOT / "data" / "real_slices" / "close_relative_genomes_manifest.csv")
    genomes = manifest[["genus", "species", "assembly_accession"]].drop_duplicates().sort_values(
        ["genus", "species"]
    )
    lines = [
        r"\begin{tabular}{@{}lll@{}}",
        r"\toprule",
        r"\textbf{genus} & \textbf{species} & \textbf{NCBI assembly accession} \\",
        r"\midrule",
    ]
    for row in genomes.itertuples(index=False):
        accession = str(row.assembly_accession).replace("_", r"\_")
        lines.append(f"{row.genus} & \\textit{{{row.species}}} & {accession} " + r"\\")
    lines.extend([r"\bottomrule", r"\end{tabular}"])
    _write(out / "table_s7_genome_accessions.tex", lines)


def p_msp_ablation_table(out: Path, filename: str = "table4_p_msp_ablation.tex") -> None:
    stability = pd.read_csv(RESULTS / "p_msp_contribution" / "p_msp_contribution_stability_summary.csv")
    readout = pd.read_csv(RESULTS / "p_msp_contribution" / "p_msp_contribution_delta_readout_summary.csv")
    merged = stability.merge(
        readout.loc[readout["classifier"].eq("logistic"), ["representation_label", "macro_f1_mean"]],
        on="representation_label",
        how="left",
    )
    order = ["CK4", "P", "MSP", "CK4+P", "CK4+MSP", "P+MSP", "CK4P-MSP"]
    merged = merged.set_index("representation_label").loc[order].reset_index()
    roles = {
        "CK4": "local composition and composition-linked retrieval",
        "P": "global property stability without local-composition retrieval",
        "MSP": "coarse positional property readout",
        "CK4+P": "composition plus global property stability",
        "CK4+MSP": "composition plus local-change readability",
        "P+MSP": "stable property-only summary with incomplete retrieval",
        "CK4P-MSP": "balanced block-decomposable trade-off",
    }
    lines = [
        r"\begin{tabular}{@{}p{0.12\textwidth}p{0.08\textwidth}p{0.13\textwidth}p{0.13\textwidth}p{0.17\textwidth}p{0.27\textwidth}@{}}",
        r"\toprule",
        r"\textbf{representation} & \textbf{features} & \textbf{L2 drift} & \textbf{retrieval} & \textbf{grouped macro-F1} & \textbf{observed audit role} \\",
        r"\midrule",
    ]
    for row in merged.itertuples(index=False):
        lines.append(
            f"{row.representation_label} & {int(round(row.n_features))} & {row.l2_delta_mean:.3f} & "
            f"{row.retrieval_top1_mean:.3f} & {row.macro_f1_mean:.3f} & {roles[row.representation_label]} \\\\"
        )
    lines.extend([r"\bottomrule", r"\end{tabular}"])
    _write(out / filename, lines)


def conditional_contrasts_table(out: Path) -> None:
    frame = pd.read_csv(RESULTS / "p_msp_contribution" / "p_msp_contribution_conditional_contrasts.csv")
    lines = [
        r"\begin{tabular}{@{}llllrrl@{}}",
        r"\toprule",
        r"\textbf{block contrast} & \textbf{evidence layer} & \textbf{metric} & \textbf{$n$} & \textbf{full} & \textbf{comparator} & \textbf{improvement [95\% CI]; BH $q$} \\",
        r"\midrule",
    ]
    def fmt_ci(value: float) -> str:
        return f"{value:.4f}" if 0 < abs(value) < 0.001 else f"{value:.3f}"

    def fmt_q(value: float) -> str:
        if value < 0.001:
            exponent = int(f"{value:.1e}".split("e")[1])
            mantissa = value / (10 ** exponent)
            return rf"${mantissa:.1f}\times10^{{{exponent}}}$"
        return f"{value:.3f}"

    def fmt_interval(low: float, high: float) -> str:
        low_text, high_text = fmt_ci(low), fmt_ci(high)
        return f"[${low_text},{high_text}$]"

    for index, row in enumerate(frame.itertuples(index=False)):
        if index in {4, 8}:
            lines.append(r"\addlinespace")
        contrast_label = str(row.contrast).replace("CK4", "K")
        contrast = contrast_label.replace(" | ", r" $\mid$ ")
        layer = "global" if row.evidence_layer == "global_perturbation_stability" else "local"
        metric = "paired cosine" if row.metric == "paired_cosine_mean" else "L2 drift" if row.metric == "l2_delta_mean" else "retrieval" if row.metric == "retrieval_top1" else "grouped macro-F1"
        n = int(row.n_pairs)
        lines.append(
            f"{contrast} & {layer} & {metric} & {n} & {row.full_mean:.3f} & {row.comparator_mean:.3f} & "
            f"${row.mean_improvement_positive_is_better:.3f}$ {fmt_interval(row.bootstrap_95_ci_low, row.bootstrap_95_ci_high)}; "
            f"{fmt_q(row.bh_q)} \\\\"
        )
    lines.extend([r"\bottomrule", r"\end{tabular}"])
    _write(out / "table_s2_conditional_contrasts.tex", lines)


def cami_multitarget_table(out: Path) -> None:
    frame = pd.read_csv(RESULTS / "cami_multitarget_fixed_head" / "cami_multitarget_aggregate.csv")
    order = ["CK4", "CK4+P", "CK4+MSP", "CK4P-MSP", "CK5", "PseKNC", "PseEIIP", "NCP+ANF", "Hashed k=15"]
    frame = frame.set_index("representation_label").loc[order].reset_index()
    lines = [
        r"\begin{tabular}{@{}lrrrrrr@{}}",
        r"\toprule",
        r"\textbf{representation} & \textbf{dimensions} & \textbf{clean F1} & \textbf{shifted F1} & \textbf{minimum target F1} & \textbf{retention} & \textbf{minimum target retention} \\",
        r"\midrule",
    ]
    for row in frame.itertuples(index=False):
        label = "Hashed $k=15$" if row.representation_label == "Hashed k=15" else row.representation_label
        lines.append(
            f"{label} & {int(row.n_features)} & {row.mean_baseline_macro_f1:.3f} & {row.mean_shifted_macro_f1:.3f} & "
            f"{row.min_target_shifted_macro_f1:.3f} & {row.mean_retention:.3f} & {row.min_target_retention:.3f} \\\\"
        )
    lines.extend([r"\bottomrule", r"\end{tabular}"])
    _write(out / "table_s8_cami_multitarget.tex", lines)


def cami_metadata_table(out: Path) -> None:
    frame = pd.read_csv(RESULTS / "cami_multitarget_fixed_head" / "cami_multitarget_target_manifest.csv")
    lines = [
        r"\begin{tabular}{@{}rlllr@{}}",
        r"\toprule",
        r"\textbf{selection rank} & \textbf{NCBI TaxID} & \textbf{scientific name} & \textbf{taxonomic rank} & \textbf{target/background groups} \\",
        r"\midrule",
    ]
    for row in frame.sort_values("selection_rank").itertuples(index=False):
        name = str(row.scientific_name).replace("_", r"\_")
        target_background = f"{int(row.n_target_groups):,}/{int(row.n_background_groups):,}"
        lines.append(f"{int(row.selection_rank)} & {int(row.tax_id)} & \\textit{{{name}}} & {row.taxonomic_rank} & {target_background} \\\\")
    lines.extend([r"\bottomrule", r"\end{tabular}"])
    _write(out / "table_s9_cami_target_metadata.tex", lines)


def cami2_preview_table(out: Path) -> None:
    frame = pd.read_csv(RESULTS / "cami2_marine_stability" / "cami2_marine_figure_source.csv")
    frame = frame.loc[
        frame["condition"].eq("N_3pct") & frame["length"].isin([69, 75, 100])
    ].copy()
    order = {"CK4": 0, "CK4+P": 1, "CK4P-MSP\n(222-dim)": 2, "CK5": 3}
    frame["method_order"] = frame["method"].map(order)
    frame = frame.sort_values(["length", "method_order"])
    lines = [
        r"\begin{tabular}{@{}p{0.07\textwidth}p{0.12\textwidth}p{0.14\textwidth}p{0.08\textwidth}p{0.13\textwidth}p{0.11\textwidth}p{0.09\textwidth}@{}}",
        r"\toprule",
        r"\textbf{length} & \textbf{condition} & \textbf{method} & \textbf{features} & \textbf{paired cosine} & \textbf{L2 drift} & \textbf{top-1} \\",
        r"\midrule",
    ]
    for row in frame.itertuples(index=False):
        method = str(row.method).replace("\n(222-dim)", "")
        condition = str(row.condition).replace("_", r"\_")
        lines.append(
            f"{int(row.length)} & {condition} & {method} & {int(row.n_features)} & "
            f"{row.paired_cosine_mean:.4f} & {row.l2_delta_mean:.4f} & {row.retrieval_top1:.4f} \\\\"
        )
    lines.extend([r"\bottomrule", r"\end{tabular}"])
    _write(out / "table_s10_preview.tex", lines)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--main-outdir", type=Path, default=DEFAULT_MAIN_OUT)
    parser.add_argument("--supp-outdir", type=Path, default=DEFAULT_SUPP_OUT)
    args = parser.parse_args()
    compact_table(args.main_outdir, filename="table3.tex")
    p_msp_ablation_table(args.main_outdir, filename="table4.tex")
    mi_table(args.supp_outdir)
    factorial_table(args.supp_outdir)
    scaling_table(args.supp_outdir)
    feature_definition_table(args.supp_outdir)
    genome_accession_table(args.supp_outdir)
    conditional_contrasts_table(args.supp_outdir)
    cami_multitarget_table(args.supp_outdir)
    cami_metadata_table(args.supp_outdir)
    cami2_preview_table(args.supp_outdir)
    print(
        "Wrote contract-v2 LaTeX tables to "
        f"{args.main_outdir} and {args.supp_outdir}"
    )


if __name__ == "__main__":
    main()
