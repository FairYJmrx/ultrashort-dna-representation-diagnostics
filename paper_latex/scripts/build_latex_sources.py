from __future__ import annotations

import argparse
import csv
import re
from pathlib import Path


LATEX = Path(__file__).resolve().parents[1]
REPOSITORY = LATEX.parent
PAPER = REPOSITORY / "paper"
SECTIONS = LATEX / "sections"
TABLE_MAIN = LATEX / "tables" / "main"
TABLE_SUPP = LATEX / "tables" / "supplementary"


FIGURES = {
    "Figure 1": ("figures/main/nature_fig1_framework.pdf", "Representation-diagnostic framework and read-length regime."),
    "Figure 2": ("figures/main/nature_fig2_compact_stability.pdf", "P/MSP contribution and counterfactual property-mapping audit."),
    "Figure 3": ("figures/main/nature_fig3_ck4p_msp_tradeoff.pdf", "Dimension-matched compact stability and readability audit."),
    "Figure 4": ("figures/main/nature_fig4_external_probes.pdf", "External stability and coarse-readout probes."),
    "Figure 5": ("figures/main/nature_fig5_full_position_upper_bound.pdf", "Full-position diagnostic upper bound for positional information."),
    "Figure 6": ("figures/main/nature_fig6_local_mutation_sensitivity.pdf", "Local-change readability and distance-ratio boundary."),
}

FIGURE_ALT_TEXT = {
    "Figure 1": "Workflow diagram showing short reads separated into identity, biochemical and positional representation channels before diagnostic readouts and boundary checks.",
    "Figure 2": "Bar plots showing P/MSP contribution to drift, local-change readout and real-versus-counterfactual property mapping.",
    "Figure 3": "Scatter plots comparing CK4P-MSP with compact k-mer and dimension-matched high-k compressed baselines for stability and shallow readability.",
    "Figure 4": "Three-panel comparison of ART stability, CAMI coarse target-background readout and CAMI II anonymous-read stability.",
    "Figure 5": "Bar and scatter plots showing that full-position matrices add positional readout value at substantially higher feature dimension.",
    "Figure 6": "Bar plots showing MSP-driven local-change readability and the separate distance-ratio boundary against full-position property probes.",
}

SUPP_FIGURES = {
    "Supplementary Figure S1": ("figures/supplementary/supp_fig_s1_baseline_audit.pdf", "Baseline and mixed-metric audit."),
    "Supplementary Figure S2": ("figures/supplementary/supp_fig_s2_mi_audit.pdf", "Empirical MI and conditional-MI audit."),
    "Supplementary Figure S3": ("figures/supplementary/supp_fig_s3_error_aware_art.pdf", "Quality-stratified ART perturbation audit."),
    "Supplementary Figure S4": ("figures/supplementary/supp_fig_s4_mutation_fraction_sweep.pdf", "Local mutation-fraction sweep."),
    "Supplementary Figure S5": ("figures/supplementary/supp_fig_s5_p_channel_counterfactual_audit.pdf", "P-channel counterfactual and short-bin reliability audit."),
    "Supplementary Figure S6": ("figures/supplementary/supp_fig_s6_msp_bin_gamma_sensitivity.pdf", "MSP binset and gamma-sensitivity audit."),
    "Supplementary Figure S7": ("figures/supplementary/supp_fig_s7_method_hardening_audit.pdf", "kNN MI robustness and dimension-matched high-k compressed baseline audit."),
    "Supplementary Figure S8": ("figures/supplementary/supp_fig_s8_redundancy_runtime_audit.pdf", "P/MSP contribution, redundancy and runtime audit."),
    "Supplementary Figure S9": ("figures/supplementary/supp_fig_s9_p_msp_relation_audit.pdf", "P/MSP relation audit."),
    "Supplementary Figure S10": ("figures/supplementary/supp_fig_s10_cami2_marine_probe.pdf", "CAMI II marine anonymous-read stability probe."),
}

SUPP_FIGURE_ALT_TEXT = {
    "Supplementary Figure S1": "Baseline audit plots comparing full-position matrices, reduced controls and block-weight sensitivity.",
    "Supplementary Figure S2": "Bar plots summarizing empirical mutual-information and conditional-mutual-information audit values across representation blocks.",
    "Supplementary Figure S3": "Line plots showing ART perturbation behavior across quality levels for paired cosine and L2 drift.",
    "Supplementary Figure S4": "Line plot showing local mutation-fraction sensitivity across compact representation families.",
    "Supplementary Figure S5": "Multi-panel audit of P-channel counterfactual behavior, drift decomposition and short-bin sampling bounds.",
    "Supplementary Figure S6": "Line plots showing MSP binset and gamma-weight sensitivity for 69 and 75 bp reads and delta-readout.",
    "Supplementary Figure S7": "Multi-panel audit showing kNN mutual-information robustness and dimension-matched high-k compressed baseline comparisons.",
    "Supplementary Figure S8": "Multi-panel audit showing P and MSP contributions, redundancy and runtime costs.",
    "Supplementary Figure S9": "Line and heatmap panels showing CCA and correlation relationships between P and MSP feature layers.",
    "Supplementary Figure S10": "Line, heatmap and bar panels showing CAMI II marine anonymous-read stability across length and perturbation settings.",
}

TABLES = {
    "Table 1": ("nature_table1_representation_families.csv", "Representation families and diagnostic roles."),
    "Table 2": ("nature_table2_data_layers.csv", "Data layers, diagnostic questions, metrics and claim boundaries."),
    "Table 3": ("nature_table3_compact_main_method.csv", "Compact main-method metrics."),
    "Table 4": ("nature_table4_local_mutation_sensitivity.csv", "Local mutation sensitivity metrics."),
    "Table 5": ("nature_table5_boundary_summary.csv", "Boundary and mechanism summary."),
}


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def english_after_marker(path: Path) -> str:
    text = read_text(path)
    marker = "# English draft"
    if marker in text:
        return text.split(marker, 1)[1].strip()
    return text.strip()


def back_matter_text(path: Path) -> str:
    text = read_text(path)
    start = text.index("## Data Availability")
    end = text.index("## References")
    return text[start:end].strip()


def protect_math(text: str) -> tuple[str, list[str]]:
    parts: list[str] = []

    def repl(match: re.Match[str]) -> str:
        parts.append(match.group(0))
        return f"@@MATH{len(parts)-1}@@"

    text = re.sub(r"\$\$.*?\$\$", repl, text, flags=re.S)
    text = re.sub(r"\$[^$\n]+\$", repl, text)
    return text, parts


def restore_math(text: str, parts: list[str]) -> str:
    for idx, value in enumerate(parts):
        if value.startswith("$$"):
            value = "\\[\n" + value[2:-2].strip() + "\n\\]"
        text = text.replace(f"@@MATH{idx}@@", value)
    return text


def escape_latex(text: str) -> str:
    repl = {
        "\\": r"\textbackslash{}",
        "&": r"\&",
        "%": r"\%",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }
    return "".join(repl.get(ch, ch) for ch in text)


def protect_citations(text: str) -> tuple[str, list[str]]:
    citations: list[str] = []

    def repl(match: re.Match[str]) -> str:
        keys = re.findall(r"@([A-Za-z0-9:_-]+)", match.group(1))
        if not keys:
            return match.group(0)
        citations.append(r"\citep{" + ",".join(keys) + "}")
        return f"@@CITE{len(citations)-1}@@"

    return re.sub(r"\[([^\]]*@[^]]+)\]", repl, text), citations


def convert_inline(text: str) -> str:
    text, math_parts = protect_math(text)
    text, cite_parts = protect_citations(text)
    code_parts: list[str] = []

    def code_repl(match: re.Match[str]) -> str:
        raw = match.group(1)
        if raw.startswith(("http://", "https://")):
            code_parts.append(r"\url{" + raw + "}")
        elif "/" in raw or "\\" in raw:
            code_parts.append(r"\path{" + raw + "}")
        else:
            code_parts.append(r"\texttt{" + escape_latex(raw) + "}")
        return f"@@CODE{len(code_parts)-1}@@"

    text = re.sub(r"`([^`]+)`", code_repl, text)
    text = escape_latex(text)

    text = re.sub(r"\*\*([^*]+)\*\*", r"\\textbf{\1}", text)
    text = re.sub(r"\*([^*\n]+)\*", r"\\textit{\1}", text)

    for idx, value in enumerate(code_parts):
        text = text.replace(f"@@CODE{idx}@@", value)
    for idx, value in enumerate(cite_parts):
        text = text.replace(f"@@CITE{idx}@@", value)
    text = restore_math(text, math_parts)
    text = text.replace(" - ", " -- ")
    return text


def slug(label: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", label.lower()).strip("-")


def figure_float(key: str) -> str:
    path, caption = FIGURES[key]
    alt = FIGURE_ALT_TEXT[key]
    label = "fig:" + key.lower().replace(" ", "")
    return (
        "\\begin{figure*}[!tbp]\n"
        "\\centering\n"
        f"\\includegraphics[width=0.92\\textwidth]{{{path}}}\n"
        f"\\caption{{{convert_inline(caption)}}}\n"
        f"\\label{{{label}}}\n"
        f"{{\\small\\noindent\\textbf{{Alt text:}} {convert_inline(alt)}\\par}}\n"
        "\\end{figure*}\n"
    )


def table_float(key: str) -> str:
    _, caption = TABLES[key]
    fname = "table" + key.split()[1] + ".tex"
    label = "tab:" + key.lower().replace(" ", "")
    return (
        "\\begin{table*}[!tbp]\n"
        "\\centering\n"
        "\\scriptsize\n"
        f"\\caption{{{convert_inline(caption)}}}\n"
        f"\\label{{{label}}}\n"
        f"\\input{{tables/main/{fname}}}\n"
        "\\end{table*}\n"
    )


def placeholder_to_latex(line: str) -> str | None:
    if not (line.startswith("[Insert ") and line.endswith("]")):
        return None
    content = line.strip("[]")
    if content.startswith("Insert FloatBarrier"):
        return "\\FloatBarrier"
    if content.startswith("Insert Supplementary Figure"):
        m = re.search(r"Supplementary Figure S\d+", content)
        if m:
            key = m.group(0)
            return f"See {key}."
    if content.startswith("Insert Figure"):
        m = re.search(r"Figure \d+", content)
        if m and m.group(0) in FIGURES:
            return figure_float(m.group(0))
    if content.startswith("Insert Table"):
        m = re.search(r"Table \d+", content)
        if m and m.group(0) in TABLES:
            return table_float(m.group(0))
    return None


def markdown_to_latex(text: str, *, skip_placement_summary: bool = True) -> str:
    lines = text.splitlines()
    out: list[str] = []
    in_display = False
    display_buf: list[str] = []
    skip = False
    paragraph: list[str] = []

    def flush_para() -> None:
        nonlocal paragraph
        if paragraph:
            out.append(convert_inline(" ".join(p.strip() for p in paragraph)))
            out.append("")
            paragraph = []

    for raw in lines:
        line = raw.rstrip()
        if skip_placement_summary and line.startswith("## Figure and Table Placement Summary"):
            flush_para()
            skip = True
            continue
        if skip:
            continue
        if line.strip() == "$$":
            if in_display:
                out.append("\\[\n" + "\n".join(display_buf).strip() + "\n\\]")
                out.append("")
                display_buf = []
                in_display = False
            else:
                flush_para()
                in_display = True
                display_buf = []
            continue
        if in_display:
            display_buf.append(line)
            continue
        if not line.strip():
            flush_para()
            continue
        repl = placeholder_to_latex(line.strip())
        if repl is not None:
            flush_para()
            out.append(repl)
            out.append("")
            continue
        if line.startswith("# "):
            flush_para()
            title = line[2:].strip()
            if title.lower() not in {"materials and methods and results", "discussion, limitations, future work and conclusion", "back matter and reference support"}:
                if out and out[-1] != "\\FloatBarrier":
                    out.append("\\FloatBarrier")
                out.append(f"\\section{{{convert_inline(title)}}}")
                out.append("")
            continue
        if line.startswith("## "):
            flush_para()
            if out and out[-1] != "\\FloatBarrier":
                out.append("\\FloatBarrier")
            out.append(f"\\section{{{convert_inline(line[3:].strip())}}}")
            out.append("")
            continue
        if line.startswith("### "):
            flush_para()
            out.append(f"\\subsection{{{convert_inline(line[4:].strip())}}}")
            out.append("")
            continue
        if line.startswith("- "):
            flush_para()
            out.append("\\begin{itemize}")
            out.append("\\item " + convert_inline(line[2:].strip()))
            out.append("\\end{itemize}")
            out.append("")
            continue
        paragraph.append(line)
    flush_para()
    return "\n".join(out).strip() + "\n"


def table_tex_from_csv(csv_path: Path) -> str:
    rows = list(csv.reader(csv_path.read_text(encoding="utf-8-sig").splitlines()))
    ncols = len(rows[0])
    widths = {
        3: ["0.22\\textwidth", "0.36\\textwidth", "0.34\\textwidth"],
        4: ["0.18\\textwidth", "0.24\\textwidth", "0.24\\textwidth", "0.26\\textwidth"],
        5: ["0.13\\textwidth", "0.22\\textwidth", "0.21\\textwidth", "0.14\\textwidth", "0.13\\textwidth"],
        6: ["0.14\\textwidth", "0.11\\textwidth", "0.11\\textwidth", "0.13\\textwidth", "0.16\\textwidth", "0.10\\textwidth"],
    }.get(ncols, [f"{0.88/ncols:.3f}\\textwidth"] * ncols)
    spec = "@{}" + "".join(f"p{{{w}}}" for w in widths) + "@{}"
    body = [f"\\begin{{tabular}}{{{spec}}}", "\\toprule"]
    body.append(" & ".join("\\textbf{" + convert_inline(cell) + "}" for cell in rows[0]) + r" \\")
    body.append("\\midrule")
    for row in rows[1:]:
        body.append(" & ".join(convert_inline(cell) for cell in row) + r" \\")
    body.append("\\bottomrule")
    body.append("\\end{tabular}")
    return "\n".join(body) + "\n"


def write_tables() -> None:
    TABLE_MAIN.mkdir(parents=True, exist_ok=True)
    for key, (fname, _) in TABLES.items():
        out = TABLE_MAIN / ("table" + key.split()[1] + ".tex")
        out.write_text(table_tex_from_csv(PAPER / "tables" / fname), encoding="utf-8")

    TABLE_SUPP.mkdir(parents=True, exist_ok=True)
    src = PAPER / "tables" / "supp_table_s10_cami2_marine_probe_source.csv"
    if src.exists():
        rows = list(csv.reader(src.read_text(encoding="utf-8-sig").splitlines()))
        preview = compact_s10_preview(rows)
        temp = TABLE_SUPP / "table_s10_preview.tex"
        with temp.open("w", encoding="utf-8", newline="") as f:
            f.write(table_tex_from_rows(
                preview,
                widths=[
                    "0.07\\textwidth",
                    "0.12\\textwidth",
                    "0.14\\textwidth",
                    "0.08\\textwidth",
                    "0.13\\textwidth",
                    "0.11\\textwidth",
                    "0.09\\textwidth",
                ],
            ))


def compact_s10_preview(rows: list[list[str]]) -> list[list[str]]:
    header = rows[0]
    keep = [
        "length",
        "condition",
        "method",
        "n_features",
        "paired_cosine_mean",
        "l2_delta_mean",
        "retrieval_top1",
    ]
    index = {name: header.index(name) for name in keep}
    out = [["length", "condition", "method", "features", "paired cosine", "L2 drift", "top-1"]]
    for row in rows[1:16]:
        compact = []
        for name in keep:
            value = row[index[name]]
            if name == "method":
                value = value.replace("(222-dim)", "").replace("(297-dim)", "")
            if name in {"paired_cosine_mean", "l2_delta_mean", "retrieval_top1"}:
                value = f"{float(value):.4f}"
            compact.append(value)
        out.append(compact)
    return out


def table_tex_from_rows(rows: list[list[str]], widths: list[str] | None = None) -> str:
    ncols = len(rows[0])
    if widths is None:
        width = f"{0.88/ncols:.3f}\\textwidth"
        widths = [width] * ncols
    spec = "@{}" + "".join(f"p{{{w}}}" for w in widths) + "@{}"
    body = [f"\\begin{{tabular}}{{{spec}}}", "\\toprule"]
    body.append(" & ".join("\\textbf{" + convert_inline(cell) + "}" for cell in rows[0]) + r" \\")
    body.append("\\midrule")
    for row in rows[1:]:
        body.append(" & ".join(convert_inline(cell) for cell in row) + r" \\")
    body.append("\\bottomrule")
    body.append("\\end{tabular}")
    return "\n".join(body) + "\n"


def write_sections() -> None:
    SECTIONS.mkdir(parents=True, exist_ok=True)
    abstract = english_after_marker(PAPER / "01_abstract.md")
    (SECTIONS / "abstract.tex").write_text(convert_inline(abstract) + "\n", encoding="utf-8")
    (SECTIONS / "introduction.tex").write_text(markdown_to_latex(english_after_marker(PAPER / "02_intro_related_work.md")), encoding="utf-8")
    (SECTIONS / "materials_results.tex").write_text(markdown_to_latex(read_text(PAPER / "03_method_experiments.md")), encoding="utf-8")
    (SECTIONS / "discussion.tex").write_text(markdown_to_latex(read_text(PAPER / "04_limitations_future_conclusion.md")), encoding="utf-8")
    (SECTIONS / "back_matter.tex").write_text(markdown_to_latex(back_matter_text(PAPER / "05_references.md"), skip_placement_summary=False), encoding="utf-8")


def main_tex() -> str:
    return r"""\documentclass[unnumsec,webpdf,modern,large,numbered]{oup-authoring-template}

\usepackage{url}
\usepackage{booktabs}
\usepackage{array}
\usepackage{etoolbox}
\usepackage{placeins}
\setcitestyle{numbers,square,comma}
\makeatletter
\setlength{\@fptop}{0pt}
\setlength{\@fpsep}{12pt}
\setlength{\@fpbot}{0pt plus 1fil}
\makeatother
\renewcommand{\topfraction}{0.95}
\renewcommand{\bottomfraction}{0.95}
\renewcommand{\textfraction}{0.05}
\renewcommand{\floatpagefraction}{0.75}
\setlength{\textfloatsep}{12pt plus 2pt minus 2pt}
\setlength{\floatsep}{10pt plus 2pt minus 2pt}

% OUP generic templates include a society-logo placeholder on the opening page.
% NAR G&B author-submission PDFs do not need that generic placeholder.
\def\societylogo{}
\makeatletter
\patchcmd{\ps@opening}
  {\hfill{\smash{\societylogo{}\hspace*{12pt}}\color{black!20}\rule{45pt}{55pt}}}
  {}
  {}
  {}
\patchcmd{\ps@opening}
  {\hfill{\smash{\societylogo{}\hspace*{12pt}}\color{black!20}\rule{45pt}{55pt}}}
  {}
  {}
  {}
\makeatother

\journaltitle{NAR Genomics and Bioinformatics}
\pubyear{2026}
\copyrightyear{2026}
\makeatletter
\def\ps@headings{%
  \let\@oddfoot\@empty\let\@evenfoot\@empty
  \def\@oddhead{\vbox{\hbox to \textwidth{\fontsize{8bp}{10bp}\selectfont\itshape\@journaltitle, \@pubyear\hfill\bfseries\thepage}\vspace{5pt}\rule{\textwidth}{1pt}}}%
  \def\@evenhead{\vbox{\hbox to \textwidth{\fontsize{8bp}{10bp}\selectfont\bfseries\thepage\hfill\itshape\@journaltitle, \@pubyear}\vspace{5pt}\rule{\textwidth}{1pt}}}%
}
\makeatother
\pagestyle{headings}

\title[Layered representation diagnostics for short metagenomic reads]{Layered representation diagnostics for short metagenomic reads}

\author[1,*]{Ruixiang Mei\,\ORCID{0009-0003-2128-0726}}
\author[2]{Zhi Chen\,\ORCID{0009-0001-0072-5576}}
\author[3]{Rui Cao\,\ORCID{0009-0006-6182-1381}}
\author[2]{Xunbing Gong\,\ORCID{0009-0009-6715-0656}}

\address[1]{School of Data Science, The Chinese University of Hong Kong, Shenzhen, 2001 Longxiang Road, Longgang District, Shenzhen 518172, Guangdong, China}
\address[2]{School of Medicine, The Chinese University of Hong Kong, Shenzhen, 2001 Longxiang Road, Longgang District, Shenzhen 518172, Guangdong, China}
\address[3]{School of Artificial Intelligence, The Chinese University of Hong Kong, Shenzhen, 2001 Longxiang Road, Longgang District, Shenzhen 518172, Guangdong, China}

\corresp[*]{Correspondence: Ruixiang Mei, \url{ruixiangmei@link.cuhk.edu.cn}}

\abstract{\input{sections/abstract}}

\keywords{metagenomics, short reads, representation diagnostics, k-mer features, nucleotide-property coding}

\begin{document}

\maketitle

\input{sections/introduction}
\input{sections/materials_results}
\input{sections/discussion}
\input{sections/back_matter}

\bibliographystyle{unsrtnat}
\bibliography{references}

\end{document}
"""


def supplementary_tex() -> str:
    """Return the historical migration-only supplementary scaffold.

    The edited ``supplementary.tex`` is now a canonical source because it
    contains manuscript-specific S11--S15 methods, captions and layout rules.
    ``main()`` deliberately preserves that file instead of regenerating this
    scaffold.
    """
    lines = [r"\documentclass[unnumsec,webpdf,modern,large,numbered]{oup-authoring-template}",
             r"\usepackage{url}",
             r"\usepackage{booktabs}",
             r"\usepackage{array}",
             r"\usepackage{etoolbox}",
             r"\setcitestyle{numbers,square,comma}",
             r"\def\societylogo{}",
             r"\makeatletter",
             r"\patchcmd{\ps@opening}{\hfill{\smash{\societylogo{}\hspace*{12pt}}\color{black!20}\rule{45pt}{55pt}}}{}{}{}",
             r"\patchcmd{\ps@opening}{\hfill{\smash{\societylogo{}\hspace*{12pt}}\color{black!20}\rule{45pt}{55pt}}}{}{}{}",
             r"\makeatother",
             r"\journaltitle{NAR Genomics and Bioinformatics}",
             r"\pubyear{2026}",
             r"\copyrightyear{2026}",
             r"\lastpage{10}",
             r"\makeatletter",
             r"\def\ps@headings{\let\@oddfoot\@empty\let\@evenfoot\@empty\def\@oddhead{\vbox{\hbox to \textwidth{\fontsize{8bp}{10bp}\selectfont\itshape\@journaltitle, \@pubyear\hfill\bfseries\thepage}\vspace{5pt}\rule{\textwidth}{1pt}}}\def\@evenhead{\vbox{\hbox to \textwidth{\fontsize{8bp}{10bp}\selectfont\bfseries\thepage\hfill\itshape\@journaltitle, \@pubyear}\vspace{5pt}\rule{\textwidth}{1pt}}}}",
             r"\makeatother",
             r"\pagestyle{headings}",
             r"\title[Supplementary Data]{Supplementary Data for Layered representation diagnostics for short metagenomic reads}",
             r"\author[1,*]{Ruixiang Mei\,\ORCID{0009-0003-2128-0726}}",
             r"\author[2]{Zhi Chen\,\ORCID{0009-0001-0072-5576}}",
             r"\author[3]{Rui Cao\,\ORCID{0009-0006-6182-1381}}",
             r"\author[2]{Xunbing Gong\,\ORCID{0009-0009-6715-0656}}",
             r"\address[1]{School of Data Science, The Chinese University of Hong Kong, Shenzhen, 2001 Longxiang Road, Longgang District, Shenzhen 518172, Guangdong, China}",
             r"\address[2]{School of Medicine, The Chinese University of Hong Kong, Shenzhen, 2001 Longxiang Road, Longgang District, Shenzhen 518172, Guangdong, China}",
             r"\address[3]{School of Artificial Intelligence, The Chinese University of Hong Kong, Shenzhen, 2001 Longxiang Road, Longgang District, Shenzhen 518172, Guangdong, China}",
             r"\corresp[*]{Correspondence: Ruixiang Mei, \url{ruixiangmei@link.cuhk.edu.cn}}",
             r"\abstract{Supplementary figures and source-table preview supporting the representation-diagnostic analyses.}",
             r"\keywords{supplementary data, metagenomics, representation diagnostics}",
             r"\begin{document}",
             r"\renewcommand{\thefigure}{S\arabic{figure}}",
             r"\renewcommand{\thetable}{S\arabic{table}}",
             r"\maketitle",
             r"\section{Supplementary data overview}",
             r"This supplementary file collects the visual audits and source-table preview that support the main representation-diagnostic manuscript. Figures S1--S3 evaluate baseline controls, empirical information proxies and sequencing-error-aware perturbations. Figures S4--S7 examine local mutation fraction, P-channel counterfactuals, MSP bin and weight sensitivity, kNN mutual-information robustness and dimension-matched high-k compressed baselines. Figures S8--S10 summarize P/MSP redundancy, runtime, relation audits and the CAMI II marine anonymous-read stability probe. Table S1 gives a compact preview of the CAMI II marine source table; the full CSV is retained in the accompanying data package.",
             r"\section{Supplementary Figures}"]
    for key, (path, caption) in SUPP_FIGURES.items():
        alt = SUPP_FIGURE_ALT_TEXT[key]
        label = "fig:" + key.lower().replace(" ", "").replace("supplementary", "supp")
        lines.extend([
            r"\begin{figure*}[p]",
            r"\centering",
            f"\\includegraphics[width=0.95\\textwidth]{{{path}}}",
            f"\\caption{{{convert_inline(caption)}}}",
            f"\\label{{{label}}}",
            f"{{\\small\\noindent\\textbf{{Alt text:}} {convert_inline(alt)}\\par}}",
            r"\end{figure*}",
            "",
        ])
    lines.extend([
        r"\section{Supplementary Table}",
        r"\begin{table*}[p]",
        r"\centering",
        r"\scriptsize",
        r"\caption{Preview of the CAMI II marine subset source table. The full CSV is retained in the data package.}",
        r"\label{tab:supps10}",
        r"\input{tables/supplementary/table_s10_preview.tex}",
        r"\end{table*}",
        r"\clearpage",
        r"\end{document}",
    ])
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Re-run the historical Markdown-to-LaTeX migration."
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite the canonical LaTeX sources with migration output.",
    )
    args = parser.parse_args()
    if not args.overwrite:
        parser.error(
            "This is a migration-only utility. The edited .tex files are the source of truth; "
            "pass --overwrite only when intentionally rebuilding them from paper/*.md."
        )
    write_tables()
    write_sections()
    (LATEX / "main.tex").write_text(main_tex(), encoding="utf-8")
    print("Generated main-manuscript LaTeX sources in", LATEX)
    print("Preserved canonical supplementary.tex; it is no longer migration-generated.")


if __name__ == "__main__":
    main()
