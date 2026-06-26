"""Spaced k-mer feature builders.

These features are deliberately small and deterministic. They are used to test
whether mismatch-tolerant seeds and reverse-complement canonicalization can be
combined with lightweight biochemical summaries.
"""

from __future__ import annotations

import math
from collections import Counter

import numpy as np
from scipy import sparse
from sklearn.preprocessing import normalize

from .base_encodings import EIIP, GC, HYDROGEN, PURINE
from .sequence_utils import reverse_complement, shannon_entropy


DEFAULT_PATTERN = (0, 2, 4, 6)


def spaced_kmer_tokens(
    seq: str,
    pattern: tuple[int, ...] = DEFAULT_PATTERN,
    canonical: bool = False,
    ignore_n: bool = True,
) -> list[str]:
    seq = seq.upper()
    span = max(pattern) + 1
    if len(seq) < span:
        return []
    tokens: list[str] = []
    for start in range(0, len(seq) - span + 1):
        token = "".join(seq[start + offset] for offset in pattern)
        if ignore_n and "N" in token:
            continue
        if canonical:
            token = min(token, reverse_complement(token))
        tokens.append(token)
    return tokens


def spaced_kmer_counts(
    seq: str,
    pattern: tuple[int, ...] = DEFAULT_PATTERN,
    canonical: bool = False,
    ignore_n: bool = True,
) -> Counter[str]:
    return Counter(spaced_kmer_tokens(seq, pattern=pattern, canonical=canonical, ignore_n=ignore_n))


def build_spaced_kmer_matrix(
    sequences: list[str],
    pattern: tuple[int, ...] = DEFAULT_PATTERN,
    canonical: bool = False,
    vocabulary: dict[str, int] | None = None,
    vocabulary_mode: str = "observed",
) -> tuple[sparse.csr_matrix, dict[str, int]]:
    if vocabulary is None:
        observed: set[str] = set()
        for seq in sequences:
            observed.update(spaced_kmer_counts(seq, pattern=pattern, canonical=canonical, ignore_n=True).keys())
        vocabulary = {term: idx for idx, term in enumerate(sorted(observed))}
        if vocabulary_mode != "observed":
            raise ValueError("Only observed vocabulary mode is supported for spaced k-mers.")

    rows: list[int] = []
    cols: list[int] = []
    data: list[float] = []
    for row_idx, seq in enumerate(sequences):
        counts = spaced_kmer_counts(seq, pattern=pattern, canonical=canonical, ignore_n=True)
        for token, count in counts.items():
            col = vocabulary.get(token)
            if col is not None:
                rows.append(row_idx)
                cols.append(col)
                data.append(float(count))
    mat = sparse.csr_matrix((data, (rows, cols)), shape=(len(sequences), len(vocabulary)), dtype=np.float64)
    return mat, vocabulary


def property_summary_matrix(sequences: list[str]) -> np.ndarray:
    rows: list[np.ndarray] = []
    for seq in sequences:
        seq = seq.upper()
        bases = [base for base in seq if base in "ACGTN"]
        n = max(1, len(bases))
        channels = []
        for table in (HYDROGEN, GC, PURINE, EIIP):
            values = np.asarray([table.get(base, 0.0) for base in bases], dtype=np.float64)
            channels.extend([float(values.mean()) if values.size else 0.0, float(values.std()) if values.size else 0.0])
        n_fraction = sum(1 for base in bases if base == "N") / n
        length_scaled = len(seq) / 200.0
        entropy_scaled = shannon_entropy(seq) / math.log2(5)
        rows.append(np.asarray(channels + [n_fraction, length_scaled, entropy_scaled], dtype=np.float64))
    return np.vstack(rows)


def spaced_count_dense(
    sequences: list[str],
    canonical: bool,
    train_indices: list[int] | None = None,
    add_property_summary: bool = False,
) -> np.ndarray:
    if train_indices is None:
        train_indices = list(range(len(sequences)))
    train_sequences = [sequences[i] for i in train_indices]
    _, vocabulary = build_spaced_kmer_matrix(train_sequences, canonical=canonical, vocabulary_mode="observed")
    mat, _ = build_spaced_kmer_matrix(sequences, canonical=canonical, vocabulary=vocabulary)
    mat = normalize(mat, norm="l2", axis=1)
    dense = mat.toarray()
    if add_property_summary:
        props = property_summary_matrix(sequences)
        dense = np.hstack([dense, props])
        dense = normalize(dense, norm="l2", axis=1)
    return dense
