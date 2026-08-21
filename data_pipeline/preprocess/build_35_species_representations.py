"""Build fixed representations from a 35-species FASTQ in bounded batches.

The script is intentionally data-source agnostic: it reads one FASTQ stream,
keeps only one batch of sequences in memory, and writes one ``.npy`` matrix
per requested representation. The output row order is the FASTQ record order
and must therefore be used with the aligned label array.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Iterator

import numpy as np

# Allow both ``python -m ...`` and the documented direct script invocation.
REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from methods.ck4p_msp import CK4PMSPConfig, build_ck4_block, build_ck4p_msp_features
from methods.stage2_features import build_feature_matrix


def sha256_file(path: Path, chunk_size: int = 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(chunk_size), b""):
            digest.update(chunk)
    return digest.hexdigest()


def iter_fastq(path: Path) -> Iterator[str]:
    with path.open("rt", encoding="ascii", errors="replace") as handle:
        while True:
            header = handle.readline()
            if not header:
                return
            sequence = handle.readline().strip()
            plus = handle.readline()
            quality = handle.readline()
            if not plus or not quality or not header.startswith("@") or not plus.startswith("+"):
                raise ValueError(f"malformed FASTQ record near header: {header[:80]!r}")
            if len(sequence) != len(quality.rstrip("\r\n")):
                raise ValueError("FASTQ sequence and quality lengths differ")
            yield sequence.upper()


def feature_batch(sequences: list[str], name: str, length: int) -> np.ndarray:
    normalized = name.lower().replace("-", "_")
    if normalized == "ck4":
        matrix, _ = build_ck4_block(sequences, config=CK4PMSPConfig(k=4))
        return matrix
    if normalized == "ck5":
        matrix, _ = build_ck4_block(sequences, config=CK4PMSPConfig(k=5))
        return matrix
    if normalized == "ck7":
        matrix, _ = build_ck4_block(sequences, config=CK4PMSPConfig(k=7))
        return matrix
    if normalized == "ck4p_msp":
        return build_ck4p_msp_features(sequences, config=CK4PMSPConfig()).matrix
    historical = {
        "pseknc": "pseknc_k3_l3",
        "pseeiip": "pseeiip",
    }.get(normalized, normalized)
    matrix, _ = build_feature_matrix(sequences, historical, length=length)
    return np.asarray(matrix, dtype=np.float64)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fastq", type=Path, required=True)
    parser.add_argument("--labels", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--representation", action="append", required=True)
    parser.add_argument("--batch-size", type=int, default=4096)
    parser.add_argument("--read-length", type=int, default=75)
    parser.add_argument("--max-reads", type=int)
    args = parser.parse_args()

    if args.batch_size < 1:
        raise ValueError("batch size must be positive")
    if not args.fastq.exists() or not args.labels.exists():
        raise FileNotFoundError("FASTQ and labels must both exist")

    labels = np.asarray(np.load(args.labels, mmap_mode="r"))
    if labels.ndim != 1:
        raise ValueError(f"labels must be one-dimensional: {labels.shape}")
    n_rows = int(labels.size if args.max_reads is None else min(labels.size, args.max_reads))
    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    matrices: dict[str, np.memmap] = {}
    dimensions: dict[str, int] = {}
    seen = 0
    batch: list[str] = []

    def flush() -> None:
        nonlocal batch, seen
        if not batch:
            return
        start = seen
        end = seen + len(batch)
        for name in args.representation:
            matrix = feature_batch(batch, name, args.read_length)
            key = name.replace("-", "_")
            if key not in matrices:
                dimensions[key] = int(matrix.shape[1])
                matrices[key] = np.lib.format.open_memmap(
                    output_dir / f"{key}.npy",
                    mode="w+",
                    dtype="float32",
                    shape=(n_rows, matrix.shape[1]),
                )
            if matrix.shape != (len(batch), dimensions[key]):
                raise ValueError(f"dimension changed for {name}: {matrix.shape} vs {dimensions[key]}")
            matrices[key][start:end] = matrix.astype(np.float32, copy=False)
        seen = end
        batch = []

    for sequence in iter_fastq(args.fastq):
        if len(sequence) != args.read_length:
            raise ValueError(
                f"read length mismatch at FASTQ row {seen + len(batch)}: "
                f"{len(sequence)} vs {args.read_length}"
            )
        if seen + len(batch) >= n_rows:
            if args.max_reads is None:
                raise ValueError(
                    f"FASTQ contains more records than labels: first extra row {n_rows}"
                )
            break
        batch.append(sequence)
        if len(batch) >= args.batch_size:
            flush()
    flush()
    if seen != n_rows:
        raise ValueError(f"FASTQ rows ({seen}) do not match requested rows ({n_rows})")
    for matrix in matrices.values():
        matrix.flush()

    manifest = {
        "fastq": {"path": str(args.fastq.resolve()), "sha256": sha256_file(args.fastq)},
        "labels": {"path": str(args.labels.resolve()), "sha256": sha256_file(args.labels)},
        "n_reads": seen,
        "read_length": args.read_length,
        "batch_size": args.batch_size,
        "max_reads": args.max_reads,
        "truncated": args.max_reads is not None and args.max_reads < labels.size,
        "representations": args.representation,
        "dimensions": dimensions,
        "row_order": "FASTQ record order; labels must be aligned to this order",
        "outputs": {key: str((output_dir / f"{key}.npy").resolve()) for key in matrices},
    }
    (output_dir / "representation_build_manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
