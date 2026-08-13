#!/usr/bin/env python3
"""Verify the P0-01 repository scaffold without external services."""

from __future__ import annotations

from pathlib import Path
import re
import sys


ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = [
    "README.md",
    ".gitignore",
    "STATUS.md",
    ".github/workflows/ci.yml",
    ".github/labels.yml",
    ".github/CODEOWNERS",
    ".github/ISSUE_TEMPLATE/roadmap_task.yml",
    "docs/adr/README.md",
    "scripts/verify_skeleton.py",
]

REQUIRED_LABELS = [
    "roadmap:P0",
    "roadmap:P1",
    "roadmap:P2",
    "roadmap:P3",
    "type:adr",
    "type:test",
    "risk:legacy-regression",
    "gate",
    "blocker",
]


def fail(message: str) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(1)


def read(relative: str) -> str:
    path = ROOT / relative
    if not path.is_file():
        fail(f"missing required file: {relative}")
    return path.read_text(encoding="utf-8")


def main() -> None:
    for relative in REQUIRED_FILES:
        read(relative)

    status = read("STATUS.md")
    if "P0-01" not in status or "next ID:" not in status:
        fail("STATUS.md must record completed P0-01 and next ID")

    ci = read(".github/workflows/ci.yml")
    if "python3 scripts/verify_skeleton.py" not in ci:
        fail("CI must run the local skeleton verifier")

    labels = read(".github/labels.yml")
    missing_labels = [label for label in REQUIRED_LABELS if f"name: {label}" not in labels]
    if missing_labels:
        fail(f"missing labels: {', '.join(missing_labels)}")

    codeowners = read(".github/CODEOWNERS")
    if not re.search(r"^\*\s+@", codeowners, flags=re.MULTILINE):
        fail("CODEOWNERS must define a default owner")

    print("P0-01 scaffold verification passed")


if __name__ == "__main__":
    main()
