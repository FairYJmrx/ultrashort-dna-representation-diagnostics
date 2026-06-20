# Render QA Report

Date: 2026-06-20

## Purpose

This report records the document-rendering verification for the manuscript package. The requested Word manuscript remains `manuscript/final_manuscript.docx`. Because the local LibreOffice installation was damaged, a PDF rendering path was used as the visual QA fallback.

## LibreOffice Status

LibreOffice did not start reliably on this machine.

- `D:\AI-NGS\_tools\LibreOfficeExtracted\program\bootstrap.ini` contained `InstallMode=<installmode>`.
- `C:\Program Files\LibreOffice\program\bootstrap.ini` also contained `InstallMode=<installmode>`.
- Launching LibreOffice showed the error that `bootstrap.ini` was corrupted.
- Headless DOCX conversion failed with `libpng error: Write Error`.
- The system install path is under `C:\Program Files`, and the current process cannot repair it without administrator rights.

Conclusion: the failure is a LibreOffice installation/configuration failure, not evidence that the manuscript DOCX is corrupted.

## Fallback Render Chain

The manuscript was rendered through a LaTeX/PDF fallback:

1. `scripts/build_pdf_manuscript.py` converted `manuscript/final_manuscript.md` to `manuscript/final_manuscript.tex`.
2. MiKTeX `xelatex` compiled `manuscript/final_manuscript.pdf`.
3. Poppler `pdftoppm` rendered the PDF to PNG pages under `manuscript/rendered_pdf_verified/`.

Rendered pages:

- `manuscript/final_manuscript.pdf`: 14 pages.
- `manuscript/rendered_pdf_verified/page-01.png` through `page-14.png`.
- `manuscript/rendered_pdf_verified/contact_sheet.png` provides an all-page overview.

## QA Result

The rendered PDF pages were inspected as page PNGs. The final render has:

- no blank pages;
- no visibly clipped body text;
- no missing figures;
- no broken figure rendering;
- tables contained inside the printable page area;
- readable title, section hierarchy, figures, tables, methods, limitations, conclusions and references.

Minor residual issue: some wide tables require compact labels in the PDF fallback. This was addressed by shortening table headers in `scripts/build_pdf_manuscript.py`.

## Deliverable Interpretation

The Word manuscript is still the primary editable manuscript deliverable. The PDF and PNG render set are the verified visual QA artifacts because LibreOffice/Word rendering was unavailable in the local environment.
