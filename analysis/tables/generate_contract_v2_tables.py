"""Generate manuscript LaTeX tables from contract-v2 result files."""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
RESULTS = ROOT / "results" / "stage3" / "contract_v2"
DEFAULT_OUT = ROOT / "manuscript" / "tables" / "contract_v2"


def _write(path: Path, lines: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def compact_table(out: Path) -> None:
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
    _write(out / "table3_contract_v2.tex", lines)


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
    source = pd.read_csv(RESULTS / "compact_baselines" / "stage3_compact_baseline_reads.csv")
    clean = source[source["condition"].eq("clean")].copy()
    clean["assembly_accession"] = clean["notes"].astype(str).str.split(";").str[0]
    genomes = clean[["genus", "species", "assembly_accession"]].drop_duplicates().sort_values(
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


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--outdir", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()
    compact_table(args.outdir)
    mi_table(args.outdir)
    factorial_table(args.outdir)
    scaling_table(args.outdir)
    feature_definition_table(args.outdir)
    genome_accession_table(args.outdir)
    print(f"Wrote contract-v2 LaTeX tables to {args.outdir}")


if __name__ == "__main__":
    main()
