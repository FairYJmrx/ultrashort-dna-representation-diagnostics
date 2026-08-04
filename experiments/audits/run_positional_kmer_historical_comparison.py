"""Compare the promoted PKM candidate with current historical descriptors."""

from __future__ import annotations

import argparse
import json
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
from methods.ck4p_msp import CK4PMSPConfig, build_ck4_block, build_ck4p_msp_features  # noqa: E402
from methods.experimental_positional_kmer import (  # noqa: E402
    CK4P_MSP_PKM_KEY,
    build_ck4p_msp_pkm,
)
from methods.historical_descriptors import build_historical_descriptor_matrix  # noqa: E402


LABELS = {
    "ck4": "CK4",
    "ck5": "CK5",
    "ck4p_msp": "CK4P-MSP",
    CK4P_MSP_PKM_KEY: "CK4P-MSP-PKM",
    "pseknc_k3_l3": "PseKNC (k=3, lambda=3)",
    "pseeiip": "PseEIIP",
    "ncp_anf": "NCP+ANF",
}


def build_matrices(sequences: list[str], representations: list[str]) -> dict[str, np.ndarray]:
    length = max((len(sequence) for sequence in sequences), default=1)
    current = build_ck4p_msp_features(sequences)
    matrices: dict[str, np.ndarray] = {}
    for representation in representations:
        if representation == "ck4":
            matrices[representation] = current.ck4
        elif representation == "ck5":
            matrices[representation], _ = build_ck4_block(sequences, config=CK4PMSPConfig(k=5))
        elif representation == "ck4p_msp":
            matrices[representation] = current.matrix
        elif representation == CK4P_MSP_PKM_KEY:
            matrices[representation] = build_ck4p_msp_pkm(sequences)
        else:
            matrices[representation] = build_historical_descriptor_matrix(
                sequences,
                representation,
                length=length,
            )
    return matrices


def summary_table(
    stability: pd.DataFrame,
    local: pd.DataFrame,
    motif: pd.DataFrame,
    art: pd.DataFrame,
    cami: pd.DataFrame,
) -> pd.DataFrame:
    tables = [
        stability.groupby("representation", as_index=False).agg(
            wgs_l2=("l2_delta_mean", "mean"),
            wgs_retrieval=("retrieval_top1", "mean"),
        ),
        local.groupby("representation", as_index=False).agg(local_macro_f1=("macro_f1", "mean")),
        motif.groupby("representation", as_index=False).agg(motif_macro_f1=("macro_f1", "mean")),
        art.groupby("representation", as_index=False).agg(art_l2=("l2_delta_mean", "mean")),
    ]
    shifted = cami[~(cami["length"].eq(100) & cami["condition"].eq("clean"))]
    tables.append(
        shifted.groupby("representation", as_index=False).agg(
            cami_mean_retention=("retention_ratio", "mean")
        )
    )
    result = pd.DataFrame(
        {
            "representation": list(LABELS),
            "representation_label": list(LABELS.values()),
        }
    )
    for table in tables:
        result = result.merge(table, on="representation", how="left")
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stability-reads", default=str(PROJECT_ROOT / "results" / "stage3" / "contract_v2" / "compact_baselines" / "stage3_compact_baseline_reads.csv"))
    parser.add_argument("--local-triplets", default=str(PROJECT_ROOT / "results" / "stage3" / "contract_v2" / "local_mutation_sensitivity" / "local_mutation_triplets.csv"))
    parser.add_argument("--motif-reads", default=str(PROJECT_ROOT / "results" / "stage3" / "external_motif_position_probe" / "external_motif_position_probe_reads.csv"))
    parser.add_argument("--art-reads", default=str(PROJECT_ROOT / "results" / "stage3" / "contract_v2" / "art_current_contract" / "art_paired_reads.csv"))
    parser.add_argument("--cami-shifted", default=str(PROJECT_ROOT / "results" / "stage3" / "contract_v2" / "cami_fixed_head_transfer" / "cami_fixed_head_shifted_rows.csv"))
    parser.add_argument("--output-dir", default=str(PROJECT_ROOT / "results" / "stage3" / "candidate_positional_kmer_historical_comparison"))
    parser.add_argument("--lengths", default="69,75,100,150")
    parser.add_argument("--conditions", default="substitution_1pct,N_3pct,trim_5bp,substitution_1pct_N_3pct,local_mismatch_6bp,short_indel")
    parser.add_argument("--max-pairs", type=int, default=200)
    parser.add_argument("--max-triplets", type=int, default=250)
    parser.add_argument("--max-art-pairs-per-length", type=int, default=500)
    parser.add_argument("--max-cami-sources-per-class", type=int, default=200)
    parser.add_argument("--cv-folds", type=int, default=5)
    parser.add_argument("--seed", type=int, default=20260823)
    args = parser.parse_args()

    started = time.time()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    representations = list(LABELS)
    lengths = audit.parse_int_list(args.lengths)
    conditions = audit.parse_csv_list(args.conditions)
    stability_reads = pd.read_csv(args.stability_reads)
    local_triplets = pd.read_csv(args.local_triplets)
    motif_reads = pd.read_csv(args.motif_reads)
    art_reads = pd.read_csv(args.art_reads)
    cami_shifted = pd.read_csv(args.cami_shifted)

    audit.REPRESENTATION_LABELS = LABELS
    audit.build_all_matrices = build_matrices

    stability = audit.stability_audit(stability_reads, lengths=lengths, conditions=conditions, representations=representations, max_pairs=args.max_pairs, seed=args.seed)
    stability.to_csv(output_dir / "historical_wgs_stability.csv", index=False, encoding="utf-8-sig")
    print("[historical-comparison] WGS complete", flush=True)
    local = audit.local_audit(local_triplets, lengths=[length for length in lengths if length in set(local_triplets["source_length"])], representations=representations, max_triplets=args.max_triplets, cv_folds=args.cv_folds, seed=args.seed, standardize=False)
    local.to_csv(output_dir / "historical_local_readout.csv", index=False, encoding="utf-8-sig")
    print("[historical-comparison] local complete", flush=True)
    motif = audit.motif_audit(motif_reads, representations=representations, cv_folds=args.cv_folds, seed=args.seed)
    motif.to_csv(output_dir / "historical_motif_position.csv", index=False, encoding="utf-8-sig")
    print("[historical-comparison] motif complete", flush=True)
    art = audit.art_audit(art_reads, representations=representations, max_pairs_per_length=args.max_art_pairs_per_length, seed=args.seed)
    art.to_csv(output_dir / "historical_art_stability.csv", index=False, encoding="utf-8-sig")
    print("[historical-comparison] ART complete", flush=True)
    cami = audit.cami_fixed_head_audit(cami_shifted, representations=representations, max_sources_per_class=args.max_cami_sources_per_class, cv_folds=args.cv_folds, seed=args.seed)
    cami.to_csv(output_dir / "historical_cami_fixed_head.csv", index=False, encoding="utf-8-sig")
    print("[historical-comparison] CAMI complete", flush=True)

    summary = summary_table(stability, local, motif, art, cami)
    summary.to_csv(output_dir / "historical_comparison_summary.csv", index=False, encoding="utf-8-sig")
    (output_dir / "historical_comparison_summary.md").write_text(
        "# Current-contract historical descriptor comparison\n\n"
        + summary.to_markdown(index=False, floatfmt=".4f")
        + "\n\nThis lightweight comparison uses the same current feature contract, grouped probes and sampled evidence cells for every representation. It is a comparative profile, not a universal ranking.\n",
        encoding="utf-8",
    )
    (output_dir / "historical_comparison_run.json").write_text(
        json.dumps(
            {
                "elapsed_seconds": round(time.time() - started, 3),
                "representations": representations,
                "lengths": lengths,
                "conditions": conditions,
                "max_pairs": args.max_pairs,
                "max_triplets": args.max_triplets,
                "max_art_pairs_per_length": args.max_art_pairs_per_length,
                "max_cami_sources_per_class": args.max_cami_sources_per_class,
                "local_probe_scaling": "none (contract-space primary)",
                "cv_folds": args.cv_folds,
                "seed": args.seed,
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    print(summary.to_string(index=False))


if __name__ == "__main__":
    main()
