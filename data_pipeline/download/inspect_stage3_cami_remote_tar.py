from __future__ import annotations

import argparse
import csv
import math
from dataclasses import dataclass
from pathlib import Path

import requests


DEFAULT_URL = (
    "https://s3.ap-northeast-1.wasabisys.com/gigadb-datasets/live/pub/"
    "10.5524/100001_101000/100344/ToyTestDatasets.dir/30_genomes.tar"
)


@dataclass
class TarMember:
    name: str
    size: int
    typeflag: str
    header_offset: int
    data_offset: int
    next_header_offset: int


def fetch_range(url: str, start: int, end: int) -> bytes:
    headers = {"Range": f"bytes={start}-{end}"}
    response = requests.get(url, headers=headers, timeout=(30, 120))
    if response.status_code not in {200, 206}:
        raise RuntimeError(f"HTTP {response.status_code} while fetching range {start}-{end}")
    return response.content


def parse_octal(raw: bytes) -> int:
    if raw and raw[0] & 0x80:
        data = bytearray(raw)
        data[0] &= 0x7F
        return int.from_bytes(data, byteorder="big", signed=False)
    text = raw.decode("ascii", errors="ignore").strip("\x00 ").strip()
    return int(text or "0", 8)


def parse_header(block: bytes, offset: int) -> TarMember | None:
    if len(block) != 512:
        raise ValueError(f"Expected 512-byte tar header at {offset}, got {len(block)} bytes")
    if not block.strip(b"\x00"):
        return None
    name = block[0:100].split(b"\x00", 1)[0].decode("utf-8", errors="replace")
    prefix = block[345:500].split(b"\x00", 1)[0].decode("utf-8", errors="replace")
    if prefix:
        name = f"{prefix}/{name}"
    size = parse_octal(block[124:136])
    typeflag = (block[156:157] or b"0").decode("ascii", errors="ignore") or "0"
    data_offset = offset + 512
    padded = int(math.ceil(size / 512.0) * 512) if size else 0
    return TarMember(
        name=name,
        size=size,
        typeflag=typeflag,
        header_offset=offset,
        data_offset=data_offset,
        next_header_offset=data_offset + padded,
    )


def inspect_remote_tar(url: str, max_members: int) -> list[TarMember]:
    members: list[TarMember] = []
    offset = 0
    pending_long_name: str | None = None
    for _ in range(max_members):
        block = fetch_range(url, offset, offset + 511)
        member = parse_header(block, offset)
        if member is None:
            break
        if member.typeflag == "L":
            raw_name = fetch_range(url, member.data_offset, member.data_offset + member.size - 1)
            pending_long_name = raw_name.split(b"\x00", 1)[0].decode("utf-8", errors="replace")
            offset = member.next_header_offset
            continue
        if pending_long_name:
            member.name = pending_long_name
            pending_long_name = None
        members.append(member)
        offset = member.next_header_offset
    return members


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a lightweight manifest for a remote uncompressed tar via HTTP Range.")
    parser.add_argument("--url", default=DEFAULT_URL)
    parser.add_argument("--output", default="results/stage3/cami_remote_tar_manifest.csv")
    parser.add_argument("--max-members", type=int, default=200)
    args = parser.parse_args()

    members = inspect_remote_tar(args.url, max_members=args.max_members)
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["name", "size", "typeflag", "header_offset", "data_offset", "next_header_offset"],
        )
        writer.writeheader()
        for member in members:
            writer.writerow(member.__dict__)
    print(f"Wrote {len(members)} tar members to {out}")
    for member in members[:30]:
        print(f"{member.name}\t{member.size}\t{member.typeflag}\tdata@{member.data_offset}")


if __name__ == "__main__":
    main()


