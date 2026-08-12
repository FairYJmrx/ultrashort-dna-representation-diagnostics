"""Run the single long-duration runtime contract used by the manuscript.

The benchmark measures raw-sequence-to-feature-matrix extraction only.  Every
method receives the same seeded 75-bp batch, with no disk I/O in the timed
region.  Each method is timed for at least ``target_seconds`` and
``minimum_repeats``.  The round-robin schedule keeps methods exposed to the
same long-running workstation state instead of making one short call look
representative of the whole process.
"""

from __future__ import annotations

import argparse
import gc
import json
import os
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

from experiments.audits.run_high_k_compressed_baselines import (  # noqa: E402
    hashed_kmer_matrix,
    minhash_signatures,
    random_projection_kmer_matrix,
)
from methods.ck4p_msp import (  # noqa: E402
    build_ck4_block,
    build_ck4p_msp_features,
    build_p_block,
)
from methods.experimental_positional_kmer import build_ck4p_msp_pkm  # noqa: E402
from methods.stage2_features import build_feature_matrix  # noqa: E402


DEFAULT_METHODS = (
    "ck4",
    "ck4_p",
    "ck4p_msp",
    "ck4p_msp_pkm",
    "hash_k15_d222",
    "minhash_k15_s222",
    "rp_ck15_d222",
    "pseknc_k3_l3",
    "ncp_anf",
    "pseeiip",
)

LABELS = {
    "ck4": "CK4",
    "ck4_p": "CK4+P",
    "ck4p_msp": "CK4P-MSP",
    "ck4p_msp_pkm": "CK4P-MSP-PKM",
    "hash_k15_d222": "Hashed k=15, d=222",
    "minhash_k15_s222": "MinHash k=15, s=222",
    "rp_ck15_d222": "CK15 random projection, d=222",
    "pseknc_k3_l3": "PseKNC (k=3, lambda=3)",
    "ncp_anf": "NCP+ANF",
    "pseeiip": "PseEIIP",
}


def _build_matrix(
    sequences: list[str],
    method: str,
    *,
    train_indices: list[int],
    seed: int,
) -> np.ndarray:
    """Build one method matrix using the release reference implementation."""
    if method == "ck4":
        matrix, _ = build_ck4_block(sequences, train_indices=train_indices)
        return matrix
    if method == "ck4_p":
        ck4, _ = build_ck4_block(sequences, train_indices=train_indices)
        p = build_p_block(sequences)
        return np.hstack([ck4, p]) / np.sqrt(2.0)
    if method == "ck4p_msp":
        return build_ck4p_msp_features(sequences, train_indices=train_indices).matrix
    if method == "ck4p_msp_pkm":
        return build_ck4p_msp_pkm(sequences)
    if method == "hash_k15_d222":
        return hashed_kmer_matrix(sequences, k=15, n_features=222, canonical=True, signed=True)
    if method == "minhash_k15_s222":
        return minhash_signatures(sequences, k=15, sketch_size=222, canonical=True, seed=seed)
    if method == "rp_ck15_d222":
        matrix, _ = random_projection_kmer_matrix(
            sequences,
            train_indices=train_indices,
            k=15,
            n_features=222,
            seed=seed,
        )
        return matrix
    if method in {"pseknc_k3_l3", "ncp_anf", "pseeiip"}:
        matrix, _ = build_feature_matrix(
            sequences,
            method,
            length=75,
            train_indices=train_indices,
        )
        return matrix
    raise ValueError(f"Unsupported runtime method: {method}")


def _timed_call(
    sequences: list[str],
    method: str,
    *,
    repeat: int,
    order_in_round: int,
    train_indices: list[int],
    seed: int,
    phase: str,
) -> dict[str, object]:
    gc.collect()
    started = time.perf_counter()
    matrix = _build_matrix(sequences, method, train_indices=train_indices, seed=seed + repeat)
    elapsed = time.perf_counter() - started
    checksum = float(np.sum(np.asarray(matrix)[:5]))
    n_features = int(matrix.shape[1])
    del matrix
    return {
        "method": method,
        "method_label": LABELS[method],
        "repeat": repeat,
        "order_in_round": order_in_round,
        "phase": phase,
        "n_reads": len(sequences),
        "n_features": n_features,
        "elapsed_seconds": float(elapsed),
        "milliseconds_per_10000_reads": float(elapsed * 1000.0 * 10000.0 / len(sequences)),
        "reads_per_second": float(len(sequences) / elapsed),
        "checksum": checksum,
    }


def _load_fixed_batch(reads_csv: Path, *, n_reads: int, seed: int) -> tuple[list[str], int]:
    reads = pd.read_csv(reads_csv, usecols=["source_length", "condition", "sequence"])
    pool = reads.loc[
        reads["source_length"].eq(75) & reads["condition"].eq("clean"), "sequence"
    ].astype(str).tolist()
    if not pool:
        raise RuntimeError("No clean 75-bp reads were found in the runtime input.")
    rng = np.random.default_rng(seed)
    indices = rng.choice(len(pool), size=n_reads, replace=len(pool) < n_reads)
    return [pool[int(index)] for index in indices], len(pool)


def _summary(raw: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for method, group in raw.groupby("method", sort=False):
        values = group["elapsed_seconds"].to_numpy(float)
        midpoint = max(1, len(values) // 2)
        first = values[:midpoint]
        second = values[midpoint:]
        rows.append(
            {
                "method": method,
                "method_label": LABELS[method],
                "n_features": int(group["n_features"].iloc[0]),
                "n_timed_calls": int(len(values)),
                "total_timed_seconds": float(values.sum()),
                "median_seconds_per_call": float(np.median(values)),
                "q25_seconds_per_call": float(np.quantile(values, 0.25)),
                "q75_seconds_per_call": float(np.quantile(values, 0.75)),
                "mean_seconds_per_call": float(values.mean()),
                "cv_seconds_per_call": float(values.std(ddof=1) / values.mean()) if len(values) > 1 else 0.0,
                "first_half_median_seconds": float(np.median(first)),
                "second_half_median_seconds": float(np.median(second)) if len(second) else np.nan,
                "steady_state_q25_seconds_per_call": float(np.quantile(second, 0.25)) if len(second) else np.nan,
                "steady_state_q75_seconds_per_call": float(np.quantile(second, 0.75)) if len(second) else np.nan,
                "second_to_first_median_ratio": float(np.median(second) / np.median(first)) if len(second) else np.nan,
                "median_ms_per_10000_reads": float(np.median(group["milliseconds_per_10000_reads"])),
                "steady_state_median_ms_per_10000_reads": float(np.median(second) * 1000.0),
                "median_reads_per_second": float(np.median(group["reads_per_second"])),
                "min_repeat_requirement_met": bool(len(values) >= 5),
            }
        )
    result = pd.DataFrame(rows)
    direct = float(result.loc[result["method"].eq("ck4p_msp"), "median_ms_per_10000_reads"].iloc[0])
    steady_direct = float(
        result.loc[result["method"].eq("ck4p_msp"), "steady_state_median_ms_per_10000_reads"].iloc[0]
    )
    result["runtime_ratio_vs_ck4p_msp"] = result["median_ms_per_10000_reads"] / direct
    result["steady_state_runtime_ratio_vs_ck4p_msp"] = (
        result["steady_state_median_ms_per_10000_reads"] / steady_direct
    )
    return result


def run_benchmark(
    sequences: list[str],
    methods: list[str],
    *,
    target_seconds: float,
    minimum_repeats: int,
    seed: int,
    output_dir: Path,
) -> pd.DataFrame:
    train_indices = list(range(len(sequences)))
    raw_rows: list[dict[str, object]] = []
    completed: dict[str, float] = {method: 0.0 for method in methods}
    repeats: dict[str, int] = {method: 0 for method in methods}
    round_number = 0

    # Every path receives an untimed 100-read warm-up. The first full batch is
    # timed in the long-run schedule, so the burn-in policy is explicit.
    warmup = sequences[:100]
    for method in methods:
        _build_matrix(warmup, method, train_indices=list(range(len(warmup))), seed=seed)

    while any(completed[method] < target_seconds or repeats[method] < minimum_repeats for method in methods):
        round_number += 1
        order = methods.copy()
        np.random.default_rng(seed + round_number).shuffle(order)
        for order_index, method in enumerate(order, start=1):
            if completed[method] >= target_seconds and repeats[method] >= minimum_repeats:
                continue
            row = _timed_call(
                sequences,
                method,
                repeat=repeats[method] + 1,
                order_in_round=order_index,
                train_indices=train_indices,
                seed=seed,
                phase="long_duration_round_robin",
            )
            raw_rows.append(row)
            completed[method] += float(row["elapsed_seconds"])
            repeats[method] += 1
            pd.DataFrame(raw_rows).to_csv(output_dir / "unified_runtime_raw_partial.csv", index=False, encoding="utf-8-sig")
    return pd.DataFrame(raw_rows)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--reads-csv",
        default=str(PROJECT_ROOT / "results" / "stage3" / "contract_v2" / "compact_baselines" / "stage3_compact_baseline_reads.csv"),
    )
    parser.add_argument("--output-dir", default=str(PROJECT_ROOT / "results" / "stage3" / "contract_v2" / "unified_runtime_benchmark"))
    parser.add_argument("--n-reads", type=int, default=10000)
    parser.add_argument("--target-seconds", type=float, default=120.0)
    parser.add_argument("--minimum-repeats", type=int, default=5)
    parser.add_argument("--seed", type=int, default=20260811)
    parser.add_argument("--methods", default=",".join(DEFAULT_METHODS))
    parser.add_argument("--scaling-read-count", type=int, default=100000)
    parser.add_argument("--skip-scaling", action="store_true")
    parser.add_argument("--scaling-only", action="store_true")
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    methods = [method.strip() for method in args.methods.split(",") if method.strip()]
    unknown = sorted(set(methods) - set(DEFAULT_METHODS))
    if unknown:
        raise ValueError(f"Unsupported methods: {unknown}")
    sequences, pool_size = _load_fixed_batch(Path(args.reads_csv), n_reads=args.n_reads, seed=args.seed)

    started = time.perf_counter()
    if args.scaling_only:
        scaling_sequences, _ = _load_fixed_batch(
            Path(args.reads_csv), n_reads=args.scaling_read_count, seed=args.seed + 1
        )
        scaling_rows: list[dict[str, object]] = []
        with threadpool_limits(limits=1):
            warmup = scaling_sequences[:100]
            for method in methods:
                _build_matrix(
                    warmup,
                    method,
                    train_indices=list(range(len(warmup))),
                    seed=args.seed + 1,
                )
            train_indices = list(range(len(scaling_sequences)))
            for order_index, method in enumerate(methods, start=1):
                scaling_rows.append(
                    _timed_call(
                        scaling_sequences,
                        method,
                        repeat=1,
                        order_in_round=order_index,
                        train_indices=train_indices,
                        seed=args.seed + 1,
                        phase="single_scaling_pass",
                    )
                )
        scaling = pd.DataFrame(scaling_rows)
        scaling.to_csv(output_dir / "unified_runtime_scaling.csv", index=False, encoding="utf-8-sig")
        (output_dir / "unified_runtime_scaling_run.json").write_text(
            json.dumps(
                {
                    "protocol": "one actual scaling pass per method after an untimed 100-read warm-up; one numerical-library thread; disk I/O excluded",
                    "n_reads": int(args.scaling_read_count),
                    "source_pool_clean_75bp_reads": int(pool_size),
                    "seed": int(args.seed + 1),
                    "methods": methods,
                    "elapsed_wall_seconds": float(time.perf_counter() - started),
                    "python": sys.version,
                    "platform": platform.platform(),
                    "processor": platform.processor(),
                    "input": str(Path(args.reads_csv)),
                },
                indent=2,
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )
        print(scaling.to_string(index=False))
        print(f"Wrote unified runtime scaling pass to {output_dir}")
        return

    with threadpool_limits(limits=1):
        raw = run_benchmark(
            sequences,
            methods,
            target_seconds=args.target_seconds,
            minimum_repeats=args.minimum_repeats,
            seed=args.seed,
            output_dir=output_dir,
        )
        scaling_rows: list[dict[str, object]] = []
        if not args.skip_scaling:
            scaling_sequences, _ = _load_fixed_batch(
                Path(args.reads_csv), n_reads=args.scaling_read_count, seed=args.seed + 1
            )
            train_indices = list(range(len(scaling_sequences)))
            # One direct scaling pass per method; the long-duration benchmark
            # remains the primary runtime estimate.
            for order_index, method in enumerate(methods, start=1):
                row = _timed_call(
                    scaling_sequences,
                    method,
                    repeat=1,
                    order_in_round=order_index,
                    train_indices=train_indices,
                    seed=args.seed + 1,
                    phase="single_scaling_pass",
                )
                scaling_rows.append(row)
            scaling = pd.DataFrame(scaling_rows)
            scaling.to_csv(output_dir / "unified_runtime_scaling.csv", index=False, encoding="utf-8-sig")
    raw.to_csv(output_dir / "unified_runtime_raw.csv", index=False, encoding="utf-8-sig")
    summary = _summary(raw)
    summary.to_csv(output_dir / "unified_runtime_summary.csv", index=False, encoding="utf-8-sig")
    metadata = {
        "protocol": "same seeded clean 75-bp batch; no timed disk I/O; untimed 100-read warm-up; one numerical-library thread; round-robin randomized order; each method timed for at least target_seconds and minimum_repeats",
        "n_reads": int(args.n_reads),
        "source_pool_clean_75bp_reads": int(pool_size),
        "target_seconds_per_method": float(args.target_seconds),
        "minimum_repeats": int(args.minimum_repeats),
        "seed": int(args.seed),
        "methods": methods,
        "scaling_read_count": None if args.skip_scaling else int(args.scaling_read_count),
        "elapsed_wall_seconds": float(time.perf_counter() - started),
        "python": sys.version,
        "platform": platform.platform(),
        "processor": platform.processor(),
        "pid": os.getpid(),
        "input": str(Path(args.reads_csv)),
        "runtime_definition": "raw sequence strings to returned feature matrix, including method-specific construction/setup but excluding disk I/O",
        "primary_summary": "unified_runtime_summary.csv",
    }
    (output_dir / "unified_runtime_benchmark_run.json").write_text(
        json.dumps(metadata, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    summary_text = [
        "# Unified long-duration runtime benchmark",
        "",
        "The primary estimate is the full-run median per-call wall-clock time from a seeded 10,000-read, 75-bp batch. Each method was warmed up, then timed in randomized round-robin order until both the declared duration and minimum repeat count were reached. The benchmark excludes disk I/O and uses one numerical-library thread. Second-half medians and the second-half/first-half ratio are retained as load-dependent drift diagnostics, not as cross-method ranking values.",
        "",
        summary.to_markdown(index=False, floatfmt=".4f"),
        "",
        "Runtime is an implementation- and hardware-specific engineering measurement. The steady-state value is not a hardware-independent complexity estimate.",
    ]
    (output_dir / "unified_runtime_benchmark_summary.md").write_text("\n".join(summary_text) + "\n", encoding="utf-8")
    print(summary.to_string(index=False))
    print(f"Wrote unified runtime benchmark to {output_dir}")


if __name__ == "__main__":
    main()
