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
from typing import Sequence

import numpy as np
from sklearn.preprocessing import normalize

from .sequence_utils import all_kmers, reverse_complement
from .sklearn_features import build_kmer_matrix, transform_feature_matrix
from .spaced_features import property_summary_matrix
from .stage2_features import property_multiscale_matrix


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
#           standardized diagnostic representation, not physical unit conversion.
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
#           222-dimensional CK4P-MSP vector.
#       CN: 使用完整反向互补规范化 k-mer 词表。k=4 时 CK4 固定为
#           136 维，默认 CK4P-MSP 为 222 维。
#
#   vocabulary_mode="observed"
#       EN: fits the k-mer vocabulary from training reads only. This is useful
#           for some historical grids, but the dimensionality becomes
#           data-dependent.
#       CN: 只从训练 reads 中拟合 k-mer 词表，适合部分历史实验网格；
#           但维度会依赖数据集。
# ---------------------------------------------------------------------------

DEFAULT_MSP_BINS = (2, 3, 4, 6)
DEFAULT_WEIGHTS = (1.0, 1.0, 1.0)
P_DIMENSION = 11
MSP_CHANNELS = 5


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
    return _normalize_rows(property_summary_matrix(_as_sequence_list(sequences)))


def build_msp_block(
    sequences: Sequence[str],
    *,
    config: CK4PMSPConfig | None = None,
) -> np.ndarray:
    """Build the multi-scale positional property pooling block."""
    config = config or CK4PMSPConfig()
    return _normalize_rows(
        property_multiscale_matrix(
            _as_sequence_list(sequences),
            bins=config.bins,
            include_std=config.include_msp_std,
        )
    )


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
    p = build_p_block(sequence_list)
    msp = build_msp_block(sequence_list, config=config)
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
    """Row-wise L2 drift used as a standardized diagnostic metric."""
    clean_norm = _normalize_rows(clean)
    perturbed_norm = _normalize_rows(perturbed)
    return np.linalg.norm(clean_norm - perturbed_norm, axis=1)
