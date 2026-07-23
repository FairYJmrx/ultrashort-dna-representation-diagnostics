from __future__ import annotations

import re
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


MANUSCRIPT = PROJECT_ROOT / "manuscript"
MD_PATH = MANUSCRIPT / "stage3_manuscript_v3.md"
DOCX_PATH = MANUSCRIPT / "stage3_manuscript_v3.docx"

REP_LABELS = {
    "ckmer5_count_l2": "canonical 5-mer",
    "ckmer7_count_l2": "canonical 7-mer",
    "cspaced_count_l2": "canonical spaced count",
    "cspaced_property_l2": "CSP",
    "hybrid_ckmer5_csp": "canonical 5-mer + CSP",
    "minhash_k5_s128": "MinHash k=5, s=128",
    "minhash_k7_s128": "MinHash k=7, s=128",
    "eiip_l2": "EIIP positional signal",
    "eiip_summary_l2": "EIIP summary",
}


def fmt(value: float) -> str:
    return f"{float(value):.3f}"


def load_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    return pd.read_csv(path)


def representation_summary(df: pd.DataFrame, focus: list[str]) -> pd.DataFrame:
    valid = df[df["representation"].isin(focus)].copy()
    grouped = valid.groupby("representation", as_index=False).agg(
        paired_cosine_mean=("paired_cosine_mean", "mean"),
        l2_delta_mean=("l2_delta_mean", "mean"),
        retrieval_top1=("retrieval_top1", "mean"),
        n_features=("n_features", "median"),
        density=("density", "mean"),
    )
    grouped["Representation"] = grouped["representation"].map(REP_LABELS).fillna(grouped["representation"])
    out = grouped[["Representation", "paired_cosine_mean", "l2_delta_mean", "retrieval_top1", "n_features", "density"]]
    out = out.rename(
        columns={
            "paired_cosine_mean": "mean paired cosine",
            "l2_delta_mean": "mean L2 drift",
            "retrieval_top1": "top-1 retrieval",
            "n_features": "median features",
            "density": "mean density",
        }
    )
    for col in ["mean paired cosine", "mean L2 drift", "top-1 retrieval", "mean density"]:
        out[col] = out[col].map(fmt)
    out["median features"] = out["median features"].map(lambda x: f"{float(x):.0f}")
    order = {name: idx for idx, name in enumerate(focus)}
    out["_order"] = grouped["representation"].map(order).to_numpy()
    return out.sort_values("_order").drop(columns="_order")


def compact_baseline_section() -> tuple[str, pd.DataFrame]:
    path = PROJECT_ROOT / "results" / "stage3" / "compact_baselines" / "compact_baseline_stability.csv"
    df = load_csv(path)
    focus = [
        "cspaced_property_l2",
        "minhash_k5_s128",
        "minhash_k7_s128",
        "eiip_l2",
        "eiip_summary_l2",
        "hybrid_ckmer5_csp",
        "ckmer5_count_l2",
    ]
    table = representation_summary(df, focus)
    by_rep = df.groupby("representation", as_index=False).agg(
        paired_cosine_mean=("paired_cosine_mean", "mean"),
        l2_delta_mean=("l2_delta_mean", "mean"),
        retrieval_top1=("retrieval_top1", "mean"),
        n_features=("n_features", "median"),
    )
    get = lambda rep, col: float(by_rep.loc[by_rep["representation"].eq(rep), col].iloc[0])
    paragraph = (
        "The compact-baseline analysis showed that CSP was not merely benefiting from being smaller than a high-dimensional "
        "k-mer vocabulary. Across the WGS-derived perturbation grid, CSP had mean paired cosine "
        f"{fmt(get('cspaced_property_l2', 'paired_cosine_mean'))}, mean L2 drift "
        f"{fmt(get('cspaced_property_l2', 'l2_delta_mean'))} and top-1 nearest-clean retrieval "
        f"{fmt(get('cspaced_property_l2', 'retrieval_top1'))} with a median of "
        f"{get('cspaced_property_l2', 'n_features'):.0f} features. A compact MinHash control preserved retrieval but drifted more "
        f"(k=5 sketch cosine {fmt(get('minhash_k5_s128', 'paired_cosine_mean'))}, L2 "
        f"{fmt(get('minhash_k5_s128', 'l2_delta_mean'))}), whereas an eight-feature EIIP summary could look stable by cosine "
        f"but lost identity retrieval (retrieval {fmt(get('eiip_summary_l2', 'retrieval_top1'))}). This separated three concepts "
        "that are easily conflated: compactness, perturbation stability and recoverable identity evidence."
    )
    return paragraph, table


def art_section() -> tuple[str, pd.DataFrame]:
    path = PROJECT_ROOT / "results" / "stage3" / "art_illumina" / "art_stability_metrics.csv"
    df = load_csv(path)
    qpath = PROJECT_ROOT / "results" / "stage3" / "art_quality_stratified" / "art_quality_stratified_stability.csv"
    qdf = load_csv(qpath)
    focus = [
        "cspaced_property_l2",
        "eiip_l2",
        "eiip_summary_l2",
        "minhash_k5_s128",
        "ckmer5_count_l2",
        "hybrid_ckmer5_csp",
    ]
    table = representation_summary(df, focus)
    by_rep = df.groupby("representation", as_index=False).agg(
        paired_cosine_mean=("paired_cosine_mean", "mean"),
        l2_delta_mean=("l2_delta_mean", "mean"),
        retrieval_top1=("retrieval_top1", "mean"),
    )
    get = lambda rep, col: float(by_rep.loc[by_rep["representation"].eq(rep), col].iloc[0])
    quality_sentence = ""
    if not qdf.empty and "quality_bin" in qdf.columns:
        cq = qdf[qdf["representation"].eq("cspaced_property_l2")].groupby("quality_bin", as_index=False).agg(
            paired_cosine_mean=("paired_cosine_mean", "mean"),
            l2_delta_mean=("l2_delta_mean", "mean"),
            retrieval_top1=("retrieval_top1", "mean"),
        )
        if not cq.empty:
            low = cq[cq["quality_bin"].astype(str).eq("low")].iloc[0]
            high = cq[cq["quality_bin"].astype(str).eq("high")].iloc[0]
            quality_sentence = (
                f" In quality-stratified ART analysis, CSP preserved top-1 retrieval {fmt(low['retrieval_top1'])} in the low-quality stratum "
                f"and {fmt(high['retrieval_top1'])} in the high-quality stratum, with mean paired cosine increasing from "
                f"{fmt(low['paired_cosine_mean'])} to {fmt(high['paired_cosine_mean'])}."
            )
    paragraph = (
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
        + " Thus the ART layer supported the narrower claim that CSP carries stable auxiliary evidence under a field-standard read simulator; it did not convert CSP into a stand-alone classifier."
    )
    return paragraph, table


def cami_section() -> tuple[str, pd.DataFrame]:
    path = PROJECT_ROOT / "results" / "stage3" / "cami_probe_expanded" / "cami_probe_readout.csv"
    meta_path = PROJECT_ROOT / "results" / "stage3" / "cami_subset_expanded_metadata.json"
    df = load_csv(path)
    valid = df.dropna(subset=["macro_f1"]).copy()
    grouped = valid.groupby(["task", "condition", "length", "representation"], as_index=False).agg(
        mean_macro_f1=("macro_f1", "mean"),
        mean_accuracy=("accuracy", "mean"),
        mean_features=("n_features", "mean"),
    )
    best = (
        grouped.sort_values(["task", "condition", "length", "mean_macro_f1"], ascending=[True, True, True, False])
        .groupby(["task", "condition", "length"], as_index=False)
        .first()
    )
    best["best representation"] = best["representation"].map(REP_LABELS).fillna(best["representation"])
    table = best.rename(
        columns={
            "mean_macro_f1": "mean macro-F1",
            "mean_accuracy": "mean accuracy",
            "mean_features": "mean features",
        }
    )
    table = table[["task", "condition", "length", "best representation", "mean macro-F1", "mean accuracy", "mean features"]]
    for col in ["mean macro-F1", "mean accuracy"]:
        table[col] = table[col].map(fmt)
    table["mean features"] = table["mean features"].map(lambda x: f"{float(x):.0f}")

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
    hybrid_label_wins = int(label_best_counts.get("hybrid_ckmer5_csp", 0))
    spaced_target_wins = int(target_best_counts.get("cspaced_count_l2", 0))
    hybrid_target_wins = int(target_best_counts.get("hybrid_ckmer5_csp", 0))

    paragraph = (
        "The CAMI_TOY_low probe added an external metagenomic benchmark context with read-level gold mapping and an MLP-compatible readout set. We used a "
        f"range-extracted, labelled subset rather than the full 14.35 GiB tar archive, yielding {n_reads:,} reads across {n_labels} taxon "
        f"labels from {mapping_mib} MiB of gold-mapping prefix and {fastq_mib} MiB of read prefix. Absolute multi-taxon label macro-F1 remained "
        "low, as expected for weak readouts over short anonymous metagenomic reads; the hybrid won "
        f"{hybrid_label_wins} of 9 label-probe condition-length settings, and the best 100 bp clean label probe was "
        f"{REP_LABELS.get(label_clean_100['representation'], label_clean_100['representation'])} with mean macro-F1 {fmt(label_clean_100['mean_macro_f1'])}. "
        "In the binary target/background probe, compact spaced counts and hybrid features were more often readable than CSP alone: "
        f"canonical spaced count won {spaced_target_wins} of 9 settings and the hybrid won {hybrid_target_wins} of 9 settings. For example, at 69 bp under "
        f"1% substitution, {REP_LABELS.get(target_sub_69['representation'], target_sub_69['representation'])} reached mean macro-F1 "
        f"{fmt(target_sub_69['mean_macro_f1'])}. These CAMI results support model-readability of the layered representation idea, but they are not a production metagenomic classifier benchmark."
    )
    return paragraph, table


def stage3_results_section() -> str:
    compact_text, compact_table = compact_baseline_section()
    art_text, art_table = art_section()
    cami_text, cami_table = cami_section()
    return "\n".join(
        [
            "### Stage-3 external validation separated compactness, simulator realism and benchmark readability\n",
            "The stage-3 experiments were added to address three reviewer-level questions that the controlled WGS grid alone could not answer. "
            "First, MinHash and EIIP controls tested whether CSP's advantage was simply a consequence of low dimensionality or numerical DNA coding. "
            "Second, ART Illumina simulation tested whether the stability pattern survived a standard sequencing-error model. Third, CAMI_TOY_low "
            "tested whether the representations remained readable in an external metagenomic benchmark subset with read-level gold mapping.\n",
            compact_text,
            base.df_to_markdown(compact_table),
            art_text,
            base.df_to_markdown(art_table),
            cami_text,
            base.df_to_markdown(cami_table),
            "Taken together, the added validation sharpened rather than broadened the claim. CSP was consistently useful as a compact and interpretable "
            "stability block. MinHash and canonical k-mers retained strong identity evidence. EIIP-only summaries showed that low drift without retrieval "
            "is not sufficient. The hybrid route remained the most practical downstream interpretation when both identity evidence and perturbation-stable "
            "auxiliary evidence are needed.",
        ]
    )


def replace_abstract(md: str) -> str:
    abstract = (
        "Clinical metagenomic next-generation sequencing (mNGS) often produces short or quality-trimmed reads, yet DNA representations are still commonly "
        "judged by downstream accuracy alone. This can obscure which information an encoding preserves before any classifier is trained. We present a "
        "controlled representation-diagnostics framework for ultra-short DNA reads and define canonical spaced-property encoding (CSP), a deterministic "
        "feature block that combines reverse-complement canonical spaced-seed counts with interpretable biochemical summaries. Across a close-relative "
        "WGS-slice grid spanning 69, 75, 100, 110, 125, 150 bp and a PE150 proxy, CSP was the top clean-perturbed stability representation in 42 of 42 "
        "length-by-perturbation settings. Stage-3 validation added compact MinHash and EIIP controls, ART Illumina error-profile simulation and a "
        "CAMI_TOY_low readout probe. The compact controls showed that CSP was not merely a low-dimensional numerical code: an EIIP summary could have "
        "very low drift but poor nearest-clean retrieval, whereas CSP retained both compactness and recoverable paired-read identity. ART simulation "
        "supported the same bounded conclusion under platform-like sequencing errors, and the CAMI probe showed that hybrid or compact spaced evidence was often "
        "more readable than either stability-only or identity-only evidence alone in lightweight downstream probes. These results do not establish a "
        "clinical species or resistance classifier. They support a narrower design principle: short-read DNA pipelines should separate exact identity "
        "evidence from compact perturbation-stable auxiliary evidence, rather than ranking representations by a single accuracy number."
    )
    return re.sub(r"## Abstract\n\n.*?\n\n## Introduction", f"## Abstract\n\n\n{abstract}\n\n## Introduction", md, flags=re.S)


def update_methods_language(md: str) -> str:
    replacements = {
        "ART Illumina validation is planned to test whether the same stability patterns hold under a field-standard sequencing-error profile rather than only under hand-specified substitutions, N masking and trimming. CAMI low-complexity data are planned as an external benchmark probe for lightweight readout, not as a production taxonomic-classification leaderboard.": (
            "ART Illumina validation tested whether the same stability patterns held under a field-standard sequencing-error profile rather than only under hand-specified substitutions, N masking and trimming. CAMI low-complexity data were used as an external benchmark probe for lightweight readout, not as a production taxonomic-classification leaderboard."
        ),
        "Stage-3 validation extends this data hierarchy without changing the paper's scope. ART Illumina profiles will be used to generate platform-like sequencing-error reads from the same reference genomes, preserving the stability metrics while replacing hand-specified perturbations with a commonly used read simulator. CAMI low-complexity reads will be processed as an external benchmark subset for target/background or genus-level lightweight readout probes. These additions are designed to test externality and noise-model robustness, not to claim clinical sensitivity or specificity.": (
            "Stage-3 validation extended this data hierarchy without changing the paper's scope. ART Illumina profiles generated platform-like sequencing-error reads from the same reference genomes, preserving paired stability metrics while replacing hand-specified perturbations with a commonly used read simulator. CAMI_TOY_low reads were processed as an external benchmark subset for target/background and multi-taxon lightweight readout probes. These additions tested externality and noise-model robustness, not clinical sensitivity or specificity."
        ),
    }
    for old, new in replacements.items():
        md = md.replace(old, new)
    return md


def replace_stage3_placeholder(md: str) -> str:
    pattern = r"### Planned stage-3 external validation will test simulator and benchmark generality\n.*?(?=\n## Discussion\n)"
    return re.sub(pattern, stage3_results_section() + "\n", md, flags=re.S)


def replace_discussion(md: str) -> str:
    old = (
        "Several conclusions remain deliberately unproven. The neural probe was intentionally small and local; it does not "
        "establish CNN or Transformer superiority on realistic clinical mNGS data. The stage-3 ART and CAMI analyses are "
        "planned to test measurement robustness and external benchmark readability, but they still will not constitute "
        "clinical sensitivity, specificity or production-pipeline validation. Kraken2, Centrifuge, Kaiju, alignment pipelines "
        "and curated CARD/ResFinder/AMRFinderPlus tasks remain the appropriate next layer once the representation-level "
        "evidence is fixed."
    )
    new = (
        "Several conclusions remain deliberately unproven. The neural probe was intentionally small and local; it does not "
        "establish CNN or Transformer superiority on realistic clinical mNGS data. The stage-3 ART and CAMI analyses now "
        "test measurement robustness and external benchmark readability, but they still do not constitute clinical sensitivity, "
        "specificity or production-pipeline validation. Kraken2, Centrifuge, Kaiju, alignment pipelines and curated "
        "CARD/ResFinder/AMRFinderPlus tasks remain the appropriate next layer once the representation-level evidence is fixed."
    )
    return md.replace(old, new)


def replace_future_limitations_and_data(md: str) -> str:
    future = (
        "## Future Work\n\n"
        "Future work will extend the proposed layered evidence architecture into an end-to-end metagenomic workflow. In that larger system, canonical k-mer, "
        "alignment or database evidence should provide high-resolution taxonomic or ARG identity support, while CSP-like auxiliary features provide compact "
        "perturbation-stability, quality-audit and confidence-side information for degraded, N-masked, trimmed or locally mismatched reads. The next stage "
        "should test host/background mixtures, realistic abundance variation, larger genome-held-out panels, clinical sample-level orthogonal validation, "
        "and independent pipeline comparisons with tools such as Kraken2, Centrifuge and Kaiju. For antimicrobial resistance, curated CARD, ResFinder, "
        "AMRFinderPlus and MEGARes/AMR++ tasks should be used to test whether the identity-plus-stability architecture helps ARG-family screening without "
        "claiming allele or resistance-SNP calls from CSP alone.\n\n"
    )
    limitations = (
        "## Limitations\n\n"
        "This study remains a representation-diagnostics study rather than a clinical diagnostic validation. The WGS panel contained 21 genomes from six "
        "genera and was designed for controlled mechanism analysis, not for microbial diversity, hospital abundance structure, host depletion, database "
        "incompleteness, sample-level uncertainty or wet-lab contamination. ART Illumina adds a standard sequencing-error model, but it cannot reproduce "
        "all library-preparation artifacts or clinical background mixtures. CAMI_TOY_low provides external read-level truth, but the subset used here was "
        "range-extracted from a 2x100 bp toy benchmark and therefore supports only 69/75/100 bp external readout probes. The readout models were intentionally "
        "small and deterministic. Therefore, CSP-alone species identification, ARG allele calling, resistance SNP classification, mobile-element context and "
        "plasmid linkage should not be claimed from these data. The correct inference is narrower: CSP supplies compact perturbation-stable auxiliary evidence "
        "that can be layered with exact identity evidence.\n\n"
    )
    data = (
        "## Code and Data Availability\n\n"
        "All code, generated lightweight reads, result tables, figures and manuscript builders are maintained in the project repository "
        f"({base.REPO_URL}; release tag v0.3.0-stage3-external-validation; exact commit hash to be reported from the public archive or cover letter at submission). "
        "Random seeds and single-thread CPU settings are fixed in the experiment scripts where applicable. The submitted code package includes executable scripts, "
        "configuration files, generated summary tables, figures, manuscript builders and the 21-genome close-relative WGS-slice manifest. ART Illumina was obtained "
        "from the official NIEHS distribution and used to generate the stage-3 sequencing-error layer. CAMI_TOY_low was accessed through GigaDB dataset 100344 "
        "(DOI: 10.5524/100344); only a range-extracted labelled subset was cached locally for lightweight probe experiments. Bulky downloaded reference FASTA files "
        "and full CAMI archives are excluded and can be regenerated or re-extracted from the documented manifest and scripts. If journal policy requires public access, "
        "the private repository should be made public or archived with a DOI after double-blind constraints are resolved.\n\n"
    )
    md = re.sub(r"## Future Work\n.*?(?=\n## Limitations\n)", future, md, flags=re.S)
    md = re.sub(r"## Limitations\n.*?(?=\n## Code and Data Availability\n)", limitations, md, flags=re.S)
    md = re.sub(r"## Code and Data Availability\n.*?(?=\n## Conclusions\n)", data, md, flags=re.S)
    return md


def reorder_back_matter(md: str) -> str:
    pattern = (
        r"## Future Work\n(?P<future>.*?)(?=\n## Limitations\n)"
        r"\n## Limitations\n(?P<limitations>.*?)(?=\n## Code and Data Availability\n)"
        r"\n## Code and Data Availability\n(?P<data>.*?)(?=\n## Conclusions\n)"
        r"\n## Conclusions\n(?P<conclusions>.*?)(?=\n## References\n)"
    )
    match = re.search(pattern, md, flags=re.S)
    if not match:
        return md
    replacement = (
        "## Limitations\n"
        f"{match.group('limitations').strip()}\n\n"
        "## Future Work\n"
        f"{match.group('future').strip()}\n\n"
        "## Conclusions\n"
        f"{match.group('conclusions').strip()}\n\n"
        "## Code and Data Availability\n"
        f"{match.group('data').strip()}\n\n"
    )
    return re.sub(pattern, replacement, md, flags=re.S)


def build_stage3_markdown() -> str:
    md = base.build_markdown()
    md = replace_abstract(md)
    md = update_methods_language(md)
    md = replace_stage3_placeholder(md)
    md = replace_discussion(md)
    md = replace_future_limitations_and_data(md)
    md = reorder_back_matter(md)
    md = md.replace("v0.2.1-stage2-mei-submission", "v0.3.0-stage3-external-validation")
    return md


def main() -> None:
    md = build_stage3_markdown()
    MD_PATH.write_text(md, encoding="utf-8")
    base.DOCX_PATH = DOCX_PATH
    base.build_docx(md)
    print(f"Wrote {MD_PATH}")
    print(f"Wrote {DOCX_PATH}")


if __name__ == "__main__":
    main()






