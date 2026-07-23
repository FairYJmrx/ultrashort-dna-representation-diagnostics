from __future__ import annotations

import argparse
import json
import random
import sys
import tarfile
import time
import urllib.request
import zlib
from pathlib import Path

import numpy as np
import pandas as pd

def _find_project_root(start: Path) -> Path:
    for candidate in [start.parent, *start.parents]:
        if (candidate / "methods").is_dir() and (candidate / "configs").is_dir():
            return candidate
    raise RuntimeError("Could not locate the release repository root.")


PROJECT_ROOT = _find_project_root(Path(__file__).resolve())
sys.path.insert(0, str(PROJECT_ROOT))

from experiments.main.run_stage2_representation_grid import (  # noqa: E402
    apply_stage2_condition,
    parse_csv_list,
    parse_int_list,
    run_stability_grid,
    set_global_seed,
)


DEFAULT_READS_URL = (
    "https://frl.publisso.de/data/frl:6425521/marine/short_read/"
    "marmgCAMI2_sample_0_reads.tar.gz"
)
DEFAULT_SETUP_URL = (
    "https://frl.publisso.de/data/frl:6425521/marine/short_read/"
    "marmgCAMI2_setup.tar.gz"
)
DEFAULT_REPRESENTATIONS = ",".join(
    [
        "ckmer4_count_l2",
        "ckmer4_property_l2",
        "ck4p_msp",
        "ckmer4_property_multiscale_l2",
        "ckmer5_count_l2",
        "minhash_k5_s128",
        "cspaced_property_l2",
        "hybrid:ckmer5_count_l2+ckmer4_property_multiscale_mean_l2",
    ]
)


def download_range(url: str, output: Path, n_bytes: int, timeout: int = 120) -> Path:
    output.parent.mkdir(parents=True, exist_ok=True)
    if output.exists() and output.stat().st_size >= n_bytes:
        return output
    req = urllib.request.Request(url, headers={"Range": f"bytes=0-{n_bytes - 1}"})
    with urllib.request.urlopen(req, timeout=timeout) as response, output.open("wb") as handle:
        remaining = n_bytes
        while remaining > 0:
            chunk = response.read(min(1024 * 1024, remaining))
            if not chunk:
                break
            handle.write(chunk)
            remaining -= len(chunk)
    return output


def extract_setup_prefix(setup_prefix: Path, output_dir: Path) -> dict[str, object]:
    output_dir.mkdir(parents=True, exist_ok=True)
    members: list[dict[str, object]] = []
    try:
        with tarfile.open(setup_prefix, mode="r:gz") as archive:
            for member in archive:
                members.append({"name": member.name, "size": int(member.size)})
                if (
                    member.name.endswith(("config.ini", "metadata.tsv", "genome_to_id.tsv"))
                    or "taxonomic_profile_" in member.name
                ):
                    archive.extract(member, output_dir)
    except (EOFError, tarfile.ReadError):
        # The file is intentionally a prefix of the full gzip stream.
        pass
    return {"setup_prefix": str(setup_prefix), "extracted_dir": str(output_dir), "members_seen": members}


def read_inner_fastq_prefix(reads_prefix: Path, inner_compressed_bytes: int) -> bytes:
    inner = b""
    try:
        with tarfile.open(reads_prefix, mode="r|gz") as archive:
            for member in archive:
                if not member.isfile():
                    continue
                handle = archive.extractfile(member)
                if handle is None:
                    continue
                inner = handle.read(inner_compressed_bytes)
                break
    except (EOFError, tarfile.ReadError):
        pass
    if not inner:
        raise RuntimeError(f"Could not read the embedded FASTQ gzip prefix from {reads_prefix}")
    return zlib.decompressobj(16 + zlib.MAX_WBITS).decompress(inner)


def parse_fastq_records(raw_fastq: bytes, max_reads: int, seed: int) -> pd.DataFrame:
    lines = raw_fastq.splitlines()
    rows: list[dict[str, object]] = []
    for idx in range(0, len(lines) - 3, 4):
        header, seq_raw, plus, qual_raw = lines[idx:idx + 4]
        if not header.startswith(b"@") or not plus.startswith(b"+"):
            continue
        read_id = header[1:].decode("utf-8", errors="ignore").split()[0]
        seq = seq_raw.decode("utf-8", errors="ignore").upper()
        qual = qual_raw.decode("utf-8", errors="ignore")
        if len(seq) < 150:
            continue
        if any(base not in "ACGTN" for base in seq):
            continue
        rows.append(
            {
                "read_id": read_id,
                "clean_read_id": read_id,
                "sequence": seq,
                "quality": qual,
                "sample": "marmgCAMI2_sample_0",
                "source_dataset": "CAMI II marine short-read sample 0",
            }
        )
    frame = pd.DataFrame(rows)
    if frame.empty:
        raise RuntimeError("No usable CAMI II FASTQ records were parsed.")
    if max_reads > 0 and len(frame) > max_reads:
        frame = frame.sample(n=max_reads, random_state=seed)
    return frame.sort_values("clean_read_id").reset_index(drop=True)


def build_probe_rows(reads: pd.DataFrame, lengths: list[int], conditions: list[str], seed: int) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for length in lengths:
        eligible = reads[reads["sequence"].str.len() >= length].copy()
        for _, row in eligible.iterrows():
            clean = row.to_dict()
            clean["sequence"] = str(clean["sequence"])[:length]
            clean["quality"] = str(clean.get("quality", ""))[:length]
            clean["source_length"] = int(length)
            clean["length"] = int(length)
            clean["condition"] = "clean"
            clean["mutation_profile"] = ""
            clean["label"] = "unlabeled_cami2_marine"
            clean["species_id"] = "unlabeled_cami2_marine"
            clean["genus"] = "unlabeled_cami2_marine"
            clean["read_id"] = f"{clean['clean_read_id']}_L{length}_clean"
            for condition in conditions:
                if condition == "clean":
                    rows.append(clean.copy())
                else:
                    rows.append(apply_stage2_condition(pd.Series(clean), condition, seed))
    out = pd.DataFrame(rows)
    out["source_length"] = out["source_length"].astype(int)
    out["length"] = out["length"].astype(int)
    return out


def summarize_results(stability: pd.DataFrame, output_dir: Path, metadata: dict[str, object]) -> None:
    if "error" in stability.columns:
        valid = stability[stability["error"].fillna("").astype(str).str.len().eq(0)].copy()
    else:
        valid = stability.copy()
    lines: list[str] = [
        "# CAMI II Marine Lightweight Probe Summary",
        "",
        "This probe uses CAMI II marine short-read sample 0 as an external metagenomic short-read source.",
        "It is an unlabeled paired perturbation-stability probe, not a taxonomic classifier benchmark.",
        "",
        "## Input",
        "",
        f"- Reads URL: `{metadata['reads_url']}`",
        f"- Setup URL: `{metadata['setup_url']}`",
        f"- Parsed FASTQ reads: {metadata['n_clean_reads']}",
        f"- Probe rows after length/condition expansion: {metadata['n_probe_rows']}",
        f"- Lengths: {metadata['lengths']}",
        f"- Conditions: {metadata['conditions']}",
        "",
    ]
    if valid.empty:
        lines.append("No valid stability rows were produced.")
    else:
        best = (
            valid.sort_values(["condition", "length", "l2_delta_mean"])
            .groupby(["condition", "length"], as_index=False)
            .first()
        )
        lines.extend(
            [
                "## Lowest-drift representation by condition and length",
                "",
                best[
                    [
                        "condition",
                        "length",
                        "representation",
                        "paired_cosine_mean",
                        "l2_delta_mean",
                        "retrieval_top1",
                        "n_features",
                    ]
                ].to_markdown(index=False, floatfmt=".3f"),
                "",
                "## Interpretation boundary",
                "",
                "Because read-level taxonomic labels are not available from the anonymous FASTQ header and the BAM truth files are distributed as large OTU-specific bundles, this run should be reported only as an external short-read stability probe. It should not be described as CAMI II taxonomic validation.",
            ]
        )
    (output_dir / "cami2_marine_lightweight_probe_summary.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a lightweight CAMI II marine perturbation-stability probe.")
    parser.add_argument("--reads-url", default=DEFAULT_READS_URL)
    parser.add_argument("--setup-url", default=DEFAULT_SETUP_URL)
    parser.add_argument("--output-dir", default=str(PROJECT_ROOT / "results" / "stage3" / "cami2_marine_lightweight_probe"))
    parser.add_argument("--cache-dir", default=str(PROJECT_ROOT / "data" / "stage3" / "cami2_marine"))
    parser.add_argument("--reads-prefix-mib", type=int, default=8)
    parser.add_argument("--setup-prefix-mib", type=int, default=64)
    parser.add_argument("--inner-fastq-prefix-mib", type=int, default=6)
    parser.add_argument("--max-reads", type=int, default=12000)
    parser.add_argument("--lengths", default="69,75,100")
    parser.add_argument("--conditions", default="clean,N_3pct,substitution_1pct,substitution_1pct_N_3pct")
    parser.add_argument("--representations", default=DEFAULT_REPRESENTATIONS)
    parser.add_argument("--max-pairs", type=int, default=4000)
    parser.add_argument("--seed", type=int, default=626)
    args = parser.parse_args()

    started = time.time()
    set_global_seed(args.seed)
    random.seed(args.seed)
    np.random.seed(args.seed)

    output_dir = Path(args.output_dir)
    cache_dir = Path(args.cache_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    cache_dir.mkdir(parents=True, exist_ok=True)

    reads_prefix = download_range(
        args.reads_url,
        cache_dir / f"marmgCAMI2_sample_0_reads.head{args.reads_prefix_mib}mb.tar.gz.part",
        args.reads_prefix_mib * 1024 * 1024,
        timeout=180,
    )
    setup_prefix = download_range(
        args.setup_url,
        cache_dir / f"marmgCAMI2_setup.head{args.setup_prefix_mib}mb.tar.gz.part",
        args.setup_prefix_mib * 1024 * 1024,
        timeout=180,
    )
    setup_meta = extract_setup_prefix(setup_prefix, cache_dir / "setup_head_extract")
    raw_fastq = read_inner_fastq_prefix(reads_prefix, args.inner_fastq_prefix_mib * 1024 * 1024)
    clean_reads = parse_fastq_records(raw_fastq, max_reads=args.max_reads, seed=args.seed)
    clean_reads.to_csv(output_dir / "cami2_marine_clean_reads.csv", index=False, encoding="utf-8-sig")

    lengths = parse_int_list(args.lengths)
    conditions = parse_csv_list(args.conditions)
    representations = parse_csv_list(args.representations)
    probe_rows = build_probe_rows(clean_reads, lengths=lengths, conditions=conditions, seed=args.seed)
    probe_rows.to_csv(output_dir / "cami2_marine_probe_reads.csv", index=False, encoding="utf-8-sig")

    stability = run_stability_grid(
        probe_rows,
        lengths=lengths,
        conditions=conditions,
        representations=representations,
        max_pairs=args.max_pairs,
        seed=args.seed,
        output_path=output_dir / "cami2_marine_stability.csv",
    )
    stability.to_csv(output_dir / "cami2_marine_stability.csv", index=False, encoding="utf-8-sig")

    metadata: dict[str, object] = {
        "elapsed_seconds": time.time() - started,
        "reads_url": args.reads_url,
        "setup_url": args.setup_url,
        "reads_prefix": str(reads_prefix),
        "setup_prefix": str(setup_prefix),
        "reads_prefix_mib": args.reads_prefix_mib,
        "setup_prefix_mib": args.setup_prefix_mib,
        "inner_fastq_prefix_mib": args.inner_fastq_prefix_mib,
        "n_clean_reads": int(len(clean_reads)),
        "n_probe_rows": int(len(probe_rows)),
        "n_stability_rows": int(len(stability)),
        "lengths": lengths,
        "conditions": conditions,
        "representations": representations,
        "max_pairs": args.max_pairs,
        "seed": args.seed,
        "setup_meta": setup_meta,
    }
    (output_dir / "cami2_marine_lightweight_probe_run.json").write_text(
        json.dumps(metadata, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    summarize_results(stability, output_dir, metadata)
    print(f"Wrote CAMI II marine lightweight probe to {output_dir}")


if __name__ == "__main__":
    main()

