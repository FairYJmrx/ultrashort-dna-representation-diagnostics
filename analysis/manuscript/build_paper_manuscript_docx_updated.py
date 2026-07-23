from pathlib import Path
import re, csv, textwrap, zipfile, html
from collections import OrderedDict

from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.enum.style import WD_STYLE_TYPE

ROOT = Path(r'D:\AI-NGS\info')
PAPER = ROOT / 'paper'
OUT = PAPER / 'paper_manuscript_updated.docx'
FIG = PAPER / 'figures_docx'
FIG_RAW = PAPER / 'figures'
TABLE = PAPER / 'tables'
BIB = ROOT / 'references' / 'references.bib'

TITLE = 'Layered representation diagnostics for ultra-short metagenomic reads'

FIGURES = {
    'Figure 1': ('nature_fig1_framework.png', 'Representation-diagnostic framework and read-length regime.'),
    'Figure 2': ('nature_fig2_compact_stability.png', 'Compact stability under controlled perturbation.'),
    'Figure 3': ('nature_fig3_ck4p_msp_tradeoff.png', 'CK4P-MSP stability-readout-dimension trade-off.'),
    'Figure 4': ('nature_fig4_external_probes.png', 'External ART and CAMI consistency probes.'),
    'Figure 5': ('nature_fig5_full_position_upper_bound.png', 'Full-position diagnostic upper bound for positional information.'),
    'Figure 6': ('nature_fig6_local_mutation_sensitivity.png', 'Local mutation sensitivity and delta-readout.'),
    'Supplementary Figure S1': ('supp_fig_s1_baseline_audit.jpg', 'Baseline and mixed-metric audit.'),
    'Supplementary Figure S2': ('supp_fig_s2_mi_audit.jpg', 'Empirical MI and conditional-MI audit.'),
    'Supplementary Figure S3': ('supp_fig_s3_error_aware_art.jpg', 'Quality-stratified ART perturbation audit.'),
    'Supplementary Figure S4': ('supp_fig_s4_mutation_fraction_sweep.jpg', 'Local mutation-fraction sweep.'),
    'Supplementary Figure S5': ('supp_fig_s5_p_channel_counterfactual_audit.jpg', 'P-channel counterfactual and short-bin reliability audit.'),
    'Supplementary Figure S6': ('supp_fig_s6_msp_bin_gamma_sensitivity.png', 'MSP binset and gamma-sensitivity audit.'),
    'Supplementary Figure S9': ('supp_fig_s9_p_msp_relation_audit.jpg', 'P/MSP relation audit.'),
}
TABLES = {
    'Table 1': ('nature_table1_representation_families.csv', 'Representation families and diagnostic roles.'),
    'Table 2': ('nature_table2_data_layers.csv', 'Data layers, diagnostic questions, metrics and claim boundaries.'),
    'Table 3': ('nature_table3_compact_main_method.csv', 'Compact main-method metrics.'),
    'Table 4': ('nature_table4_local_mutation_sensitivity.csv', 'Local mutation sensitivity metrics.'),
    'Table 5': ('nature_table5_boundary_summary.csv', 'Boundary and mechanism summary.'),
}

# ---------- text utilities ----------

def read_text(name):
    return (PAPER / name).read_text(encoding='utf-8-sig')

def extract_english_draft(text):
    marker = '# English draft'
    if marker in text:
        return text.split(marker, 1)[1].strip()
    return text.strip()

def strip_working_notes(text):
    lines = []
    skip = False
    for line in text.splitlines():
        if line.strip().startswith('# Figure and Table Placement Summary'):
            skip = True
        if not skip:
            lines.append(line)
    return '\n'.join(lines).strip()

citation_order = OrderedDict()

def cite_replace(match):
    content = match.group(1)
    keys = [k.strip().lstrip('@') for k in re.split(r';', content) if k.strip()]
    nums=[]
    for key in keys:
        if key not in citation_order:
            citation_order[key] = len(citation_order)+1
        nums.append(str(citation_order[key]))
    return '[' + ','.join(nums) + ']'

def convert_citations(text):
    return re.sub(r'\[@([^\]]+)\]', cite_replace, text)

def clean_inline(text):
    text = text.replace('`', '')
    text = text.replace('–', '-')
    text = text.replace('—', '-')
    text = text.replace('‑', '-')
    text = text.replace('≤', '<=')
    text = text.replace('≥', '>=')
    return text

# ---------- bib parsing ----------

def parse_bib(path):
    raw = path.read_text(encoding='utf-8')
    entries = {}
    starts = list(re.finditer(r'@\w+\s*\{\s*([^,]+),', raw))
    for i,m in enumerate(starts):
        key = m.group(1).strip()
        start = m.end()
        end = starts[i+1].start() if i+1 < len(starts) else len(raw)
        body = raw[start:end]
        fields = {}
        for fm in re.finditer(r'\n\s*(\w+)\s*=\s*\{', body):
            fname = fm.group(1).lower()
            val_start = fm.end()
            depth = 1
            j = val_start
            while j < len(body) and depth:
                if body[j] == '{': depth += 1
                elif body[j] == '}': depth -= 1
                j += 1
            fields[fname] = body[val_start:j-1].replace('\n',' ').strip()
        entries[key] = fields
    return entries

bib = parse_bib(BIB)

def first_author_year(authors, year):
    if not authors:
        return ''
    first = authors.split(' and ')[0]
    surname = first.split(',')[0] if ',' in first else first.split()[-1]
    return f'{surname} et al. ({year})'

def format_ref(key, n):
    f = bib.get(key, {})
    if not f:
        return f'{n}. {key}. Reference metadata to be verified before submission.'
    authors = f.get('author','')
    title = f.get('title','')
    journal = f.get('journal','')
    year = f.get('year','')
    volume = f.get('volume','')
    pages = f.get('pages','')
    doi = f.get('doi','')
    # NAR final style should be produced by a reference manager; this is a clean draft list.
    bits = []
    if authors: bits.append(authors.replace(' and ', '; '))
    if title: bits.append(title + '.')
    tail = ''
    if journal: tail += journal
    if year: tail += f' {year}'
    if volume: tail += f';{volume}'
    if pages: tail += f':{pages}'
    if tail: bits.append(tail + '.')
    if doi: bits.append('doi:' + doi)
    return f'{n}. ' + ' '.join(bits)

# ---------- docx helpers ----------

def set_cell_shading(cell, fill):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:fill'), fill)
    tcPr.append(shd)

def set_cell_margins(cell, top=80, start=120, bottom=80, end=120):
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()
    tcMar = tcPr.first_child_found_in('w:tcMar')
    if tcMar is None:
        tcMar = OxmlElement('w:tcMar')
        tcPr.append(tcMar)
    for m, v in [('top', top), ('start', start), ('bottom', bottom), ('end', end)]:
        node = tcMar.find(qn(f'w:{m}'))
        if node is None:
            node = OxmlElement(f'w:{m}')
            tcMar.append(node)
        node.set(qn('w:w'), str(v))
        node.set(qn('w:type'), 'dxa')

def set_table_width(table, widths):
    table.autofit = False
    tbl = table._tbl
    tblPr = tbl.tblPr
    tblW = tblPr.find(qn('w:tblW'))
    if tblW is None:
        tblW = OxmlElement('w:tblW')
        tblPr.append(tblW)
    tblW.set(qn('w:type'), 'dxa')
    tblW.set(qn('w:w'), str(sum(widths)))
    for row in table.rows:
        for cell, width in zip(row.cells, widths):
            tcPr = cell._tc.get_or_add_tcPr()
            tcW = tcPr.find(qn('w:tcW'))
            if tcW is None:
                tcW = OxmlElement('w:tcW')
                tcPr.append(tcW)
            tcW.set(qn('w:type'), 'dxa')
            tcW.set(qn('w:w'), str(width))

def add_caption(doc, text):
    p = doc.add_paragraph(style='Caption')
    r = p.add_run(clean_inline(text))
    r.bold = True
    return p

def add_paragraph_with_runs(doc, text, style=None):
    p = doc.add_paragraph(style=style)
    # Italicize simple markdown *tokens*, keep citations normal.
    parts = re.split(r'(\*[^*]+\*)', text)
    for part in parts:
        if not part:
            continue
        if part.startswith('*') and part.endswith('*') and len(part) > 2:
            r = p.add_run(clean_inline(part[1:-1]))
            r.italic = True
        else:
            p.add_run(clean_inline(part))
    return p

def add_equation_block(doc, eq_text):
    compact = ' '.join(line.strip() for line in eq_text.splitlines() if line.strip())
    if not compact:
        return
    if r'\mathbf{x}_i' in compact and r'\hat{\mathbf{K}}_i' in compact:
        rendered = 'x_i = [? K?_i ; ? P?_i ; ? M?_i] / ?[? K?_i ; ? P?_i ; ? M?_i]??'
    elif 'd(i,j)' in compact and r'\mathbf{x}_i-\mathbf{x}_j' in compact:
        rendered = 'd(i,j) = ?x_i - x_j??'
    elif r'd_{\mathrm{block}}^2(i,j)' in compact:
        rendered = 'd_block?(i,j) = ???K?_i - K?_j??? + ???P?_i - P?_j??? + ???M?_i - M?_j???'
    else:
        rendered = compact
        replacements = [
            (r'\left', ''), (r'\right', ''), (r'\mathrm{block}', 'block'),
            (r'\mathbf{x}_i', 'x_i'), (r'\mathbf{x}_j', 'x_j'),
            (r'\hat{\mathbf{K}}_i', 'K?_i'), (r'\hat{\mathbf{K}}_j', 'K?_j'),
            (r'\hat{\mathbf{P}}_i', 'P?_i'), (r'\hat{\mathbf{P}}_j', 'P?_j'),
            (r'\hat{\mathbf{M}}_i', 'M?_i'), (r'\hat{\mathbf{M}}_j', 'M?_j'),
            (r'\alpha', '?'), (r'\beta', '?'), (r'\gamma', '?'),
            (r'\frac', ''), (r'\left[', '['), (r'\right]', ']'),
            (r'\left\|', '?'), (r'\right\|', '?'), (r'\|', '?'),
            (r'\left(', '('), (r'\right)', ')'), (r'\,', ' '), (r'\;', ' '),
            ('^2', '?'), ('_2', '?'), (r'\mathit{', ''), ('}', ''), ('{', ''),
        ]
        for old, new in replacements:
            rendered = rendered.replace(old, new)
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(4)
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.line_spacing = 1.0
    r = p.add_run(rendered)
    r.font.name = 'Cambria Math'
    r.font.size = Pt(11)
    return p

def add_table_from_csv(doc, csv_path, caption, max_rows=None):
    with open(csv_path, newline='', encoding='utf-8-sig') as f:
        rows = list(csv.reader(f))
    if max_rows:
        rows = rows[:max_rows]
    add_caption(doc, caption)
    ncols = len(rows[0])
    table = doc.add_table(rows=1, cols=ncols)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.style = 'Table Grid'
    hdr = table.rows[0].cells
    for i, val in enumerate(rows[0]):
        hdr[i].text = clean_inline(val)
        set_cell_shading(hdr[i], 'F2F4F7')
    for row in rows[1:]:
        cells = table.add_row().cells
        for i, val in enumerate(row):
            cells[i].text = clean_inline(val)
    # Width heuristic.
    if ncols == 4:
        widths = [1700, 3300, 2200, 2160]
    elif ncols == 5:
        widths = [1350, 2350, 2000, 1800, 1860]
    else:
        widths = [int(9360/ncols)] * ncols
    set_table_width(table, widths)
    for row in table.rows:
        for cell in row.cells:
            cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
            set_cell_margins(cell)
            for p in cell.paragraphs:
                p.paragraph_format.space_after = Pt(0)
                p.paragraph_format.line_spacing = 1.0
                for r in p.runs:
                    r.font.name = 'Times New Roman'
                    r.font.size = Pt(8)
    doc.add_paragraph()
    return table

def add_figure(doc, fig_key):
    fname, title = FIGURES[fig_key]
    path = FIG / fname
    if not path.exists():
        # main figures were copied as png only in raw folder; use raw png.
        path = FIG_RAW / fname
    add_caption(doc, f'{fig_key}. {title}')
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run()
    # S1 square can be 5.7, others 6.2.
    width = Inches(5.75 if 'S1' in fig_key else 6.2)
    if fig_key in ['Figure 1','Figure 2','Figure 3','Figure 4','Figure 5','Figure 6']:
        width = Inches(6.1)
    run.add_picture(str(path), width=width)
    doc.add_paragraph()

PLACEHOLDER_RE = re.compile(r'^\[Insert (.+?) here(?::| or|\]).*\]$')

def handle_placeholder(doc, line):
    m = PLACEHOLDER_RE.match(line.strip())
    if not m:
        return False
    key = m.group(1).strip()
    # Normalize possible phrases.
    if key.startswith('Figure') and key.split()[0] == 'Figure':
        key = ' '.join(key.split()[:2])
    elif key.startswith('Table'):
        key = ' '.join(key.split()[:2])
    elif key.startswith('Supplementary Figure'):
        key = ' '.join(key.split()[:3])
    if key in FIGURES:
        add_figure(doc, key)
        return True
    if key in TABLES:
        fname, title = TABLES[key]
        add_table_from_csv(doc, TABLE / fname, f'{key}. {title}')
        return True
    return False

def add_markdown_section(doc, md, skip_top_heading=False):
    md = convert_citations(md)
    in_equation = False
    eq_lines = []
    for raw_line in md.splitlines():
        line = raw_line.rstrip()
        if line.strip() == '$$':
            if in_equation:
                add_equation_block(doc, '\n'.join(eq_lines))
                in_equation = False
                eq_lines = []
            else:
                in_equation = True
                eq_lines = []
            continue
        if in_equation:
            eq_lines.append(line)
            continue
        if not line.strip():
            continue
        if handle_placeholder(doc, line):
            continue
        if line.startswith('#'):
            level = len(line) - len(line.lstrip('#'))
            title = line[level:].strip()
            if skip_top_heading and level == 1:
                continue
            # Avoid internal planning heading.
            if title.lower().startswith('figure and table placement'):
                continue
            style = 'Heading 1' if level == 1 else 'Heading 2' if level == 2 else 'Heading 3'
            doc.add_paragraph(clean_inline(title), style=style)
        elif line.startswith('- '):
            p = doc.add_paragraph(style='List Bullet')
            p.add_run(clean_inline(line[2:].strip()))
        else:
            add_paragraph_with_runs(doc, line.strip())

# ---------- build doc ----------
# ---------- build doc ----------

doc = Document()
sec = doc.sections[0]
sec.top_margin = Inches(1)
sec.bottom_margin = Inches(1)
sec.left_margin = Inches(1)
sec.right_margin = Inches(1)
sec.header_distance = Inches(0.5)
sec.footer_distance = Inches(0.5)

styles = doc.styles
styles['Normal'].font.name = 'Times New Roman'
styles['Normal']._element.rPr.rFonts.set(qn('w:eastAsia'), 'Times New Roman')
styles['Normal'].font.size = Pt(12)
styles['Normal'].paragraph_format.line_spacing = 1.0
styles['Normal'].paragraph_format.space_after = Pt(6)
for name, size, before, after in [('Heading 1',16,14,8),('Heading 2',14,12,6),('Heading 3',12,10,4)]:
    st = styles[name]
    st.font.name = 'Times New Roman'
    st._element.rPr.rFonts.set(qn('w:eastAsia'), 'Times New Roman')
    st.font.size = Pt(size)
    st.font.bold = True
    st.font.color.rgb = RGBColor(0,0,0)
    st.paragraph_format.space_before = Pt(before)
    st.paragraph_format.space_after = Pt(after)
    st.paragraph_format.line_spacing = 1.0
styles['Caption'].font.name = 'Times New Roman'
styles['Caption'].font.size = Pt(10)
styles['Caption'].font.italic = False
styles['Caption'].paragraph_format.space_before = Pt(6)
styles['Caption'].paragraph_format.space_after = Pt(4)

# Title page/front matter, no decorative cover.
p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = p.add_run(TITLE)
r.bold = True
r.font.name = 'Times New Roman'
r.font.size = Pt(16)

doc.add_paragraph('Authors: TBD', style=None).alignment = WD_ALIGN_PARAGRAPH.CENTER
doc.add_paragraph('Affiliations: TBD', style=None).alignment = WD_ALIGN_PARAGRAPH.CENTER

doc.add_paragraph('Abstract', style='Heading 1')
abstract = extract_english_draft(read_text('01_abstract.md'))
add_markdown_section(doc, abstract, skip_top_heading=True)

doc.add_paragraph('Introduction', style='Heading 1')
intro = extract_english_draft(read_text('02_intro_related_work.md'))
add_markdown_section(doc, intro, skip_top_heading=True)

# 03 already has H2/H3; skip top combined heading but keep Methods/Results.
section03 = strip_working_notes(read_text('03_method_experiments.md'))
add_markdown_section(doc, section03, skip_top_heading=True)

# 04 discussion etc.
section04 = read_text('04_limitations_future_conclusion.md')
add_markdown_section(doc, section04, skip_top_heading=True)

# Back matter from 05: include only formal sections, not citation support plan.
back = read_text('05_references.md')
start = back.find('## Data Availability')
formal = back[start:] if start >= 0 else back
# Exclude working References reminder and add real references below.
formal = formal.split('## References',1)[0].strip()
add_markdown_section(doc, formal, skip_top_heading=True)

# References generated from citation order.
doc.add_paragraph('References', style='Heading 1')
if citation_order:
    for key, n in citation_order.items():
        p = doc.add_paragraph(style=None)
        p.paragraph_format.first_line_indent = Inches(-0.25)
        p.paragraph_format.left_indent = Inches(0.25)
        p.add_run(format_ref(key, n))
else:
    doc.add_paragraph('References to be generated from the working bibliography before submission.')

# Add a short draft note at end, not visible as submission claim.
doc.add_paragraph('Draft note: Author names, affiliations, funding, repository DOI/accession, licence and final reference-manager formatting must be completed before submission.', style='Caption')

# Accessibility alt text for images via docPr descr.
for shape in doc.inline_shapes:
    docPr = shape._inline.docPr
    name = docPr.get('name') or 'Figure'
    docPr.set('descr', name)

# Save.
doc.save(OUT)
print('Wrote', OUT)
print('citation_count', len(citation_order))
print('citations', list(citation_order.keys()))

