"""Raw-base and DNA signal feature encodings."""

from __future__ import annotations

import math

import numpy as np

from .sequence_utils import shannon_entropy

BASE_TO_IDX = {"A": 0, "C": 1, "G": 2, "T": 3}
EIIP = {"A": 0.1260, "C": 0.1340, "G": 0.0806, "T": 0.1335, "N": 0.0}
HYDROGEN = {"A": 2.0, "T": 2.0, "C": 3.0, "G": 3.0, "N": 0.0}
PURINE = {"A": 1.0, "G": 1.0, "C": 0.0, "T": 0.0, "N": 0.0}
GC = {"G": 1.0, "C": 1.0, "A": 0.0, "T": 0.0, "N": 0.0}
TETRAHEDRON = {
    "A": np.array([1.0, 1.0, 1.0], dtype=np.float64),
    "C": np.array([1.0, -1.0, -1.0], dtype=np.float64),
    "G": np.array([-1.0, 1.0, -1.0], dtype=np.float64),
    "T": np.array([-1.0, -1.0, 1.0], dtype=np.float64),
    "N": np.array([0.0, 0.0, 0.0], dtype=np.float64),
}


def pad_or_trim(seq: str, length: int) -> str:
    seq = seq.upper()
    if len(seq) >= length:
        return seq[:length]
    return seq + ("N" * (length - len(seq)))


def one_hot(seq: str, length: int) -> np.ndarray:
    seq = pad_or_trim(seq, length)
    arr = np.zeros((length, 5), dtype=np.float64)
    for i, base in enumerate(seq):
        if base in BASE_TO_IDX:
            arr[i, BASE_TO_IDX[base]] = 1.0
        else:
            arr[i, 4] = 1.0
    return arr.ravel()


def scalar_signal(seq: str, length: int, table: dict[str, float]) -> np.ndarray:
    seq = pad_or_trim(seq, length)
    return np.array([table.get(base, 0.0) for base in seq], dtype=np.float64)


def property_channels(seq: str, length: int) -> np.ndarray:
    seq = pad_or_trim(seq, length)
    channels = []
    for table in (HYDROGEN, GC, PURINE, EIIP):
        channels.append([table.get(base, 0.0) for base in seq])
    channels.append([1.0 if base == "N" else 0.0 for base in seq])
    return np.asarray(channels, dtype=np.float64).T.ravel()


def tetrahedron(seq: str, length: int) -> np.ndarray:
    seq = pad_or_trim(seq, length)
    return np.vstack([TETRAHEDRON.get(base, TETRAHEDRON["N"]) for base in seq]).ravel()


def three_phase_signal(seq: str, length: int, omega: float | None = None) -> np.ndarray:
    seq = pad_or_trim(seq, length)
    omega = omega if omega is not None else 2.0 * math.pi / 3.0
    values = np.zeros(length, dtype=np.float64)
    for i, base in enumerate(seq):
        phase = 2.0 * math.pi * (i % 3) / 3.0
        values[i] = HYDROGEN.get(base, 0.0) * math.cos(omega * i + phase)
    return values


def fft_power_features(signal: np.ndarray, n_bins: int = 16) -> np.ndarray:
    if signal.size == 0:
        return np.zeros(n_bins + 2, dtype=np.float64)
    centered = signal - np.mean(signal)
    power = np.abs(np.fft.rfft(centered)) ** 2
    if power.size == 0:
        power = np.zeros(1, dtype=np.float64)
    bins = np.zeros(n_bins, dtype=np.float64)
    take = min(n_bins, power.size)
    bins[:take] = power[:take]
    total = float(np.sum(power))
    probs = power / total if total > 0 else np.zeros_like(power)
    spectral_entropy = -float(np.sum([p * math.log2(p) for p in probs if p > 0]))
    return np.concatenate([bins, np.array([total, spectral_entropy], dtype=np.float64)])


def encode_sequences(sequences: list[str], encoding: str, length: int) -> np.ndarray:
    rows = []
    for seq in sequences:
        if encoding in {"one_hot", "voss"}:
            rows.append(one_hot(seq, length))
        elif encoding == "eiip":
            rows.append(scalar_signal(seq, length, EIIP))
        elif encoding == "hydrogen_bond_scalar":
            rows.append(scalar_signal(seq, length, HYDROGEN))
        elif encoding == "property_channels":
            rows.append(property_channels(seq, length))
        elif encoding == "tetrahedron":
            rows.append(tetrahedron(seq, length))
        elif encoding == "three_phase":
            rows.append(three_phase_signal(seq, length))
        elif encoding == "fft_eiip":
            rows.append(fft_power_features(scalar_signal(seq, length, EIIP)))
        elif encoding == "fft_three_phase":
            rows.append(fft_power_features(three_phase_signal(seq, length)))
        elif encoding == "summary_entropy":
            rows.append(
                np.array(
                    [shannon_entropy(seq), len(seq), seq.upper().count("N") / max(1, len(seq))],
                    dtype=np.float64,
                )
            )
        else:
            raise ValueError(f"Unsupported encoding: {encoding}")
    return np.vstack(rows)

