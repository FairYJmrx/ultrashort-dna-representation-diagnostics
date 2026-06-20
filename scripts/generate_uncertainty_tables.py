from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.preprocessing import normalize

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.run_prior_ablation import cosine_diag, paired_matrix


def bootstrap_ci(values: np.ndarray, rng: np.random.Generator, n_boot: int) -> tuple[float, float]:
    values = np.asarray(values, dtype=np.float64)
    if values.size == 0:
        return float("nan"), float("nan")
    idx = rng.integers(0, values.size, size=(n_boot, values.size))
    means = values[idx].mean(axis=1)
    return float(np.quantile(means, 0.025)), float(np.quantile(means, 0.975))


def property_ablation_uncertainty(
    df: pd.DataFrame,
    lengths: list[int],
    conditions: list[str],
    n_boot: int,
    seed: int,
) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    rows: list[dict[str, object]] = []
    for length in lengths:
        for condition in conditions:
            clean_b, pert_b, x_clean_b, x_pert_b = paired_matrix(df, "cspaced_count_l2", length, condition)
            clean_t, pert_t, x_clean_t, x_pert_t = paired_matrix(df, "cspaced_property_l2", length, condition)
            if clean_b.empty or clean_t.empty:
                continue
            ids_b = clean_b["clean_read_id"].tolist()
            ids_t = clean_t["clean_read_id"].tolist()
            if ids_b != ids_t or pert_b["clean_read_id"].tolist() != pert_t["clean_read_id"].tolist():
                raise ValueError(f"Pair order mismatch for length={length}, condition={condition}")

            cos_base = cosine_diag(x_clean_b, x_pert_b)
            cos_test = cosine_diag(x_clean_t, x_pert_t)
            norm_clean_b = normalize(x_clean_b, norm="l2", axis=1)
            norm_pert_b = normalize(x_pert_b, norm="l2", axis=1)
            norm_clean_t = normalize(x_clean_t, norm="l2", axis=1)
            norm_pert_t = normalize(x_pert_t, norm="l2", axis=1)
            l2_base = np.linalg.norm(norm_clean_b - norm_pert_b, axis=1)
            l2_test = np.linalg.norm(norm_clean_t - norm_pert_t, axis=1)

            delta_cos = cos_test - cos_base
            l2_improvement = l2_base - l2_test
            cos_lo, cos_hi = bootstrap_ci(delta_cos, rng, n_boot)
            l2_lo, l2_hi = bootstrap_ci(l2_improvement, rng, n_boot)
            rows.append(
                {
                    "condition": condition,
                    "length": length,
                    "n_pairs": int(delta_cos.size),
                    "delta_cosine_mean": float(delta_cos.mean()),
                    "delta_cosine_ci95_low": cos_lo,
                    "delta_cosine_ci95_high": cos_hi,
                    "l2_improvement_mean": float(l2_improvement.mean()),
                    "l2_improvement_ci95_low": l2_lo,
                    "l2_improvement_ci95_high": l2_hi,
                    "n_boot": n_boot,
                    "seed": seed,
                }
            )
    return pd.DataFrame(rows)


def markdown_table(df: pd.DataFrame, path: Path) -> None:
    view = df.copy()
    for col in view.columns:
        if pd.api.types.is_float_dtype(view[col]):
            view[col] = view[col].map(lambda x: f"{x:.3f}")
    path.write_text(view.to_markdown(index=False), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="data/real_slices/close_relative_reads.csv")
    parser.add_argument("--output-dir", default="results/runs/uncertainty")
    parser.add_argument("--table-dir", default="manuscript/tables")
    parser.add_argument("--lengths", default="69,75,100,125,150,300")
    parser.add_argument("--conditions", default="N_3pct,substitution_1pct")
    parser.add_argument("--n-boot", type=int, default=1000)
    parser.add_argument("--seed", type=int, default=20260620)
    args = parser.parse_args()

    df = pd.read_csv(PROJECT_ROOT / args.input)
    lengths = [int(item) for item in args.lengths.split(",") if item.strip()]
    conditions = [item.strip() for item in args.conditions.split(",") if item.strip()]
    out = property_ablation_uncertainty(df, lengths, conditions, args.n_boot, args.seed)

    output_dir = PROJECT_ROOT / args.output_dir
    table_dir = PROJECT_ROOT / args.table_dir
    output_dir.mkdir(parents=True, exist_ok=True)
    table_dir.mkdir(parents=True, exist_ok=True)
    out.to_csv(output_dir / "property_ablation_bootstrap.csv", index=False, encoding="utf-8-sig")
    markdown_table(out, table_dir / "table_property_ablation_bootstrap.md")
    print(f"Wrote {output_dir / 'property_ablation_bootstrap.csv'}")
    print(f"Wrote {table_dir / 'table_property_ablation_bootstrap.md'}")


if __name__ == "__main__":
    main()
