"""Position-base joint encodings for lightweight experiments.

These encodings are not final neural modules. They are deterministic or
semi-prior feature constructors designed to test whether position/base priors
carry usable signal before building heavier models.
"""

from __future__ import annotations

import math

import numpy as np

from .base_encodings import EIIP, GC, HYDROGEN, PURINE, one_hot, pad_or_trim
from .sequence_utils import kmer_tokens

BASE_ORDER = "ACGTN"


def base_property_vector(base: str) -> np.ndarray:
    base = base.upper()
    one = np.zeros(5, dtype=np.float64)
    one[BASE_ORDER.index(base if base in BASE_ORDER else "N")] = 1.0
    props = np.array(
        [
            HYDROGEN.get(base, 0.0) / 3.0,
            GC.get(base, 0.0),
            PURINE.get(base, 0.0),
            EIIP.get(base, 0.0),
            1.0 if base == "N" else 0.0,
        ],
        dtype=np.float64,
    )
    return np.concatenate([one, props])


def sequence_property_matrix(seq: str, length: int) -> np.ndarray:
    seq = pad_or_trim(seq, length)
    return np.vstack([base_property_vector(base) for base in seq])


def sinusoidal_position_matrix(length: int, dim: int, base: float = 10000.0) -> np.ndarray:
    if dim % 2 != 0:
        dim += 1
    pe = np.zeros((length, dim), dtype=np.float64)
    positions = np.arange(length, dtype=np.float64)[:, None]
    div_term = np.exp(np.arange(0, dim, 2, dtype=np.float64) * (-math.log(base) / dim))
    pe[:, 0::2] = np.sin(positions * div_term)
    pe[:, 1::2] = np.cos(positions * div_term)
    return pe


def property_projected(seq: str, length: int, dim: int = 16) -> np.ndarray:
    props = sequence_property_matrix(seq, length)
    # Deterministic projection from 10 property dims to dim using sin/cos basis.
    in_dim = props.shape[1]
    weights = np.zeros((in_dim, dim), dtype=np.float64)
    for i in range(in_dim):
        for j in range(dim):
            weights[i, j] = math.sin((i + 1) * (j + 1)) + math.cos((i + 1) * (j + 1) / 2.0)
    return props @ weights / math.sqrt(in_dim)


def highdim_phase_joint(seq: str, length: int, dim: int = 16, mode: str = "prior") -> np.ndarray:
    """High-dimensional multi-frequency phase vector.

    mode:
    - prior: alpha/theta are deterministic functions of DNA properties.
    - learnable_proxy: deterministic random-like projection without explicit biology.
    - prior_residual: concatenate prior with a projected property residual.
    """
    if dim % 2 != 0:
        dim += 1
    seq = pad_or_trim(seq, length)
    props = sequence_property_matrix(seq, length)
    half = dim // 2
    freqs = np.array([1.0 / (75.0 ** (2 * d / dim)) for d in range(half)], dtype=np.float64)
    positions = np.arange(length, dtype=np.float64)[:, None]

    gc_strength = props[:, 6:7]
    hydrogen_strength = props[:, 5:6]
    purine_strength = props[:, 7:8]
    eiip_strength = props[:, 8:9]

    if mode == "learnable_proxy":
        projected = property_projected(seq, length, dim=dim)
        return projected

    alpha = 0.5 + 0.5 * gc_strength + 0.25 * hydrogen_strength
    theta_base = math.pi * (purine_strength + eiip_strength)
    angles = positions * freqs[None, :] + theta_base
    out = np.empty((length, dim), dtype=np.float64)
    out[:, 0::2] = alpha * np.sin(angles)
    out[:, 1::2] = alpha * np.cos(angles)

    if mode == "prior_residual":
        residual = property_projected(seq, length, dim=dim)
        out = np.concatenate([out, residual], axis=1)
    elif mode != "prior":
        raise ValueError(f"Unsupported joint mode: {mode}")
    return out


def attribute_gated_pe(seq: str, length: int, dim: int = 16, gate: str = "multi_property") -> np.ndarray:
    pe = sinusoidal_position_matrix(length, dim)
    props = sequence_property_matrix(seq, length)
    if gate == "scalar_gc":
        g = 0.25 + 0.75 * props[:, 6:7]
    elif gate == "scalar_hydrogen":
        g = props[:, 5:6]
    elif gate == "multi_property":
        g = 0.2 + 0.2 * props[:, 5:6] + 0.3 * props[:, 6:7] + 0.2 * props[:, 7:8] + props[:, 8:9]
    elif gate == "learnable_proxy":
        projected = property_projected(seq, length, dim=dim)
        g = 1.0 / (1.0 + np.exp(-projected))
        return g * pe
    else:
        raise ValueError(f"Unsupported gate: {gate}")
    return g * pe


def rope_like_rotation(seq: str, length: int, dim: int = 16, semantic: str = "property") -> np.ndarray:
    if dim % 2 != 0:
        dim += 1
    if semantic == "onehot":
        base_sem = one_hot(seq, length).reshape(length, 5)
        # Expand one-hot into dim with deterministic projection.
        weights = np.zeros((5, dim), dtype=np.float64)
        for i in range(5):
            for j in range(dim):
                weights[i, j] = math.sin((i + 1) * (j + 1))
        z = base_sem @ weights
    elif semantic == "property":
        z = property_projected(seq, length, dim=dim)
    else:
        raise ValueError(f"Unsupported semantic: {semantic}")

    half = dim // 2
    freqs = np.array([1.0 / (75.0 ** (2 * d / dim)) for d in range(half)], dtype=np.float64)
    pos = np.arange(length, dtype=np.float64)[:, None]
    theta = pos * freqs[None, :]
    even = z[:, 0::2]
    odd = z[:, 1::2]
    rotated = np.empty_like(z)
    rotated[:, 0::2] = even * np.cos(theta) - odd * np.sin(theta)
    rotated[:, 1::2] = even * np.sin(theta) + odd * np.cos(theta)
    return rotated


def kmer_property_sequence(seq: str, length: int, k: int, dim: int = 16) -> np.ndarray:
    """Token-level property sequence for k-mer schemes."""
    tokens = kmer_tokens(pad_or_trim(seq, length), k, canonical=False, ignore_n=False)
    rows = []
    for token in tokens:
        props = np.vstack([base_property_vector(base) for base in token])
        rows.append(np.concatenate([props.mean(axis=0), props.std(axis=0)]))
    if not rows:
        return np.zeros((max(1, length - k + 1), dim), dtype=np.float64)
    mat = np.vstack(rows)
    # Project to dim.
    in_dim = mat.shape[1]
    weights = np.zeros((in_dim, dim), dtype=np.float64)
    for i in range(in_dim):
        for j in range(dim):
            weights[i, j] = math.sin((i + 2) * (j + 1) / 3.0)
    return mat @ weights / math.sqrt(in_dim)


def codon_frame_channels(seq: str, length: int, dim: int = 16) -> np.ndarray:
    """Three-frame property channels.

    This does not assume the read is coding. It tests whether explicitly exposing
    phase/frame structure is more useful than a single scalar three-phase signal.
    """
    props = sequence_property_matrix(seq, length)
    frame = np.zeros((length, 3), dtype=np.float64)
    for i in range(length):
        frame[i, i % 3] = 1.0
    framed = np.concatenate([props, props[:, 5:9] * frame[:, 0:1], props[:, 5:9] * frame[:, 1:2], props[:, 5:9] * frame[:, 2:3]], axis=1)
    in_dim = framed.shape[1]
    weights = np.zeros((in_dim, dim), dtype=np.float64)
    for i in range(in_dim):
        for j in range(dim):
            weights[i, j] = math.sin((i + 1) * (j + 2) / 5.0) + math.cos((i + 3) * (j + 1) / 7.0)
    return framed @ weights / math.sqrt(in_dim)


def local_entropy(values: str, window: int = 9) -> np.ndarray:
    seq = values.upper()
    out = np.zeros(len(seq), dtype=np.float64)
    for i in range(len(seq)):
        start = max(0, i - window // 2)
        end = min(len(seq), i + window // 2 + 1)
        sub = seq[start:end]
        counts = {base: sub.count(base) for base in BASE_ORDER}
        total = sum(counts.values()) or 1
        ent = 0.0
        for count in counts.values():
            if count:
                p = count / total
                ent -= p * math.log2(p)
        out[i] = ent / math.log2(5)
    return out


def entropy_gated_pe(seq: str, length: int, dim: int = 16) -> np.ndarray:
    seq = pad_or_trim(seq, length)
    pe = sinusoidal_position_matrix(length, dim)
    ent = local_entropy(seq, window=9)[:, None]
    props = sequence_property_matrix(seq, length)
    biological_gate = 0.25 + 0.35 * props[:, 6:7] + 0.25 * props[:, 7:8] + 0.15 * props[:, 8:9]
    return pe * (0.5 + ent) * biological_gate


def spaced_kmer_property_sequence(
    seq: str,
    length: int,
    pattern: tuple[int, ...] = (0, 2, 4, 6),
    dim: int = 16,
    include_phase: bool = True,
) -> np.ndarray:
    seq = pad_or_trim(seq, length)
    span = max(pattern) + 1
    rows = []
    for start in range(0, max(0, len(seq) - span + 1)):
        picked = [seq[start + offset] for offset in pattern]
        props = np.vstack([base_property_vector(base) for base in picked])
        parts = [props.mean(axis=0), props.std(axis=0)]
        if include_phase:
            phase = np.array([math.sin(2 * math.pi * start / 3), math.cos(2 * math.pi * start / 3)], dtype=np.float64)
            parts.append(phase)
        rows.append(np.concatenate(parts))
    if not rows:
        return np.zeros((1, dim), dtype=np.float64)
    mat = np.vstack(rows)
    in_dim = mat.shape[1]
    weights = np.zeros((in_dim, dim), dtype=np.float64)
    for i in range(in_dim):
        for j in range(dim):
            weights[i, j] = math.sin((i + 1) * (j + 1) / 4.0)
    return mat @ weights / math.sqrt(in_dim)


def rc_consistent_pool(seq: str, length: int, dim: int = 16, base_scheme: str = "rope_property") -> np.ndarray:
    from .sequence_utils import reverse_complement

    if base_scheme == "rope_property":
        a = rope_like_rotation(seq, length, dim=dim, semantic="property")
        b = rope_like_rotation(reverse_complement(seq), length, dim=dim, semantic="property")
    elif base_scheme == "joint_phase":
        a = highdim_phase_joint(seq, length, dim=dim, mode="prior_residual")
        b = highdim_phase_joint(reverse_complement(seq), length, dim=dim, mode="prior_residual")
    else:
        raise ValueError(f"Unsupported RC base scheme: {base_scheme}")
    b = b[::-1, :]
    return np.concatenate([(a + b) / 2.0, np.abs(a - b)], axis=1)


def pool_matrix(mat: np.ndarray, pooling: str = "flatten") -> np.ndarray:
    if pooling == "flatten":
        return mat.ravel()
    if pooling == "mean":
        return mat.mean(axis=0)
    if pooling == "mean_std":
        return np.concatenate([mat.mean(axis=0), mat.std(axis=0)])
    if pooling == "fft":
        parts = []
        for col in range(mat.shape[1]):
            signal = mat[:, col] - mat[:, col].mean()
            power = np.abs(np.fft.rfft(signal)) ** 2
            parts.extend(power[: min(8, len(power))])
        return np.asarray(parts, dtype=np.float64)
    raise ValueError(f"Unsupported pooling: {pooling}")


def encode_position_sequences(
    sequences: list[str],
    scheme: str,
    length: int,
    dim: int = 16,
    pooling: str = "flatten",
    k: int = 3,
) -> np.ndarray:
    rows = []
    for seq in sequences:
        if scheme == "sinusoidal_pe":
            mat = sinusoidal_position_matrix(length, dim)
        elif scheme == "base_property":
            mat = sequence_property_matrix(seq, length)
        elif scheme == "joint_phase_prior":
            mat = highdim_phase_joint(seq, length, dim=dim, mode="prior")
        elif scheme == "joint_phase_learnable_proxy":
            mat = highdim_phase_joint(seq, length, dim=dim, mode="learnable_proxy")
        elif scheme == "joint_phase_prior_residual":
            mat = highdim_phase_joint(seq, length, dim=dim, mode="prior_residual")
        elif scheme == "gated_pe_gc":
            mat = attribute_gated_pe(seq, length, dim=dim, gate="scalar_gc")
        elif scheme == "gated_pe_hydrogen":
            mat = attribute_gated_pe(seq, length, dim=dim, gate="scalar_hydrogen")
        elif scheme == "gated_pe_multi":
            mat = attribute_gated_pe(seq, length, dim=dim, gate="multi_property")
        elif scheme == "gated_pe_learnable_proxy":
            mat = attribute_gated_pe(seq, length, dim=dim, gate="learnable_proxy")
        elif scheme == "rope_property":
            mat = rope_like_rotation(seq, length, dim=dim, semantic="property")
        elif scheme == "rope_onehot":
            mat = rope_like_rotation(seq, length, dim=dim, semantic="onehot")
        elif scheme == "kmer_property":
            mat = kmer_property_sequence(seq, length, k=k, dim=dim)
        elif scheme == "codon_frame_channels":
            mat = codon_frame_channels(seq, length, dim=dim)
        elif scheme == "entropy_gated_pe":
            mat = entropy_gated_pe(seq, length, dim=dim)
        elif scheme == "spaced_kmer_phase":
            mat = spaced_kmer_property_sequence(seq, length, pattern=(0, 2, 4, 6), dim=dim, include_phase=True)
        elif scheme == "spaced_kmer_no_phase":
            mat = spaced_kmer_property_sequence(seq, length, pattern=(0, 2, 4, 6), dim=dim, include_phase=False)
        elif scheme == "rc_rope_pool":
            mat = rc_consistent_pool(seq, length, dim=dim, base_scheme="rope_property")
        elif scheme == "rc_joint_phase_pool":
            mat = rc_consistent_pool(seq, length, dim=dim, base_scheme="joint_phase")
        else:
            raise ValueError(f"Unsupported position scheme: {scheme}")
        rows.append(pool_matrix(mat, pooling=pooling))
    return np.vstack(rows)
