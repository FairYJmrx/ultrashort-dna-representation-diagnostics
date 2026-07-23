from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import pandas as pd

def _find_project_root(start: Path) -> Path:
    for candidate in [start.parent, *start.parents]:
        if (candidate / "methods").is_dir() and (candidate / "configs").is_dir():
            return candidate
    raise RuntimeError("Could not locate the release repository root.")


PROJECT_ROOT = _find_project_root(Path(__file__).resolve())

FINAL_TABLE_SPECS = {
    "stage2_table_hospital_69_75_focus": "results/stage2/publication_assets/tables/stage2_table_hospital_69_75_focus.csv",
    "stage2_table_stability_gain_summary": "results/stage2/publication_assets/tables/stage2_table_stability_gain_summary.csv",
    "stage2_table_csp_component_singletons": "results/stage2/publication_assets/tables/stage2_table_csp_component_singletons.csv",
    "stage2_table_csp_full_ablation": "results/stage2/publication_assets/tables/stage2_table_csp_full_ablation.csv",
    "stage2_table_readout_aggregate": "results/stage2/publication_assets/tables/stage2_table_readout_aggregate.csv",
    "stage2_table_attention_change_points": "results/stage2/publication_assets/tables/stage2_table_attention_change_points.csv",
    "stage2_table_arg_snp_best_stability": "results/stage2/publication_assets/tables/stage2_table_arg_snp_best_stability.csv",
    "stage2_table_arg_snp_readout_aggregate": "results/stage2/publication_assets/tables/stage2_table_arg_snp_readout_aggregate.csv",
    "stage3_table_compact_bootstrap_ci": "results/stage3/bootstrap_ci/stage3_compact_bootstrap_ci.csv",
    "stage3_table_art_bootstrap_ci": "results/stage3/bootstrap_ci/stage3_art_bootstrap_ci.csv",
    "stage3_table_art_quality_bootstrap_ci": "results/stage3/bootstrap_ci/stage3_art_quality_bootstrap_ci.csv",
    "stage3_table_cami_macro_f1_bootstrap_ci": "results/stage3/bootstrap_ci/stage3_cami_macro_f1_bootstrap_ci.csv",
    "stage3_table_fullmatrix_property_controlled_ci": "results/stage3/fullmatrix_property_contribution_ci/fullmatrix_property_controlled_ci.csv",
    "stage3_table_fullmatrix_property_controlled_delta_ci": "results/stage3/fullmatrix_property_contribution_ci/fullmatrix_property_controlled_delta_ci.csv",
    "stage3_table_fullmatrix_property_art_ci": "results/stage3/fullmatrix_property_contribution_ci/fullmatrix_property_art_ci.csv",
    "stage3_table_fullmatrix_property_art_delta_ci": "results/stage3/fullmatrix_property_contribution_ci/fullmatrix_property_art_delta_ci.csv",
    "stage3_table_fullmatrix_property_cami_ci": "results/stage3/fullmatrix_property_contribution_ci/fullmatrix_property_cami_ci.csv",
    "stage3_table_fullmatrix_property_cami_delta_ci": "results/stage3/fullmatrix_property_contribution_ci/fullmatrix_property_cami_delta_ci.csv",
    "table_spaced_pattern_sanity_cardinality": "results/stage3/spaced_pattern_sanity/spaced_pattern_sanity_cardinality_summary.csv",
    "table_spaced_pattern_sanity_best_four_position": "results/stage3/spaced_pattern_sanity/spaced_pattern_sanity_best_four_position.csv",
}

STATIC_TABLES = {
    "stage3_table_representation_scheme_summary": "method/representation taxonomy table generated from manuscript asset script",
    "table_representation_taxonomy": "legacy representation taxonomy table; not used by final stage-3 manuscript",
}

DEPRECATED_RESULT_TABLES = {
    "stage2_table_parameter_readout_best": "real stage-2 parameter-sensitivity readout table, but replaced in final manuscript by stage3/spaced_pattern_sanity to avoid mixed parameter-grid provenance",
    "stage2_table_parameter_stability_best": "real stage-2 parameter-sensitivity stability table, but not used by final manuscript after provenance cleanup",
    "table_parameter_sensitivity_best_classification": "later results/runs parameter-sensitivity table; not used by final manuscript after provenance cleanup",
    "table_parameter_sensitivity_best_stability": "later results/runs parameter-sensitivity table; not used by final manuscript after provenance cleanup",
    "stage2_table_neural_compatibility_aggregate": "old deterministic neural compatibility table; not used by the revised final manuscript because no third neural baseline is added",
}

STAGE_LEDGER = [
    {
        "stage": "stage1_exploratory_runs",
        "paths": "results/runs/* except explicit uncertainty helper",
        "status": "historical exploration",
        "final_release_policy": "exclude as bulk historical runs; keep only scripts if needed for provenance",
        "notes": "Includes smoke, first-wave toy, early WGS-slice and exploratory parameter grids. These runs informed development but are not the final evidence source.",
    },
    {
        "stage": "stage2_main_mechanism_grid",
        "paths": "results/stage2/representation_grid, csp_ablation, attention_breakpoint, arg_snp_boundary, publication_assets",
        "status": "final evidence source",
        "final_release_policy": "include selected raw summary CSVs, run json files, generated figures and publication tables",
        "notes": "Main controlled WGS-slice mechanism results used by the final manuscript. The old deterministic neural-compatibility run is not part of the revised final evidence set.",
    },
    {
        "stage": "stage2_neural_compatibility_historical",
        "paths": "results/stage2/neural_compatibility",
        "status": "historical/deprecated for final manuscript",
        "final_release_policy": "exclude from clean final evidence bundle unless archived separately as exploratory provenance",
        "notes": "Retained only as an old diagnostic. The revised manuscript does not add or rely on a third neural baseline family.",
    },
    {
        "stage": "stage2_parameter_sensitivity_old_grid",
        "paths": "results/stage2/parameter_sensitivity",
        "status": "real historical stage2 experiment, deprecated for final seed table",
        "final_release_policy": "exclude from clean final evidence bundle unless separately archived as historical provenance",
        "notes": "Contains patterns 0-2-5-7 and 0-3-5-8. Valid as old stage2 run, but superseded by stage3/spaced_pattern_sanity for final manuscript.",
    },
    {
        "stage": "runs_parameter_sensitivity_later_grid",
        "paths": "results/runs/parameter_sensitivity",
        "status": "real later parameter grid, deprecated for final seed table",
        "final_release_policy": "exclude from clean final evidence bundle to avoid mixed grid claims",
        "notes": "Has six read lengths but only three spaced patterns. It is not the source for the old stage2 parameter table.",
    },
    {
        "stage": "stage3_external_validation",
        "paths": "results/stage3/compact_baselines, art_illumina, art_quality_stratified, cami_probe_expanded, bootstrap_ci",
        "status": "final evidence source",
        "final_release_policy": "include compact summary/readout CSVs, ART stability summaries, CAMI readout summaries, bootstrap CI tables; exclude bulky paired-read/FASTQ/SAM intermediates",
        "notes": "External validation and uncertainty summaries used by stage3 final manuscript.",
    },
    {
        "stage": "stage3_position_property_revision",
        "paths": "results/stage3/position_property_ablation, art_ck4p_position_ablation, cami_ck4p_position_ablation_fast",
        "status": "final evidence source",
        "final_release_policy": "include summary/readout/stability CSVs and run JSON files; exclude generated read intermediates",
        "notes": "Compact CK4/CK5 plus biochemical and position-aware property ablations used by the revised manuscript.",
    },
    {
        "stage": "stage3_fullmatrix_property_contribution",
        "paths": "results/stage3/fullmatrix_property_contribution_controlled, art_fullmatrix_property_contribution, cami_fullmatrix_property_contribution, fullmatrix_property_contribution_ci",
        "status": "final evidence source for upper-bound diagnostic",
        "final_release_policy": "include lightweight controlled/ART/CAMI summaries and CI tables; exclude generated read intermediates",
        "notes": "Lightweight P-versus-non-P full-matrix ablation. It supports the position-resolution upper-bound diagnostic, not a new neural baseline.",
    },
    {
        "stage": "stage3_spaced_pattern_sanity",
        "paths": "results/stage3/spaced_pattern_sanity",
        "status": "final evidence source for seed-layout sanity statement",
        "final_release_policy": "include stability, cardinality summary, best-four-position summary, run json and markdown summary",
        "notes": "Added to resolve mixed parameter-grid provenance and support conservative default wording.",
    },
]


def read_md_table_text(text: str) -> pd.DataFrame:
    lines = [line for line in text.splitlines() if line.strip().startswith("|")]
    if len(lines) < 3:
        return pd.DataFrame()
    header = [cell.strip() for cell in lines[0].strip("|").split("|")]
    rows = [[cell.strip() for cell in line.strip("|").split("|")] for line in lines[2:]]
    return pd.DataFrame(rows, columns=header)


def read_md_table(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    return read_md_table_text(path.read_text(encoding="utf-8"))


def source_display_frame(df: pd.DataFrame) -> pd.DataFrame:
    """Recreate the markdown-facing table display used by manuscript generators."""
    display = df.copy()
    for col in display.columns:
        if pd.api.types.is_float_dtype(display[col]):
            display[col] = display[col].map(lambda value: "" if pd.isna(value) else f"{value:.3f}")
    return read_md_table_text(display.to_markdown(index=False))


def comparable_frame(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    for col in out.columns:
        out[col] = out[col].astype(str).str.strip()
        numeric = pd.to_numeric(out[col].str.replace(",", "", regex=False), errors="coerce")
        if numeric.notna().mean() >= 0.8:
            out[col] = numeric.round(3).astype(str)
            out[col] = out[col].str.replace(r"\.0$", "", regex=True)
    return out.fillna("")


def displayed_column_differences(md: pd.DataFrame, src: pd.DataFrame, abs_tolerance: float = 0.0015, rel_tolerance: float = 5e-6) -> list[str]:
    diff_cols: list[str] = []
    for col in md.columns:
        md_text = md[col].astype(str).str.strip()
        src_text = src[col].astype(str).str.strip()
        md_num = pd.to_numeric(md_text.str.replace(",", "", regex=False), errors="coerce")
        src_num = pd.to_numeric(src_text.str.replace(",", "", regex=False), errors="coerce")
        if md_num.notna().mean() >= 0.8 and src_num.notna().mean() >= 0.8:
            tolerance = abs_tolerance + rel_tolerance * src_num.abs().fillna(0.0)
            ok = (md_num - src_num).abs().le(tolerance) | (md_num.isna() & src_num.isna())
        else:
            ok = md_text.fillna("").eq(src_text.fillna(""))
        if not bool(ok.all()):
            diff_cols.append(col)
    return diff_cols


def audit_table(name: str, md_path: Path, source_rel: str | None, status_hint: str = "final") -> dict[str, object]:
    row: dict[str, object] = {"table": name, "md_path": str(md_path.relative_to(PROJECT_ROOT)), "status_hint": status_hint}
    if source_rel is None:
        row.update({"source_csv": "", "status": "static_or_deprecated", "details": STATIC_TABLES.get(name) or DEPRECATED_RESULT_TABLES.get(name, "no source spec")})
        return row
    source_path = PROJECT_ROOT / source_rel
    row["source_csv"] = source_rel
    if not md_path.exists():
        row.update({"status": "missing_md", "details": "manuscript table file missing"})
        return row
    if not source_path.exists():
        row.update({"status": "missing_source", "details": "source CSV missing"})
        return row
    md = read_md_table(md_path)
    src = pd.read_csv(source_path)
    row["md_rows"] = int(len(md))
    row["source_rows"] = int(len(src))
    missing_cols = [col for col in md.columns if col not in src.columns]
    if missing_cols:
        # Generated manuscript display tables may use renamed headers; in that case only row/source existence is audited.
        row.update({"status": "source_exists_display_renamed", "details": "MD display columns differ from source CSV: " + ", ".join(missing_cols)})
        return row
    src_display = src[md.columns].head(len(md)).copy()
    diff_cols = displayed_column_differences(md, src_display)
    if not diff_cols:
        row.update({"status": "ok", "details": "markdown values match source CSV within displayed precision tolerance"})
    else:
        row.update({"status": "value_mismatch", "details": "differences in displayed columns: " + ", ".join(diff_cols[:8])})
    return row


def manuscript_pattern_audit(final_md: Path) -> list[dict[str, object]]:
    text = final_md.read_text(encoding="utf-8") if final_md.exists() else ""
    patterns = sorted(set(re.findall(r"pattern=([0-9-]+)|`([0-9]-[0-9](?:-[0-9])*)`", text)))
    flat = sorted({a or b for a, b in patterns if (a or b)})
    source_patterns: dict[str, set[str]] = {}
    for label, rel in {
        "stage2_parameter_sensitivity": "results/stage2/parameter_sensitivity/parameter_stability_metrics.csv",
        "runs_parameter_sensitivity": "results/runs/parameter_sensitivity/parameter_stability_metrics.csv",
        "stage3_spaced_pattern_sanity": "results/stage3/spaced_pattern_sanity/spaced_pattern_sanity_stability.csv",
    }.items():
        path = PROJECT_ROOT / rel
        if path.exists():
            df = pd.read_csv(path)
            if "pattern" in df.columns:
                source_patterns[label] = set(df["pattern"].dropna().astype(str))
    rows = []
    for pattern in flat:
        support = [label for label, values in source_patterns.items() if pattern in values]
        rows.append({"pattern": pattern, "supported_by": "; ".join(support), "status": "ok" if support else "unsupported_in_known_sources"})
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description="Audit final manuscript table/result provenance and stage directory roles.")
    parser.add_argument("--output-dir", default=str(PROJECT_ROOT / "results" / "audits" / "final_provenance"))
    args = parser.parse_args()
    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    table_rows = []
    table_dir = PROJECT_ROOT / "manuscript" / "tables"
    for name, rel in FINAL_TABLE_SPECS.items():
        table_rows.append(audit_table(name, table_dir / f"{name}.md", rel, status_hint="final"))
    for name in sorted(STATIC_TABLES):
        table_rows.append(audit_table(name, table_dir / f"{name}.md", None, status_hint="static"))
    for name in sorted(DEPRECATED_RESULT_TABLES):
        table_rows.append(audit_table(name, table_dir / f"{name}.md", None, status_hint="deprecated"))

    table_df = pd.DataFrame(table_rows)
    stage_df = pd.DataFrame(STAGE_LEDGER)
    pattern_df = pd.DataFrame(manuscript_pattern_audit(PROJECT_ROOT / "manuscript" / "final_manuscript.md"))
    table_df.to_csv(out_dir / "table_provenance_audit.csv", index=False, encoding="utf-8-sig")
    stage_df.to_csv(out_dir / "stage_result_ledger.csv", index=False, encoding="utf-8-sig")
    pattern_df.to_csv(out_dir / "manuscript_pattern_support_audit.csv", index=False, encoding="utf-8-sig")

    lines = [
        "# Final Provenance Audit",
        "",
        "This audit separates final evidence sources from exploratory or superseded results. It is intended for the clean release bundle, not as a new scientific claim.",
        "",
        "## Stage/result ledger",
        "",
        stage_df.to_markdown(index=False),
        "",
        "## Table provenance audit",
        "",
        table_df.to_markdown(index=False),
        "",
        "## Pattern support audit",
        "",
        pattern_df.to_markdown(index=False) if not pattern_df.empty else "No pattern tokens found in final manuscript.",
        "",
    ]
    (out_dir / "final_provenance_audit.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote provenance audit to {out_dir}")


if __name__ == "__main__":
    main()





