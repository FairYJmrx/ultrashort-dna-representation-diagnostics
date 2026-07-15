# NAR Genomics and Bioinformatics Submission Checklist

This checklist records the current submission metadata and remaining fields for
the CK4P-MSP manuscript. It is a working checklist, not manuscript prose.

## Target Journal

- Target: NAR Genomics and Bioinformatics.
- Current manuscript route: Word/DOCX source with a submission-ready single PDF
  generated from the Word file.
- Repository route: private GitHub review-access repository first; public DOI
  after public release.

## Confirmed Author Metadata

- First author: Ruixiang Mei.
- First author ORCID: https://orcid.org/0009-0003-2128-0726.
- Corresponding author: Jianhua Huang.
- Corresponding author email: jhuang@cuhk.edu.cn.
- Shared affiliation currently used in the draft: The Chinese University of
  Hong Kong, Shenzhen, Shenzhen, Guangdong, China.
- Conflict of interest: The authors declare no competing interests.
- Patent/IP status: no current patent application or commercialization claim.

## Metadata Still To Confirm Before Submission

- Whether to use a more specific affiliation line, such as School of Data
  Science, The Chinese University of Hong Kong, Shenzhen.
- Jianhua Huang ORCID, if available.
- Funding statement:
  - If no grant supported the work, use:
    "This research received no specific grant from any funding agency in the
    public, commercial or not-for-profit sectors."
  - If a grant should be acknowledged, add exact funder name and grant number.
- Author contributions:
  - Current draft: Ruixiang Mei handled conceptualization, methodology,
    software, formal analysis, investigation, data curation, visualization,
    writing - original draft, and writing - review and editing.
  - Current draft: Jianhua Huang handled supervision and writing - review and
    editing.
  - Confirm final CRediT roles before submission.
- Acknowledgements, if any.
- Final institutional wording for ethics/data-governance boundary.
- Whether to retain local restricted sequencing length provenance or rely only
  on the published 50-75 bp mNGS read-length background source.

## Data And Code Availability

- Private review-access repository:
  https://github.com/FairYJmrx/ultrashort-dna-representation-diagnostics
- Branch: release.
- Repository visibility confirmed as private on 2026-07-16.
- Submission access route to decide:
  - add journal/editor/reviewer account as read-only collaborator; or
  - provide reviewer access credentials/token in the submission system; or
  - create a public/embargoed archive if the editorial office does not accept
    private GitHub access.
- Public DOI: not minted yet. Mint from a frozen release when the authors
  decide to make the repository public.

## Reference And Citation Tasks

- Export final numbered references in NAR/OUP style after the manuscript text
  is stable.
- Verify all BibTeX metadata for citation keys used in the manuscript.
- Verify Yang book metadata before final export:
  - English title: Practice and Progress of mNGS Report Interpretation.
  - Editor: Q.w. Yang or official publisher spelling to be confirmed from the
    copyright page.
  - Page 99 statement about common mNGS read length range.
- Check all first-use abbreviations in Abstract and main text:
  CK4P-MSP, CSP, MSP, MI, KSG, ART, CAMI, EIIP.

## Word/PDF Submission Checks

- Rebuild `paper/paper_manuscript.docx` from the split Markdown source.
- Export a single PDF containing text, references, tables and figures for
  initial submission.
- Render-check the PDF pages for:
  - figure label overlap;
  - missing glyphs in equations;
  - broken tables;
  - excessive blank space;
  - unreadable axes or legends.
- Confirm that all figure/table placeholders have been replaced.
- Confirm that no temporary citation keys such as `[@Wood2019]` remain.
- Confirm that no working comments such as "TBD" remain except fields that are
  deliberately unresolved before internal final approval.

## Final Pre-Submission Decision Points

- Choose whether to submit with the private GitHub repository only, or to make
  a public release at submission.
- Decide whether to post a preprint. If any patent/IP strategy changes, consult
  the institutional IP office before public release or preprint posting.
- Confirm final funding statement with Jianhua Huang.
- Confirm final author contributions with Jianhua Huang.
- Confirm final corresponding-author details and institutional affiliation.
