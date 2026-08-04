"""Measure reverse-complement sensitivity of promoted positional candidates."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import pandas as pd


def _find_project_root(start: Path) -> Path:
    for candidate in [start.parent, *start.parents]:
        if (candidate / "methods").is_dir() and (candidate / "configs").is_dir():
            return candidate
    raise RuntimeError("Could not locate the release repository root.")


PROJECT_ROOT = _find_project_root(Path(__file__).resolve())
sys.path.insert(0, str(PROJECT_ROOT))

from methods.experimental_positional_kmer import (  # noqa: E402
    CK4P_MSP_PKM_KEY,
    build_weighted_augment_candidates,
)
from methods.sequence_utils import reverse_complement  # noqa: E402
from methods.stage2_features import paired_retrieval_metrics  # noqa: E402


LABELS = {
    "ck4p_msp": "CK4P-MSP",
    CK4P_MSP_PKM_KEY: "CK4P-MSP-PKM",
    "cpkm_weight_w025": "CPKM weight=0.25",
}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reads", default=str(PROJECT_ROOT / "results" / "stage3" / "contract_v2" / "art_current_contract" / "art_paired_reads.csv"))
    parser.add_argument("--output-dir", default=str(PROJECT_ROOT / "results" / "stage3" / "candidate_positional_kmer_strand_audit"))
    parser.add_argument("--max-reads", type=int, default=5000)
    args = parser.parse_args()

    frame = pd.read_csv(args.reads)
    clean = frame[frame["condition"].eq("clean")].copy()
    clean = clean.sort_values(["length", "clean_read_id"]).head(args.max_reads)
    sequences = clean["sequence"].astype(str).tolist()
    reverse_sequences = [reverse_complement(sequence) for sequence in sequences]
    forward = build_weighted_augment_candidates(sequences, [0.25])
    reverse = build_weighted_augment_candidates(reverse_sequences, [0.25])
    rows: list[dict[str, object]] = []
    for representation in LABELS:
        rows.append(
            {
                "representation": representation,
                "representation_label": LABELS[representation],
                "n_features": int(forward[representation].shape[1]),
                "n_pairs": len(sequences),
                **paired_retrieval_metrics(forward[representation], reverse[representation]),
            }
        )
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    result = pd.DataFrame(rows)
    result.to_csv(output_dir / "strand_audit.csv", index=False, encoding="utf-8-sig")
    (output_dir / "strand_audit_run.json").write_text(
        json.dumps(
            {
                "reads": str(Path(args.reads).resolve()),
                "n_reads": len(sequences),
                "length_counts": clean["length"].value_counts().sort_index().to_dict(),
                "candidate_weight": 0.25,
                "interpretation": "Input-order sensitivity audit; not a claim that the full representation is reverse-complement invariant.",
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    print(result.to_string(index=False))


if __name__ == "__main__":
    main()
