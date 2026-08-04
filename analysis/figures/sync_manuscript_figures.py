"""Synchronize authoritative figure exports into the LaTeX manuscript tree.

The manuscript-facing filenames are stable, while several figures are generated
by contract-v2, historical-context, or dedicated audit entrypoints.  This map
prevents an older all-in-one generator from silently overwriting current figures.
"""

from __future__ import annotations

import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CONTRACT = ROOT / "figures" / "contract_v2"
LEGACY_MAIN = ROOT / "manuscript" / "figures"
PAPER_FIGURES = ROOT / "paper" / "figures"
COUNTERFACTUAL = ROOT / "results" / "stage3" / "contract_v2" / "p_channel_counterfactual_audit"
LATEX = ROOT / "paper_latex" / "figures"


FIGURE_MAP = {
    "main/nature_fig1_framework": LEGACY_MAIN / "nature_fig1_framework",
    "main/nature_fig2_compact_stability": CONTRACT / "figure_2_p_msp_contribution",
    "main/nature_fig3_ck4p_msp_tradeoff": CONTRACT / "figure_3_contract_v2_stability",
    "main/nature_fig4_external_probes": CONTRACT / "figure_4_external_contract_v2",
    "main/nature_fig5_full_position_upper_bound": LEGACY_MAIN / "nature_fig5_full_position_upper_bound",
    "main/nature_fig6_local_mutation_sensitivity": CONTRACT / "figure_6_local_readout_boundary",
    "supplementary/supp_fig_s1_baseline_audit": CONTRACT / "supplementary_figure_s1_baseline_audit",
    "supplementary/supp_fig_s2_mi_audit": CONTRACT / "supplementary_figure_s2_knn_mi",
    "supplementary/supp_fig_s3_error_aware_art": CONTRACT / "supplementary_figure_s3_art_current_contract",
    "supplementary/supp_fig_s4_mutation_fraction_sweep": CONTRACT / "supplementary_figure_s4_mutation_fraction",
    "supplementary/supp_fig_s5_p_channel_counterfactual_audit": COUNTERFACTUAL / "p_channel_counterfactual_audit",
    "supplementary/supp_fig_s6_msp_bin_gamma_sensitivity": CONTRACT / "supplementary_figure_s6_msp_sensitivity",
    "supplementary/supp_fig_s7_method_hardening_audit": CONTRACT / "supplementary_figure_s7_high_k_audit",
    "supplementary/supp_fig_s8_redundancy_runtime_audit": CONTRACT / "supp_fig_s8_redundancy_runtime_audit",
    "supplementary/supp_fig_s9_p_msp_relation_audit": CONTRACT / "supplementary_figure_s9_p_msp_relation",
    "supplementary/supp_fig_s10_cami2_marine_probe": CONTRACT / "supplementary_figure_s10_cami2_marine_probe",
    "supplementary/supp_fig_s11_factorial_scaling": CONTRACT / "supplementary_figure_s11_factorial_scaling",
    "supplementary/supp_fig_s12_historical_descriptor_audit": CONTRACT / "supplementary_figure_s12_historical_descriptor_audit",
    "supplementary/supp_fig_s13_short_read_continuity": CONTRACT / "supplementary_figure_s13_short_read_continuity",
    "supplementary/supp_fig_s14_fixed_head_sensitivity": CONTRACT / "supplementary_figure_s14_fixed_head_sensitivity",
    "supplementary/supp_fig_s15_pkm_pareto_audit": CONTRACT / "supplementary_figure_s15_pkm_pareto_audit",
}

STALE_STEMS = [
    "main/nature_fig7_spaced_seed_transfer",
    "main/nature_fig8_context_arg_boundaries",
    "main/supp_fig_s2_mi_audit",
    "main/supp_fig_s6_msp_bin_gamma_sensitivity",
    "main/supp_fig_s7_method_hardening_audit",
    "main/supp_fig_s8_redundancy_runtime_audit",
]


def main() -> None:
    removed = 0
    for stale_stem in STALE_STEMS:
        for suffix in (".pdf", ".png", ".svg", ".tiff"):
            stale = (LATEX / stale_stem).with_suffix(suffix)
            if stale.exists():
                stale.unlink()
                removed += 1

    copied = 0
    for destination_stem, source_stem in FIGURE_MAP.items():
        destination = LATEX / destination_stem
        destination.parent.mkdir(parents=True, exist_ok=True)
        for suffix in (".pdf", ".png", ".svg"):
            source = source_stem.with_suffix(suffix)
            if not source.exists():
                raise FileNotFoundError(f"Missing authoritative figure asset: {source}")
            shutil.copy2(source, destination.with_suffix(suffix))
            copied += 1
    print(f"Synchronized {copied} assets and removed {removed} stale copies in {LATEX}")


if __name__ == "__main__":
    main()
