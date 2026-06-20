"""Build matrices for named lightweight representations."""

from __future__ import annotations

import numpy as np
from scipy import sparse
from sklearn.preprocessing import normalize

from .base_encodings import encode_sequences
from .position_encodings import encode_position_sequences
from .sklearn_features import build_kmer_matrix, transform_feature_matrix
from .spaced_features import spaced_count_dense


def parse_kmer_representation(name: str) -> tuple[int, str, str, bool] | None:
    """Parse k-mer representation names.

    Supported forms:
    - kmer5_count_l2
    - kmer7_tfidf_l2
    - ckmer5_count_l2, where c means canonical reverse-complement k-mers.
    """
    canonical = False
    if name.startswith("ckmer"):
        canonical = True
        prefix = "ckmer"
    elif name.startswith("kmer"):
        prefix = "kmer"
    else:
        return None

    parts = name.split("_")
    k = int(parts[0].replace(prefix, ""))
    feature_type = parts[1] if len(parts) > 1 else "count"
    normalization = parts[2] if len(parts) > 2 else "l2"
    if feature_type == "frequency":
        feature_type = "relative_frequency"
    return k, feature_type, normalization, canonical


def build_representation(
    sequences: list[str],
    name: str,
    length: int,
    train_indices: list[int] | None = None,
    seed: int = 13,
) -> np.ndarray:
    """Return dense representation matrix for diagnostics and retrieval."""
    parsed_kmer = parse_kmer_representation(name)
    if parsed_kmer:
        k, feature_type, normalization, canonical = parsed_kmer
        mat, _ = build_kmer_matrix(sequences, k=k, canonical=canonical, vocabulary_mode="observed")
        if train_indices is None:
            train_indices = list(range(len(sequences)))
        feat, _ = transform_feature_matrix(mat, feature_type=feature_type, normalization=normalization, train_indices=train_indices)
        return feat.toarray() if sparse.issparse(feat) else np.asarray(feat)

    if name == "spaced_count_l2":
        return spaced_count_dense(sequences, canonical=False, train_indices=train_indices, add_property_summary=False)
    if name == "cspaced_count_l2":
        return spaced_count_dense(sequences, canonical=True, train_indices=train_indices, add_property_summary=False)
    if name == "cspaced_property_l2":
        return spaced_count_dense(sequences, canonical=True, train_indices=train_indices, add_property_summary=True)

    base_names = {
        "one_hot",
        "voss",
        "tetrahedron",
        "property_channels",
        "three_phase",
        "eiip",
        "hydrogen_bond_scalar",
        "fft_eiip",
        "fft_three_phase",
        "summary_entropy",
    }
    if name in base_names:
        return encode_sequences(sequences, name, length)

    position_names = {
        "base_property",
        "joint_phase_prior",
        "joint_phase_prior_residual",
        "rope_property",
        "rope_onehot",
        "codon_frame_channels",
        "entropy_gated_pe",
        "spaced_kmer_phase",
        "spaced_kmer_no_phase",
        "rc_rope_pool",
        "rc_joint_phase_pool",
        "kmer_property",
    }
    if name in position_names:
        return encode_position_sequences(
            sequences,
            scheme=name,
            length=length,
            dim=16,
            pooling="flatten",
            k=5,
        )

    raise ValueError(f"Unsupported representation: {name}")


def l2_normalize_dense(x: np.ndarray) -> np.ndarray:
    return normalize(x, norm="l2", axis=1)
