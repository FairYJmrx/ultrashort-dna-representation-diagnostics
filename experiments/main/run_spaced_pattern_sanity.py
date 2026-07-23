from __future__ import annotations

import argparse
import json
import os
import random
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import sparse
from sklearn.preprocessing import normalize

def _find_project_root(start: Path) -> Path:
    for candidate in [start.parent, *start.parents]:
        if (candidate / "methods").is_dir() and (candidate / "configs").is_dir():
            return candidate
    raise RuntimeError("Could not locate the release repository root.")


PROJECT_ROOT = _find_project_root(Path(__file__).resolve())
sys.path.insert(0, str(PROJECT_ROOT))
os.environ.setdefault("LOKY_MAX_CPU_COUNT", "1")
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

from scripts.run_parameter_sensitivity import (  # noqa: E402
    classification_probe,
    cosine_diag,
    matrix_with_train_vocabulary,
    parse_int_list,
    parse_pattern,
    parse_str_list,
    row_l2_delta,
    sample_paired,
)
from experiments.main.run_stage2_representation_grid import apply_stage2_condition  # noqa: E402

CONDITION_LABELS = {
    "N_3pct": "3% N mask",
    "substitution_1pct": "1% substitution",
    "local_mismatch_6bp": "6-bp local mismatch",
}


def pattern_text(pattern: tuple[int, ...]) -> str:
    return "-".join(str(item) for item in pattern)


def pattern_role(pattern: tuple[int, ...]) -> str:
    return "primary four-position scan" if len(pattern) == 4 else "cardinality sanity check"


def derive_reads(source: pd.DataFrame, lengths: list[int], conditions: list[str], seed: int, max_clean_per_length: int) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for length in lengths:
        clean = source[(source["source_length"].astype(int) == length) & (source["condition"] == "clean")].copy()
        if clean.empty:
            continue
        if max_clean_per_length > 0 and len(clean) > max_clean_per_length:
            clean = clean.sample(n=max_clean_per_length, random_state=seed + length).reset_index(drop=True)
        for _, row in clean.iterrows():
            for condition in ["clean", *conditions]:
                rows.append(apply_stage2_condition(row, condition, seed=seed))
    out = pd.DataFrame(rows)
    out["source_length"] = out["source_length"].astype(int)
    out["length"] = out["length"].astype(int)
    return out


def paired_subsets(df: pd.DataFrame, length: int, condition: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    clean = df[(df["source_length"] == length) & (df["condition"] == "clean")].copy()
    pert = df[(df["source_length"] == length) & (df["condition"] == condition)].copy()
    common = sorted(set(clean["clean_read_id"]) & set(pert["clean_read_id"]))
    clean = clean[clean["clean_read_id"].isin(common)].sort_values("clean_read_id").reset_index(drop=True)
    pert = pert[pert["clean_read_id"].isin(common)].sort_values("clean_read_id").reset_index(drop=True)
    return clean, pert


def retrieval_top1(clean_x: sparse.spmatrix | np.ndarray, pert_x: sparse.spmatrix | np.ndarray) -> float:
    clean_norm = normalize(clean_x, norm="l2", axis=1)
    pert_norm = normalize(pert_x, norm="l2", axis=1)
    sims = pert_norm @ clean_norm.T
    if sparse.issparse(sims):
        sims = sims.toarray()
    nearest = np.asarray(sims).argmax(axis=1)
    return float(np.mean(nearest == np.arange(len(nearest))))


def stability_rows(df: pd.DataFrame, lengths: list[int], conditions: list[str], patterns: list[tuple[int, ...]], max_pairs: int, seed: int) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for length in lengths:
        for condition in conditions:
            clean, pert = paired_subsets(df, length, condition)
            if clean.empty:
                continue
            clean, pert = sample_paired(clean, pert, max_pairs=max_pairs, seed=seed + length)
            train_sequences = clean["sequence"].astype(str).str.upper().tolist()
            sequences = train_sequences + pert["sequence"].astype(str).str.upper().tolist()
            for pattern in patterns:
                if length < max(pattern) + 1:
                    continue
                for add_property in [False, True]:
                    mat, feature_count = matrix_with_train_vocabulary(
                        train_sequences,
                        sequences,
                        family="spaced",
                        pattern=pattern,
                        canonical=True,
                        add_property=add_property,
                    )
                    clean_x = mat[: len(clean)]
                    pert_x = mat[len(clean) :]
                    cos = cosine_diag(clean_x, pert_x)
                    l2 = row_l2_delta(clean_x, pert_x)
                    rows.append(
                        {
                            "length": length,
                            "condition": condition,
                            "condition_label": CONDITION_LABELS.get(condition, condition),
                            "method": "canonical spaced + property" if add_property else "canonical spaced",
                            "pattern": pattern_text(pattern),
                            "cardinality": len(pattern),
                            "span": max(pattern) + 1,
                            "role": pattern_role(pattern),
                            "add_property": add_property,
                            "n_pairs": int(len(clean)),
                            "paired_cosine_mean": float(np.mean(cos)),
                            "paired_cosine_p05": float(np.quantile(cos, 0.05)),
                            "l2_delta_mean": float(np.mean(l2)),
                            "l2_delta_p95": float(np.quantile(l2, 0.95)),
                            "retrieval_top1": retrieval_top1(clean_x, pert_x),
                            "n_features": int(feature_count),
                        }
                    )
    return pd.DataFrame(rows)


def readout_rows(df: pd.DataFrame, lengths: list[int], patterns: list[tuple[int, ...]], max_samples_per_group: int, seed: int) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for length in lengths:
        clean = df[(df["source_length"] == length) & (df["condition"] == "clean")].copy()
        if clean.empty:
            continue
        for genus, group_df in clean.groupby("genus"):
            if max_samples_per_group > 0 and len(group_df) > max_samples_per_group:
                group_df = group_df.sample(n=max_samples_per_group, random_state=seed + length).reset_index(drop=True)
            for label_col, probe_name in [("label", "within_genus_species"), ("target_binary", "target_background")]:
                if group_df[label_col].nunique() < 2:
                    continue
                for pattern in patterns:
                    if length < max(pattern) + 1:
                        continue
                    for add_property in [False, True]:
                        result = classification_probe(
                            group_df,
                            family="spaced",
                            k=None,
                            pattern=pattern,
                            canonical=True,
                            add_property=add_property,
                            label_col=label_col,
                            seed=seed,
                        )
                        row = {
                            "probe": probe_name,
                            "genus": genus,
                            "length": length,
                            "condition": "clean",
                            "method": "canonical spaced + property" if add_property else "canonical spaced",
                            "pattern": pattern_text(pattern),
                            "cardinality": len(pattern),
                            "span": max(pattern) + 1,
                            "role": pattern_role(pattern),
                            "add_property": add_property,
                            "n_samples": int(len(group_df)),
                            "n_classes": int(group_df[label_col].nunique()),
                        }
                        row.update(result)
                        rows.append(row)
    return pd.DataFrame(rows)


def aggregate_cardinality(stability: pd.DataFrame, readout: pd.DataFrame) -> pd.DataFrame:
    csp_stability = stability[stability["add_property"].eq(True)].copy()
    summary = (
        csp_stability.groupby(["cardinality", "role"], as_index=False)
        .agg(
            n_patterns=("pattern", "nunique"),
            n_stability_cells=("paired_cosine_mean", "size"),
            min_features=("n_features", "min"),
            median_features=("n_features", "median"),
            max_features=("n_features", "max"),
            mean_paired_cosine=("paired_cosine_mean", "mean"),
            min_paired_cosine=("paired_cosine_mean", "min"),
            max_paired_cosine=("paired_cosine_mean", "max"),
            mean_l2_delta=("l2_delta_mean", "mean"),
            mean_retrieval_top1=("retrieval_top1", "mean"),
        )
        .sort_values("cardinality")
    )
    if not readout.empty and "macro_f1" in readout:
        csp_readout = readout[readout["add_property"].eq(True)].dropna(subset=["macro_f1"]).copy()
        readout_agg = csp_readout.groupby(["cardinality"], as_index=False).agg(
            mean_macro_f1=("macro_f1", "mean"), min_macro_f1=("macro_f1", "min"), max_macro_f1=("macro_f1", "max")
        )
        summary = summary.merge(readout_agg, on="cardinality", how="left")
    return summary


def best_four_position_by_condition(stability: pd.DataFrame) -> pd.DataFrame:
    csp4 = stability[stability["add_property"].eq(True) & stability["cardinality"].eq(4)].copy()
    if csp4.empty:
        return csp4
    best = (
        csp4.sort_values(
            ["condition", "length", "paired_cosine_mean", "l2_delta_mean", "retrieval_top1"],
            ascending=[True, True, False, True, False],
        )
        .groupby(["condition", "length"], as_index=False)
        .first()
    )
    return best[
        ["condition_label", "length", "pattern", "paired_cosine_mean", "l2_delta_mean", "retrieval_top1", "n_features"]
    ].rename(
        columns={
            "condition_label": "Perturbation",
            "length": "Length",
            "pattern": "Best 4-position CSP pattern",
            "paired_cosine_mean": "Mean paired cosine",
            "l2_delta_mean": "Mean L2 drift",
            "retrieval_top1": "Nearest-clean retrieval",
            "n_features": "Features",
        }
    )


def best_readout(readout: pd.DataFrame) -> pd.DataFrame:
    if readout.empty or "macro_f1" not in readout:
        return pd.DataFrame()
    valid = readout.dropna(subset=["macro_f1"]).copy()
    grouped = valid.groupby(["probe", "length", "method", "pattern", "cardinality"], as_index=False).agg(
        mean_macro_f1=("macro_f1", "mean"),
        sd_macro_f1=("macro_f1", "std"),
        mean_accuracy=("accuracy", "mean"),
        mean_features=("n_features", "mean"),
        genera=("genus", "nunique"),
    )
    return grouped.sort_values(["probe", "length", "mean_macro_f1"], ascending=[True, True, False]).groupby(
        ["probe", "length"], as_index=False
    ).first()


def write_markdown(df: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(df.to_markdown(index=False, floatfmt=".3f") + "\n" if not df.empty else "", encoding="utf-8")


def write_summary(out_dir: Path, patterns: list[tuple[int, ...]], cardinality: pd.DataFrame, best4: pd.DataFrame, best_ro: pd.DataFrame) -> None:
    pattern_set = pd.DataFrame(
        [{"pattern": pattern_text(pattern), "cardinality": len(pattern), "span": max(pattern) + 1, "role": pattern_role(pattern)} for pattern in patterns]
    )
    lines = [
        "# Spaced-Pattern Sanity Validation",
        "",
        "This run keeps earlier parameter-sensitivity outputs intact and tests whether CSP conclusions depend on one four-position default seed.",
        "Expanded four-position layouts are the primary point-layout scan. Three-position and five-position layouts are supplementary cardinality sanity checks, not an exhaustive seed-design search.",
        "",
        "## Pattern set",
        "",
        pattern_set.to_markdown(index=False),
        "",
        "## CSP summary by seed cardinality",
        "",
        cardinality.to_markdown(index=False, floatfmt=".3f") if not cardinality.empty else "",
        "",
        "## Best four-position CSP pattern by perturbation and length",
        "",
        best4.to_markdown(index=False, floatfmt=".3f") if not best4.empty else "",
        "",
        "## Best clean readout setting within this spaced-pattern sanity run",
        "",
        best_ro.to_markdown(index=False, floatfmt=".3f")
        if not best_ro.empty
        else "Readout was skipped for this focused sanity run; the reported evidence is stability and feature-scale only.",
        "",
        "Interpretation: the expanded four-position scan is a sensitivity check. A best pattern changing across cells should be read as evidence against a universal seed prescription, not as evidence that a newly observed best pattern is globally optimized.",
    ]
    (out_dir / "spaced_pattern_sanity_summary.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Focused spaced-seed point-layout and cardinality sanity validation.")
    parser.add_argument("--input", default=str(PROJECT_ROOT / "data" / "real_slices" / "close_relative_reads.csv"))
    parser.add_argument("--output-dir", default=str(PROJECT_ROOT / "results" / "stage3" / "spaced_pattern_sanity"))
    parser.add_argument("--table-dir", default=str(PROJECT_ROOT / "manuscript" / "tables"))
    parser.add_argument("--lengths", default="69,75")
    parser.add_argument("--conditions", default="N_3pct,substitution_1pct,local_mismatch_6bp")
    parser.add_argument(
        "--patterns",
        default=(
            "0-1-2,0-2-4,0-3-6,"
            "0-1-2-3,0-1-3-6,0-2-4-6,0-1-4-7,0-2-5-7,0-2-5-8,0-3-5-8,0-3-6-9,"
            "0-1-2-3-4,0-1-3-6-9,0-2-4-6-8"
        ),
    )
    parser.add_argument("--max-clean-per-length", type=int, default=720)
    parser.add_argument("--max-paired-reads", type=int, default=360)
    parser.add_argument("--max-samples-per-group", type=int, default=120)
    parser.add_argument("--skip-readout", action="store_true", help="Only run stability and cardinality sanity metrics.")
    parser.add_argument("--seed", type=int, default=20260623)
    args = parser.parse_args()

    started = time.time()
    random.seed(args.seed)
    np.random.seed(args.seed)
    source = pd.read_csv(args.input)
    source["sequence"] = source["sequence"].astype(str).str.upper()
    source["source_length"] = source["source_length"].astype(int)
    lengths = parse_int_list(args.lengths)
    conditions = parse_str_list(args.conditions)
    patterns = [parse_pattern(item) for item in parse_str_list(args.patterns)]

    out_dir = Path(args.output_dir)
    table_dir = Path(args.table_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    table_dir.mkdir(parents=True, exist_ok=True)

    derived = derive_reads(source, lengths, conditions, seed=args.seed, max_clean_per_length=args.max_clean_per_length)
    stability = stability_rows(derived, lengths, conditions, patterns, max_pairs=args.max_paired_reads, seed=args.seed)
    readout = pd.DataFrame() if args.skip_readout else readout_rows(derived, lengths, patterns, max_samples_per_group=args.max_samples_per_group, seed=args.seed)
    cardinality = aggregate_cardinality(stability, readout)
    best4 = best_four_position_by_condition(stability)
    best_ro = best_readout(readout)

    stability.to_csv(out_dir / "spaced_pattern_sanity_stability.csv", index=False, encoding="utf-8-sig")
    if args.skip_readout:
        for stale in [out_dir / "spaced_pattern_sanity_readout.csv", out_dir / "spaced_pattern_sanity_best_readout.csv"]:
            if stale.exists():
                stale.unlink()
    else:
        readout.to_csv(out_dir / "spaced_pattern_sanity_readout.csv", index=False, encoding="utf-8-sig")
        best_ro.to_csv(out_dir / "spaced_pattern_sanity_best_readout.csv", index=False, encoding="utf-8-sig")
    cardinality.to_csv(out_dir / "spaced_pattern_sanity_cardinality_summary.csv", index=False, encoding="utf-8-sig")
    best4.to_csv(out_dir / "spaced_pattern_sanity_best_four_position.csv", index=False, encoding="utf-8-sig")

    write_markdown(cardinality, table_dir / "table_spaced_pattern_sanity_cardinality.md")
    write_markdown(best4, table_dir / "table_spaced_pattern_sanity_best_four_position.md")
    if args.skip_readout:
        readout_md = table_dir / "table_spaced_pattern_sanity_best_readout.md"
        if readout_md.exists():
            readout_md.unlink()
    else:
        write_markdown(best_ro, table_dir / "table_spaced_pattern_sanity_best_readout.md")
    write_summary(out_dir, patterns, cardinality, best4, best_ro)
    with (out_dir / "spaced_pattern_sanity_run.json").open("w", encoding="utf-8") as fh:
        json.dump(
            {
                "elapsed_seconds": time.time() - started,
                "input": args.input,
                "lengths": lengths,
                "conditions": conditions,
                "patterns": [pattern_text(pattern) for pattern in patterns],
                "max_clean_per_length": args.max_clean_per_length,
                "max_paired_reads": args.max_paired_reads,
                "max_samples_per_group": args.max_samples_per_group,
                "seed": args.seed,
                "n_stability_rows": int(len(stability)),
                "skip_readout": bool(args.skip_readout),
                "n_readout_rows": int(len(readout)),
            },
            fh,
            indent=2,
            ensure_ascii=False,
        )
    print(f"Wrote spaced-pattern sanity outputs to {out_dir}")


if __name__ == "__main__":
    main()

