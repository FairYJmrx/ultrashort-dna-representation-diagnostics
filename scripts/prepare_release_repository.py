from __future__ import annotations

import argparse
import fnmatch
import shutil
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = PROJECT_ROOT.parent / "ultrashort-dna-representation-diagnostics-release-clean"

SCRIPT_ALLOWLIST = [
    "prepare_release_repository.py",
    "audit_result_inventory.py",
    "audit_final_provenance.py",
    "prepare_close_relative_genomes.py",
    "make_genome_slice_reads.py",
    "make_close_relative_reads.py",
    "make_hardened_reads.py",
    "make_toy_reads.py",
    "run_stage2_representation_grid.py",
    "run_stage2_csp_ablation.py",
    "run_stage2_attention_breakpoint.py",
    "run_stage2_arg_snp_boundary.py",
    "run_parameter_sensitivity.py",
    "run_spaced_pattern_sanity.py",
    "run_stage3_compact_baselines.py",
    "run_stage3_art_generate_and_evaluate.py",
    "run_stage3_art_validation.py",
    "summarize_stage3_art_quality.py",
    "download_stage3_cami_toy_low.py",
    "inspect_stage3_cami_remote_tar.py",
    "prepare_stage3_cami_toy_low_subset.py",
    "run_stage3_cami_probe.py",
    "run_position_property_controlled_tasks.py",
    "generate_stage3_bootstrap_ci.py",
    "generate_fullmatrix_property_contribution_ci.py",
    "generate_stage3_manuscript_assets_v2.py",
    "build_stage2_manuscript.py",
    "build_stage3_manuscript.py",
    "build_stage3_manuscript_v4.py",
    "polish_stage3_manuscript_v4.py",
    "finalize_stage3_manuscript_v5.py",
    "repair_stage3_v4_word_equations.py",
]

FINAL_TABLE_NAMES = [
    "stage2_table_hospital_69_75_focus",
    "stage2_table_stability_gain_summary",
    "stage2_table_csp_component_singletons",
    "stage2_table_csp_full_ablation",
    "stage2_table_readout_aggregate",
    "stage2_table_attention_change_points",
    "stage2_table_arg_snp_best_stability",
    "stage2_table_arg_snp_readout_aggregate",
    "stage3_table_compact_bootstrap_ci",
    "stage3_table_art_bootstrap_ci",
    "stage3_table_art_quality_bootstrap_ci",
    "stage3_table_cami_macro_f1_bootstrap_ci",
    "stage3_table_fullmatrix_property_controlled_ci",
    "stage3_table_fullmatrix_property_controlled_delta_ci",
    "stage3_table_fullmatrix_property_art_ci",
    "stage3_table_fullmatrix_property_art_delta_ci",
    "stage3_table_fullmatrix_property_cami_ci",
    "stage3_table_fullmatrix_property_cami_delta_ci",
    "stage3_table_representation_scheme_summary",
    "table_spaced_pattern_sanity_cardinality",
    "table_spaced_pattern_sanity_best_four_position",
]

FIGURE_FILES = [
    "manuscript/figures/stage3_fig_layered_evidence_architecture.png",
    "manuscript/figures/stage3_fig_layered_evidence_architecture.svg",
    "manuscript/figures/stage3_fig_layered_evidence_architecture.pdf",
    "manuscript/figures/stage2_fig_stability_grid.png",
    "manuscript/figures/stage2_fig_hospital_69_75_l2.png",
    "manuscript/figures/stage2_fig_csp_singleton_ablation.png",
    "manuscript/figures/stage2_fig_readout_aggregate.png",
    "manuscript/figures/stage2_fig_attention_breakpoints.png",
    "manuscript/figures/stage2_fig_attention_f1_breakpoints.png",
    "manuscript/figures/stage2_fig_arg_snp_readout.png",
]

FILE_ALLOWLIST = [
    "requirements.txt",
    "configs/experiment_matrix.yaml",
    "references/references.bib",
    "docs/stage3_external_validation_task_plan.md",
    "docs/stage3_reinforcement_execution_report.md",
    "docs/stage3_submission_metadata_and_reproducibility.md",
    "docs/stage3_download_scope_decision.md",
    "docs/final_release_provenance_map.md",
    "manuscript/final_manuscript.md",
    "manuscript/final_manuscript.docx",
    "manuscript/stage3_manuscript_v5.md",
    "manuscript/stage3_manuscript_v5.docx",
    "data/real_slices/close_relative_genomes_manifest.csv",
    "data/real_slices/close_relative_genomes_manifest_preview.csv",
    "data/real_slices/close_relative_reads.csv",
    "data/real_slices/local_wgs_slices.csv",
    "data/real_slices/stage2_close_relative_base_reads.csv",
    "data/stage3/cami/cami_toy_low_subset_reads.csv",
    "data/stage3/cami/cami_toy_low_subset_reads_expanded.csv",
    "results/stage3/cami_subset_expanded_metadata.json",
    "results/stage3/cami_subset_metadata.json",
    "results/stage3/cami_remote_tar_manifest.csv",
    "results/stage3/gigadb_100344_files.csv",
]

SELECTED_RESULT_FILES = [
    # Stage 2 mechanism evidence, excluding bulky generated read intermediates.
    "results/stage2/representation_grid/stability_grid.csv",
    "results/stage2/representation_grid/readout_grid.csv",
    "results/stage2/representation_grid/stage2_representation_grid_run.json",
    "results/stage2/representation_grid/stage2_representation_grid_summary.md",
    "results/stage2/csp_ablation/csp_ablation_metrics.csv",
    "results/stage2/csp_ablation/csp_ablation_deltas.csv",
    "results/stage2/csp_ablation/csp_ablation_run.json",
    "results/stage2/csp_ablation/csp_ablation_summary.md",
    "results/stage2/attention_breakpoint/attention_breakpoint_change_points.csv",
    "results/stage2/attention_breakpoint/attention_breakpoint_results.csv",
    "results/stage2/attention_breakpoint/attention_breakpoint_run.json",
    "results/stage2/attention_breakpoint/attention_breakpoint_summary.md",
    "results/stage2/arg_snp_boundary/arg_snp_stability.csv",
    "results/stage2/arg_snp_boundary/arg_snp_readout.csv",
    "results/stage2/arg_snp_boundary/arg_snp_boundary_run.json",
    "results/stage2/arg_snp_boundary/arg_snp_boundary_summary.md",
    # Stage 3 validation evidence.
    "results/stage3/compact_baselines/compact_baseline_interpretation.md",
    "results/stage3/compact_baselines/compact_baseline_readout.csv",
    "results/stage3/compact_baselines/compact_baseline_stability.csv",
    "results/stage3/compact_baselines/stage2_representation_grid_summary.md",
    "results/stage3/compact_baselines/stage3_compact_baselines_run.json",
    "results/stage3/art_illumina/art_completed_summary.md",
    "results/stage3/art_illumina/art_generation_manifest.csv",
    "results/stage3/art_illumina/art_stability_metrics.csv",
    "results/stage3/art_illumina/stage3_art_generate_run.json",
    "results/stage3/art_quality_stratified/art_quality_stratified_stability.csv",
    "results/stage3/art_quality_stratified/art_quality_stratified_run.json",
    "results/stage3/art_quality_stratified/art_quality_stratified_summary.md",
    "results/stage3/cami_probe_expanded/cami_probe_readout.csv",
    "results/stage3/cami_probe_expanded/cami_probe_summary.md",
    "results/stage3/cami_probe_expanded/stage3_cami_probe_run.json",
    "results/stage3/bootstrap_ci/stage3_compact_bootstrap_ci.csv",
    "results/stage3/bootstrap_ci/stage3_art_bootstrap_ci.csv",
    "results/stage3/bootstrap_ci/stage3_art_quality_bootstrap_ci.csv",
    "results/stage3/bootstrap_ci/stage3_cami_macro_f1_bootstrap_ci.csv",
    "results/stage3/bootstrap_ci/stage3_bootstrap_ci_summary.md",
    "results/stage3/position_property_ablation/compact_baseline_stability.csv",
    "results/stage3/position_property_ablation/compact_baseline_readout.csv",
    "results/stage3/position_property_ablation/compact_baseline_readout_all_conditions.csv",
    "results/stage3/position_property_ablation/stage3_compact_baselines_run.json",
    "results/stage3/position_property_ablation/stage2_representation_grid_summary.md",
    "results/stage3/art_ck4p_position_ablation/art_stability_metrics.csv",
    "results/stage3/art_ck4p_position_ablation/art_validation_summary.md",
    "results/stage3/art_ck4p_position_ablation/stage3_art_validation_run.json",
    "results/stage3/cami_ck4p_position_ablation_fast/cami_probe_readout.csv",
    "results/stage3/cami_ck4p_position_ablation_fast/cami_probe_summary.md",
    "results/stage3/cami_ck4p_position_ablation_fast/stage3_cami_probe_run.json",
    "results/stage3/fullmatrix_property_contribution_controlled/position_property_controlled_results.csv",
    "results/stage3/fullmatrix_property_contribution_controlled/position_property_controlled_run.json",
    "results/stage3/art_fullmatrix_property_contribution/art_stability_metrics.csv",
    "results/stage3/art_fullmatrix_property_contribution/art_validation_summary.md",
    "results/stage3/art_fullmatrix_property_contribution/stage3_art_validation_run.json",
    "results/stage3/cami_fullmatrix_property_contribution/cami_probe_readout.csv",
    "results/stage3/cami_fullmatrix_property_contribution/cami_probe_summary.md",
    "results/stage3/cami_fullmatrix_property_contribution/stage3_cami_probe_run.json",
    "results/stage3/fullmatrix_property_contribution_ci/fullmatrix_property_controlled_ci.csv",
    "results/stage3/fullmatrix_property_contribution_ci/fullmatrix_property_controlled_delta_ci.csv",
    "results/stage3/fullmatrix_property_contribution_ci/fullmatrix_property_art_ci.csv",
    "results/stage3/fullmatrix_property_contribution_ci/fullmatrix_property_art_delta_ci.csv",
    "results/stage3/fullmatrix_property_contribution_ci/fullmatrix_property_cami_ci.csv",
    "results/stage3/fullmatrix_property_contribution_ci/fullmatrix_property_cami_delta_ci.csv",
    "results/stage3/fullmatrix_property_contribution_ci/fullmatrix_property_contribution_ci_summary.md",
    "results/stage3/spaced_pattern_sanity/spaced_pattern_sanity_stability.csv",
    "results/stage3/spaced_pattern_sanity/spaced_pattern_sanity_cardinality_summary.csv",
    "results/stage3/spaced_pattern_sanity/spaced_pattern_sanity_best_four_position.csv",
    "results/stage3/spaced_pattern_sanity/spaced_pattern_sanity_run.json",
    "results/stage3/spaced_pattern_sanity/spaced_pattern_sanity_summary.md",
    # Audit outputs.
    "results/audits/final_provenance/final_provenance_audit.md",
    "results/audits/final_provenance/table_provenance_audit.csv",
    "results/audits/final_provenance/stage_result_ledger.csv",
    "results/audits/final_provenance/manuscript_pattern_support_audit.csv",
    "results/audits/final_provenance/final_result_script_map.csv",
    "results/audits/result_inventory/final_result_source_analysis.md",
    "results/audits/result_inventory/result_directory_inventory.csv",
    "results/audits/result_inventory/run_json_configuration_inventory.csv",
    "results/audits/result_inventory/csv_schema_inventory.csv",
    "results/audits/result_inventory/parameter_grid_comparison.csv",
]

DIR_ALLOWLIST = [
    "src",
    "tests",
    "data/toy_reads",
]

EXCLUDE_PATTERNS = [
    "__pycache__",
    "*.pyc",
    ".DS_Store",
    "Thumbs.db",
    "*.part",
    "*.sam",
    "*.fq",
    "*.fastq",
    "*.fq.gz",
    "*.fastq.gz",
    "run.log",
    "run.err",
    "*.err.log",
    "*.log",
    "run_stdout.log",
    "run_stderr.log",
    "rendered_*",
    "latex_build*",
    "*.docx_text_check.txt",
    "*.tiff",
]

FORBIDDEN_RELEASE_PATH_PATTERNS = [
    "results/runs/*",
    "results/stage2/parameter_sensitivity/*",
    "results/stage2/representation_grid/stage2_derived_reads.csv",
    "results/stage2/attention_breakpoint/attention_breakpoint_reads.csv",
    "results/stage2/arg_snp_boundary/arg_snp_reads.csv",
    "results/stage3/art_illumina/art_paired_reads.csv",
    "results/stage3/art_illumina/fastq/*",
    "results/stage3/compact_baselines/stage3_compact_baseline_reads.csv",
    "results/stage3/cami_probe_expanded/cami_probe_reads.csv",
    "results/stage3/cami_probe/*",
    "data/stage3/cami/remote_prefix_cache/*",
    "data/stage3/cami/30_genomes.tar.part",
    "manuscript/tables/stage2_table_parameter_*",
    "manuscript/tables/table_parameter_sensitivity_*",
]


def as_posix(path: Path) -> str:
    return path.as_posix()


def excluded(rel: Path) -> bool:
    rel_posix = as_posix(rel)
    for pattern in EXCLUDE_PATTERNS:
        if fnmatch.fnmatch(rel.name, pattern) or fnmatch.fnmatch(rel_posix, pattern):
            return True
    return False


def copy_file(rel: str, dest_root: Path, copied: list[str], missing: list[str]) -> None:
    rel_path = Path(rel)
    src = PROJECT_ROOT / rel_path
    if not src.exists() or src.is_dir():
        missing.append(as_posix(rel_path))
        return
    if excluded(rel_path):
        return
    dst = dest_root / rel_path
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
    copied.append(as_posix(rel_path))


def copy_dir(rel: str, dest_root: Path, copied: list[str], missing: list[str]) -> None:
    src_root = PROJECT_ROOT / rel
    if not src_root.exists():
        missing.append(rel)
        return
    for src in src_root.rglob("*"):
        if src.is_dir():
            continue
        rel_path = src.relative_to(PROJECT_ROOT)
        if excluded(rel_path):
            continue
        dst = dest_root / rel_path
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        copied.append(as_posix(rel_path))


def write_text_files(dest_root: Path, copied: list[str], missing: list[str]) -> None:
    readme = dest_root / "README.md"
    readme.write_text(
        "# Ultra-short DNA Read Representation Diagnostics, Clean Release\n\n"
        "This branch is a clean release snapshot for the final manuscript. It contains the scripts, lightweight input data, "
        "summary results, figures, manuscript tables, final manuscript files and audit reports used by the submitted stage-3 manuscript.\n\n"
        "## Scientific Scope\n\n"
        "The project is a representation-diagnostics study, not a clinical diagnostic validation. The final claim is deliberately bounded: "
        "canonical k-mer, alignment and database evidence remain necessary for exact identity and functional calls, while compact biochemical and position-aware property summaries supply perturbation-stable auxiliary evidence. "
        "Full position matrices are retained only as lightweight upper-bound diagnostics, and CSP is retained as a spaced-seed boundary control.\n\n"
        "## What Is Included\n\n"
        "- Core source code under `src/`.\n"
        "- Final experiment and manuscript scripts under `scripts/`.\n"
        "- Lightweight toy data, WGS-slice manifests/reads and the CAMI_TOY_low labelled subset under `data/`.\n"
        "- Final summary result CSV/JSON/Markdown files under `results/`.\n"
        "- Final manuscript files, selected final tables and selected final figures under `manuscript/`.\n"
        "- The one-stop provenance map under `docs/final_release_provenance_map.md` and audit reports under `results/audits/`.\n\n"
        "## What Is Excluded\n\n"
        "Historical `results/runs` outputs, smoke runs, old parameter-sensitivity result tables, render intermediates, local virtual environments, "
        "download fragments, full CAMI archives, ART FASTQ/SAM outputs and large paired-read intermediates are excluded. The final manuscript uses "
        "`results/stage3/spaced_pattern_sanity` for seed-layout claims. Older parameter grids are documented only in audit reports.\n\n"
        "## Main Reproduction Path\n\n"
        "```powershell\n"
        ".\\.venv\\Scripts\\python.exe scripts\\run_stage2_representation_grid.py\n"
        ".\\.venv\\Scripts\\python.exe scripts\\run_stage2_csp_ablation.py\n"
        ".\\.venv\\Scripts\\python.exe scripts\\run_stage2_attention_breakpoint.py\n"
        ".\\.venv\\Scripts\\python.exe scripts\\run_stage2_arg_snp_boundary.py\n"
        ".\\.venv\\Scripts\\python.exe scripts\\run_stage3_compact_baselines.py\n"
        ".\\.venv\\Scripts\\python.exe scripts\\run_stage3_art_generate_and_evaluate.py\n"
        ".\\.venv\\Scripts\\python.exe scripts\\summarize_stage3_art_quality.py\n"
        ".\\.venv\\Scripts\\python.exe scripts\\run_stage3_cami_probe.py\n"
        ".\\.venv\\Scripts\\python.exe scripts\\run_position_property_controlled_tasks.py --output-dir results/stage3/fullmatrix_property_contribution_controlled --representations ckmer4_property_multiscale_mean_l2,one_hot,property_channels,base_property,rope_onehot,rope_property,ckmer5_count_l2,kmer_property --lengths 69,100 --conditions clean,N_3pct\n"
        ".\\.venv\\Scripts\\python.exe scripts\\run_stage3_art_validation.py --reads-csv results/stage3/art_illumina/art_paired_reads.csv --output-dir results/stage3/art_fullmatrix_property_contribution --lengths 69,100 --representations ckmer5_count_l2,ckmer4_property_multiscale_mean_l2,one_hot,property_channels,base_property,rope_onehot,rope_property,kmer_property --max-retrieval-pairs 100\n"
        ".\\.venv\\Scripts\\python.exe scripts\\run_stage3_cami_probe.py --reads-csv data/stage3/cami/cami_toy_low_subset_smoke.csv --output-dir results/stage3/cami_fullmatrix_property_contribution --lengths 69,100 --conditions clean,N_3pct --representations ckmer5_count_l2,ckmer4_property_multiscale_mean_l2,one_hot,property_channels,base_property,rope_onehot,rope_property,kmer_property --target-label tax_552396 --max-per-class 30\n"
        ".\\.venv\\Scripts\\python.exe scripts\\run_spaced_pattern_sanity.py --skip-readout --max-paired-reads 240 --max-clean-per-length 480\n"
        ".\\.venv\\Scripts\\python.exe scripts\\generate_stage3_bootstrap_ci.py\n"
        ".\\.venv\\Scripts\\python.exe scripts\\generate_fullmatrix_property_contribution_ci.py\n"
        ".\\.venv\\Scripts\\python.exe scripts\\generate_stage3_manuscript_assets_v2.py\n"
        ".\\.venv\\Scripts\\python.exe scripts\\audit_result_inventory.py\n"
        ".\\.venv\\Scripts\\python.exe scripts\\audit_final_provenance.py\n"
        ".\\.venv\\Scripts\\python.exe scripts\\finalize_stage3_manuscript_v5.py\n"
        "```\n\n"
        "The final files are `manuscript/final_manuscript.md` and `manuscript/final_manuscript.docx`.\n",
        encoding="utf-8",
    )
    copied.append("README.md")

    manifest = dest_root / "RELEASE_MANIFEST.md"
    manifest.write_text(
        "# Release Manifest\n\n"
        "This manifest was generated by `scripts/prepare_release_repository.py`. The copy is intentionally allowlisted.\n\n"
        "## Included Files\n\n"
        + "\n".join(f"- `{item}`" for item in sorted(copied))
        + "\n\n## Missing Optional Files\n\n"
        + ("\n".join(f"- `{item}`" for item in sorted(missing)) if missing else "None")
        + "\n\n## Excluded By Policy\n\n"
        "- Historical `results/runs` directories.\n"
        "- Superseded `results/stage2/parameter_sensitivity` and later `results/runs/parameter_sensitivity` result tables.\n"
        "- ART FASTQ/SAM and paired-read intermediates.\n"
        "- Full CAMI archives and range-download fragments.\n"
        "- Rendered QA folders, local environments and historical manuscript drafts.\n",
        encoding="utf-8",
    )
    copied.append("RELEASE_MANIFEST.md")

    (dest_root / ".gitignore").write_text(
        ".venv/\n__pycache__/\n*.pyc\n*.part\n*.sam\n*.fq\n*.fastq\n*.fq.gz\n*.fastq.gz\n"
        "results/runs/\nresults/stage2/parameter_sensitivity/\nresults/stage3/art_illumina/fastq/\n"
        "results/stage3/art_illumina/art_paired_reads.csv\nresults/stage3/compact_baselines/stage3_compact_baseline_reads.csv\n"
        "results/stage3/cami_probe_expanded/cami_probe_reads.csv\nresults/stage3/cami_fullmatrix_property_contribution/cami_probe_reads.csv\ndata/stage3/cami/remote_prefix_cache/\n",
        encoding="utf-8",
    )
    copied.append(".gitignore")


def validate_release(dest_root: Path) -> list[str]:
    violations: list[str] = []
    for path in dest_root.rglob("*"):
        if path.is_dir():
            continue
        rel = path.relative_to(dest_root).as_posix()
        for pattern in FORBIDDEN_RELEASE_PATH_PATTERNS:
            if fnmatch.fnmatch(rel, pattern):
                violations.append(rel)
                break
    return sorted(set(violations))


def resolve_output(path: Path) -> Path:
    if not path.exists():
        return path
    suffix = datetime.now().strftime("%Y%m%d_%H%M%S")
    return path.with_name(f"{path.name}_{suffix}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Prepare a clean, allowlisted release repository copy.")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUTPUT, help="Output directory. Existing directories are not overwritten.")
    args = parser.parse_args()
    dest_root = resolve_output(args.out)
    dest_root.mkdir(parents=True, exist_ok=False)
    copied: list[str] = []
    missing: list[str] = []

    for rel in DIR_ALLOWLIST:
        copy_dir(rel, dest_root, copied, missing)
    for rel in FILE_ALLOWLIST:
        copy_file(rel, dest_root, copied, missing)
    for script_name in SCRIPT_ALLOWLIST:
        copy_file(f"scripts/{script_name}", dest_root, copied, missing)
    for name in FINAL_TABLE_NAMES:
        copy_file(f"manuscript/tables/{name}.md", dest_root, copied, missing)
        if name.startswith("stage2_"):
            copy_file(f"results/stage2/publication_assets/tables/{name}.csv", dest_root, copied, missing)
            copy_file(f"results/stage2/publication_assets/tables/{name}.md", dest_root, copied, missing)
    for rel in FIGURE_FILES:
        copy_file(rel, dest_root, copied, missing)
    for rel in SELECTED_RESULT_FILES:
        copy_file(rel, dest_root, copied, missing)

    write_text_files(dest_root, copied, missing)
    violations = validate_release(dest_root)
    if violations:
        raise SystemExit("Forbidden release files copied:\n" + "\n".join(violations))
    print(dest_root)
    print(f"Copied {len(copied)} files")
    if missing:
        print(f"Missing optional files: {len(missing)}")


if __name__ == "__main__":
    main()


