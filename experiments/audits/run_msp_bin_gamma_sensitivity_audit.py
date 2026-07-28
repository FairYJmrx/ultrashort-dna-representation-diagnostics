
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler, normalize

def _find_project_root(start: Path) -> Path:
    for candidate in [start.parent, *start.parents]:
        if (candidate / "methods").is_dir() and (candidate / "configs").is_dir():
            return candidate
    raise RuntimeError("Could not locate the release repository root.")


PROJECT_ROOT = _find_project_root(Path(__file__).resolve())
sys.path.insert(0, str(PROJECT_ROOT))

from experiments.main.run_stage2_representation_grid import paired_subsets, parse_int_list, parse_csv_list, set_global_seed  # noqa: E402
from experiments.audits.run_p_msp_contribution_audit import evaluate_delta_readout  # noqa: E402
from methods.ck4p_msp import CK4PMSPConfig, build_ck4p_msp_features  # noqa: E402
from src.stage2_features import paired_retrieval_metrics  # noqa: E402

BINSETS = {
    "2": (2,),
    "2_3": (2, 3),
    "2_3_4": (2, 3, 4),
    "2_3_4_6": (2, 3, 4, 6),
}


def safe_norm(x: np.ndarray) -> np.ndarray:
    return normalize(np.nan_to_num(np.asarray(x, dtype=np.float64), nan=0.0, posinf=0.0, neginf=0.0), norm="l2", axis=1)


def build_rep(seqs: list[str], length: int, train_indices: list[int], bins: tuple[int, ...], gamma: float) -> tuple[np.ndarray, dict[str, int]]:
    del length
    config = CK4PMSPConfig(bins=bins, gamma=float(gamma))
    features = build_ck4p_msp_features(seqs, config=config, train_indices=train_indices)
    return features.matrix, {
        "k_dim": int(features.ck4.shape[1]),
        "p_dim": int(features.p.shape[1]),
        "m_dim": int(features.msp.shape[1]),
        "total_dim": int(features.matrix.shape[1]),
    }


def stability_audit(reads: pd.DataFrame, lengths: list[int], conditions: list[str], gammas: list[float], max_pairs: int, seed: int) -> pd.DataFrame:
    rows = []
    for length in lengths:
        for condition in [c for c in conditions if c != "clean"]:
            clean, pert = paired_subsets(reads, int(length), condition)
            if clean.empty:
                continue
            if max_pairs > 0 and len(clean) > max_pairs:
                keep = clean["clean_read_id"].drop_duplicates().sample(n=max_pairs, random_state=seed + int(length)).tolist()
                clean = clean[clean["clean_read_id"].isin(keep)].sort_values("clean_read_id").reset_index(drop=True)
                pert = pert[pert["clean_read_id"].isin(keep)].sort_values("clean_read_id").reset_index(drop=True)
            seqs = clean["sequence"].astype(str).tolist() + pert["sequence"].astype(str).tolist()
            train = list(range(len(clean)))
            for bin_name, bins in BINSETS.items():
                for gamma in gammas:
                    x, dims = build_rep(seqs, int(length), train, bins, gamma)
                    metrics = paired_retrieval_metrics(x[: len(clean)], x[len(clean):])
                    metrics.update({
                        "length": int(length),
                        "condition": condition,
                        "binset": bin_name,
                        "bins": "+".join(map(str, bins)),
                        "max_bin_count": int(max(bins)),
                        "gamma": float(gamma),
                        "n_pairs": int(len(clean)),
                        **dims,
                    })
                    rows.append(metrics)
    return pd.DataFrame(rows)


def local_audit(triplets: pd.DataFrame, lengths: list[int], gammas: list[float], max_triplets: int, seed: int, cv_folds: int) -> pd.DataFrame:
    rows = []
    triplets = triplets[triplets["source_length"].astype(int).isin(lengths)].copy()
    for (length, mode), subset in triplets.groupby(["source_length", "local_mode"], sort=True):
        sample_ids = sorted(subset["sample_id"].unique().tolist())
        if max_triplets > 0 and len(sample_ids) > max_triplets:
            rng = np.random.default_rng(seed + int(length) + len(str(mode)))
            sample_ids = sorted(rng.choice(sample_ids, size=max_triplets, replace=False).tolist())
        ordered = []
        for variant in ["clean", "random_noise", "local_property_shift"]:
            ordered.extend(subset[subset["variant"].eq(variant)].set_index("sample_id").loc[sample_ids]["sequence"].astype(str).tolist())
        n = len(sample_ids)
        train = list(range(n))
        for bin_name, bins in BINSETS.items():
            for gamma in gammas:
                x, dims = build_rep(ordered, int(length), train, bins, gamma)
                clean = x[:n]
                noise = x[n:2*n]
                local = x[2*n:3*n]
                noise_l2 = np.linalg.norm(safe_norm(clean) - safe_norm(noise), axis=1)
                local_l2 = np.linalg.norm(safe_norm(clean) - safe_norm(local), axis=1)
                base = {
                    "length": int(length),
                    "local_mode": mode,
                    "binset": bin_name,
                    "bins": "+".join(map(str, bins)),
                    "max_bin_count": int(max(bins)),
                    "gamma": float(gamma),
                    "n_triplets": int(n),
                    "noise_l2_mean": float(np.mean(noise_l2)),
                    "local_l2_mean": float(np.mean(local_l2)),
                    "local_minus_noise_l2_mean": float(np.mean(local_l2 - noise_l2)),
                    "selective_sensitivity_ratio_mean": float(np.mean(local_l2 / np.maximum(noise_l2, 1e-12))),
                    **dims,
                }
                for row in evaluate_delta_readout(
                    clean,
                    noise,
                    local,
                    sample_ids=sample_ids,
                    seed=seed + int(length),
                    cv_folds=cv_folds,
                ):
                    rows.append({**base, **row})
    return pd.DataFrame(rows)


def summarize(stability: pd.DataFrame, local: pd.DataFrame, out_dir: Path) -> dict[str, pd.DataFrame]:
    outputs = {}
    if not stability.empty:
        outputs["stability_summary"] = stability.groupby(["length", "binset", "gamma"], as_index=False).agg(
            n_cells=("paired_cosine_mean", "count"),
            paired_cosine_mean=("paired_cosine_mean", "mean"),
            l2_delta_mean=("l2_delta_mean", "mean"),
            retrieval_top1_mean=("retrieval_top1", "mean"),
            m_dim=("m_dim", "mean"),
        )
    if not local.empty:
        cv = local[local["split"].astype(str).str.contains("grouped_cv")].copy()
        outputs["delta_readout_summary"] = cv.groupby(["length", "binset", "gamma"], as_index=False).agg(
            n_cells=("macro_f1", "count"),
            macro_f1_mean=("macro_f1", "mean"),
            macro_f1_std_mean=("macro_f1_std", "mean"),
            local_minus_noise_l2_mean=("local_minus_noise_l2_mean", "mean"),
            selective_sensitivity_ratio_mean=("selective_sensitivity_ratio_mean", "mean"),
            m_dim=("m_dim", "mean"),
        )
    for name, df in outputs.items():
        df.to_csv(out_dir / f"{name}.csv", index=False, encoding="utf-8-sig")
    return outputs


def plot(outputs: dict[str, pd.DataFrame], out_dir: Path) -> None:
    plt.rcParams.update({
        "font.family": "Arial",
        "font.size": 8,
        "axes.linewidth": 0.6,
        "svg.fonttype": "none",
        "pdf.fonttype": 42,
    })
    fig = plt.figure(figsize=(7.0, 4.7), constrained_layout=True)
    gs = fig.add_gridspec(2, 2, height_ratios=[1.0, 1.05])
    axes = [fig.add_subplot(gs[0, 0]), fig.add_subplot(gs[0, 1]), fig.add_subplot(gs[1, :])]
    colors = {"2": "#4C78A8", "2_3": "#59A14F", "2_3_4": "#F2A541", "2_3_4_6": "#E45756"}
    stab = outputs.get("stability_summary", pd.DataFrame())
    read = outputs.get("delta_readout_summary", pd.DataFrame())
    for ax, length in zip(axes[:2], [69, 75]):
        sub = stab[stab["length"].eq(length)] if not stab.empty else pd.DataFrame()
        if sub.empty:
            ax.axis("off")
            continue
        for binset, g in sub.groupby("binset"):
            g = g.sort_values("gamma")
            ax.plot(g["gamma"], g["l2_delta_mean"], marker="o", linewidth=1.0, markersize=3, label=binset.replace("_", "+"), color=colors.get(binset, "0.5"))
        ax.set_title(f"{length} bp stability", loc="left", fontweight="bold")
        ax.set_xlabel("MSP weight gamma")
        ax.set_ylabel("Mean paired L2 drift")
        ax.grid(axis="y", color="0.9", linewidth=0.5)
    ax = axes[2]
    if not read.empty:
        sub = read[read["length"].isin([69, 100, 150])]
        pivot = sub.groupby(["binset", "gamma"], as_index=False)["macro_f1_mean"].mean()
        for binset, g in pivot.groupby("binset"):
            g = g.sort_values("gamma")
            ax.plot(g["gamma"], g["macro_f1_mean"], marker="o", linewidth=1.0, markersize=3, label=binset.replace("_", "+"), color=colors.get(binset, "0.5"))
        ax.set_title("Delta-readout", loc="left", fontweight="bold")
        ax.set_xlabel("MSP weight gamma")
        ax.set_ylabel("Macro-F1")
        ax.set_ylim(0.65, 1.02)
        ax.grid(axis="y", color="0.9", linewidth=0.5)
        ax.legend(frameon=False, fontsize=6.2, ncol=4, loc="upper center", bbox_to_anchor=(0.5, -0.20))
    else:
        ax.axis("off")
    for ax in axes:
        if ax.has_data():
            ax.spines["top"].set_visible(False)
            ax.spines["right"].set_visible(False)
    fig.suptitle("Supplementary Figure S6 | MSP binset and gamma-sensitivity audit", x=0.02, ha="left", fontsize=9.2, fontweight="bold")
    for ext in ("png", "pdf", "svg"):
        fig.savefig(out_dir / f"msp_bin_gamma_sensitivity.{ext}", dpi=450 if ext == "png" else None, bbox_inches="tight")
    plt.close(fig)


def write_md(outputs: dict[str, pd.DataFrame], out_dir: Path, meta: dict[str, object]) -> None:
    lines = [
        "# MSP bin/gamma sensitivity audit",
        "",
        "Purpose: test whether static MSP weighting is catastrophically sensitive to fine binning or to the chosen MSP weight gamma in short reads. This is not a dynamic-weighting method benchmark.",
        "",
        "## Run metadata",
        pd.DataFrame([meta]).to_markdown(index=False),
        "",
    ]
    for title, key in [("Stability", "stability_summary"), ("Delta-readout", "delta_readout_summary")]:
        df = outputs.get(key, pd.DataFrame())
        if not df.empty:
            lines += [f"## {title}", "", df.to_markdown(index=False, floatfmt=".4f"), ""]
    (out_dir / "msp_bin_gamma_sensitivity_summary.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Lightweight MSP bin/gamma sensitivity audit.")
    parser.add_argument("--reads-csv", default=str(PROJECT_ROOT / "results" / "stage3" / "contract_v2" / "compact_baselines" / "stage3_compact_baseline_reads.csv"))
    parser.add_argument("--triplets-csv", default=str(PROJECT_ROOT / "results" / "stage3" / "contract_v2" / "local_mutation_sensitivity" / "local_mutation_triplets.csv"))
    parser.add_argument("--output-dir", default=str(PROJECT_ROOT / "results" / "stage3" / "contract_v2" / "msp_bin_gamma_sensitivity"))
    parser.add_argument("--stability-lengths", default="69,75")
    parser.add_argument("--local-lengths", default="69,100,150")
    parser.add_argument("--conditions", default="substitution_1pct,N_3pct,substitution_1pct_N_3pct,local_mismatch_6bp,short_indel")
    parser.add_argument("--gammas", default="0,0.25,0.5,1,2")
    parser.add_argument("--max-pairs", type=int, default=250)
    parser.add_argument("--max-triplets", type=int, default=250)
    parser.add_argument("--cv-folds", type=int, default=5)
    parser.add_argument("--seed", type=int, default=20260625)
    args = parser.parse_args()
    started = time.time()
    set_global_seed(args.seed)
    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    reads = pd.read_csv(args.reads_csv)
    triplets = pd.read_csv(args.triplets_csv)
    gammas = [float(x) for x in parse_csv_list(args.gammas)]
    stability = stability_audit(reads, parse_int_list(args.stability_lengths), parse_csv_list(args.conditions), gammas, args.max_pairs, args.seed)
    local = local_audit(triplets, parse_int_list(args.local_lengths), gammas, args.max_triplets, args.seed, args.cv_folds)
    stability.to_csv(out_dir / "msp_bin_gamma_stability.csv", index=False, encoding="utf-8-sig")
    local.to_csv(out_dir / "msp_bin_gamma_delta_readout.csv", index=False, encoding="utf-8-sig")
    outputs = summarize(stability, local, out_dir)
    meta = {
        "elapsed_seconds": round(time.time() - started, 3),
        "stability_lengths": args.stability_lengths,
        "local_lengths": args.local_lengths,
        "gammas": args.gammas,
        "max_pairs": args.max_pairs,
        "max_triplets": args.max_triplets,
        "seed": args.seed,
    }
    write_md(outputs, out_dir, meta)
    plot(outputs, out_dir)
    (out_dir / "msp_bin_gamma_sensitivity_run.json").write_text(json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote MSP bin/gamma sensitivity audit to {out_dir}")


if __name__ == "__main__":
    main()

