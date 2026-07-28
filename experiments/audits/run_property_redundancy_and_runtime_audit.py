from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import sparse
from sklearn.cross_decomposition import CCA
from sklearn.decomposition import PCA
from sklearn.preprocessing import normalize

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
from experiments.main.run_stage2_representation_grid import parse_int_list, set_global_seed  # noqa: E402
from methods.ck4p_msp import build_ck4p_msp_features  # noqa: E402


REPRESENTATIONS = [
    "ck4",
    "ck4_p",
    "ck4p_msp",
    "hash_k15_d222",
    "minhash_k15_s222",
    "rp_ck15_d222",
]

REP_LABELS = {
    "ck4": "CK4",
    "ck4_p": "CK4+P",
    "ck4p_msp": "CK4P-MSP",
    "hash_k15_d222": "Hashed k=15, d=222",
    "minhash_k15_s222": "MinHash k=15, s=222",
    "rp_ck15_d222": "CK15 random projection, d=222",
}


def safe_norm(x: np.ndarray) -> np.ndarray:
    return normalize(np.nan_to_num(np.asarray(x, dtype=np.float64), nan=0.0, posinf=0.0, neginf=0.0), norm="l2", axis=1)


def sample_clean_reads(reads: pd.DataFrame, lengths: list[int], max_per_length: int, seed: int) -> pd.DataFrame:
    clean = reads[(reads["condition"].eq("clean")) & (reads["source_length"].astype(int).isin(lengths))].copy()
    parts = []
    for length, group in clean.groupby("source_length", sort=True):
        n = min(max_per_length, len(group))
        parts.append(group.sample(n=n, random_state=seed + int(length)) if n < len(group) else group)
    return pd.concat(parts, ignore_index=True)


def redundancy_audit(sample: pd.DataFrame, seed: int, max_cca_components: int) -> tuple[pd.DataFrame, pd.DataFrame]:
    rows = []
    details = []
    for length, group in sample.groupby("source_length", sort=True):
        seqs = group["sequence"].astype(str).tolist()
        train = list(range(len(seqs)))
        features = build_ck4p_msp_features(seqs, train_indices=train)
        p, m = features.p, features.msp
        p = safe_norm(p)
        m = safe_norm(m)

        n_components = int(min(max_cca_components, p.shape[1], m.shape[1], len(seqs) - 1))
        p_rank = int(np.linalg.matrix_rank(p))
        m_rank = int(np.linalg.matrix_rank(m))
        pca_p = PCA(n_components=min(p.shape[1], len(seqs) - 1), random_state=seed).fit(p)
        pca_m = PCA(n_components=min(m.shape[1], len(seqs) - 1), random_state=seed).fit(m)
        p_pc1 = pca_p.transform(p)[:, 0]
        m_pc1 = pca_m.transform(m)[:, 0]
        pc1_corr = float(np.corrcoef(p_pc1, m_pc1)[0, 1])

        cca_corrs = []
        if n_components >= 1:
            cca = CCA(n_components=n_components, max_iter=2000)
            p_c, m_c = cca.fit_transform(p, m)
            for idx in range(n_components):
                corr = np.corrcoef(p_c[:, idx], m_c[:, idx])[0, 1]
                if np.isfinite(corr):
                    cca_corrs.append(float(corr))
                    details.append(
                        {
                            "length": int(length),
                            "component": idx + 1,
                            "canonical_correlation": float(corr),
                        }
                    )

        # Row-wise cosine between global P and a PCA-compressed MSP view with
        # equal dimensionality to P. This is descriptive, not a formal
        # orthogonality proof.
        m_to_p = PCA(n_components=min(p.shape[1], m.shape[1], len(seqs) - 1), random_state=seed).fit_transform(m)
        p_trim = p[:, : m_to_p.shape[1]]
        row_cos = np.sum(safe_norm(p_trim) * safe_norm(m_to_p), axis=1)

        rows.append(
            {
                "length": int(length),
                "n_reads": int(len(seqs)),
                "p_dim": int(p.shape[1]),
                "msp_dim": int(m.shape[1]),
                "p_rank": p_rank,
                "msp_rank": m_rank,
                "pc1_corr_abs": abs(pc1_corr),
                "cca1_abs": abs(cca_corrs[0]) if cca_corrs else np.nan,
                "cca_mean_abs": float(np.mean(np.abs(cca_corrs))) if cca_corrs else np.nan,
                "row_cosine_median_abs": float(np.median(np.abs(row_cos))),
                "row_cosine_p95_abs": float(np.quantile(np.abs(row_cos), 0.95)),
            }
        )
    return pd.DataFrame(rows), pd.DataFrame(details)


def build_representation_timed(seqs: list[str], length: int, representation: str, train_indices: list[int], seed: int, repeats: int) -> tuple[np.ndarray, int, list[float]]:
    durations = []
    x = None
    n_features = 0
    for rep_idx in range(repeats):
        started = time.perf_counter()
        if representation == "hash_k15_d222":
            x = hashed_kmer_matrix(seqs, k=15, n_features=222, canonical=True, signed=True)
            n_features = 222
        elif representation == "minhash_k15_s222":
            x = minhash_signatures(seqs, k=15, sketch_size=222, canonical=True, seed=seed + rep_idx)
            n_features = 222
        elif representation == "rp_ck15_d222":
            x, n_features = random_projection_kmer_matrix(seqs, train_indices=train_indices, k=15, n_features=222, seed=seed + rep_idx)
        else:
            if representation == "ck4p_msp":
                x = build_ck4p_msp_features(seqs, train_indices=train_indices).matrix
            elif representation == "ck4":
                x = build_ck4p_msp_features(seqs, train_indices=train_indices).ck4
            elif representation == "ck4_p":
                features = build_ck4p_msp_features(seqs, train_indices=train_indices)
                x = safe_norm(np.hstack([features.ck4, features.p]))
            else:
                raise ValueError(f"Unsupported runtime representation: {representation}")
            x = safe_norm(x)
            n_features = int(x.shape[1])
        durations.append(time.perf_counter() - started)
    assert x is not None
    return np.asarray(x), int(n_features), durations


def matrix_density(x: np.ndarray) -> float:
    if sparse.issparse(x):
        return float(x.nnz / (x.shape[0] * x.shape[1]))
    arr = np.asarray(x)
    return float(np.count_nonzero(arr) / arr.size) if arr.size else 0.0


def runtime_audit(sample: pd.DataFrame, seed: int, repeats: int) -> pd.DataFrame:
    rows = []
    for length, group in sample.groupby("source_length", sort=True):
        seqs = group["sequence"].astype(str).tolist()
        train = list(range(len(seqs)))
        for representation in REPRESENTATIONS:
            x, n_features, durations = build_representation_timed(
                seqs=seqs,
                length=int(length),
                representation=representation,
                train_indices=train,
                seed=seed + int(length),
                repeats=repeats,
            )
            seconds = np.asarray(durations, dtype=np.float64)
            rows.append(
                {
                    "length": int(length),
                    "representation": representation,
                    "representation_label": REP_LABELS[representation],
                    "n_reads": int(len(seqs)),
                    "n_features": int(n_features),
                    "repeats": int(repeats),
                    "seconds_mean": float(seconds.mean()),
                    "seconds_median": float(np.median(seconds)),
                    "ms_per_10k_reads": float(seconds.mean() / max(len(seqs), 1) * 10000 * 1000),
                    "microseconds_per_read": float(seconds.mean() / max(len(seqs), 1) * 1_000_000),
                    "density": matrix_density(x),
                }
            )
    return pd.DataFrame(rows)


def summarize(redundancy: pd.DataFrame, cca_detail: pd.DataFrame, runtime: pd.DataFrame, out_dir: Path, meta: dict[str, object]) -> None:
    redundancy.to_csv(out_dir / "property_msp_redundancy_summary.csv", index=False, encoding="utf-8-sig")
    cca_detail.to_csv(out_dir / "property_msp_cca_detail.csv", index=False, encoding="utf-8-sig")
    runtime.to_csv(out_dir / "feature_runtime_summary.csv", index=False, encoding="utf-8-sig")

    runtime_overall = (
        runtime.groupby(["representation", "representation_label"], as_index=False)
        .agg(
            n_lengths=("length", "count"),
            median_features=("n_features", "median"),
            ms_per_10k_reads=("ms_per_10k_reads", "mean"),
            microseconds_per_read=("microseconds_per_read", "mean"),
            density=("density", "mean"),
        )
        .sort_values("ms_per_10k_reads")
    )
    runtime_overall.to_csv(out_dir / "feature_runtime_overall.csv", index=False, encoding="utf-8-sig")

    lines = [
        "# Property redundancy and runtime audit",
        "",
        "This lightweight audit addresses two reviewer-risk questions: whether global P and MSP channels are assumed to be orthogonal, and what feature-extraction cost is paid for CK4P-MSP relative to identity and high-k compressed baselines.",
        "",
        "## Run metadata",
        pd.DataFrame([meta]).to_markdown(index=False),
        "",
        "## P/MSP redundancy summary",
        redundancy.to_markdown(index=False, floatfmt=".4f"),
        "",
        "## Feature runtime summary",
        runtime_overall.to_markdown(index=False, floatfmt=".4f"),
        "",
    ]
    (out_dir / "property_redundancy_runtime_summary.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run P/MSP redundancy and feature runtime audit.")
    parser.add_argument("--input", default=str(PROJECT_ROOT / "results" / "stage3" / "contract_v2" / "compact_baselines" / "stage3_compact_baseline_reads.csv"))
    parser.add_argument("--output-dir", default=str(PROJECT_ROOT / "results" / "stage3" / "contract_v2" / "property_redundancy_runtime"))
    parser.add_argument("--lengths", default="69,75,100,150")
    parser.add_argument("--max-per-length", type=int, default=400)
    parser.add_argument("--runtime-repeats", type=int, default=5)
    parser.add_argument("--max-cca-components", type=int, default=5)
    parser.add_argument("--seed", type=int, default=20260625)
    args = parser.parse_args()

    started = time.time()
    set_global_seed(args.seed)
    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    reads = pd.read_csv(args.input)
    lengths = parse_int_list(args.lengths)
    sample = sample_clean_reads(reads, lengths=lengths, max_per_length=args.max_per_length, seed=args.seed)
    sample.to_csv(out_dir / "audit_clean_read_sample.csv", index=False, encoding="utf-8-sig")
    redundancy, cca_detail = redundancy_audit(sample, seed=args.seed, max_cca_components=args.max_cca_components)
    runtime = runtime_audit(sample, seed=args.seed, repeats=args.runtime_repeats)
    meta = {
        "elapsed_seconds": round(time.time() - started, 3),
        "input": args.input,
        "lengths": lengths,
        "n_sampled_reads": int(len(sample)),
        "max_per_length": int(args.max_per_length),
        "runtime_repeats": int(args.runtime_repeats),
        "max_cca_components": int(args.max_cca_components),
    }
    (out_dir / "property_redundancy_runtime_run.json").write_text(json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8")
    summarize(redundancy, cca_detail, runtime, out_dir, meta)
    print(f"Wrote property redundancy/runtime audit to {out_dir}")


if __name__ == "__main__":
    main()

