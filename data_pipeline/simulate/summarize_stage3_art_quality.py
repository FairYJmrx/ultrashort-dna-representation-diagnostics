from __future__ import annotations

import argparse
import json
import random
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

from experiments.main.run_stage2_representation_grid import parse_csv_list, set_global_seed  # noqa: E402
from src.stage2_features import build_feature_matrix, paired_retrieval_metrics  # noqa: E402

DEFAULT_REPRESENTATIONS = ",".join([
    "ckmer5_count_l2",
    "ckmer7_count_l2",
    "cspaced_count_l2",
    "cspaced_property_l2",
    "hybrid_ckmer5_csp",
    "minhash_k5_s128",
    "eiip_l2",
    "eiip_summary_l2",
])

REP_LABELS = {
    "ckmer5_count_l2": "canonical 5-mer",
    "ckmer7_count_l2": "canonical 7-mer",
    "cspaced_count_l2": "canonical spaced count",
    "cspaced_property_l2": "CSP",
    "hybrid_ckmer5_csp": "canonical 5-mer + CSP",
    "minhash_k5_s128": "MinHash k=5, s=128",
    "eiip_l2": "EIIP positional signal",
    "eiip_summary_l2": "EIIP summary",
}


def mean_phred(quality: str) -> float:
    if not isinstance(quality, str) or not quality:
        return float("nan")
    return float(sum(max(0, ord(ch) - 33) for ch in quality) / len(quality))


def assign_quality_bins(art: pd.DataFrame) -> pd.DataFrame:
    out = art.copy()
    out["mean_phred"] = out["quality"].map(mean_phred)
    out = out.dropna(subset=["mean_phred"]).copy()
    bins = ["low", "mid", "high"]
    for length, idx in out.groupby("source_length").groups.items():
        ranks = out.loc[idx, "mean_phred"].rank(method="first")
        out.loc[idx, "quality_bin"] = pd.qcut(ranks, q=3, labels=bins)
    return out


def paired_for_bin(reads: pd.DataFrame, art_bin: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    ids = set(art_bin["clean_read_id"].astype(str))
    clean = reads[(reads["condition"] == "clean") & reads["clean_read_id"].astype(str).isin(ids)].copy()
    pert = art_bin.copy()
    common = sorted(set(clean["clean_read_id"].astype(str)) & set(pert["clean_read_id"].astype(str)))
    clean = clean[clean["clean_read_id"].astype(str).isin(common)].sort_values("clean_read_id").reset_index(drop=True)
    pert = pert[pert["clean_read_id"].astype(str).isin(common)].sort_values("clean_read_id").reset_index(drop=True)
    return clean, pert


def run_quality_grid(reads: pd.DataFrame, reps: list[str], max_pairs: int, seed: int, output_path: Path) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    art = assign_quality_bins(reads[reads["condition"] == "art_illumina"].copy())
    for length in sorted(art["source_length"].astype(int).unique()):
        length_art = art[art["source_length"].astype(int) == length].copy()
        for qbin in ["low", "mid", "high"]:
            bin_art = length_art[length_art["quality_bin"].astype(str) == qbin].copy()
            if bin_art.empty:
                continue
            clean, pert = paired_for_bin(reads[reads["source_length"].astype(int) == length].copy(), bin_art)
            if clean.empty:
                continue
            if max_pairs > 0 and len(clean) > max_pairs:
                rng = random.Random(int(seed) + int(length) + {"low": 1, "mid": 2, "high": 3}[qbin])
                keep = rng.sample(clean["clean_read_id"].tolist(), max_pairs)
                clean = clean[clean["clean_read_id"].isin(keep)].sort_values("clean_read_id").reset_index(drop=True)
                pert = pert[pert["clean_read_id"].isin(keep)].sort_values("clean_read_id").reset_index(drop=True)
            all_seq = clean["sequence"].tolist() + pert["sequence"].tolist()
            train_idx = list(range(len(clean)))
            q_min = float(bin_art["mean_phred"].min())
            q_mean = float(bin_art["mean_phred"].mean())
            q_max = float(bin_art["mean_phred"].max())
            for rep in reps:
                try:
                    x, info = build_feature_matrix(all_seq, rep, length=length, train_indices=train_idx)
                    metric = paired_retrieval_metrics(x[: len(clean)], x[len(clean) :])
                    metric.update({
                        "length": int(length),
                        "quality_bin": qbin,
                        "mean_phred_min": q_min,
                        "mean_phred_mean": q_mean,
                        "mean_phred_max": q_max,
                        "representation": rep,
                        "representation_label": REP_LABELS.get(rep, rep),
                        "n_pairs": int(len(clean)),
                        "n_features": info.n_features,
                        "density": info.density,
                        "avg_nnz_per_read": info.avg_nnz_per_read,
                    })
                    rows.append(metric)
                except Exception as exc:
                    rows.append({
                        "length": int(length),
                        "quality_bin": qbin,
                        "representation": rep,
                        "n_pairs": int(len(clean)),
                        "error": f"{type(exc).__name__}: {exc}",
                    })
                pd.DataFrame(rows).to_csv(output_path, index=False, encoding="utf-8-sig")
                print(f"[art-quality] rows={len(rows)} length={length} bin={qbin} rep={rep}", flush=True)
    return pd.DataFrame(rows)


def write_summary(metrics: pd.DataFrame, output_dir: Path) -> None:
    lines: list[str] = ["# Stage-3 ART Quality-stratified Stability Summary\n"]
    valid = metrics[metrics.get("error", pd.Series(index=metrics.index, dtype=object)).isna()].copy()
    if valid.empty:
        lines.append("No valid ART quality-stratified metrics were produced.")
    else:
        best = (
            valid.sort_values(["length", "quality_bin", "paired_cosine_mean"], ascending=[True, True, False])
            .groupby(["length", "quality_bin"], as_index=False)
            .first()
        )
        cols = [
            "length", "quality_bin", "representation_label", "paired_cosine_mean", "l2_delta_mean",
            "retrieval_top1", "mean_phred_mean", "n_pairs", "n_features",
        ]
        lines.append("## Best stability by length and quality bin\n")
        lines.append(best[cols].to_markdown(index=False, floatfmt=".3f"))
        lines.append("\n## Mean by representation and quality bin\n")
        grouped = valid.groupby(["quality_bin", "representation_label"], as_index=False).agg(
            paired_cosine_mean=("paired_cosine_mean", "mean"),
            l2_delta_mean=("l2_delta_mean", "mean"),
            retrieval_top1=("retrieval_top1", "mean"),
            n_features=("n_features", "median"),
        )
        lines.append(grouped.to_markdown(index=False, floatfmt=".3f"))
    (output_dir / "art_quality_stratified_summary.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Summarize ART Illumina stability across FASTQ quality strata.")
    parser.add_argument("--input", default=str(PROJECT_ROOT / "results" / "stage3" / "art_illumina" / "art_paired_reads.csv"))
    parser.add_argument("--output-dir", default=str(PROJECT_ROOT / "results" / "stage3" / "art_quality_stratified"))
    parser.add_argument("--representations", default=DEFAULT_REPRESENTATIONS)
    parser.add_argument("--max-pairs", type=int, default=400)
    parser.add_argument("--seed", type=int, default=707)
    args = parser.parse_args()

    started = time.time()
    set_global_seed(args.seed)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    reads = pd.read_csv(args.input)
    reads["source_length"] = reads["source_length"].astype(int)
    reads["sequence"] = reads["sequence"].astype(str).str.upper()
    reps = parse_csv_list(args.representations)
    metrics = run_quality_grid(
        reads=reads,
        reps=reps,
        max_pairs=args.max_pairs,
        seed=args.seed,
        output_path=output_dir / "art_quality_stratified_stability.csv",
    )
    metrics.to_csv(output_dir / "art_quality_stratified_stability.csv", index=False, encoding="utf-8-sig")
    write_summary(metrics, output_dir)
    (output_dir / "art_quality_stratified_run.json").write_text(
        json.dumps({
            "elapsed_seconds": time.time() - started,
            "input": args.input,
            "representations": reps,
            "max_pairs": args.max_pairs,
            "seed": args.seed,
            "n_rows": int(len(metrics)),
        }, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(f"Wrote ART quality-stratified results to {output_dir}")


if __name__ == "__main__":
    main()


