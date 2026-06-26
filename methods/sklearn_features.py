"""Feature builders backed by numpy/scipy/scikit-learn."""

from __future__ import annotations

from collections import Counter

import numpy as np
import pandas as pd
from scipy import sparse
from sklearn.decomposition import TruncatedSVD
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.preprocessing import normalize

from .sequence_utils import all_kmers, kmer_counts, kmer_tokens, reverse_complement


def build_kmer_matrix(
    sequences: list[str],
    k: int,
    canonical: bool = False,
    vocabulary: dict[str, int] | None = None,
    vocabulary_mode: str = "full",
) -> tuple[sparse.csr_matrix, dict[str, int]]:
    if vocabulary is None:
        if vocabulary_mode == "observed":
            observed: set[str] = set()
            for seq in sequences:
                observed.update(kmer_counts(seq, k, canonical=canonical, ignore_n=True).keys())
            vocab_terms = sorted(observed)
        elif canonical:
            vocab_terms = sorted({min(kmer, reverse_complement(kmer)) for kmer in all_kmers(k)})
        else:
            vocab_terms = all_kmers(k)
        vocabulary = {term: idx for idx, term in enumerate(vocab_terms)}

    rows: list[int] = []
    cols: list[int] = []
    data: list[float] = []
    for row_idx, seq in enumerate(sequences):
        counts = kmer_counts(seq, k, canonical=canonical, ignore_n=True)
        for kmer, count in counts.items():
            col = vocabulary.get(kmer)
            if col is not None:
                rows.append(row_idx)
                cols.append(col)
                data.append(float(count))
    mat = sparse.csr_matrix((data, (rows, cols)), shape=(len(sequences), len(vocabulary)), dtype=np.float64)
    return mat, vocabulary


def transform_feature_matrix(
    count_matrix: sparse.csr_matrix,
    feature_type: str,
    normalization: str = "none",
    train_indices: list[int] | None = None,
) -> tuple[sparse.csr_matrix, dict[str, object]]:
    info: dict[str, object] = {"feature_type": feature_type, "normalization": normalization}
    x = count_matrix.copy().astype(np.float64)

    if feature_type == "relative_frequency":
        row_sums = np.asarray(x.sum(axis=1)).ravel()
        row_sums[row_sums == 0] = 1.0
        x = sparse.diags(1.0 / row_sums).dot(x).tocsr()
    elif feature_type == "tfidf":
        if train_indices is None:
            raise ValueError("train_indices are required for train-only TF-IDF fit")
        transformer = TfidfTransformer(norm=None, use_idf=True, smooth_idf=True)
        transformer.fit(x[train_indices])
        x = transformer.transform(x).tocsr()
        info["idf_min"] = float(np.min(transformer.idf_))
        info["idf_max"] = float(np.max(transformer.idf_))
    elif feature_type == "count":
        pass
    else:
        raise ValueError(f"Unsupported feature_type: {feature_type}")

    if normalization in {"l1", "l2"}:
        x = normalize(x, norm=normalization, axis=1)
    elif normalization in {"none", None}:
        pass
    else:
        raise ValueError(f"Unsupported normalization: {normalization}")
    return x.tocsr(), info


def maybe_reduce_svd(
    matrix: sparse.csr_matrix,
    n_components: int | None,
    train_indices: list[int],
    random_state: int,
) -> tuple[np.ndarray | sparse.csr_matrix, dict[str, object]]:
    if not n_components or n_components <= 0:
        return matrix, {"reducer": "none"}
    max_components = min(n_components, max(1, matrix.shape[1] - 1), max(1, len(train_indices) - 1))
    if max_components < 2:
        return matrix, {"reducer": "none", "reason": "not enough samples/features for SVD"}
    svd = TruncatedSVD(n_components=max_components, random_state=random_state)
    svd.fit(matrix[train_indices])
    transformed = svd.transform(matrix)
    return transformed, {
        "reducer": "truncated_svd",
        "n_components_requested": n_components,
        "n_components_used": max_components,
        "explained_variance_ratio_sum": float(np.sum(svd.explained_variance_ratio_)),
    }


def sparsity_report(matrix: sparse.csr_matrix) -> dict[str, float]:
    row_nnz = np.diff(matrix.indptr)
    total = matrix.shape[0] * matrix.shape[1]
    return {
        "n_samples": int(matrix.shape[0]),
        "n_features": int(matrix.shape[1]),
        "nnz": int(matrix.nnz),
        "density": float(matrix.nnz / total) if total else 0.0,
        "avg_nnz_per_read": float(np.mean(row_nnz)) if len(row_nnz) else 0.0,
        "min_nnz_per_read": int(np.min(row_nnz)) if len(row_nnz) else 0,
        "max_nnz_per_read": int(np.max(row_nnz)) if len(row_nnz) else 0,
    }


def profile_duplicate_rate(matrix: sparse.csr_matrix) -> float:
    seen: set[tuple[tuple[int, float], ...]] = set()
    for row_idx in range(matrix.shape[0]):
        row = matrix.getrow(row_idx)
        signature = tuple(zip(row.indices.tolist(), np.round(row.data, 8).tolist()))
        seen.add(signature)
    return 1.0 - (len(seen) / matrix.shape[0]) if matrix.shape[0] else 0.0


def token_id_sequences(sequences: list[str], k: int, canonical: bool = False, vocabulary: dict[str, int] | None = None) -> tuple[list[list[int]], dict[str, int]]:
    if vocabulary is None:
        counter: Counter[str] = Counter()
        for seq in sequences:
            counter.update(kmer_tokens(seq, k, canonical=canonical, ignore_n=True))
        terms = [term for term, _ in counter.most_common()]
        vocabulary = {term: idx + 1 for idx, term in enumerate(terms)}
    output: list[list[int]] = []
    for seq in sequences:
        output.append([vocabulary[token] for token in kmer_tokens(seq, k, canonical=canonical, ignore_n=True) if token in vocabulary])
    return output, vocabulary


def load_dataset(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    df["sequence"] = df["sequence"].astype(str).str.upper()
    df["length"] = df["length"].astype(int)
    return df
