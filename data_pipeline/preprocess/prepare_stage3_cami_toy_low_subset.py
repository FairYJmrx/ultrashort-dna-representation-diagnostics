from __future__ import annotations

import argparse
import gzip
import json
import math
import re
import zlib
from collections import Counter
from pathlib import Path
from typing import Iterable

import pandas as pd
import requests


DEFAULT_URL = (
    "https://s3.ap-northeast-1.wasabisys.com/gigadb-datasets/live/pub/"
    "10.5524/100001_101000/100344/ToyTestDatasets.dir/30_genomes.tar"
)


def fetch_member_prefix(url: str, data_offset: int, member_size: int, max_bytes: int, output: Path) -> Path:
    output.parent.mkdir(parents=True, exist_ok=True)
    target = min(member_size, max_bytes)
    existing = output.stat().st_size if output.exists() else 0
    if existing >= target:
        return output
    headers = {"Range": f"bytes={data_offset + existing}-{data_offset + target - 1}"}
    with requests.get(url, headers=headers, stream=True, timeout=(60, 180)) as response:
        if existing and response.status_code != 206:
            raise RuntimeError(f"Resume requested but server returned HTTP {response.status_code}")
        response.raise_for_status()
        with output.open("ab" if existing else "wb") as handle:
            for chunk in response.iter_content(chunk_size=1024 * 1024):
                if chunk:
                    handle.write(chunk)
    return output


def iter_truncated_gzip_lines(path: Path) -> Iterable[str]:
    decompressor = zlib.decompressobj(16 + zlib.MAX_WBITS)
    try:
        raw = decompressor.decompress(path.read_bytes())
    except zlib.error:
        raw = b""
    for line in raw.splitlines():
        yield line.decode("utf-8", errors="ignore").rstrip("\r")


def read_full_member_gzip(url: str, data_offset: int, member_size: int) -> list[str]:
    response = requests.get(
        url,
        headers={"Range": f"bytes={data_offset}-{data_offset + member_size - 1}"},
        timeout=(60, 180),
    )
    response.raise_for_status()
    return gzip.decompress(response.content).decode("utf-8", errors="ignore").splitlines()


def get_member(manifest: pd.DataFrame, pattern: str) -> pd.Series:
    hits = manifest[manifest["name"].astype(str).str.contains(pattern, regex=True)]
    if hits.empty:
        raise ValueError(f"No CAMI tar member matched pattern: {pattern}")
    return hits.iloc[0]


def fastq_rows(path: Path, max_read_index: int) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    chunk: list[str] = []
    for line in iter_truncated_gzip_lines(path):
        chunk.append(line)
        if len(chunk) < 4:
            continue
        header, seq, _, qual = chunk
        chunk = []
        if not header.startswith("@"):
            continue
        rid = header[1:].split()[0]
        base_id = rid.split("/")[0]
        match = re.search(r"\|R(\d+)$", base_id)
        if match and int(match.group(1)) > max_read_index:
            continue
        rows.append({"read_id": rid, "clean_read_id": base_id, "sequence": seq.upper(), "quality": qual})
    return rows


def mapping_dict(path: Path, max_read_index: int) -> dict[str, dict[str, str]]:
    mapping: dict[str, dict[str, str]] = {}
    for line in iter_truncated_gzip_lines(path):
        if not line or line.startswith("#"):
            continue
        parts = line.split("\t")
        if len(parts) < 4:
            continue
        rid, genome_id, tax_id, sequence_id = parts[:4]
        match = re.search(r"\|R(\d+)$", rid)
        if not match:
            continue
        if int(match.group(1)) > max_read_index:
            continue
        mapping[rid] = {"genome_id": genome_id, "tax_id": tax_id, "sequence_id": sequence_id}
    return mapping


def balanced_cap(df: pd.DataFrame, label_col: str, max_rows: int, seed: int) -> pd.DataFrame:
    if len(df) <= max_rows:
        return df.sample(frac=1.0, random_state=seed).reset_index(drop=True)
    labels = df[label_col].astype(str)
    classes = labels.nunique()
    per_class = max(1, math.ceil(max_rows / max(1, classes)))
    parts = []
    for _, part in df.groupby(label_col):
        parts.append(part.sample(n=min(per_class, len(part)), random_state=seed))
    out = pd.concat(parts, ignore_index=True)
    if len(out) > max_rows:
        out = out.sample(n=max_rows, random_state=seed)
    return out.sample(frac=1.0, random_state=seed).reset_index(drop=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="Prepare a small labelled CAMI_TOY_low read subset via remote tar ranges.")
    parser.add_argument("--url", default=DEFAULT_URL)
    parser.add_argument("--manifest", default="results/stage3/cami_remote_tar_manifest.csv")
    parser.add_argument("--cache-dir", default="data/stage3/cami/remote_prefix_cache")
    parser.add_argument("--output", default="data/stage3/cami/cami_toy_low_subset_reads.csv")
    parser.add_argument("--metadata", default="results/stage3/cami_subset_metadata.json")
    parser.add_argument("--fastq-prefix-mib", type=int, default=16)
    parser.add_argument("--mapping-prefix-mib", type=int, default=96)
    parser.add_argument("--max-read-index", type=int, default=50000)
    parser.add_argument("--max-reads", type=int, default=50000)
    parser.add_argument("--seed", type=int, default=606)
    args = parser.parse_args()

    manifest = pd.read_csv(args.manifest)
    cache = Path(args.cache_dir)
    fastq = get_member(manifest, "reads_anonymous\\.fq\\.gz")
    mapping = get_member(manifest, "gs_read_mapping\\.tsv\\.gz")
    abundance = get_member(manifest, "abundances\\.tsv\\.gz")

    fastq_prefix = fetch_member_prefix(
        args.url,
        int(fastq["data_offset"]),
        int(fastq["size"]),
        args.fastq_prefix_mib * 1024 * 1024,
        cache / f"reads_anonymous.first_{args.fastq_prefix_mib}MiB.fq.gz.part",
    )
    mapping_prefix = fetch_member_prefix(
        args.url,
        int(mapping["data_offset"]),
        int(mapping["size"]),
        args.mapping_prefix_mib * 1024 * 1024,
        cache / f"gs_read_mapping.first_{args.mapping_prefix_mib}MiB.tsv.gz.part",
    )

    fq_rows = fastq_rows(fastq_prefix, max_read_index=args.max_read_index)
    labels = mapping_dict(mapping_prefix, max_read_index=args.max_read_index)
    rows = []
    for row in fq_rows:
        label = labels.get(row["clean_read_id"])
        if not label:
            continue
        merged = dict(row)
        merged.update(label)
        merged["label"] = f"tax_{label['tax_id']}"
        merged["species_id"] = f"tax_{label['tax_id']}"
        merged["genus"] = f"tax_{label['tax_id']}"
        rows.append(merged)
    df = pd.DataFrame(rows)
    if df.empty:
        raise RuntimeError("No labelled CAMI reads were recovered; increase mapping/FASTQ prefixes.")
    df = balanced_cap(df, "label", max_rows=args.max_reads, seed=args.seed)
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out, index=False, encoding="utf-8-sig")

    abundance_lines = read_full_member_gzip(args.url, int(abundance["data_offset"]), int(abundance["size"]))
    top_labels = Counter(df["label"]).most_common(10)
    Path(args.metadata).write_text(
        json.dumps(
            {
                "url": args.url,
                "manifest": args.manifest,
                "fastq_prefix_mib": args.fastq_prefix_mib,
                "mapping_prefix_mib": args.mapping_prefix_mib,
                "max_read_index": args.max_read_index,
                "max_reads": args.max_reads,
                "seed": args.seed,
                "n_fastq_rows_seen": len(fq_rows),
                "n_mapping_labels_seen": len(labels),
                "n_labelled_rows_written": len(df),
                "n_labels": int(df["label"].nunique()),
                "top_labels": top_labels,
                "abundance_preview": abundance_lines[:20],
                "output": str(out),
            },
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    print(f"Wrote {len(df)} labelled CAMI reads across {df['label'].nunique()} labels to {out}")
    print("Top labels:", top_labels[:5])


if __name__ == "__main__":
    main()


