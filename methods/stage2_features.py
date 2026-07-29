"""Stage-2 representation helpers.

The stage-2 experiments compare canonical k-mer composition evidence with compact CSP
auxiliary evidence. This module keeps feature construction shared across the
grid, ablation and readout scripts.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import re

import numpy as np
from scipy import sparse
from sklearn.preprocessing import normalize

from .base_encodings import EIIP, GC, HYDROGEN, PURINE, scalar_signal
from .representation_registry import build_representation
from .sequence_utils import kmer_tokens, shannon_entropy
from .sklearn_features import build_kmer_matrix, transform_feature_matrix
from .spaced_features import build_spaced_kmer_matrix, property_summary_matrix


PROPERTY_COMPONENTS = ("hydrogen", "gc", "purine", "eiip", "n_fraction", "entropy", "length")


@dataclass(frozen=True)
class FeatureInfo:
    name: str
    n_features: int
    density: float
    avg_nnz_per_read: float
    observed_vocab_size: int | None = None


def parse_hybrid_name(name: str) -> tuple[str, ...] | None:
    if name == "hybrid_ckmer5_csp":
        return ("ckmer5_count_l2", "cspaced_property_l2")
    if name == "hybrid_ckmer7_csp":
        return ("ckmer7_count_l2", "cspaced_property_l2")
    if name == "hybrid_ckmer5_cspaced":
        return ("ckmer5_count_l2", "cspaced_count_l2")
    if name.startswith("hybrid:"):
        return tuple(part.strip() for part in name.replace("hybrid:", "").split("+") if part.strip())
    return None


def _hash_to_unit_float(text: str) -> float:
    value = int.from_bytes(hashlib.blake2b(text.encode("utf-8"), digest_size=8).digest(), byteorder="big", signed=False)
    return value / float(2**64 - 1)


def minhash_sketch_matrix(
    sequences: list[str],
    k: int = 5,
    sketch_size: int = 128,
    canonical: bool = True,
) -> np.ndarray:
    """Build a deterministic MinHash sketch over observed k-mers.

    The sketch is a compact alignment-free control. It is intentionally not a
    classifier or a replacement for Mash; it gives the representation grid a
    fixed-width sketch baseline with deterministic seeds.
    """
    rows: list[np.ndarray] = []
    for seq in sequences:
        tokens = kmer_tokens(seq, k=k, canonical=canonical, ignore_n=True)
        if not tokens:
            rows.append(np.ones(sketch_size, dtype=np.float64))
            continue
        values = np.empty(sketch_size, dtype=np.float64)
        for seed in range(sketch_size):
            values[seed] = min(_hash_to_unit_float(f"{seed}:{token}") for token in tokens)
        rows.append(values)
    return normalize(np.vstack(rows), norm="l2", axis=1)


def eiip_summary_matrix(sequences: list[str], length: int) -> np.ndarray:
    """Low-dimensional EIIP-only control features."""
    rows: list[np.ndarray] = []
    for seq in sequences:
        signal = scalar_signal(seq, length, EIIP)
        nonzero = signal[signal > 0]
        if nonzero.size == 0:
            rows.append(np.zeros(8, dtype=np.float64))
            continue
        centered = signal - float(np.mean(signal))
        power = np.abs(np.fft.rfft(centered)) ** 2
        total_power = float(np.sum(power))
        probs = power / total_power if total_power > 0 else np.zeros_like(power)
        spectral_entropy = -float(np.sum([p * np.log2(p) for p in probs if p > 0]))
        rows.append(
            np.asarray(
                [
                    float(np.mean(signal)),
                    float(np.std(signal)),
                    float(np.min(nonzero)),
                    float(np.max(nonzero)),
                    float(np.median(nonzero)),
                    float(np.mean(np.abs(np.diff(signal)))) if signal.size > 1 else 0.0,
                    total_power,
                    spectral_entropy,
                ],
                dtype=np.float64,
            )
        )
    return normalize(np.vstack(rows), norm="l2", axis=1)


def selected_property_summary_matrix(
    sequences: list[str],
    components: tuple[str, ...] = PROPERTY_COMPONENTS,
) -> np.ndarray:
    """Build DNA property summaries with selectable components.

    Per-base tables contribute mean and standard deviation. Scalar read-level
    components contribute one column each.
    """
    rows: list[np.ndarray] = []
    for seq in sequences:
        seq = seq.upper()
        bases = [base for base in seq if base in "ACGTN"]
        n = max(1, len(bases))
        values: list[float] = []
        for name, table in (
            ("hydrogen", HYDROGEN),
            ("gc", GC),
            ("purine", PURINE),
            ("eiip", EIIP),
        ):
            if name not in components:
                continue
            arr = np.asarray([table.get(base, 0.0) for base in bases], dtype=np.float64)
            values.extend([float(arr.mean()) if arr.size else 0.0, float(arr.std()) if arr.size else 0.0])
        if "n_fraction" in components:
            values.append(sum(1 for base in bases if base == "N") / n)
        if "entropy" in components:
            values.append(shannon_entropy(seq) / np.log2(5))
        if "length" in components:
            values.append(len(seq) / 200.0)
        rows.append(np.asarray(values, dtype=np.float64))
    return np.vstack(rows)


def _training_sequences(sequences: list[str], train_indices: list[int] | None) -> list[str]:
    if train_indices is None:
        return sequences
    return [sequences[idx] for idx in train_indices]



PROPERTY_TABLES = (
    ("hydrogen", HYDROGEN),
    ("gc", GC),
    ("purine", PURINE),
    ("eiip", EIIP),
)


def _property_signal_matrix(seq: str) -> np.ndarray:
    bases = [base for base in seq.upper() if base in "ACGTN"]
    if not bases:
        bases = ["N"]
    channels = []
    for _, table in PROPERTY_TABLES:
        channels.append([table.get(base, 0.0) for base in bases])
    channels.append([1.0 if base == "N" else 0.0 for base in bases])
    return np.asarray(channels, dtype=np.float64).T


def _safe_normalize_dense(x: np.ndarray) -> np.ndarray:
    x = np.nan_to_num(np.asarray(x, dtype=np.float64), nan=0.0, posinf=0.0, neginf=0.0)
    return normalize(x, norm="l2", axis=1)


def property_multiscale_matrix(
    sequences: list[str],
    bins: tuple[int, ...] = (2, 3, 4, 6),
    include_std: bool = True,
) -> np.ndarray:
    """Multi-resolution property pooling over fixed relative-position bins."""
    rows: list[np.ndarray] = []
    for seq in sequences:
        mat = _property_signal_matrix(seq)
        n = mat.shape[0]
        values: list[float] = []
        for n_bins in bins:
            edges = np.linspace(0, n, n_bins + 1)
            for left_f, right_f in zip(edges[:-1], edges[1:]):
                left = int(np.floor(left_f))
                right = int(np.floor(right_f))
                if right <= left:
                    right = min(n, left + 1)
                block = mat[left:right]
                if block.size == 0:
                    block = np.zeros((1, mat.shape[1]), dtype=np.float64)
                means = block.mean(axis=0)
                values.extend(float(v) for v in means)
                if include_std:
                    stds = block.std(axis=0)
                    values.extend(float(v) for v in stds)
        rows.append(np.asarray(values, dtype=np.float64))
    return _safe_normalize_dense(np.vstack(rows))


def property_positional_moment_matrix(sequences: list[str]) -> np.ndarray:
    """Compact soft positional moments for biochemical property channels."""
    rows: list[np.ndarray] = []
    for seq in sequences:
        mat = _property_signal_matrix(seq)
        n = mat.shape[0]
        coords = np.linspace(0.0, 1.0, n, dtype=np.float64) if n > 1 else np.asarray([0.0], dtype=np.float64)
        centered_coords = coords - 0.5
        left_mask = coords < 0.5
        right_mask = ~left_mask
        terminal_mask = (coords <= 0.2) | (coords >= 0.8)
        middle_mask = ~terminal_mask
        values: list[float] = []
        for channel_idx in range(mat.shape[1]):
            channel = mat[:, channel_idx]
            mean = float(channel.mean())
            std = float(channel.std())
            total = float(channel.sum())
            if total > 1e-12:
                center = float(np.sum(channel * coords) / total)
                variance = float(np.sum(channel * (coords - center) ** 2) / total)
                third = float(np.sum(channel * (coords - center) ** 3) / total)
            else:
                center = 0.0
                variance = 0.0
                third = 0.0
            left_mean = float(channel[left_mask].mean()) if np.any(left_mask) else mean
            right_mean = float(channel[right_mask].mean()) if np.any(right_mask) else mean
            terminal_mean = float(channel[terminal_mask].mean()) if np.any(terminal_mask) else mean
            middle_mean = float(channel[middle_mask].mean()) if np.any(middle_mask) else mean
            denom = float(np.sum(centered_coords**2))
            slope = float(np.sum((channel - mean) * centered_coords) / denom) if denom > 1e-12 else 0.0
            values.extend(
                [
                    mean,
                    std,
                    center,
                    variance,
                    third,
                    right_mean - left_mean,
                    terminal_mean - middle_mean,
                    slope,
                ]
            )
        rows.append(np.asarray(values, dtype=np.float64))
    return _safe_normalize_dense(np.vstack(rows))


def _window_entropy(chars: list[str]) -> float:
    if not chars:
        return 0.0
    counts = {base: chars.count(base) for base in "ACGTN"}
    total = sum(counts.values())
    if total == 0:
        return 0.0
    entropy = 0.0
    for count in counts.values():
        if count:
            p = count / total
            entropy -= p * np.log2(p)
    return float(entropy)


def _rare_kmer_scores(train_sequences: list[str], k: int = 4) -> dict[str, float]:
    counts: dict[str, int] = {}
    for seq in train_sequences:
        for token in kmer_tokens(seq, k=k, canonical=True, ignore_n=True):
            counts[token] = counts.get(token, 0) + 1
    if not counts:
        return {}
    max_count = max(counts.values())
    return {token: 1.0 - (count / max_count) for token, count in counts.items()}


def _anchor_positions(seq: str, rare_scores: dict[str, float] | None = None, k: int = 4) -> list[tuple[str, int]]:
    seq = seq.upper()
    if not seq:
        return [("gc_shift", 0), ("entropy", 0), ("rare_kmer", 0)]
    chars = [base if base in "ACGTN" else "N" for base in seq]
    n = len(chars)
    window = max(5, min(21, n // 5 if n >= 25 else n))
    window = max(1, min(window, n))
    global_gc = sum(1 for base in chars if base in "GC") / max(1, sum(1 for base in chars if base in "ACGT"))
    gc_best = (0.0, n // 2)
    entropy_best = (-1.0, n // 2)
    for start in range(0, n - window + 1):
        block = chars[start:start + window]
        valid = [base for base in block if base in "ACGT"]
        local_gc = sum(1 for base in valid if base in "GC") / max(1, len(valid))
        gc_score = abs(local_gc - global_gc)
        if gc_score > gc_best[0]:
            gc_best = (gc_score, start + window // 2)
        ent = _window_entropy(block)
        if ent > entropy_best[0]:
            entropy_best = (ent, start + window // 2)
    rare_best = (-1.0, n // 2)
    if rare_scores and n >= k:
        for start in range(0, n - k + 1):
            token = seq[start:start + k]
            if "N" in token:
                continue
            from .sequence_utils import reverse_complement

            token = min(token, reverse_complement(token))
            score = rare_scores.get(token, 1.0)
            if score > rare_best[0]:
                rare_best = (score, start + k // 2)
    return [("gc_shift", gc_best[1]), ("entropy", entropy_best[1]), ("rare_kmer", rare_best[1])]


def property_anchor_adaptive_matrix(
    sequences: list[str],
    train_indices: list[int] | None = None,
    k: int = 4,
) -> np.ndarray:
    """Anchor-centered left/local/right property summaries with train-only rare-kmer scores."""
    train_sequences = _training_sequences(sequences, train_indices)
    rare_scores = _rare_kmer_scores(train_sequences, k=k)
    rows: list[np.ndarray] = []
    for seq in sequences:
        mat = _property_signal_matrix(seq)
        n = mat.shape[0]
        anchors = _anchor_positions(seq, rare_scores=rare_scores, k=k)
        values: list[float] = []
        radius = max(2, int(round(n * 0.1)))
        global_mean = mat.mean(axis=0)
        for _, anchor in anchors:
            anchor = int(max(0, min(n - 1, anchor)))
            left = mat[:anchor]
            local = mat[max(0, anchor - radius): min(n, anchor + radius + 1)]
            right = mat[anchor + 1:]
            left_mean = left.mean(axis=0) if left.size else global_mean
            local_mean = local.mean(axis=0) if local.size else global_mean
            local_std = local.std(axis=0) if local.size else np.zeros(mat.shape[1], dtype=np.float64)
            right_mean = right.mean(axis=0) if right.size else global_mean
            values.append(float(anchor / max(1, n - 1)))
            values.extend(float(v) for v in left_mean)
            values.extend(float(v) for v in local_mean)
            values.extend(float(v) for v in local_std)
            values.extend(float(v) for v in right_mean)
            values.extend(float(v) for v in (right_mean - left_mean))
        rows.append(np.asarray(values, dtype=np.float64))
    return _safe_normalize_dense(np.vstack(rows))


def build_position_property_matrix(
    sequences: list[str],
    property_name: str,
    train_indices: list[int] | None = None,
) -> np.ndarray:
    if property_name == "property":
        return _safe_normalize_dense(property_summary_matrix(sequences))
    if property_name == "property_multiscale":
        return property_multiscale_matrix(sequences, include_std=True)
    if property_name == "property_multiscale_mean":
        return property_multiscale_matrix(sequences, include_std=False)
    if property_name == "property_moment":
        return property_positional_moment_matrix(sequences)
    if property_name == "property_anchor":
        return property_anchor_adaptive_matrix(sequences, train_indices=train_indices)
    raise ValueError(f"Unsupported property block: {property_name}")


def canonical_kmer_plus_property_matrix(
    sequences: list[str],
    k: int,
    property_name: str,
    train_indices: list[int] | None = None,
) -> np.ndarray:
    train_sequences = _training_sequences(sequences, train_indices)
    _, vocabulary = build_kmer_matrix(train_sequences, k=k, canonical=True, vocabulary_mode="observed")
    counts, _ = build_kmer_matrix(sequences, k=k, canonical=True, vocabulary=vocabulary)
    counts, _ = transform_feature_matrix(counts, feature_type="count", normalization="l2", train_indices=train_indices)
    global_props = property_summary_matrix(sequences)
    if property_name == "property":
        props = global_props
    else:
        position_props = build_position_property_matrix(sequences, property_name, train_indices=train_indices)
        props = np.hstack([global_props, position_props])
    return _safe_normalize_dense(np.hstack([counts.toarray(), props]))


def canonical_kmer_property_matrix(
    sequences: list[str],
    k: int,
    train_indices: list[int] | None = None,
) -> np.ndarray:
    """Canonical contiguous k-mer counts plus the same property summaries used by CSP."""
    return canonical_kmer_plus_property_matrix(sequences, k=k, property_name="property", train_indices=train_indices)


def canonical_spaced_pattern_matrix(
    sequences: list[str],
    pattern: tuple[int, ...],
    add_property: bool,
    train_indices: list[int] | None = None,
) -> np.ndarray:
    """Canonical spaced counts for an explicit seed pattern, optionally plus CSP property summaries."""
    train_sequences = _training_sequences(sequences, train_indices)
    _, vocabulary = build_spaced_kmer_matrix(train_sequences, pattern=pattern, canonical=True, vocabulary_mode="observed")
    counts, _ = build_spaced_kmer_matrix(sequences, pattern=pattern, canonical=True, vocabulary=vocabulary)
    base = normalize(counts, norm="l2", axis=1).toarray()
    if not add_property:
        return base
    props = property_summary_matrix(sequences)
    return normalize(np.hstack([base, props]), norm="l2", axis=1)


def parse_compact_pattern(text: str) -> tuple[int, ...]:
    if not text.isdigit():
        raise ValueError(f"Pattern name must contain only digits: {text}")
    return tuple(int(char) for char in text)


def build_feature_matrix(
    sequences: list[str],
    name: str,
    length: int,
    train_indices: list[int] | None = None,
) -> tuple[np.ndarray, FeatureInfo]:
    """Build a dense feature matrix and lightweight metadata."""
    # The manuscript-facing mixed method has a dedicated implementation.
    # Keep the historical ``ckmer*_property_*`` names below for archived
    # experiments, but do not use them as aliases for CK4P-MSP.
    public_block_names = {"ck4", "p", "msp", "ck4_p", "ck4_msp", "p_msp", "ck4p_msp"}
    if name in public_block_names:
        from .ck4p_msp import (
            BLOCK_COMBINATIONS,
            build_ck4_block,
            build_msp_block,
            build_p_block,
            build_property_blocks,
        )

        selected = BLOCK_COMBINATIONS[name]
        shared_property_blocks: dict[str, np.ndarray] = {}
        if "P" in selected and "M" in selected:
            p_block, msp_block = build_property_blocks(sequences)
            shared_property_blocks = {"P": p_block, "M": msp_block}
        blocks: list[np.ndarray] = []
        for block_name in selected:
            if block_name == "K":
                block, _ = build_ck4_block(sequences, train_indices=train_indices)
            elif block_name == "P":
                block = shared_property_blocks.get("P")
                if block is None:
                    block = build_p_block(sequences)
            elif block_name == "M":
                block = shared_property_blocks.get("M")
                if block is None:
                    block = build_msp_block(sequences)
            else:  # pragma: no cover - guarded by the public contract mapping.
                raise ValueError(f"Unsupported public block: {block_name}")
            blocks.append(block)
        x = np.hstack(blocks) / np.sqrt(float(len(blocks)))
        nnz = np.count_nonzero(np.abs(x) > 1e-12)
        total = x.shape[0] * x.shape[1]
        return x, FeatureInfo(
            name=name,
            n_features=int(x.shape[1]),
            density=float(nnz / total) if total else 0.0,
            avg_nnz_per_read=float(nnz / max(1, x.shape[0])),
            observed_vocab_size=None,
        )

    historical_descriptor_names = {"pseknc_k3_l3", "ncp_anf", "pseeiip"}
    if name in historical_descriptor_names:
        from .historical_descriptors import build_historical_descriptor_matrix

        x = build_historical_descriptor_matrix(sequences, name, length=length)
        nnz = np.count_nonzero(np.abs(x) > 1e-12)
        total = x.shape[0] * x.shape[1]
        return x, FeatureInfo(
            name=name,
            n_features=int(x.shape[1]),
            density=float(nnz / total) if total else 0.0,
            avg_nnz_per_read=float(nnz / max(1, x.shape[0])),
            observed_vocab_size=None,
        )

    parts = parse_hybrid_name(name)
    minhash_match = re.fullmatch(r"minhash_k(\d+)_s(\d+)", name)
    ckmer_property_match = re.fullmatch(r"ckmer(\d+)_(property|property_multiscale|property_multiscale_mean|property_moment|property_anchor)_l2", name)
    property_block_match = re.fullmatch(r"(property|property_multiscale|property_multiscale_mean|property_moment|property_anchor)_l2", name)
    cspaced_pattern_match = re.fullmatch(r"cspaced_p([0-9]+)_(count|property)_l2", name)
    if parts:
        matrices = [build_feature_matrix(sequences, part, length, train_indices=train_indices)[0] for part in parts]
        x = np.hstack(matrices)
        x = normalize(x, norm="l2", axis=1)
    elif ckmer_property_match:
        x = canonical_kmer_plus_property_matrix(
            sequences,
            k=int(ckmer_property_match.group(1)),
            property_name=ckmer_property_match.group(2),
            train_indices=train_indices,
        )
    elif property_block_match:
        x = build_position_property_matrix(sequences, property_block_match.group(1), train_indices=train_indices)
    elif cspaced_pattern_match:
        pattern = parse_compact_pattern(cspaced_pattern_match.group(1))
        x = canonical_spaced_pattern_matrix(
            sequences,
            pattern=pattern,
            add_property=cspaced_pattern_match.group(2) == "property",
            train_indices=train_indices,
        )
    elif minhash_match:
        x = minhash_sketch_matrix(
            sequences,
            k=int(minhash_match.group(1)),
            sketch_size=int(minhash_match.group(2)),
            canonical=True,
        )
    elif name == "eiip_l2":
        x = normalize(np.vstack([scalar_signal(seq, length, EIIP) for seq in sequences]), norm="l2", axis=1)
    elif name == "eiip_summary_l2":
        x = eiip_summary_matrix(sequences, length=length)
    elif name.startswith("cspaced_property_selected:"):
        component_text = name.split(":", 1)[1]
        components = tuple(part for part in component_text.split("+") if part)
        base = build_representation(sequences, "cspaced_count_l2", length=length, train_indices=train_indices)
        props = selected_property_summary_matrix(sequences, components=components)
        x = normalize(np.hstack([base, props]), norm="l2", axis=1)
    elif name.startswith("property_summary:"):
        component_text = name.split(":", 1)[1]
        components = tuple(part for part in component_text.split("+") if part)
        x = normalize(selected_property_summary_matrix(sequences, components=components), norm="l2", axis=1)
    else:
        x = build_representation(sequences, name, length=length, train_indices=train_indices)
        if sparse.issparse(x):
            x = x.toarray()
        else:
            x = np.asarray(x, dtype=np.float64)

    if x.ndim != 2:
        x = np.asarray(x).reshape(len(sequences), -1)
    nnz = np.count_nonzero(np.abs(x) > 1e-12)
    total = x.shape[0] * x.shape[1]
    info = FeatureInfo(
        name=name,
        n_features=int(x.shape[1]),
        density=float(nnz / total) if total else 0.0,
        avg_nnz_per_read=float(nnz / max(1, x.shape[0])),
        observed_vocab_size=None,
    )
    return x, info


def cosine_diag(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    a_norm = normalize(a, norm="l2", axis=1)
    b_norm = normalize(b, norm="l2", axis=1)
    return np.sum(a_norm * b_norm, axis=1)


def l2_delta(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    a_norm = normalize(a, norm="l2", axis=1)
    b_norm = normalize(b, norm="l2", axis=1)
    return np.linalg.norm(a_norm - b_norm, axis=1)


def paired_retrieval_metrics(clean_x: np.ndarray, pert_x: np.ndarray) -> dict[str, float]:
    clean_norm = normalize(clean_x, norm="l2", axis=1)
    pert_norm = normalize(pert_x, norm="l2", axis=1)
    sim = pert_norm @ clean_norm.T
    diag = np.diag(sim)
    top1 = np.argmax(sim, axis=1) == np.arange(sim.shape[0])
    sorted_sim = np.sort(sim, axis=1)
    nearest_nonpaired = np.where(sim.shape[1] > 1, sorted_sim[:, -2], np.nan)
    return {
        "retrieval_top1": float(np.mean(top1)),
        "paired_cosine_mean": float(np.mean(diag)),
        "paired_cosine_p05": float(np.quantile(diag, 0.05)),
        "l2_delta_mean": float(np.mean(l2_delta(clean_x, pert_x))),
        "l2_delta_p95": float(np.quantile(l2_delta(clean_x, pert_x), 0.95)),
        "mean_pair_margin": float(np.nanmean(diag - nearest_nonpaired)),
        "margin_positive_rate": float(np.mean(diag > nearest_nonpaired)) if sim.shape[1] > 1 else 1.0,
    }
