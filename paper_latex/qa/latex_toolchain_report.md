# LaTeX Toolchain and Manuscript QA Report

Date: 2026-07-16

## Local Toolchain

- MiKTeX is available at `C:\Users\24409\AppData\Local\Programs\MiKTeX\miktex\bin\x64`.
- Strawberry Perl is available at `C:\Strawberry\perl\bin`.
- `latexmk`, `pdflatex`, `xelatex`, `lualatex`, `bibtex` and `biber` are detected after prepending the MiKTeX and Strawberry Perl paths.
- OUP authoring class is detected at `C:\Users\24409\AppData\Local\Programs\MiKTeX\tex\latex\oup-authoring-template\oup-authoring-template.cls`.

## Project Layout

- Main source: `D:\AI-NGS\info\paper_latex\main.tex`
- Supplementary source: `D:\AI-NGS\info\paper_latex\supplementary.tex`
- Source generator: `D:\AI-NGS\info\paper_latex\scripts\build_latex_sources.py`
- Main PDF: `D:\AI-NGS\info\paper_latex\build\main.pdf`
- Supplementary PDF: `D:\AI-NGS\info\paper_latex\build_supp\supplementary.pdf`
- Rendered main pages: `D:\AI-NGS\info\paper_latex\qa\main_pages`
- Rendered supplementary pages: `D:\AI-NGS\info\paper_latex\qa\supp_pages`

## Build Commands

Run from `D:\AI-NGS\info\paper_latex`:

```powershell
$py='C:\Users\24409\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
& $py .\scripts\build_latex_sources.py
.\scripts\build_latex.cmd
.\scripts\build_latex.cmd -MainTex supplementary.tex -OutputDirectory build_supp
& $py .\scripts\render_pdf_pages.py .\build\main.pdf --out-dir .\qa\main_pages --prefix main
& $py .\scripts\render_pdf_pages.py .\build_supp\supplementary.pdf --out-dir .\qa\supp_pages --prefix supp
```

## Current Build Status

- Main manuscript compiles successfully to 16 pages.
- Supplementary file compiles successfully to 9 pages.
- Numeric citations render correctly; no `[@...]` citation tokens remain in the generated TeX.
- The OUP society-logo placeholder has been removed locally without editing the system class file.
- Page headers now show `NAR Genomics and Bioinformatics, 2026` and page numbers rather than an empty `Volume, Issue` template field.
- Supplementary page range is fixed at `1-9`.
- Figure and table captions no longer duplicate the words `Figure`, `Table`, or `Supplementary Figure`.
- The supplementary first page now includes a compact overview rather than an empty cover-like page.
- The CAMI II source-table preview is compacted and no longer triggers a table-specific overfull warning.

## Visual QA Notes

- Main pages inspected: page 1, page 9 and full contact sheet.
- Supplementary pages inspected: page 1, page 5 and full contact sheet.
- No obvious figure-label collisions, caption duplication, broken references, missing pages, blank figure panels or unreadable tables were observed in the inspected rendered pages.
- Remaining `Overfull \hbox (261.76535pt too wide) while \output is active` warnings are produced by the OUP/crop output routine and do not correspond to visible page-body overflow in the rendered PNGs.

## Nonfatal Environment Warnings

- PowerShell prints an execution-policy warning from the user's profile script. The project build uses `.cmd` wrappers and is not blocked.
- MiKTeX prints `So far, you have not checked for MiKTeX updates.` This is nonfatal, but should be cleared in MiKTeX Console before final submission packaging.
- The OUP class reports unused global options for this local template invocation. The manuscript still compiles and renders with the OUP class.
- Some font-shape substitution warnings remain from the OUP class and figure/table caption sizes. They are not fatal.

## Pending Before Formal Submission

- Replace private code/data placeholders with final public repository and DOI information.
- Finalize funding, acknowledgements and any institutional ethics/IRB wording.
- Confirm the journal submission system's current requirements for single-blind/double-blind review, source-file upload and supplementary-file naming.
- Run one last reference-format pass against the final target journal instructions.
