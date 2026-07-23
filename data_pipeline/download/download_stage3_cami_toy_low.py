from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import requests


DEFAULT_URL = (
    "https://s3.ap-northeast-1.wasabisys.com/gigadb-datasets/live/pub/"
    "10.5524/100001_101000/100344/ToyTestDatasets.dir/30_genomes.tar"
)


def human_bytes(value: float) -> str:
    units = ["B", "KiB", "MiB", "GiB", "TiB"]
    size = float(value)
    for unit in units:
        if abs(size) < 1024.0 or unit == units[-1]:
            return f"{size:.2f} {unit}"
        size /= 1024.0
    return f"{size:.2f} TiB"


def remote_size(url: str) -> int:
    response = requests.head(url, allow_redirects=True, timeout=60)
    response.raise_for_status()
    length = response.headers.get("content-length")
    if not length:
        raise RuntimeError("Remote server did not report content-length.")
    return int(length)


def write_metadata(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def download(url: str, output: Path, metadata_path: Path, max_seconds: int, chunk_size: int) -> int:
    output.parent.mkdir(parents=True, exist_ok=True)
    partial = output.with_suffix(output.suffix + ".part")
    expected = remote_size(url)

    if output.exists() and output.stat().st_size == expected:
        write_metadata(
            metadata_path,
            {
                "status": "complete",
                "url": url,
                "output": str(output),
                "expected_bytes": expected,
                "downloaded_bytes": expected,
                "completed_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            },
        )
        print(f"Already complete: {output} ({human_bytes(expected)})", flush=True)
        return 0

    if output.exists() and output.stat().st_size != expected:
        raise RuntimeError(
            f"Existing output has unexpected size: {output.stat().st_size} bytes. "
            f"Move it manually before retrying."
        )

    downloaded = partial.stat().st_size if partial.exists() else 0
    if downloaded > expected:
        raise RuntimeError(f"Partial file is larger than expected: {partial}")

    headers = {"Range": f"bytes={downloaded}-"} if downloaded else {}
    mode = "ab" if downloaded else "wb"
    started = time.time()
    last_report = started
    last_bytes = downloaded

    print(
        f"Downloading CAMI_TOY_low 30_genomes.tar: "
        f"{human_bytes(downloaded)} / {human_bytes(expected)}",
        flush=True,
    )
    with requests.get(url, headers=headers, stream=True, timeout=(60, 120)) as response:
        if downloaded and response.status_code != 206:
            raise RuntimeError(f"Resume requested but server returned HTTP {response.status_code}.")
        response.raise_for_status()
        with partial.open(mode + "") as handle:
            for chunk in response.iter_content(chunk_size=chunk_size):
                if not chunk:
                    continue
                handle.write(chunk)
                downloaded += len(chunk)
                now = time.time()
                if now - last_report >= 30:
                    speed = (downloaded - last_bytes) / max(now - last_report, 1e-9)
                    total_speed = downloaded / max(now - started, 1e-9)
                    remaining = max(expected - downloaded, 0)
                    eta = remaining / max(total_speed, 1e-9)
                    print(
                        f"progress={human_bytes(downloaded)} / {human_bytes(expected)} "
                        f"recent={human_bytes(speed)}/s eta={eta / 60:.1f} min",
                        flush=True,
                    )
                    last_report = now
                    last_bytes = downloaded
                    write_metadata(
                        metadata_path,
                        {
                            "status": "downloading",
                            "url": url,
                            "output": str(output),
                            "partial": str(partial),
                            "expected_bytes": expected,
                            "downloaded_bytes": downloaded,
                            "elapsed_seconds": now - started,
                            "recent_bytes_per_second": speed,
                            "total_bytes_per_second": total_speed,
                            "eta_seconds": eta,
                            "updated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                        },
                    )
                if max_seconds > 0 and now - started >= max_seconds:
                    print("Reached time budget; rerun this script to resume.", flush=True)
                    return 2

    if downloaded != expected:
        write_metadata(
            metadata_path,
            {
                "status": "partial",
                "url": url,
                "output": str(output),
                "partial": str(partial),
                "expected_bytes": expected,
                "downloaded_bytes": downloaded,
                "updated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            },
        )
        print(f"Partial download: {human_bytes(downloaded)} / {human_bytes(expected)}", flush=True)
        return 2

    partial.replace(output)
    write_metadata(
        metadata_path,
        {
            "status": "complete",
            "url": url,
            "output": str(output),
            "expected_bytes": expected,
            "downloaded_bytes": downloaded,
            "elapsed_seconds": time.time() - started,
            "completed_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        },
    )
    print(f"Download complete: {output} ({human_bytes(downloaded)})", flush=True)
    return 0


def main() -> None:
    parser = argparse.ArgumentParser(description="Resume-safe CAMI_TOY_low 30_genomes.tar downloader.")
    parser.add_argument("--url", default=DEFAULT_URL)
    parser.add_argument("--output", default="data/stage3/cami/30_genomes.tar")
    parser.add_argument("--metadata", default="results/stage3/downloads/cami_toy_low_download.json")
    parser.add_argument("--max-seconds", type=int, default=0)
    parser.add_argument("--chunk-size", type=int, default=1024 * 1024)
    args = parser.parse_args()

    raise SystemExit(
        download(
            url=args.url,
            output=Path(args.output),
            metadata_path=Path(args.metadata),
            max_seconds=args.max_seconds,
            chunk_size=args.chunk_size,
        )
    )


if __name__ == "__main__":
    main()

