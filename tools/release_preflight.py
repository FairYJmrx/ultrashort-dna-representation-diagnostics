"""Fail fast on metadata and packaging problems before a public release."""

from __future__ import annotations

import re
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MAX_TRACKED_BYTES = 50 * 1024 * 1024
TEXT_SUFFIXES = {".cff", ".csv", ".json", ".md", ".py", ".tex", ".txt", ".yaml", ".yml"}
PATH_RULE_FILES = {"tools/sanitize_release_paths.py"}
LOCAL_PATHS = re.compile(r"(?:[A-Za-z]:[\\/](?:AI-NGS|Users)[\\/]|D:[\\/]AI-NGS)", re.IGNORECASE)
SECRET_PATTERNS = {
    "private key": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    "GitHub token": re.compile(r"gh[oprsu]_[A-Za-z0-9_]{30,}"),
    "generic API key": re.compile(r"(?i)(?:api[_-]?key|secret[_-]?key)\s*[:=]\s*['\"][^'\"]{12,}['\"]"),
}


def tracked_files() -> list[Path]:
    output = subprocess.check_output(["git", "ls-files", "-z"], cwd=ROOT)
    return [ROOT / item.decode("utf-8") for item in output.split(b"\0") if item]


def main() -> None:
    errors: list[str] = []
    required = [
        "README.md",
        "LICENSE",
        "CITATION.cff",
        "requirements.txt",
        "methods/ck4p_msp.py",
        "paper_latex/main.tex",
        "paper_latex/supplementary.tex",
    ]
    for relative in required:
        if not (ROOT / relative).is_file():
            errors.append(f"missing required file: {relative}")

    for path in tracked_files():
        relative = path.relative_to(ROOT).as_posix()
        if not path.is_file():
            continue
        size = path.stat().st_size
        if size > MAX_TRACKED_BYTES:
            errors.append(f"tracked file exceeds 50 MiB: {relative} ({size / 1024**2:.1f} MiB)")
        if path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        if relative not in PATH_RULE_FILES and LOCAL_PATHS.search(text):
            errors.append(f"local absolute path found: {relative}")
        for label, pattern in SECRET_PATTERNS.items():
            if pattern.search(text):
                errors.append(f"possible {label} found: {relative}")

    citation = (ROOT / "CITATION.cff").read_text(encoding="utf-8")
    if "Jianhua Huang" in citation or 'family-names: "Huang"' in citation:
        errors.append("CITATION.cff contains a non-author")
    if "submission-private" in citation:
        errors.append("CITATION.cff still uses a private-submission version")

    if errors:
        raise SystemExit("Release preflight failed:\n- " + "\n- ".join(errors))
    print("ok: release metadata, tracked paths, file sizes and credential patterns")


if __name__ == "__main__":
    main()
