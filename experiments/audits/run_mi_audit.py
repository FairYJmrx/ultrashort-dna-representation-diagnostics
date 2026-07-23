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


def discretize(values: np.ndarray, n_bins: int = 8) -> np.ndarray:
    values = np.asarray(values, dtype=np.float64)
    if values.size == 0:
        return np.zeros(0, dtype=int)
    edges = np.quantile(values, np.linspace(0, 1, n_bins + 1))
    edges = np.unique(edges)
    if edges.size <= 2:
        return np.zeros_like(values, dtype=int)
    return np.digitize(values, edges[1:-1], right=True)


def mutual_information_bits(x: np.ndarray, y: np.ndarray) -> float:
    x = np.asarray(x, dtype=int)
    y = np.asarray(y, dtype=int)
    n = float(len(x))
    if n == 0:
        return float("nan")
    x_vals = np.unique(x)
    y_vals = np.unique(y)
    px = {int(v): float(np.mean(x == v)) for v in x_vals}
    py = {int(v): float(np.mean(y == v)) for v in y_vals}
    mi = 0.0
    for xv in x_vals:
        for yv in y_vals:
            pxy = float(np.mean((x == xv) & (y == yv)))
            if pxy <= 0:
                continue
            mi += pxy * np.log2(max(pxy / max(px[int(xv)] * py[int(yv)], 1e-12), 1e-12))
    return float(max(mi, 0.0))


def md_table(df: pd.DataFrame, floatfmt: str = ".4f") -> str:
    if df.empty:
        return "No rows."
    out = df.copy()
    for col in out.columns:
        if pd.api.types.is_float_dtype(out[col]) or pd.api.types.is_integer_dtype(out[col]):
            out[col] = out[col].map(lambda v: f"{float(v):{floatfmt}}" if pd.notna(v) else "")
    widths = {col: max(len(str(col)), max((len(str(v)) for v in out[col].tolist()), default=0)) for col in out.columns}
    header = "| " + " | ".join(f"{col:<{widths[col]}}" for col in out.columns) + " |"
    sep = "| " + " | ".join("-" * widths[col] for col in out.columns) + " |"
    rows = [
        "| " + " | ".join(f"{str(row[col]):<{widths[col]}}" for col in out.columns) + " |"
        for _, row in out.iterrows()
    ]
    return "\n".join([header, sep, *rows])


def run_mi_audit(pair_metrics: pd.DataFrame, delta_readout: pd.DataFrame, output_dir: Path) -> pd.DataFrame:
    pair_metrics = pair_metrics.copy()
    pair_metrics["source_length"] = pair_metrics["length"].astype(int)

    long_rows: list[dict[str, object]] = []
    for _, row in pair_metrics.iterrows():
        long_rows.append(
            {
                "representation": row["representation"],
                "source_length": int(row["source_length"]),
                "local_mode": row["local_mode"],
                "perturbation_label": 0,
                "distance": float(row["noise_l2"]),
            }
        )
        long_rows.append(
            {
                "representation": row["representation"],
                "source_length": int(row["source_length"]),
                "local_mode": row["local_mode"],
                "perturbation_label": 1,
                "distance": float(row["local_l2"]),
            }
        )
    long_df = pd.DataFrame(long_rows)

    rows: list[dict[str, object]] = []
    for rep, rep_df in long_df.groupby("representation", sort=True):
        pooled_bins = discretize(rep_df["distance"].to_numpy(), n_bins=8)
        pooled_mi = mutual_information_bits(pooled_bins, rep_df["perturbation_label"].to_numpy())
        pooled_perm = []
        rng = np.random.default_rng(20260624)
        for _ in range(200):
            perm = rng.permutation(rep_df["perturbation_label"].to_numpy())
            pooled_perm.append(mutual_information_bits(pooled_bins, perm))
        pooled_perm = np.asarray(pooled_perm, dtype=np.float64)
        pooled_p = float((1.0 + np.sum(pooled_perm >= pooled_mi)) / (1.0 + len(pooled_perm)))

        cmi_vals = []
        cmi_perm_vals = []
        for (length, mode), sub in rep_df.groupby(["source_length", "local_mode"], sort=True):
            if len(sub) < 16:
                continue
            bins = discretize(sub["distance"].to_numpy(), n_bins=8)
            label = sub["perturbation_label"].to_numpy()
            cmi_vals.append((len(sub) / len(rep_df)) * mutual_information_bits(bins, label))
            local_perm = []
            local_rng = np.random.default_rng(20260624 + int(length))
            for _ in range(100):
                perm = local_rng.permutation(label)
                local_perm.append((len(sub) / len(rep_df)) * mutual_information_bits(bins, perm))
            cmi_perm_vals.extend(local_perm)
        cmi = float(np.sum(cmi_vals))
        cmi_perm = np.asarray(cmi_perm_vals, dtype=np.float64) if cmi_perm_vals else np.asarray([float("nan")], dtype=np.float64)
        cmi_p = float((1.0 + np.sum(cmi_perm >= cmi)) / (1.0 + len(cmi_perm))) if np.isfinite(cmi).all() else float("nan")

        rows.append(
            {
                "representation": rep,
                "pooled_mi_bits": pooled_mi,
                "pooled_perm_p": pooled_p,
                "conditional_mi_bits": cmi,
                "conditional_perm_p": cmi_p,
                "n_rows": int(len(rep_df)),
                "mean_distance": float(rep_df["distance"].mean()),
                "median_distance": float(rep_df["distance"].median()),
            }
        )

    df = pd.DataFrame(rows)
    df.to_csv(output_dir / "mi_audit_summary.csv", index=False, encoding="utf-8-sig")
    lines = [
        "# Mutual-information audit",
        "",
        "This audit estimates a discretized mutual-information proxy from existing local-mutation pair metrics and delta-readout summaries. It is an empirical information-gain check, not a universal theorem.",
        "",
        md_table(df) if not df.empty else "No MI rows were produced.",
        "",
    ]
    (output_dir / "mi_audit_summary.md").write_text("\n".join(lines), encoding="utf-8")
    return df


def main() -> None:
    parser = argparse.ArgumentParser(description="Estimate MI-style information gain from existing local mutation results.")
    parser.add_argument("--pair-metrics", default=str(PROJECT_ROOT / "results" / "stage3" / "local_mutation_sensitivity" / "local_mutation_pair_metrics.csv"))
    parser.add_argument("--delta-readout", default=str(PROJECT_ROOT / "results" / "stage3" / "local_mutation_sensitivity" / "local_mutation_delta_readout.csv"))
    parser.add_argument("--output-dir", default=str(PROJECT_ROOT / "results" / "stage3" / "reviewer_response" / "mi_audit"))
    args = parser.parse_args()

    started = time.time()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    pair_metrics = pd.read_csv(args.pair_metrics)
    delta_readout = pd.read_csv(args.delta_readout)
    out = run_mi_audit(pair_metrics=pair_metrics, delta_readout=delta_readout, output_dir=output_dir)
    (output_dir / "mi_audit_run.json").write_text(
        json.dumps(
            {
                "elapsed_seconds": time.time() - started,
                "pair_metrics": args.pair_metrics,
                "delta_readout": args.delta_readout,
                "n_rows": int(len(out)),
            },
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    print(f"Wrote MI audit results to {output_dir}")


if __name__ == "__main__":
    main()

