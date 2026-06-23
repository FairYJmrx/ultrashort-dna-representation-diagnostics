from __future__ import annotations

import argparse
import json
import shutil
import sys
import time
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.run_stage2_representation_grid import parse_csv_list, parse_int_list, run_stability_grid, set_global_seed  # noqa: E402


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


def resolve_path(path_text: str) -> Path:
    path = Path(path_text)
    return path if path.is_absolute() else PROJECT_ROOT / path


def write_art_manifest(
    genome_manifest: Path,
    output_dir: Path,
    lengths: list[int],
    art_exe: str,
    profile: str,
    fold_coverage: float,
    seed: int,
    max_genomes: int,
) -> pd.DataFrame:
    manifest = pd.read_csv(genome_manifest)
    if max_genomes > 0:
        manifest = manifest.head(max_genomes).copy()
    rows: list[dict[str, object]] = []
    fastq_dir = output_dir / "fastq"
    fastq_dir.mkdir(parents=True, exist_ok=True)
    for _, row in manifest.iterrows():
        genome = resolve_path(str(row["genome_path"]))
        if not genome.exists():
            continue
        label = str(row.get("label", genome.stem))
        for length in lengths:
            prefix = fastq_dir / f"{label}_L{length}_ART_"
            command = (
                f'"{art_exe}" -ss {profile} -i "{genome}" -l {length} '
                f"-f {fold_coverage} -rs {seed + length} -na -o \"{prefix}\""
            )
            rows.append(
                {
                    "label": label,
                    "genus": row.get("genus", ""),
                    "species": row.get("species", ""),
                    "genome_path": str(genome),
                    "length": length,
                    "profile": profile,
                    "fold_coverage": fold_coverage,
                    "seed": seed + length,
                    "output_prefix": str(prefix),
                    "command": command,
                }
            )
    commands = pd.DataFrame(rows)
    commands.to_csv(output_dir / "art_command_manifest.csv", index=False, encoding="utf-8-sig")
    return commands


def evaluate_art_csv(
    reads_csv: Path,
    output_dir: Path,
    lengths: list[int],
    representations: list[str],
    max_pairs: int,
    seed: int,
) -> pd.DataFrame:
    reads = pd.read_csv(reads_csv)
    required = {"clean_read_id", "sequence", "condition", "source_length"}
    missing = required - set(reads.columns)
    if missing:
        raise ValueError(f"ART reads CSV is missing required columns: {sorted(missing)}")
    reads["source_length"] = reads["source_length"].astype(int)
    reads["sequence"] = reads["sequence"].astype(str).str.upper()
    conditions = ["clean", "art_illumina"]
    stability = run_stability_grid(
        reads,
        lengths=lengths,
        conditions=conditions,
        representations=representations,
        max_pairs=max_pairs,
        seed=seed,
        output_path=output_dir / "art_stability_metrics.csv",
    )
    stability.to_csv(output_dir / "art_stability_metrics.csv", index=False, encoding="utf-8-sig")
    return stability


def write_summary(commands: pd.DataFrame, stability: pd.DataFrame | None, output_dir: Path, art_found: bool, art_exe: str) -> None:
    lines: list[str] = []
    lines.append("# Stage-3 ART Illumina Validation Summary\n")
    lines.append("This stage validates representation stability under ART Illumina-like sequencing error profiles. It is a simulator-profile validation, not a clinical endpoint.\n")
    lines.append(f"- ART executable requested: `{art_exe}`")
    lines.append(f"- ART executable found: `{art_found}`")
    lines.append(f"- ART command rows: {len(commands)}")
    if not commands.empty:
        lines.append("\n## Command manifest preview\n")
        lines.append(commands.head(12)[["label", "length", "profile", "fold_coverage", "command"]].to_markdown(index=False))
    if stability is not None and not stability.empty:
        valid = stability[~stability.get("error", pd.Series(index=stability.index, dtype=object)).notna()].copy()
        if not valid.empty:
            best = valid.sort_values(["length", "paired_cosine_mean"], ascending=[True, False]).groupby("length", as_index=False).first()
            lines.append("\n## Best ART stability by length\n")
            lines.append(best[["length", "representation", "paired_cosine_mean", "l2_delta_mean", "retrieval_top1", "n_features"]].to_markdown(index=False, floatfmt=".3f"))
    else:
        lines.append("\n## Result status\n")
        lines.append("No normalized ART read CSV was evaluated in this run. Generate ART FASTQ externally, convert it to the documented read schema with condition `art_illumina`, then rerun with `--reads-csv`.")
    (output_dir / "art_validation_summary.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Prepare and evaluate ART Illumina stage-3 validation.")
    parser.add_argument("--genome-manifest", default=str(PROJECT_ROOT / "data" / "real_slices" / "close_relative_genomes_manifest.csv"))
    parser.add_argument("--reads-csv", default="", help="Optional normalized CSV containing clean and art_illumina paired reads.")
    parser.add_argument("--output-dir", default=str(PROJECT_ROOT / "results" / "stage3" / "art_illumina"))
    parser.add_argument("--lengths", default="69,75,100,125,150")
    parser.add_argument("--representations", default=DEFAULT_REPRESENTATIONS)
    parser.add_argument("--art-exe", default="art_illumina")
    parser.add_argument("--profile", default="HS25")
    parser.add_argument("--fold-coverage", type=float, default=0.01)
    parser.add_argument("--max-genomes", type=int, default=0)
    parser.add_argument("--max-retrieval-pairs", type=int, default=400)
    parser.add_argument("--seed", type=int, default=404)
    args = parser.parse_args()

    started = time.time()
    set_global_seed(args.seed)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    lengths = parse_int_list(args.lengths)
    reps = parse_csv_list(args.representations)
    art_path = shutil.which(args.art_exe) or args.art_exe
    art_found = shutil.which(args.art_exe) is not None or Path(args.art_exe).exists()

    commands = write_art_manifest(
        genome_manifest=Path(args.genome_manifest),
        output_dir=output_dir,
        lengths=lengths,
        art_exe=art_path,
        profile=args.profile,
        fold_coverage=args.fold_coverage,
        seed=args.seed,
        max_genomes=args.max_genomes,
    )

    stability = None
    if args.reads_csv.strip():
        stability = evaluate_art_csv(
            reads_csv=Path(args.reads_csv),
            output_dir=output_dir,
            lengths=lengths,
            representations=reps,
            max_pairs=args.max_retrieval_pairs,
            seed=args.seed,
        )

    write_summary(commands, stability, output_dir, art_found=art_found, art_exe=args.art_exe)
    (output_dir / "stage3_art_validation_run.json").write_text(
        json.dumps(
            {
                "elapsed_seconds": time.time() - started,
                "genome_manifest": args.genome_manifest,
                "reads_csv": args.reads_csv,
                "lengths": lengths,
                "representations": reps,
                "art_exe": args.art_exe,
                "art_found": art_found,
                "profile": args.profile,
                "fold_coverage": args.fold_coverage,
                "n_command_rows": int(len(commands)),
                "n_stability_rows": int(0 if stability is None else len(stability)),
            },
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    print(f"Wrote ART validation planning/evaluation files to {output_dir}")


if __name__ == "__main__":
    main()
