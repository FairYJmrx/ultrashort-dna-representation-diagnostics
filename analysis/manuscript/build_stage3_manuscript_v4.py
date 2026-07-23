from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

import pandas as pd


def _find_project_root(start: Path) -> Path:
    for candidate in [start.parent, *start.parents]:
        if (candidate / "methods").is_dir() and (candidate / "configs").is_dir():
            return candidate
    raise RuntimeError("Could not locate the release repository root.")


PROJECT_ROOT = _find_project_root(Path(__file__).resolve())
sys.path.insert(0, str(PROJECT_ROOT))

import scripts.build_stage2_manuscript as base  # noqa: E402
import scripts.build_stage3_manuscript as stage3  # noqa: E402


MANUSCRIPT = PROJECT_ROOT / "manuscript"
MD_PATH = MANUSCRIPT / "stage3_manuscript_v4.md"
DOCX_PATH = MANUSCRIPT / "stage3_manuscript_v4.docx"

CORE_BOUNDARY_SENTENCE = (
    "CSP provides compact perturbation-stable auxiliary evidence, whereas canonical k-mer/alignment/database evidence "
    "remains necessary for exact identity and functional calls."
)

REP_LABELS = stage3.REP_LABELS


def load_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    return pd.read_csv(path)


def fmt(value: float) -> str:
    return f"{float(value):.3f}"


def git_head() -> str:
    try:
        completed = subprocess.run(
            ["git", "-C", str(PROJECT_ROOT), "rev-parse", "HEAD"],
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        if completed.returncode == 0:
            return completed.stdout.strip()
    except Exception:
        pass
    return "TO_BE_REPORTED_FROM_PUBLIC_ARCHIVE"


def read_ci_table(filename: str, columns: list[str], max_rows: int | None = None) -> pd.DataFrame:
    path = PROJECT_ROOT / "results" / "stage3" / "bootstrap_ci" / filename
    df = load_csv(path)
    if df.empty:
        return pd.DataFrame()
    present = [col for col in columns if col in df.columns]
    out = df[present].copy()
    if max_rows is not None:
        out = out.head(max_rows).copy()
    return out


def representation_scheme_table() -> str:
    path = MANUSCRIPT / "tables" / "stage3_table_representation_scheme_summary.md"
    return path.read_text(encoding="utf-8").strip() if path.exists() else ""


def insert_representation_map(md: str) -> str:
    if "### Representation map and layered evidence architecture" in md:
        return md
    insertion = "\n".join(
        [
            "### Representation map and layered evidence architecture\n",
            CORE_BOUNDARY_SENTENCE,
            "",
            "The study treats representation design as a division of labor rather than a one-winner leaderboard. "
            "Table 1 summarizes what each representation encodes, where it is expected to help, and where it should fail.",
            "",
            representation_scheme_table(),
            "",
            "![Figure 1. Layered evidence architecture for short-read representation diagnostics.](figures/stage3_fig_layered_evidence_architecture.png)",
            "",
            "Figure 1 summarizes the operational interpretation used throughout the manuscript: raw short reads feed exact identity evidence and CSP auxiliary stability evidence as separate branches before any lightweight readout, probe model or confidence audit.",
        ]
    )
    return md.replace("\n\n## Method\n", "\n\n" + insertion + "\n\n## Method\n", 1)


def compact_paragraph_and_table() -> tuple[str, pd.DataFrame]:
    df = load_csv(PROJECT_ROOT / "results" / "stage3" / "compact_baselines" / "compact_baseline_stability.csv")
    by_rep = df.groupby("representation", as_index=False).agg(
        paired_cosine_mean=("paired_cosine_mean", "mean"),
        l2_delta_mean=("l2_delta_mean", "mean"),
        retrieval_top1=("retrieval_top1", "mean"),
        n_features=("n_features", "median"),
    )
    get = lambda rep, col: float(by_rep.loc[by_rep["representation"].eq(rep), col].iloc[0])
    text = (
        "The compact-baseline analysis showed that CSP was not merely benefiting from being smaller than a high-dimensional "
        "k-mer vocabulary. Across the WGS-derived perturbation grid, CSP had mean paired cosine "
        f"{fmt(get('cspaced_property_l2', 'paired_cosine_mean'))}, mean L2 drift "
        f"{fmt(get('cspaced_property_l2', 'l2_delta_mean'))} and top-1 nearest-clean retrieval "
        f"{fmt(get('cspaced_property_l2', 'retrieval_top1'))} with a median of "
        f"{get('cspaced_property_l2', 'n_features'):.0f} features. A compact MinHash control preserved retrieval but drifted more "
        f"(k=5 sketch cosine {fmt(get('minhash_k5_s128', 'paired_cosine_mean'))}, L2 "
        f"{fmt(get('minhash_k5_s128', 'l2_delta_mean'))}), whereas an eight-feature EIIP summary could look stable by cosine "
        f"but lost identity retrieval (retrieval {fmt(get('eiip_summary_l2', 'retrieval_top1'))}). This separated three concepts "
        "that are easily conflated: compactness, perturbation stability and recoverable identity evidence. The table reports analysis-cell bootstrap 95% CIs across length-by-perturbation cells."
    )
    table = read_ci_table(
        "stage3_compact_bootstrap_ci.csv",
        [
            "representation_label",
            "n_cells",
            "paired cosine (95% CI)",
            "L2 drift (95% CI)",
            "top-1 retrieval (95% CI)",
            "median_features",
        ],
    )
    return text, table


def art_paragraph_and_table() -> tuple[str, pd.DataFrame]:
    df = load_csv(PROJECT_ROOT / "results" / "stage3" / "art_illumina" / "art_stability_metrics.csv")
    qdf = load_csv(PROJECT_ROOT / "results" / "stage3" / "art_quality_stratified" / "art_quality_stratified_stability.csv")
    by_rep = df.groupby("representation", as_index=False).agg(
        paired_cosine_mean=("paired_cosine_mean", "mean"),
        l2_delta_mean=("l2_delta_mean", "mean"),
        retrieval_top1=("retrieval_top1", "mean"),
    )
    get = lambda rep, col: float(by_rep.loc[by_rep["representation"].eq(rep), col].iloc[0])
    quality_sentence = ""
    if not qdf.empty:
        cq = qdf[qdf["representation"].eq("cspaced_property_l2")].groupby("quality_bin", as_index=False).agg(
            paired_cosine_mean=("paired_cosine_mean", "mean"),
            l2_delta_mean=("l2_delta_mean", "mean"),
            retrieval_top1=("retrieval_top1", "mean"),
        )
        if not cq.empty and set(cq["quality_bin"].astype(str)) >= {"low", "high"}:
            low = cq[cq["quality_bin"].astype(str).eq("low")].iloc[0]
            high = cq[cq["quality_bin"].astype(str).eq("high")].iloc[0]
            quality_sentence = (
                f" In quality-stratified ART analysis, CSP preserved top-1 retrieval {fmt(low['retrieval_top1'])} in the low-quality stratum "
                f"and {fmt(high['retrieval_top1'])} in the high-quality stratum, with mean paired cosine increasing from "
                f"{fmt(low['paired_cosine_mean'])} to {fmt(high['paired_cosine_mean'])}."
            )
    text = (
        "ART Illumina simulation provided a second noise model with position-dependent sequencing errors rather than only "
        "hand-specified substitutions, N masking or trimming. The same qualitative separation held, but the ART results also "
        "clarified why low numerical drift alone is not enough. EIIP summaries often had the smallest movement "
        f"(mean paired cosine {fmt(get('eiip_summary_l2', 'paired_cosine_mean'))}), but their nearest-clean retrieval averaged only "
        f"{fmt(get('eiip_summary_l2', 'retrieval_top1'))}. EIIP positional signals were also stable under this simulator, but they "
        "are length-dependent positional signals rather than strand-canonical identity summaries. CSP retained perfect retrieval "
        f"across the ART grid in this run while remaining compact (mean paired cosine "
        f"{fmt(get('cspaced_property_l2', 'paired_cosine_mean'))}, mean L2 drift "
        f"{fmt(get('cspaced_property_l2', 'l2_delta_mean'))})."
        + quality_sentence
        + " Thus the ART layer supported the narrower claim that CSP carries stable auxiliary evidence under a field-standard read simulator; it did not convert CSP into a stand-alone classifier. The table reports analysis-cell bootstrap 95% CIs across ART read-length cells."
    )
    table = read_ci_table(
        "stage3_art_bootstrap_ci.csv",
        [
            "representation_label",
            "n_cells",
            "paired cosine (95% CI)",
            "L2 drift (95% CI)",
            "top-1 retrieval (95% CI)",
            "median_features",
        ],
    )
    return text, table


def cami_paragraph_and_table() -> tuple[str, pd.DataFrame]:
    df = load_csv(PROJECT_ROOT / "results" / "stage3" / "cami_probe_expanded" / "cami_probe_readout.csv")
    meta_path = PROJECT_ROOT / "results" / "stage3" / "cami_subset_expanded_metadata.json"
    valid = df.dropna(subset=["macro_f1"]).copy()
    grouped = valid.groupby(["task", "condition", "length", "representation"], as_index=False).agg(
        mean_macro_f1=("macro_f1", "mean"),
        mean_accuracy=("accuracy", "mean"),
    )
    best = (
        grouped.sort_values(["task", "condition", "length", "mean_macro_f1"], ascending=[True, True, True, False])
        .groupby(["task", "condition", "length"], as_index=False)
        .first()
    )
    label_clean_100 = best[
        best["task"].eq("label_probe") & best["condition"].eq("clean") & best["length"].eq(100)
    ].iloc[0]
    target_sub_69 = best[
        best["task"].eq("target_background")
        & best["condition"].eq("substitution_1pct")
        & best["length"].eq(69)
    ].iloc[0]
    n_reads = 24000
    n_labels = 30
    fastq_mib = 32
    mapping_mib = 256
    if meta_path.exists():
        import json

        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        n_reads = int(meta.get("n_labelled_rows_written", n_reads))
        n_labels = int(meta.get("n_labels", n_labels))
        fastq_mib = int(meta.get("fastq_prefix_mib", fastq_mib))
        mapping_mib = int(meta.get("mapping_prefix_mib", mapping_mib))
    label_best_counts = best[best["task"].eq("label_probe")]["representation"].value_counts().to_dict()
    target_best_counts = best[best["task"].eq("target_background")]["representation"].value_counts().to_dict()
    text = (
        "The CAMI_TOY_low probe added an external metagenomic benchmark context with read-level gold mapping and an MLP-compatible readout set. We used a "
        f"range-extracted, labelled subset rather than the full 14.35 GiB tar archive, yielding {n_reads:,} reads across {n_labels} taxon "
        f"labels from {mapping_mib} MiB of gold-mapping prefix and {fastq_mib} MiB of read prefix. Absolute multi-taxon label macro-F1 remained "
        "low, as expected for weak readouts over short anonymous metagenomic reads; the hybrid won "
        f"{int(label_best_counts.get('hybrid_ckmer5_csp', 0))} of 9 label-probe condition-length settings, and the best 100 bp clean label probe was "
        f"{REP_LABELS.get(label_clean_100['representation'], label_clean_100['representation'])} with mean macro-F1 {fmt(label_clean_100['mean_macro_f1'])}. "
        "In the binary target/background probe, compact spaced counts and hybrid features were more often readable than CSP alone: "
        f"canonical spaced count won {int(target_best_counts.get('cspaced_count_l2', 0))} of 9 settings and the hybrid won "
        f"{int(target_best_counts.get('hybrid_ckmer5_csp', 0))} of 9 settings. For example, at 69 bp under 1% substitution, "
        f"{REP_LABELS.get(target_sub_69['representation'], target_sub_69['representation'])} reached mean macro-F1 "
        f"{fmt(target_sub_69['mean_macro_f1'])}. These CAMI results support model-readability of the layered representation idea, but they are not a production metagenomic classifier benchmark. The aggregate table reports analysis-cell bootstrap 95% CIs across task, read length, condition and readout model cells."
    )
    table = read_ci_table(
        "stage3_cami_macro_f1_bootstrap_ci.csv",
        ["task", "representation_label", "n_cells", "macro-F1 (95% CI)", "accuracy (95% CI)", "mean_features"],
    )
    return text, table


def stage3_results_section_v4() -> str:
    compact_text, compact_table = compact_paragraph_and_table()
    art_text, art_table = art_paragraph_and_table()
    cami_text, cami_table = cami_paragraph_and_table()
    return "\n".join(
        [
            "### Stage-3 external validation separated compactness, simulator realism and benchmark readability\n",
            "The stage-3 experiments were added to address three reviewer-level questions that the controlled WGS grid alone could not answer. "
            "First, MinHash and EIIP controls tested whether CSP's advantage was simply a consequence of low dimensionality or numerical DNA coding. "
            "Second, ART Illumina simulation tested whether the stability pattern survived a standard sequencing-error model. Third, CAMI_TOY_low "
            "tested whether the representations remained readable in an external metagenomic benchmark subset with read-level gold mapping. "
            "All confidence intervals in this subsection are analysis-cell bootstrap 95% intervals; they quantify robustness across the controlled grid and should not be read as clinical sample-level uncertainty.\n",
            compact_text,
            base.df_to_markdown(compact_table),
            art_text,
            base.df_to_markdown(art_table),
            cami_text,
            base.df_to_markdown(cami_table),
            "Taken together, the added validation sharpened rather than broadened the claim. CSP was consistently useful as a compact and interpretable "
            "stability block. MinHash and canonical k-mers retained strong identity evidence. EIIP-only summaries showed that low drift without retrieval "
            "is not sufficient. The hybrid route remained the most practical downstream interpretation when both identity evidence and perturbation-stable "
            "auxiliary evidence are needed. "
            + CORE_BOUNDARY_SENTENCE,
        ]
    )


def replace_stage3_results(md: str) -> str:
    pattern = r"### Stage-3 external validation separated compactness, simulator realism and benchmark readability\n.*?(?=\n## Discussion\n)"
    return re.sub(pattern, stage3_results_section_v4() + "\n", md, flags=re.S)



def spaced_pattern_sanity_section() -> str:
    out_dir = PROJECT_ROOT / "results" / "stage3" / "spaced_pattern_sanity"
    cardinality = load_csv(out_dir / "spaced_pattern_sanity_cardinality_summary.csv")
    best4 = load_csv(out_dir / "spaced_pattern_sanity_best_four_position.csv")
    stability = load_csv(out_dir / "spaced_pattern_sanity_stability.csv")
    if cardinality.empty or best4.empty:
        return "### k and spaced-pattern sensitivity argued against a single-parameter recommendation\n\nThe final spaced-pattern sanity outputs were not available when this manuscript was generated."

    csp4 = stability[stability.get("add_property", pd.Series(dtype=bool)).eq(True) & stability.get("cardinality", pd.Series(dtype=int)).eq(4)].copy()
    default = csp4[csp4["pattern"].eq("0-2-4-6")].copy() if not csp4.empty else pd.DataFrame()
    default_cos = float(default["paired_cosine_mean"].mean()) if not default.empty else float("nan")
    default_l2 = float(default["l2_delta_mean"].mean()) if not default.empty else float("nan")
    default_retrieval = float(default["retrieval_top1"].mean()) if not default.empty else float("nan")

    card_view = cardinality[
        [
            "cardinality",
            "role",
            "n_patterns",
            "median_features",
            "mean_paired_cosine",
            "min_paired_cosine",
            "max_paired_cosine",
            "mean_l2_delta",
            "mean_retrieval_top1",
        ]
    ].copy()
    card_view = card_view.rename(
        columns={
            "cardinality": "Seed positions",
            "role": "Scan role",
            "n_patterns": "Patterns",
            "median_features": "Median features",
            "mean_paired_cosine": "Mean paired cosine",
            "min_paired_cosine": "Min paired cosine",
            "max_paired_cosine": "Max paired cosine",
            "mean_l2_delta": "Mean L2 drift",
            "mean_retrieval_top1": "Nearest-clean retrieval",
        }
    )
    best_view = best4.copy()
    best_pattern = str(best4["Best 4-position CSP pattern"].iloc[0]) if not best4.empty else "0-1-2-3"
    text = (
        "### Spaced-pattern sanity supported a conservative default, not an optimized seed\n\n"
        "To prevent the CSP default from being interpreted as a fitted optimum, we added a focused seed-layout sanity check. "
        "The primary scan compared eight four-position patterns at 69 and 75 bp under 3% N masking, 1% substitution and "
        "a 6-bp local mismatch block. Three-position and five-position sets were included only as feature-cardinality sanity "
        "checks, not as an exhaustive seed-design search.\n\n"
        "Four-position CSP used 147 features and averaged paired cosine "
        f"{fmt(float(cardinality.loc[cardinality['cardinality'].eq(4), 'mean_paired_cosine'].iloc[0]))} "
        "across 48 length-by-perturbation-by-pattern cells, with nearest-clean retrieval 1.000. The default `0-2-4-6` pattern remained "
        f"in the same high-stability region (mean cosine {fmt(default_cos)}, mean L2 drift {fmt(default_l2)}, retrieval {fmt(default_retrieval)}). "
        f"The stability-only scan ranked `{best_pattern}` highest in the six four-position length-by-perturbation cells. "
        "We therefore retained `P=(0,2,4,6)` as the conservative default used throughout the main experiments, while treating seed choice "
        "as a sensitivity parameter rather than as a globally optimized design.\n"
    )
    return "\n".join(
        [
            text,
            card_view.to_markdown(index=False, floatfmt=".3f"),
            "",
            "The table below reports the best four-position CSP layout for each perturbation and read length in this focused stability check.",
            "",
            best_view.to_markdown(index=False, floatfmt=".3f"),
        ]
    )


def replace_parameter_sensitivity_section(md: str) -> str:
    pattern = r"### k and spaced-pattern sensitivity argued against a single-parameter recommendation\n.*?(?=\n### Deterministic neural probes showed model compatibility, not neural superiority\n)"
    return re.sub(pattern, spaced_pattern_sanity_section() + "\n", md, flags=re.S)

def replace_code_and_metadata(md: str) -> str:
    metadata = (
        "## Author Information and Submission Metadata\n\n"
        "Author: MEI Ruixiang. Full institutional affiliation, corresponding-author designation, email address, ORCID, funding statement and acknowledgements should be finalized with the supervising group before journal submission. The current working template uses the following conservative defaults until institutional details are supplied: competing interests, none declared; ethics approval, not applicable for controlled simulated reads and public benchmark data; author contributions, conception, implementation, analysis and drafting by MEI Ruixiang with supervisory contributions to be specified before submission.\n\n"
    )
    data = (
        "## Code and Data Availability\n\n"
        "All code, generated lightweight reads, result tables, figures and manuscript builders are maintained in the project repository "
        f"({base.REPO_URL}; release tag v0.3.0-stage3-external-validation; current local HEAD {git_head()}; final public archive hash should be inserted after repository cleanup). "
        "The main reproduction path is: install `requirements.txt`, then run `scripts/run_stage3_compact_baselines.py`, "
        "`scripts/run_stage3_art_generate_and_evaluate.py`, `scripts/summarize_stage3_art_quality.py`, "
        "`scripts/run_stage3_cami_probe.py`, `scripts/generate_stage3_bootstrap_ci.py`, "
        "`scripts/generate_stage3_manuscript_assets_v2.py` and `scripts/build_stage3_manuscript_v4.py`. "
        "Random seeds and single-thread CPU settings are fixed in the experiment scripts where applicable. The submitted code package includes executable scripts, "
        "configuration files, generated summary tables, figures, manuscript builders and the 21-genome close-relative WGS-slice manifest. ART Illumina was obtained "
        "from the official NIEHS distribution and used to generate the stage-3 sequencing-error layer. CAMI_TOY_low was accessed through GigaDB dataset 100344 "
        "(DOI: 10.5524/100344); only a range-extracted labelled subset was cached locally for lightweight probe experiments. Bulky downloaded reference FASTA files "
        "and full CAMI archives are excluded and can be regenerated or re-extracted from the documented manifest and scripts. If journal policy requires public access, "
        "the private repository should be made public or archived with a DOI after double-blind constraints are resolved.\n\n"
    )
    md = re.sub(r"## Code and Data Availability\n.*?(?=\n## References\n)", metadata + data, md, flags=re.S)
    return md


def tighten_claim_language(md: str) -> str:
    replacements = {
        "CSP-alone species identification, ARG allele calling, resistance SNP classification, mobile-element context and plasmid linkage should not be claimed from these data. The correct inference is narrower: CSP supplies compact perturbation-stable auxiliary evidence that can be layered with exact identity evidence.": (
            "CSP-alone species identification, ARG allele calling, resistance SNP classification, mobile-element context and plasmid linkage should not be claimed from these data. The correct inference is narrower: "
            + CORE_BOUNDARY_SENTENCE
        ),
        "canonical k-mers provide high-resolution identity evidence, whereas CSP provides compact, strand-friendly and perturbation-stable auxiliary evidence.": (
            "canonical k-mers provide high-resolution identity evidence, whereas CSP provides compact, strand-friendly and perturbation-stable auxiliary evidence. "
            + CORE_BOUNDARY_SENTENCE
        ),
    }
    for old, new in replacements.items():
        md = md.replace(old, new)
    return md


def build_stage3_v4_markdown() -> str:
    md = stage3.build_stage3_markdown()
    md = insert_representation_map(md)
    md = replace_stage3_results(md)
    md = replace_parameter_sensitivity_section(md)
    md = tighten_claim_language(md)
    md = replace_code_and_metadata(md)
    return md


def main() -> None:
    md = build_stage3_v4_markdown()
    MD_PATH.write_text(md, encoding="utf-8")
    base.DOCX_PATH = DOCX_PATH
    base.build_docx(md)
    print(f"Wrote {MD_PATH}")
    print(f"Wrote {DOCX_PATH}")


if __name__ == "__main__":
    main()

