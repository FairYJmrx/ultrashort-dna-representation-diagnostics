"""Stage-2 representation helpers.

The stage-2 experiments compare exact-identity k-mer evidence with compact CSP
auxiliary evidence. This module keeps feature construction shared across the
grid, ablation and readout scripts.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy import sparse
from sklearn.preprocessing import normalize

from .base_encodings import EIIP, GC, HYDROGEN, PURINE
from .representation_registry import build_representation
from .sequence_utils import shannon_entropy


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


def build_feature_matrix(
    sequences: list[str],
    name: str,
    length: int,
    train_indices: list[int] | None = None,
) -> tuple[np.ndarray, FeatureInfo]:
    """Build a dense feature matrix and lightweight metadata."""
    parts = parse_hybrid_name(name)
    if parts:
        matrices = [build_feature_matrix(sequences, part, length, train_indices=train_indices)[0] for part in parts]
        x = np.hstack(matrices)
        x = normalize(x, norm="l2", axis=1)
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
