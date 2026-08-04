"""Positional k-mer extensions used in supplementary sensitivity analyses.

The stable manuscript-facing method remains CK4P-MSP.  This module also exposes
CK4P-MSP-PKM, a fixed-weight supplementary extension that appends a hashed
positional k-mer moment block.  The remaining candidates are retained as
experimental screens and are not manuscript methods.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from typing import Sequence

import numpy as np
from sklearn.preprocessing import normalize

from .ck4p_msp import (
    build_ck4_block,
    build_ck4p_msp_features,
    build_msp_block,
    build_p_block,
)
from .sequence_utils import all_kmers, reverse_complement


PKM_DIMENSION = 75
POSITION_BASIS_ORDER = 3
CONTEXT_PROPERTY_CHANNELS = 5
DEFAULT_HASH_SEED = 20260805
CK4P_MSP_PKM_WEIGHT = 0.25
CK4P_MSP_PKM_KEY = "ck4p_msp_pkm_w025"
CK4P_MSP_PKM_LABEL = "CK4P-MSP-PKM"


_PROPERTY_LOOKUP = {
    "A": np.asarray([0.0, 0.0, 1.0, 0.8372, 0.0], dtype=np.float64),
    "C": np.asarray([1.0, 1.0, 0.0, 0.9869, 0.0], dtype=np.float64),
    "G": np.asarray([1.0, 1.0, 1.0, 0.0000, 0.0], dtype=np.float64),
    "T": np.asarray([0.0, 0.0, 0.0, 0.9775, 0.0], dtype=np.float64),
    "N": np.asarray([0.0, 0.0, 0.0, 0.0000, 1.0], dtype=np.float64),
}

_ASCII_BASE_LOOKUP = np.full(256, -1, dtype=np.int16)
for _base, _value in (("A", 0), ("C", 1), ("G", 2), ("T", 3)):
    _ASCII_BASE_LOOKUP[ord(_base)] = _value


CANDIDATE_BLOCKS = {
    "ck4p_msp": ("K", "P", "M"),
    "candidate_pkm_replace": ("K", "P", "Z"),
    "candidate_cpkm_replace": ("K", "P", "C"),
    "candidate_pkm_augment": ("K", "P", "M", "Z"),
    "candidate_cpkm_augment": ("K", "P", "M", "C"),
    "candidate_dual_augment": ("K", "P", "M", "Z", "C"),
}


CANDIDATE_LABELS = {
    "ck4p_msp": "CK4P-MSP",
    "candidate_pkm_replace": "PKM replace (222D)",
    "candidate_cpkm_replace": "CPKM replace (222D)",
    "candidate_pkm_augment": "PKM augmentation screen (297D)",
    "candidate_cpkm_augment": "CPKM augmentation screen (297D)",
    "candidate_dual_augment": "PKM-CPKM upper screen (372D)",
}


@dataclass(frozen=True)
class PositionalKmerConfig:
    """Configuration shared by the experimental positional blocks."""

    k: int = 4
    output_dim: int = PKM_DIMENSION
    basis_order: int = POSITION_BASIS_ORDER
    context_radius: int = 4
    hash_seed: int = DEFAULT_HASH_SEED


@dataclass(frozen=True)
class PositionalKmerCandidates:
    """Transparent blocks and assembled candidate matrices."""

    ck4: np.ndarray
    p: np.ndarray
    msp: np.ndarray
    pkm: np.ndarray
    cpkm: np.ndarray
    matrices: dict[str, np.ndarray]
    config: PositionalKmerConfig


def _safe_normalize(x: np.ndarray) -> np.ndarray:
    arr = np.nan_to_num(np.asarray(x, dtype=np.float64), nan=0.0, posinf=0.0, neginf=0.0)
    return normalize(arr, norm="l2", axis=1)


@lru_cache(maxsize=None)
def _canonical_vocabulary(k: int) -> dict[str, int]:
    terms = sorted({min(token, reverse_complement(token)) for token in all_kmers(k)})
    return {term: index for index, term in enumerate(terms)}


@lru_cache(maxsize=None)
def _canonical_code_lookup(k: int) -> np.ndarray:
    vocabulary = _canonical_vocabulary(k)
    lookup = np.full(4**k, -1, dtype=np.int32)
    for token in all_kmers(k):
        code = 0
        for base in token:
            code = code * 4 + int(_ASCII_BASE_LOOKUP[ord(base)])
        lookup[code] = vocabulary[min(token, reverse_complement(token))]
    return lookup


def _token_indices(sequence: str, k: int) -> np.ndarray:
    n_windows = len(sequence) - k + 1
    if n_windows <= 0:
        return np.zeros(0, dtype=np.int32)
    encoded = _ASCII_BASE_LOOKUP[np.frombuffer(sequence.encode("ascii"), dtype=np.uint8)]
    valid = np.ones(n_windows, dtype=bool)
    codes = np.zeros(n_windows, dtype=np.int64)
    for offset in range(k):
        values = encoded[offset : offset + n_windows]
        valid &= values >= 0
        codes = codes * 4 + np.maximum(values, 0)
    indices = np.full(n_windows, -1, dtype=np.int32)
    indices[valid] = _canonical_code_lookup(k)[codes[valid]]
    return indices


@lru_cache(maxsize=None)
def _position_basis(n_windows: int, order: int) -> np.ndarray:
    if n_windows <= 0:
        return np.zeros((0, order), dtype=np.float64)
    if n_windows == 1:
        u = np.zeros(1, dtype=np.float64)
    else:
        u = np.linspace(-1.0, 1.0, n_windows, dtype=np.float64)
    columns = []
    if order >= 1:
        columns.append(u)
    if order >= 2:
        columns.append(0.5 * (3.0 * u**2 - 1.0))
    if order >= 3:
        columns.append(0.5 * (5.0 * u**3 - 3.0 * u))
    for degree in range(4, order + 1):
        columns.append(u**degree)
    return np.column_stack(columns) if columns else np.zeros((n_windows, 0), dtype=np.float64)


def _hash_coordinates(raw_indices: np.ndarray, output_dim: int, seed: int) -> tuple[np.ndarray, np.ndarray]:
    values = np.asarray(raw_indices, dtype=np.uint64)
    mixed = values * np.uint64(11400714819323198485) + np.uint64(seed)
    buckets = np.asarray(mixed % np.uint64(output_dim), dtype=np.int64)
    sign_bits = (mixed >> np.uint64(63)) & np.uint64(1)
    signs = np.where(sign_bits == 0, 1.0, -1.0)
    return buckets, signs


def _valid_token(sequence: str, start: int, k: int) -> str | None:
    token = sequence[start : start + k]
    if len(token) != k or any(base not in "ACGT" for base in token):
        return None
    return min(token, reverse_complement(token))


def _sequence_properties(sequence: str) -> np.ndarray:
    if not sequence:
        return np.zeros((1, CONTEXT_PROPERTY_CHANNELS), dtype=np.float64)
    return np.vstack([_PROPERTY_LOOKUP.get(base, _PROPERTY_LOOKUP["N"]) for base in sequence])


def build_pkm_block(
    sequences: Sequence[str],
    config: PositionalKmerConfig | None = None,
) -> np.ndarray:
    """Build a hashed low-rank positional canonical k-mer moment block."""
    config = config or PositionalKmerConfig()
    vocabulary = _canonical_vocabulary(config.k)
    raw_width = len(vocabulary) * config.basis_order
    raw_indices = np.arange(raw_width, dtype=np.uint64)
    buckets, signs = _hash_coordinates(raw_indices, config.output_dim, config.hash_seed)
    bucket_map = buckets.reshape(len(vocabulary), config.basis_order)
    sign_map = signs.reshape(len(vocabulary), config.basis_order)
    rows = np.zeros((len(sequences), config.output_dim), dtype=np.float64)

    for row_index, raw_sequence in enumerate(sequences):
        sequence = str(raw_sequence).upper()
        n_windows = len(sequence) - config.k + 1
        basis = _position_basis(n_windows, config.basis_order)
        token_array = _token_indices(sequence, config.k)
        start_array = np.flatnonzero(token_array >= 0)
        if start_array.size:
            token_array = token_array[start_array]
            selected_buckets = bucket_map[token_array]
            values = basis[start_array] * sign_map[token_array]
            np.add.at(rows[row_index], selected_buckets.ravel(), values.ravel())
    return _safe_normalize(rows)


def build_cpkm_block(
    sequences: Sequence[str],
    config: PositionalKmerConfig | None = None,
) -> np.ndarray:
    """Build context-property-conditioned positional canonical k-mer moments.

    The conditioning value is the difference between flanking-context property
    means and the token-internal property means. This avoids re-encoding a
    property value that is already deterministic from the k-mer identity.
    """
    config = config or PositionalKmerConfig()
    vocabulary = _canonical_vocabulary(config.k)
    raw_width = len(vocabulary) * config.basis_order * CONTEXT_PROPERTY_CHANNELS
    raw_indices = np.arange(raw_width, dtype=np.uint64)
    buckets, signs = _hash_coordinates(raw_indices, config.output_dim, config.hash_seed + 17)
    bucket_map = buckets.reshape(len(vocabulary), config.basis_order, CONTEXT_PROPERTY_CHANNELS)
    sign_map = signs.reshape(len(vocabulary), config.basis_order, CONTEXT_PROPERTY_CHANNELS)
    rows = np.zeros((len(sequences), config.output_dim), dtype=np.float64)

    for row_index, raw_sequence in enumerate(sequences):
        sequence = str(raw_sequence).upper()
        properties = _sequence_properties(sequence)
        n_windows = len(sequence) - config.k + 1
        basis = _position_basis(n_windows, config.basis_order)
        token_indices: list[int] = []
        valid_starts: list[int] = []
        contrasts: list[np.ndarray] = []
        for start in range(max(0, n_windows)):
            token = _valid_token(sequence, start, config.k)
            if token is None:
                continue
            token_end = start + config.k
            token_mean = properties[start:token_end].mean(axis=0)
            left = properties[max(0, start - config.context_radius) : start]
            right = properties[token_end : min(len(sequence), token_end + config.context_radius)]
            if left.size and right.size:
                context = np.vstack([left, right])
            elif left.size:
                context = left
            elif right.size:
                context = right
            else:
                context = properties[start:token_end]
            contrast = context.mean(axis=0) - token_mean
            token_indices.append(vocabulary[token])
            valid_starts.append(start)
            contrasts.append(contrast)
        if token_indices:
            token_array = np.asarray(token_indices, dtype=np.int64)
            start_array = np.asarray(valid_starts, dtype=np.int64)
            contrast_array = np.vstack(contrasts)
            selected_buckets = bucket_map[token_array]
            values = (
                basis[start_array, :, None]
                * contrast_array[:, None, :]
                * sign_map[token_array]
            )
            np.add.at(rows[row_index], selected_buckets.ravel(), values.ravel())
    return _safe_normalize(rows)


def _assemble(blocks: dict[str, np.ndarray], parts: tuple[str, ...]) -> np.ndarray:
    return _safe_normalize(np.hstack([blocks[part] for part in parts]))


def _assemble_weighted(
    blocks: dict[str, np.ndarray],
    parts: tuple[str, ...],
    weights: tuple[float, ...],
) -> np.ndarray:
    if len(parts) != len(weights):
        raise ValueError("parts and weights must have the same length")
    return _safe_normalize(
        np.hstack([float(weight) * blocks[part] for part, weight in zip(parts, weights)])
    )


def build_positional_kmer_candidates(
    sequences: Sequence[str],
    config: PositionalKmerConfig | None = None,
) -> PositionalKmerCandidates:
    """Build the current main representation and all experimental candidates."""
    config = config or PositionalKmerConfig()
    sequence_list = [str(sequence).upper() for sequence in sequences]
    current = build_ck4p_msp_features(sequence_list)
    pkm = build_pkm_block(sequence_list, config=config)
    cpkm = build_cpkm_block(sequence_list, config=config)
    blocks = {"K": current.ck4, "P": current.p, "M": current.msp, "Z": pkm, "C": cpkm}
    matrices = {name: _assemble(blocks, parts) for name, parts in CANDIDATE_BLOCKS.items()}
    return PositionalKmerCandidates(
        ck4=current.ck4,
        p=current.p,
        msp=current.msp,
        pkm=pkm,
        cpkm=cpkm,
        matrices=matrices,
        config=config,
    )


def build_positional_kmer_candidate(
    sequences: Sequence[str],
    name: str,
    config: PositionalKmerConfig | None = None,
) -> np.ndarray:
    """Build one candidate without computing unused experimental blocks."""
    if name not in CANDIDATE_BLOCKS:
        raise ValueError(f"Unsupported positional k-mer candidate: {name}")
    config = config or PositionalKmerConfig()
    sequence_list = [str(sequence).upper() for sequence in sequences]
    parts = CANDIDATE_BLOCKS[name]
    blocks: dict[str, np.ndarray] = {}

    if name == "ck4p_msp":
        return build_ck4p_msp_features(sequence_list).matrix
    if "K" in parts:
        blocks["K"], _ = build_ck4_block(sequence_list)
    if "P" in parts:
        blocks["P"] = build_p_block(sequence_list)
    if "M" in parts:
        blocks["M"] = build_msp_block(sequence_list)
    if "Z" in parts:
        blocks["Z"] = build_pkm_block(sequence_list, config=config)
    if "C" in parts:
        blocks["C"] = build_cpkm_block(sequence_list, config=config)
    return _assemble(blocks, parts)


def build_weighted_augment_candidates(
    sequences: Sequence[str],
    candidate_weights: Sequence[float],
    config: PositionalKmerConfig | None = None,
) -> dict[str, np.ndarray]:
    """Build fixed-weight PKM and CPKM augment variants from shared blocks."""
    config = config or PositionalKmerConfig()
    sequence_list = [str(sequence).upper() for sequence in sequences]
    current = build_ck4p_msp_features(sequence_list)
    pkm = build_pkm_block(sequence_list, config=config)
    cpkm = build_cpkm_block(sequence_list, config=config)
    blocks = {"K": current.ck4, "P": current.p, "M": current.msp, "Z": pkm, "C": cpkm}
    matrices = {"ck4p_msp": current.matrix}
    for raw_weight in candidate_weights:
        weight = float(raw_weight)
        if weight < 0:
            raise ValueError("candidate weights must be non-negative")
        suffix = f"w{int(round(weight * 100)):03d}"
        pkm_key = (
            CK4P_MSP_PKM_KEY
            if np.isclose(weight, CK4P_MSP_PKM_WEIGHT)
            else f"pkm_weight_{suffix}"
        )
        matrices[pkm_key] = _assemble_weighted(
            blocks,
            ("K", "P", "M", "Z"),
            (1.0, 1.0, 1.0, weight),
        )
        matrices[f"cpkm_weight_{suffix}"] = _assemble_weighted(
            blocks,
            ("K", "P", "M", "C"),
            (1.0, 1.0, 1.0, weight),
        )
    return matrices


def build_weighted_positional_candidate(
    sequences: Sequence[str],
    route: str,
    weight: float,
    config: PositionalKmerConfig | None = None,
) -> np.ndarray:
    """Build one fixed-weight augment candidate without unused route blocks."""
    if route not in {"pkm", "cpkm"}:
        raise ValueError("route must be 'pkm' or 'cpkm'")
    if weight < 0:
        raise ValueError("weight must be non-negative")
    config = config or PositionalKmerConfig()
    sequence_list = [str(sequence).upper() for sequence in sequences]
    current = build_ck4p_msp_features(sequence_list)
    candidate = (
        build_pkm_block(sequence_list, config=config)
        if route == "pkm"
        else build_cpkm_block(sequence_list, config=config)
    )
    blocks = {"K": current.ck4, "P": current.p, "M": current.msp, "X": candidate}
    return _assemble_weighted(
        blocks,
        ("K", "P", "M", "X"),
        (1.0, 1.0, 1.0, float(weight)),
    )


def build_ck4p_msp_pkm(
    sequences: Sequence[str],
    config: PositionalKmerConfig | None = None,
) -> np.ndarray:
    """Build the fixed 297D CK4P-MSP-PKM supplementary extension.

    The extension preserves the CK4P-MSP K/P/MSP blocks and appends the 75D
    positional k-mer moment block with the prespecified weight delta=0.25.
    It is an exploratory Pareto variant, not a replacement for the stable main
    method and not a universally optimized weight setting.
    """

    return build_weighted_positional_candidate(
        sequences,
        route="pkm",
        weight=CK4P_MSP_PKM_WEIGHT,
        config=config,
    )


def candidate_dimensions(config: PositionalKmerConfig | None = None) -> dict[str, int]:
    """Return candidate dimensions without constructing sequences."""
    config = config or PositionalKmerConfig()
    block_dimensions = {"K": 136, "P": 11, "M": 75, "Z": config.output_dim, "C": config.output_dim}
    return {
        name: int(sum(block_dimensions[part] for part in parts))
        for name, parts in CANDIDATE_BLOCKS.items()
    }
