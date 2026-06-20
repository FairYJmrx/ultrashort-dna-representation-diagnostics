from __future__ import annotations

import argparse
import re
import shutil
import subprocess
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MANUSCRIPT = PROJECT_ROOT / "manuscript"


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


def inline_math(text: str) -> str:
    placeholders: list[str] = []

    def protect(raw: str) -> str:
        placeholders.append(raw)
        return f"@@LATEX{len(placeholders)-1}@@"

    def math_repl(match: re.Match[str]) -> str:
        placeholders.append(match.group(0))
        return f"@@LATEX{len(placeholders)-1}@@"

    tmp = re.sub(r"\\\(.*?\\\)", math_repl, text)
    tmp = re.sub(r"`([^`]+)`", lambda m: protect(r"\texttt{" + esc(m.group(1)) + "}"), tmp)
    tmp = re.sub(r"\*\*([^*]+)\*\*", lambda m: protect(r"\textbf{" + esc(m.group(1)) + "}"), tmp)
    tmp = esc(tmp)
    for idx, value in enumerate(placeholders):
        tmp = tmp.replace(esc(f"@@LATEX{idx}@@"), value)
    return tmp


def parse_table(lines: list[str]) -> tuple[list[str], list[list[str]]]:
    header = [cell.strip() for cell in lines[0].strip("|").split("|")]
    rows = [[cell.strip() for cell in line.strip("|").split("|")] for line in lines[2:]]
    return header, rows


def compact_cell(text: str) -> str:
    replacements = {
        "Mean paired cosine": "mean cosine",
        "5th percentile paired cosine": "cosine p05",
        "Mean L2 drift": "L2 drift",
        "95th percentile L2 drift": "L2 p95",
        "Nearest-clean retrieval": "retrieval",
        "Canonical spaced seed": "c-spaced",
        "Canonical 5-mer + CSP": "5-mer+CSP",
        "Canonical 7-mer + CSP": "7-mer+CSP",
        "1% substitution + 3% N": "sub+N",
        "6-bp local mismatch": "6-bp mismatch",
        "Mean_macro_F1": "mean F1",
        "Mean_accuracy": "accuracy",
        "Mean_features": "features",
        "Mean macro-F1": "mean F1",
        "SD macro-F1": "sd F1",
        "First length with full motif-pair visibility": "first full visibility",
        "110,115,120,125,130,135,138,140,142,145,148,150,155,160": "110-160 dense grid",
    }
    return replacements.get(text, text)


def table_to_latex(lines: list[str]) -> str:
    header, rows = parse_table(lines)
    header = [compact_cell(cell) for cell in header]
    rows = [[compact_cell(cell) for cell in row] for row in rows]
    if len(header) > 8 or len(rows) > 22:
        return (
            r"\begin{quote}\small "
            + esc(f"Full table omitted from the PDF body for readability ({len(rows)} rows, {len(header)} columns); see the Markdown manuscript and stage-2 table files.")
            + r"\end{quote}"
        )
    n = len(header)
    spec = "@{}" + "".join([r">{\raggedright\arraybackslash}p{" + f"{0.92/n:.3f}" + r"\linewidth}" for _ in range(n)]) + "@{}"
    out = [
        r"\begin{center}",
        r"\scriptsize",
        r"\begin{adjustbox}{max width=\linewidth}",
        rf"\begin{{tabular}}{{{spec}}}",
        r"\toprule",
        " & ".join(r"\textbf{" + inline_math(cell) + "}" for cell in header) + r" \\",
        r"\midrule",
    ]
    for row in rows:
        padded = row + [""] * (n - len(row))
        out.append(" & ".join(inline_math(cell) for cell in padded[:n]) + r" \\")
    out.extend([r"\bottomrule", r"\end{tabular}", r"\end{adjustbox}", r"\end{center}", r"\normalsize"])
    return "\n".join(out)


def figure_to_latex(line: str, manuscript_dir: Path) -> str:
    match = re.match(r"!\[(.*?)\]\((.*?)\)", line)
    if not match:
        return ""
    caption = inline_math(match.group(1))
    raw_path = match.group(2)
    fig_path = (manuscript_dir / raw_path).resolve()
    rel = fig_path.relative_to(manuscript_dir).as_posix() if fig_path.is_relative_to(manuscript_dir) else fig_path.as_posix()
    return "\n".join(
        [
            r"\begin{figure}[H]",
            r"\centering",
            rf"\includegraphics[width=0.95\linewidth]{{{esc(rel)}}}",
            rf"\caption{{{caption}}}",
            r"\end{figure}",
        ]
    )


def markdown_to_latex(md: str, manuscript_dir: Path) -> str:
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
            out.append(r"\title{\Large " + inline_math(line[2:].strip()) + "}")
            i += 1
            continue
        if line.startswith("**") and line.endswith("**"):
            subtitle = inline_math(line.strip("*"))
            out.append(r"\author{\parbox{0.88\linewidth}{\centering\small " + subtitle + r"}}")
            out.append(r"\date{}")
            out.append(r"\maketitle")
            i += 1
            continue
        if line.startswith("## "):
            title = line[3:].strip()
            in_refs = title == "References"
            out.append(r"\section*{" + inline_math(title) + "}")
            i += 1
            continue
        if line.startswith("### "):
            out.append(r"\subsection*{" + inline_math(line[4:].strip()) + "}")
            i += 1
            continue
        if line.startswith("!["):
            out.append(figure_to_latex(line, manuscript_dir))
            i += 1
            continue
        if line.startswith("|"):
            table_lines = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                table_lines.append(lines[i])
                i += 1
            out.append(table_to_latex(table_lines))
            continue
        if line.startswith(r"\["):
            math_lines = []
            while i < len(lines):
                math_lines.append(lines[i])
                if lines[i].strip().startswith(r"\]"):
                    i += 1
                    break
                i += 1
            out.append("\n".join(math_lines))
            continue
        if in_refs and re.match(r"^\d+\. ", line):
            out.append(r"\hangindent=1.5em \hangafter=1 " + inline_math(line) + r"\par")
            i += 1
            continue
        out.append(inline_math(line) + "\n")
        i += 1
    return "\n\n".join(out)


def build_tex(md_path: Path, tex_path: Path) -> None:
    body = markdown_to_latex(md_path.read_text(encoding="utf-8"), md_path.parent)
    tex = rf"""
\documentclass[10.5pt]{{article}}
\usepackage[letterpaper,margin=0.85in]{{geometry}}
\usepackage{{fontspec}}
\setmainfont{{Times New Roman}}
\setsansfont{{Arial}}
\usepackage{{graphicx}}
\usepackage{{float}}
\usepackage{{booktabs}}
\usepackage{{array}}
\usepackage{{adjustbox}}
\usepackage{{caption}}
\usepackage{{amsmath}}
\usepackage{{microtype}}
\usepackage{{hyperref}}
\hypersetup{{colorlinks=true,linkcolor=black,urlcolor=blue,citecolor=black}}
\setlength{{\parskip}}{{5pt}}
\setlength{{\parindent}}{{0pt}}
\captionsetup{{font=small,labelfont=bf}}
\renewcommand{{\arraystretch}}{{1.16}}
\sloppy
\begin{{document}}
{body}
\end{{document}}
"""
    tex_path.write_text(tex.strip() + "\n", encoding="utf-8")


def compile_tex(tex_path: Path, pdf_path: Path, build_dir: Path) -> None:
    build_dir.mkdir(parents=True, exist_ok=True)
    cmd = [
        "xelatex",
        "-interaction=nonstopmode",
        "-halt-on-error",
        f"-output-directory={build_dir}",
        str(tex_path),
    ]
    for _ in range(2):
        subprocess.run(cmd, cwd=tex_path.parent, check=True)
    built_pdf = build_dir / f"{tex_path.stem}.pdf"
    shutil.copy2(built_pdf, pdf_path)


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a PDF manuscript from stage-2 markdown.")
    parser.add_argument("--input", default=str(MANUSCRIPT / "stage2_manuscript_v2.md"))
    parser.add_argument("--tex", default=str(MANUSCRIPT / "stage2_manuscript_v2.tex"))
    parser.add_argument("--pdf", default=str(MANUSCRIPT / "stage2_manuscript_v2.pdf"))
    parser.add_argument("--build-dir", default=str(MANUSCRIPT / "latex_build_stage2"))
    args = parser.parse_args()
    md_path = Path(args.input)
    tex_path = Path(args.tex)
    pdf_path = Path(args.pdf)
    build_dir = Path(args.build_dir)
    build_tex(md_path, tex_path)
    compile_tex(tex_path, pdf_path, build_dir)
    print(f"Wrote {tex_path}")
    print(f"Wrote {pdf_path}")


if __name__ == "__main__":
    main()
