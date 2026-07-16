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

- Main manuscript compiles successfully to 16 pages in the review-layout build.
- Supplementary file compiles successfully to 10 pages.
- Numeric citations render correctly; no `[@...]` citation tokens remain in the generated TeX.
- The OUP society-logo placeholder has been removed locally without editing the system class file.
- Page headers now show `NAR Genomics and Bioinformatics, 2026` and page numbers rather than an empty `Volume, Issue` template field.
- Supplementary page range is fixed at `1-10`.
- Figure and table captions no longer duplicate the words `Figure`, `Table`, or `Supplementary Figure`.
- Main and supplementary figure legends now include concise `Alt text:` statements below each caption, following the NAR G&B author-guideline requirement for main-article images and improving accessibility for supplementary figures.
- The supplementary first page now includes a compact overview rather than an empty cover-like page.
- The CAMI II source-table preview is compacted and no longer triggers a table-specific overfull warning.
- Main Tables 2 and 3 were regenerated with narrower five-column layouts; their previous table-specific overfull warnings are resolved.
- Long review-repository and CAMI II resource URLs were rewritten as prose placeholders so the Data and Code Availability sections no longer create body-text overfull warnings.
- Main figures and tables now use flexible top/bottom/page float placement with major-section barriers rather than figure-page-only placement. This allows figures to lag their discussion by about one page when needed, while avoiding full figure-only pages and reducing sparse single-column text pages.
- The back matter includes Data Availability, Code Availability, Supplementary Data, Ethics and Data Governance, Author Contributions, Funding, Acknowledgements and Conflict of Interest sections.

## Visual QA Notes

- Main pages inspected: page 1 and full review-layout contact sheet.
- Supplementary pages inspected: page 1, page 8 and full contact sheet.
- No obvious figure-label collisions, caption duplication, broken references, missing pages, blank figure panels or unreadable tables were observed in the inspected rendered pages.
- Remaining `Overfull \hbox (261.76535pt too wide) while \output is active` warnings are produced by the OUP/crop output routine and do not correspond to visible page-body overflow in the rendered PNGs. No remaining overfull warnings were detected from manuscript body text, generated tables, figure captions or availability statements.
- Figure/table placement now favors reviewer readability and page density. Main figures are embedded in the text stream rather than isolated on figure-only pages; Figure 2/3 share a mixed figure/text page, Figure 4/5 share a mixed figure/text page, and Figure 6 remains adjacent to the local-mutation results.
- The local `build/main.pdf` may be locked by a PDF viewer on Windows. In that case, the current review-layout PDF is available as `build/main_review_layout.pdf`; the release package uses this review-layout PDF as `paper_latex/build/main.pdf`.

## NAR G&B Submission Checks Applied

- OUP Modern Large LaTeX class is used through `oup-authoring-template`.
- Main manuscript and supplementary PDF are both generated from source.
- Figures and tables are embedded in the review PDF near the relevant manuscript text.
- Data and code availability statements are present, with private-review repository access noted and public DOI release still pending.
- A Supplementary Data statement is present.
- Conflict of Interest statement is present.
- Funding, acknowledgements and institutional ethics/IRB wording remain explicitly marked for final author confirmation before submission.

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
