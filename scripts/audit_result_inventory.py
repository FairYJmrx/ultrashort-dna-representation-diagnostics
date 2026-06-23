from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]

KEYS_OF_INTEREST = [
    "input",
    "reads_csv",
    "lengths",
    "classification_lengths",
    "patterns",
    "k_values",
    "conditions",
    "representations",
    "readout_representations",
    "max_paired_reads",
    "max_samples_per_group",
    "max_clean_per_length",
    "seed",
    "skip_readout",
    "n_reads",
    "n_rows",
    "n_stage2_reads",
    "n_stability_rows",
    "n_classification_rows",
    "n_readout_rows",
]

CONTAINER_RULES = {
    "results": ("results_container", "container_directory", "container_only", "Top-level results container; evidence classification is assigned to child result directories."),
    "results/stage2": ("stage2_container", "container_directory", "container_only", "Top-level stage-2 container; evidence classification is assigned to child result directories."),
    "results/stage3": ("stage3_container", "container_directory", "container_only", "Top-level stage-3 container; evidence classification is assigned to child result directories."),
    "results/audits": ("audit_container", "container_directory", "container_only", "Top-level audit container; evidence classification is assigned to child audit directories."),
    "results/runs": ("stage1_exploratory_runs", "historical_exploration", "exclude_bulk", "Stage-1 exploratory run container; child directories are historical development outputs."),
    "results/figures": ("legacy_publication_assets", "legacy_or_unused_figures", "exclude_until_explicitly_used", "Legacy top-level figure directory; final figures are selected from manuscript/figures or results/stage3/figures."),
}

STAGE_RULES = [
    ("results/runs/parameter_sensitivity", "stage1_later_parameter_grid", "real_later_development_grid", "exclude_final_evidence", "Later results/runs parameter grid with fewer spaced patterns; not used for final seed-layout claims."),
    ("results/runs", "stage1_exploratory_runs", "historical_exploration", "exclude_bulk", "Smoke, first-wave, order/position, early WGS-slice and exploratory runs."),
    ("results/stage2/parameter_sensitivity", "stage2_parameter_sensitivity_old_grid", "real_historical_grid_deprecated", "exclude_final_evidence", "Old stage-2 parameter grid; source of 0-2-5-7 and 0-3-5-8 tables, now superseded for final seed-layout claims."),
    ("results/stage2/representation_grid_smoke", "stage2_smoke", "smoke_test", "exclude", "Stage-2 smoke output."),
    ("results/stage2/neural_compatibility_smoke", "stage2_smoke", "smoke_test", "exclude", "Stage-2 neural smoke output."),
    ("results/stage2/representation_grid", "stage2_main_mechanism_grid", "final_evidence_source", "include_selected", "Main WGS-slice representation stability/readout grid."),
    ("results/stage2/csp_ablation", "stage2_main_mechanism_grid", "final_evidence_source", "include_selected", "CSP component ablation evidence."),
    ("results/stage2/attention_breakpoint", "stage2_main_mechanism_grid", "final_evidence_source", "include_selected", "Position/context breakpoint diagnostic evidence."),
    ("results/stage2/arg_snp_boundary", "stage2_main_mechanism_grid", "final_evidence_source", "include_selected", "ARG/SNP boundary stress-test evidence."),
    ("results/stage2/neural_compatibility", "stage2_neural_compatibility_historical", "historical_deprecated", "exclude_final_evidence", "Old deterministic neural probe diagnostic; excluded from revised final evidence because no third neural baseline is added."),
    ("results/stage2/publication_assets", "stage2_publication_assets", "derived_final_tables_figures", "include_selected_tables_figures", "Generated stage-2 manuscript tables and figures; parameter-sensitivity tables are deprecated."),
    ("results/stage3/compact_baselines_smoke", "stage3_smoke", "smoke_test", "exclude", "Stage-3 compact-baseline smoke output."),
    ("results/stage3/art_illumina_smoke", "stage3_smoke", "smoke_test", "exclude", "ART smoke output."),
    ("results/stage3/art_illumina_smoke2", "stage3_smoke", "smoke_test", "exclude", "ART smoke output."),
    ("results/stage3/cami_probe_expanded", "stage3_external_validation", "final_evidence_source", "include_summary_exclude_reads", "Expanded CAMI_TOY_low readout probe used in final manuscript."),
    ("results/stage3/cami_probe", "stage3_deprecated_validation", "older_validation_run", "exclude_final_evidence", "Older CAMI probe superseded by cami_probe_expanded."),
    ("results/stage3/compact_baselines", "stage3_external_validation", "final_evidence_source", "include_summary_exclude_reads", "Compactness controls and stability/readout external validation."),
    ("results/stage3/art_illumina", "stage3_external_validation", "final_evidence_source", "include_summary_exclude_fastq_reads", "ART Illumina simulator validation."),
    ("results/stage3/art_quality_stratified", "stage3_external_validation", "final_evidence_source", "include_selected", "ART quality-stratified summary."),
    ("results/stage3/bootstrap_ci", "stage3_external_validation", "final_evidence_source", "include", "Analysis-cell bootstrap CI tables used in final manuscript."),
    ("results/stage3/figures", "stage3_publication_assets", "derived_final_figures", "include_selected", "Stage-3 generated figures."),
    ("results/stage3/position_property_ablation", "stage3_position_property_revision", "final_evidence_source", "include_summary_exclude_reads", "Compact CK4/CK5 plus biochemical and position-aware property ablation."),
    ("results/stage3/art_ck4p_position_ablation", "stage3_position_property_revision", "final_evidence_source", "include_selected", "ART compact CK4/CK5 plus position-aware property validation."),
    ("results/stage3/cami_ck4p_position_ablation_fast", "stage3_position_property_revision", "final_evidence_source", "include_summary_exclude_reads", "CAMI compact CK4/CK5 plus position-aware property readout probe."),
    ("results/stage3/fullmatrix_property_contribution_controlled", "stage3_fullmatrix_property_contribution", "final_evidence_source", "include", "Controlled P-versus-non-P full-matrix ablation."),
    ("results/stage3/art_fullmatrix_property_contribution", "stage3_fullmatrix_property_contribution", "final_evidence_source", "include_selected", "ART P-versus-non-P full-matrix stability ablation."),
    ("results/stage3/cami_fullmatrix_property_contribution", "stage3_fullmatrix_property_contribution", "final_evidence_source", "include_summary_exclude_reads", "CAMI P-versus-non-P full-matrix readout ablation."),
    ("results/stage3/fullmatrix_property_contribution_ci", "stage3_fullmatrix_property_contribution", "final_evidence_source", "include", "Bootstrap CI tables for full-matrix property contribution."),
    ("results/stage3/spaced_pattern_sanity", "stage3_spaced_pattern_sanity", "final_evidence_source", "include", "Focused seed-layout stability and cardinality sanity check."),
    ("results/stage3/downloads", "stage3_download_cache", "cache", "exclude", "External download/cache metadata and fragments."),
    ("results/audits", "audit_outputs", "audit_evidence", "include", "Result inventory and manuscript provenance audit outputs."),
    ("results/stage3", "stage3_metadata", "metadata", "include_selected", "Stage-3 top-level manifests and subset metadata."),
]

FINAL_RESULT_DIRS = {
    "results/stage2/representation_grid",
    "results/stage2/csp_ablation",
    "results/stage2/attention_breakpoint",
    "results/stage2/arg_snp_boundary",
    "results/stage2/publication_assets",
    "results/stage3/compact_baselines",
    "results/stage3/art_illumina",
    "results/stage3/art_quality_stratified",
    "results/stage3/cami_probe_expanded",
    "results/stage3/bootstrap_ci",
    "results/stage3/position_property_ablation",
    "results/stage3/art_ck4p_position_ablation",
    "results/stage3/cami_ck4p_position_ablation_fast",
    "results/stage3/fullmatrix_property_contribution_controlled",
    "results/stage3/art_fullmatrix_property_contribution",
    "results/stage3/cami_fullmatrix_property_contribution",
    "results/stage3/fullmatrix_property_contribution_ci",
    "results/stage3/spaced_pattern_sanity",
    "results/audits/final_provenance",
    "results/audits/result_inventory",
}

DEPRECATED_TABLES = [
    "manuscript/tables/stage2_table_parameter_readout_best.md",
    "manuscript/tables/stage2_table_parameter_stability_best.md",
    "manuscript/tables/table_parameter_sensitivity_best_classification.md",
    "manuscript/tables/table_parameter_sensitivity_best_stability.md",
    "manuscript/tables/stage2_table_neural_compatibility_aggregate.md",
]


def rel(path: Path) -> str:
    return path.relative_to(PROJECT_ROOT).as_posix()


def compact(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, (str, int, float, bool)):
        return str(value)
    if isinstance(value, list):
        return ",".join(compact(item) for item in value)
    if isinstance(value, dict):
        return json.dumps(value, ensure_ascii=False, sort_keys=True)
    return str(value)


def find_key(obj: Any, key: str) -> Any:
    if isinstance(obj, dict):
        if key in obj:
            return obj[key]
        for value in obj.values():
            found = find_key(value, key)
            if found is not None:
                return found
    elif isinstance(obj, list):
        for value in obj:
            found = find_key(value, key)
            if found is not None:
                return found
    return None


def classify_result_dir(path: Path) -> dict[str, str]:
    rel_dir = rel(path)
    if rel_dir in CONTAINER_RULES:
        category, status, policy, notes = CONTAINER_RULES[rel_dir]
        return {
            "stage_category": category,
            "evidence_status": status,
            "clean_release_policy": policy,
            "classification_notes": notes,
        }
    for prefix, category, status, policy, notes in STAGE_RULES:
        if rel_dir == prefix or rel_dir.startswith(prefix + "/"):
            return {
                "stage_category": category,
                "evidence_status": status,
                "clean_release_policy": policy,
                "classification_notes": notes,
            }
    return {
        "stage_category": "uncategorized_result",
        "evidence_status": "needs_manual_review",
        "clean_release_policy": "exclude_until_reviewed",
        "classification_notes": "No explicit stage rule matched this result directory.",
    }


def directory_inventory(results_root: Path) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for directory in sorted([p for p in results_root.rglob("*") if p.is_dir()] + [results_root]):
        files = [p for p in directory.iterdir() if p.is_file()]
        csvs = [p for p in files if p.suffix.lower() == ".csv"]
        jsons = [p for p in files if p.suffix.lower() == ".json"]
        mds = [p for p in files if p.suffix.lower() == ".md"]
        run_jsons = [p.name for p in jsons if "run" in p.stem or p.name.endswith("results.json")]
        info = classify_result_dir(directory)
        rel_dir = rel(directory)
        rows.append(
            {
                "dir": rel_dir,
                "csv_files": len(csvs),
                "json_files": len(jsons),
                "md_files": len(mds),
                "total_csv_bytes": sum(p.stat().st_size for p in csvs),
                "run_jsons": ";".join(run_jsons),
                "csv_names": ";".join(p.name for p in csvs),
                "is_final_result_dir": rel_dir in FINAL_RESULT_DIRS,
                **info,
            }
        )
    return pd.DataFrame(rows)


def json_inventory(results_root: Path) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for path in sorted(results_root.rglob("*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:
            rows.append({"json": rel(path), "json_parse_error": str(exc)})
            continue
        row: dict[str, object] = {"json": rel(path)}
        row.update(classify_result_dir(path.parent))
        for key in KEYS_OF_INTEREST:
            row[key] = compact(find_key(data, key))
        rows.append(row)
    return pd.DataFrame(rows)


def csv_schema_inventory(results_root: Path) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for path in sorted(results_root.rglob("*.csv")):
        try:
            df = pd.read_csv(path, nrows=5)
            full_rows = sum(1 for _ in path.open("r", encoding="utf-8", errors="ignore")) - 1
            columns = list(df.columns)
            parse_error = ""
        except Exception as exc:
            full_rows = None
            columns = []
            parse_error = str(exc)
        rows.append(
            {
                "csv": rel(path),
                "rows": full_rows,
                "columns": ";".join(columns),
                "bytes": path.stat().st_size,
                "parse_error": parse_error,
                **classify_result_dir(path.parent),
            }
        )
    return pd.DataFrame(rows)


def parameter_grid_summary(project_root: Path) -> pd.DataFrame:
    rows = []
    for label, folder in [
        ("stage2_parameter_sensitivity_old_grid", project_root / "results" / "stage2" / "parameter_sensitivity"),
        ("runs_parameter_sensitivity_later_grid", project_root / "results" / "runs" / "parameter_sensitivity"),
        ("stage3_spaced_pattern_sanity_final", project_root / "results" / "stage3" / "spaced_pattern_sanity"),
    ]:
        run_json = next(folder.glob("*run.json"), None) if folder.exists() else None
        stability = folder / ("spaced_pattern_sanity_stability.csv" if "spaced" in label else "parameter_stability_metrics.csv")
        readout = folder / ("spaced_pattern_sanity_readout.csv" if "spaced" in label else "parameter_classification_probes.csv")
        patterns = ""
        lengths = ""
        k_values = ""
        conditions = ""
        if stability.exists():
            sdf = pd.read_csv(stability)
            if "pattern" in sdf.columns:
                patterns = ",".join(sorted(sdf["pattern"].dropna().astype(str).unique()))
            for col in ["length", "source_length"]:
                if col in sdf.columns:
                    lengths = ",".join(str(int(x)) for x in sorted(sdf[col].dropna().astype(int).unique()))
                    break
            if "k" in sdf.columns:
                k_values = ",".join(str(int(x)) for x in sorted(sdf["k"].dropna().astype(int).unique()))
            if "condition" in sdf.columns:
                conditions = ",".join(sorted(sdf["condition"].dropna().astype(str).unique()))
        config = {}
        if run_json and run_json.exists():
            try:
                config = json.loads(run_json.read_text(encoding="utf-8"))
            except Exception:
                config = {}
        rows.append(
            {
                "grid": label,
                "folder": rel(folder),
                "run_json": rel(run_json) if run_json else "",
                "patterns_from_stability_csv": patterns,
                "lengths_from_stability_csv": lengths,
                "k_values_from_stability_csv": k_values,
                "conditions_from_stability_csv": conditions,
                "n_stability_rows": int(len(pd.read_csv(stability))) if stability.exists() else 0,
                "readout_csv_exists": readout.exists(),
                "n_readout_rows": int(len(pd.read_csv(readout))) if readout.exists() else 0,
                "patterns_from_run_json": compact(config.get("patterns")),
                "lengths_from_run_json": compact(config.get("lengths")),
                "classification_lengths_from_run_json": compact(config.get("classification_lengths")),
                "k_values_from_run_json": compact(config.get("k_values")),
                "status_for_final_manuscript": "final_seed_layout_sanity" if "stage3" in label else "deprecated_for_final_seed_claims",
            }
        )
    return pd.DataFrame(rows)


def write_analysis_report(out_dir: Path, dir_df: pd.DataFrame, json_df: pd.DataFrame, schema_df: pd.DataFrame, param_df: pd.DataFrame) -> None:
    final_dirs = dir_df[dir_df["is_final_result_dir"].astype(bool)][
        ["dir", "stage_category", "evidence_status", "clean_release_policy", "csv_files", "json_files", "md_files", "total_csv_bytes"]
    ]
    stage_counts = dir_df.groupby(["stage_category", "evidence_status", "clean_release_policy"], as_index=False).agg(
        directories=("dir", "count"), csv_files=("csv_files", "sum"), csv_bytes=("total_csv_bytes", "sum")
    )
    deprecated_existing = [path for path in DEPRECATED_TABLES if (PROJECT_ROOT / path).exists()]
    unsupported_note = "All known final manuscript pattern tokens are checked separately by audit_final_provenance.py."
    lines = [
        "# Final Result Source Analysis",
        "",
        "This audit is a project-level result inventory. It separates final evidence, historical exploratory output, superseded parameter grids, smoke runs and generated audit outputs before the final manuscript is regenerated.",
        "",
        "## Main conclusion",
        "",
        "The 0-2-5-7 and 0-3-5-8 patterns were not fabricated. They came from the real stage-2 parameter-sensitivity grid, which scanned five four-position layouts. The later results/runs parameter grid scanned only three four-position layouts, so mixing those two grids in the manuscript would create a provenance problem. The final manuscript should therefore use the focused stage-3 spaced-pattern sanity run for seed-layout statements and mark both older parameter tables as deprecated for final claims.",
        "",
        "Stage 1 corresponds to results/runs. Those outputs are historical exploration and early diagnostics, not the final evidence base. Stage 2 contains the main controlled mechanism grid, except its old parameter-sensitivity directory. Stage 3 contains external validation, bootstrap CIs and the final seed-layout sanity check.",
        "",
        "## Stage/category counts",
        "",
        stage_counts.to_markdown(index=False),
        "",
        "## Parameter-grid comparison",
        "",
        param_df.to_markdown(index=False),
        "",
        "## Final evidence directories selected for clean release",
        "",
        final_dirs.to_markdown(index=False),
        "",
        "## Deprecated result tables still present in the working project",
        "",
        "\n".join(f"- `{path}`" for path in deprecated_existing) if deprecated_existing else "No deprecated parameter tables were found in the working manuscript table directory.",
        "",
        "## Audit interpretation rules",
        "",
        "- Final manuscript tables must match their source CSVs through the manuscript table formatting path, not through ad hoc visual copying.",
        "- The clean release should include final scripts, source summary CSVs, generated final tables, figures, manuscript builders and audit reports.",
        "- The clean release should exclude bulk historical results/runs, smoke outputs, old parameter-sensitivity tables, full FASTQ/SAM files and large reproducible read intermediates.",
        f"- {unsupported_note}",
        "",
        "## Inventory files generated",
        "",
        "- `result_directory_inventory.csv`: directory-level counts, stage categories and clean-release policy.",
        "- `run_json_configuration_inventory.csv`: JSON/run-configuration fields extracted from result files.",
        "- `csv_schema_inventory.csv`: CSV row counts, columns and stage categories.",
        "- `parameter_grid_comparison.csv`: side-by-side comparison of old stage-2, later results/runs and final stage-3 seed-layout grids.",
        "",
    ]
    (out_dir / "final_result_source_analysis.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Inventory result directories and classify final evidence versus historical outputs.")
    parser.add_argument("--output-dir", default=str(PROJECT_ROOT / "results" / "audits" / "result_inventory"))
    args = parser.parse_args()
    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    results_root = PROJECT_ROOT / "results"
    dir_df = directory_inventory(results_root)
    json_df = json_inventory(results_root)
    schema_df = csv_schema_inventory(results_root)
    param_df = parameter_grid_summary(PROJECT_ROOT)

    dir_df.to_csv(out_dir / "result_directory_inventory.csv", index=False, encoding="utf-8-sig")
    json_df.to_csv(out_dir / "run_json_configuration_inventory.csv", index=False, encoding="utf-8-sig")
    schema_df.to_csv(out_dir / "csv_schema_inventory.csv", index=False, encoding="utf-8-sig")
    param_df.to_csv(out_dir / "parameter_grid_comparison.csv", index=False, encoding="utf-8-sig")
    write_analysis_report(out_dir, dir_df, json_df, schema_df, param_df)
    print(f"Wrote result inventory audit to {out_dir}")


if __name__ == "__main__":
    main()


