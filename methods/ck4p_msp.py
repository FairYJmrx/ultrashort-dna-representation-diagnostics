"""Public CK4P-MSP method API.

This module is the stable, manuscript-facing entrypoint for the main compact
representation. It keeps the three evidence blocks visible:

- CK4: reverse-complement canonical 4-mer composition counts.
- P: global biochemical-property summary.
- MSP: multi-scale positional property pooling.

The lower-level feature builders remain in ``stage2_features.py`` and related
modules for historical experiment scripts. New code that wants the paper's
main method should import from this module.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from typing import Sequence

import numpy as np
from sklearn.preprocessing import normalize

from .sequence_utils import all_kmers, reverse_complement
from .sklearn_features import build_kmer_matrix, transform_feature_matrix


# ---------------------------------------------------------------------------
# Top-level configuration guide / 顶部配置说明
#
# CK4P-MSP is controlled by CK4PMSPConfig below. The defaults implement the
# manuscript main method:
#
#   k=4
#       EN: reverse-complement canonical 4-mers form the local composition
#           backbone.
#       CN: 反向互补规范化 4-mer 构成局部组成主干。
#   bins=(2, 3, 4, 6)
#       EN: MSP pools per-base property signals over coarse-to-fine relative
#           position bins. The default has 15 bins in total.
#       CN: MSP 按相对位置由粗到细池化逐碱基属性信号，默认共 15 个分箱。
#   include_msp_std=False
#       EN: False keeps mean-only MSP for the compact manuscript method. True
#           additionally appends per-bin standard deviations for audit variants.
#       CN: False 表示仅保留均值 MSP；True 额外加入每个分箱的标准差，用于审计变体。
#   alpha, beta, gamma = 1.0, 1.0, 1.0
#       EN: weights for CK4, P and MSP before concatenation. They define a
#           standardized representation, not physical unit conversion.
#       CN: 分别为 CK4、P 和 MSP 的拼接权重；定义标准化诊断表征，不是物理单位换算。
#   vocabulary_mode="full"
#       EN: uses the complete canonical vocabulary. For k=4, CK4 is 136D and
#           the default CK4P-MSP representation is 222D.
#       CN: 使用完整规范化词表；k=4 时 CK4 为 136 维，CK4P-MSP 为 222 维。
#   vocabulary_mode="observed"
#       EN: fits vocabulary on training reads only; suitable for historical
#           grids, but its dimensionality is data-dependent.
#       CN: 仅根据训练 reads 拟合词表；适用于历史网格，但维度会随数据变化。
# ---------------------------------------------------------------------------

DEFAULT_MSP_BINS = (2, 3, 4, 6)
DEFAULT_WEIGHTS = (1.0, 1.0, 1.0)
P_DIMENSION = 11
MSP_CHANNELS = 5

_BASE_CODE_LOOKUP = np.full(256, -1, dtype=np.int8)
for _base_code, _base in enumerate("ACGTN"):
    _BASE_CODE_LOOKUP[ord(_base)] = _base_code

# Columns follow the public MSP contract: hydrogen, GC, purine, EIIP and N.
_PROPERTY_LOOKUP = np.asarray(
    [
        [2.0, 0.0, 1.0, 0.1260, 0.0],  # A
        [3.0, 1.0, 0.0, 0.1340, 0.0],  # C
        [3.0, 1.0, 1.0, 0.0806, 0.0],  # G
        [2.0, 0.0, 0.0, 0.1335, 0.0],  # T
        [0.0, 0.0, 0.0, 0.0000, 1.0],  # N
    ],
    dtype=np.float64,
)

BLOCK_COMBINATIONS = {
    "ck4": ("K",),
    "p": ("P",),
    "msp": ("M",),
    "ck4_p": ("K", "P"),
    "ck4_msp": ("K", "M"),
    "p_msp": ("P", "M"),
    "ck4p_msp": ("K", "P", "M"),
}


@dataclass(frozen=True)
class CK4PMSPConfig:
    """Configuration for the compact mixed representation."""

    k: int = 4
    bins: tuple[int, ...] = DEFAULT_MSP_BINS
    include_msp_std: bool = False
    alpha: float = DEFAULT_WEIGHTS[0]
    beta: float = DEFAULT_WEIGHTS[1]
    gamma: float = DEFAULT_WEIGHTS[2]
    canonical: bool = True
    vocabulary_mode: str = "full"


@dataclass(frozen=True)
class CK4PMSPFeatures:
    """Feature matrix plus transparent component blocks."""

    matrix: np.ndarray
    ck4: np.ndarray
    p: np.ndarray
    msp: np.ndarray
    vocabulary: dict[str, int]
    config: CK4PMSPConfig


def _as_sequence_list(sequences: Sequence[str]) -> list[str]:
    return [str(seq).upper() for seq in sequences]


def _training_sequences(sequences: list[str], train_indices: Sequence[int] | None) -> list[str]:
    if train_indices is None:
        return sequences
    return [sequences[int(idx)] for idx in train_indices]


def _normalize_rows(x: np.ndarray) -> np.ndarray:
    x = np.nan_to_num(np.asarray(x, dtype=np.float64), nan=0.0, posinf=0.0, neginf=0.0)
    return normalize(x, norm="l2", axis=1)


def _base_codes(sequence: str) -> np.ndarray:
    """Map one upper-case sequence to A/C/G/T/N codes; invalid symbols are -1."""
    raw = np.frombuffer(sequence.encode("ascii", errors="replace"), dtype=np.uint8)
    return _BASE_CODE_LOOKUP[raw]


def _reverse_complement_code(code: int, k: int) -> int:
    reverse = 0
    value = int(code)
    for _ in range(k):
        reverse = reverse * 4 + (3 - (value % 4))
        value //= 4
    return reverse


@lru_cache(maxsize=None)
def _full_canonical_vocabulary(k: int) -> tuple[dict[str, int], np.ndarray]:
    terms = sorted({min(kmer, reverse_complement(kmer)) for kmer in all_kmers(k)})
    vocabulary = {term: idx for idx, term in enumerate(terms)}
    canonical_codes = sorted(
        {min(code, _reverse_complement_code(code, k)) for code in range(4**k)}
    )
    code_to_column = np.full(4**k, -1, dtype=np.int32)
    canonical_to_column = {code: idx for idx, code in enumerate(canonical_codes)}
    for code in range(4**k):
        canonical = min(code, _reverse_complement_code(code, k))
        code_to_column[code] = canonical_to_column[canonical]
    return vocabulary, code_to_column


def _full_canonical_kmer_matrix(sequences: list[str], k: int) -> tuple[np.ndarray, dict[str, int]]:
    """Dense integer fast path for the fixed full canonical vocabulary."""
    vocabulary, code_to_column = _full_canonical_vocabulary(k)
    matrix = np.zeros((len(sequences), len(vocabulary)), dtype=np.float64)
    powers_forward = np.asarray([4 ** (k - 1 - offset) for offset in range(k)], dtype=np.int64)
    powers_reverse = np.asarray([4**offset for offset in range(k)], dtype=np.int64)

    for row_idx, sequence in enumerate(sequences):
        codes = _base_codes(sequence)
        n_windows = codes.size - k + 1
        if n_windows <= 0:
            continue
        forward = np.zeros(n_windows, dtype=np.int64)
        reverse = np.zeros(n_windows, dtype=np.int64)
        valid = np.ones(n_windows, dtype=bool)
        for offset in range(k):
            values = codes[offset : offset + n_windows]
            is_valid = (values >= 0) & (values < 4)
            valid &= is_valid
            safe_values = np.where(is_valid, values, 0).astype(np.int64, copy=False)
            forward += safe_values * powers_forward[offset]
            reverse += (3 - safe_values) * powers_reverse[offset]
        if not np.any(valid):
            continue
        canonical = np.minimum(forward[valid], reverse[valid])
        columns = code_to_column[canonical]
        matrix[row_idx] = np.bincount(columns, minlength=matrix.shape[1])

    return _normalize_rows(matrix), dict(vocabulary)


def _property_rows(
    sequences: list[str],
    *,
    bins: tuple[int, ...],
    include_msp_std: bool,
    include_p: bool,
    include_msp: bool,
) -> tuple[np.ndarray | None, np.ndarray | None]:
    """Build P and MSP from one per-sequence numerical encoding pass."""
    encoded = [_base_codes(sequence) for sequence in sequences]
    if encoded and all(codes.size > 0 and np.all(codes >= 0) for codes in encoded):
        p_matrix = np.zeros((len(sequences), P_DIMENSION), dtype=np.float64) if include_p else None
        msp_width = sum(bins) * MSP_CHANNELS * (2 if include_msp_std else 1)
        msp_matrix = np.zeros((len(sequences), msp_width), dtype=np.float64) if include_msp else None
        groups: dict[int, list[int]] = {}
        for row_idx, codes in enumerate(encoded):
            groups.setdefault(int(codes.size), []).append(row_idx)

        for sequence_length, row_indices in groups.items():
            code_matrix = np.vstack([encoded[row_idx] for row_idx in row_indices])
            signals = _PROPERTY_LOOKUP[code_matrix]

            if include_p:
                global_signals = signals[:, :, :4]
                means = global_signals.mean(axis=1)
                stds = global_signals.std(axis=1)
                p_matrix[row_indices, :8:2] = means
                p_matrix[row_indices, 1:8:2] = stds
                counts = np.stack(
                    [(code_matrix == code).sum(axis=1) for code in range(5)],
                    axis=1,
                ).astype(np.float64)
                probabilities = counts / float(sequence_length)
                entropy_terms = np.zeros_like(probabilities)
                positive = probabilities > 0
                entropy_terms[positive] = probabilities[positive] * np.log2(probabilities[positive])
                p_matrix[row_indices, 8] = counts[:, 4] / float(sequence_length)
                p_matrix[row_indices, 9] = sequence_length / 200.0
                p_matrix[row_indices, 10] = -entropy_terms.sum(axis=1) / float(np.log2(5.0))

            if include_msp:
                pooled_parts: list[np.ndarray] = []
                for n_bins in bins:
                    edges = np.linspace(0, sequence_length, n_bins + 1)
                    for left_float, right_float in zip(edges[:-1], edges[1:]):
                        left = int(np.floor(left_float))
                        right = int(np.floor(right_float))
                        if right <= left:
                            right = min(sequence_length, left + 1)
                        block = signals[:, left:right, :]
                        pooled_parts.append(block.mean(axis=1))
                        if include_msp_std:
                            pooled_parts.append(block.std(axis=1))
                msp_matrix[row_indices] = np.concatenate(pooled_parts, axis=1)

        return (
            _normalize_rows(p_matrix) if p_matrix is not None else None,
            _normalize_rows(msp_matrix) if msp_matrix is not None else None,
        )

    p_rows: list[np.ndarray] = []
    msp_rows: list[np.ndarray] = []
    entropy_scale = float(np.log2(5.0))

    for sequence, codes in zip(sequences, encoded):
        valid_codes = codes[codes >= 0]

        if include_p:
            if valid_codes.size:
                global_signals = _PROPERTY_LOOKUP[valid_codes, :4]
                means = global_signals.mean(axis=0)
                stds = global_signals.std(axis=0)
                interleaved = np.column_stack((means, stds)).ravel()
                counts = np.bincount(valid_codes, minlength=5).astype(np.float64)
                probabilities = counts[counts > 0] / float(valid_codes.size)
                entropy = -float(np.sum(probabilities * np.log2(probabilities)))
                n_fraction = float(counts[4] / valid_codes.size)
            else:
                interleaved = np.zeros(8, dtype=np.float64)
                entropy = 0.0
                n_fraction = 0.0
            p_rows.append(
                np.concatenate(
                    (
                        interleaved,
                        np.asarray(
                            [n_fraction, len(sequence) / 200.0, entropy / entropy_scale],
                            dtype=np.float64,
                        ),
                    )
                )
            )

        if include_msp:
            positional_codes = valid_codes if valid_codes.size else np.asarray([4], dtype=np.int8)
            signals = _PROPERTY_LOOKUP[positional_codes]
            n_positions = signals.shape[0]
            prefix = np.vstack((np.zeros((1, MSP_CHANNELS), dtype=np.float64), np.cumsum(signals, axis=0)))
            values: list[np.ndarray] = []
            for n_bins in bins:
                edges = np.linspace(0, n_positions, n_bins + 1)
                for left_float, right_float in zip(edges[:-1], edges[1:]):
                    left = int(np.floor(left_float))
                    right = int(np.floor(right_float))
                    if right <= left:
                        right = min(n_positions, left + 1)
                    width = max(1, right - left)
                    means = (prefix[right] - prefix[left]) / float(width)
                    values.append(means)
                    if include_msp_std:
                        values.append(signals[left:right].std(axis=0))
            msp_rows.append(np.concatenate(values))

    p_matrix = _normalize_rows(np.vstack(p_rows)) if include_p else None
    msp_matrix = _normalize_rows(np.vstack(msp_rows)) if include_msp else None
    return p_matrix, msp_matrix


def canonical_kmer_vocabulary_size(k: int = 4) -> int:
    """Return the full reverse-complement canonical vocabulary size."""
    return len({min(kmer, reverse_complement(kmer)) for kmer in all_kmers(k)})


def expected_dimensions(config: CK4PMSPConfig | None = None) -> dict[str, int | None]:
    """Expected block dimensions for a configuration.

    ``ck4`` is known only for the default full vocabulary mode. Observed
    vocabularies are data-dependent and therefore reported as ``None``.
    """
    config = config or CK4PMSPConfig()
    ck_dim = canonical_kmer_vocabulary_size(config.k) if config.vocabulary_mode == "full" else None
    msp_dim = sum(config.bins) * MSP_CHANNELS * (2 if config.include_msp_std else 1)
    total = None if ck_dim is None else ck_dim + P_DIMENSION + msp_dim
    return {"ck4": ck_dim, "p": P_DIMENSION, "msp": msp_dim, "total": total}


def build_ck4_block(
    sequences: Sequence[str],
    *,
    config: CK4PMSPConfig | None = None,
    train_indices: Sequence[int] | None = None,
) -> tuple[np.ndarray, dict[str, int]]:
    """Build the reverse-complement canonical local k-mer composition block."""
    config = config or CK4PMSPConfig()
    sequence_list = _as_sequence_list(sequences)
    if config.vocabulary_mode == "full" and config.canonical:
        return _full_canonical_kmer_matrix(sequence_list, config.k)

    vocabulary = None
    if config.vocabulary_mode == "observed":
        train_sequences = _training_sequences(sequence_list, train_indices)
        _, vocabulary = build_kmer_matrix(
            train_sequences,
            k=config.k,
            canonical=config.canonical,
            vocabulary_mode="observed",
        )
    elif config.vocabulary_mode != "full":
        raise ValueError(f"Unsupported vocabulary_mode: {config.vocabulary_mode}")

    counts, vocabulary = build_kmer_matrix(
        sequence_list,
        k=config.k,
        canonical=config.canonical,
        vocabulary=vocabulary,
        vocabulary_mode="full" if vocabulary is None else "observed",
    )
    features, _ = transform_feature_matrix(
        counts,
        feature_type="count",
        normalization="l2",
        train_indices=list(train_indices) if train_indices is not None else None,
    )
    return features.toarray(), vocabulary


def build_p_block(sequences: Sequence[str]) -> np.ndarray:
    """Build the global biochemical-property summary block."""
    p, _ = _property_rows(
        _as_sequence_list(sequences),
        bins=DEFAULT_MSP_BINS,
        include_msp_std=False,
        include_p=True,
        include_msp=False,
    )
    assert p is not None
    return p


def build_msp_block(
    sequences: Sequence[str],
    *,
    config: CK4PMSPConfig | None = None,
) -> np.ndarray:
    """Build the multi-scale positional property pooling block."""
    config = config or CK4PMSPConfig()
    _, msp = _property_rows(
        _as_sequence_list(sequences),
        bins=config.bins,
        include_msp_std=config.include_msp_std,
        include_p=False,
        include_msp=True,
    )
    assert msp is not None
    return msp


def build_property_blocks(
    sequences: Sequence[str],
    *,
    config: CK4PMSPConfig | None = None,
) -> tuple[np.ndarray, np.ndarray]:
    """Build P and MSP together without rescanning the input sequences."""
    config = config or CK4PMSPConfig()
    p, msp = _property_rows(
        _as_sequence_list(sequences),
        bins=config.bins,
        include_msp_std=config.include_msp_std,
        include_p=True,
        include_msp=True,
    )
    assert p is not None and msp is not None
    return p, msp


def concatenate_weighted_blocks(
    ck4: np.ndarray,
    p: np.ndarray,
    msp: np.ndarray,
    *,
    alpha: float = 1.0,
    beta: float = 1.0,
    gamma: float = 1.0,
) -> np.ndarray:
    """Combine internally normalized blocks using the manuscript weights."""
    weights = np.asarray([alpha, beta, gamma], dtype=np.float64)
    if np.any(weights < 0):
        raise ValueError("Block weights must be non-negative.")
    denominator = float(np.linalg.norm(weights))
    if denominator <= 0:
        raise ValueError("At least one block weight must be positive.")
    blocks = [
        float(alpha) * _normalize_rows(ck4),
        float(beta) * _normalize_rows(p),
        float(gamma) * _normalize_rows(msp),
    ]
    return np.hstack(blocks) / denominator


def build_block_combination(
    features: CK4PMSPFeatures,
    name: str,
) -> np.ndarray:
    """Assemble one of the seven public K/P/MSP block combinations.

    Every selected block is internally L2-normalized. Equal-weight
    combinations are divided by the square root of the selected block count,
    so the scale is fixed by the declared contract rather than by row energy.
    """
    try:
        parts = BLOCK_COMBINATIONS[name]
    except KeyError as exc:
        supported = ", ".join(sorted(BLOCK_COMBINATIONS))
        raise ValueError(f"Unsupported public block combination {name!r}; choose from {supported}.") from exc
    blocks = {"K": features.ck4, "P": features.p, "M": features.msp}
    selected = [_normalize_rows(blocks[part]) for part in parts]
    return np.hstack(selected) / np.sqrt(float(len(selected)))


def build_ck4p_msp_features(
    sequences: Sequence[str],
    *,
    config: CK4PMSPConfig | None = None,
    train_indices: Sequence[int] | None = None,
) -> CK4PMSPFeatures:
    """Build CK4P-MSP and return the mixed matrix plus each component block."""
    config = config or CK4PMSPConfig()
    sequence_list = _as_sequence_list(sequences)
    ck4, vocabulary = build_ck4_block(sequence_list, config=config, train_indices=train_indices)
    p, msp = build_property_blocks(sequence_list, config=config)
    matrix = concatenate_weighted_blocks(
        ck4,
        p,
        msp,
        alpha=config.alpha,
        beta=config.beta,
        gamma=config.gamma,
    )
    return CK4PMSPFeatures(matrix=matrix, ck4=ck4, p=p, msp=msp, vocabulary=vocabulary, config=config)


def build_ck4p_msp(
    sequences: Sequence[str],
    *,
    config: CK4PMSPConfig | None = None,
    train_indices: Sequence[int] | None = None,
) -> np.ndarray:
    """Build the default paper representation matrix."""
    return build_ck4p_msp_features(sequences, config=config, train_indices=train_indices).matrix


def paired_cosine(clean: np.ndarray, perturbed: np.ndarray) -> np.ndarray:
    """Row-wise paired cosine similarity after L2 normalization."""
    clean_norm = _normalize_rows(clean)
    perturbed_norm = _normalize_rows(perturbed)
    return np.sum(clean_norm * perturbed_norm, axis=1)


def standardized_diagnostic_drift(clean: np.ndarray, perturbed: np.ndarray) -> np.ndarray:
    """Row-wise L2 drift used as a standardized representation metric."""
    clean_norm = _normalize_rows(clean)
    perturbed_norm = _normalize_rows(perturbed)
    return np.linalg.norm(clean_norm - perturbed_norm, axis=1)
