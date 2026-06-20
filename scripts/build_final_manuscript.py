from __future__ import annotations

import re
from pathlib import Path

import pandas as pd
from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT, WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor

PROJECT_ROOT = Path(__file__).resolve().parents[1]
MANUSCRIPT = PROJECT_ROOT / "manuscript"
TABLES = MANUSCRIPT / "tables"
FIGS = PROJECT_ROOT / "results" / "figures"
REFERENCES = PROJECT_ROOT / "references" / "references.bib"

TITLE = "Information-preservation diagnostics for ultra-short DNA read representations"
SUBTITLE = "A lightweight mNGS-oriented study of k-mer, spaced-seed, biochemical-property and attention-compatible encodings"


def read_table_md(path: Path) -> pd.DataFrame:
    text = path.read_text(encoding="utf-8")
    lines = [line for line in text.splitlines() if line.strip().startswith("|")]
    if len(lines) < 2:
        return pd.DataFrame()
    header = [cell.strip() for cell in lines[0].strip("|").split("|")]
    rows = []
    for line in lines[2:]:
        rows.append([cell.strip() for cell in line.strip("|").split("|")])
    return pd.DataFrame(rows, columns=header)


def df_to_markdown(df: pd.DataFrame) -> str:
    if df.empty:
        return ""
    columns = [str(col) for col in df.columns]
    rows = [[str(value) for value in row] for row in df.astype(str).values.tolist()]
    widths = []
    for idx, col in enumerate(columns):
        values = [row[idx] for row in rows]
        widths.append(max([len(col)] + [len(value) for value in values]))
    header = "| " + " | ".join(col.ljust(widths[idx]) for idx, col in enumerate(columns)) + " |"
    sep = "| " + " | ".join("-" * widths[idx] for idx in range(len(columns))) + " |"
    body = ["| " + " | ".join(row[idx].ljust(widths[idx]) for idx in range(len(columns))) + " |" for row in rows]
    return "\n".join([header, sep] + body)


def bib_entries() -> list[dict[str, str]]:
    text = REFERENCES.read_text(encoding="utf-8")
    blocks = re.split(r"\n(?=@)", text.strip())
    entries: list[dict[str, str]] = []
    for block in blocks:
        key_match = re.match(r"@\w+\{([^,]+),", block)
        if not key_match:
            continue
        entry = {"key": key_match.group(1)}
        for field in ["author", "title", "journal", "year", "volume", "pages", "doi", "eprint", "archivePrefix"]:
            match = re.search(rf"\n\s*{field}\s*=\s*\{{(.*?)\}}\s*,?", block, re.IGNORECASE | re.DOTALL)
            if match:
                entry[field] = re.sub(r"\s+", " ", match.group(1)).strip()
        entries.append(entry)
    return entries


def author_year_citation(entries: list[dict[str, str]], key: str) -> str:
    entry = next((item for item in entries if item.get("key") == key), {"key": key})
    authors = entry.get("author", key).split(" and ")
    first = authors[0].split(",")[0]
    suffix = " et al." if len(authors) > 2 else (f" and {authors[1].split(',')[0]}" if len(authors) == 2 else "")
    return f"{first}{suffix}, {entry.get('year', 'n.d.')}"


def ref_text(entry: dict[str, str]) -> str:
    raw_authors = entry.get("author", "").split(" and ") if entry.get("author") else []
    if len(raw_authors) > 8:
        authors = "; ".join(raw_authors[:8]) + "; et al."
    else:
        authors = "; ".join(raw_authors)
    title = entry.get("title", "")
    year = entry.get("year", "")
    journal = entry.get("journal", "")
    bits = [authors, f"({year})." if year else "", title + "." if title else ""]
    if journal:
        bits.append(journal + ".")
    if entry.get("volume"):
        bits.append(entry["volume"] + ".")
    if entry.get("pages"):
        bits.append(entry["pages"] + ".")
    if entry.get("doi"):
        bits.append("https://doi.org/" + entry["doi"])
    elif entry.get("eprint"):
        prefix = entry.get("archivePrefix", "arXiv")
        bits.append(f"{prefix}:{entry['eprint']}")
    return " ".join(bit for bit in bits if bit).strip()


def build_markdown() -> str:
    refs = bib_entries()
    used_ref_keys: list[str] = []

    def cite(key: str) -> str:
        if key not in used_ref_keys:
            used_ref_keys.append(key)
        return f"({author_year_citation(refs, key)})"

    def cited_entries() -> list[dict[str, str]]:
        entries: list[dict[str, str]] = []
        for key in used_ref_keys:
            entry = next((item for item in refs if item.get("key") == key), None)
            if entry is not None:
                entries.append(entry)
        return entries

    rep_table = read_table_md(TABLES / "table_representation_taxonomy.md")
    prop_table = read_table_md(TABLES / "table_property_ablation.md")
    prop_bootstrap = read_table_md(TABLES / "table_property_ablation_bootstrap.md")
    param_stable = read_table_md(TABLES / "table_parameter_sensitivity_best_stability.md")
    param_class = read_table_md(TABLES / "table_parameter_sensitivity_best_classification.md")
    attention = read_table_md(TABLES / "table_attention_context_visibility.md")

    prop_short = df_to_markdown(prop_table.head(5))
    if prop_bootstrap.empty:
        prop_bootstrap_short = ""
    else:
        boot = prop_bootstrap[
            (prop_bootstrap["condition"] == "N_3pct")
            & (prop_bootstrap["length"].isin(["69", "75", "100", "125", "150", "300"]))
        ].copy()
        boot_display = pd.DataFrame(
            {
                "condition": boot["condition"],
                "length": boot["length"],
                "n": boot["n_pairs"],
                "delta cosine": boot.apply(
                    lambda r: f"{float(r['delta_cosine_mean']):.3f} [{float(r['delta_cosine_ci95_low']):.3f}, {float(r['delta_cosine_ci95_high']):.3f}]",
                    axis=1,
                ),
                "L2 reduction": boot.apply(
                    lambda r: f"{float(r['l2_improvement_mean']):.3f} [{float(r['l2_improvement_ci95_low']):.3f}, {float(r['l2_improvement_ci95_high']):.3f}]",
                    axis=1,
                ),
            }
        )
        prop_bootstrap_short = df_to_markdown(boot_display)
    param_short = df_to_markdown(param_stable[param_stable["condition"] == "N_3pct"])
    class_short = df_to_markdown(param_class)
    attn_short = df_to_markdown(attention[["length", "observed_layout", "pair_visible_rate", "class_motif_visible_rate", "representation", "macro_f1"]])

    md: list[str] = []
    md.append(f"# {TITLE}\n")
    md.append(f"**{SUBTITLE}**\n")
    md.append("## Abstract\n")
    md.append(
        "Ultra-short sequencing reads are common after adapter and quality trimming in clinical metagenomic next-generation sequencing (mNGS), "
        "but DNA read representations are often compared mainly by downstream accuracy. "
        "We instead frame representation choice as an information-preservation problem: which encodings preserve strand symmetry, local composition, "
        "biochemical properties, perturbation stability, positional context and close-relative separability when observed reads are 69-150 bp long, or when paired-end information is simplified as a PE150 proxy? "
        "We compare contiguous k-mers, canonical k-mers, canonical spaced seeds, property-channel encodings, phase-aware encodings and RoPE-like property encodings on controlled reads and a lightweight WGS-slice panel from clinically relevant close-relative genera. "
        "The main proposed representation, canonical spaced-property encoding, concatenates reverse-complement canonical spaced-token counts with low-dimensional DNA property summaries and then applies L2 normalization. "
        "This representation is not a replacement for canonical k-mers. It is a compact, strand-friendly and perturbation-stable auxiliary feature block. "
        "In the WGS-slice perturbation audit, adding property summaries to canonical spaced counts improved clean-versus-perturbed cosine under 3% N masking at 75 bp by 0.028 (95% bootstrap interval 0.027-0.028; n=1680 paired reads) and reduced L2 perturbation by 0.154 (0.152-0.155). "
        "Canonical k-mer and canonical spaced variants remained strong baselines in close-relative classification probes. "
        "A motif-pair diagnostic further showed that read-length effects can be nonlinear for attention-like models: below 150 bp, a class-defining contextual motif pair can be structurally absent, not merely diluted. "
        "The study supports a bounded conclusion: biologically informed auxiliary encodings can expose robustness and context properties that are hidden by accuracy-only benchmarks, whereas clinical species identification and antimicrobial-resistance claims require larger server-scale validation."
    )

    md.append("## Introduction\n")
    md.append(
        "Clinical mNGS has changed pathogen detection because it can identify unexpected organisms without a fixed target panel "
        f"{cite('Wilson2014')} {cite('Wilson2019')} {cite('Chiu2019')}. However, the computational problem is not only organism classification. "
        "Clinical reads may be shortened by adapter and quality trimming, dominated by host or background material, contain ambiguous bases, or originate from either strand "
        f"{cite('Martin2011')} {cite('Bolger2014')} {cite('Salter2014')}. "
        "These constraints make the representation layer scientifically important: before a classifier can succeed, the encoding determines which sequence properties remain available. "
        "We therefore study read representation in a lightweight, reproducible diagnostic setting rather than presenting a clinically validated classifier."
    )
    md.append(
        "Most mature metagenomic classifiers rely on k-mer or related exact-match signals. Kraken, Kraken 2, CLARK, Centrifuge and Kaiju demonstrate how powerful indexed word or translated-word matching can be at scale "
        f"{cite('Wood2014')} {cite('Wood2019')} {cite('Ounit2015')} {cite('Kim2016')} {cite('Menzel2016')}. "
        "Community benchmarks such as CAMI also show that metagenomic tool performance depends strongly on dataset construction, novelty, abundance and taxonomic difficulty "
        f"{cite('Sczyrba2017')} {cite('Meyer2022')}. This argues against using a small local experiment as a clinical leaderboard."
    )
    md.append(
        "Deep learning has also shifted attention from hand-designed word counts to learned sequence representations. "
        "Early DNA and regulatory-sequence models showed that convolutional and recurrent architectures can learn sequence specificity and noncoding regulatory signals "
        f"{cite('Alipanahi2015')} {cite('Zhou2015')} {cite('Quang2016')}. "
        "In metagenomics, DeepMicrobes and MetaTransformer illustrate read-level neural classification, including attention-based models "
        f"{cite('Liang2020')} {cite('Wichmann2023')}. "
        "In broader genomics, DNABERT, DNABERT-2, Nucleotide Transformer, HyenaDNA, Caduceus, GENA-LM and Evo show how pretraining, long-context modeling, reverse-complement-aware architectures and single-nucleotide modeling can be used for DNA sequences "
        f"{cite('Ji2021')} {cite('Zhou2024')} {cite('DallaTorre2025')} {cite('Nguyen2023')} {cite('Schiff2024')} {cite('Fishman2025')} {cite('Nguyen2024Evo')}. "
        "These models motivate a more precise question for short mNGS reads: which information should be injected before learning, and which information is absent regardless of model capacity?"
    )
    md.append(
        "This work makes three bounded contributions. First, it organizes short-read encodings by the information they preserve rather than by model family alone. "
        "Second, it defines and ablates a canonical spaced-property encoding that combines strand-canonical spaced seeds with interpretable biochemical summaries. "
        "Third, it provides lightweight length, perturbation, close-relative and attention-context diagnostics that identify where the proposed encoding is useful and where conventional canonical k-mers remain stronger."
    )

    md.append("## Related Work\n")
    md.append(
        "Alignment-free sequence analysis begins from the premise that exact alignment is not always necessary to compare or classify sequences. "
        "k-mer counting, MinHash sketches and related tools provide efficient word-based representations for genome comparison and metagenomic classification "
        f"{cite('Marcais2011')} {cite('Ondov2016')} {cite('Zielezinski2017')}. "
        "Canonical k-mers are not a single named model but a common strand-symmetry operation: a word and its reverse complement are mapped to the same feature index. "
        "This operation is attractive for mNGS because reads can originate from either strand, but it can also erase strand-specific signals. "
        "Spaced seeds, introduced for sensitive homology search and later adapted to metagenomic classification, provide a mismatch-tolerant alternative to contiguous words "
        f"{cite('Ma2002')} {cite('Brinda2015')}."
    )
    md.append(
        "DNA can also be treated as a signal or numerical sequence. Shannon information theory provides language for uncertainty and information loss "
        f"{cite('Shannon1948')}, while chaos game representation, genomic signal processing and EIIP-style mappings show that bases can be converted into numeric, compositional or physicochemical channels "
        f"{cite('Jeffrey1990')} {cite('Voss1992')} {cite('Anastassiou2001')} {cite('Cristea2002')} {cite('Nair2006')}. "
        "Vector representations of variable-length k-mers provide another bridge between discrete words and continuous embeddings "
        f"{cite('Ng2017')}. "
        "Our property encodings follow this tradition but are intentionally modest: they summarize GC status, purine class, hydrogen-bond class, EIIP-like values, N fraction, length and entropy as interpretable auxiliary features rather than learned embeddings."
    )
    md.append(
        "Transformer-style encodings add a separate issue: position and co-occurrence. Self-attention can connect all observed tokens "
        f"{cite('Vaswani2017')}, and rotary position embeddings provide a compact relative-position mechanism "
        f"{cite('Su2021')}. But attention cannot attend to a motif that has been trimmed away. This distinction motivates our context-visibility diagnostic."
    )
    md.append(
        "Antimicrobial-resistance (AMR) and ARG detection add a stricter biological target than taxonomic assignment. "
        "Practical systems and databases such as CARD, AMRFinderPlus, ResFinder and MEGARes/AMR++ encode curated gene families, protein evidence, mutation rules or high-throughput resistome workflows "
        f"{cite('Alcock2023')} {cite('Feldgarden2021')} {cite('Bortolaia2020')} {cite('Bonin2023')}. "
        "DeepARG further shows that learned models can be applied to ARG prediction from metagenomic data "
        f"{cite('ArangoArgoty2018')}. "
        "Our experiments do not claim AMR calling ability. They instead ask whether compact property-aware representations could serve as auxiliary robustness or interpretability features for future ARG tasks."
    )

    md.append("## Problem Formulation\n")
    md.append(
        "Let a DNA read be a sequence x = (x1, ..., xL), xi in {A,C,G,T,N}. A representation is a map phi(x) into either a fixed vector or a token sequence. "
        "The paper evaluates phi by information properties rather than by assuming one downstream classifier is definitive. "
        "For a diagnostic representation study, the relevant question is not only whether phi improves one accuracy number, but whether it preserves a stated source of information under a stated constraint."
    )
    md.append(
        "For a contiguous k-mer word w = x_i...x_{i+k-1}, the ordinary count vector stores c_w(x). "
        "The reverse-complement canonical form is canon(w) = min(w, rc(w)) under lexicographic order, so the canonical k-mer count feature is c_canon(w)(x). "
        "This operation is expected to improve strand consistency but may discard strand-specific information. "
        "In this manuscript, canonical k-mers are therefore treated as a strong strand-symmetric baseline rather than as a method to be displaced."
    )
    md.append(
        "For a spaced seed pattern P = (p1, ..., pm), a spaced token is s_i,P(x) = x_{i+p1}...x_{i+pm}. "
        "In the default implementation P=(0,2,4,6), but the sensitivity audit also evaluates alternative patterns. "
        "A canonical spaced representation counts canon(s_i,P) over the observed training vocabulary and L2-normalizes the count vector. "
        "The proposed canonical spaced-property representation adds a property vector g(x). "
        "For each read, g(x) contains the mean and standard deviation of four base-level channels: hydrogen-bond class H(A,T)=2 and H(C,G)=3; GC indicator; purine indicator R(A,G)=1 and R(C,T)=0; and EIIP-like numerical value. "
        "It also contains the N fraction, length/200 scaling and Shannon entropy scaled by log2(5). "
        "The final representation is phi_CSP(x) = L2([L2(c_canon-spaced(x)); g(x)]). "
        "In code this method is named `cspaced_property_l2`; in the manuscript we call it canonical spaced-property encoding."
    )
    md.append(
        "The ablation design separates the priors that are otherwise fused in the proposed representation: contiguous versus spaced tokens, noncanonical versus canonical reverse-complement pooling, canonical spaced counts with versus without property summaries, property tokens with versus without phase terms, and RoPE-like position handling with one-hot versus property channels. "
        "We evaluate five information properties: compactness, reverse-complement consistency, perturbation stability, read-length/context visibility and close-relative separability. "
        "Accuracy and macro-F1 are used only as tertiary probes: they test whether a simple readout can extract a signal from a representation, not whether the representation is clinically diagnostic."
    )

    md.append("## Experimental Design\n")
    md.append(
        "The local panel contains 21 genomes from six clinically relevant genera: Acinetobacter, Burkholderia, Candida, Enterobacter, Escherichia and Klebsiella. "
        "Reads were sampled as 69, 75, 100, 125 and 150 bp single-end fragments plus a PE150 proxy represented by 300 bp concatenated end information. "
        "Perturbations included reverse complement, 3% N masking and 1% substitution. "
        "The panel is intentionally lightweight and close-relative-biased; it is a stress test, not a universal microbial benchmark. "
        "The PE150 proxy captures the information available from two read ends as a simplified 300 bp representation and is not a full paired-end insert, overlap or quality-score simulation."
    )
    md.append(
        "The close-relative panel is intentionally biased toward genera where species-level boundaries can be difficult for short reads. "
        "It is useful for finding failure modes, but it is not a representative sample of all bacteria, fungi or clinical backgrounds. "
        "Therefore all classification numbers in this manuscript are treated as signal-readability probes. "
        "They are not clinical sensitivity, specificity or diagnostic accuracy estimates."
    )
    md.append(
        "We also used a controlled attention/context diagnostic. Latent templates contain a shared anchor motif near position 18 and a class-specific motif near position 138. "
        "Short reads can include the anchor while excluding the class motif. This design tests whether read shortening removes an entire semantic relation rather than only a proportional number of bases."
    )
    md.append(
        "The metric hierarchy is fixed before interpreting results. Primary metrics are dimensionality, sparsity, paired cosine, perturbation L2 delta, component deltas and motif-pair visibility. "
        "Secondary metrics include close-relative stress probes. Tertiary metrics include accuracy and macro-F1 from nearest-centroid or lightweight linear readouts. "
        "For the main property-ablation claim we add a paired-read bootstrap interval with 1000 resamples. "
        "Other p05 and p95 values in the tables are descriptive quantiles of the local sampled audit, not population-level confidence intervals."
    )

    md.append("## Results\n")
    md.append("### Canonical spaced-property encoding has its clearest advantage in perturbation stability\n")
    md.append(
        "The strongest supported advantage of canonical spaced-property encoding is robustness, especially under N masking. "
        "Adding property summaries to canonical spaced counts consistently increased clean-versus-perturbed cosine and reduced L2 change across 69 bp, 75 bp, 100 bp, 125 bp, 150 bp and the PE150 proxy. "
        "Under 3% N masking at 75 bp, cosine increased by 0.028 with a 95% paired bootstrap interval of 0.027-0.028, and mean L2 perturbation decreased by 0.154 with an interval of 0.152-0.155 (n=1680 paired reads; 1000 bootstrap resamples). "
        "The largest N-masking improvement was observed at 69 bp, where cosine increased by 0.031 and L2 perturbation decreased by 0.163. "
        "The effect decreased with read length, which is plausible because longer reads provide more redundant word evidence."
    )
    md.append(prop_short)
    md.append(
        "The table below reports the N-masking bootstrap audit for the fused property component. Brackets denote 95% bootstrap intervals over paired clean-perturbed reads."
    )
    md.append(prop_bootstrap_short)
    md.append("![Figure 1. Perturbation stability across read lengths.](../results/figures/fig_publication_perturbation_stability.png)")
    md.append("![Figure 2. Component ablation for DNA property summaries.](../results/figures/fig_publication_property_ablation.png)")

    md.append("### Canonicalization, not property summaries alone, explains strand symmetry\n")
    md.append(
        "Reverse-complement robustness was dominated by canonicalization. Canonical contiguous k-mers achieved paired cosine near 1.0 under reverse complement, whereas noncanonical contiguous k-mers had much lower paired cosine. "
        "The canonical spaced-property representation inherits this property from canonical spaced tokens. Therefore the manuscript should not attribute strand invariance to biochemical property summaries alone."
    )

    md.append("### k and spaced-seed pattern sensitivity argues against a single-parameter claim\n")
    md.append(
        "A reviewer would reasonably ask why k=5 or why pattern (0,2,4,6) was selected. We therefore ran a lightweight sensitivity audit over k=4-7 and three spaced patterns. "
        "For N masking, canonical spaced-property variants remained the stability winners across all read lengths in the sampled audit, with paired cosine between 0.994 and 0.997. "
        "However, downstream close-relative probes were parameter-sensitive: the best readout settings changed with task and length. "
        "This result supports a representation-diagnostics paper rather than a universal k or pattern recommendation. "
        "The practical interpretation is that k and spacing should be selected according to the target information property: exact local resolution, mismatch tolerance, robustness to ambiguous bases or model-compatible dense input."
    )
    md.append(param_short)
    md.append("![Figure 3. Parameter sensitivity for k and spaced-seed patterns.](../results/figures/fig_publication_parameter_sensitivity.png)")

    md.append("### Read length can erase context relations relevant to attention-like models\n")
    md.append(
        "The attention/context diagnostic supports the hypothesis tested here: the loss caused by short reads is not always linear in base count. "
        "At 69, 75 and 100 bp the class-defining motif was absent, pair visibility was 0, and lightweight readouts stayed near chance. "
        "At 125 bp, accidental partial-prefix matches appeared but full pair visibility remained essentially absent. "
        "At 150 bp and PE150, the pair became fully visible and simple readouts reached perfect or near-perfect macro-F1. "
        "A Transformer with self-attention would have many token pairs even at 69 bp, but those pairs cannot include a missing class motif. "
        "This is the DNA-read analogue of a language model receiving only the opening fragment of a phrase: the architecture can model relationships among observed tokens, but the intended semantic relation is unavailable if one side of the relation is absent."
    )
    md.append(attn_short)
    md.append("![Figure 4. Context visibility as read length increases.](../results/figures/fig_attention_context_visibility.png)")
    md.append("![Figure 5. Classification probe transition when the motif pair becomes visible.](../results/figures/fig_attention_context_classification.png)")

    md.append("### Close-relative classification is a stress probe, not the paper's main endpoint\n")
    md.append(
        "The close-relative WGS-slice benchmark deliberately tests a harder situation than artificial composition tasks. "
        "It does not support a broad claim that the proposed method is better for species identification. "
        "Canonical k-mer and canonical spaced variants remained strong baselines. In the clean within-genus species probe, the best averaged readout in the core comparison was canonical spaced at 125 bp. "
        "In the target/background probe, canonical spaced-property was best at the PE150 proxy. "
        "In the k/pattern sensitivity audit, best settings varied by task: target/background at 75 bp favored canonical spaced pattern 0-1-3-6, while within-genus probes favored different k-mer or spaced settings depending on length. "
        "Because the panel is small and genus-biased, these results define local advantage regions and failure modes; they do not establish broad species-identification superiority."
    )
    md.append(class_short)
    md.append("![Figure 6. Close-relative WGS-slice classification probes.](../results/figures/fig_publication_close_relative_probes.png)")

    md.append("## Model Suitability and Application Boundaries\n")
    md.append(
        "In this diagnostic setting, different encodings suggest different model pairings. "
        "Canonical k-mer counts remain suitable for nearest-centroid, linear and database-index-like readouts because they expose exact local composition with strand symmetry. "
        "Canonical spaced counts provide a compact, mismatch-tolerant alternative. "
        "Canonical spaced-property encoding is best interpreted as an auxiliary dense feature block for robustness audits, perturbation-aware screening or concatenation with stronger exact-match features. "
        "Property channels and RoPE-property encodings are more natural inputs for CNNs or attention models because they preserve per-position numeric channels and positional phase information. "
        "The present study does not test Transformer superiority; it identifies when attention-compatible features have enough observed context to be meaningful."
    )
    md.append(
        "The advantage region for canonical spaced-property encoding is therefore narrow but real: ultra-short or lightly degraded reads, strand-ambiguous inputs, N masking, representation drift audits, and small readouts that benefit from low-dimensional biochemical summaries. "
        "It is expected to be weaker for close-relative strain resolution, allele-level ARG calling, resistance SNPs, mobile-element context, plasmid linkage, abundance estimation and any task where exact gene identity or protein-domain evidence dominates. "
        "For ARG analysis, a property-aware feature block should be tested as an adjunct to CARD/AMRFinderPlus/ResFinder-style sequence evidence, not as a replacement for curated resistance rules. "
        "Its plausible value in ARG work is interpretability and robustness auditing: for example, detecting when ambiguous bases or trimming change a read's biochemical summary while exact-match evidence remains uncertain."
    )

    md.append("## Discussion\n")
    md.append(
        "The central conclusion is deliberately narrower than a classification claim. Ultra-short DNA read representations differ in what they make stable, compact and visible. "
        "Canonical k-mers remain strong close-relative baselines. Canonical spaced-property encoding contributes a different advantage: compact perturbation stability and interpretability. "
        "This division is scientifically useful because mNGS workflows face both taxonomic discrimination and robustness/QC problems."
    )
    md.append(
        "The study also clarifies the role of accuracy. Accuracy and macro-F1 are helpful only when they are interpreted as readout probes. "
        "If written as clinical endpoints, the current experiments would be underpowered and non-representative. "
        "If written as representation diagnostics, they help map advantage regions and failure modes. "
        "This resolves the apparent tension between the local classification probes and the paper's purpose: accuracy is not the main claim, but it is useful evidence that a representation's preserved signal can be read by a simple model."
    )
    md.append(
        "Several claims require server-scale follow-up. A larger panel should include many strains per close-relative complex, realistic FASTQ quality profiles, host/background mixtures, abundance variation and repeated random seeds. "
        "A tiny CNN/Transformer comparison should test whether property and RoPE-property channels help when the model can learn local or global interactions. "
        "Kraken2/Centrifuge/Kaiju audits would connect representation diagnostics to clinical-pipeline baselines, and a CARD/AMRFinderPlus/ResFinder-grounded ARG task would be needed before making resistance-detection claims."
    )

    md.append("## Methods\n")
    md.append(
        "Genome metadata were selected from the local blood-panel spreadsheet and available WGS FASTA sources. Missing close-relative genomes were retrieved using NCBI Datasets when available. "
        "The reproducible scripts generate the close-relative manifest, sampled reads, perturbations, representation matrices, ablation metrics, sensitivity audits, figures and this manuscript. "
        "No heavy neural model was trained locally. Nearest-centroid and lightweight linear probes were used only to test signal readability."
    )
    md.append(
        "Reverse-complement consistency was measured by paired cosine between a clean read and its reverse complement after representation. "
        "Perturbation stability was measured by paired cosine and L2 distance between clean and perturbed representations. "
        "Component ablation compared matched representations that differed by one prior: canonicalization, spaced seeding, property summary, phase or RoPE-like position handling."
    )
    md.append(
        "For the WGS-slice property-ablation audit, paired clean-perturbed comparisons used 1680 paired reads for each length and perturbation condition. "
        "Bootstrap intervals for the difference between canonical spaced-property and canonical spaced counts were computed by resampling paired read-level deltas 1000 times with a fixed seed. "
        "The interval is therefore conditional on this sampled panel and should not be interpreted as a population-level clinical confidence interval."
    )
    md.append(
        "Parameter sensitivity was run as a sampled audit. Stability used at most 120 paired reads per length/condition, k=4-7 and three spaced patterns. "
        "Classification sensitivity used 75, 150 and PE150 proxy lengths with at most 80 reads per genus. These limits make the audit reproducible on the local computer and should be expanded on a server for stronger statistical inference."
    )

    md.append("## Data and Code Availability\n")
    md.append(
        "The code repository contains the read-generation scripts, representation builders, analysis workflows, result tables, figures and manuscript builder. "
        "Large downloaded reference genomes are not treated as manuscript evidence and should be regenerated from accession manifests when needed. "
        "The repository is intended to archive lightweight reproducibility artifacts while excluding environment folders and bulky downloaded FASTA files."
    )

    md.append("## Limitations\n")
    md.append(
        "The experiments are lightweight and not clinically representative. The close-relative panel has 21 genomes from six genera, so it cannot represent the microbial tree, host background, contamination spectrum, epidemiology or clinical sample complexity. "
        "The classification probes use simple readouts and are intentionally not clinical performance estimates. "
        "The attention diagnostic is synthetic; it demonstrates structural context loss but does not evaluate a full Transformer. "
        "The property channels are interpretable but may not capture all biologically relevant chemistry or evolutionary constraints. "
        "The study does not evaluate real AMR/ARG calling, so resistance-detection use remains a hypothesis for future validation."
    )

    md.append("## Conclusions\n")
    md.append(
        "The safest conclusion is that no single DNA representation dominates all short-read mNGS-like settings. "
        "Canonical k-mer remains a strong close-relative classification backbone. "
        "Canonical spaced-property encoding is a compact, strand-friendly and perturbation-stable auxiliary representation with a clear advantage region in robustness diagnostics. "
        "Attention-compatible encodings should be evaluated with explicit context-visibility tests because short reads can delete whole motif relations. "
        "The resulting paper should be positioned as a representation-diagnostics study and a foundation for larger mNGS and AMR validation, not as a final clinical classifier."
    )

    md.append("## References\n")
    for i, entry in enumerate(cited_entries(), 1):
        md.append(f"{i}. {ref_text(entry)}")

    return "\n\n".join(md) + "\n"


def set_cell_shading(cell, fill: str) -> None:
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:fill"), fill)
    tc_pr.append(shd)


def set_cell_width(cell, width_dxa: int) -> None:
    tc_pr = cell._tc.get_or_add_tcPr()
    tc_w = tc_pr.first_child_found_in("w:tcW")
    if tc_w is None:
        tc_w = OxmlElement("w:tcW")
        tc_pr.append(tc_w)
    tc_w.set(qn("w:w"), str(width_dxa))
    tc_w.set(qn("w:type"), "dxa")


def set_cell_margins(table, top=80, start=120, bottom=80, end=120) -> None:
    tbl_pr = table._tbl.tblPr
    tbl_cell_mar = tbl_pr.find(qn("w:tblCellMar"))
    if tbl_cell_mar is None:
        tbl_cell_mar = OxmlElement("w:tblCellMar")
        tbl_pr.append(tbl_cell_mar)
    for m, v in [("top", top), ("start", start), ("bottom", bottom), ("end", end)]:
        node = tbl_cell_mar.find(qn(f"w:{m}"))
        if node is None:
            node = OxmlElement(f"w:{m}")
            tbl_cell_mar.append(node)
        node.set(qn("w:w"), str(v))
        node.set(qn("w:type"), "dxa")


def set_table_width(table, widths: list[int]) -> None:
    table.autofit = False
    table.alignment = WD_TABLE_ALIGNMENT.LEFT
    tbl_pr = table._tbl.tblPr
    tbl_w = tbl_pr.find(qn("w:tblW"))
    if tbl_w is None:
        tbl_w = OxmlElement("w:tblW")
        tbl_pr.append(tbl_w)
    tbl_w.set(qn("w:w"), str(sum(widths)))
    tbl_w.set(qn("w:type"), "dxa")
    tbl_ind = tbl_pr.find(qn("w:tblInd"))
    if tbl_ind is None:
        tbl_ind = OxmlElement("w:tblInd")
        tbl_pr.append(tbl_ind)
    tbl_ind.set(qn("w:w"), "120")
    tbl_ind.set(qn("w:type"), "dxa")
    grid = table._tbl.tblGrid
    if grid is None:
        grid = OxmlElement("w:tblGrid")
        table._tbl.insert(0, grid)
    for child in list(grid):
        grid.remove(child)
    for width in widths:
        col = OxmlElement("w:gridCol")
        col.set(qn("w:w"), str(width))
        grid.append(col)
    for row in table.rows:
        for idx, cell in enumerate(row.cells):
            set_cell_width(cell, widths[min(idx, len(widths) - 1)])


def configure_styles(doc: Document) -> None:
    styles = doc.styles
    normal = styles["Normal"]
    normal.font.name = "Calibri"
    normal.font.size = Pt(11)
    normal.paragraph_format.space_after = Pt(8)
    normal.paragraph_format.line_spacing = 1.333
    normal.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    for name, size, color, before, after in [
        ("Heading 1", 16, "2E74B5", 18, 10),
        ("Heading 2", 13, "2E74B5", 12, 6),
        ("Heading 3", 12, "1F4D78", 8, 4),
    ]:
        style = styles[name]
        style.font.name = "Calibri"
        style.font.size = Pt(size)
        style.font.color.rgb = RGBColor.from_string(color)
        style.paragraph_format.space_before = Pt(before)
        style.paragraph_format.space_after = Pt(after)
        style.paragraph_format.keep_with_next = True


def add_title(doc: Document) -> None:
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(4)
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    r = p.add_run(TITLE)
    r.bold = True
    r.font.name = "Calibri"
    r.font.size = Pt(22)
    r.font.color.rgb = RGBColor.from_string("0B2545")
    p2 = doc.add_paragraph()
    p2.paragraph_format.space_after = Pt(12)
    r2 = p2.add_run(SUBTITLE)
    r2.italic = True
    r2.font.size = Pt(11)
    r2.font.color.rgb = RGBColor.from_string("555555")
    p3 = doc.add_paragraph()
    p3.paragraph_format.space_after = Pt(18)
    r3 = p3.add_run("Methods article | Representation diagnostics | Reproducible lightweight evidence package")
    r3.font.size = Pt(9)
    r3.font.color.rgb = RGBColor.from_string("666666")


def add_md_table(doc: Document, table_md: str, max_rows: int | None = None) -> None:
    lines = [line for line in table_md.splitlines() if line.strip().startswith("|")]
    if len(lines) < 2:
        return
    header = [cell.strip() for cell in lines[0].strip("|").split("|")]
    rows = [[cell.strip() for cell in line.strip("|").split("|")] for line in lines[2:]]
    if max_rows:
        rows = rows[:max_rows]
    table = doc.add_table(rows=1, cols=len(header))
    table.style = "Table Grid"
    hdr = table.rows[0].cells
    for i, item in enumerate(header):
        hdr[i].text = item
        set_cell_shading(hdr[i], "F4F6F9")
        for p in hdr[i].paragraphs:
            for run in p.runs:
                run.bold = True
                run.font.size = Pt(8)
    for row in rows:
        cells = table.add_row().cells
        for i, item in enumerate(row):
            cells[i].text = item
            cells[i].vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
            for p in cells[i].paragraphs:
                p.paragraph_format.space_after = Pt(0)
                for run in p.runs:
                    run.font.size = Pt(8)
    width = 9360 // len(header)
    set_table_width(table, [width] * len(header))
    set_cell_margins(table)
    doc.add_paragraph()


def add_figure(doc: Document, rel: str, caption: str) -> None:
    path = (MANUSCRIPT / rel).resolve() if rel.startswith("..") else (PROJECT_ROOT / rel).resolve()
    if not path.exists():
        para = doc.add_paragraph(f"[Missing figure: {path}]")
        para.style = "Intense Quote"
        return
    doc.add_picture(str(path), width=Inches(6.2))
    cap = doc.add_paragraph(caption)
    cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    cap.paragraph_format.space_after = Pt(10)
    for run in cap.runs:
        run.font.size = Pt(9)
        run.font.italic = True
        run.font.color.rgb = RGBColor.from_string("555555")


def build_docx(md: str, output: Path) -> None:
    doc = Document()
    section = doc.sections[0]
    section.top_margin = Inches(1)
    section.bottom_margin = Inches(1)
    section.left_margin = Inches(1)
    section.right_margin = Inches(1)
    section.header_distance = Inches(0.492)
    section.footer_distance = Inches(0.492)
    configure_styles(doc)
    add_title(doc)

    lines = md.splitlines()
    in_refs = False
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if not line:
            i += 1
            continue
        if line == f"**{SUBTITLE}**":
            i += 1
            continue
        if line.startswith("# "):
            if line[2:].strip() != TITLE:
                doc.add_heading(line[2:].strip(), level=1)
            i += 1
            continue
        if line.startswith("## "):
            title = line[3:].strip()
            in_refs = title == "References"
            doc.add_heading(title, level=1)
            i += 1
            continue
        if line.startswith("### "):
            doc.add_heading(line[4:].strip(), level=2)
            i += 1
            continue
        if line.startswith("!["):
            match = re.match(r"!\[(.*?)\]\((.*?)\)", line)
            if match:
                add_figure(doc, match.group(2), match.group(1))
            i += 1
            continue
        if line.startswith("|"):
            table_lines = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                table_lines.append(lines[i])
                i += 1
            add_md_table(doc, "\n".join(table_lines), max_rows=12)
            continue
        if re.match(r"^\d+\. ", line) and in_refs:
            p = doc.add_paragraph(style=None)
            p.paragraph_format.left_indent = Inches(0.22)
            p.paragraph_format.first_line_indent = Inches(-0.22)
            p.paragraph_format.space_after = Pt(4)
            run = p.add_run(line)
            run.font.size = Pt(9)
            i += 1
            continue
        if line.startswith("**") and line.endswith("**"):
            p = doc.add_paragraph()
            run = p.add_run(line.strip("*"))
            run.bold = True
            i += 1
            continue
        para = doc.add_paragraph(line)
        para.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        i += 1

    output.parent.mkdir(parents=True, exist_ok=True)
    doc.save(output)


def main() -> None:
    md = build_markdown()
    md_path = MANUSCRIPT / "final_manuscript.md"
    docx_path = MANUSCRIPT / "final_manuscript.docx"
    md_path.write_text(md, encoding="utf-8")
    build_docx(md, docx_path)
    print(f"Wrote {md_path}")
    print(f"Wrote {docx_path}")


if __name__ == "__main__":
    main()
