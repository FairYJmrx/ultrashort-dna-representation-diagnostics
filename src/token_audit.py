"""Token sequence audit features."""

from __future__ import annotations

import random
from collections import Counter

import numpy as np
from scipy import sparse

from .sequence_utils import kmer_tokens


def build_token_vocab(sequences: list[str], k: int, canonical: bool = False) -> dict[str, int]:
    counter: Counter[str] = Counter()
    for seq in sequences:
        counter.update(kmer_tokens(seq, k, canonical=canonical, ignore_n=True))
    return {token: idx + 1 for idx, (token, _) in enumerate(counter.most_common())}


def tokenize_to_ids(sequences: list[str], k: int, vocab: dict[str, int], canonical: bool = False) -> list[list[int]]:
    out: list[list[int]] = []
    for seq in sequences:
        out.append([vocab[t] for t in kmer_tokens(seq, k, canonical=canonical, ignore_n=True) if t in vocab])
    return out


def apply_ablation(token_ids: list[list[int]], ablation: str, seed: int = 13) -> list[list[int]]:
    rng = random.Random(seed)
    if ablation == "none":
        return [tokens[:] for tokens in token_ids]
    if ablation == "token_shuffle":
        out = []
        for tokens in token_ids:
            shuffled = tokens[:]
            rng.shuffle(shuffled)
            out.append(shuffled)
        return out
    if ablation == "position_shuffle":
        # Same observable effect for order-sensitive n-gram features; kept separate for reporting.
        out = []
        for tokens in token_ids:
            shuffled = tokens[:]
            rng.shuffle(shuffled)
            out.append(shuffled)
        return out
    if ablation == "token_id_permutation":
        unique = sorted({tok for seq in token_ids for tok in seq})
        permuted = unique[:]
        rng.shuffle(permuted)
        mapping = dict(zip(unique, permuted))
        return [[mapping[tok] for tok in seq] for seq in token_ids]
    raise ValueError(f"Unsupported ablation: {ablation}")


def token_bag_matrix(token_ids: list[list[int]], vocab_size: int) -> sparse.csr_matrix:
    rows: list[int] = []
    cols: list[int] = []
    data: list[float] = []
    for row_idx, tokens in enumerate(token_ids):
        counts = Counter(tokens)
        for token_id, count in counts.items():
            if token_id > 0:
                rows.append(row_idx)
                cols.append(token_id - 1)
                data.append(float(count))
    return sparse.csr_matrix((data, (rows, cols)), shape=(len(token_ids), vocab_size), dtype=np.float64)


def token_transition_matrix(token_ids: list[list[int]], vocab_size: int, hash_bins: int = 4096) -> sparse.csr_matrix:
    rows: list[int] = []
    cols: list[int] = []
    data: list[float] = []
    for row_idx, tokens in enumerate(token_ids):
        counts: Counter[int] = Counter()
        for a, b in zip(tokens, tokens[1:]):
            bucket = ((a * 1000003) ^ b) % hash_bins
            counts[bucket] += 1
        for bucket, count in counts.items():
            rows.append(row_idx)
            cols.append(bucket)
            data.append(float(count))
    return sparse.csr_matrix((data, (rows, cols)), shape=(len(token_ids), hash_bins), dtype=np.float64)


def token_numeric_summary(token_ids: list[list[int]]) -> np.ndarray:
    rows = []
    for tokens in token_ids:
        arr = np.asarray(tokens, dtype=np.float64)
        if arr.size == 0:
            rows.append([0.0, 0.0, 0.0, 0.0, 0.0])
        else:
            diffs = np.diff(arr) if arr.size > 1 else np.asarray([0.0])
            rows.append([arr.size, float(np.mean(arr)), float(np.std(arr)), float(np.mean(np.abs(diffs))), float(np.std(diffs))])
    return np.asarray(rows, dtype=np.float64)

