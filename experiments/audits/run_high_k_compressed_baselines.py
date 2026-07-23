from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import sparse
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score
from sklearn.model_selection import train_test_split
from sklearn.neighbors import NearestCentroid
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import LabelEncoder, StandardScaler, normalize
from sklearn.random_projection import SparseRandomProjection

def _find_project_root(start: Path) -> Path:
    for candidate in [start.parent, *start.parents]:
        if (candidate / "methods").is_dir() and (candidate / "configs").is_dir():
            return candidate
    raise RuntimeError("Could not locate the release repository root.")


PROJECT_ROOT = _find_project_root(Path(__file__).resolve())
sys.path.insert(0, str(PROJECT_ROOT))

from experiments.main.run_stage2_representation_grid import balanced_sample, paired_subsets, parse_csv_list, parse_int_list, set_global_seed  # noqa: E402
from src.sequence_utils import kmer_tokens  # noqa: E402
from src.sklearn_features import build_kmer_matrix, transform_feature_matrix  # noqa: E402
from src.stage2_features import build_feature_matrix, paired_retrieval_metrics  # noqa: E402


REP_LABELS = {
    "ckmer4_count_l2": "CK4",
    "ckmer5_count_l2": "CK5",
    "ckmer4_property_l2": "CK4+P",
    "ck4p_msp": "CK4P-MSP",
    "hash_k15_d222": "Hashed k=15, d=222",
    "rp_ck15_d222": "CK15 random projection, d=222",
}


def _hash_int(text: str, digest_size: int = 8) -> int:
    return int.from_bytes(hashlib.blake2b(text.encode("utf-8"), digest_size=digest_size).digest(), "big", signed=False)


def hashed_kmer_matrix(sequences: list[str], k: int, n_features: int, canonical: bool = True, signed: bool = True) -> np.ndarray:
    rows, cols, data = [], [], []
    for row_idx, seq in enumerate(sequences):
        counts: dict[int, float] = {}
        for token in kmer_tokens(seq, k=k, canonical=canonical, ignore_n=True):
            h = _hash_int(token)
            col = h % n_features
            sign = -1.0 if signed and ((_hash_int("sign:" + token) % 2) == 1) else 1.0
            counts[col] = counts.get(col, 0.0) + sign
        for col, value in counts.items():
            rows.append(row_idx)
            cols.append(col)
            data.append(value)
    mat = sparse.csr_matrix((data, (rows, cols)), shape=(len(sequences), n_features), dtype=np.float64)
    return normalize(mat, norm="l2", axis=1).toarray()


def minhash_signatures(
    sequences: list[str],
    k: int,
    sketch_size: int,
    canonical: bool = True,
    seed: int = 0,
) -> np.ndarray:
    """Return MinHash signatures for collision-based Jaccard estimation.

    A MinHash signature is not treated as an L2 feature vector. Its intended
    statistic is the fraction of matching signature positions, which estimates
    Jaccard similarity between the underlying k-mer sets.
    """
    prime = np.uint64(18446744073709551557)
    rng = np.random.default_rng(seed)
    a = rng.integers(1, np.iinfo(np.uint64).max, size=sketch_size, dtype=np.uint64) | np.uint64(1)
    b = rng.integers(0, np.iinfo(np.uint64).max, size=sketch_size, dtype=np.uint64)
    rows: list[np.ndarray] = []
    for seq in sequences:
        tokens = kmer_tokens(seq, k=k, canonical=canonical, ignore_n=True)
        if not tokens:
            rows.append(np.full(sketch_size, prime, dtype=np.uint64))
            continue
        h = np.asarray([_hash_int(token) for token in sorted(set(tokens))], dtype=np.uint64)
        rows.append(((a[:, None] * h[None, :] + b[:, None]) % prime).min(axis=1))
    return np.vstack(rows)


def exact_jaccard(clean_sequence: str, perturbed_sequence: str, k: int) -> float:
    clean = set(kmer_tokens(clean_sequence, k=k, canonical=True, ignore_n=True))
    perturbed = set(kmer_tokens(perturbed_sequence, k=k, canonical=True, ignore_n=True))
    union = clean | perturbed
    return float(len(clean & perturbed) / len(union)) if union else 1.0


def random_projection_kmer_matrix(sequences: list[str], train_indices: list[int], k: int, n_features: int, seed: int) -> tuple[np.ndarray, int]:
    train_sequences = [sequences[idx] for idx in train_indices]
    _, vocabulary = build_kmer_matrix(train_sequences, k=k, canonical=True, vocabulary_mode="observed")
    counts, _ = build_kmer_matrix(sequences, k=k, canonical=True, vocabulary=vocabulary)
    counts, _ = transform_feature_matrix(counts, feature_type="count", normalization="l2", train_indices=train_indices)
    if counts.shape[1] <= 1:
        return normalize(counts, norm="l2", axis=1).toarray(), int(counts.shape[1])
    dim = min(n_features, counts.shape[1])
    projector = SparseRandomProjection(n_components=dim, random_state=seed, dense_output=True)
    projector.fit(counts[train_indices])
    x = projector.transform(counts)
    return normalize(np.nan_to_num(x, nan=0.0, posinf=0.0, neginf=0.0), norm="l2", axis=1), int(dim)


def build_named_features(sequences: list[str], length: int, train_indices: list[int], representation: str, seed: int, high_k: int, target_dim: int) -> tuple[np.ndarray, int, str]:
    if representation == "hash_k15_d222":
        x = hashed_kmer_matrix(sequences, k=high_k, n_features=target_dim, canonical=True, signed=True)
        return x, int(target_dim), REP_LABELS[representation]
    if representation == "rp_ck15_d222":
        x, dim = random_projection_kmer_matrix(sequences, train_indices=train_indices, k=high_k, n_features=target_dim, seed=seed)
        return x, dim, REP_LABELS[representation]
    x, info = build_feature_matrix(sequences, representation, length=length, train_indices=train_indices)
    x = normalize(np.nan_to_num(np.asarray(x, dtype=np.float64), nan=0.0, posinf=0.0, neginf=0.0), norm="l2", axis=1)
    return x, int(info.n_features), REP_LABELS.get(representation, representation)


def run_stability(reads: pd.DataFrame, lengths: list[int], conditions: list[str], representations: list[str], max_pairs: int, seed: int, high_k: int, target_dim: int) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
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
            for rep in representations:
                try:
                    x, n_features, label = build_named_features(sequences, int(length), train_indices, rep, seed + int(length), high_k, target_dim)
                    metrics = paired_retrieval_metrics(x[: len(clean)], x[len(clean) :])
                    metrics.update(
                        {
                            "length": int(length),
                            "condition": condition,
                            "representation": rep,
                            "representation_label": label,
                            "n_pairs": int(len(clean)),
                            "n_features": int(n_features),
                            "high_k": int(high_k) if rep in {"hash_k15_d222", "rp_ck15_d222"} else np.nan,
                            "target_dim": int(target_dim) if rep in {"hash_k15_d222", "rp_ck15_d222"} else np.nan,
                        }
                    )
                    rows.append(metrics)
                except Exception as exc:
                    rows.append({"length": int(length), "condition": condition, "representation": rep, "error": f"{type(exc).__name__}: {exc}"})
    return pd.DataFrame(rows)


def run_minhash_jaccard_audit(
    reads: pd.DataFrame,
    lengths: list[int],
    conditions: list[str],
    max_pairs: int,
    seed: int,
    high_k: int,
    sketch_size: int,
) -> pd.DataFrame:
    """Audit k=15 MinHash in its native collision/Jaccard geometry."""
    rows: list[dict[str, object]] = []
    for length in lengths:
        for condition in [c for c in conditions if c != "clean"]:
            clean, pert = paired_subsets(reads, length, condition)
            if clean.empty:
                continue
            if max_pairs > 0 and len(clean) > max_pairs:
                keep = clean["clean_read_id"].drop_duplicates().sample(n=max_pairs, random_state=seed + length).tolist()
                clean = clean[clean["clean_read_id"].isin(keep)].sort_values("clean_read_id").reset_index(drop=True)
                pert = pert[pert["clean_read_id"].isin(keep)].sort_values("clean_read_id").reset_index(drop=True)
            clean_sequences = clean["sequence"].astype(str).tolist()
            perturbed_sequences = pert["sequence"].astype(str).tolist()
            signatures = minhash_signatures(
                clean_sequences + perturbed_sequences,
                k=high_k,
                sketch_size=sketch_size,
                seed=seed + length,
            )
            n = len(clean_sequences)
            collision = np.mean(signatures[:n] == signatures[n:], axis=1)
            exact = np.asarray(
                [exact_jaccard(a, b, high_k) for a, b in zip(clean_sequences, perturbed_sequences)],
                dtype=np.float64,
            )
            rows.append(
                {
                    "length": int(length),
                    "condition": condition,
                    "representation": f"minhash_k{high_k}_s{sketch_size}",
                    "representation_label": f"MinHash k={high_k}, s={sketch_size}",
                    "n_pairs": int(n),
                    "sketch_size": int(sketch_size),
                    "minhash_jaccard_mean": float(np.mean(collision)),
                    "minhash_jaccard_sd": float(np.std(collision)),
                    "exact_jaccard_mean": float(np.mean(exact)),
                    "exact_jaccard_sd": float(np.std(exact)),
                    "mean_absolute_error": float(np.mean(np.abs(collision - exact))),
                }
            )
    return pd.DataFrame(rows)


def classifier_registry(seed: int) -> dict[str, object]:
    return {
        "nearest_centroid": NearestCentroid(),
        "logistic": make_pipeline(StandardScaler(), LogisticRegression(max_iter=4000, random_state=seed)),
    }


def evaluate_readout(subset: pd.DataFrame, representation: str, label_col: str, length: int, seed: int, classifiers: list[str], high_k: int, target_dim: int) -> list[dict[str, object]]:
    labels = subset[label_col].astype(str).to_numpy()
    unique, counts = np.unique(labels, return_counts=True)
    if len(unique) < 2 or np.min(counts) < 3:
        return [{"representation": representation, "classifier": "all", "error": "not enough labels"}]
    y = LabelEncoder().fit_transform(labels)
    idx = np.arange(len(y))
    train_idx, test_idx = train_test_split(idx, test_size=0.3, random_state=seed, stratify=y)
    x, n_features, label = build_named_features(
        subset["sequence"].astype(str).tolist(),
        int(length),
        train_idx.tolist(),
        representation,
        seed + int(length),
        high_k,
        target_dim,
    )
    rows: list[dict[str, object]] = []
    for clf_name in classifiers:
        model = classifier_registry(seed)[clf_name]
        try:
            model.fit(x[train_idx], y[train_idx])
            pred = model.predict(x[test_idx])
            rows.append(
                {
                    "representation": representation,
                    "representation_label": label,
                    "classifier": clf_name,
                    "n_samples": int(len(subset)),
                    "n_classes": int(len(unique)),
                    "n_features": int(n_features),
                    "accuracy": float(accuracy_score(y[test_idx], pred)),
                    "macro_f1": float(f1_score(y[test_idx], pred, average="macro", zero_division=0)),
                }
            )
        except Exception as exc:
            rows.append({"representation": representation, "classifier": clf_name, "error": f"{type(exc).__name__}: {exc}"})
    return rows


def run_readout(reads: pd.DataFrame, lengths: list[int], conditions: list[str], representations: list[str], classifiers: list[str], max_per_class: int, seed: int, high_k: int, target_dim: int) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for length in lengths:
        for condition in conditions:
            subset = reads[(reads["source_length"].eq(length)) & (reads["condition"].eq(condition))].copy()
            if subset.empty:
                continue
            for genus, genus_df in subset.groupby("genus"):
                for task, label_col in (("within_genus_species", "label"), ("target_background", "target_binary")):
                    if genus_df[label_col].nunique() < 2:
                        continue
                    sampled = balanced_sample(genus_df, label_col, max_per_class=max_per_class, seed=seed + int(length))
                    for rep in representations:
                        for row in evaluate_readout(sampled, rep, label_col, int(length), seed, classifiers, high_k, target_dim):
                            row.update({"task": task, "genus": genus, "length": int(length), "condition": condition, "label_col": label_col})
                            rows.append(row)
    return pd.DataFrame(rows)


def summarize(stability: pd.DataFrame, readout: pd.DataFrame, minhash: pd.DataFrame, out_dir: Path) -> None:
    lines = [
        "# High-k compressed k-mer baseline audit",
        "",
        "This audit compares CK4P-MSP with dimension-matched high-specificity k-mer vector controls. Hashing trick counts and sparse random projection are evaluated in vector geometry. MinHash is reported separately through its native signature-collision estimate of k-mer-set Jaccard similarity.",
        "",
    ]
    valid = stability[~stability.get("error", pd.Series(index=stability.index, dtype=object)).notna()].copy() if not stability.empty else pd.DataFrame()
    if not valid.empty:
        stab = (
            valid.groupby(["representation", "representation_label"], as_index=False)
            .agg(
                n_cells=("paired_cosine_mean", "count"),
                paired_cosine=("paired_cosine_mean", "mean"),
                l2_drift=("l2_delta_mean", "mean"),
                retrieval_top1=("retrieval_top1", "mean"),
                median_features=("n_features", "median"),
            )
            .sort_values(["paired_cosine", "l2_drift"], ascending=[False, True])
        )
        stab.to_csv(out_dir / "high_k_stability_summary.csv", index=False, encoding="utf-8-sig")
        lines.extend(["## Stability summary", "", stab.to_markdown(index=False, floatfmt=".3f"), ""])
    valid_r = readout.dropna(subset=["macro_f1"]).copy() if not readout.empty and "macro_f1" in readout else pd.DataFrame()
    if not valid_r.empty:
        read = (
            valid_r.groupby(["representation", "representation_label", "classifier"], as_index=False)
            .agg(
                n_cells=("macro_f1", "count"),
                macro_f1=("macro_f1", "mean"),
                accuracy=("accuracy", "mean"),
                median_features=("n_features", "median"),
            )
            .sort_values(["macro_f1", "accuracy"], ascending=False)
        )
        read.to_csv(out_dir / "high_k_readout_summary.csv", index=False, encoding="utf-8-sig")
        lines.extend(["## Readout summary", "", read.to_markdown(index=False, floatfmt=".3f"), ""])
    if not minhash.empty:
        minhash_summary = (
            minhash.groupby(["representation", "representation_label"], as_index=False)
            .agg(
                n_cells=("minhash_jaccard_mean", "count"),
                estimated_jaccard=("minhash_jaccard_mean", "mean"),
                exact_jaccard=("exact_jaccard_mean", "mean"),
                mean_absolute_error=("mean_absolute_error", "mean"),
            )
        )
        minhash_summary.to_csv(out_dir / "high_k_minhash_jaccard_summary.csv", index=False, encoding="utf-8-sig")
        lines.extend(["## Native MinHash Jaccard audit", "", minhash_summary.to_markdown(index=False, floatfmt=".3f"), ""])
    (out_dir / "high_k_compressed_baseline_summary.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run dimension-matched high-k compressed k-mer baseline audit.")
    parser.add_argument("--input", default=str(PROJECT_ROOT / "results" / "stage3" / "position_property_ablation" / "stage3_compact_baseline_reads.csv"))
    parser.add_argument("--output-dir", default=str(PROJECT_ROOT / "results" / "stage3" / "reviewer_response" / "high_k_compressed_baselines"))
    parser.add_argument("--lengths", default="69,75,100,150")
    parser.add_argument("--stability-conditions", default="substitution_1pct,N_3pct,trim_5bp,substitution_1pct_N_3pct,local_mismatch_6bp,short_indel")
    parser.add_argument("--readout-conditions", default="clean,substitution_1pct,N_3pct")
    parser.add_argument("--representations", default="ckmer4_count_l2,ckmer5_count_l2,ckmer4_property_l2,ck4p_msp,hash_k15_d222,rp_ck15_d222")
    parser.add_argument("--classifiers", default="nearest_centroid,logistic")
    parser.add_argument("--high-k", type=int, default=15)
    parser.add_argument("--target-dim", type=int, default=222)
    parser.add_argument("--minhash-sketch-size", type=int, default=222)
    parser.add_argument("--max-pairs", type=int, default=250)
    parser.add_argument("--max-per-class", type=int, default=40)
    parser.add_argument("--skip-readout", action="store_true")
    parser.add_argument("--seed", type=int, default=20260625)
    args = parser.parse_args()

    started = time.time()
    set_global_seed(args.seed)
    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    reads = pd.read_csv(args.input)
    reads["source_length"] = reads["source_length"].astype(int)
    reads["sequence"] = reads["sequence"].astype(str).str.upper()
    lengths = parse_int_list(args.lengths)
    reps = parse_csv_list(args.representations)

    stability = run_stability(
        reads=reads,
        lengths=lengths,
        conditions=parse_csv_list(args.stability_conditions),
        representations=reps,
        max_pairs=args.max_pairs,
        seed=args.seed,
        high_k=args.high_k,
        target_dim=args.target_dim,
    )
    stability.to_csv(out_dir / "high_k_stability.csv", index=False, encoding="utf-8-sig")
    minhash = run_minhash_jaccard_audit(
        reads=reads,
        lengths=lengths,
        conditions=parse_csv_list(args.stability_conditions),
        max_pairs=args.max_pairs,
        seed=args.seed,
        high_k=args.high_k,
        sketch_size=args.minhash_sketch_size,
    )
    minhash.to_csv(out_dir / "high_k_minhash_jaccard.csv", index=False, encoding="utf-8-sig")
    readout = pd.DataFrame()
    if not args.skip_readout:
        readout = run_readout(
            reads=reads,
            lengths=lengths,
            conditions=parse_csv_list(args.readout_conditions),
            representations=reps,
            classifiers=parse_csv_list(args.classifiers),
            max_per_class=args.max_per_class,
            seed=args.seed,
            high_k=args.high_k,
            target_dim=args.target_dim,
        )
    readout.to_csv(out_dir / "high_k_readout.csv", index=False, encoding="utf-8-sig")
    summarize(stability, readout, minhash, out_dir)
    (out_dir / "high_k_compressed_baseline_run.json").write_text(
        json.dumps(
            {
                "elapsed_seconds": time.time() - started,
                "input": args.input,
                "lengths": lengths,
                "stability_conditions": parse_csv_list(args.stability_conditions),
                "readout_conditions": parse_csv_list(args.readout_conditions),
                "representations": reps,
                "high_k": args.high_k,
                "target_dim": args.target_dim,
                "minhash_sketch_size": args.minhash_sketch_size,
                "max_pairs": args.max_pairs,
                "max_per_class": args.max_per_class,
                "skip_readout": bool(args.skip_readout),
                "n_stability_rows": int(len(stability)),
                "n_readout_rows": int(len(readout)),
                "n_minhash_jaccard_rows": int(len(minhash)),
            },
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    print(f"Wrote high-k compressed baseline audit to {out_dir}")


if __name__ == "__main__":
    main()

