from __future__ import annotations

import argparse
import json
import sys
import time
import warnings
from pathlib import Path

import pandas as pd


def _find_project_root(start: Path) -> Path:
    for candidate in [start.parent, *start.parents]:
        if (candidate / "methods").is_dir() and (candidate / "configs").is_dir():
            return candidate
    raise RuntimeError("Could not locate the release repository root.")


PROJECT_ROOT = _find_project_root(Path(__file__).resolve())
sys.path.insert(0, str(PROJECT_ROOT))

from experiments.main.run_local_mutation_sensitivity import make_triplets, parse_csv_list, parse_int_list, run_experiment  # noqa: E402


def write_summary(summary: pd.DataFrame, readout: pd.DataFrame, out_dir: Path) -> None:
    distance = (
        summary.groupby(["mutation_fraction", "representation"], as_index=False)
        .agg(
            n_cells=("noise_l2_mean", "count"),
            noise_l2=("noise_l2_mean", "mean"),
            local_l2=("local_l2_mean", "mean"),
            local_minus_noise_l2=("local_minus_noise_l2_mean", "mean"),
            n_features=("n_features", "mean"),
        )
        .sort_values(["mutation_fraction", "representation"])
    )
    distance["selective_sensitivity_ratio"] = distance["local_l2"] / distance["noise_l2"].clip(lower=1e-12)
    delta_readout = (
        readout[readout["split"].astype(str).str.contains("fold_cv")]
        .groupby(["mutation_fraction", "representation", "classifier"], as_index=False)
        .agg(
            n_cells=("macro_f1", "count"),
            macro_f1=("macro_f1", "mean"),
            accuracy=("accuracy", "mean"),
            n_features=("n_features", "mean"),
        )
        .sort_values(["mutation_fraction", "macro_f1"], ascending=[True, False])
    )
    distance.to_csv(out_dir / "local_mutation_fraction_distance_summary.csv", index=False, encoding="utf-8-sig")
    delta_readout.to_csv(out_dir / "local_mutation_fraction_delta_readout_summary.csv", index=False, encoding="utf-8-sig")
    lines = [
        "# Local mutation fraction sweep",
        "",
        "This reviewer-response sweep keeps the existing local-mode coverage (center, left, right, jittered) and varies mutation fraction. It is a focused supplement to the full local mutation sensitivity run, not a replacement for the complete representation matrix.",
        "",
        "## Distance summary",
        "",
        distance.to_markdown(index=False, floatfmt=".3f"),
        "",
        "## Delta-readout summary",
        "",
        delta_readout.to_markdown(index=False, floatfmt=".3f"),
        "",
    ]
    (out_dir / "local_mutation_fraction_sweep_summary.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    warnings.filterwarnings("ignore", category=UserWarning, module="sklearn.neighbors._nearest_centroid")
    warnings.filterwarnings("ignore", category=RuntimeWarning, module="sklearn.neighbors._nearest_centroid")
    parser = argparse.ArgumentParser(description="Run a focused local-mutation fraction sweep for reviewer response.")
    parser.add_argument("--output-dir", default=str(PROJECT_ROOT / "results" / "stage3" / "reviewer_response" / "local_mutation_fraction_sweep"))
    parser.add_argument("--representations", default="ckmer4_count_l2,ckmer4_property_l2,ckmer4_property_multiscale_mean_l2,property_channels,one_hot")
    parser.add_argument("--lengths", default="69,100,150")
    parser.add_argument("--local-modes", default="center,left,right,jittered")
    parser.add_argument("--mutation-fractions", default="0.01,0.03,0.05")
    parser.add_argument("--n-reads", type=int, default=180)
    parser.add_argument("--cv-folds", type=int, default=5)
    parser.add_argument("--seed", type=int, default=20260624)
    args = parser.parse_args()

    started = time.time()
    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    representations = parse_csv_list(args.representations)
    lengths = parse_int_list(args.lengths)
    local_modes = parse_csv_list(args.local_modes)
    fractions = [float(value) for value in parse_csv_list(args.mutation_fractions)]

    all_metrics: list[pd.DataFrame] = []
    all_readout: list[pd.DataFrame] = []
    all_summary: list[pd.DataFrame] = []
    for idx, fraction in enumerate(fractions):
        triplets = make_triplets(
            lengths=lengths,
            n_reads=args.n_reads,
            mutation_fraction=fraction,
            local_modes=local_modes,
            seed=args.seed + idx,
        )
        metrics, readout, summary = run_experiment(
            triplets=triplets,
            representations=representations,
            seed=args.seed + idx,
            cv_folds=args.cv_folds,
        )
        for frame in (metrics, readout, summary):
            frame["mutation_fraction"] = fraction
        all_metrics.append(metrics)
        all_readout.append(readout)
        all_summary.append(summary)
        triplets["mutation_fraction"] = fraction
        triplets.to_csv(out_dir / f"local_mutation_triplets_frac_{fraction:g}.csv", index=False, encoding="utf-8-sig")

    metrics_out = pd.concat(all_metrics, ignore_index=True)
    readout_out = pd.concat(all_readout, ignore_index=True)
    summary_out = pd.concat(all_summary, ignore_index=True)
    metrics_out.to_csv(out_dir / "local_mutation_fraction_pair_metrics.csv", index=False, encoding="utf-8-sig")
    readout_out.to_csv(out_dir / "local_mutation_fraction_delta_readout.csv", index=False, encoding="utf-8-sig")
    summary_out.to_csv(out_dir / "local_mutation_fraction_summary.csv", index=False, encoding="utf-8-sig")
    write_summary(summary_out, readout_out, out_dir)
    (out_dir / "local_mutation_fraction_sweep_run.json").write_text(
        json.dumps(
            {
                "elapsed_seconds": time.time() - started,
                "representations": representations,
                "lengths": lengths,
                "local_modes": local_modes,
                "mutation_fractions": fractions,
                "n_reads": args.n_reads,
                "cv_folds": args.cv_folds,
                "seed": args.seed,
                "n_metric_rows": int(len(metrics_out)),
                "n_readout_rows": int(len(readout_out)),
                "n_summary_rows": int(len(summary_out)),
            },
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    print(f"Wrote local mutation fraction sweep to {out_dir}")


if __name__ == "__main__":
    main()

