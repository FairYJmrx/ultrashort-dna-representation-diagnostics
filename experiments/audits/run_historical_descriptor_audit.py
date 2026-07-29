"""Compare CK4P-MSP with representative historical handcrafted descriptors."""

from __future__ import annotations

import argparse
import gc
import json
import platform
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
from threadpoolctl import threadpool_limits


def _find_project_root(start: Path) -> Path:
    for candidate in [start.parent, *start.parents]:
        if (candidate / "methods").is_dir() and (candidate / "configs").is_dir():
            return candidate
    raise RuntimeError("Could not locate the release repository root.")


PROJECT_ROOT = _find_project_root(Path(__file__).resolve())
sys.path.insert(0, str(PROJECT_ROOT))

from experiments.main.run_local_mutation_sensitivity import run_experiment  # noqa: E402
from experiments.main.run_stage2_representation_grid import (  # noqa: E402
    parse_csv_list,
    parse_int_list,
    run_readout_grid,
    run_stability_grid,
)
from methods.stage2_features import build_feature_matrix  # noqa: E402


DEFAULT_REPRESENTATIONS = "ck4,ck4p_msp,pseknc_k3_l3,ncp_anf,pseeiip"
DISPLAY_NAMES = {
    "ck4": "CK4",
    "ck4p_msp": "CK4P-MSP",
    "pseknc_k3_l3": "PseKNC (k=3, lambda=3)",
    "ncp_anf": "NCP+ANF",
    "pseeiip": "PseEIIP",
}


def _runtime_audit(
    reads: pd.DataFrame,
    representations: list[str],
    *,
    length: int,
    n_reads: int,
    repeats: int,
    seed: int,
) -> pd.DataFrame:
    subset = reads[(reads["source_length"].eq(length)) & (reads["condition"].eq("clean"))]
    if subset.empty:
        raise ValueError(f"No clean reads were available at {length} bp.")
    sequences = subset["sequence"].astype(str).tolist()
    rng = np.random.default_rng(seed)
    if len(sequences) < n_reads:
        indices = rng.choice(len(sequences), size=n_reads, replace=True)
        sequences = [sequences[int(idx)] for idx in indices]
    else:
        sequences = sequences[:n_reads]

    rows: list[dict[str, object]] = []
    warmup_sequences = sequences[: min(100, len(sequences))]
    with threadpool_limits(limits=1):
        for representation in representations:
            build_feature_matrix(
                warmup_sequences,
                representation,
                length=length,
                train_indices=list(range(len(warmup_sequences))),
            )

        tasks: list[tuple[int, str, int]] = []
        for repeat in range(repeats):
            order = list(representations)
            rng.shuffle(order)
            tasks.extend((repeat, representation, order_idx) for order_idx, representation in enumerate(order))

        for repeat, representation, order_idx in tasks:
            gc.collect()
            started = time.perf_counter()
            matrix, info = build_feature_matrix(
                sequences,
                representation,
                length=length,
                train_indices=list(range(len(sequences))),
            )
            elapsed = time.perf_counter() - started
            rows.append(
                {
                    "representation": representation,
                    "representation_label": DISPLAY_NAMES.get(representation, representation),
                    "repeat": repeat + 1,
                    "order_in_repeat": order_idx + 1,
                    "length": length,
                    "n_reads": len(sequences),
                    "n_features": info.n_features,
                    "elapsed_seconds": elapsed,
                    "milliseconds_per_10000_reads": elapsed * 1000.0 * 10000.0 / len(sequences),
                    "checksum": float(np.sum(matrix[: min(5, len(matrix))])),
                }
            )
    return pd.DataFrame(rows)


def _write_summary(
    stability: pd.DataFrame,
    readout: pd.DataFrame,
    local_summary: pd.DataFrame,
    local_readout: pd.DataFrame,
    runtime: pd.DataFrame,
    output_path: Path,
) -> None:
    stability_summary = (
        stability.dropna(subset=["l2_delta_mean"])
        .groupby("representation", as_index=False)
        .agg(
            n_cells=("l2_delta_mean", "size"),
            paired_cosine=("paired_cosine_mean", "mean"),
            standardized_drift=("l2_delta_mean", "mean"),
            retrieval_top1=("retrieval_top1", "mean"),
            n_features_min=("n_features", "min"),
            n_features_max=("n_features", "max"),
        )
    )
    readout_summary = (
        readout[(readout["classifier"].eq("logistic")) & readout["macro_f1"].notna()]
        .groupby("representation", as_index=False)
        .agg(macro_f1=("macro_f1", "mean"), n_readout_cells=("macro_f1", "size"))
    )
    local_distance_summary = (
        local_summary.groupby("representation", as_index=False)
        .agg(
            selective_sensitivity_ratio=("selective_sensitivity_ratio_mean", "mean"),
            local_minus_noise_l2=("local_minus_noise_l2_mean", "mean"),
        )
    )
    local_readout_summary = (
        local_readout[
            local_readout["split"].astype(str).str.contains("grouped_cv")
            & local_readout["classifier"].eq("logistic")
        ]
        .groupby("representation", as_index=False)
        .agg(grouped_local_change_macro_f1=("macro_f1", "mean"))
    )
    runtime_summary = (
        runtime.groupby(["representation", "representation_label"], as_index=False)
        .agg(
            runtime_ms_per_10000=("milliseconds_per_10000_reads", "median"),
            runtime_q25=("milliseconds_per_10000_reads", lambda values: float(np.quantile(values, 0.25))),
            runtime_q75=("milliseconds_per_10000_reads", lambda values: float(np.quantile(values, 0.75))),
            runtime_n_features=("n_features", "first"),
        )
    )
    combined = stability_summary
    for table in (readout_summary, local_distance_summary, local_readout_summary, runtime_summary):
        combined = combined.merge(table, on="representation", how="left")
    if "representation_label" not in combined.columns:
        combined.insert(1, "representation_label", combined["representation"].map(DISPLAY_NAMES))
    else:
        combined["representation_label"] = combined["representation_label"].fillna(
            combined["representation"].map(DISPLAY_NAMES)
        )
    combined.to_csv(output_path.with_suffix(".csv"), index=False, encoding="utf-8-sig")

    lines = [
        "# Historical Handcrafted Descriptor Audit",
        "",
        "The controls represent three established descriptor families: PseKNC composition plus physicochemical sequence-order correlation, NCP plus accumulated nucleotide frequency, and composition-weighted PseEIIP. All matrices entered the same row-normalized representation audit. Ambiguous bases used the deterministic extensions declared in `methods/historical_descriptors.py`.",
        "",
        combined.to_markdown(index=False, floatfmt=".4f"),
        "",
        "This audit tests comparative profile, not universal superiority. CK4P-MSP is distinguished only where the data support a different stability/readability/dimension/attribution trade-off.",
    ]
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--reads-csv",
        default=str(PROJECT_ROOT / "results" / "stage3" / "contract_v2" / "compact_baselines" / "stage3_compact_baseline_reads.csv"),
    )
    parser.add_argument(
        "--triplets-csv",
        default=str(PROJECT_ROOT / "results" / "stage3" / "contract_v2" / "local_mutation_sensitivity" / "local_mutation_triplets.csv"),
    )
    parser.add_argument(
        "--output-dir",
        default=str(PROJECT_ROOT / "results" / "stage3" / "contract_v2" / "historical_descriptor_audit"),
    )
    parser.add_argument("--representations", default=DEFAULT_REPRESENTATIONS)
    parser.add_argument("--lengths", default="69,75,100,125,150")
    parser.add_argument(
        "--conditions",
        default="substitution_1pct,N_3pct,trim_5bp,substitution_1pct_N_3pct,short_indel,local_mismatch_6bp",
    )
    parser.add_argument("--readout-conditions", default="clean,substitution_1pct,N_3pct,trim_5bp,substitution_1pct_N_3pct")
    parser.add_argument("--classifiers", default="logistic")
    parser.add_argument("--max-retrieval-pairs", type=int, default=400)
    parser.add_argument("--max-per-class", type=int, default=60)
    parser.add_argument("--cv-folds", type=int, default=5)
    parser.add_argument("--runtime-length", type=int, default=75)
    parser.add_argument("--runtime-reads", type=int, default=1000)
    parser.add_argument("--runtime-repeats", type=int, default=5)
    parser.add_argument(
        "--runtime-only",
        action="store_true",
        help="Recompute the implementation runtime table without rerunning the numerical audit.",
    )
    parser.add_argument("--seed", type=int, default=20260729)
    args = parser.parse_args()

    started = time.time()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    representations = parse_csv_list(args.representations)
    lengths = parse_int_list(args.lengths)
    conditions = parse_csv_list(args.conditions)
    readout_conditions = parse_csv_list(args.readout_conditions)
    classifiers = parse_csv_list(args.classifiers)

    reads = pd.read_csv(args.reads_csv)
    reads["source_length"] = reads["source_length"].astype(int)
    reads["sequence"] = reads["sequence"].astype(str).str.upper()
    available_conditions = set(reads["condition"].astype(str))
    conditions = [condition for condition in conditions if condition in available_conditions]
    readout_conditions = [condition for condition in readout_conditions if condition in available_conditions]

    if args.runtime_only:
        runtime = _runtime_audit(
            reads,
            representations,
            length=args.runtime_length,
            n_reads=args.runtime_reads,
            repeats=args.runtime_repeats,
            seed=args.seed,
        )
        runtime.to_csv(output_dir / "historical_descriptor_runtime.csv", index=False, encoding="utf-8-sig")
        (output_dir / "historical_descriptor_runtime_run.json").write_text(
            json.dumps(
                {
                    "elapsed_seconds": time.time() - started,
                    "representations": representations,
                    "runtime_length": args.runtime_length,
                    "runtime_reads": args.runtime_reads,
                    "runtime_repeats": args.runtime_repeats,
                    "runtime_protocol": "warm-up; randomized order within repeat; garbage collection before timing; one numerical-library thread",
                    "platform": platform.platform(),
                    "python": platform.python_version(),
                    "seed": args.seed,
                },
                indent=2,
            ),
            encoding="utf-8",
        )
        existing = {
            "stability": output_dir / "historical_descriptor_stability.csv",
            "readout": output_dir / "historical_descriptor_readout.csv",
            "local_summary": output_dir / "historical_descriptor_local_summary.csv",
            "local_readout": output_dir / "historical_descriptor_local_readout.csv",
        }
        if all(path.exists() for path in existing.values()):
            _write_summary(
                pd.read_csv(existing["stability"]),
                pd.read_csv(existing["readout"]),
                pd.read_csv(existing["local_summary"]),
                pd.read_csv(existing["local_readout"]),
                runtime,
                output_dir / "historical_descriptor_summary.md",
            )
        print(f"Updated historical descriptor runtime in {output_dir}")
        return

    stability = run_stability_grid(
        reads,
        lengths=lengths,
        conditions=["clean", *conditions],
        representations=representations,
        max_pairs=args.max_retrieval_pairs,
        seed=args.seed,
        output_path=output_dir / "historical_descriptor_stability.csv",
    )
    stability.to_csv(output_dir / "historical_descriptor_stability.csv", index=False, encoding="utf-8-sig")

    readout = run_readout_grid(
        reads,
        lengths=lengths,
        conditions=readout_conditions,
        representations=representations,
        classifiers=classifiers,
        seed=args.seed,
        max_per_class=args.max_per_class,
    )
    readout.to_csv(output_dir / "historical_descriptor_readout.csv", index=False, encoding="utf-8-sig")

    triplets = pd.read_csv(args.triplets_csv)
    local_metrics, local_readout, local_summary = run_experiment(
        triplets=triplets,
        representations=representations,
        seed=args.seed,
        cv_folds=args.cv_folds,
    )
    local_metrics.to_csv(output_dir / "historical_descriptor_local_metrics.csv", index=False, encoding="utf-8-sig")
    local_readout.to_csv(output_dir / "historical_descriptor_local_readout.csv", index=False, encoding="utf-8-sig")
    local_summary.to_csv(output_dir / "historical_descriptor_local_summary.csv", index=False, encoding="utf-8-sig")

    runtime = _runtime_audit(
        reads,
        representations,
        length=args.runtime_length,
        n_reads=args.runtime_reads,
        repeats=args.runtime_repeats,
        seed=args.seed,
    )
    runtime.to_csv(output_dir / "historical_descriptor_runtime.csv", index=False, encoding="utf-8-sig")

    _write_summary(
        stability,
        readout,
        local_summary,
        local_readout,
        runtime,
        output_dir / "historical_descriptor_summary.md",
    )
    (output_dir / "historical_descriptor_audit_run.json").write_text(
        json.dumps(
            {
                "elapsed_seconds": time.time() - started,
                "reads_csv": str(Path(args.reads_csv).resolve()),
                "triplets_csv": str(Path(args.triplets_csv).resolve()),
                "representations": representations,
                "lengths": lengths,
                "conditions": conditions,
                "readout_conditions": readout_conditions,
                "classifiers": classifiers,
                "max_retrieval_pairs": args.max_retrieval_pairs,
                "max_per_class": args.max_per_class,
                "cv_folds": args.cv_folds,
                "runtime_length": args.runtime_length,
                "runtime_reads": args.runtime_reads,
                "runtime_repeats": args.runtime_repeats,
                "runtime_protocol": "warm-up; randomized order within repeat; garbage collection before timing; one numerical-library thread",
                "platform": platform.platform(),
                "python": platform.python_version(),
                "seed": args.seed,
                "n_stability_rows": len(stability),
                "n_readout_rows": len(readout),
                "n_local_rows": len(local_summary),
            },
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    print(f"Wrote historical descriptor audit to {output_dir}")


if __name__ == "__main__":
    main()
