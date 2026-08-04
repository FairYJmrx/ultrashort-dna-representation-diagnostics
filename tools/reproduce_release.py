"""Run the quick or maintained full release-reproduction path."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "results" / "_repro_check"

QUICK = [
    [sys.executable, "-m", "pytest", "smoke_tests", "-q"],
    [sys.executable, "tools/release_preflight.py"],
]

FULL = QUICK + [
    [sys.executable, "experiments/main/run_stage3_compact_baselines.py", "--output-dir", "results/_repro_check/compact_baselines"],
    [sys.executable, "experiments/main/run_local_mutation_sensitivity.py", "--output-dir", "results/_repro_check/local_mutation_sensitivity"],
    [sys.executable, "experiments/audits/run_p_msp_contribution_audit.py", "--output-dir", "results/_repro_check/p_msp_contribution"],
    [sys.executable, "experiments/audits/run_high_k_compressed_baselines.py", "--output-dir", "results/_repro_check/high_k_compressed_baselines"],
    [sys.executable, "experiments/audits/run_knn_mi_robustness_audit.py", "--output-dir", "results/_repro_check/knn_mi_robustness"],
    [sys.executable, "experiments/audits/run_short_read_length_continuity_audit.py", "--output-dir", "results/_repro_check/short_read_length_continuity"],
]


def run(commands: list[list[str]]) -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    records: list[dict[str, object]] = []
    for command in commands:
        started = datetime.now(timezone.utc)
        print("+", subprocess.list2cmdline(command), flush=True)
        completed = subprocess.run(command, cwd=ROOT, check=False)
        records.append(
            {
                "command": command,
                "started_utc": started.isoformat(),
                "returncode": completed.returncode,
            }
        )
        if completed.returncode:
            (OUTPUT / "reproduction_log.json").write_text(json.dumps(records, indent=2), encoding="utf-8")
            raise SystemExit(completed.returncode)
    (OUTPUT / "reproduction_log.json").write_text(json.dumps(records, indent=2), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=("quick", "full"), default="quick")
    args = parser.parse_args()
    run(QUICK if args.mode == "quick" else FULL)
    print(f"ok: {args.mode} release reproduction completed")


if __name__ == "__main__":
    main()
