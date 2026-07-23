
from __future__ import annotations

import argparse
import json
import math
import sys
import time
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score
from sklearn.model_selection import StratifiedKFold, train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler, normalize

def _find_project_root(start: Path) -> Path:
    for candidate in [start.parent, *start.parents]:
        if (candidate / "methods").is_dir() and (candidate / "configs").is_dir():
            return candidate
    raise RuntimeError("Could not locate the release repository root.")


PROJECT_ROOT = _find_project_root(Path(__file__).resolve())
sys.path.insert(0, str(PROJECT_ROOT))

from experiments.main.run_stage2_representation_grid import paired_subsets, parse_csv_list, parse_int_list, set_global_seed  # noqa: E402
from scripts.run_mi_audit import discretize, mutual_information_bits  # noqa: E402
from src.stage2_features import build_feature_matrix, paired_retrieval_metrics  # noqa: E402

REP_LABELS = {
    "ck4": "CK4",
    "ck4p_msp": "CK4P-MSP",
    "ck4_permuted_pmsp": "CK4 + permuted P/MSP",
    "ck4_gaussian_pmsp": "CK4 + Gaussian P/MSP",
}


def _safe_norm(x: np.ndarray) -> np.ndarray:
    return normalize(np.nan_to_num(np.asarray(x, dtype=np.float64), nan=0.0, posinf=0.0, neginf=0.0), norm="l2", axis=1)


def build_blocks(sequences: list[str], length: int, train_indices: list[int]) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    k, _ = build_feature_matrix(sequences, "ckmer4_count_l2", length=length, train_indices=train_indices)
    p, _ = build_feature_matrix(sequences, "property_l2", length=length, train_indices=train_indices)
    msp, _ = build_feature_matrix(sequences, "property_multiscale_mean_l2", length=length, train_indices=train_indices)
    return np.asarray(k, dtype=np.float64), np.asarray(p, dtype=np.float64), np.asarray(msp, dtype=np.float64)


def assemble_representations(k: np.ndarray, p: np.ndarray, msp: np.ndarray, rng: np.random.Generator) -> dict[str, np.ndarray]:
    pmsp = np.hstack([p, msp])
    perm_idx = rng.permutation(pmsp.shape[0])
    col_mean = pmsp.mean(axis=0)
    col_std = pmsp.std(axis=0)
    col_std = np.where(col_std > 1e-12, col_std, 1.0)
    gaussian = rng.normal(loc=col_mean, scale=col_std, size=pmsp.shape)
    return {
        "ck4": _safe_norm(k),
        "ck4p_msp": _safe_norm(np.hstack([k, p, msp])),
        "ck4_permuted_pmsp": _safe_norm(np.hstack([k, pmsp[perm_idx]])),
        "ck4_gaussian_pmsp": _safe_norm(np.hstack([k, gaussian])),
    }


def stability_counterfactual(reads: pd.DataFrame, lengths: list[int], conditions: list[str], max_pairs: int, seed: int) -> tuple[pd.DataFrame, pd.DataFrame]:
    metric_rows: list[dict[str, object]] = []
    block_rows: list[dict[str, object]] = []
    for length in lengths:
        for condition in [c for c in conditions if c != "clean"]:
            clean, pert = paired_subsets(reads, length, condition)
            if clean.empty:
                continue
            if max_pairs > 0 and len(clean) > max_pairs:
                keep = clean["clean_read_id"].drop_duplicates().sample(n=max_pairs, random_state=seed + length).tolist()
                clean = clean[clean["clean_read_id"].isin(keep)].sort_values("clean_read_id").reset_index(drop=True)
                pert = pert[pert["clean_read_id"].isin(keep)].sort_values("clean_read_id").reset_index(drop=True)
            sequences = clean["sequence"].astype(str).tolist() + pert["sequence"].astype(str).tolist()
            train_indices = list(range(len(clean)))
            k, p, msp = build_blocks(sequences, int(length), train_indices)
            rng = np.random.default_rng(seed + 1000 * int(length) + len(condition))
            reps = assemble_representations(k, p, msp, rng)
            for rep_name, x in reps.items():
                metrics = paired_retrieval_metrics(x[: len(clean)], x[len(clean) :])
                metrics.update({
                    "length": int(length),
                    "condition": condition,
                    "representation": rep_name,
                    "representation_label": REP_LABELS[rep_name],
                    "n_pairs": int(len(clean)),
                    "n_features": int(x.shape[1]),
                })
                metric_rows.append(metrics)
            for block_name, block in [("identity_CK4", k), ("global_property_P", p), ("multiscale_property_MSP", msp)]:
                clean_b = _safe_norm(block[: len(clean)])
                pert_b = _safe_norm(block[len(clean) :])
                l2 = np.linalg.norm(clean_b - pert_b, axis=1)
                cos = np.sum(clean_b * pert_b, axis=1)
                block_rows.append({
                    "length": int(length),
                    "condition": condition,
                    "block": block_name,
                    "n_pairs": int(len(clean)),
                    "n_features": int(block.shape[1]),
                    "l2_delta_mean": float(np.mean(l2)),
                    "l2_delta_p95": float(np.quantile(l2, 0.95)),
                    "paired_cosine_mean": float(np.mean(cos)),
                    "paired_cosine_p05": float(np.quantile(cos, 0.05)),
                })
    return pd.DataFrame(metric_rows), pd.DataFrame(block_rows)


def classifier_registry(seed: int) -> dict[str, object]:
    return {"logistic": make_pipeline(StandardScaler(), LogisticRegression(max_iter=5000, random_state=seed))}


def evaluate_delta_readout(clean: np.ndarray, noise: np.ndarray, local: np.ndarray, seed: int, cv_folds: int) -> list[dict[str, object]]:
    x_delta = np.vstack([np.abs(noise - clean), np.abs(local - clean)])
    y = np.asarray([0] * clean.shape[0] + [1] * clean.shape[0])
    rows: list[dict[str, object]] = []
    train_idx, test_idx = train_test_split(np.arange(len(y)), test_size=0.3, random_state=seed, stratify=y)
    for clf_name, clf in classifier_registry(seed).items():
        clf.fit(x_delta[train_idx], y[train_idx])
        pred = clf.predict(x_delta[test_idx])
        rows.append({"split": "holdout", "classifier": clf_name, "accuracy": float(accuracy_score(y[test_idx], pred)), "macro_f1": float(f1_score(y[test_idx], pred, average="macro", zero_division=0))})
    if cv_folds > 1:
        skf = StratifiedKFold(n_splits=cv_folds, shuffle=True, random_state=seed)
        for clf_name in classifier_registry(seed):
            acc, f1 = [], []
            for cv_train, cv_test in skf.split(x_delta, y):
                clf = classifier_registry(seed)[clf_name]
                clf.fit(x_delta[cv_train], y[cv_train])
                pred = clf.predict(x_delta[cv_test])
                acc.append(float(accuracy_score(y[cv_test], pred)))
                f1.append(float(f1_score(y[cv_test], pred, average="macro", zero_division=0)))
            rows.append({"split": f"{cv_folds}fold_cv", "classifier": clf_name, "accuracy": float(np.mean(acc)), "accuracy_std": float(np.std(acc)), "macro_f1": float(np.mean(f1)), "macro_f1_std": float(np.std(f1))})
    return rows


def mi_from_distances(noise_l2: np.ndarray, local_l2: np.ndarray, seed: int) -> dict[str, float]:
    distance = np.concatenate([noise_l2, local_l2])
    label = np.asarray([0] * len(noise_l2) + [1] * len(local_l2), dtype=int)
    bins = discretize(distance, n_bins=8)
    mi = mutual_information_bits(bins, label)
    rng = np.random.default_rng(seed)
    perm = np.asarray([mutual_information_bits(bins, rng.permutation(label)) for _ in range(200)], dtype=np.float64)
    p = float((1 + np.sum(perm >= mi)) / (1 + len(perm)))
    return {"mi_bits": float(mi), "mi_perm_p": p, "mi_perm_mean": float(np.mean(perm))}



def joint_discretize(arrays: list[np.ndarray], n_bins: int = 6) -> np.ndarray:
    codes = None
    multiplier = 1
    for arr in arrays:
        b = discretize(np.asarray(arr, dtype=np.float64), n_bins=n_bins)
        if codes is None:
            codes = b.astype(int)
        else:
            codes = codes + multiplier * b.astype(int)
        multiplier *= max(n_bins, int(b.max()) + 1 if b.size else n_bins)
    return np.asarray(codes if codes is not None else np.zeros(0, dtype=int), dtype=int)


def conditional_mutual_information_bits(x: np.ndarray, y: np.ndarray, z: np.ndarray) -> float:
    x = np.asarray(x, dtype=int)
    y = np.asarray(y, dtype=int)
    z = np.asarray(z, dtype=int)
    if len(x) == 0:
        return float("nan")
    total = float(len(x))
    out = 0.0
    for zv in np.unique(z):
        mask = z == zv
        if int(mask.sum()) < 8:
            continue
        out += (float(mask.sum()) / total) * mutual_information_bits(x[mask], y[mask])
    return float(max(out, 0.0))


def local_block_information(k: np.ndarray, p: np.ndarray, msp: np.ndarray, n: int, seed: int) -> dict[str, float]:
    clean_k, noise_k, local_k = _safe_norm(k[:n]), _safe_norm(k[n:2*n]), _safe_norm(k[2*n:3*n])
    clean_p, noise_p, local_p = _safe_norm(p[:n]), _safe_norm(p[n:2*n]), _safe_norm(p[2*n:3*n])
    clean_m, noise_m, local_m = _safe_norm(msp[:n]), _safe_norm(msp[n:2*n]), _safe_norm(msp[2*n:3*n])
    dk = np.concatenate([np.linalg.norm(clean_k - noise_k, axis=1), np.linalg.norm(clean_k - local_k, axis=1)])
    dp = np.concatenate([np.linalg.norm(clean_p - noise_p, axis=1), np.linalg.norm(clean_p - local_p, axis=1)])
    dm = np.concatenate([np.linalg.norm(clean_m - noise_m, axis=1), np.linalg.norm(clean_m - local_m, axis=1)])
    y = np.asarray([0] * n + [1] * n, dtype=int)
    k_bins = discretize(dk, n_bins=8)
    p_bins = discretize(dp, n_bins=8)
    m_bins = discretize(dm, n_bins=8)
    pm_bins = joint_discretize([dp, dm], n_bins=6)
    joint_bins = joint_discretize([dk, dp, dm], n_bins=5)
    ck4_mi = mutual_information_bits(k_bins, y)
    p_mi = mutual_information_bits(p_bins, y)
    msp_mi = mutual_information_bits(m_bins, y)
    pmsp_mi = mutual_information_bits(pm_bins, y)
    joint_mi = mutual_information_bits(joint_bins, y)
    cmi = conditional_mutual_information_bits(pm_bins, y, k_bins)
    rng = np.random.default_rng(seed)
    cmi_perm = []
    incr_perm = []
    for _ in range(200):
        perm_idx = rng.permutation(len(y))
        pm_perm = pm_bins[perm_idx]
        dp_perm = dp[perm_idx]
        dm_perm = dm[perm_idx]
        cmi_perm.append(conditional_mutual_information_bits(pm_perm, y, k_bins))
        perm_joint_bins = joint_discretize([dk, dp_perm, dm_perm], n_bins=5)
        incr_perm.append(max(mutual_information_bits(perm_joint_bins, y) - ck4_mi, 0.0))
    cmi_perm = np.asarray(cmi_perm, dtype=np.float64)
    incr = float(max(joint_mi - ck4_mi, 0.0))
    incr_perm = np.asarray(incr_perm, dtype=np.float64)
    return {
        "ck4_distance_mi_bits": float(ck4_mi),
        "p_distance_mi_bits": float(p_mi),
        "msp_distance_mi_bits": float(msp_mi),
        "pmsp_joint_mi_bits": float(pmsp_mi),
        "joint_ck4_pmsp_mi_bits": float(joint_mi),
        "pmsp_conditional_on_ck4_mi_bits": float(cmi),
        "joint_minus_ck4_mi_bits": incr,
        "pmsp_conditional_perm_p": float((1 + np.sum(cmi_perm >= cmi)) / (1 + len(cmi_perm))),
        "joint_minus_ck4_perm_p": float((1 + np.sum(incr_perm >= incr)) / (1 + len(incr_perm))),
    }


def local_counterfactual(triplets: pd.DataFrame, lengths: list[int], max_triplets: int, seed: int, cv_folds: int) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    pair_rows: list[dict[str, object]] = []
    readout_rows: list[dict[str, object]] = []
    mi_rows: list[dict[str, object]] = []
    conditional_rows: list[dict[str, object]] = []
    triplets = triplets[triplets["source_length"].astype(int).isin(lengths)].copy()
    for (length, mode), subset in triplets.groupby(["source_length", "local_mode"], sort=True):
        sample_ids = sorted(subset["sample_id"].unique().tolist())
        if max_triplets > 0 and len(sample_ids) > max_triplets:
            rng_ids = np.random.default_rng(seed + int(length) + len(str(mode)))
            sample_ids = sorted(rng_ids.choice(sample_ids, size=max_triplets, replace=False).tolist())
        ordered: list[str] = []
        for variant in ["clean", "random_noise", "local_property_shift"]:
            variant_df = subset[subset["variant"].eq(variant)].set_index("sample_id").loc[sample_ids]
            ordered.extend(variant_df["sequence"].astype(str).tolist())
        n = len(sample_ids)
        train_indices = list(range(n))
        k, p, msp = build_blocks(ordered, int(length), train_indices)
        rng = np.random.default_rng(seed + 10000 + int(length) + len(str(mode)))
        reps = assemble_representations(k, p, msp, rng)
        cmi = local_block_information(k, p, msp, n, seed + 30000 + int(length) + len(str(mode)))
        cmi.update({"length": int(length), "local_mode": mode, "n_triplets": int(n)})
        conditional_rows.append(cmi)
        for rep_name, x in reps.items():
            clean = x[:n]
            noise = x[n : 2 * n]
            local = x[2 * n : 3 * n]
            noise_l2 = np.linalg.norm(_safe_norm(clean) - _safe_norm(noise), axis=1)
            local_l2 = np.linalg.norm(_safe_norm(clean) - _safe_norm(local), axis=1)
            ratio = local_l2 / np.maximum(noise_l2, 1e-12)
            for i, sample_id in enumerate(sample_ids):
                pair_rows.append({
                    "sample_id": sample_id,
                    "length": int(length),
                    "local_mode": mode,
                    "representation": rep_name,
                    "representation_label": REP_LABELS[rep_name],
                    "noise_l2": float(noise_l2[i]),
                    "local_l2": float(local_l2[i]),
                    "local_minus_noise_l2": float(local_l2[i] - noise_l2[i]),
                    "selective_sensitivity_ratio": float(ratio[i]),
                    "n_features": int(x.shape[1]),
                })
            mi = mi_from_distances(noise_l2, local_l2, seed + int(length))
            mi.update({
                "length": int(length),
                "local_mode": mode,
                "representation": rep_name,
                "representation_label": REP_LABELS[rep_name],
                "n_triplets": int(n),
            })
            mi_rows.append(mi)
            for row in evaluate_delta_readout(clean, noise, local, seed=seed + int(length), cv_folds=cv_folds):
                row.update({
                    "length": int(length),
                    "local_mode": mode,
                    "representation": rep_name,
                    "representation_label": REP_LABELS[rep_name],
                    "n_samples": int(2 * n),
                    "n_features": int(x.shape[1]),
                })
                readout_rows.append(row)
    return pd.DataFrame(pair_rows), pd.DataFrame(readout_rows), pd.DataFrame(mi_rows), pd.DataFrame(conditional_rows)


def reliability_audit(reads: pd.DataFrame, lengths: list[int], max_reads: int, seed: int, bootstrap: int) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    clean_reads = reads[reads["condition"].eq("clean")].copy()
    for length in lengths:
        sub = clean_reads[clean_reads["source_length"].astype(int).eq(int(length))].copy()
        if sub.empty:
            continue
        if max_reads > 0 and len(sub) > max_reads:
            sub = sub.sample(n=max_reads, random_state=seed + int(length))
        seqs = sub["sequence"].astype(str).tolist()
        train = list(range(len(seqs)))
        p, _ = build_feature_matrix(seqs, "property_l2", length=int(length), train_indices=train)
        msp, _ = build_feature_matrix(seqs, "property_multiscale_mean_l2", length=int(length), train_indices=train)
        for block_name, mat in [("global_property_P", p), ("multiscale_property_MSP", msp)]:
            mat = np.asarray(mat, dtype=np.float64)
            rng = np.random.default_rng(seed + int(length) + mat.shape[1])
            boot_means = []
            for _ in range(bootstrap):
                idx = rng.integers(0, mat.shape[0], size=mat.shape[0])
                boot_means.append(mat[idx].mean(axis=0))
            boot = np.vstack(boot_means)
            ci_width = np.quantile(boot, 0.975, axis=0) - np.quantile(boot, 0.025, axis=0)
            rows.append({
                "length": int(length),
                "block": block_name,
                "n_reads": int(len(seqs)),
                "n_features": int(mat.shape[1]),
                "mean_feature_sd": float(np.mean(np.std(mat, axis=0))),
                "median_feature_sd": float(np.median(np.std(mat, axis=0))),
                "mean_bootstrap_ci_width": float(np.mean(ci_width)),
                "median_bootstrap_ci_width": float(np.median(ci_width)),
            })
        for n_bins in (2, 3, 4, 6):
            edges = np.linspace(0, int(length), n_bins + 1)
            widths = [max(1, int(math.floor(r)) - int(math.floor(l))) for l, r in zip(edges[:-1], edges[1:])]
            min_bp = int(min(widths))
            median_bp = float(np.median(widths))
            rows.append({
                "length": int(length),
                "block": f"MSP_bin_scale_{n_bins}",
                "n_reads": int(len(seqs)),
                "n_features": int(n_bins * 5),
                "min_bin_bp": min_bp,
                "median_bin_bp": median_bp,
                "worst_case_binomial_se": float(math.sqrt(0.25 / min_bp)),
            })
    return pd.DataFrame(rows)


def aggregate_outputs(stability: pd.DataFrame, block: pd.DataFrame, local_pairs: pd.DataFrame, readout: pd.DataFrame, mi: pd.DataFrame, conditional_mi: pd.DataFrame, reliability: pd.DataFrame, out_dir: Path) -> dict[str, pd.DataFrame]:
    outputs: dict[str, pd.DataFrame] = {}
    if not stability.empty:
        outputs["stability_summary"] = stability.groupby(["representation", "representation_label"], as_index=False).agg(
            n_cells=("paired_cosine_mean", "count"),
            n_pairs_mean=("n_pairs", "mean"),
            paired_cosine_mean=("paired_cosine_mean", "mean"),
            l2_delta_mean=("l2_delta_mean", "mean"),
            retrieval_top1_mean=("retrieval_top1", "mean"),
            mean_pair_margin=("mean_pair_margin", "mean"),
        ).sort_values("paired_cosine_mean", ascending=False)
    if not block.empty:
        outputs["block_drift_summary"] = block.groupby("block", as_index=False).agg(
            n_cells=("l2_delta_mean", "count"),
            paired_cosine_mean=("paired_cosine_mean", "mean"),
            l2_delta_mean=("l2_delta_mean", "mean"),
            l2_delta_p95_mean=("l2_delta_p95", "mean"),
        ).sort_values("l2_delta_mean")
    if not local_pairs.empty:
        outputs["local_pair_summary"] = local_pairs.groupby(["representation", "representation_label"], as_index=False).agg(
            n_cells=("selective_sensitivity_ratio", "count"),
            noise_l2_mean=("noise_l2", "mean"),
            local_l2_mean=("local_l2", "mean"),
            local_minus_noise_l2_mean=("local_minus_noise_l2", "mean"),
            selective_sensitivity_ratio_mean=("selective_sensitivity_ratio", "mean"),
        ).sort_values("local_minus_noise_l2_mean", ascending=False)
    if not readout.empty:
        outputs["delta_readout_summary"] = readout[readout["split"].astype(str).str.contains("fold_cv")].groupby(["representation", "representation_label", "classifier"], as_index=False).agg(
            n_cells=("macro_f1", "count"),
            macro_f1_mean=("macro_f1", "mean"),
            macro_f1_std_mean=("macro_f1_std", "mean"),
            accuracy_mean=("accuracy", "mean"),
        ).sort_values("macro_f1_mean", ascending=False)
    if not mi.empty:
        outputs["mi_summary"] = mi.groupby(["representation", "representation_label"], as_index=False).agg(
            n_cells=("mi_bits", "count"),
            mi_bits_mean=("mi_bits", "mean"),
            mi_perm_p_median=("mi_perm_p", "median"),
            mi_perm_mean=("mi_perm_mean", "mean"),
        ).sort_values("mi_bits_mean", ascending=False)
    if not conditional_mi.empty:
        outputs["conditional_mi_summary"] = conditional_mi.agg({
            "ck4_distance_mi_bits": "mean",
            "p_distance_mi_bits": "mean",
            "msp_distance_mi_bits": "mean",
            "pmsp_joint_mi_bits": "mean",
            "joint_ck4_pmsp_mi_bits": "mean",
            "pmsp_conditional_on_ck4_mi_bits": "mean",
            "joint_minus_ck4_mi_bits": "mean",
            "pmsp_conditional_perm_p": "median",
            "joint_minus_ck4_perm_p": "median",
            "n_triplets": "mean",
        }).to_frame().T
    if not reliability.empty:
        outputs["reliability_summary"] = reliability.copy()
    for name, df in outputs.items():
        df.to_csv(out_dir / f"{name}.csv", index=False, encoding="utf-8-sig")
    return outputs


def write_summary(outputs: dict[str, pd.DataFrame], out_dir: Path, run_meta: dict[str, object]) -> None:
    lines = [
        "# P-channel counterfactual and reliability audit",
        "",
        "Purpose: test whether the P/MSP contribution remains sequence-linked after controlling for dimensionality and marginal scale. Permuted and Gaussian P/MSP blocks preserve extra dimensions but remove the biological sequence-to-feature mapping.",
        "",
        "This is empirical support for the diagnostic representation, not a proof that heterogeneous Euclidean distance is a universal biophysical metric.",
        "",
        "## Run metadata",
        "",
        pd.DataFrame([run_meta]).to_markdown(index=False),
        "",
    ]
    for title, key in [
        ("Stability counterfactual", "stability_summary"),
        ("Block-wise drift", "block_drift_summary"),
        ("Local mutation distance", "local_pair_summary"),
        ("Delta-readout", "delta_readout_summary"),
        ("Mutual information", "mi_summary"),
        ("Conditional block information", "conditional_mi_summary"),
        ("Pooled-feature reliability", "reliability_summary"),
    ]:
        if key in outputs and not outputs[key].empty:
            lines.extend([f"## {title}", "", outputs[key].to_markdown(index=False, floatfmt=".4f"), ""])
    (out_dir / "p_channel_counterfactual_summary.md").write_text("\n".join(lines), encoding="utf-8")


def plot_audit(outputs: dict[str, pd.DataFrame], out_dir: Path) -> None:
    plt.rcParams.update({
        "font.family": "Arial",
        "font.size": 8,
        "axes.linewidth": 0.6,
        "xtick.major.width": 0.6,
        "ytick.major.width": 0.6,
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
    })
    fig, axes = plt.subplots(2, 2, figsize=(7.2, 5.4), constrained_layout=True)
    palette = {"CK4": "#4C78A8", "CK4P-MSP": "#1B9E77", "CK4 + permuted P/MSP": "#E45756", "CK4 + Gaussian P/MSP": "#F2A541"}

    ax = axes[0, 0]
    stab = outputs.get("stability_summary", pd.DataFrame())
    if not stab.empty:
        stab = stab.sort_values("l2_delta_mean")
        ax.barh(stab["representation_label"], stab["l2_delta_mean"], color=[palette.get(v, "0.5") for v in stab["representation_label"]])
        ax.set_xlabel("Mean paired L2 drift")
        ax.set_title("A. Stability under matched dimensions", loc="left", fontweight="bold")
    else:
        ax.axis("off")

    ax = axes[0, 1]
    cmi = outputs.get("conditional_mi_summary", pd.DataFrame())
    mi = outputs.get("mi_summary", pd.DataFrame())
    readout = outputs.get("delta_readout_summary", pd.DataFrame())
    if not cmi.empty:
        vals = cmi.iloc[0]
        labels = ["CK4 distance", "P/MSP | CK4", "Joint increment"]
        heights = [vals.get("ck4_distance_mi_bits", 0.0), vals.get("pmsp_conditional_on_ck4_mi_bits", 0.0), vals.get("joint_minus_ck4_mi_bits", 0.0)]
        ax.barh(labels, heights, color=["#4C78A8", "#1B9E77", "#59A14F"])
        ax.set_xlabel("MI proxy (bits)")
        ax.set_title("B. Conditional P/MSP information", loc="left", fontweight="bold")
    elif not mi.empty:
        mi = mi.sort_values("mi_bits_mean", ascending=False)
        ax.barh(mi["representation_label"], mi["mi_bits_mean"], color=[palette.get(v, "0.5") for v in mi["representation_label"]])
        ax.set_xlabel("MI proxy (bits)")
        ax.set_title("B. Local perturbation information", loc="left", fontweight="bold")
        if not readout.empty:
            ax2 = ax.twiny()
            read = readout.set_index("representation_label").reindex(mi["representation_label"])
            y = np.arange(len(mi))
            ax2.plot(read["macro_f1_mean"], y, marker="o", color="black", linewidth=0.8, markersize=3)
            ax2.set_xlabel("Delta-readout F1")
            ax2.set_xlim(0, 1.05)
    else:
        ax.axis("off")

    ax = axes[1, 0]
    block = outputs.get("block_drift_summary", pd.DataFrame())
    if not block.empty:
        block = block.sort_values("l2_delta_mean")
        colors = ["#4C78A8", "#59A14F", "#B07AA1"][: len(block)]
        ax.barh(block["block"], block["l2_delta_mean"], color=colors)
        ax.set_xlabel("Mean within-block L2 drift")
        ax.set_title("C. Drift decomposed by block", loc="left", fontweight="bold")
    else:
        ax.axis("off")

    ax = axes[1, 1]
    rel = outputs.get("reliability_summary", pd.DataFrame())
    if not rel.empty:
        bin_df = rel[rel["block"].astype(str).str.startswith("MSP_bin_scale_")].copy()
        if not bin_df.empty:
            bin_df["n_bins"] = bin_df["block"].str.extract(r"(\d+)$").astype(int)
            for n_bins, sub in bin_df.groupby("n_bins"):
                sub = sub.sort_values("length")
                ax.plot(sub["length"], sub["worst_case_binomial_se"], marker="o", linewidth=1.0, markersize=3, label=f"{n_bins} bins")
            ax.legend(frameon=False, fontsize=7, ncol=2)
            ax.set_xlabel("Read length (bp)")
            ax.set_ylabel("Worst-case binomial SE")
            ax.set_title("D. Short-bin sampling bound", loc="left", fontweight="bold")
        else:
            ax.axis("off")
    else:
        ax.axis("off")

    for ax in axes.ravel():
        if ax.has_data():
            ax.spines["top"].set_visible(False)
            ax.spines["right"].set_visible(False)
            ax.grid(axis="x", color="0.9", linewidth=0.5)
    for ext in ("png", "pdf", "svg"):
        fig.savefig(out_dir / f"p_channel_counterfactual_audit.{ext}", dpi=450 if ext == "png" else None)
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run P-channel counterfactual, block drift, and short-read reliability audits.")
    parser.add_argument("--reads-csv", default=str(PROJECT_ROOT / "results" / "stage3" / "position_property_ablation" / "stage3_compact_baseline_reads.csv"))
    parser.add_argument("--triplets-csv", default=str(PROJECT_ROOT / "results" / "stage3" / "local_mutation_sensitivity" / "local_mutation_triplets.csv"))
    parser.add_argument("--output-dir", default=str(PROJECT_ROOT / "results" / "stage3" / "reviewer_response" / "p_channel_counterfactual_audit"))
    parser.add_argument("--lengths", default="69,75,100,150")
    parser.add_argument("--conditions", default="substitution_1pct,N_3pct,substitution_1pct_N_3pct,local_mismatch_6bp,short_indel")
    parser.add_argument("--max-pairs", type=int, default=250)
    parser.add_argument("--max-triplets", type=int, default=250)
    parser.add_argument("--max-reliability-reads", type=int, default=600)
    parser.add_argument("--bootstrap", type=int, default=200)
    parser.add_argument("--cv-folds", type=int, default=5)
    parser.add_argument("--seed", type=int, default=20260625)
    args = parser.parse_args()

    started = time.time()
    set_global_seed(args.seed)
    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    reads = pd.read_csv(args.reads_csv)
    triplets = pd.read_csv(args.triplets_csv)
    lengths = parse_int_list(args.lengths)
    conditions = parse_csv_list(args.conditions)

    stability, block = stability_counterfactual(reads, lengths, conditions, args.max_pairs, args.seed)
    local_pairs, readout, mi, conditional_mi = local_counterfactual(triplets, lengths, args.max_triplets, args.seed, args.cv_folds)
    reliability = reliability_audit(reads, lengths, args.max_reliability_reads, args.seed, args.bootstrap)

    raw_outputs = {
        "counterfactual_stability": stability,
        "blockwise_drift": block,
        "local_counterfactual_pairs": local_pairs,
        "local_counterfactual_delta_readout": readout,
        "local_counterfactual_mi": mi,
        "local_conditional_block_mi": conditional_mi,
        "pooled_feature_reliability": reliability,
    }
    for name, df in raw_outputs.items():
        df.to_csv(out_dir / f"{name}.csv", index=False, encoding="utf-8-sig")

    outputs = aggregate_outputs(stability, block, local_pairs, readout, mi, conditional_mi, reliability, out_dir)
    meta = {
        "elapsed_seconds": round(time.time() - started, 3),
        "reads_rows": int(len(reads)),
        "triplet_rows": int(len(triplets)),
        "lengths": args.lengths,
        "conditions": args.conditions,
        "max_pairs": int(args.max_pairs),
        "max_triplets": int(args.max_triplets),
        "seed": int(args.seed),
    }
    write_summary(outputs, out_dir, meta)
    plot_audit(outputs, out_dir)
    (out_dir / "p_channel_counterfactual_run.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote P-channel counterfactual audit to {out_dir}")


if __name__ == "__main__":
    main()

