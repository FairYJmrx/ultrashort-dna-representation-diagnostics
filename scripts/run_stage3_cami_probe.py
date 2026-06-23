from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.run_stage2_representation_grid import (  # noqa: E402
    apply_stage2_condition,
    balanced_sample,
    evaluate_readout,
    parse_csv_list,
    parse_int_list,
    set_global_seed,
)


DEFAULT_REPRESENTATIONS = ",".join(
    [
        "ckmer5_count_l2",
        "ckmer7_count_l2",
        "cspaced_count_l2",
        "cspaced_property_l2",
        "hybrid_ckmer5_csp",
        "minhash_k5_s128",
        "eiip_l2",
        "eiip_summary_l2",
    ]
)


def read_fastq(path: Path, max_reads: int) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    opener = open
    if str(path).endswith(".gz"):
        import gzip

        opener = gzip.open  # type: ignore[assignment]
    with opener(path, "rt", encoding="utf-8", errors="ignore") as fh:  # type: ignore[arg-type]
        idx = 0
        while True:
            header = fh.readline()
            if not header:
                break
            seq = fh.readline().strip().upper()
            plus = fh.readline()
            qual = fh.readline().strip()
            if not qual:
                break
            read_id = header.strip().split()[0].lstrip("@")
            rows.append({"read_id": read_id, "clean_read_id": read_id, "sequence": seq, "quality": qual})
            idx += 1
            if max_reads > 0 and idx >= max_reads:
                break
    return pd.DataFrame(rows)


def load_cami_reads(args: argparse.Namespace) -> pd.DataFrame:
    if args.reads_csv.strip():
        reads = pd.read_csv(args.reads_csv)
    elif args.fastq.strip() and args.labels_csv.strip():
        reads = read_fastq(Path(args.fastq), max_reads=args.max_reads)
        labels = pd.read_csv(args.labels_csv)
        if "read_id" not in labels.columns:
            raise ValueError("labels CSV must contain read_id")
        reads = reads.merge(labels, on="read_id", how="inner")
    else:
        raise ValueError("Provide either --reads-csv or both --fastq and --labels-csv.")

    if "sequence" not in reads.columns:
        raise ValueError("CAMI reads input must contain sequence")
    reads["sequence"] = reads["sequence"].astype(str).str.upper()
    if "label" not in reads.columns:
        for candidate in ["species", "taxon", "genus", "sample_label"]:
            if candidate in reads.columns:
                reads["label"] = reads[candidate].astype(str)
                break
    if "label" not in reads.columns:
        raise ValueError("CAMI reads input must contain label or species/genus/taxon/sample_label")
    if "genus" not in reads.columns:
        reads["genus"] = reads["label"].astype(str).str.split().str[0]
    if "species_id" not in reads.columns:
        reads["species_id"] = reads["label"].astype(str)
    return reads


def build_length_condition_rows(reads: pd.DataFrame, lengths: list[int], conditions: list[str], seed: int) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    base = reads.copy()
    base["clean_read_id"] = base.get("clean_read_id", base.get("read_id", pd.Series(range(len(base))))).astype(str)
    for length in lengths:
        eligible = base[base["sequence"].str.len() >= length].copy()
        if eligible.empty:
            continue
        for _, row in eligible.iterrows():
            clean = row.to_dict()
            clean["sequence"] = str(clean["sequence"])[:length]
            clean["source_length"] = length
            clean["length"] = length
            clean["condition"] = "clean"
            clean["read_id"] = f"{clean['clean_read_id']}_L{length}_clean"
            clean["target_binary"] = "target" if str(clean.get("label")) == str(clean.get("target_label", "")) else "background"
            for condition in conditions:
                if condition == "clean":
                    out = clean.copy()
                else:
                    out = apply_stage2_condition(pd.Series(clean), condition, seed)
                rows.append(out)
    out_df = pd.DataFrame(rows)
    if out_df.empty:
        return out_df
    out_df["source_length"] = out_df["source_length"].astype(int)
    out_df["length"] = out_df["length"].astype(int)
    return out_df


def run_cami_readouts(
    df: pd.DataFrame,
    lengths: list[int],
    conditions: list[str],
    representations: list[str],
    classifiers: list[str],
    max_per_class: int,
    seed: int,
    target_label: str,
) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for length in lengths:
        for condition in conditions:
            subset = df[(df["source_length"] == length) & (df["condition"] == condition)].copy()
            if subset.empty:
                continue
            tasks = [("label_probe", "label")]
            if target_label:
                subset["target_binary"] = np.where(subset["label"].astype(str).eq(target_label), "target", "background")
                tasks.append(("target_background", "target_binary"))
            for task, label_col in tasks:
                if subset[label_col].nunique() < 2:
                    continue
                sampled = balanced_sample(subset, label_col, max_per_class=max_per_class, seed=seed + length)
                for rep in representations:
                    for row in evaluate_readout(sampled, rep, label_col, length, seed, classifiers):
                        row.update({"task": task, "length": length, "condition": condition, "label_col": label_col})
                        rows.append(row)
    return pd.DataFrame(rows)


def write_summary(readout: pd.DataFrame, output_dir: Path) -> None:
    lines: list[str] = []
    lines.append("# Stage-3 CAMI Low-complexity Probe Summary\n")
    lines.append("This analysis treats CAMI as an external lightweight readout probe, not as an end-to-end clinical classifier benchmark.\n")
    if readout.empty:
        lines.append("No readout rows were produced. Check labels, read lengths and class balance.")
    else:
        valid = readout.dropna(subset=["macro_f1"]) if "macro_f1" in readout else pd.DataFrame()
        if not valid.empty:
            grouped = valid.groupby(["task", "condition", "length", "representation"], as_index=False).agg(
                mean_macro_f1=("macro_f1", "mean"),
                mean_accuracy=("accuracy", "mean"),
                mean_features=("n_features", "mean"),
            )
            best = grouped.sort_values(["task", "condition", "length", "mean_macro_f1"], ascending=[True, True, True, False]).groupby(["task", "condition", "length"], as_index=False).first()
            lines.append("## Best readout by task, condition and length\n")
            lines.append(best.to_markdown(index=False, floatfmt=".3f"))
    (output_dir / "cami_probe_summary.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a lightweight CAMI low-complexity readout probe for stage-3 validation.")
    parser.add_argument("--reads-csv", default="", help="Normalized reads CSV. Must contain sequence and label/species/genus.")
    parser.add_argument("--fastq", default="", help="Optional CAMI FASTQ input when --reads-csv is not provided.")
    parser.add_argument("--labels-csv", default="", help="Optional read_id-to-label CSV for FASTQ input.")
    parser.add_argument("--output-dir", default=str(PROJECT_ROOT / "results" / "stage3" / "cami_probe"))
    parser.add_argument("--lengths", default="69,75,100,125,150")
    parser.add_argument("--conditions", default="clean,N_3pct,substitution_1pct")
    parser.add_argument("--representations", default=DEFAULT_REPRESENTATIONS)
    parser.add_argument("--classifiers", default="nearest_centroid,logistic")
    parser.add_argument("--target-label", default="")
    parser.add_argument("--max-reads", type=int, default=20000)
    parser.add_argument("--max-per-class", type=int, default=80)
    parser.add_argument("--seed", type=int, default=505)
    args = parser.parse_args()

    started = time.time()
    set_global_seed(args.seed)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    lengths = parse_int_list(args.lengths)
    conditions = parse_csv_list(args.conditions)
    reps = parse_csv_list(args.representations)
    classifiers = parse_csv_list(args.classifiers)

    reads = load_cami_reads(args)
    if args.target_label:
        reads["target_label"] = args.target_label
    cami_rows = build_length_condition_rows(reads, lengths=lengths, conditions=conditions, seed=args.seed)
    cami_rows.to_csv(output_dir / "cami_probe_reads.csv", index=False, encoding="utf-8-sig")

    readout = run_cami_readouts(
        cami_rows,
        lengths=lengths,
        conditions=conditions,
        representations=reps,
        classifiers=classifiers,
        max_per_class=args.max_per_class,
        seed=args.seed,
        target_label=args.target_label,
    )
    readout.to_csv(output_dir / "cami_probe_readout.csv", index=False, encoding="utf-8-sig")
    write_summary(readout, output_dir)
    (output_dir / "stage3_cami_probe_run.json").write_text(
        json.dumps(
            {
                "elapsed_seconds": time.time() - started,
                "reads_csv": args.reads_csv,
                "fastq": args.fastq,
                "labels_csv": args.labels_csv,
                "lengths": lengths,
                "conditions": conditions,
                "representations": reps,
                "classifiers": classifiers,
                "target_label": args.target_label,
                "n_input_reads": int(len(reads)),
                "n_probe_rows": int(len(cami_rows)),
                "n_readout_rows": int(len(readout)),
            },
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    print(f"Wrote CAMI probe files to {output_dir}")


if __name__ == "__main__":
    main()
