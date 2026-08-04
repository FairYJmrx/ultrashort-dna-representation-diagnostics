"""Audit whether MSP separates sequences with identical canonical CK4 profiles."""

from __future__ import annotations

import argparse
import collections
import json
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd


def find_project_root(start: Path) -> Path:
    for candidate in [start.parent, *start.parents]:
        if (candidate / "methods").is_dir() and (candidate / "configs").is_dir():
            return candidate
    raise RuntimeError("Could not locate the release repository root.")


PROJECT_ROOT = find_project_root(Path(__file__).resolve())
sys.path.insert(0, str(PROJECT_ROOT))

from methods.ck4p_msp import (  # noqa: E402
    build_block_combination,
    build_ck4p_msp_features,
)
from methods.historical_descriptors import build_historical_descriptor_matrix  # noqa: E402


REPRESENTATIONS = [
    "ck4",
    "p",
    "msp",
    "ck4_p",
    "ck4_msp",
    "p_msp",
    "ck4p_msp",
    "pseknc_k3_l3",
    "pseeiip",
    "ncp_anf",
]

LABELS = {
    "ck4": "CK4",
    "p": "P",
    "msp": "MSP",
    "ck4_p": "CK4+P",
    "ck4_msp": "CK4+MSP",
    "p_msp": "P+MSP",
    "ck4p_msp": "CK4P-MSP",
    "pseknc_k3_l3": "PseKNC",
    "pseeiip": "PseEIIP",
    "ncp_anf": "NCP+ANF",
}


def reverse_complement(sequence: str) -> str:
    table = str.maketrans("ACGT", "TGCA")
    return sequence.translate(table)[::-1]


def canonical_profile(sequence: str, k: int = 4) -> collections.Counter[str]:
    return collections.Counter(
        min(sequence[index : index + k], reverse_complement(sequence[index : index + k]))
        for index in range(len(sequence) - k + 1)
    )


def eulerian_reorder(sequence: str, rng: np.random.Generator, k: int = 4) -> str | None:
    """Generate a different Eulerian trail with the same contiguous k-mer multiset."""
    if len(sequence) < k or any(base not in "ACGT" for base in sequence):
        return None

    adjacency: dict[str, list[str]] = collections.defaultdict(list)
    indegree: collections.Counter[str] = collections.Counter()
    outdegree: collections.Counter[str] = collections.Counter()
    for index in range(len(sequence) - k + 1):
        left = sequence[index : index + k - 1]
        right = sequence[index + 1 : index + k]
        adjacency[left].append(right)
        outdegree[left] += 1
        indegree[right] += 1

    start = sequence[: k - 1]
    imbalanced = [node for node in adjacency if outdegree[node] - indegree[node] == 1]
    if len(imbalanced) == 1:
        start = imbalanced[0]

    for _ in range(64):
        local = {node: list(edges) for node, edges in adjacency.items()}
        for edges in local.values():
            rng.shuffle(edges)
        stack = [start]
        trail: list[str] = []
        while stack:
            node = stack[-1]
            if local.get(node):
                stack.append(local[node].pop())
            else:
                trail.append(stack.pop())
        trail.reverse()
        if len(trail) != len(sequence) - k + 2:
            continue
        candidate = trail[0] + "".join(node[-1] for node in trail[1:])
        if candidate != sequence and canonical_profile(candidate, k) == canonical_profile(sequence, k):
            return candidate
    return None


def sample_templates(source: pd.DataFrame, lengths: list[int], max_per_length: int, seed: int) -> pd.DataFrame:
    clean = source[
        source["condition"].astype(str).eq("clean")
        & source["source_length"].astype(int).isin(lengths)
        & source["sequence"].astype(str).str.fullmatch("[ACGT]+")
    ].copy()
    parts: list[pd.DataFrame] = []
    for length, group in clean.groupby("source_length", sort=True):
        n = min(max_per_length, len(group))
        parts.append(group.sample(n=n, random_state=seed + int(length)))
    if not parts:
        raise ValueError("No suitable clean source reads were found.")
    return pd.concat(parts, ignore_index=True)


def build_pairs(source: pd.DataFrame, lengths: list[int], max_per_length: int, seed: int) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    templates = sample_templates(source, lengths, max_per_length, seed)
    rows: list[dict[str, object]] = []
    for index, row in templates.reset_index(drop=True).iterrows():
        sequence = str(row["sequence"]).upper()
        alternative = eulerian_reorder(sequence, rng)
        if alternative is None:
            continue
        profile = canonical_profile(sequence)
        rows.extend(
            [
                {
                    "pair_id": f"order_pair_{index:06d}",
                    "source_read_id": str(row["clean_read_id"]),
                    "length": int(len(sequence)),
                    "label": str(row["label"]),
                    "variant": "original",
                    "sequence": sequence,
                    "canonical_ck4_profile": json.dumps(sorted(profile.items())),
                },
                {
                    "pair_id": f"order_pair_{index:06d}",
                    "source_read_id": str(row["clean_read_id"]),
                    "length": int(len(sequence)),
                    "label": str(row["label"]),
                    "variant": "eulerian_reorder",
                    "sequence": alternative,
                    "canonical_ck4_profile": json.dumps(sorted(profile.items())),
                },
            ]
        )
    pairs = pd.DataFrame(rows)
    if pairs.empty:
        raise RuntimeError("No alternative Eulerian trails were generated.")
    return pairs


def normalize_rows(matrix: np.ndarray) -> np.ndarray:
    matrix = np.nan_to_num(np.asarray(matrix, dtype=float), nan=0.0, posinf=0.0, neginf=0.0)
    norms = np.linalg.norm(matrix, axis=1, keepdims=True)
    return matrix / np.maximum(norms, 1e-12)


def representation_matrices(sequences: list[str], length: int) -> dict[str, np.ndarray]:
    features = build_ck4p_msp_features(sequences, train_indices=list(range(len(sequences))))
    blocks = {
        "ck4": features.ck4,
        "p": features.p,
        "msp": features.msp,
        "ck4_p": build_block_combination(features, "ck4_p"),
        "ck4_msp": build_block_combination(features, "ck4_msp"),
        "p_msp": build_block_combination(features, "p_msp"),
        "ck4p_msp": features.matrix,
    }
    for name in ["pseknc_k3_l3", "pseeiip", "ncp_anf"]:
        blocks[name] = build_historical_descriptor_matrix(sequences, name, length=length)
    return {name: normalize_rows(matrix) for name, matrix in blocks.items()}


def audit_pairs(pairs: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    metric_rows: list[dict[str, object]] = []
    for length, group in pairs.groupby("length", sort=True):
        ordered = group.sort_values(["pair_id", "variant"])
        sequences = ordered["sequence"].astype(str).tolist()
        matrices = representation_matrices(sequences, int(length))
        pair_order = ordered["pair_id"].drop_duplicates().tolist()
        for representation, matrix in matrices.items():
            for pair_id in pair_order:
                pair_rows = ordered[ordered["pair_id"].eq(pair_id)]
                original_index = int(pair_rows.index[pair_rows["variant"].eq("original")][0])
                reorder_index = int(pair_rows.index[pair_rows["variant"].eq("eulerian_reorder")][0])
                original_vector = matrix[ordered.index.get_loc(original_index)]
                reorder_vector = matrix[ordered.index.get_loc(reorder_index)]
                metric_rows.append(
                    {
                        "pair_id": pair_id,
                        "length": int(length),
                        "representation": representation,
                        "representation_label": LABELS[representation],
                        "l2_drift": float(np.linalg.norm(original_vector - reorder_vector)),
                        "paired_cosine": float(np.dot(original_vector, reorder_vector)),
                        "n_features": int(matrix.shape[1]),
                    }
                )
    metrics = pd.DataFrame(metric_rows)
    summary = (
        metrics.groupby(["length", "representation", "representation_label"], as_index=False)
        .agg(
            n_pairs=("pair_id", "nunique"),
            l2_drift_mean=("l2_drift", "mean"),
            l2_drift_median=("l2_drift", "median"),
            l2_drift_p95=("l2_drift", lambda values: float(np.quantile(values, 0.95))),
            paired_cosine_mean=("paired_cosine", "mean"),
            n_features=("n_features", "first"),
        )
    )
    return metrics, summary


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--source-reads",
        default=str(PROJECT_ROOT / "data" / "real_slices" / "close_relative_reads.csv"),
    )
    parser.add_argument(
        "--output-dir",
        default=str(PROJECT_ROOT / "results" / "decision_stage" / "e2_order_collision"),
    )
    parser.add_argument("--lengths", default="69,75,100,150")
    parser.add_argument("--max-per-length", type=int, default=400)
    parser.add_argument("--seed", type=int, default=20260804)
    args = parser.parse_args()

    started = time.time()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    lengths = [int(item) for item in args.lengths.split(",") if item.strip()]
    source = pd.read_csv(args.source_reads)
    source["source_length"] = source["source_length"].astype(int)
    pairs = build_pairs(source, lengths, args.max_per_length, args.seed)
    metrics, summary = audit_pairs(pairs)
    pairs.to_csv(output_dir / "order_collision_pairs.csv", index=False, encoding="utf-8-sig")
    metrics.to_csv(output_dir / "order_collision_metrics.csv", index=False, encoding="utf-8-sig")
    summary.to_csv(output_dir / "order_collision_summary.csv", index=False, encoding="utf-8-sig")
    metadata = {
        "elapsed_seconds": round(time.time() - started, 3),
        "source_reads": str(Path(args.source_reads).resolve()),
        "lengths": lengths,
        "max_per_length": args.max_per_length,
        "n_pairs": int(pairs["pair_id"].nunique()),
        "n_pairs_by_length": pairs.groupby("length")["pair_id"].nunique().to_dict(),
        "generation": "randomized Eulerian trails preserving the canonical contiguous 4-mer multiset",
        "negative_result_rule": "lack of separation beyond controls downgrades MSP order-resolution claims",
        "seed": args.seed,
    }
    (output_dir / "order_collision_run.json").write_text(
        json.dumps(metadata, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    (output_dir / "order_collision_summary.md").write_text(
        "# E2：CK4 等价类顺序分辨审计\n\n"
        "每个配对序列具有完全相同的 canonical contiguous 4-mer multiset，差异来自随机化 Eulerian trail。该实验检验 MSP 是否能对 CK4 组成等价类提供额外的粗粒度顺序敏感性；它不等价于完整 motif 或基因组位置恢复。\n\n"
        + summary.to_markdown(index=False, floatfmt=".5f")
        + "\n",
        encoding="utf-8",
    )
    print(f"Wrote E2 order-collision audit to {output_dir}")


if __name__ == "__main__":
    main()
