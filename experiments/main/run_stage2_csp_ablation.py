from __future__ import annotations

import argparse
import json
import random
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

from src.stage2_features import build_feature_matrix, paired_retrieval_metrics


def parse_csv_list(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


def parse_int_list(value: str) -> list[int]:
    return [int(item.strip()) for item in value.split(",") if item.strip()]


def set_global_seed(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)


def paired_subsets(df: pd.DataFrame, length: int, condition: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    clean = df[(df["source_length"] == length) & (df["condition"] == "clean")].copy()
    pert = df[(df["source_length"] == length) & (df["condition"] == condition)].copy()
    common = sorted(set(clean["clean_read_id"]) & set(pert["clean_read_id"]))
    clean = clean[clean["clean_read_id"].isin(common)].sort_values("clean_read_id").reset_index(drop=True)
    pert = pert[pert["clean_read_id"].isin(common)].sort_values("clean_read_id").reset_index(drop=True)
    return clean, pert


def component_representations() -> list[tuple[str, str]]:
    components = ["hydrogen", "gc", "purine", "eiip", "n_fraction", "entropy", "length"]
    rows: list[tuple[str, str]] = [
        ("spaced_count_l2", "spaced, no RC"),
        ("cspaced_count_l2", "canonical spaced"),
    ]
    for comp in components:
        rows.append((f"cspaced_property_selected:{comp}", f"canonical spaced + {comp}"))
    cumulative: list[str] = []
    for comp in components:
        cumulative.append(comp)
        rows.append((f"cspaced_property_selected:{'+'.join(cumulative)}", "canonical spaced + cumulative " + "+".join(cumulative)))
    rows.extend(
        [
            ("cspaced_property_selected:hydrogen+gc+purine+eiip+entropy+length", "full CSP without N fraction"),
            ("cspaced_property_selected:hydrogen+gc+purine+eiip+n_fraction+entropy", "full CSP without length"),
            ("cspaced_property_l2", "full CSP"),
        ]
    )
    return rows


def run_ablation(df: pd.DataFrame, lengths: list[int], conditions: list[str], max_pairs: int, seed: int) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    reps = component_representations()
    for length in lengths:
        for condition in conditions:
            if condition == "clean":
                continue
            clean, pert = paired_subsets(df, length, condition)
            if clean.empty:
                continue
            if max_pairs > 0 and len(clean) > max_pairs:
                keep = clean["clean_read_id"].drop_duplicates().sample(n=max_pairs, random_state=seed + length).tolist()
                clean = clean[clean["clean_read_id"].isin(keep)].sort_values("clean_read_id").reset_index(drop=True)
                pert = pert[pert["clean_read_id"].isin(keep)].sort_values("clean_read_id").reset_index(drop=True)
            all_seq = clean["sequence"].tolist() + pert["sequence"].tolist()
            train_idx = list(range(len(clean)))
            for rep, label in reps:
                try:
                    x, info = build_feature_matrix(all_seq, rep, length=length, train_indices=train_idx)
                    metric = paired_retrieval_metrics(x[: len(clean)], x[len(clean) :])
                    metric.update(
                        {
                            "length": length,
                            "condition": condition,
                            "representation": rep,
                            "label": label,
                            "n_pairs": int(len(clean)),
                            "n_features": info.n_features,
                            "density": info.density,
                        }
                    )
                    rows.append(metric)
                except Exception as exc:
                    rows.append(
                        {
                            "length": length,
                            "condition": condition,
                            "representation": rep,
                            "label": label,
                            "n_pairs": int(len(clean)),
                            "error": f"{type(exc).__name__}: {exc}",
                        }
                    )
    return pd.DataFrame(rows)


def delta_table(metrics: pd.DataFrame) -> pd.DataFrame:
    if metrics.empty:
        return metrics
    valid = metrics[~metrics.get("error", pd.Series(index=metrics.index, dtype=object)).notna()].copy()
    base = valid[valid["representation"] == "cspaced_count_l2"][
        ["length", "condition", "paired_cosine_mean", "l2_delta_mean", "retrieval_top1"]
    ].rename(
        columns={
            "paired_cosine_mean": "base_paired_cosine_mean",
            "l2_delta_mean": "base_l2_delta_mean",
            "retrieval_top1": "base_retrieval_top1",
        }
    )
    merged = valid.merge(base, on=["length", "condition"], how="left")
    merged["delta_cosine_vs_cspaced_count"] = merged["paired_cosine_mean"] - merged["base_paired_cosine_mean"]
    merged["delta_l2_vs_cspaced_count"] = merged["l2_delta_mean"] - merged["base_l2_delta_mean"]
    merged["delta_top1_vs_cspaced_count"] = merged["retrieval_top1"] - merged["base_retrieval_top1"]
    return merged


def write_summary(metrics: pd.DataFrame, deltas: pd.DataFrame, output_dir: Path) -> None:
    lines: list[str] = []
    lines.append("# Stage-2 CSP Component Ablation\n")
    lines.append("This audit separates the priors fused in CSP: spaced seeds, reverse-complement canonicalization and individual DNA property summaries.\n")
    if not deltas.empty:
        valid = deltas[deltas["representation"] != "cspaced_count_l2"].copy()
        best = (
            valid.sort_values(["condition", "length", "delta_cosine_vs_cspaced_count"], ascending=[True, True, False])
            .groupby(["condition", "length"], as_index=False)
            .first()
        )
        cols = [
            "condition",
            "length",
            "label",
            "delta_cosine_vs_cspaced_count",
            "delta_l2_vs_cspaced_count",
            "paired_cosine_mean",
            "l2_delta_mean",
            "n_features",
        ]
        lines.append("## Best property additions over canonical spaced counts\n")
        lines.append(best[cols].to_markdown(index=False, floatfmt=".4f"))
        lines.append("")
        full = deltas[deltas["representation"] == "cspaced_property_l2"]
        if not full.empty:
            lines.append("## Full CSP effect\n")
            lines.append(full[cols].to_markdown(index=False, floatfmt=".4f"))
            lines.append("")
    (output_dir / "csp_ablation_summary.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run stage-2 CSP component ablation.")
    parser.add_argument("--input", default=str(PROJECT_ROOT / "results" / "stage2" / "representation_grid" / "stage2_derived_reads.csv"))
    parser.add_argument("--output-dir", default=str(PROJECT_ROOT / "results" / "stage2" / "csp_ablation"))
    parser.add_argument("--lengths", default="69,75,100,150")
    parser.add_argument("--conditions", default="substitution_1pct,N_3pct,trim_5bp,substitution_1pct_N_3pct,short_indel,local_mismatch_6bp")
    parser.add_argument("--max-pairs", type=int, default=800)
    parser.add_argument("--seed", type=int, default=303)
    args = parser.parse_args()

    started = time.time()
    set_global_seed(args.seed)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(args.input)
    df["source_length"] = df["source_length"].astype(int)
    df["sequence"] = df["sequence"].astype(str).str.upper()
    metrics = run_ablation(
        df,
        lengths=parse_int_list(args.lengths),
        conditions=parse_csv_list(args.conditions),
        max_pairs=args.max_pairs,
        seed=args.seed,
    )
    deltas = delta_table(metrics)
    metrics.to_csv(output_dir / "csp_ablation_metrics.csv", index=False, encoding="utf-8-sig")
    deltas.to_csv(output_dir / "csp_ablation_deltas.csv", index=False, encoding="utf-8-sig")
    write_summary(metrics, deltas, output_dir)
    (output_dir / "csp_ablation_run.json").write_text(
        json.dumps(
            {
                "elapsed_seconds": time.time() - started,
                "input": args.input,
                "lengths": parse_int_list(args.lengths),
                "conditions": parse_csv_list(args.conditions),
                "max_pairs": args.max_pairs,
                "seed": args.seed,
                "n_metric_rows": int(len(metrics)),
            },
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    print(f"Wrote CSP ablation to {output_dir}")


if __name__ == "__main__":
    main()

