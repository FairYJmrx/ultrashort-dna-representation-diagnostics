from pathlib import Path
import math
import pandas as pd
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from PIL import Image

ROOT = Path(r'D:\AI-NGS\info')
OUT = ROOT / 'paper' / 'figures'
DOCX = ROOT / 'paper' / 'figures_docx'
OUT.mkdir(parents=True, exist_ok=True)
DOCX.mkdir(parents=True, exist_ok=True)

mpl.rcParams.update({
    'font.family': 'sans-serif',
    'font.sans-serif': ['Arial', 'Helvetica', 'DejaVu Sans', 'sans-serif'],
    'svg.fonttype': 'none',
    'pdf.fonttype': 42,
    'font.size': 8,
    'axes.spines.right': False,
    'axes.spines.top': False,
    'axes.linewidth': 0.8,
    'axes.titleweight': 'bold',
    'axes.titlesize': 9,
    'axes.labelsize': 8,
    'xtick.labelsize': 7,
    'ytick.labelsize': 7,
    'legend.fontsize': 7,
    'legend.frameon': False,
})

COLORS = {
    'proposed': '#2A6F97',
    'identity': '#6C757D',
    'reduction': '#B56576',
    'sketch': '#6A994E',
    'signal': '#D97706',
    'support': '#577590',
    'light': '#E9ECEF',
    'dark': '#212529',
}

def save_all(fig, stem, w_docx=1800):
    base = OUT / stem
    fig.savefig(base.with_suffix('.svg'), bbox_inches='tight')
    fig.savefig(base.with_suffix('.pdf'), bbox_inches='tight')
    fig.savefig(base.with_suffix('.png'), dpi=450, bbox_inches='tight')
    fig.savefig(base.with_suffix('.tiff'), dpi=600, bbox_inches='tight')
    plt.close(fig)
    im = Image.open(base.with_suffix('.png')).convert('RGB')
    scale = w_docx / im.width
    if scale < 1:
        im = im.resize((int(im.width * scale), int(im.height * scale)), Image.Resampling.LANCZOS)
    im.save(DOCX / f'{stem}.jpg', quality=92, optimize=True)


def clean_label(x):
    if pd.isna(x):
        return ''
    s = str(x)
    repl = {
        'ckmer4_property_multiscale_mean_l2': 'CK4P-MSP',
        'ckmer4_property_l2': 'CK4+P',
        'ckmer4_count_l2': 'CK4',
        'ckmer5_count_l2': 'CK5',
        'ckmer6_count_l2': 'CK6',
        'ckmer7_count_l2': 'CK7',
        'cspaced_property_l2': 'CSP+P',
        'hybrid_ckmer5_csp': 'CK5+CSP',
        'minhash_k5_s128': 'MinHash k5',
        'minhash_k7_s128': 'MinHash k7',
        'eiip_l2': 'EIIP positional',
        'eiip_summary_l2': 'EIIP summary',
        'property_channels': 'Property channels',
        'base_property': 'Base property',
        'one_hot_l2': 'One-hot',
        'ck5_pca147': 'CK5 PCA-147',
        'ck5_pca222': 'CK5 PCA-222',
        'ck5_svd147': 'CK5 SVD-147',
        'ck5_svd222': 'CK5 SVD-222',
        'ck7_pca147': 'CK7 PCA-147',
        'ck7_pca222': 'CK7 PCA-222',
        'ck7_svd147': 'CK7 SVD-147',
        'ck7_svd222': 'CK7 SVD-222',
    }
    return repl.get(s, s.replace('_', ' '))

# Figure S1: baseline audit.
stab_dim = pd.read_csv(ROOT / 'results' / 'stage3' / 'reviewer_response' / 'dimension_reduction_baselines' / 'dimension_reduction_stability_summary.csv')
readout_dim = pd.read_csv(ROOT / 'results' / 'stage3' / 'reviewer_response' / 'dimension_reduction_baselines' / 'dimension_reduction_readout_summary.csv')
compact_ci = pd.read_csv(ROOT / 'results' / 'stage3' / 'bootstrap_ci' / 'stage3_compact_bootstrap_ci.csv')
block_stab = pd.read_csv(ROOT / 'results' / 'stage3' / 'reviewer_response' / 'mixed_metric_audit' / 'block_weight_stability_summary.csv')
block_readout = pd.read_csv(ROOT / 'results' / 'stage3' / 'reviewer_response' / 'mixed_metric_audit' / 'block_weight_delta_readout_summary.csv')

# Build stability panel from dimension-reduction plus compact hash/signal baselines.
stab_a = stab_dim[['representation','representation_label','paired_cosine','l2_drift','retrieval_top1','median_features']].copy()
stab_a['family'] = np.where(stab_a['representation'].str.contains('pca|svd'), 'Same-dim reduction',
                    np.where(stab_a['representation'].str.contains('property'), 'Proposed/property-aware', 'Identity k-mer'))
ci_map_cols = {c: c for c in compact_ci.columns}
# infer compact CI labels and metrics robustly
if 'representation' in compact_ci.columns:
    comp = compact_ci.copy()
else:
    comp = pd.DataFrame()
needed = ['minhash_k5_s128','minhash_k7_s128','eiip_l2','eiip_summary_l2','cspaced_property_l2','hybrid_ckmer5_csp']
rows=[]
if not comp.empty:
    for rep in needed:
        d = comp[comp['representation'].astype(str).eq(rep)] if 'representation' in comp.columns else pd.DataFrame()
        if d.empty:
            continue
        # choose aggregate row if available, otherwise mean across rows
        cos_col = next((c for c in d.columns if c in ['paired_cosine_mean','paired_cosine','mean_paired_cosine']), None)
        l2_col = next((c for c in d.columns if c in ['l2_delta_mean','l2_drift','mean_l2_delta','l2_mean']), None)
        ret_col = next((c for c in d.columns if c in ['retrieval_top1','retrieval_top1_mean','mean_retrieval_top1']), None)
        feat_col = next((c for c in d.columns if c in ['n_features','median_features','features']), None)
        if cos_col:
            rows.append({
                'representation': rep,
                'representation_label': clean_label(rep),
                'paired_cosine': float(pd.to_numeric(d[cos_col], errors='coerce').mean()),
                'l2_drift': float(pd.to_numeric(d[l2_col], errors='coerce').mean()) if l2_col else np.nan,
                'retrieval_top1': float(pd.to_numeric(d[ret_col], errors='coerce').mean()) if ret_col else np.nan,
                'median_features': float(pd.to_numeric(d[feat_col], errors='coerce').median()) if feat_col else np.nan,
                'family': 'Hash/sketch or signal',
            })
if rows:
    stab_a = pd.concat([stab_a, pd.DataFrame(rows)], ignore_index=True)

fig = plt.figure(figsize=(7.2, 7.2), constrained_layout=True)
gs = fig.add_gridspec(2, 2, height_ratios=[1.05, 1.0])
ax1 = fig.add_subplot(gs[0,0])
ax2 = fig.add_subplot(gs[0,1])
ax3 = fig.add_subplot(gs[1,:])
family_colors = {
    'Proposed/property-aware': COLORS['proposed'],
    'Identity k-mer': COLORS['identity'],
    'Same-dim reduction': COLORS['reduction'],
    'Hash/sketch or signal': COLORS['sketch'],
}
# Filter for readable main comparators.
show_reps = ['CK4P-MSP','CK4+P','CK4','CK5','CK7 SVD-147','CK7 PCA-147','CK5 SVD-147','CK5 PCA-147','MinHash k5','MinHash k7','EIIP positional','EIIP summary','CSP+P','CK5+CSP']
stab_a['label'] = stab_a['representation_label'].map(clean_label)
stab_plot = stab_a[stab_a['label'].isin(show_reps)].copy()
for fam, sub in stab_plot.groupby('family'):
    ax1.scatter(sub['median_features'], sub['paired_cosine'], s=38, color=family_colors.get(fam, '#333'), label=fam, alpha=0.9, edgecolor='white', linewidth=0.5)
for _, r in stab_plot.iterrows():
    lab = r['label']
    if lab in ['CK4P-MSP','CK4+P','CK4','CK5','CK7 SVD-147','MinHash k5','EIIP summary','CSP+P']:
        ax1.annotate(lab, (r['median_features'], r['paired_cosine']), xytext=(3, 3), textcoords='offset points', fontsize=6.5)
ax1.set_xscale('log')
ax1.set_xlabel('Feature dimension (log scale)')
ax1.set_ylabel('Paired cosine (higher is better)')
ax1.set_title('A  Stability audit across baseline families', loc='left')
ax1.set_ylim(0.90, 1.002)
ax1.grid(True, color='#E9ECEF', linewidth=0.6)
ax1.legend(loc='lower right', ncol=1)

# Readout panel.
readout_dim['label'] = readout_dim['representation_label'].map(clean_label)
readout_show = ['CK4P-MSP','CK4+P','CK4','CK5','CK7 SVD-147','CK7 PCA-147','CK5 SVD-147','CK5 PCA-147','CK7 SVD-222','CK7 PCA-222']
rd = readout_dim[readout_dim['label'].isin(readout_show)].copy()
rd['family'] = np.where(rd['label'].str.contains('PCA|SVD'), 'Same-dim reduction',
                np.where(rd['label'].isin(['CK4P-MSP','CK4+P']), 'Proposed/property-aware', 'Identity k-mer'))
for fam, sub in rd.groupby('family'):
    ax2.scatter(sub['median_features'], sub['macro_f1'], s=38, color=family_colors.get(fam, '#333'), label=fam, alpha=0.9, edgecolor='white', linewidth=0.5)
for _, r in rd.iterrows():
    if r['label'] in ['CK4P-MSP','CK5','CK5 PCA-147','CK7 SVD-147','CK4']:
        ax2.annotate(r['label'], (r['median_features'], r['macro_f1']), xytext=(3, 3), textcoords='offset points', fontsize=6.5)
ax2.set_xscale('log')
ax2.set_xlabel('Feature dimension (log scale)')
ax2.set_ylabel('Macro-F1')
ax2.set_title('B  Readout audit at matched dimensions', loc='left')
ax2.set_ylim(max(0, rd['macro_f1'].min()-0.02), rd['macro_f1'].max()+0.02)
ax2.grid(True, color='#E9ECEF', linewidth=0.6)

# Block-weight panel: L2 drift bar + delta-readout dot.
order = ['identity_only','ck4_plus_p','ck4p_msp','identity_dominant','property_dominant','property_only']
labels = {
    'identity_only':'Identity only', 'ck4_plus_p':'CK4+P', 'ck4p_msp':'CK4P-MSP',
    'identity_dominant':'Identity-dominant', 'property_dominant':'Property-dominant', 'property_only':'Property only'
}
bs = block_stab.set_index('weight_name').reindex(order).reset_index()
br = block_readout[block_readout['classifier'].eq('logistic')].drop_duplicates('weight_name').set_index('weight_name').reindex(order).reset_index()
x = np.arange(len(order))
bar_colors = [COLORS['identity'], COLORS['support'], COLORS['proposed'], '#8D99AE', '#90BE6D', COLORS['signal']]
ax3.bar(x, bs['l2_drift'], color=bar_colors, alpha=0.86, width=0.62, label='L2 drift')
ax3.set_ylabel('L2 drift (lower is better)')
ax3.set_xticks(x)
ax3.set_xticklabels([labels[o] for o in order], rotation=20, ha='right')
ax3.set_title('C  Block-weight audit separates metric stability from biological readout', loc='left')
ax3.grid(True, axis='y', color='#E9ECEF', linewidth=0.6)
ax3b = ax3.twinx()
ax3b.plot(x, br['macro_f1'], color=COLORS['dark'], marker='o', linewidth=1.4, label='Delta-readout macro-F1')
ax3b.set_ylabel('Delta-readout macro-F1')
ax3b.set_ylim(0.86, 1.00)
lines, labs = ax3.get_legend_handles_labels()
lines2, labs2 = ax3b.get_legend_handles_labels()
ax3.legend(lines+lines2, labs+labs2, loc='upper center', ncol=2)
fig.suptitle('Supplementary Figure S1 | Baseline and mixed-metric audit', x=0.02, ha='left', fontsize=11, fontweight='bold')
save_all(fig, 'supp_fig_s1_baseline_audit')

# Figure S2: MI audit.
mi = pd.read_csv(ROOT / 'results' / 'stage3' / 'reviewer_response' / 'mi_audit' / 'mi_audit_summary.csv')
mi['label'] = mi['representation'].map(clean_label)
mi_order = ['CK4','CK4+P','CK4P-MSP','Property channels','Base property','CK5','One-hot']
mi_plot = mi[mi['label'].isin(mi_order)].copy()
mi_plot['label'] = pd.Categorical(mi_plot['label'], mi_order, ordered=True)
mi_plot = mi_plot.sort_values('label')
fig, ax = plt.subplots(figsize=(6.4, 3.6), constrained_layout=True)
x = np.arange(len(mi_plot))
w = 0.36
ax.bar(x-w/2, mi_plot['pooled_mi_bits'], width=w, color=COLORS['support'], label='Pooled MI proxy')
ax.bar(x+w/2, mi_plot['conditional_mi_bits'], width=w, color=COLORS['proposed'], label='Conditional MI proxy')
for i, (_, r) in enumerate(mi_plot.iterrows()):
    if r.get('conditional_perm_p', 1) <= 0.01:
        ax.text(i+w/2, r['conditional_mi_bits']+0.025, '*', ha='center', va='bottom', fontsize=10)
ax.set_ylabel('Mutual-information proxy (bits)')
ax.set_xticks(x)
ax.set_xticklabels(mi_plot['label'], rotation=20, ha='right')
ax.set_title('Supplementary Figure S2 | Empirical information-gain audit', loc='left')
ax.grid(True, axis='y', color='#E9ECEF', linewidth=0.6)
ax.legend(loc='upper left')
ax.text(0.99, 0.02, '* permutation P <= 0.01', transform=ax.transAxes, ha='right', va='bottom', fontsize=7, color='#495057')
save_all(fig, 'supp_fig_s2_mi_audit')

# Figure S3: error-aware ART.
err = pd.read_csv(ROOT / 'results' / 'stage3' / 'reviewer_response' / 'error_aware_perturbation' / 'error_aware_perturbation_quality_summary.csv')
err['label'] = err['representation'].map(clean_label)
sel_labels = ['CSP+P','CK5+CSP']
err = err[err['label'].isin(sel_labels)].copy()
quality_order = ['low','mid','high']
err['quality_bin'] = pd.Categorical(err['quality_bin'], quality_order, ordered=True)
fig, axes = plt.subplots(1, 2, figsize=(7.0, 3.25), constrained_layout=True, sharex=True)
for label, sub in err.groupby('label'):
    sub = sub.sort_values(['source_length','quality_bin'])
    agg = sub.groupby('quality_bin', observed=False).agg({'paired_cosine_mean':'mean','l2_delta_mean':'mean'}).reindex(quality_order).reset_index()
    axes[0].plot(quality_order, agg['paired_cosine_mean'], marker='o', linewidth=1.6, label=label)
    axes[1].plot(quality_order, agg['l2_delta_mean'], marker='o', linewidth=1.6, label=label)
axes[0].set_title('A  Paired cosine across quality bins', loc='left')
axes[0].set_ylabel('Paired cosine')
axes[0].set_ylim(0.92, 1.0)
axes[1].set_title('B  L2 drift across quality bins', loc='left')
axes[1].set_ylabel('L2 drift')
for ax in axes:
    ax.set_xlabel('Quality bin')
    ax.grid(True, color='#E9ECEF', linewidth=0.6)
axes[1].legend(loc='upper right')
fig.suptitle('Supplementary Figure S3 | Quality-stratified ART perturbation audit', x=0.02, ha='left', fontsize=11, fontweight='bold')
save_all(fig, 'supp_fig_s3_error_aware_art')

# Figure S4: mutation-fraction sweep.
mut = pd.read_csv(ROOT / 'results' / 'stage3' / 'reviewer_response' / 'local_mutation_fraction_sweep' / 'local_mutation_fraction_delta_readout_summary.csv')
mut['label'] = mut['representation'].map(clean_label)
sel = ['CK4P-MSP','CK4+P','CK4','CK5','Property channels']
mut = mut[(mut['classifier'].eq('logistic')) & (mut['label'].isin(sel))].copy()
fig, ax = plt.subplots(figsize=(6.2, 3.4), constrained_layout=True)
for label, sub in mut.groupby('label'):
    sub = sub.sort_values('mutation_fraction')
    color = COLORS['proposed'] if label == 'CK4P-MSP' else (COLORS['support'] if label in ['CK4+P','Property channels'] else COLORS['identity'])
    lw = 2.2 if label == 'CK4P-MSP' else 1.4
    ax.plot(sub['mutation_fraction']*100, sub['macro_f1'], marker='o', linewidth=lw, label=label, color=color, alpha=0.95)
ax.set_xlabel('Mutated fraction (%)')
ax.set_ylabel('Delta-readout macro-F1')
ax.set_title('Supplementary Figure S4 | Local-mutation fraction sensitivity', loc='left')
ax.set_ylim(0.84, 1.01)
ax.grid(True, color='#E9ECEF', linewidth=0.6)
ax.legend(loc='lower right', ncol=2)
save_all(fig, 'supp_fig_s4_mutation_fraction_sweep')

# Write source-data inventory.
inv = OUT.parent / 'figure_table_inventory.md'
inv.write_text('''# Figure and Table Inventory\n\n## Main figures\n\n- Figure 1: Representation-diagnostic framework and read-length regime. Source script: `info/scripts/generate_nature_main_figures.py`. Asset: `paper/figures/nature_fig1_framework.*`.\n- Figure 2: Compact stability of identity, spaced, and property-aware representations. Source script: `info/scripts/generate_nature_main_figures.py` plus bootstrap tables. Asset: `paper/figures/nature_fig2_compact_stability.*`.\n- Figure 3: CK4P-MSP compact trade-off between stability, readout, and feature dimension. Source script: `info/scripts/generate_nature_main_figures.py`. Asset: `paper/figures/nature_fig3_ck4p_msp_tradeoff.*`.\n- Figure 4: External ART/CAMI consistency probes. Source script: `info/scripts/generate_nature_main_figures.py`. Asset: `paper/figures/nature_fig4_external_probes.*`.\n- Figure 5: Full-position diagnostic upper-bound analysis. Source script: `info/scripts/generate_nature_main_figures.py`. Asset: `paper/figures/nature_fig5_full_position_upper_bound.*`.\n- Figure 6: Local mutation sensitivity and delta-readout analysis. Source script: `info/scripts/generate_nature_main_figures.py`. Asset: `paper/figures/nature_fig6_local_mutation_sensitivity.*`.\n\n## Supplementary figures generated for the paper folder\n\n- Supplementary Figure S1: Baseline and mixed-metric audit, including same-dimensional PCA/SVD, hash/sketch or signal baselines, and block-weight sensitivity. Source script: `info/scripts/generate_paper_supplementary_figures.py`. Asset: `paper/figures/supp_fig_s1_baseline_audit.*`.\n- Supplementary Figure S2: Empirical MI/conditional-MI proxy audit for mutation labels. Source script: `info/scripts/generate_paper_supplementary_figures.py`. Asset: `paper/figures/supp_fig_s2_mi_audit.*`.\n- Supplementary Figure S3: Error-aware, quality-stratified ART perturbation audit. Source script: `info/scripts/generate_paper_supplementary_figures.py`. Asset: `paper/figures/supp_fig_s3_error_aware_art.*`.\n- Supplementary Figure S4: Local-mutation fraction sweep. Source script: `info/scripts/generate_paper_supplementary_figures.py`. Asset: `paper/figures/supp_fig_s4_mutation_fraction_sweep.*`.\n\n## Tables\n\n- Table 1: Representation families. Source script: `info/scripts/generate_nature_main_tables.py`. Asset: `paper/tables/nature_table1_representation_families.*`.\n- Table 2: Data layers and perturbation design. Source script: `info/scripts/generate_nature_main_tables.py`; requires paper-level note for quality-stratified ART row. Asset: `paper/tables/nature_table2_data_layers.*`.\n- Table 3: Compact main-method metrics. Source script: `info/scripts/generate_nature_main_tables.py`. Asset: `paper/tables/nature_table3_compact_main_method.*`.\n- Table 4: Local mutation sensitivity metrics. Source script: `info/scripts/generate_nature_main_tables.py`. Asset: `paper/tables/nature_table4_local_mutation_sensitivity.*`.\n- Table 5: Boundary and mechanism summary. Source script: `info/scripts/generate_nature_main_tables.py`. Asset: `paper/tables/nature_table5_boundary_summary.*`.\n''', encoding='utf-8')
print('Generated supplementary figures and inventory in', OUT.parent)
