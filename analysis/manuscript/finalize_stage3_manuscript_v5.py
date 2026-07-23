from __future__ import annotations

import re
import shutil
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
import scripts.build_stage3_manuscript_v4 as v4  # noqa: E402
import scripts.polish_stage3_manuscript_v4 as polish  # noqa: E402
import scripts.repair_stage3_v4_word_equations as equation_repair  # noqa: E402

MANUSCRIPT = PROJECT_ROOT / "manuscript"
TABLES = MANUSCRIPT / "tables"
MD_PATH = MANUSCRIPT / "stage3_manuscript_v5.md"
DOCX_PATH = MANUSCRIPT / "stage3_manuscript_v5.docx"

REP_LABELS = {
    "ckmer4_count_l2": "CK4 count",
    "ckmer4_property_l2": "CK4+P global",
    "ckmer4_property_multiscale_mean_l2": "CK4+P multi-scale mean",
    "ckmer4_property_multiscale_l2": "CK4+P multi-scale",
    "ckmer4_property_moment_l2": "CK4+P moments",
    "ckmer4_property_anchor_l2": "CK4+P anchor",
    "ckmer5_count_l2": "CK5 count",
    "ckmer5_property_multiscale_l2": "CK5+P multi-scale",
    "cspaced_property_l2": "CSP/spaced-property control",
    "property_channels": "position property channels",
    "one_hot": "position one-hot",
    "base_property": "one-hot + property matrix",
    "rope_property": "RoPE property",
    "rope_onehot": "RoPE one-hot",
    "kmer_property": "position k-mer property",
}


def load_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    return pd.read_csv(path)


def fmt(value: float) -> str:
    if pd.isna(value):
        return ""
    return f"{float(value):.3f}"


def markdown(df: pd.DataFrame, columns: list[str] | None = None, max_rows: int | None = None) -> str:
    if df.empty:
        return "[Table unavailable]"
    out = df.copy()
    if columns is not None:
        out = out[[c for c in columns if c in out.columns]].copy()
    if max_rows is not None:
        out = out.head(max_rows).copy()
    for col in out.columns:
        if pd.api.types.is_float_dtype(out[col]):
            out[col] = out[col].map(lambda x: "" if pd.isna(x) else f"{x:.3f}")
    return out.to_markdown(index=False)


def read_table_md(name: str) -> str:
    path = TABLES / name
    return path.read_text(encoding="utf-8").strip() if path.exists() else "[Table unavailable]"


def grouped_stability(path: Path, focus: list[str]) -> pd.DataFrame:
    df = load_csv(path)
    if df.empty:
        return pd.DataFrame()
    out = (
        df[df["representation"].isin(focus)]
        .groupby("representation", as_index=False)
        .agg(
            paired_cosine=("paired_cosine_mean", "mean"),
            l2_drift=("l2_delta_mean", "mean"),
            retrieval=("retrieval_top1", "mean"),
            mean_features=("n_features", "mean"),
        )
    )
    out["representation_label"] = out["representation"].map(REP_LABELS).fillna(out["representation"])
    out["_order"] = out["representation"].map({rep: i for i, rep in enumerate(focus)})
    return out.sort_values("_order").drop(columns="_order")


def grouped_readout(path: Path, task: str, focus: list[str]) -> pd.DataFrame:
    df = load_csv(path)
    if df.empty:
        return pd.DataFrame()
    df = df[df["task"].eq(task) & df["representation"].isin(focus)].copy()
    out = df.groupby("representation", as_index=False).agg(
        macro_f1=("macro_f1", "mean"),
        accuracy=("accuracy", "mean"),
        mean_features=("n_features", "mean"),
        n_cells=("macro_f1", "count"),
    )
    out["representation_label"] = out["representation"].map(REP_LABELS).fillna(out["representation"])
    return out.sort_values("macro_f1", ascending=False)


def title_block(md: str) -> str:
    replacement = (
        "# Compact biochemical and position-aware priors for ultra-short DNA read representation\n\n\n"
        "**Canonical k-mer identity features, compact biochemical summaries and lightweight positional pooling provide complementary evidence for short-read representation diagnostics**\n\n\n"
        "Author:"
    )
    return re.sub(r"# .*?\n\n\n\*\*.*?\*\*\n\n\nAuthor:", replacement, md, count=1, flags=re.S)


def replace_abstract(md: str) -> str:
    abstract = """
## Abstract

Clinical metagenomic next-generation sequencing often produces short, trimmed or ambiguous reads, but representation choices are still commonly judged by downstream accuracy alone. This can obscure which information is preserved before any classifier is trained. We present a controlled representation-diagnostics framework for ultra-short DNA reads and test three complementary feature families: reverse-complement canonical k-mer identity features, compact biochemical property summaries and lightweight position-aware property pooling. Across WGS-derived perturbation grids, ART Illumina-like simulator profiles and CAMI_TOY_low readout probes, canonical k-mers remained the appropriate identity backbone, whereas biochemical property side channels improved perturbation stability. The most balanced compact representation was canonical 4-mer plus multi-scale property means: it had the highest ART stability among compact CK4/CK5 variants and retained only about 222 features. Controlled motif-position tasks and full-matrix screens showed that fine positional information is accessible when the representation exposes it, but complete position matrices were higher-dimensional and task-specific. A direct full-matrix P-versus-non-P ablation showed that property channels improved ART stability over position one-hot (delta paired cosine 0.044, 95% analysis-cell CI 0.030 to 0.058; delta L2 drift -0.190, -0.228 to -0.152) and gave a small CAMI target/background readout gain (delta macro-F1 0.048, 0.006 to 0.085), while not universally improving controlled motif readout. Spaced-seed CSP was retained as a mechanism and sensitivity control rather than the central method. These results support an architectural conclusion rather than a classifier leaderboard: short-read pipelines should layer exact identity evidence with compact biochemical and position-aware auxiliary evidence, and should treat full positional encodings as upper-bound diagnostics unless larger validation justifies their cost.
""".strip()
    return re.sub(r"## Abstract\n.*?(?=\n## Introduction\n)", abstract + "\n\n", md, flags=re.S)


def replace_intro(md: str) -> str:
    intro = """
## Introduction

Clinical mNGS has become an important route for pathogen detection because it can detect unexpected organisms without a fixed target panel (Wilson et al., 2014; Wilson et al., 2019; Chiu and Miller, 2019). The same setting creates difficult input conditions for computational analysis. Reads may be shortened by adapter and quality trimming, contain ambiguous bases, appear from either strand, or include background and low-biomass artifacts (Martin, 2011; Bolger et al., 2014; Salter et al., 2014). These constraints make representation design more than an engineering detail. Before a classifier, aligner or database index can succeed, the encoding has already decided which sequence properties remain available.

Most mature metagenomic classifiers are built around exact or near-exact word evidence. Kraken, Kraken 2, CLARK, Centrifuge and Kaiju show the practical power of indexed k-mer, minimizer or translated-word matching at scale (Wood and Salzberg, 2014; Wood et al., 2019; Ounit et al., 2015; Kim et al., 2016; Menzel et al., 2016). CAMI benchmarks further show that apparent performance depends on novelty, taxonomic difficulty, abundance structure and database coverage (Sczyrba et al., 2017; Meyer et al., 2022). These observations argue against presenting a small local study as a clinical species-identification leaderboard. They motivate a narrower question: what information does each representation preserve under short-read perturbations, and what is the cost of making that information readable?

This manuscript separates three representational roles. Canonical k-mers provide high-resolution identity evidence. Biochemical property summaries provide compact, interpretable and perturbation-stable side information. Position-aware property pooling attempts to recover limited layout information without flattening a full per-position matrix. Full position encodings, including property channels and RoPE-like variants, are used only as upper-bound diagnostics for what fine positional information can expose.

The resulting claim is deliberately bounded. We do not propose a final clinical taxonomic or resistance classifier. We test whether compact biochemical and position-aware priors can complement canonical k-mer evidence in short-read representation diagnostics. The evidence combines WGS-derived clean-perturbed read pairs, ART Illumina-like simulator profiles, CAMI_TOY_low lightweight readout probes, controlled motif-position tasks and spaced-seed mechanism checks. Accuracy and macro-F1 are interpreted only as downstream readout probes, not as clinical endpoints.
""".strip()
    return re.sub(r"## Introduction\n.*?(?=\n## Related Work\n)", intro + "\n\n", md, flags=re.S)


def replace_terminology(md: str) -> str:
    terminology = """
## Terminology and Contribution

We use one term for one representation family. **CK4** and **CK5** denote reverse-complement canonical contiguous 4-mer and 5-mer count vectors. **P** denotes the biochemical property side channel, including hydrogen-bond class, GC, purine, EIIP-like values, N fraction, entropy and length summaries. **CK4+P** denotes canonical 4-mer counts concatenated with a global property summary. **Multi-scale property pooling** denotes property means or means plus standard deviations computed over 2, 3, 4 and 6 read bins. **Soft positional moments** denote property centers, spread, skew and terminal enrichment. **Anchor-adaptive pooling** denotes exploratory summaries around local high-information anchors. **CSP** denotes the older canonical spaced-property control, implemented as `cspaced_property_l2`; it is retained as a spaced-seed mechanism control, not as the primary method.

The contribution is a representation-diagnostics framework for ultra-short reads. It answers five questions: (i) how much stability a compact biochemical property block adds to canonical k-mer counts, (ii) whether multi-scale positional pooling improves compact side-channel information, (iii) when full position matrices reveal information that compact descriptors cannot, (iv) whether spaced-seed effects are universal or mechanism-specific, and (v) how read length limits context visibility independently of model architecture.

### Representation map and layered evidence architecture

The study treats representation design as a division of labor rather than a one-winner leaderboard. Table 1 summarizes the representation families, their expected strengths and their failure modes.

""".strip()
    table = read_table_md("stage3_table_representation_scheme_summary.md")
    tail = """

![Figure 1. Layered evidence architecture for short-read representation diagnostics.](figures/stage3_fig_layered_evidence_architecture.png)

Figure 1 summarizes the operational interpretation used throughout the manuscript: raw short reads feed exact identity evidence and compact biochemical/position-aware side-channel evidence before any lightweight readout or stability audit. Full position matrices serve as upper-bound diagnostics rather than the default representation.
""".rstrip()
    return re.sub(r"## Terminology and Contribution\n.*?(?=\n## Method\n)", terminology + "\n\n" + table + tail + "\n\n", md, flags=re.S)


def replace_methods(md: str) -> str:
    definitions = r"""
### Representation definitions

Let a DNA read be \(x=x_1,\ldots,x_L\), with \(x_i \in \{A,C,G,T,N\}\). For a contiguous word \(w=x_i,\ldots,x_{i+k-1}\), reverse-complement canonicalization maps \(w\) and \(\operatorname{rc}(w)\) to the same feature index,

\[
\operatorname{canon}(w)=\min_{\mathrm{lex}}(w,\operatorname{rc}(w)).
\]

CK4 and CK5 are L2-normalized canonical k-mer count vectors. The global biochemical property vector \(g(x)\) contains summary statistics of hydrogen-bond class, GC indicator, purine indicator and EIIP-like base values, together with N fraction, normalized length and Shannon entropy. The compact CK4+P representation is

\[
\phi_{\mathrm{CK4+P}}(x)=\operatorname{L2}([\operatorname{L2}(c_{\operatorname{canon-4mer}}(x));g(x)]).
\]

For multi-scale property pooling, the read is partitioned into \(b\in\{2,3,4,6\}\) bins. For each bin, biochemical property means, and optionally standard deviations, are computed and concatenated. The primary compact position-aware representation in the revised manuscript is CK4 plus multi-scale property means. Soft positional moments instead summarize where property mass lies along the read by center, variance, skew and terminal enrichment. Anchor-adaptive pooling is exploratory: it chooses local high-information anchors, such as entropy or rare-k-mer peaks, and summarizes left, right and local property neighborhoods.

CSP uses a spaced seed pattern \(P=(0,2,4,6)\) and is retained as a control for the spaced-seed idea rather than as the manuscript's core method. The spaced token beginning at position \(i\) is \(s_{i,P}(x)=x_{i+p_1}\ldots x_{i+p_m}\), and CSP concatenates reverse-complement canonical spaced counts with the global property vector. The final seed-layout sanity checks therefore support only a conservative default and a mechanism boundary, not a universal optimized spaced seed.

Full position encodings include one-hot, property channels, RoPE-one-hot, RoPE-property, base-property matrices and k-mer property sequences. They are flattened for shallow diagnostic probes. These encodings test whether fine layout information is readable and whether biochemical semantics improve over non-property positional controls, but they are not treated as the main compact method.
""".strip()
    md = re.sub(r"### Representation definitions\n.*?(?=\n### Data sources and perturbations\n)", lambda _m: definitions + "\n\n", md, flags=re.S)
    metrics = """
### Metrics and readout probes

Perturbation stability was measured by paired clean-perturbed cosine similarity, paired L2 drift and nearest-clean retrieval. Compactness was measured by feature dimension and density. Readout probes were shallow diagnostics, primarily nearest centroid and logistic regression. Existing CAMI grids also retained a fixed scikit-learn MLP readout where it had already been generated, but this was treated only as an information-accessibility probe rather than as a neural baseline family. These probes measured whether a signal could be extracted by simple models. They were not interpreted as clinical accuracy estimates.

Ablations separated count-only CK4/CK5 features, global biochemical properties, multi-scale property pooling, soft positional moments, anchor-adaptive pooling, spaced-property CSP and full position encodings. Bootstrap intervals are analysis-cell intervals over length, condition, perturbation or classifier cells. They quantify robustness across the controlled analysis grid and should not be read as clinical sample-level uncertainty.
""".strip()
    md = re.sub(r"### Metrics and readout probes\n.*?(?=\n## Results\n)", metrics + "\n\n", md, flags=re.S)
    return md


def compact_results_text() -> str:
    focus = [
        "ckmer4_count_l2",
        "ckmer4_property_l2",
        "ckmer4_property_multiscale_mean_l2",
        "ckmer4_property_multiscale_l2",
        "ckmer4_property_moment_l2",
        "cspaced_property_l2",
        "ckmer5_count_l2",
        "ckmer5_property_multiscale_l2",
    ]
    wgs = grouped_stability(PROJECT_ROOT / "results/stage3/position_property_ablation/compact_baseline_stability.csv", focus)
    art = grouped_stability(PROJECT_ROOT / "results/stage3/art_ck4p_position_ablation/art_stability_metrics.csv", focus)
    return "\n\n".join(
        [
            "### Biochemical property summaries and multi-scale pooling stabilized compact canonical k-mer features\n\nThe revised compact screen compared count-only canonical k-mers, global CK4+P, multi-scale property pooling, soft moments, CSP and CK5 variants. Across the WGS-derived perturbation grid, CK4+P already improved stability over CK4 count, and adding multi-scale property means gave the best compact stability balance: mean paired cosine 0.991, mean L2 drift 0.116 and about 222 features. CSP remained stable but no longer led the compact screen, supporting its role as a spaced-seed control rather than the primary method.",
            markdown(wgs, ["representation_label", "paired_cosine", "l2_drift", "retrieval", "mean_features"]),
            "ART Illumina-like simulation reinforced the same hierarchy. CK4+P multi-scale mean gave the highest compact ART stability, followed closely by multi-scale standard-deviation and moment variants. Count-only CK4 and CK5 were substantially less stable, while CSP was close to global CK4+P but did not exceed the multi-scale compact variants.",
            markdown(art, ["representation_label", "paired_cosine", "l2_drift", "retrieval", "mean_features"]),
        ]
    )


def readout_results_text() -> str:
    focus = [
        "ckmer4_count_l2",
        "ckmer4_property_l2",
        "ckmer4_property_multiscale_mean_l2",
        "ckmer4_property_multiscale_l2",
        "ckmer4_property_moment_l2",
        "ckmer5_count_l2",
        "ckmer5_property_multiscale_l2",
        "cspaced_property_l2",
    ]
    wgs_target = grouped_readout(PROJECT_ROOT / "results/stage3/position_property_ablation/compact_baseline_readout.csv", "target_background", focus)
    wgs_within = grouped_readout(PROJECT_ROOT / "results/stage3/position_property_ablation/compact_baseline_readout.csv", "within_genus_species", focus)
    cami_target = grouped_readout(PROJECT_ROOT / "results/stage3/cami_ck4p_position_ablation_fast/cami_probe_readout.csv", "target_background", focus)
    cami_label = grouped_readout(PROJECT_ROOT / "results/stage3/cami_ck4p_position_ablation_fast/cami_probe_readout.csv", "label_probe", focus)
    return "\n\n".join(
        [
            "### Readout probes showed task-dependent gains rather than a universal accuracy winner\n\nReadout probes were used only to ask whether the information in a representation was accessible to shallow models. In the WGS-derived target/background probe, CK4+P multi-scale mean had the highest average macro-F1 among the compact variants, whereas within-genus species discrimination remained k-mer-dominated and all compact variants differed only modestly. This supports a representation-level claim, not a species-classifier claim.",
            "WGS target/background readout:",
            markdown(wgs_target, ["representation_label", "macro_f1", "accuracy", "mean_features", "n_cells"], max_rows=8),
            "WGS within-genus species readout:",
            markdown(wgs_within, ["representation_label", "macro_f1", "accuracy", "mean_features", "n_cells"], max_rows=8),
            "The CAMI_TOY_low compact readout probe gave the same caution. CK4+P multi-scale variants were strong in target/background readout, but the label-level probe favored simpler CK4+P global or moment variants and absolute multi-taxon scores remained low. CAMI therefore supports external readability of compact biochemical features, not clinical taxonomic performance.",
            "CAMI target/background readout:",
            markdown(cami_target, ["representation_label", "macro_f1", "accuracy", "mean_features", "n_cells"], max_rows=8),
            "CAMI label-probe readout:",
            markdown(cami_label, ["representation_label", "macro_f1", "accuracy", "mean_features", "n_cells"], max_rows=8),
        ]
    )


def fullmatrix_results_text() -> str:
    return "\n\n".join(
        [
            "### Full-matrix controls separated position resolution from biochemical semantics\n\nFull position encodings were retained as high-resolution diagnostics. In controlled motif-position readout, full position encodings exposed layout information that compact descriptors only partly recovered. However, the P-versus-non-P comparison showed that biochemical semantics were not a universal readout advantage in these controlled tasks: one-hot and RoPE-one-hot were competitive or stronger for some motif-position settings. This is an important boundary, because it prevents us from claiming that biochemical properties automatically dominate exact positional identity.",
            read_table_md("stage3_table_fullmatrix_property_controlled_ci.md"),
            "The same full-matrix comparison was more favorable to biochemical properties under perturbation and external target/background probes. In ART, position property channels improved paired cosine over position one-hot by 0.044 and reduced L2 drift by 0.190; RoPE-property similarly improved over RoPE-one-hot under the same positional transform. In the CAMI target/background smoke probe, property channels gave a small positive macro-F1 delta over one-hot, whereas k-mer property sequences and RoPE-property did not consistently outperform compact k-mer baselines. Full matrices therefore define an upper-bound and mechanism diagnostic, not the paper's main representation.",
            "ART P-versus-non-P deltas:",
            read_table_md("stage3_table_fullmatrix_property_art_delta_ci.md"),
            "CAMI P-versus-non-P deltas:",
            read_table_md("stage3_table_fullmatrix_property_cami_delta_ci.md"),
        ]
    )


def boundary_results_text() -> str:
    return """
### Spaced-seed, context and ARG/SNP diagnostics defined the boundary of the claim

The spaced-seed analyses no longer serve as the main novelty claim. They show a mechanism boundary: spaced seeds can help seed-hit survival when mutations fall in skipped positions, but they can lose when mutations hit sampled positions. The focused seed-layout scan also showed that `P=(0,2,4,6)` was not a universal optimum; `0-1-2-3` ranked highest in the final four-position stability-only sanity check. We therefore keep CSP as a matching-inspired control and avoid presenting S0246 as the source of the paper's innovation.

The attention-context diagnostic was retained only to interpret read-length limits. When two motif/context elements did not both fall inside the observed read, no representation could recover that relation. Once the read length crossed the visibility threshold, position-resolved representations could read it out. This supports the distinction between lost sequence context and insufficient encoding.

Synthetic ARG/SNP probes were kept as boundary checks. They showed that compact stable representations can remain close to perturbed ARG-like reads, but exact allele, resistance-SNP, functional-site and gene-context decisions require canonical k-mer, alignment, protein-domain or curated database evidence. Stability is therefore not biological equivalence.
""".strip()


def replace_results(md: str) -> str:
    results = "\n\n".join(
        [
            "## Results",
            compact_results_text(),
            readout_results_text(),
            fullmatrix_results_text(),
            boundary_results_text(),
        ]
    )
    return re.sub(r"## Results\n.*?(?=\n## Discussion\n)", results + "\n\n", md, flags=re.S)


def replace_discussion_and_end(md: str) -> str:
    discussion = """
## Discussion

The main result is a division of labor among representations. Canonical k-mers remain the most defensible identity backbone. Biochemical properties add compact perturbation-stable side information. Multi-scale property pooling adds a small but useful amount of coarse layout information without flattening a full position matrix. Full position encodings expose more layout information but at substantially higher dimensional cost and with task-specific gains.

This resolves the earlier CSP conflict. Spaced seeds are well motivated as matching and retrieval devices, but their value depends on where mutations fall relative to sampled positions. Used as dense feature summaries, they did not provide a universal advantage over contiguous CK4+P. The manuscript therefore shifts the novelty from S0246 to compact biochemical and position-aware property priors, while retaining CSP as a transparent mechanism control.

The P-versus-non-P full-matrix ablation also sharpens the claim. Property channels were more stable than one-hot under ART-like perturbation and gave a small CAMI target/background readout gain. Yet biochemical semantics did not consistently beat one-hot in controlled motif-position readout. The correct interpretation is not that P is always better than base identity. It is that P supplies a useful perturbation-stable biochemical side channel, while exact identity and fine layout require k-mer or full position evidence.

Accuracy and macro-F1 remain downstream probes in this manuscript. They ask whether a shallow model can read information from a representation. They do not estimate clinical sensitivity, specificity or diagnostic accuracy. The paper's contribution is therefore a representation diagnostic and design principle: layer exact identity evidence with compact biochemical and position-aware auxiliary evidence, and treat read length and context visibility as part of the representation problem.

## Limitations

This study remains a representation-diagnostics study rather than a clinical diagnostic validation. The WGS panel contained 21 genomes from six genera and was designed for controlled mechanism analysis, not for microbial diversity, hospital abundance structure, host depletion, database incompleteness, sample-level uncertainty or wet-lab contamination. ART Illumina-like simulation adds a standard sequencing-error model, but it cannot reproduce all library-preparation artifacts or clinical background mixtures. CAMI_TOY_low provides external read-level truth, but the subset used here supports only lightweight readout probes. Bootstrap intervals are analysis-cell intervals over controlled settings, not population-level clinical uncertainty.

Full-matrix position encodings were tested only in small triage screens. They are sufficient to show that fine position information can be useful and to test P-versus-non-P semantics, but they are not sufficient to promote a high-dimensional full-matrix method as the paper's main contribution. Anchor-adaptive pooling is also exploratory and should remain future work unless anchor stability is tested more directly.

## Future Work

Future work should connect the compact representation layer to end-to-end mNGS pipelines with realistic host/background mixtures, abundance variation, larger genome-held-out panels and independent tools such as Kraken2, Centrifuge and Kaiju. For antimicrobial resistance, curated CARD, ResFinder, AMRFinderPlus and MEGARes/AMR++ tasks should test whether the identity-plus-side-channel architecture helps ARG-family screening without claiming allele or resistance-SNP calls from compact features alone. A larger future position-encoding study could compare full position matrices, learned sequence models and compact property pooling, but that is deliberately outside the present manuscript.

## Conclusions

No single DNA representation dominated all short-read settings. Canonical k-mers preserved identity evidence. Compact biochemical properties improved perturbation stability. Multi-scale property pooling supplied the best current balance between stability, dimension and limited positional information. Full position encodings confirmed that layout information can matter, but their cost and task dependence make them upper-bound diagnostics rather than the default method. The actionable message is architectural: short-read DNA pipelines should layer exact identity evidence with compact biochemical and position-aware auxiliary evidence instead of ranking representations by a single downstream accuracy number.
""".strip()
    return re.sub(r"## Discussion\n.*?(?=\n## Author Information and Submission Metadata\n)", discussion + "\n\n", md, flags=re.S)


def replace_code_availability(md: str) -> str:
    data = (
        "## Code and Data Availability\n\n"
        "All code, generated lightweight reads, result tables, figures and manuscript builders are maintained in the project repository "
        f"({base.REPO_URL}; current local HEAD should be replaced by the final public archive hash after repository cleanup). "
        "The main reproduction path for the revised manuscript is: install `requirements.txt`, then run `scripts/run_stage3_compact_baselines.py`, "
        "`scripts/run_stage3_art_validation.py`, `scripts/run_stage3_cami_probe.py`, `scripts/run_position_property_controlled_tasks.py`, "
        "`scripts/generate_stage3_bootstrap_ci.py`, `scripts/generate_fullmatrix_property_contribution_ci.py`, "
        "`scripts/generate_stage3_manuscript_assets_v2.py` and `scripts/finalize_stage3_manuscript_v5.py`. "
        "The submitted release package should include executable scripts, configuration files, lightweight public/toy datasets, WGS-slice manifests, generated summary tables, figures, manuscript builders and final manuscript files. It should exclude virtual environments, historical drafts, render intermediates, full CAMI archives and bulky ART FASTQ/SAM intermediates; those files can be regenerated or re-extracted from the documented manifests and scripts.\n\n"
    )
    return re.sub(r"## Code and Data Availability\n.*?(?=\n## References\n)", data, md, flags=re.S)


def main() -> None:
    md = polish.polish_text(v4.build_stage3_v4_markdown())
    md = title_block(md)
    md = replace_abstract(md)
    md = replace_intro(md)
    md = replace_terminology(md)
    md = replace_methods(md)
    md = replace_results(md)
    md = replace_discussion_and_end(md)
    md = replace_code_availability(md)
    MD_PATH.write_text(md, encoding="utf-8")
    base.TITLE = "Compact biochemical and position-aware priors for ultra-short DNA read representation"
    base.SUBTITLE = "Canonical k-mer identity features, compact biochemical summaries and lightweight positional pooling provide complementary evidence for short-read representation diagnostics"
    base.DOCX_PATH = DOCX_PATH
    base.build_docx(md)
    equation_repair.patch_docx(DOCX_PATH)
    shutil.copy2(DOCX_PATH, MANUSCRIPT / "final_manuscript.docx")
    shutil.copy2(MD_PATH, MANUSCRIPT / "final_manuscript.md")
    print(f"Finalized {MD_PATH}")
    print(f"Finalized {DOCX_PATH}")
    print(f"Copied v5 manuscript to {MANUSCRIPT / 'final_manuscript.md'} and final_manuscript.docx")


if __name__ == "__main__":
    main()


