"""Audit prespecified PKM/CPKM augment weights across the evidence layers."""

from __future__ import annotations

import argparse
import json
import platform
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

from experiments.audits import run_positional_kmer_candidate_audit as audit  # noqa: E402
from methods.experimental_positional_kmer import (  # noqa: E402
    CK4P_MSP_PKM_KEY,
    CK4P_MSP_PKM_LABEL,
    CK4P_MSP_PKM_WEIGHT,
    build_positional_kmer_candidate,
    build_weighted_augment_candidates,
)


def parse_float_list(text: str) -> list[float]:
    values = [float(item.strip()) for item in text.split(",") if item.strip()]
    if not values or any(value <= 0 for value in values):
        raise ValueError("weights must contain positive comma-separated values")
    return values


def weight_suffix(weight: float) -> str:
    return f"w{int(round(float(weight) * 100)):03d}"


def representation_metadata(weights: list[float]) -> pd.DataFrame:
    rows: list[dict[str, object]] = [
        {
            "representation": "ck4p_msp",
            "representation_label": "CK4P-MSP",
            "route": "main",
            "candidate_weight": 0.0,
            "n_features": 222,
        }
    ]
    for route in ["pkm", "cpkm"]:
        for weight in weights:
            suffix = weight_suffix(weight)
            is_selected = route == "pkm" and np.isclose(weight, CK4P_MSP_PKM_WEIGHT)
            representation = (
                CK4P_MSP_PKM_KEY
                if is_selected
                else f"{route}_weight_{suffix}"
            )
            display_label = (
                CK4P_MSP_PKM_LABEL
                if is_selected
                else f"{route.upper()} weight={weight:g}"
            )
            rows.append(
                {
                    "representation": representation,
                    "representation_label": display_label,
                    "route": route,
                    "candidate_weight": float(weight),
                    "n_features": 297,
                }
            )
    return pd.DataFrame(rows)


def build_decision_table(
    metadata: pd.DataFrame,
    stability: pd.DataFrame,
    local: pd.DataFrame,
    motif: pd.DataFrame,
    art: pd.DataFrame,
    cami: pd.DataFrame,
    inherited_runtime: pd.DataFrame,
) -> pd.DataFrame:
    wgs = stability.groupby("representation", as_index=False).agg(
        wgs_l2=("l2_delta_mean", "mean"),
        wgs_retrieval=("retrieval_top1", "mean"),
    )
    local_summary = local.groupby("representation", as_index=False).agg(
        local_macro_f1=("macro_f1", "mean")
    )
    motif_summary = motif.groupby("representation", as_index=False).agg(
        motif_macro_f1=("macro_f1", "mean")
    )
    art_summary = art.groupby("representation", as_index=False).agg(
        art_l2=("l2_delta_mean", "mean")
    )
    shifted = cami[~(cami["length"].eq(100) & cami["condition"].eq("clean"))]
    cami_summary = shifted.groupby("representation", as_index=False).agg(
        cami_mean_retention=("retention_ratio", "mean")
    )
    decision = metadata.copy()
    for frame in [wgs, local_summary, motif_summary, art_summary, cami_summary, inherited_runtime]:
        decision = decision.merge(frame, on="representation", how="left")
    baseline = decision[decision["representation"].eq("ck4p_msp")].iloc[0]
    decision["motif_gain_vs_main"] = decision["motif_macro_f1"] - baseline["motif_macro_f1"]
    decision["wgs_l2_change_vs_main"] = decision["wgs_l2"] - baseline["wgs_l2"]
    decision["wgs_retrieval_change_vs_main"] = decision["wgs_retrieval"] - baseline["wgs_retrieval"]
    decision["local_f1_change_vs_main"] = decision["local_macro_f1"] - baseline["local_macro_f1"]
    decision["art_l2_change_vs_main"] = decision["art_l2"] - baseline["art_l2"]
    decision["cami_retention_change_vs_main"] = (
        decision["cami_mean_retention"] - baseline["cami_mean_retention"]
    )
    decision["runtime_ratio_vs_main"] = decision["runtime_seconds"] / baseline["runtime_seconds"]
    decision["pass_motif"] = decision["motif_gain_vs_main"].ge(0.02)
    decision["pass_wgs_l2"] = decision["wgs_l2_change_vs_main"].le(0.01)
    decision["pass_retrieval"] = decision["wgs_retrieval_change_vs_main"].ge(-0.01)
    decision["pass_local"] = decision["local_f1_change_vs_main"].ge(-0.01)
    decision["pass_art"] = decision["art_l2_change_vs_main"].le(0.01)
    decision["pass_cami"] = decision["cami_retention_change_vs_main"].ge(-0.02)
    decision["pass_runtime"] = decision["runtime_ratio_vs_main"].le(2.0)
    scientific = ["pass_motif", "pass_wgs_l2", "pass_retrieval", "pass_local", "pass_art", "pass_cami"]
    candidate = decision["route"].ne("main")
    decision["eligible_scientific_confirmation"] = candidate & decision[scientific].all(axis=1)
    decision["eligible_main_confirmation"] = (
        decision["eligible_scientific_confirmation"] & decision["pass_runtime"]
    )
    return decision


def runtime_audit(
    metadata: pd.DataFrame,
    sequences: list[str],
    repeats: int,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    method_by_route = {
        "main": "ck4p_msp",
        "pkm": "candidate_pkm_augment",
        "cpkm": "candidate_cpkm_augment",
    }
    raw_rows: list[dict[str, object]] = []
    routes = list(method_by_route)
    for repeat in range(repeats):
        ordered_routes = routes if repeat % 2 == 0 else list(reversed(routes))
        for route in ordered_routes:
            started = time.perf_counter()
            matrix = build_positional_kmer_candidate(sequences, method_by_route[route])
            elapsed = time.perf_counter() - started
            raw_rows.append(
                {
                    "route": route,
                    "method": method_by_route[route],
                    "repeat": repeat + 1,
                    "n_reads": len(sequences),
                    "n_features": int(matrix.shape[1]),
                    "seconds": float(elapsed),
                }
            )
    raw = pd.DataFrame(raw_rows)
    route_runtime = raw.groupby("route")["seconds"].median().to_dict()
    table = metadata[["representation", "route"]].copy()
    table["runtime_seconds"] = table["route"].map(route_runtime)
    table["runtime_source"] = "direct route extraction; fixed weight does not change extraction cost"
    return table.drop(columns="route"), raw


def write_summary(decision: pd.DataFrame, output_dir: Path, run_metadata: dict[str, object]) -> None:
    scientific = decision[decision["eligible_scientific_confirmation"]]
    main = decision[decision["eligible_main_confirmation"]]
    lines = [
        "# Fixed-weight positional k-mer augment screen",
        "",
        "Weights were prespecified before viewing this screen. This is a Pareto audit, not task-specific tuning. CK4P-MSP-PKM denotes only the prespecified PKM delta=0.25 extension.",
        "A candidate can replace CK4P-MSP only after passing every scientific and engineering gate and reproducing under an independent seed/template split.",
        "",
        decision.to_markdown(index=False, floatfmt=".4f"),
        "",
        "## Outcome",
        "",
        "Scientifically eligible for independent confirmation: "
        + (", ".join(scientific["representation"].tolist()) if not scientific.empty else "none"),
        "",
        "Eligible for main-method confirmation including runtime: "
        + (", ".join(main["representation"].tolist()) if not main.empty else "none"),
        "",
        "Runtime is measured directly for each extraction route; changing the fixed concatenation weight does not change extraction cost.",
        "",
        "## Run metadata",
        "",
        "```json",
        json.dumps(run_metadata, indent=2, ensure_ascii=False),
        "```",
    ]
    (output_dir / "positional_kmer_weight_sweep_summary.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--weights", default="0.1,0.25,0.5,0.75,1.0")
    parser.add_argument("--stability-reads", default=str(PROJECT_ROOT / "results" / "stage3" / "contract_v2" / "compact_baselines" / "stage3_compact_baseline_reads.csv"))
    parser.add_argument("--local-triplets", default=str(PROJECT_ROOT / "results" / "stage3" / "contract_v2" / "local_mutation_sensitivity" / "local_mutation_triplets.csv"))
    parser.add_argument("--motif-reads", default=str(PROJECT_ROOT / "results" / "stage3" / "external_motif_position_probe" / "external_motif_position_probe_reads.csv"))
    parser.add_argument("--art-reads", default=str(PROJECT_ROOT / "results" / "stage3" / "contract_v2" / "art_current_contract" / "art_paired_reads.csv"))
    parser.add_argument("--cami-shifted", default=str(PROJECT_ROOT / "results" / "stage3" / "contract_v2" / "cami_fixed_head_transfer" / "cami_fixed_head_shifted_rows.csv"))
    parser.add_argument("--output-dir", default=str(PROJECT_ROOT / "results" / "stage3" / "candidate_positional_kmer_weight_sweep"))
    parser.add_argument("--lengths", default="69,75,100,150")
    parser.add_argument("--conditions", default="substitution_1pct,N_3pct,trim_5bp,substitution_1pct_N_3pct,local_mismatch_6bp,short_indel")
    parser.add_argument("--max-pairs", type=int, default=500)
    parser.add_argument("--max-triplets", type=int, default=400)
    parser.add_argument("--max-art-pairs-per-length", type=int, default=2000)
    parser.add_argument("--max-cami-sources-per-class", type=int, default=600)
    parser.add_argument("--runtime-reads", type=int, default=10000)
    parser.add_argument("--runtime-repeats", type=int, default=2)
    parser.add_argument("--cv-folds", type=int, default=5)
    parser.add_argument("--seed", type=int, default=20260805)
    args = parser.parse_args()

    started = time.time()
    weights = parse_float_list(args.weights)
    metadata = representation_metadata(weights)
    representations = metadata["representation"].tolist()
    labels = dict(zip(metadata["representation"], metadata["representation_label"]))

    def weighted_builder(sequences: list[str], requested: list[str]) -> dict[str, np.ndarray]:
        matrices = build_weighted_augment_candidates(sequences, weights)
        return {name: matrices[name] for name in requested}

    # The shared audit functions resolve these two names at call time.
    audit.REPRESENTATION_LABELS = labels
    audit.build_all_matrices = weighted_builder

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    lengths = audit.parse_int_list(args.lengths)
    conditions = audit.parse_csv_list(args.conditions)
    stability_reads = pd.read_csv(args.stability_reads)
    local_triplets = pd.read_csv(args.local_triplets)
    motif_reads = pd.read_csv(args.motif_reads)
    art_reads = pd.read_csv(args.art_reads)
    cami_shifted = pd.read_csv(args.cami_shifted)

    stability = audit.stability_audit(stability_reads, lengths=lengths, conditions=conditions, representations=representations, max_pairs=args.max_pairs, seed=args.seed)
    stability.to_csv(output_dir / "weight_wgs_stability.csv", index=False, encoding="utf-8-sig")
    print("[weight-sweep] WGS stability complete", flush=True)
    local = audit.local_audit(local_triplets, lengths=[length for length in lengths if length in set(local_triplets["source_length"])], representations=representations, max_triplets=args.max_triplets, cv_folds=args.cv_folds, seed=args.seed, standardize=False)
    local.to_csv(output_dir / "weight_local_readout.csv", index=False, encoding="utf-8-sig")
    print("[weight-sweep] grouped local readout complete", flush=True)
    motif = audit.motif_audit(motif_reads, representations=representations, cv_folds=args.cv_folds, seed=args.seed)
    motif.to_csv(output_dir / "weight_motif_position.csv", index=False, encoding="utf-8-sig")
    print("[weight-sweep] motif-position complete", flush=True)
    art = audit.art_audit(art_reads, representations=representations, max_pairs_per_length=args.max_art_pairs_per_length, seed=args.seed)
    art.to_csv(output_dir / "weight_art_stability.csv", index=False, encoding="utf-8-sig")
    print("[weight-sweep] ART screen complete", flush=True)
    cami = audit.cami_fixed_head_audit(cami_shifted, representations=representations, max_sources_per_class=args.max_cami_sources_per_class, cv_folds=args.cv_folds, seed=args.seed)
    cami.to_csv(output_dir / "weight_cami_fixed_head.csv", index=False, encoding="utf-8-sig")
    print("[weight-sweep] CAMI fixed-head screen complete", flush=True)

    runtime_pool = art_reads.loc[art_reads["condition"].eq("clean"), "sequence"].astype(str).tolist()
    if len(runtime_pool) < args.runtime_reads:
        runtime_pool.extend(
            stability_reads.loc[stability_reads["condition"].eq("clean"), "sequence"].astype(str).tolist()
        )
    runtime_sequences = runtime_pool[: args.runtime_reads]
    runtime, runtime_raw = runtime_audit(metadata, runtime_sequences, args.runtime_repeats)
    runtime_raw.to_csv(output_dir / "weight_runtime.csv", index=False, encoding="utf-8-sig")
    print("[weight-sweep] direct runtime complete", flush=True)
    decision = build_decision_table(metadata, stability, local, motif, art, cami, runtime)
    decision.to_csv(output_dir / "weight_decision_table.csv", index=False, encoding="utf-8-sig")
    run_metadata = {
        "elapsed_seconds": round(time.time() - started, 3),
        "weights": weights,
        "lengths": lengths,
        "conditions": conditions,
        "max_pairs": args.max_pairs,
        "max_triplets": args.max_triplets,
        "max_art_pairs_per_length": args.max_art_pairs_per_length,
        "max_cami_sources_per_class": args.max_cami_sources_per_class,
        "runtime_reads": len(runtime_sequences),
        "runtime_repeats": args.runtime_repeats,
        "cv_folds": args.cv_folds,
        "local_probe_scaling": "none (contract-space primary)",
        "seed": args.seed,
        "python": sys.version,
        "platform": platform.platform(),
        "processor": platform.processor(),
    }
    (output_dir / "weight_run.json").write_text(json.dumps(run_metadata, indent=2, ensure_ascii=False), encoding="utf-8")
    write_summary(decision, output_dir, run_metadata)
    print(f"Wrote positional k-mer weight sweep to {output_dir}")


if __name__ == "__main__":
    main()
