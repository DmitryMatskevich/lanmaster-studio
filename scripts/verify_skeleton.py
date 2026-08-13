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
    "docs/adr/0001-repository-boundary-and-sdk-delivery.md",
    "docs/adr/0002-job-queue.md",
    "docs/adr/0003-object-storage-lifecycle.md",
    "docs/adr/0004-stable-component-identifiers.md",
    "docs/adr/0005-pmd-canonical-serialization.md",
    "docs/adr/0006-partial-preview-cache.md",
    "docs/adr/0007-llm-provider-and-data-retention.md",
    "docs/adr/0008-release-gates.md",
    "docs/adr/0009-openusd-after-mvp.md",
    "docs/discovery/p0-02-cad-inventory.md",
    "docs/discovery/p0-03-source-manifest.yml",
    "docs/discovery/p0-04-baseline-candidates.md",
    "docs/discovery/p0-04-source-cache-update.md",
    "docs/discovery/p0-06-slo-gates-and-tolerances.md",
    "docs/discovery/p0-07-toolchain-smoke.md",
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

    adr_index = read("docs/adr/README.md")
    for number in range(1, 10):
        adr_id = f"ADR-{number:04d}"
        if adr_id not in adr_index:
            fail(f"ADR index missing {adr_id}")
        adr_text = read(f"docs/adr/{number:04d}-" + {
            1: "repository-boundary-and-sdk-delivery.md",
            2: "job-queue.md",
            3: "object-storage-lifecycle.md",
            4: "stable-component-identifiers.md",
            5: "pmd-canonical-serialization.md",
            6: "partial-preview-cache.md",
            7: "llm-provider-and-data-retention.md",
            8: "release-gates.md",
            9: "openusd-after-mvp.md",
        }[number])
        if "Status: proposed" not in adr_text or "## Decision" not in adr_text:
            fail(f"{adr_id} must include proposed status and decision")

    inventory = read("docs/discovery/p0-02-cad-inventory.md")
    for phrase in (
        "Family Routing",
        "CLI Contracts",
        "Existing Compatibility Tests",
        "1876",
    ):
        if phrase not in inventory:
            fail(f"P0-02 inventory missing required evidence: {phrase}")

    manifest = read("docs/discovery/p0-03-source-manifest.yml")
    for phrase in (
        "TWT-CBB-42U-8x10-P1",
        "TWT-CBWNG-12U-6x6-BK",
        "TWT-FRWAJ-12U-GY",
        "currentCard: \"../lanmaster-cad/params/TWT-CBWNG-12U-6x6-BK.yaml\"",
        "sourceAuditRequired:",
        "- none",
        "sha256:",
    ):
        if phrase not in manifest:
            fail(f"P0-03 source manifest missing required evidence: {phrase}")

    baseline = read("docs/discovery/p0-04-baseline-candidates.md")
    for phrase in (
        "16c6b49e3b1c63f6be5e0c6f7fac37d8a7b276d6",
        "existing baseline candidate only",
        "P0-04 is not complete",
        "TWT-CBWNG-12U-6x6-BK",
        "TWT-FRWAJ-12U-GY",
        "87c301be02d6bd6e7cb4d09710fca3fa3ed4dc3591975607ccb9fc67bd717b49",
        "fb3d9659be6930e817b698b22195ec049ed25d86cee44c3c2e9f333254d41e23",
        "current legacy output bbox: 542 x 354 x 658 mm",
    ):
        if phrase not in baseline:
            fail(f"P0-04 baseline note missing required evidence: {phrase}")

    source_cache = read("docs/discovery/p0-04-source-cache-update.md")
    for phrase in (
        "cbcc415940421a6cfcd62e699e7d1edd291140fc73d8237b6fd1629b298f5564",
        "11add4a3c98cfb4ca3ab9f47ce6882ec2042c518d5f17b54051f3128766637d6",
        "studio-p0-source-cache",
        "Remaining Gaps",
    ):
        if phrase not in source_cache:
            fail(f"P0-04 source cache update missing required evidence: {phrase}")

    p006 = read("docs/discovery/p0-06-slo-gates-and-tolerances.md")
    for phrase in (
        "p95 <= 300 ms",
        "p50 <= 2 s, p95 <= 5 s",
        "Release Gates",
        "Format Read-Back Gates",
        "Legacy/PMD Parity Tolerances",
        "Known-defect handling",
    ):
        if phrase not in p006:
            fail(f"P0-06 checklist missing required evidence: {phrase}")

    p007 = read("docs/discovery/p0-07-toolchain-smoke.md")
    for phrase in (
        "Poppler `pdfinfo`",
        "LibreDWG `dwgread`",
        "STEPControl_Reader.ReadFile",
        "IfcOpenShell opened schema `IFC4X3`",
        "No real SVG source fixture",
        "Status: scoped pass for P0",
        "Pilot source matrix for P0 is scoped to official PDF/HTML/JSON cache evidence.",
        "source-CAD intake is explicitly deferred to P3/P6",
        "PDF table text extraction did not recover usable text",
    ):
        if phrase not in p007:
            fail(f"P0-07 smoke report missing required evidence: {phrase}")

    print("P0 scaffold verification passed")


if __name__ == "__main__":
    main()
