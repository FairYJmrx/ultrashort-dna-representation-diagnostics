from __future__ import annotations

import re
import shutil
import subprocess
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
MANUSCRIPT = PROJECT_ROOT / "manuscript"
MD_PATH = MANUSCRIPT / "final_manuscript.md"
TEX_PATH = MANUSCRIPT / "final_manuscript.tex"
PDF_PATH = MANUSCRIPT / "final_manuscript.pdf"
BUILD_DIR = MANUSCRIPT / "latex_build"


def esc(text: str) -> str:
    repl = {
        "\\": r"\textbackslash{}",
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }
    return "".join(repl.get(ch, ch) for ch in text)


def parse_table(lines: list[str]) -> tuple[list[str], list[list[str]]]:
    header = [cell.strip() for cell in lines[0].strip("|").split("|")]
    rows = [[cell.strip() for cell in line.strip("|").split("|")] for line in lines[2:]]
    return header, rows


def compact_cell(text: str) -> str:
    replacements = {
        "delta_paired_cosine_mean": "delta cos mean",
        "delta_paired_cosine_p05": "delta cos p05",
        "delta_l2_delta_mean": "delta L2 mean",
        "l2_improvement": "L2 gain",
        "paired_cosine_mean": "cos mean",
        "paired_cosine_p05": "cos p05",
        "l2_delta_mean": "L2 mean",
        "observed_vocab_size": "vocab",
        "class_motif_visible_rate": "class motif visible",
        "pair_visible_rate": "pair visible",
        "mean_macro_f1": "macro-F1",
        "sd_macro_f1": "sd F1",
        "mean_accuracy": "accuracy",
        "mean_features": "features",
        "target_background": "target/bg",
        "within_genus_species": "within-genus",
        "canonical spaced + property": "cspaced + property",
    }
    return replacements.get(text, text)


def table_to_latex(lines: list[str]) -> str:
    header, rows = parse_table(lines)
    header = [compact_cell(cell) for cell in header]
    rows = [[compact_cell(cell) for cell in row] for row in rows]
    n = len(header)
    col_spec = "p{%.3f\\linewidth}" % (0.94 / n)
    spec = "@{}" + "".join(col_spec for _ in range(n)) + "@{}"
    out = [
        r"\begin{center}",
        r"\scriptsize",
        r"\begin{adjustbox}{max width=\linewidth}",
        rf"\begin{{tabularx}}{{\linewidth}}{{{spec}}}",
        r"\toprule",
    ]
    out.append(" & ".join(r"\textbf{" + esc(cell) + "}" for cell in header) + r" \\")
    out.append(r"\midrule")
    for row in rows:
        padded = row + [""] * (n - len(row))
        out.append(" & ".join(esc(cell) for cell in padded[:n]) + r" \\")
    out.extend([r"\bottomrule", r"\end{tabularx}", r"\end{adjustbox}", r"\end{center}", r"\normalsize"])
    return "\n".join(out)


def figure_to_latex(line: str) -> str:
    match = re.match(r"!\[(.*?)\]\((.*?)\)", line)
    if not match:
        return ""
    caption = esc(match.group(1))
    raw_path = match.group(2)
    fig_path = (MANUSCRIPT / raw_path).resolve() if raw_path.startswith("..") else (PROJECT_ROOT / raw_path).resolve()
    rel = fig_path.relative_to(MANUSCRIPT).as_posix() if fig_path.is_relative_to(MANUSCRIPT) else fig_path.as_posix()
    return "\n".join(
        [
            r"\begin{figure}[H]",
            r"\centering",
            rf"\includegraphics[width=0.92\linewidth]{{{esc(rel)}}}",
            rf"\caption{{{caption}}}",
            r"\end{figure}",
        ]
    )


def markdown_to_latex(md: str) -> str:
    lines = md.splitlines()
    out: list[str] = []
    in_refs = False
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if not line:
            i += 1
            continue
        if line.startswith("# "):
            out.append(r"\title{\Large " + esc(line[2:].strip()) + "}")
            i += 1
            continue
        if line.startswith("**") and line.endswith("**"):
            out.append(r"\author{\small " + esc(line.strip("*")) + r"}")
            out.append(r"\date{}")
            out.append(r"\maketitle")
            i += 1
            continue
        if line.startswith("## "):
            title = line[3:].strip()
            in_refs = title == "References"
            out.append(r"\section*{" + esc(title) + "}")
            i += 1
            continue
        if line.startswith("### "):
            out.append(r"\subsection*{" + esc(line[4:].strip()) + "}")
            i += 1
            continue
        if line.startswith("!["):
            out.append(figure_to_latex(line))
            i += 1
            continue
        if line.startswith("|"):
            table_lines = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                table_lines.append(lines[i])
                i += 1
            out.append(table_to_latex(table_lines))
            continue
        if in_refs and re.match(r"^\d+\. ", line):
            out.append(r"\hangindent=1.5em \hangafter=1 " + esc(line) + r"\par")
            i += 1
            continue
        out.append(esc(line) + "\n")
        i += 1
    return "\n\n".join(out)


def build_tex() -> None:
    body = markdown_to_latex(MD_PATH.read_text(encoding="utf-8"))
    tex = rf"""
\documentclass[11pt]{{article}}
\usepackage[letterpaper,margin=1in]{{geometry}}
\usepackage{{fontspec}}
\setmainfont{{Times New Roman}}
\setsansfont{{Arial}}
\usepackage{{graphicx}}
\usepackage{{float}}
\usepackage{{booktabs}}
\usepackage{{tabularx}}
\usepackage{{array}}
\usepackage{{adjustbox}}
\usepackage{{caption}}
\usepackage{{microtype}}
\usepackage{{hyperref}}
\hypersetup{{colorlinks=true,linkcolor=black,urlcolor=blue,citecolor=black}}
\setlength{{\parskip}}{{6pt}}
\setlength{{\parindent}}{{0pt}}
\captionsetup{{font=small,labelfont=bf}}
\renewcommand{{\arraystretch}}{{1.18}}
\sloppy
\begin{{document}}
{body}
\end{{document}}
"""
    TEX_PATH.write_text(tex.strip() + "\n", encoding="utf-8")


def compile_tex() -> None:
    BUILD_DIR.mkdir(parents=True, exist_ok=True)
    cmd = [
        "xelatex",
        "-interaction=nonstopmode",
        "-halt-on-error",
        f"-output-directory={BUILD_DIR}",
        str(TEX_PATH),
    ]
    for _ in range(2):
        subprocess.run(cmd, cwd=MANUSCRIPT, check=True)
    built_pdf = BUILD_DIR / "final_manuscript.pdf"
    shutil.copy2(built_pdf, PDF_PATH)


def main() -> None:
    build_tex()
    compile_tex()
    print(f"Wrote {TEX_PATH}")
    print(f"Wrote {PDF_PATH}")


if __name__ == "__main__":
    main()
