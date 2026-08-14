# NAR G&B LaTeX Migration Workflow

This document records the completed migration into an OUP/NAR-compatible LaTeX source package and defines the current build and PDF-audit workflow. It is not an instruction to regenerate the revised manuscript from historical Markdown.

## Current status (2026-08-14)

- The canonical source is the four-author Standard Paper in `paper_latex`.
- Ruixiang Mei is first and corresponding author; the author order is Ruixiang Mei, Zhi Chen,
  Rui Cao and Xunbing Gong. Huang Jianhua is not an author.
- Scientific and figure/layout QA are complete for the current claim boundary. No MIXBend
  comparison, Transformer benchmark, Kraken integration or new clinical experiment is pending.
- `v1.2.0` is an immutable historical single-author snapshot. The current four-author release,
  version DOI and NAR submission package remain to be frozen and created.

## 1. Target and Submission Constraints

- Target journal: NAR Genomics and Bioinformatics.
- Review model: single-anonymized peer review; the manuscript should include author names, affiliations, corresponding-author details and ORCID information.
- Preferred LaTeX route: OUP LaTeX template, Modern Large design, adapted for NAR Genomics and Bioinformatics.
- Initial submission deliverable: a single complete PDF containing manuscript text, references, tables and figures. The LaTeX source package should still be kept reproducible for revision or production.
- Supplementary information: keep supplementary figures/tables in a separate supplementary TeX/PDF unless the final submission portal requires a combined PDF.

## 2. Author and Metadata Inputs

Confirmed:

- Current author order: Ruixiang Mei (first and corresponding), Zhi Chen, Rui Cao and Xunbing Gong.
- ORCID: https://orcid.org/0009-0003-2128-0726.
- Confirmed corresponding email: ruixiangmei@link.cuhk.edu.cn.
- Confirmed institution: The Chinese University of Hong Kong, Shenzhen. The canonical source
  records the corresponding school for each author and the institutional address.
- Conflict of interest: the authors declare no competing interests.
- Funding: no specific grant from a public, commercial or not-for-profit funding body.

Still to confirm before final submission:

- [~] Final portal rendering of the official affiliation wording, postal code and author ORCID fields.
- [~] Long-term accessibility of the corresponding institutional email.
- [~] Final AI-use disclosure placement in the OUP submission form; the manuscript wording is already settled.
- [x] Use only the published mNGS read-length background source; unpublished local read-length provenance is not retained.

## 3. Source Materials to Extract

### Manuscript text

The canonical submission text is maintained directly in:

- `paper_latex/main.tex`
- `paper_latex/sections/`
- `paper_latex/supplementary.tex`
- `paper_latex/references.bib`

The split Markdown files in `paper/`, `final_manuscript.md` and older Word manuscripts are historical provenance only. They must not overwrite the revised LaTeX text or numerical claims.

### Citation source

- Working bibliography: `paper_latex/references.bib`.
- Reference audit: `the repository bibliography and release manifest`.
- Current audit status: 57 manuscript citation keys used, 0 missing keys; remaining warnings are the manual
  `Nair2006` metadata check and optional ISBN verification for the book citation.

### Figure source

Use vector or PDF assets by default. Prefer `.pdf` for LaTeX inclusion, with `.png` fallback only when PDF rendering is problematic.

Main figures:

- Figure 1: `paper_latex/figures/main/nature_fig1_framework.pdf`
- Figure 2: `paper_latex/figures/main/nature_fig2_compact_stability.pdf`
- Figure 3: `paper_latex/figures/main/nature_fig3_ck4p_msp_tradeoff.pdf`
- Figure 4: `paper_latex/figures/main/nature_fig4_external_probes.pdf`
- Figure 5: `paper_latex/figures/main/nature_fig5_full_position_upper_bound.pdf`
- Figure 6: `paper_latex/figures/main/nature_fig6_local_mutation_sensitivity.pdf`

Supplementary figures:

- Supplementary Figure S1: `paper_latex/figures/supplementary/supp_fig_s1_baseline_audit.pdf`
- Supplementary Figure S2: `paper_latex/figures/supplementary/supp_fig_s2_mi_audit.pdf`
- Supplementary Figure S3: `paper_latex/figures/supplementary/supp_fig_s3_error_aware_art.pdf`
- Supplementary Figure S4: `paper_latex/figures/supplementary/supp_fig_s4_mutation_fraction_sweep.pdf`
- Supplementary Figure S5: `paper_latex/figures/supplementary/supp_fig_s5_p_channel_counterfactual_audit.pdf`
- Supplementary Figure S6: `paper_latex/figures/supplementary/supp_fig_s6_msp_bin_gamma_sensitivity.pdf`
- Supplementary Figure S7: `paper_latex/figures/supplementary/supp_fig_s7_method_hardening_audit.pdf`
- Supplementary Figure S8: `paper_latex/figures/supplementary/supp_fig_s8_redundancy_runtime_audit.pdf`
- Supplementary Figure S9: `paper_latex/figures/supplementary/supp_fig_s9_p_msp_relation_audit.pdf`
- Supplementary Figure S10: `paper_latex/figures/supplementary/supp_fig_s10_cami2_marine_probe.pdf`
- Supplementary Figure S11: `paper_latex/figures/supplementary/supp_fig_s11_factorial_scaling.pdf`
- Supplementary Figure S12: `paper_latex/figures/supplementary/supp_fig_s12_historical_descriptor_audit.pdf`
- Supplementary Figure S13: `paper_latex/figures/supplementary/supp_fig_s13_short_read_continuity.pdf`
- Supplementary Figure S14: `paper_latex/figures/supplementary/supp_fig_s14_fixed_head_sensitivity.pdf`
- Supplementary Figure S15: `paper_latex/figures/supplementary/supp_fig_s15_pkm_pareto_audit.pdf`

Figure inventory:

- `paper_latex and the release manifest`
- Current DOCX convenience build: `the historical DOCX builder, which is excluded from this release`; DOCX is not the formal submission source.

### Table source

Use CSV as the authoritative tabular source and convert to LaTeX tables.

- Table 1: `paper_latex/tables/nature_table1_representation_families.csv`
- Table 2: `paper_latex/tables/nature_table2_data_layers.csv`
- Table 3: `paper_latex/tables/nature_table3_compact_main_method.csv`
- Table 4: `paper_latex/tables/nature_table4_local_mutation_sensitivity.csv`
- Table 5: `paper_latex/tables/nature_table5_boundary_summary.csv`
- Supplementary Table S10 source data: `paper_latex/tables/supp_table_s10_cami2_marine_probe_source.csv`

## 4. Target LaTeX Project Layout

Create or update:

```text
paper_latex/
  main.tex
  supplementary.tex
  references.bib
  figures/
    main/
    supplementary/
  tables/
    main/
    supplementary/
  sections/
    abstract.tex
    introduction.tex
    materials_methods.tex
    results.tex
    discussion.tex
    back_matter.tex
  scripts/
    build_latex.cmd
    build_latex.ps1
    render_pdf_pages.py
    build_latex_sources.py
    convert_markdown_to_tex.py
    convert_tables_to_tex.py
    latex_qa.py
  build/
  qa/
  nargab_latex_checklist.md
  nargab_latex_migration_workflow.md
```

The LaTeX project is now the canonical, directly maintained source. Numerical changes must begin with the release result tables and figure-generation scripts, then be propagated to the corresponding LaTeX section, table or caption.

## 5. LaTeX Source-Building Rules

### Template and package discipline

- Start from the official OUP LaTeX template using the Modern Large design.
- Keep the preamble minimal. Do not add packages unless needed.
- Avoid packages that commonly conflict with publisher classes unless the OUP template already uses them.
- Prefer `graphicx`, `booktabs`, `array`, `longtable` only if the template permits them.
- Use `natbib` or the bibliography mechanism required by the OUP template; do not invent a custom citation format.

### Markdown-to-TeX conversion

The converter should:

- Remove internal working notes and checklist-only comments.
- Convert section headings to the OUP template's sectioning commands.
- Convert citations from `[@Key1; @Key2]` to the template-compatible citation command, likely `\citep{Key1,Key2}` or the exact OUP-supported alternative.
- Convert display equations to LaTeX display math.
- Preserve the current manuscript's boundary language:
  - standardized diagnostic drift, not physical distance;
  - estimator-dependent empirical MI audit, not universal proof;
  - P/MSP related but non-equivalent, not independent orthogonal axes;
  - shallow readout as readability/accessibility probe, not production classification.

### Figures

For each figure:

- Insert with `\includegraphics[width=\linewidth]{...}` or a constrained width suitable for one-column/two-column placement.
- Prefer PDF assets.
- Keep captions under the figure.
- Add `Alt text:` as a separate sentence in each main figure caption unless the final OUP template provides an accessibility field.
- Ensure all panel labels are readable at final printed size.

### Tables

For each table:

- Generate LaTeX from CSV with consistent escaping.
- Use `booktabs`-style rules if allowed by the OUP template.
- Avoid oversized tables; use `\small` only when necessary.
- If a table exceeds page width, move it to supplementary material or split it.

### Supplementary material

The supplementary file should:

- Include Supplementary Figures S1-S12.
- Include Supplementary Tables S1-S11 and retain their machine-readable source tables in the release repository.
- Start with the manuscript title and author list or the OUP-required supplementary format.
- Use the standard sentence in the main manuscript if required: `Supplementary Data are available at NAR Genomics and Bioinformatics Online.`

## 6. Build Workflow

### Step 1. Prepare assets

- Copy `references.bib` from `paper_latex/references.bib`.
- Copy main figure PDFs to `paper_latex/figures/main/`.
- Copy supplementary figure PDFs to `paper_latex/figures/supplementary/`.
- Copy CSV tables to `paper_latex/tables/main/` and `paper_latex/tables/supplementary/`.

### Step 2. Edit TeX sections

Edit and review the canonical section files directly:

- `sections/abstract.tex`
- `sections/introduction.tex`
- `sections/materials_methods.tex`
- `sections/results.tex`
- `sections/discussion.tex`
- `sections/back_matter.tex`

`scripts/build_latex_sources.py` is retained only as a migration record. It exits without changes unless `--overwrite` is supplied; do not use that option for routine manuscript editing.

### Step 3. Generate tables

Convert CSV tables into LaTeX files:

- `tables/main/table1.tex`
- `tables/main/table2.tex`
- `tables/main/table3.tex`
- `tables/main/table4.tex`
- `tables/main/table5.tex`
- `tables/supplementary/table_s10.tex`

### Step 4. Build main and supplementary PDFs

Preferred command once a TeX runtime is available:

```powershell
.\scripts\build_latex.cmd
.\scripts\build_latex.cmd -MainTex supplementary.tex
```

If the project uses `biblatex`, use the OUP-supported biber workflow. If the OUP template uses BibTeX/natbib, use BibTeX.

Reference Windows environment note, updated 2026-07-30:

- The Codex-managed TeX Live installer is not available on Windows; it supports macOS/Linux only.
- MiKTeX 25.12 and Strawberry Perl 5.42 were used for the verified Windows build.
- Add the local MiKTeX and Perl binary directories to `PATH`; do not hard-code a user profile in repository scripts.
- For a temporary PowerShell session, a portable pattern is:

```powershell
$env:Path = "$env:PERL_BIN;$env:MIKTEX_BIN;$env:Path"
```

- Smoke tests passed for:
  - `latexmk + pdflatex` minimal PDF generation;
  - `latexmk + BibTeX` citation/bibliography generation.
- The OUP authoring-template entrypoint `main.tex` compiles to `build/main.pdf`.
- The local preamble removes the generic OUP society-logo placeholder block without editing the installed `oup-authoring-template.cls`.
- MiKTeX currently reports the non-fatal warning `So far, you have not checked for MiKTeX updates.` This should be cleared by running MiKTeX Console updates before final submission builds, but it does not block compilation.
- Local status report: `qa/latex_toolchain_report.md`.

## 7. PDF QA Workflow

After compilation, render the PDF pages to PNG for visual inspection.

Current rendering command:

```powershell
python .\scripts\render_pdf_pages.py .\build\main.pdf --out-dir .\qa --prefix oup_smoke_page
```

Current OUP smoke-test render:

- `qa/oup_smoke_page_01.png`
- Status: title page, abstract, figure inclusion and bibliography render successfully; no society-logo placeholder block remains after the local preamble patch.

### Layout checks

- No large unexplained blank areas, especially before or after floats.
- No section headings stranded alone at the bottom of a page.
- No figure or table separated too far from its caption.
- No table overflow beyond margins.
- No equation overflow or missing math glyphs.
- No unresolved references such as `??`.
- No raw citation keys such as `[@Wood2019]`.
- No LaTeX warnings left unresolved for missing citations or undefined references.

### Figure checks

- Panel labels are readable at final size.
- Axis labels and tick labels are not overlapping.
- Legends do not overlap data.
- Figure text is not smaller than the journal-readable minimum after scaling.
- Main figures fit standard article widths. Use single-column or two-column widths deliberately.
- Prefer PDF/vector inclusion; use high-resolution TIFF/PNG only if required.

### Content checks

- Abstract is a single paragraph and within the journal limit.
- All abbreviations are expanded on first use: CK4P-MSP, MSP, CSP, MI, KSG, ART, CAMI, EIIP.
- Author names, affiliations, corresponding-author email and ORCID are present.
- Data Availability and Code Availability currently point to the historical repository/concept DOI; replace them with
  the new immutable four-author release URL and version DOI after freeze.
- Funding is no longer pending: the canonical manuscript states that no specific grant supported the work.
- Conflict-of-interest statement is present.
- Ethics/Data Governance boundary is present and does not imply use of patient reads.

### Reference checks

- All 57 cited manuscript keys resolve.
- NAR/OUP reference style is used by the bibliography style.
- `Nair2006` metadata remains a manual final check because no DOI/eprint is currently recorded.
- The book citation's ISBN remains optional metadata; verify it from the copyright page if the final
  reference export requires it, but do not invent an ISBN from an unverified source.

## 8. Acceptance Criteria for the LaTeX Version

The LaTeX migration is considered ready for internal author review only when:

- `main.pdf` compiles without missing citations or undefined references.
- `supplementary.pdf` compiles without missing figures/tables.
- All main figures and tables are present in the correct narrative order.
- The rendered PDF passes page-by-page visual QA.
- A QA report is written to `paper_latex/qa/latex_pdf_qa_report.md`.
- The source project can be rebuilt from scripts rather than manual one-off edits.

The LaTeX migration is considered submission-ready only when:

- [x] Final affiliation, funding, ethics wording and acknowledgements are settled in the canonical source;
  final portal rendering remains an upload-stage check.
- [ ] Repository reviewer-access mechanism for the new four-author release is confirmed.
- [ ] New version-specific public DOI is minted and backfilled.
- [~] Final NAR/OUP reference style is verified locally; perform the portal/package check immediately before upload.
- [x] The PDF generated from LaTeX matches the final approved scientific text.
