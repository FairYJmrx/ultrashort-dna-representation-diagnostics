from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

import pandas as pd

def _find_project_root(start: Path) -> Path:
    for candidate in [start.parent, *start.parents]:
        if (candidate / "methods").is_dir() and (candidate / "configs").is_dir():
            return candidate
    raise RuntimeError("Could not locate the release repository root.")


PROJECT_ROOT = _find_project_root(Path(__file__).resolve())
sys.path.insert(0, str(PROJECT_ROOT))

from experiments.main.run_stage2_representation_grid import (  # noqa: E402
    parse_csv_list,
    parse_int_list,
    run_stability_grid,
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


def read_fasta(path: Path) -> dict[str, str]:
    records: dict[str, list[str]] = {}
    current: str | None = None
    with path.open("r", encoding="utf-8", errors="ignore") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            if line.startswith(">"):
                current = line[1:].split()[0]
                records[current] = []
            elif current is not None:
                records[current].append(line.upper())
    return {key: "".join(value) for key, value in records.items()}


def reverse_complement(seq: str) -> str:
    return seq.translate(str.maketrans("ACGTNacgtn", "TGCANtgcan"))[::-1].upper()


def parse_cigar_ref_len(cigar: str) -> int:
    import re

    total = 0
    for size, op in re.findall(r"(\d+)([MIDNSHP=X])", cigar):
        if op in {"M", "D", "N", "=", "X"}:
            total += int(size)
    return total


def read_fastq(path: Path) -> dict[str, tuple[str, str]]:
    reads: dict[str, tuple[str, str]] = {}
    with path.open("r", encoding="utf-8", errors="ignore") as fh:
        while True:
            header = fh.readline()
            if not header:
                break
            seq = fh.readline().strip().upper()
            fh.readline()
            qual = fh.readline().strip()
            rid = header.strip().split()[0].lstrip("@")
            reads[rid] = (seq, qual)
    return reads


def sam_rows(sam_path: Path) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    with sam_path.open("r", encoding="utf-8", errors="ignore") as fh:
        for line in fh:
            if line.startswith("@"):
                continue
            parts = line.rstrip("\n").split("\t")
            if len(parts) < 11:
                continue
            qname, flag_text, rname, pos_text, _, cigar = parts[:6]
            try:
                flag = int(flag_text)
                pos = int(pos_text)
            except ValueError:
                continue
            if rname == "*" or pos <= 0:
                continue
            rows.append(
                {
                    "qname": qname,
                    "flag": flag,
                    "rname": rname,
                    "pos": pos,
                    "cigar": cigar,
                    "is_reverse": bool(flag & 16),
                    "ref_len": parse_cigar_ref_len(cigar),
                }
            )
    return rows


def normalize_art_output(
    genome_path: Path,
    fq_path: Path,
    sam_path: Path,
    label: str,
    genus: str,
    species: str,
    length: int,
) -> pd.DataFrame:
    refs = read_fasta(genome_path)
    fq = read_fastq(fq_path)
    rows: list[dict[str, object]] = []
    for aln in sam_rows(sam_path):
        rid = str(aln["qname"])
        if rid not in fq:
            continue
        rname = str(aln["rname"])
        if rname not in refs:
            continue
        ref_len = int(aln["ref_len"]) or length
        start0 = int(aln["pos"]) - 1
        clean_seq = refs[rname][start0 : start0 + ref_len].upper()
        if bool(aln["is_reverse"]):
            clean_seq = reverse_complement(clean_seq)
        art_seq, quality = fq[rid]
        clean_id = f"{label}|L{length}|{rid}"
        base = {
            "clean_read_id": clean_id,
            "label": label,
            "genus": genus,
            "species": species,
            "species_id": label,
            "target_binary": "target",
            "source_length": length,
            "template_contig": rname,
            "template_start": start0,
            "cigar": aln["cigar"],
            "is_reverse": bool(aln["is_reverse"]),
        }
        rows.append(
            {
                **base,
                "read_id": f"{clean_id}|clean",
                "sequence": clean_seq[:length],
                "quality": "",
                "condition": "clean",
                "length": min(length, len(clean_seq)),
            }
        )
        rows.append(
            {
                **base,
                "read_id": f"{clean_id}|art_illumina",
                "sequence": art_seq[:length],
                "quality": quality[:length],
                "condition": "art_illumina",
                "length": min(length, len(art_seq)),
            }
        )
    return pd.DataFrame(rows)


def run_art(art_exe: Path, genome: Path, prefix: Path, length: int, fold_coverage: float, seed: int) -> None:
    prefix.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        str(art_exe),
        "-i",
        str(genome),
        "-l",
        str(length),
        "-f",
        str(fold_coverage),
        "-rs",
        str(seed),
        "-sam",
        "-na",
        "-q",
        "-o",
        str(prefix),
    ]
    completed = subprocess.run(cmd, check=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if completed.returncode != 0:
        raise RuntimeError(f"ART failed with code {completed.returncode}: {completed.stderr or completed.stdout}")
    if not Path(str(prefix) + ".fq").exists() or not Path(str(prefix) + ".sam").exists():
        raise RuntimeError(f"ART did not create expected FASTQ/SAM for prefix {prefix}: {completed.stderr or completed.stdout}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate lightweight ART Illumina reads and evaluate representation stability.")
    parser.add_argument("--art-exe", default=str(PROJECT_ROOT / "tools" / "art" / "extracted_bp" / "Win64" / "art_illumina.exe"))
    parser.add_argument("--genome-manifest", default=str(PROJECT_ROOT / "data" / "real_slices" / "close_relative_genomes_manifest.csv"))
    parser.add_argument("--output-dir", default=str(PROJECT_ROOT / "results" / "stage3" / "art_illumina"))
    parser.add_argument("--lengths", default="69,75,100,125,150")
    parser.add_argument("--representations", default=DEFAULT_REPRESENTATIONS)
    parser.add_argument("--fold-coverage", type=float, default=0.005)
    parser.add_argument("--max-genomes", type=int, default=0)
    parser.add_argument("--max-retrieval-pairs", type=int, default=400)
    parser.add_argument("--seed", type=int, default=606)
    args = parser.parse_args()

    started = time.time()
    set_global_seed(args.seed)
    art_exe = Path(args.art_exe)
    output_dir = Path(args.output_dir)
    fastq_dir = output_dir / "fastq"
    output_dir.mkdir(parents=True, exist_ok=True)
    fastq_dir.mkdir(parents=True, exist_ok=True)

    manifest = pd.read_csv(args.genome_manifest)
    if args.max_genomes > 0:
        manifest = manifest.head(args.max_genomes).copy()
    lengths = parse_int_list(args.lengths)
    reps = parse_csv_list(args.representations)

    all_rows: list[pd.DataFrame] = []
    run_rows: list[dict[str, object]] = []
    for _, row in manifest.iterrows():
        genome = PROJECT_ROOT / str(row["genome_path"])
        if not genome.exists():
            continue
        label = str(row["label"])
        genus = str(row.get("genus", ""))
        species = str(row.get("species", label))
        for length in lengths:
            prefix = fastq_dir / f"{label}_L{length}_ART_"
            fq_path = Path(str(prefix) + ".fq")
            sam_path = Path(str(prefix) + ".sam")
            status = "existing"
            if not fq_path.exists() or not sam_path.exists():
                run_art(art_exe, genome, prefix, length, args.fold_coverage, args.seed + length)
                status = "generated"
            df = normalize_art_output(genome, fq_path, sam_path, label, genus, species, length)
            all_rows.append(df)
            run_rows.append(
                {
                    "label": label,
                    "length": length,
                    "status": status,
                    "n_rows": int(len(df)),
                    "n_pairs": int(len(df) // 2),
                    "fq_path": str(fq_path),
                    "sam_path": str(sam_path),
                }
            )
            pd.DataFrame(run_rows).to_csv(output_dir / "art_generation_manifest.csv", index=False, encoding="utf-8-sig")

    reads = pd.concat(all_rows, ignore_index=True) if all_rows else pd.DataFrame()
    reads = reads[reads["sequence"].astype(str).str.len() > 0].copy()
    reads.to_csv(output_dir / "art_paired_reads.csv", index=False, encoding="utf-8-sig")

    stability = run_stability_grid(
        reads,
        lengths=lengths,
        conditions=["clean", "art_illumina"],
        representations=reps,
        max_pairs=args.max_retrieval_pairs,
        seed=args.seed,
        output_path=output_dir / "art_stability_metrics.csv",
    )
    stability.to_csv(output_dir / "art_stability_metrics.csv", index=False, encoding="utf-8-sig")

    lines = ["# Stage-3 ART Illumina Completed Summary\n"]
    lines.append(f"- ART executable: `{art_exe}`")
    lines.append(f"- Fold coverage: `{args.fold_coverage}`")
    lines.append(f"- Generated paired rows: `{len(reads)}`")
    lines.append(f"- Generated clean/error pairs: `{reads['clean_read_id'].nunique() if not reads.empty else 0}`")
    if not stability.empty:
        valid = stability[~stability.get("error", pd.Series(index=stability.index, dtype=object)).notna()].copy()
        if not valid.empty:
            best = valid.sort_values(["length", "paired_cosine_mean"], ascending=[True, False]).groupby("length", as_index=False).first()
            lines.append("\n## Best ART stability by length\n")
            lines.append(best[["length", "representation", "paired_cosine_mean", "l2_delta_mean", "retrieval_top1", "n_features", "density"]].to_markdown(index=False, floatfmt=".3f"))
    (output_dir / "art_completed_summary.md").write_text("\n".join(lines), encoding="utf-8")

    (output_dir / "stage3_art_generate_run.json").write_text(
        json.dumps(
            {
                "elapsed_seconds": time.time() - started,
                "art_exe": str(art_exe),
                "genome_manifest": args.genome_manifest,
                "lengths": lengths,
                "representations": reps,
                "fold_coverage": args.fold_coverage,
                "n_reads_rows": int(len(reads)),
                "n_clean_ids": int(reads["clean_read_id"].nunique() if not reads.empty else 0),
                "n_stability_rows": int(len(stability)),
            },
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    print(f"Wrote ART generated validation to {output_dir}")


if __name__ == "__main__":
    main()

