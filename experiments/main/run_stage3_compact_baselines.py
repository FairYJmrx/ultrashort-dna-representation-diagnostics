from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import pandas as pd

def _find_project_root(start: Path) -> Path:
    for candidate in [start.parent, *start.parents]:
        if (candidate / "methods").is_dir() and (candidate / "configs").is_dir():
            return candidate
    raise RuntimeError("Could not locate the release repository root.")


PROJECT_ROOT = _find_project_root(Path(__file__).resolve())
sys.path.insert(0, str(PROJECT_ROOT))

from experiments.main.run_stage2_representation_grid import (  # noqa: E402
    derive_stage2_reads,
    parse_csv_list,
    parse_int_list,
    run_readout_grid,
    run_stability_grid,
    set_global_seed,
    write_summary,
)


DEFAULT_REPRESENTATIONS = ",".join(
    [
        "ck4",
        "ck4_p",
        "ck4p_msp",
        "ckmer5_count_l2",
        "ckmer7_count_l2",
        "cspaced_count_l2",
        "cspaced_property_l2",
        "hybrid_ckmer5_csp",
        "hybrid_ckmer7_csp",
        "minhash_k5_s128",
        "minhash_k7_s128",
        "eiip_l2",
        "eiip_summary_l2",
    ]
)

DEFAULT_READOUT_REPRESENTATIONS = ",".join(
    [
        "ck4",
        "ck4_p",
        "ck4p_msp",
        "ckmer5_count_l2",
        "cspaced_count_l2",
        "cspaced_property_l2",
        "hybrid_ckmer5_csp",
        "minhash_k5_s128",
        "eiip_l2",
        "eiip_summary_l2",
    ]
)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run stage-3 compact classical baselines against CSP on the existing WGS-derived grid."
    )
    parser.add_argument("--input", default=str(PROJECT_ROOT / "data" / "real_slices" / "close_relative_reads.csv"))
    parser.add_argument("--output-dir", default=str(PROJECT_ROOT / "results" / "stage3" / "compact_baselines"))
    parser.add_argument("--lengths", default="69,75,100,110,125,150,300")
    parser.add_argument("--readout-lengths", default="69,75,100,150")
    parser.add_argument(
        "--conditions",
        default="clean,substitution_1pct,N_3pct,trim_5bp,substitution_1pct_N_3pct,short_indel,local_mismatch_6bp",
    )
    parser.add_argument("--representations", default=DEFAULT_REPRESENTATIONS)
    parser.add_argument("--readout-representations", default=DEFAULT_READOUT_REPRESENTATIONS)
    parser.add_argument("--classifiers", default="nearest_centroid,logistic")
    parser.add_argument("--max-clean-per-length", type=int, default=600)
    parser.add_argument("--max-retrieval-pairs", type=int, default=400)
    parser.add_argument("--max-per-class", type=int, default=60)
    parser.add_argument("--seed", type=int, default=303)
    args = parser.parse_args()

    started = time.time()
    set_global_seed(args.seed)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    source = pd.read_csv(args.input)
    source["source_length"] = source["source_length"].astype(int)
    source["sequence"] = source["sequence"].astype(str).str.upper()

    lengths = parse_int_list(args.lengths)
    readout_lengths = parse_int_list(args.readout_lengths)
    conditions = parse_csv_list(args.conditions)
    reps = parse_csv_list(args.representations)
    readout_reps = parse_csv_list(args.readout_representations)
    classifiers = parse_csv_list(args.classifiers)

    stage3_reads = derive_stage2_reads(
        source,
        lengths,
        conditions,
        seed=args.seed,
        max_clean_per_length=args.max_clean_per_length,
    )
    stage3_reads.to_csv(output_dir / "stage3_compact_baseline_reads.csv", index=False, encoding="utf-8-sig")

    stability = run_stability_grid(
        stage3_reads,
        lengths=lengths,
        conditions=conditions,
        representations=reps,
        max_pairs=args.max_retrieval_pairs,
        seed=args.seed,
        output_path=output_dir / "compact_baseline_stability.csv",
    )
    stability.to_csv(output_dir / "compact_baseline_stability.csv", index=False, encoding="utf-8-sig")

    readout_conditions = [c for c in conditions if c in {"clean", "substitution_1pct", "N_3pct", "trim_5bp", "substitution_1pct_N_3pct"}]
    readout = run_readout_grid(
        stage3_reads,
        lengths=readout_lengths,
        conditions=readout_conditions,
        representations=readout_reps,
        classifiers=classifiers,
        seed=args.seed,
        max_per_class=args.max_per_class,
    )
    readout.to_csv(output_dir / "compact_baseline_readout.csv", index=False, encoding="utf-8-sig")
    write_summary(stability, readout, output_dir)

    (output_dir / "stage3_compact_baselines_run.json").write_text(
        json.dumps(
            {
                "elapsed_seconds": time.time() - started,
                "input": args.input,
                "lengths": lengths,
                "readout_lengths": readout_lengths,
                "conditions": conditions,
                "representations": reps,
                "readout_representations": readout_reps,
                "classifiers": classifiers,
                "n_reads": int(len(stage3_reads)),
                "n_stability_rows": int(len(stability)),
                "n_readout_rows": int(len(readout)),
            },
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    print(f"Wrote stage-3 compact baseline results to {output_dir}")


if __name__ == "__main__":
    main()

