"""Representative pre-deep-learning DNA sequence descriptors.

The implementations in this module provide transparent historical controls for
the manuscript's representation audit. They follow the default definitions
used by iFeatureOmega for PseKNC, nucleotide chemical property (NCP),
accumulated nucleotide frequency (ANF), and PseEIIP, with one declared
extension: ambiguous bases are retained through deterministic zero/skip rules
instead of causing the whole read to fail.

These controls are not aliases for CK4P-MSP. Their purpose is to test whether
the proposed K/P/MSP decomposition provides a distinct audit profile relative
to established composition-property and position-aware handcrafted encoders.
"""

from __future__ import annotations

import itertools
from collections.abc import Sequence

import numpy as np
from sklearn.preprocessing import normalize


BASES = "ACGT"
DINUCLEOTIDES = tuple("".join(item) for item in itertools.product(BASES, repeat=2))
TRINUCLEOTIDES = tuple("".join(item) for item in itertools.product(BASES, repeat=3))

EIIP = {"A": 0.1260, "C": 0.1340, "G": 0.0806, "T": 0.1335}
NCP = {
    "A": (1.0, 1.0, 1.0),
    "C": (0.0, 1.0, 0.0),
    "G": (1.0, 0.0, 0.0),
    "T": (0.0, 0.0, 1.0),
    "N": (0.0, 0.0, 0.0),
}

# Standardized dinucleotide structural-property values used by the default
# PseKNC/PseDNC configuration in iFeatureOmega. Columns follow
# AA, AC, AG, AT, CA, CC, CG, CT, GA, GC, GG, GT, TA, TC, TG, TT.
PSEKNC_DINUCLEOTIDE_PROPERTIES = np.asarray(
    [
        [-0.109, 1.044, -0.623, 1.171, -1.254, 0.242, -1.389, -0.623, 0.711, 1.585, 0.242, 1.044, -1.389, 0.711, -1.254, -0.109],  # Rise
        [0.090, 1.190, -0.280, 0.830, -1.010, -0.280, -1.380, -0.280, 0.090, 2.300, -0.280, 1.190, -1.380, 0.090, -1.010, 0.090],  # Roll
        [1.587, 0.126, 0.679, -1.019, -0.861, 0.560, -0.822, 0.679, 0.126, -0.348, 0.560, 0.126, -2.243, 0.126, -0.861, 1.587],  # Shift
        [0.111, 1.289, -0.241, 2.513, -0.623, -0.822, -0.287, -0.241, -0.394, 0.646, -0.822, 1.289, -1.511, -0.394, -0.623, 0.111],  # Slide
        [0.502, 0.502, 0.359, 0.215, -1.364, 1.077, -1.220, 0.359, 0.502, 0.215, 1.077, 0.502, -2.368, 0.502, -1.364, 0.502],  # Tilt
        [0.063, 1.502, 0.783, 1.071, -1.376, 0.063, -1.664, 0.783, -0.081, -0.081, 0.063, 1.502, -1.233, -0.081, -1.376, 0.063],  # Twist
    ],
    dtype=np.float64,
)
DINUCLEOTIDE_INDEX = {token: idx for idx, token in enumerate(DINUCLEOTIDES)}


def _normalize_rows(matrix: np.ndarray) -> np.ndarray:
    matrix = np.nan_to_num(np.asarray(matrix, dtype=np.float64), nan=0.0, posinf=0.0, neginf=0.0)
    return normalize(matrix, norm="l2", axis=1)


def _fixed_length_sequence(sequence: str, length: int) -> str:
    sequence = str(sequence).upper().replace("U", "T")
    sequence = "".join(base if base in "ACGT" else "N" for base in sequence)
    if len(sequence) >= length:
        return sequence[:length]
    return sequence + ("N" * (length - len(sequence)))


def ncp_anf_matrix(sequences: Sequence[str], length: int) -> np.ndarray:
    """Return interleaved NCP and ANF coordinates (four values per position).

    NCP encodes ring structure, chemical functionality and hydrogen-bond class.
    ANF is the cumulative frequency of the current symbol in the sequence
    prefix. Reads are padded with N to keep the declared source-length budget;
    N has a zero NCP code and its own cumulative frequency.
    """
    rows: list[np.ndarray] = []
    for raw_sequence in sequences:
        sequence = _fixed_length_sequence(raw_sequence, length)
        counts: dict[str, int] = {}
        values: list[float] = []
        for position, base in enumerate(sequence, start=1):
            counts[base] = counts.get(base, 0) + 1
            values.extend(NCP[base])
            values.append(counts[base] / position)
        rows.append(np.asarray(values, dtype=np.float64))
    return _normalize_rows(np.vstack(rows))


def pseeiip_matrix(sequences: Sequence[str]) -> np.ndarray:
    """Return the 64-dimensional pseudo-EIIP trinucleotide descriptor.

    Each coordinate is the normalized trinucleotide frequency multiplied by
    the sum of the three nucleotide EIIP values. Windows containing ambiguous
    bases contribute zero while the denominator remains the number of possible
    windows, making the extension deterministic for N-masked reads.
    """
    tri_index = {token: idx for idx, token in enumerate(TRINUCLEOTIDES)}
    tri_eiip = np.asarray([sum(EIIP[base] for base in token) for token in TRINUCLEOTIDES])
    rows: list[np.ndarray] = []
    for raw_sequence in sequences:
        sequence = str(raw_sequence).upper().replace("U", "T")
        counts = np.zeros(len(TRINUCLEOTIDES), dtype=np.float64)
        denominator = max(1, len(sequence) - 2)
        for start in range(max(0, len(sequence) - 2)):
            token = sequence[start:start + 3]
            idx = tri_index.get(token)
            if idx is not None:
                counts[idx] += 1.0
        rows.append((counts / denominator) * tri_eiip)
    return _normalize_rows(np.vstack(rows))


def _valid_dinucleotide_pairs(sequence: str, lag: int) -> list[tuple[str, str]]:
    pairs: list[tuple[str, str]] = []
    offset = lag
    dinucleotides = [sequence[idx:idx + 2] for idx in range(max(0, len(sequence) - 1))]
    for idx in range(max(0, len(dinucleotides) - offset)):
        left = dinucleotides[idx]
        right = dinucleotides[idx + offset]
        if left in DINUCLEOTIDE_INDEX and right in DINUCLEOTIDE_INDEX:
            pairs.append((left, right))
    return pairs


def pseknc_matrix(
    sequences: Sequence[str],
    *,
    k: int = 3,
    lambda_value: int = 3,
    weight: float = 0.05,
) -> np.ndarray:
    """Return Type-I PseKNC with the standard six dinucleotide properties.

    Defaults match the common iFeatureOmega configuration (k=3, lambda=3,
    weight=0.05). Invalid k-mer windows are omitted from counts and retain zero
    mass under the total-window denominator. Correlation terms average only
    valid dinucleotide pairs; a lag with no valid pair contributes zero.
    """
    if k < 1:
        raise ValueError("k must be positive")
    if lambda_value < 0:
        raise ValueError("lambda_value must be non-negative")
    if weight < 0:
        raise ValueError("weight must be non-negative")

    kmers = tuple("".join(item) for item in itertools.product(BASES, repeat=k))
    kmer_index = {token: idx for idx, token in enumerate(kmers)}
    rows: list[np.ndarray] = []
    for raw_sequence in sequences:
        sequence = str(raw_sequence).upper().replace("U", "T")
        counts = np.zeros(len(kmers), dtype=np.float64)
        denominator = max(1, len(sequence) - k + 1)
        for start in range(max(0, len(sequence) - k + 1)):
            token = sequence[start:start + k]
            idx = kmer_index.get(token)
            if idx is not None:
                counts[idx] += 1.0
        frequencies = counts / denominator

        theta: list[float] = []
        for lag in range(1, lambda_value + 1):
            pairs = _valid_dinucleotide_pairs(sequence, lag)
            if not pairs:
                theta.append(0.0)
                continue
            squared_differences = []
            for left, right in pairs:
                left_values = PSEKNC_DINUCLEOTIDE_PROPERTIES[:, DINUCLEOTIDE_INDEX[left]]
                right_values = PSEKNC_DINUCLEOTIDE_PROPERTIES[:, DINUCLEOTIDE_INDEX[right]]
                squared_differences.append(float(np.mean((left_values - right_values) ** 2)))
            theta.append(float(np.mean(squared_differences)))

        theta_array = np.asarray(theta, dtype=np.float64)
        scale = 1.0 + weight * float(np.sum(theta_array))
        rows.append(np.concatenate([frequencies / scale, weight * theta_array / scale]))
    return _normalize_rows(np.vstack(rows))


def build_historical_descriptor_matrix(
    sequences: Sequence[str],
    name: str,
    *,
    length: int,
) -> np.ndarray:
    """Build one manuscript historical-control matrix by registry name."""
    if name == "pseknc_k3_l3":
        return pseknc_matrix(sequences, k=3, lambda_value=3, weight=0.05)
    if name == "ncp_anf":
        return ncp_anf_matrix(sequences, length=length)
    if name == "pseeiip":
        return pseeiip_matrix(sequences)
    raise ValueError(f"Unsupported historical descriptor: {name}")

