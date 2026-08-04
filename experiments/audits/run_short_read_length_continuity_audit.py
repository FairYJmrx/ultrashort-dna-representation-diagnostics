"""Audit CK4P-MSP continuously across the controlled 50--75 bp regime."""

from __future__ import annotations

import argparse
import json
import math
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd


def _find_project_root(start: Path) -> Path:
    for candidate in [start.parent, *start.parents]:
        if (candidate / "methods").is_dir() and (candidate / "configs").is_dir():
            return candidate
    raise RuntimeError("Could not locate the release repository root.")


PROJECT_ROOT = _find_project_root(Path(__file__).resolve())
sys.path.insert(0, str(PROJECT_ROOT))

from experiments.audits.run_high_k_compressed_baselines import (  # noqa: E402
    run_minhash_jaccard_audit,
    run_stability as run_high_k_stability,
)
from experiments.audits.run_msp_bin_gamma_sensitivity_audit import (  # noqa: E402
    local_audit as run_binset_local,
    stability_audit as run_binset_stability,
)
from experiments.audits.run_p_msp_contribution_audit import (  # noqa: E402
    conditional_contribution_tests,
    local_delta_audit,
    stability_audit,
)
from experiments.main.run_local_mutation_sensitivity import make_triplets, run_experiment  # noqa: E402
from experiments.main.run_stage2_representation_grid import (  # noqa: E402
    apply_stage2_condition,
    parse_csv_list,
    parse_int_list,
    set_global_seed,
)


DEFAULT_CONDITIONS = (
    "substitution_1pct,N_3pct,trim_5bp,substitution_1pct_N_3pct,"
    "local_mismatch_6bp,short_indel"
)


def balanced_templates(frame: pd.DataFrame, max_templates: int, seed: int) -> pd.DataFrame:
    clean = frame[
        frame["condition"].astype(str).eq("clean")
        & frame["source_length"].astype(int).eq(150)
    ].copy()
    if clean.empty:
        raise ValueError("The source table contains no clean 150-bp templates.")
    labels = sorted(clean["label"].astype(str).unique().tolist())
    per_label = max(1, int(math.ceil(max_templates / max(1, len(labels)))))
    parts: list[pd.DataFrame] = []
    for index, label in enumerate(labels):
        subset = clean[clean["label"].astype(str).eq(label)]
        parts.append(subset.sample(n=min(per_label, len(subset)), random_state=seed + index))
    selected = pd.concat(parts, ignore_index=True)
    if len(selected) > max_templates:
        selected = selected.sample(n=max_templates, random_state=seed).reset_index(drop=True)
    return selected.sort_values(["label", "clean_read_id"]).reset_index(drop=True)


def derive_length_grid(
    templates: pd.DataFrame,
    lengths: list[int],
    conditions: list[str],
    seed: int,
) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for length in lengths:
        for template_index, (_, source) in enumerate(templates.iterrows()):
            base = source.copy()
            base_sequence = str(source["sequence"]).upper()[:length]
            template_id = f"continuity_T{template_index:05d}"
            clean_id = f"{template_id}_L{length}"
            base["sequence"] = base_sequence
            base["clean_read_id"] = clean_id
            base["read_id"] = f"{clean_id}_clean"
            base["source_length"] = int(length)
            base["length"] = int(length)
            base["condition"] = "clean"
            base["source_rule"] = "prefix_truncation_from_shared_150bp_template"
            base["observed_layout"] = f"SE{length}"
            base["continuity_template_id"] = template_id
            for condition in ["clean", *conditions]:
                perturbed = apply_stage2_condition(base, condition, seed)
                perturbed["continuity_template_id"] = template_id
                rows.append(perturbed)
    return pd.DataFrame(rows)


def summarize_results(
    stability: pd.DataFrame,
    readout: pd.DataFrame,
    bin_stability: pd.DataFrame,
    bin_readout: pd.DataFrame,
    anchor_historical_stability: pd.DataFrame,
    anchor_historical_readout: pd.DataFrame,
    anchor_high_k: pd.DataFrame,
    anchor_minhash: pd.DataFrame,
    output_dir: Path,
) -> None:
    stability_summary = (
        stability.groupby(["length", "representation", "representation_label"], as_index=False)
        .agg(
            n_cells=("condition", "nunique"),
            l2_delta_mean=("l2_delta_mean", "mean"),
            paired_cosine_mean=("paired_cosine_mean", "mean"),
            retrieval_top1_mean=("retrieval_top1", "mean"),
            n_features=("n_features", "first"),
        )
    )
    grouped = readout[readout["split"].astype(str).str.contains("grouped_cv")].copy()
    readout_summary = (
        grouped.groupby(["length", "representation", "representation_label"], as_index=False)
        .agg(
            n_cells=("local_mode", "nunique"),
            macro_f1_mean=("macro_f1", "mean"),
            macro_f1_sd=("macro_f1", "std"),
            n_features=("n_features", "first"),
        )
    )
    bin_stability_summary = (
        bin_stability[bin_stability["gamma"].eq(1.0)]
        .groupby(["length", "binset", "bins"], as_index=False)
        .agg(l2_delta_mean=("l2_delta_mean", "mean"), paired_cosine_mean=("paired_cosine_mean", "mean"))
    )
    bin_grouped = bin_readout[
        bin_readout["split"].astype(str).str.contains("grouped_cv")
        & bin_readout["gamma"].eq(1.0)
    ].copy()
    bin_readout_summary = (
        bin_grouped.groupby(["length", "binset", "bins"], as_index=False)
        .agg(macro_f1_mean=("macro_f1", "mean"), macro_f1_sd=("macro_f1", "std"))
    )
    historical_grouped = anchor_historical_readout[
        anchor_historical_readout["split"].astype(str).str.contains("grouped_cv")
    ].copy()
    historical_readout_summary = (
        historical_grouped.groupby(["length", "representation"], as_index=False)
        .agg(macro_f1_mean=("macro_f1", "mean"), macro_f1_sd=("macro_f1", "std"))
    )
    outputs = {
        "length_continuity_stability_summary.csv": stability_summary,
        "length_continuity_delta_readout_summary.csv": readout_summary,
        "length_continuity_binset_stability_summary.csv": bin_stability_summary,
        "length_continuity_binset_readout_summary.csv": bin_readout_summary,
        "anchor_historical_stability.csv": anchor_historical_stability,
        "anchor_historical_readout_summary.csv": historical_readout_summary,
        "anchor_high_k_stability.csv": anchor_high_k,
        "anchor_minhash_jaccard.csv": anchor_minhash,
    }
    for filename, frame in outputs.items():
        frame.to_csv(output_dir / filename, index=False, encoding="utf-8-sig")

    contrasts = conditional_contribution_tests(stability, readout, seed=20260730)
    contrasts.to_csv(output_dir / "length_continuity_conditional_contrasts.csv", index=False, encoding="utf-8-sig")

    lines = [
        "# Short-read length-continuity audit",
        "",
        "The dense 50--75 bp grid is a controlled boundary audit over shared templates, not 26 independent biological cohorts and not part of the pre-specified 24-cell primary inference grid.",
        "",
        "## Seven-block stability at 50, 60, 70 and 75 bp",
        "",
        stability_summary[stability_summary["length"].isin([50, 60, 70, 75])].to_markdown(index=False, floatfmt=".4f"),
        "",
        "## Seven-block grouped local readout at 50, 60, 70 and 75 bp",
        "",
        readout_summary[readout_summary["length"].isin([50, 60, 70, 75])].to_markdown(index=False, floatfmt=".4f"),
        "",
        "## Three-anchor historical readout",
        "",
        historical_readout_summary.to_markdown(index=False, floatfmt=".4f"),
    ]
    (output_dir / "short_read_length_continuity_summary.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-reads", default=str(PROJECT_ROOT / "data" / "real_slices" / "close_relative_reads.csv"))
    parser.add_argument("--output-dir", default=str(PROJECT_ROOT / "results" / "stage3" / "contract_v2" / "short_read_length_continuity"))
    parser.add_argument("--lengths", default="-".join(["50", "75"]))
    parser.add_argument("--anchor-lengths", default="50,60,75")
    parser.add_argument("--conditions", default=DEFAULT_CONDITIONS)
    parser.add_argument("--max-templates", type=int, default=420)
    parser.add_argument("--triplets-per-mode", type=int, default=180)
    parser.add_argument("--mutation-fraction", type=float, default=0.08)
    parser.add_argument("--local-modes", default="center,left,right,jittered")
    parser.add_argument("--cv-folds", type=int, default=5)
    parser.add_argument("--seed", type=int, default=20260730)
    args = parser.parse_args()

    started = time.time()
    set_global_seed(args.seed)
    if "-" in args.lengths and "," not in args.lengths:
        start, stop = [int(value) for value in args.lengths.split("-", maxsplit=1)]
        lengths = list(range(start, stop + 1))
    else:
        lengths = parse_int_list(args.lengths)
    anchors = parse_int_list(args.anchor_lengths)
    conditions = parse_csv_list(args.conditions)
    local_modes = parse_csv_list(args.local_modes)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    source = pd.read_csv(args.source_reads)
    templates = balanced_templates(source, args.max_templates, args.seed)
    templates[["clean_read_id", "label", "genus", "species", "template_start", "template_end"]].to_csv(
        output_dir / "shared_template_manifest.csv", index=False, encoding="utf-8-sig"
    )
    reads = derive_length_grid(templates, lengths, conditions, args.seed)
    reads.to_csv(output_dir / "short_read_length_grid.csv.gz", index=False, compression="gzip")

    triplets = make_triplets(
        lengths=lengths,
        n_reads=args.triplets_per_mode,
        mutation_fraction=args.mutation_fraction,
        local_modes=local_modes,
        seed=args.seed,
    )
    triplets.to_csv(output_dir / "short_read_local_triplets.csv.gz", index=False, compression="gzip")

    stability = stability_audit(reads, lengths, conditions, args.max_templates, args.seed)
    local_pairs, readout = local_delta_audit(triplets, lengths, args.triplets_per_mode, args.seed, args.cv_folds)
    stability.to_csv(output_dir / "length_continuity_seven_block_stability.csv", index=False, encoding="utf-8-sig")
    local_pairs.to_csv(output_dir / "length_continuity_seven_block_local_pairs.csv.gz", index=False, compression="gzip")
    readout.to_csv(output_dir / "length_continuity_seven_block_readout.csv", index=False, encoding="utf-8-sig")

    bin_stability = run_binset_stability(reads, lengths, conditions, [1.0], args.max_templates, args.seed)
    bin_readout = run_binset_local(triplets, lengths, [1.0], args.triplets_per_mode, args.seed, args.cv_folds)
    bin_stability.to_csv(output_dir / "length_continuity_binset_stability.csv", index=False, encoding="utf-8-sig")
    bin_readout.to_csv(output_dir / "length_continuity_binset_readout.csv", index=False, encoding="utf-8-sig")

    historical_representations = ["ck4", "ck4p_msp", "pseknc_k3_l3", "ncp_anf", "pseeiip"]
    historical_stability = run_high_k_stability(
        reads,
        anchors,
        conditions,
        historical_representations,
        args.max_templates,
        args.seed,
        15,
        222,
    )
    _, historical_readout, _ = run_experiment(triplets[triplets["source_length"].isin(anchors)], historical_representations, args.seed, args.cv_folds)
    high_k_stability = run_high_k_stability(
        reads,
        anchors,
        conditions,
        ["ck4", "ck4_p", "ck4p_msp", "hash_k15_d222", "rp_ck15_d222"],
        args.max_templates,
        args.seed,
        15,
        222,
    )
    minhash = run_minhash_jaccard_audit(reads, anchors, conditions, args.max_templates, args.seed, 15, 222)

    summarize_results(
        stability,
        readout,
        bin_stability,
        bin_readout,
        historical_stability,
        historical_readout,
        high_k_stability,
        minhash,
        output_dir,
    )
    metadata = {
        "elapsed_seconds": round(time.time() - started, 3),
        "source_reads": str(Path(args.source_reads).resolve()),
        "lengths": lengths,
        "anchor_lengths": anchors,
        "conditions": conditions,
        "shared_templates": int(len(templates)),
        "triplets_per_length_mode": int(args.triplets_per_mode),
        "local_modes": local_modes,
        "mutation_fraction": float(args.mutation_fraction),
        "cv_folds": int(args.cv_folds),
        "seed": int(args.seed),
        "inference_scope": "descriptive shared-template boundary audit; excluded from the primary 24-cell inferential grid",
    }
    (output_dir / "short_read_length_continuity_run.json").write_text(
        json.dumps(metadata, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(f"Wrote short-read length-continuity audit to {output_dir}")


if __name__ == "__main__":
    main()
